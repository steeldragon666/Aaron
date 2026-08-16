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

from .errors import AccessDenied, CrossContextViolation
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
    """
    table = _safe_entity(entity)
    rows = conn.execute(
        f"SELECT * FROM {table} WHERE tenant_id = ? AND ({where}) ORDER BY {order_by}",
        (reader.tenant_id, *params),
    ).fetchall()
    return filter_readable(conn, reader, entity, rows)


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
