"""Register entities.

Each constructor here does the same three things: fills the invariant fields,
defaults ``shareable_with`` to *the parties present when the record was
created and nothing more*, and writes through :mod:`register.store` so the
checks cannot be bypassed.

The default is the important part. ACTION_TIER_AND_REGISTER_SPEC §3: widening
is a deliberate act. A constructor that let the caller omit the parties and
quietly wrote ``[]`` would be safe; one that quietly wrote "everyone" would be
the failure that loses a client. There is no code path here that produces the
second.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Any

from .errors import GapSuppressed, ProvenanceError, RegisterError
from .ids import new_id
from .invariants import default_visibility, is_actionable, parse_shareable_with
from .redaction import redact
from .store import insert, now, update

# --- tenancy ----------------------------------------------------------------


def create_tenant(
    conn: sqlite3.Connection, name: str, *, is_zero: bool = False, tenant_id: str | None = None
) -> str:
    tid = tenant_id or new_id("tenant")
    conn.execute(
        "INSERT INTO tenant (id, name, is_zero, created_at) VALUES (?, ?, ?, ?)",
        (tid, name, 1 if is_zero else 0, now()),
    )
    return tid


# --- person -----------------------------------------------------------------


def create_person(
    conn: sqlite3.Connection,
    *,
    tenant_id: str,
    display_name: str,
    produced_by: str,
    provenance: str = "verbatim",
    kind: str = "person",
    email: str | None = None,
    relationship: str | None = None,
    cadence_days: int | None = None,
    sensitivity_flags: Sequence[str] = (),
    is_principal: bool = False,
    visibility: str | None = None,
    shareable_with: Iterable[str] | None = None,
    person_id: str | None = None,
) -> str:
    pid = person_id or new_id("person")
    return insert(
        conn,
        "person",
        {
            "id": pid,
            "tenant_id": tenant_id,
            "kind": kind,
            "display_name": display_name,
            "email": email,
            "relationship": relationship,
            "cadence_days": cadence_days,
            "sensitivity_flags": json.dumps(sorted(set(sensitivity_flags)), separators=(",", ":")),
            "is_principal": 1 if is_principal else 0,
            "visibility": visibility or default_visibility(sensitivity_flags),
            # A person record is shareable with themselves by default: they are
            # party to their own existence and nothing else follows from it.
            "shareable_with": list(shareable_with) if shareable_with is not None else [pid],
            "provenance": provenance,
            "produced_by": produced_by,
        },
    )


# --- meeting ----------------------------------------------------------------


def create_meeting(
    conn: sqlite3.Connection,
    *,
    tenant_id: str,
    title: str,
    starts_at: str,
    produced_by: str,
    attendees: Sequence[str] = (),
    provenance: str = "verbatim",
    ends_at: str | None = None,
    brief_issued: bool = False,
    consent_outcome: str = "not_asked",
    capture: str = "none",
    capture_reason: str | None = None,
    known_topics: Sequence[str] = (),
    gap_flag: bool = False,
    visibility: str | None = None,
    shareable_with: Iterable[str] | None = None,
    meeting_id: str | None = None,
) -> str:
    mid = meeting_id or new_id("meeting")
    insert(
        conn,
        "meeting",
        {
            "id": mid,
            "tenant_id": tenant_id,
            "title": title,
            "starts_at": starts_at,
            "ends_at": ends_at,
            "brief_issued": 1 if brief_issued else 0,
            "consent_outcome": consent_outcome,
            "capture": capture,
            "capture_reason": capture_reason,
            "known_topics": json.dumps(list(known_topics), separators=(",", ":")),
            "gap_flag": 1 if gap_flag else 0,
            "visibility": visibility or default_visibility(),
            # Parties present at creation: the attendees, and nobody else.
            "shareable_with": list(shareable_with)
            if shareable_with is not None
            else list(attendees),
            "provenance": provenance,
            "produced_by": produced_by,
        },
    )
    for person_id in attendees:
        conn.execute(
            "INSERT OR IGNORE INTO meeting_attendee (meeting_id, person_id, tenant_id) VALUES (?, ?, ?)",
            (mid, person_id, tenant_id),
        )
    return mid


def record_dark_meeting(
    conn: sqlite3.Connection,
    *,
    tenant_id: str,
    title: str,
    starts_at: str,
    attendees: Sequence[str],
    known_topics: Sequence[str],
    produced_by: str,
    reason: str = "consent_declined",
    meeting_id: str | None = None,
) -> str:
    """A meeting where transcription consent was declined.

    Produces no content but a mandatory record. Without this the register
    develops holes it does not know about, and the agent will confidently chase
    commitments that were superseded in a room it never entered.

    ``known_topics`` comes from the brief issued beforehand — the brief goes out
    regardless, because it is built entirely from the principal's own data and
    precedes the consent question.
    """
    return create_meeting(
        conn,
        tenant_id=tenant_id,
        title=title,
        starts_at=starts_at,
        produced_by=produced_by,
        attendees=attendees,
        provenance="verbatim",
        consent_outcome="declined",
        capture="none",
        capture_reason=reason,
        known_topics=known_topics,
        gap_flag=True,
        brief_issued=True,
        meeting_id=meeting_id,
    )


def dark_periods(conn: sqlite3.Connection, tenant_id: str) -> list[dict[str, Any]]:
    """Meetings the register has no content for, oldest first."""
    rows = conn.execute(
        """
        SELECT id, title, starts_at, ends_at, known_topics
        FROM meeting
        WHERE tenant_id = ? AND gap_flag = 1
        ORDER BY starts_at
        """,
        (tenant_id,),
    ).fetchall()
    return [dict(row) for row in rows]


# --- thread -----------------------------------------------------------------


def create_thread(
    conn: sqlite3.Connection,
    *,
    tenant_id: str,
    subject: str,
    produced_by: str,
    counterparties: Sequence[str] = (),
    provenance: str = "verbatim",
    external_ref: str | None = None,
    authority_tier: str = "T0",
    last_message_at: str | None = None,
    visibility: str | None = None,
    shareable_with: Iterable[str] | None = None,
    thread_id: str | None = None,
) -> str:
    tid = thread_id or new_id("thread")
    insert(
        conn,
        "thread",
        {
            "id": tid,
            "tenant_id": tenant_id,
            "subject": subject,
            "external_ref": external_ref,
            "authority_tier": authority_tier,
            "last_message_at": last_message_at,
            "visibility": visibility or default_visibility(),
            "shareable_with": list(shareable_with)
            if shareable_with is not None
            else list(counterparties),
            "provenance": provenance,
            "produced_by": produced_by,
        },
    )
    for person_id in counterparties:
        conn.execute(
            "INSERT OR IGNORE INTO thread_counterparty (thread_id, person_id, tenant_id) VALUES (?, ?, ?)",
            (tid, person_id, tenant_id),
        )
    return tid


# --- commitment -------------------------------------------------------------


def create_commitment(
    conn: sqlite3.Connection,
    *,
    tenant_id: str,
    direction: str,
    statement: str,
    made_at: str,
    source_type: str,
    provenance: str,
    produced_by: str,
    counterparty_id: str | None = None,
    confidence: float = 1.0,
    made_in: str | None = None,
    made_in_kind: str | None = None,
    due: str | None = None,
    owner: str | None = None,
    evidence_ref: str | None = None,
    status: str = "open",
    visibility: str | None = None,
    shareable_with: Iterable[str] | None = None,
    categories: Sequence[str] = (),
    commitment_id: str | None = None,
) -> str:
    """Write a commitment.

    ``shareable_with`` defaults to the counterparty the commitment is with —
    they are party to it by definition — and nobody else. A commitment with no
    counterparty defaults to ``[]``: it is shareable with no one until someone
    says otherwise.
    """
    cid = commitment_id or new_id("commitment")
    if shareable_with is None:
        parties = [counterparty_id] if counterparty_id else []
    else:
        parties = list(shareable_with)
    return insert(
        conn,
        "commitment",
        {
            "id": cid,
            "tenant_id": tenant_id,
            "direction": direction,
            "counterparty_id": counterparty_id,
            "statement": statement,
            "made_at": made_at,
            "made_in": made_in,
            "made_in_kind": made_in_kind,
            "source_type": source_type,
            "confidence": confidence,
            "due": due,
            "status": status,
            "owner": owner,
            "evidence_ref": evidence_ref,
            "superseded_by": None,
            "last_action": None,
            "last_action_at": None,
            "visibility": visibility or default_visibility(categories),
            "shareable_with": parties,
            "provenance": provenance,
            "produced_by": produced_by,
        },
    )


def supersede_commitment(
    conn: sqlite3.Connection,
    *,
    tenant_id: str,
    old_id: str,
    new_id_: str,
) -> None:
    """Point ``old_id`` at its replacement and close it.

    Supersession is a link, not a deletion: the chain stays queryable, because
    "what did we agree, and when did it change" is a question the register has
    to be able to answer against its own history.

    ``tenant_id`` scopes both lookups and the write. Without it a caller
    holding two ids could link records across tenants, which would put one
    client's commitment in another client's chain.
    """
    old = conn.execute(
        "SELECT id, status FROM commitment WHERE id = ? AND tenant_id = ?", (old_id, tenant_id)
    ).fetchone()
    if old is None:
        raise LookupError(f"commitment/{old_id} not found")
    new = conn.execute(
        "SELECT id FROM commitment WHERE id = ? AND tenant_id = ?", (new_id_, tenant_id)
    ).fetchone()
    if new is None:
        raise LookupError(f"commitment/{new_id_} not found")
    if old_id == new_id_:
        raise RegisterError("a commitment cannot supersede itself")
    # `status` was selected and never read, so a second call overwrote a
    # `superseded_by` that already pointed somewhere. `supersession_chain`
    # walks that column, so the overwritten branch became unreachable — the
    # register quietly lost a version of what was agreed, which is the one
    # thing this function exists to preserve.
    if old["status"] == "superseded":
        raise RegisterError(
            f"commitment/{old_id} is already superseded — supersede the live record "
            "at the end of its chain instead"
        )
    if _would_cycle(conn, old_id, new_id_):
        raise RegisterError("supersession would create a cycle")

    conn.execute(
        """
        UPDATE commitment SET superseded_by = ?, status = 'superseded', updated_at = ?
        WHERE id = ? AND tenant_id = ?
        """,
        (new_id_, now(), old_id, tenant_id),
    )


def _would_cycle(conn: sqlite3.Connection, old_id: str, new_id_: str) -> bool:
    seen = {old_id}
    cursor: str | None = new_id_
    while cursor:
        if cursor in seen:
            return True
        seen.add(cursor)
        row = conn.execute(
            "SELECT superseded_by FROM commitment WHERE id = ?", (cursor,)
        ).fetchone()
        cursor = row["superseded_by"] if row else None
    return False


def void_commitment(
    conn: sqlite3.Connection, commitment_id: str, reason: str, *, tenant_id: str
) -> None:
    """Mark a commitment void — it was never real, or it no longer binds.

    Distinct from superseded: superseded means replaced, void means withdrawn.
    Neither deletes anything.
    """
    update(
        conn,
        "commitment",
        commitment_id,
        {"status": "void", "last_action": f"voided: {reason}", "last_action_at": now()},
        tenant_id=tenant_id,
    )


def supersession_chain(conn: sqlite3.Connection, commitment_id: str) -> list[dict[str, Any]]:
    """Walk a commitment forward through its replacements.

    Returns the chain oldest first, ending at the live record.
    """
    chain: list[dict[str, Any]] = []
    seen: set[str] = set()
    cursor: str | None = commitment_id
    while cursor and cursor not in seen:
        seen.add(cursor)
        row = conn.execute("SELECT * FROM commitment WHERE id = ?", (cursor,)).fetchone()
        if row is None:
            break
        chain.append(dict(row))
        cursor = row["superseded_by"]
    return chain


def live_commitment(conn: sqlite3.Connection, commitment_id: str) -> dict[str, Any] | None:
    """The end of the supersession chain — what actually binds today."""
    chain = supersession_chain(conn, commitment_id)
    return chain[-1] if chain else None


# --- chase eligibility ------------------------------------------------------


@dataclass(frozen=True)
class ChaseVerdict:
    allowed: bool
    reason: str


def may_chase(conn: sqlite3.Connection, commitment: dict[str, Any]) -> ChaseVerdict:
    """Whether the agent may take autonomous action on this commitment.

    Sprint 1 does not send anything — the send path is Sprint 2. What is here
    now is the set of conditions that block a send, so that the send path is
    built against a check that already exists and is already tested:

    * ``inferred`` provenance never acts. Surface it as a question instead.
    * A superseded, met, missed or void commitment is not chased.
    * A commitment whose creating context sits inside a dark period is not
      chased until the gap is reconciled — the agent may have been superseded
      in a room it never entered.
    """
    if not is_actionable(str(commitment["provenance"])):
        return ChaseVerdict(
            False,
            "provenance is inferred — surface to the principal as a question, do not chase",
        )
    if commitment["status"] != "open":
        return ChaseVerdict(False, f"status is {commitment['status']}, not open")
    if commitment["superseded_by"]:
        return ChaseVerdict(False, "superseded")

    if _touched_by_gap(conn, commitment):
        return ChaseVerdict(False, "gap_flag: an unreconciled dark period covers this commitment")

    return ChaseVerdict(True, "eligible")


def _touched_by_gap(conn: sqlite3.Connection, commitment: dict[str, Any]) -> bool:
    """True when a dark meeting could have changed this commitment.

    Two ways that happens: the commitment was made in a meeting that went dark,
    or a dark meeting with the same counterparty happened after it was made and
    could have superseded it without the register knowing.
    """
    if commitment["made_in_kind"] == "meeting" and commitment["made_in"]:
        row = conn.execute(
            "SELECT gap_flag FROM meeting WHERE id = ?", (commitment["made_in"],)
        ).fetchone()
        if row is not None and row["gap_flag"]:
            return True

    counterparty = commitment["counterparty_id"]
    if not counterparty:
        return False

    row = conn.execute(
        """
        SELECT 1
        FROM meeting m
        JOIN meeting_attendee a ON a.meeting_id = m.id
        WHERE m.tenant_id = ?
          AND m.gap_flag = 1
          AND a.person_id = ?
          AND m.starts_at >= ?
        LIMIT 1
        """,
        (commitment["tenant_id"], counterparty, commitment["made_at"]),
    ).fetchone()
    return row is not None


def assert_chaseable(conn: sqlite3.Connection, commitment: dict[str, Any]) -> None:
    verdict = may_chase(conn, commitment)
    if verdict.allowed:
        return
    if verdict.reason.startswith("provenance"):
        raise ProvenanceError(verdict.reason)
    if verdict.reason.startswith("gap_flag"):
        raise GapSuppressed(verdict.reason)
    raise RegisterError(verdict.reason)


def reconcile_gap(conn: sqlite3.Connection, meeting_id: str, note: str) -> None:
    """Clear a gap once its content has been recovered.

    The usual recovery is the voice dump offered immediately after a dark
    meeting — the cheapest way to stop the gap compounding. The record keeps
    ``consent_outcome = declined`` forever; only the gap clears.
    """
    if not note.strip():
        raise ValueError("reconciling a gap requires a note saying how it was recovered")
    note = redact(note).text
    conn.execute(
        """
        UPDATE meeting
        SET gap_flag = 0,
            capture = 'voice_dump',
            capture_reason = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (f"reconciled: {note}", now(), meeting_id),
    )


