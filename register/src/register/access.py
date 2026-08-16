"""Access control: visibility, the cross-context rule, and the access log.

Two independent checks stand between a reader and a record.

**Visibility** answers *may this person see it* — per record, default-deny,
CLAUDE.md §1 and ACTION_TIER_AND_REGISTER_SPEC §4.

**The cross-context rule** answers *may this fact be referenced to that
counterparty* — CLAUDE.md §4. An agent may reference to a counterparty only
facts that counterparty is already party to, or that are explicitly listed in
that record's ``shareable_with``.

Both are queries the read must pass, not instructions in a system prompt.
Prompt-level constraints do not survive long context, and this is the failure
that loses a client.

Every read is logged, allowed or denied. The deny lines are the more
interesting half: a rising deny rate on one agent is the earliest signal that
its retrieval scope is wrong.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from .errors import AccessDenied, CrossContextViolation, InvariantError
from .invariants import parse_shareable_with
from .redaction import redact

# Reader roles, per A-6: principal, EA, and relevant direct reports.
ROLES: tuple[str, ...] = ("principal", "ea", "leadership", "user")

# Which roles a given visibility admits. Default-deny is expressed by
# enumerating who may read, never by enumerating who may not.
VISIBILITY_READERS: Mapping[str, frozenset[str]] = {
    "principal_only": frozenset({"principal"}),
    "principal_and_ea": frozenset({"principal", "ea"}),
    "leadership": frozenset({"principal", "ea", "leadership"}),
    "all_users": frozenset({"principal", "ea", "leadership", "user"}),
}


@dataclass(frozen=True)
class Reader:
    """Who is reading, on whose behalf, and into what context.

    ``counterparty_scope`` is set when the read is happening in order to say
    something *to* a counterparty — composing a message, building a brief for a
    meeting with them, answering a question they asked. When it is set, the
    cross-context rule applies on top of visibility.

    A read with no counterparty scope is an internal read: the principal or
    their EA looking at their own register. Visibility alone governs it.
    """

    tenant_id: str
    actor: str  # a human id, or an agent name — whatever appears in the log
    role: str
    counterparty_scope: str | None = None
    agent: str | None = None

    def __post_init__(self) -> None:
        if self.role not in ROLES:
            raise ValueError(f"unknown reader role {self.role!r}; expected one of {ROLES}")

    def scoped_to(self, counterparty_id: str | None) -> Reader:
        return Reader(
            tenant_id=self.tenant_id,
            actor=self.actor,
            role=self.role,
            counterparty_scope=counterparty_id,
            agent=self.agent,
        )


@dataclass
class Decision:
    allowed: bool
    reason: str

    def raise_if_denied(self, entity: str, record_id: str) -> None:
        if self.allowed:
            return
        message = f"{entity}/{record_id}: {self.reason}"
        if self.reason.startswith("cross_context"):
            raise CrossContextViolation(message)
        raise AccessDenied(message)


def evaluate(reader: Reader, record: Mapping[str, Any] | sqlite3.Row) -> Decision:
    """Decide whether ``reader`` may read ``record``. Pure — logs nothing.

    Accepts a ``sqlite3.Row`` as well as a dict so that callers cannot end up
    with a second, unchecked read path just because they had a raw row in hand.
    """
    record = dict(record)

    if record.get("tenant_id") != reader.tenant_id:
        return Decision(False, "tenant_mismatch: record belongs to another tenant")

    visibility = record.get("visibility")
    admitted = VISIBILITY_READERS.get(str(visibility))
    if admitted is None:
        # An unrecognised visibility is a deny, not a pass. A record written by
        # a future migration with a level this code does not know about must
        # not become readable by accident.
        return Decision(False, f"visibility_unknown: {visibility!r}")
    if reader.role not in admitted:
        return Decision(
            False,
            f"visibility_denied: {visibility} does not admit role {reader.role}",
        )

    if reader.counterparty_scope is not None:
        shareable = parse_shareable_with(record.get("shareable_with"))
        if reader.counterparty_scope not in shareable:
            return Decision(
                False,
                "cross_context_denied: counterparty "
                f"{reader.counterparty_scope} is not in shareable_with",
            )

    return Decision(True, "allow")


def log_access(
    conn: sqlite3.Connection,
    reader: Reader,
    entity: str,
    record_id: str,
    decision: Decision,
) -> None:
    conn.execute(
        """
        INSERT INTO access_log
            (tenant_id, at, actor, actor_role, counterparty_scope,
             entity, record_id, decision, reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            reader.tenant_id,
            datetime.now(UTC).isoformat(timespec="seconds"),
            reader.actor,
            reader.role,
            reader.counterparty_scope,
            entity,
            record_id,
            "allow" if decision.allowed else "deny",
            decision.reason,
        ),
    )