# --- decision ---------------------------------------------------------------


def create_decision(
    conn: sqlite3.Connection,
    *,
    tenant_id: str,
    statement: str,
    reasoning_at_time: str,
    decided_at: str,
    produced_by: str,
    provenance: str = "verbatim",
    participants: Sequence[str] = (),
    decided_in: str | None = None,
    depends_on: Sequence[str] = (),
    visibility: str | None = None,
    shareable_with: Iterable[str] | None = None,
    categories: Sequence[str] = (),
    decision_id: str | None = None,
) -> str:
    did = decision_id or new_id("decision")
    insert(
        conn,
        "decision",
        {
            "id": did,
            "tenant_id": tenant_id,
            "statement": statement,
            "reasoning_at_time": reasoning_at_time,
            "decided_at": decided_at,
            "decided_in": decided_in,
            "depends_on": json.dumps(list(depends_on), separators=(",", ":")),
            "superseded_by": None,
            "visibility": visibility or default_visibility(categories),
            "shareable_with": list(shareable_with)
            if shareable_with is not None
            else list(participants),
            "provenance": provenance,
            "produced_by": produced_by,
        },
    )
    for person_id in participants:
        conn.execute(
            "INSERT OR IGNORE INTO decision_participant (decision_id, person_id, tenant_id) VALUES (?, ?, ?)",
            (did, person_id, tenant_id),
        )
    return did


# --- exposure ---------------------------------------------------------------


def create_exposure(
    conn: sqlite3.Connection,
    *,
    tenant_id: str,
    kind: str,
    description: str,
    produced_by: str,
    provenance: str = "verbatim",
    counterparty_id: str | None = None,
    effective_from: str | None = None,
    expires_on: str | None = None,
    notice_days: int | None = None,
    visibility: str | None = None,
    shareable_with: Iterable[str] | None = None,
    categories: Sequence[str] = (),
    exposure_id: str | None = None,
) -> str:
    eid = exposure_id or new_id("exposure")
    if shareable_with is None:
        parties = [counterparty_id] if counterparty_id else []
    else:
        parties = list(shareable_with)
    return insert(
        conn,
        "exposure",
        {
            "id": eid,
            "tenant_id": tenant_id,
            "kind": kind,
            "description": description,
            "counterparty_id": counterparty_id,
            "effective_from": effective_from,
            "expires_on": expires_on,
            "notice_days": notice_days,
            "status": "open",
            "visibility": visibility or default_visibility(categories),
            "shareable_with": parties,
            "provenance": provenance,
            "produced_by": produced_by,
        },
    )


# --- open loops, both directions -------------------------------------------


def open_loops(
    conn: sqlite3.Connection,
    tenant_id: str,
    *,
    counterparty_id: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Everything still open, split by direction.

    A-5: everything is tracked in both directions — owed by the principal and
    owed to them. This is the query that makes that true rather than merely
    stored.
    """
    params: list[Any] = [tenant_id]
    clause = "tenant_id = ? AND status = 'open' AND superseded_by IS NULL"
    if counterparty_id:
        clause += " AND counterparty_id = ?"
        params.append(counterparty_id)

    rows = conn.execute(
        f"SELECT * FROM commitment WHERE {clause} ORDER BY due IS NULL, due, made_at",
        params,
    ).fetchall()

    out: dict[str, list[dict[str, Any]]] = {
        "by_principal": [],
        "to_principal": [],
        "witnessed": [],
    }
    for row in rows:
        out[row["direction"]].append(dict(row))
    return out


def shareable_counterparties(record: dict[str, Any]) -> list[str]:
    return parse_shareable_with(record.get("shareable_with"))


# --- contact cadence --------------------------------------------------------
#
# `person.last_substantive_contact` is derived, never classified.
#
# The tempting version is a classifier over inbound mail deciding what counts
# as "substantive". That is a judgement the brief does not settle, and a wrong
# one fires a cadence alert on a relationship that is perfectly healthy —
# telling the principal to chase someone they spoke to on Tuesday. The cost of
# being wrong is asymmetric and lands on the principal's credibility.
#
# So it is computed from records that are already first-class and already carry
# provenance: a meeting they attended, or a commitment created or resolved with
# them. Both are things that demonstrably happened. The failure mode is that
# the date is older than reality — the register says "no substantive contact
# since June" when there was a corridor conversation in July — and silence in
# that direction is the right way to be wrong.


def derived_last_substantive_contact(
    conn: sqlite3.Connection, tenant_id: str, person_id: str
) -> str | None:
    """The most recent trusted contact date, or ``None`` if there is none.

    Sources, both of which are records rather than inferences:

    * a meeting the person attended — including a dark one, because attendance
      is known from the calendar even when the content is not
    * a commitment with them, at the point it was made or last acted on
    """
    row = conn.execute(
        """
        SELECT MAX(at) AS at FROM (
            SELECT m.starts_at AS at
            FROM meeting m
            JOIN meeting_attendee a ON a.meeting_id = m.id
            WHERE m.tenant_id = ? AND a.person_id = ?
            UNION ALL
            SELECT c.made_at AS at
            FROM commitment c
            WHERE c.tenant_id = ? AND c.counterparty_id = ? AND c.status != 'void'
            UNION ALL
            SELECT c.last_action_at AS at
            FROM commitment c
            WHERE c.tenant_id = ? AND c.counterparty_id = ?
              AND c.status != 'void' AND c.last_action_at IS NOT NULL
        )
        """,
        (tenant_id, person_id, tenant_id, person_id, tenant_id, person_id),
    ).fetchone()
    return str(row["at"]) if row and row["at"] else None


def refresh_last_substantive_contact(conn: sqlite3.Connection, tenant_id: str) -> int:
    """Recompute the cached column for every person. Returns rows changed.

    The column is a cache of :func:`derived_last_substantive_contact`, kept so
    that a brief does not have to run the union query per person. Nothing reads
    it that could not recompute it.
    """
    changed = 0
    for row in conn.execute(
        "SELECT id, last_substantive_contact FROM person WHERE tenant_id = ?", (tenant_id,)
    ).fetchall():
        derived = derived_last_substantive_contact(conn, tenant_id, str(row["id"]))
        if derived != row["last_substantive_contact"]:
            conn.execute(
                "UPDATE person SET last_substantive_contact = ?, updated_at = ? WHERE id = ?",
                (derived, now(), row["id"]),
            )
            changed += 1
    return changed


@dataclass(frozen=True)
class CadenceAlert:
    """A relationship that has gone quiet for longer than its stated cadence.

    Advisory only, and structurally so. This is a read-side computation that
    produces no record and touches no status; nothing in the send path consults
    it, and :func:`may_chase` does not know it exists. A quiet relationship is
    something to put in front of the principal in a digest, not a reason for an
    agent to contact anyone — the whole point of tracking cadence is to prompt a
    human judgement about whether the silence means anything.
    """

    person_id: str
    display_name: str
    cadence_days: int
    last_contact: str | None
    days_since: int | None

    @property
    def never_contacted(self) -> bool:
        return self.last_contact is None


def cadence_alerts(
    conn: sqlite3.Connection, tenant_id: str, *, as_of: str | None = None
) -> list[CadenceAlert]:
    """People overdue against their stated cadence, for the digest.

    Only people with an explicit ``cadence_days`` are considered: a cadence
    nobody set is not a cadence the register gets to invent.
    """
    today = date.fromisoformat(as_of) if as_of else datetime.now(UTC).date()
    out: list[CadenceAlert] = []

    for row in conn.execute(
        """
        SELECT id, display_name, cadence_days, last_substantive_contact
        FROM person
        WHERE tenant_id = ? AND cadence_days IS NOT NULL AND is_principal = 0
        ORDER BY display_name
        """,
        (tenant_id,),
    ).fetchall():
        last = row["last_substantive_contact"]
        days_since: int | None = None
        if last:
            try:
                days_since = (today - datetime.fromisoformat(last).date()).days
            except ValueError:
                days_since = None
            if days_since is not None and days_since <= int(row["cadence_days"]):
                continue
        out.append(
            CadenceAlert(
                person_id=str(row["id"]),
                display_name=str(row["display_name"]),
                cadence_days=int(row["cadence_days"]),
                last_contact=str(last) if last else None,
                days_since=days_since,
            )
        )
    return out