def filter_readable(
    conn: sqlite3.Connection,
    reader: Reader,
    entity: str,
    rows: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Return the subset of ``rows`` this reader may see, logging every row.

    Denied rows are dropped silently from the caller's perspective — the caller
    must not be able to infer their existence from the result — but each one
    leaves a deny line in the access log.
    """
    out: list[dict[str, Any]] = []
    for raw in rows:
        row = dict(raw)
        decision = evaluate(reader, row)
        log_access(conn, reader, entity, str(row.get("id", "")), decision)
        if decision.allowed:
            out.append(row)
    return out


def read_one(
    conn: sqlite3.Connection,
    reader: Reader,
    entity: str,
    record_id: str,
) -> dict[str, Any] | None:
    """Fetch a single record by id, subject to both checks.

    Returns ``None`` when the record does not exist. Raises when it exists but
    the reader may not see it — the caller asked for a specific id, so the
    distinction is already known to them.
    """
    row = conn.execute(
        f"SELECT * FROM {_safe_entity(entity)} WHERE id = ?", (record_id,)
    ).fetchone()
    if row is None:
        return None
    decision = evaluate(reader, row)
    log_access(conn, reader, entity, record_id, decision)
    decision.raise_if_denied(entity, record_id)
    return dict(row)


def query(
    conn: sqlite3.Connection,
    reader: Reader,
    entity: str,
    where: str = "1=1",
    params: Sequence[Any] = (),
    order_by: str = "created_at",
) -> list[dict[str, Any]]:
    """Run a scoped query and filter the result through both checks.

    ``tenant_id`` is applied here rather than left to the caller. A caller that
    forgets it should get an empty result, not another tenant's rows.

    ``where`` and ``order_by`` are SQL fragments, and both are constrained.
    ``order_by`` must name a column on the allowlist. ``where`` must balance
    its parentheses, because the tenant scope above is only a guarantee while
    the caller's fragment stays inside the brackets it was given: a fragment
    such as ``"1=1) OR (1=1"`` closes them early and turns the predicate into
    ``tenant_id = ? AND (1=1) OR (1=1)``, which selects every tenant's rows.

    `filter_readable` still denies those rows on the tenant check in
    `evaluate`, so nothing foreign is returned — but every foreign record id
    lands in this tenant's `access_log` as a deny line, and the read scans the
    whole table. An audit log that can be filled with another tenant's
    identifiers is its own disclosure.
    """
    table = _safe_entity(entity)
    if order_by not in _ORDER_COLUMNS:
        raise InvariantError(f"order_by must be one of {sorted(_ORDER_COLUMNS)}, not {order_by!r}")
    _assert_balanced(where)
    rows = conn.execute(
        f"SELECT * FROM {table} WHERE tenant_id = ? AND ({where}) ORDER BY {order_by}",
        (reader.tenant_id, *params),
    ).fetchall()
    return filter_readable(conn, reader, entity, rows)


# Columns a caller may sort by. Every record table carries the first two; the
# rest are the natural orderings of specific entities. Interpolated into SQL,
# so this is an allowlist rather than an escaping problem.
_ORDER_COLUMNS = frozenset(
    {
        "created_at",
        "updated_at",
        "made_at",
        "due",
        "starts_at",
        "at",
        "confidence",
        "id",
    }
)


def _assert_balanced(where: str) -> None:
    """Refuse a fragment that could close the tenant scope's parentheses.

    Not a SQL parser, and not claimed as one — `where` remains a fragment a
    caller composes, so the real protection is that callers are inside this
    package. This closes the specific escape that makes the tenant predicate
    stop meaning what its docstring says.
    """
    depth = 0
    quoted = False
    for char in where:
        if char == "'":
            quoted = not quoted
        elif not quoted:
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth < 0:
                    raise InvariantError(
                        "where fragment closes a parenthesis it did not open — "
                        "it would escape the tenant scope"
                    )
    if depth != 0 or quoted:
        raise InvariantError("where fragment has unbalanced parentheses or quotes")


_ALLOWED_ENTITIES = frozenset(
    {
        "person",
        "meeting",
        "thread",
        "commitment",
        "decision",
        "exposure",
        "prediction",
        "curator_proposal",
        "ingest_event",
    }
)


def _safe_entity(entity: str) -> str:
    if entity not in _ALLOWED_ENTITIES:
        raise ValueError(f"not a readable entity: {entity!r}")
    return entity


# --- widening ---------------------------------------------------------------


@dataclass
class Widening:
    """A record of a deliberate widening of ``shareable_with``.

    Widening is a deliberate act (ACTION_TIER_AND_REGISTER_SPEC §3), so it goes
    through a named function that requires a reason, rather than through a
    generic field update.
    """

    entity: str
    record_id: str
    added: list[str] = field(default_factory=list)
    reason: str = ""


def widen_shareable_with(
    conn: sqlite3.Connection,
    reader: Reader,
    entity: str,
    record_id: str,
    add: Iterable[str],
    reason: str,
) -> Widening:
    """Add counterparties to a record's ``shareable_with``.

    Only the principal may widen. An EA can propose it; the widening itself is
    the principal's, because it is the act that lets a fact cross a boundary.
    """
    if reader.role != "principal":
        raise AccessDenied("only the principal may widen shareable_with")
    if not reason.strip():
        raise ValueError("widening requires a reason — it is the audit trail")
    # The reason is human free text and lands in the access log (CLAUDE.md §3).
    # Redacted in place rather than refused: a widening blocked over a false
    # positive is a widening someone does another way, off the audited path.
    reason = redact(reason).text

    record = read_one(conn, reader, entity, record_id)
    if record is None:
        raise LookupError(f"{entity}/{record_id} not found")

    from .invariants import normalise_shareable_with  # local import: avoids a cycle

    existing = parse_shareable_with(record["shareable_with"])
    added = sorted({str(a) for a in add} - set(existing))
    if not added:
        return Widening(entity, record_id, [], reason)

    updated = normalise_shareable_with(existing + added)
    conn.execute(
        f"UPDATE {_safe_entity(entity)} SET shareable_with = ?, updated_at = ? WHERE id = ?",
        (updated, datetime.now(UTC).isoformat(timespec="seconds"), record_id),
    )
    conn.execute(
        """
        INSERT INTO access_log
            (tenant_id, at, actor, actor_role, counterparty_scope,
             entity, record_id, decision, reason)
        VALUES (?, ?, ?, ?, NULL, ?, ?, 'allow', ?)
        """,
        (
            reader.tenant_id,
            datetime.now(UTC).isoformat(timespec="seconds"),
            reader.actor,
            reader.role,
            entity,
            record_id,
            f"widened shareable_with +{','.join(added)}: {reason}",
        ),
    )
    return Widening(entity, record_id, added, reason)


# --- the read surface, and which parts of it carry a Reader ------------------
#
# `read_one`, `query` and `filter_readable` above are the access-aware path:
# they take a :class:`Reader`, run `evaluate`, and write the access log. They
# are not, however, the *only* way to get a record out of the database. A
# number of module-level functions run their own SQL and hand back rows.
#
# In Sprint 1 that is not a leak. There is no send path, no counterparty-scoped
# caller and no agent — the only caller is a CLI the principal runs, reading
# their own register. But "not currently exploited" is a fact about today's
# callers, not a property of the code, and the send path arrives in Sprint 2.
# The thing to avoid is Sprint 2 reaching for `open_loops` because it was there
# and inheriting the bypass by accident.
#
# So the surface is classified, and `tests/test_read_surface.py` fails on any
# public function in these modules that is in none of these buckets. The point
# is not that the classification is enforcement — it is not — but that adding
# an unguarded read becomes a decision someone records rather than an omission
# nobody notices. Same move as the human/machine column split in `store` and
# the migration guard: convert silence into a choice.
#
# CLAUDE.md §4 is a check in the *send path*. When that path exists, everything
# in UNGUARDED_READS that it wants to call has to be re-expressed through a
# Reader first. This mapping is the work list for that.

UNGUARDED_READS: Mapping[str, str] = {
    "entities.open_loops": (
        "The principal's own view of their own commitments, both directions. "
        "Sprint 2 must not call this from a send path — route through `query`."
    ),
    "entities.dark_periods": (
        "Meetings with `gap_flag`, for the principal's digest. Names attendees, "
        "so a counterparty-scoped caller needs the Reader path instead."
    ),
    "entities.supersession_chain": (
        "Walks a chain the caller already holds the head of. Returns full rows."
    ),
    "entities.live_commitment": (
        "Resolves a superseded id to its live record. Returns a full row."
    ),
    "entities.cadence_alerts": (
        "Advisory digest only — writes nothing and `may_chase` does not consult "
        "it. Carries `display_name`, so it is a record read despite being derived."
    ),
    "curator.queued": (
        "The curator queue, which is by definition pre-confirmation material a "
        "human is about to triage. Principal and EA only in practice."
    ),
    "ledger.fold": "Current state of one AR, folded from its ledger entries.",
    "ledger.fold_all": "Current state of every AR in the tenant.",
    "coverage.measure": (
        "Scores the register against a manually compiled list. Reads statements "
        "across the whole tenant by construction — it is a tenant-wide metric."
    ),
}

# Public functions in those modules that return no record data: writers,
# validators, counters and id resolvers. Listed so the guard test can tell
# "returns nothing sensitive" from "nobody has looked at this yet".
NOT_A_READ: Mapping[str, str] = {
    "entities.assert_chaseable": "raises or returns None",
    "entities.create_commitment": "writer, returns an id",
    "entities.create_decision": "writer, returns an id",
    "entities.create_exposure": "writer, returns an id",
    "entities.create_meeting": "writer, returns an id",
    "entities.create_person": "writer, returns an id",
    "entities.create_tenant": "writer, returns an id",
    "entities.create_thread": "writer, returns an id",
    "entities.derived_last_substantive_contact": "returns a date or None",
    "entities.may_chase": "verdict about a row the caller already holds",
    "entities.reconcile_gap": "writer",
    "entities.record_dark_meeting": "writer, returns an id",
    "entities.refresh_last_substantive_contact": "writer, returns a count",
    "entities.shareable_counterparties": "reads a field of a row the caller holds",
    "entities.supersede_commitment": "writer",
    "entities.void_commitment": "writer",
    "curator.auto_confirm": "writer; the digest it returns is the principal's own",
    "curator.confirm": "writer, returns an id",
    "curator.principal_emails": "returns the tenant's own principal addresses",
    "curator.propose_from_events": "writer, returns counts",
    "curator.reject": "writer",
    "curator.resolve_person": "writer, returns an id",
    "curator.undo": "writer",
    "ledger.append_ar": "writer, returns an id",
    "ledger.open_ar_count": "returns a count",
    "ledger.score": "writer, returns a Brier component",
    "ledger.set_status": "writer, returns an entry hash",
    "ledger.verify_chain": "hashes only, no payload content",
    "coverage.load_known": "reads a file the caller supplied",
    "coverage.similarity": "string comparison, no database",
}
