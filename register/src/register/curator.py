"""The curator queue.

Write governance, per D-7 option C and ACTION_TIER §4:

* Facts from a **source of truth** — a calendar entry, an executed contract, a
  structured CRM field, a human typing into the register — write freely. They
  are re-derivable and auditable.
* Commitments extracted from **conversation** are *proposals*. They land here
  carrying a confidence score, the source reference, and the candidate fields.

Above a confidence threshold, proposals auto-confirm and appear in a daily
digest of what was confirmed. That is a deliberate design choice rather than a
shortcut: a per-item human gate will be skipped by week six, and a design that
assumes otherwise is wrong. The digest is the control — it is reviewable in one
sitting, and reversing a wrong auto-confirmation is one call.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from .canonical import canonical_json
from .entities import create_commitment, create_person
from .errors import RegisterError
from .extract import EXTRACTOR_ID, Candidate, extract_from_event
from .ids import new_id
from .ingest import unprocessed_events
from .invariants import default_visibility
from .redaction import assert_no_secrets
from .store import insert, now

# Above this, a proposal confirms itself and appears in the digest. Below it,
# it waits for a human. Tuned from the coverage run, not guessed at — see
# register.coverage.
DEFAULT_AUTO_CONFIRM_THRESHOLD = 0.85


# --- people -----------------------------------------------------------------


def resolve_person(
    conn: sqlite3.Connection,
    tenant_id: str,
    email: str,
    *,
    produced_by: str,
    display_name: str | None = None,
) -> str:
    """Find or create the person behind an email address.

    Creating a person from a message header is itself an inference — the
    address is verbatim, the identity behind it is not — so a person created
    this way carries ``provenance = paraphrase`` and can be corrected later
    without rewriting the commitments that point at it.
    """
    email = email.lower().strip()
    row = conn.execute(
        "SELECT id FROM person WHERE tenant_id = ? AND email = ?", (tenant_id, email)
    ).fetchone()
    if row is not None:
        return str(row["id"])

    return create_person(
        conn,
        tenant_id=tenant_id,
        display_name=display_name or email,
        email=email,
        produced_by=produced_by,
        provenance="paraphrase",
    )


def principal_emails(conn: sqlite3.Connection, tenant_id: str) -> list[str]:
    rows = conn.execute(
        "SELECT email FROM person WHERE tenant_id = ? AND is_principal = 1 AND email IS NOT NULL",
        (tenant_id,),
    ).fetchall()
    return [str(row["email"]).lower() for row in rows]


# --- proposing --------------------------------------------------------------


@dataclass
class ProposalReport:
    events_read: int = 0
    proposed: int = 0
    proposal_ids: list[str] = field(default_factory=list)


def _sender_of(event: Mapping[str, Any]) -> str | None:
    """The sender the adapter recorded on the ingest event.

    Stored at ingest rather than recovered here: the event body is redacted by
    the time it reaches the database, and re-parsing redacted text to find a
    header would be both fragile and pointless.
    """
    sender = event.get("sender")
    return str(sender).lower() if sender else None


def _participants_of(event: Mapping[str, Any]) -> list[str]:
    raw = event.get("participants")
    if not raw:
        return []
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return []
    return [str(item).lower() for item in raw]


def propose_from_events(
    conn: sqlite3.Connection,
    tenant_id: str,
    *,
    events: Sequence[Mapping[str, Any]] | None = None,
    senders: Mapping[str, str] | None = None,
    participants: Mapping[str, Sequence[str]] | None = None,
    reference: date | None = None,
) -> ProposalReport:
    """Extract candidates from unprocessed ingest events and queue them.

    ``senders`` and ``participants`` map ingest-event id to the addresses the
    adapter saw. They are passed in rather than re-read from the event body
    because the stored body is redacted, and re-parsing redacted text to
    recover a header would be both fragile and pointless.
    """
    report = ProposalReport()
    principals = principal_emails(conn, tenant_id)
    rows = list(events) if events is not None else unprocessed_events(conn, tenant_id)

    for event in rows:
        report.events_read += 1
        event_id = str(event["id"])
        sender = (senders or {}).get(event_id) or _sender_of(event)
        attendees = list((participants or {}).get(event_id) or _participants_of(event))

        candidates = extract_from_event(
            event,
            principal_emails=principals,
            sender=sender,
            participants=attendees,
            reference=reference,
        )
        for candidate in candidates:
            report.proposal_ids.append(_queue(conn, tenant_id, candidate, source_ref=event_id))
            report.proposed += 1

    return report


def _queue(
    conn: sqlite3.Connection,
    tenant_id: str,
    candidate: Candidate,
    *,
    source_ref: str,
) -> str:
    proposal_id = new_id("curator_proposal")
    insert(
        conn,
        "curator_proposal",
        {
            "id": proposal_id,
            "tenant_id": tenant_id,
            "target_entity": "commitment",
            "candidate": canonical_json(
                {
                    "statement": candidate.statement,
                    "direction": candidate.direction,
                    "due": candidate.due,
                    "made_at": candidate.made_at,
                    "source_type": candidate.source_type,
                    "provenance": candidate.provenance,
                    "counterparty_email": candidate.counterparty_email,
                    "shareable_with_emails": list(candidate.shareable_with_emails),
                    "pattern": candidate.pattern,
                }
            ),
            "confidence": candidate.confidence,
            "source_ref": source_ref,
            "state": "queued",
            "visibility": default_visibility(),
            "shareable_with": [],
            "provenance": candidate.provenance,
            "produced_by": EXTRACTOR_ID,
        },
    )
    return proposal_id


# --- confirming -------------------------------------------------------------


def queued(conn: sqlite3.Connection, tenant_id: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT * FROM curator_proposal
        WHERE tenant_id = ? AND state = 'queued'
        ORDER BY confidence DESC, created_at
        """,
        (tenant_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def confirm(
    conn: sqlite3.Connection,
    tenant_id: str,
    proposal_id: str,
    *,
    actor: str,
    auto: bool = False,
    overrides: Mapping[str, Any] | None = None,
) -> str:
    """Write the record a proposal describes, and close the proposal."""
    row = conn.execute(
        "SELECT * FROM curator_proposal WHERE tenant_id = ? AND id = ?",
        (tenant_id, proposal_id),
    ).fetchone()
    if row is None:
        raise LookupError(f"curator_proposal/{proposal_id} not found")
    if row["state"] != "queued":
        raise RegisterError(f"proposal {proposal_id} is already {row['state']}")
    if row["target_entity"] != "commitment":
        raise RegisterError(
            f"no writer for target_entity {row['target_entity']!r} — "
            "person, decision and exposure proposals arrive with their extractors"
        )

    candidate = json.loads(row["candidate"])
    candidate.update(overrides or {})

    counterparty_email = candidate.get("counterparty_email")
    counterparty_id = (
        resolve_person(conn, tenant_id, counterparty_email, produced_by=EXTRACTOR_ID)
        if counterparty_email
        else None
    )

    # shareable_with: the parties on the source item, and nobody else.
    shareable = [
        resolve_person(conn, tenant_id, addr, produced_by=EXTRACTOR_ID)
        for addr in candidate.get("shareable_with_emails", [])
    ]

    commitment_id = create_commitment(
        conn,
        tenant_id=tenant_id,
        direction=candidate["direction"],
        statement=candidate["statement"],
        made_at=candidate["made_at"],
        source_type=candidate["source_type"],
        provenance=candidate["provenance"],
        produced_by=EXTRACTOR_ID,
        counterparty_id=counterparty_id,
        confidence=float(row["confidence"]),
        due=candidate.get("due"),
        made_in=str(row["source_ref"]),
        made_in_kind="thread" if candidate["source_type"] == "email" else "manual",
        evidence_ref=str(row["source_ref"]),
        shareable_with=shareable,
    )

    conn.execute(
        """
        UPDATE curator_proposal
        SET state = ?, resolved_by = ?, resolved_at = ?, written_record_id = ?, updated_at = ?
        WHERE id = ?
        """,
        (
            "auto_confirmed" if auto else "confirmed",
            actor,
            now(),
            commitment_id,
            now(),
            proposal_id,
        ),
    )
    return commitment_id


def reject(
    conn: sqlite3.Connection,
    tenant_id: str,
    proposal_id: str,
    *,
    actor: str,
    reason: str = "",
) -> None:
    """Reject a proposal. Nothing is written to the register.

    Rejections stay in the queue table rather than being deleted: the ratio of
    rejected to confirmed proposals per pattern is how the extractor's rules
    get tuned, and it is the only signal that a rule has started over-firing.
    """
    assert_no_secrets(reason, "curator_proposal.resolved_by")
    conn.execute(
        """
        UPDATE curator_proposal
        SET state = 'rejected', resolved_by = ?, resolved_at = ?, updated_at = ?
        WHERE tenant_id = ? AND id = ? AND state = 'queued'
        """,
        (f"{actor}: {reason}" if reason else actor, now(), now(), tenant_id, proposal_id),
    )


@dataclass
class Digest:
    """What auto-confirmed, for the daily review."""

    auto_confirmed: list[dict[str, Any]] = field(default_factory=list)
    still_queued: int = 0
    threshold: float = DEFAULT_AUTO_CONFIRM_THRESHOLD

    def is_empty(self) -> bool:
        return not self.auto_confirmed


def auto_confirm(
    conn: sqlite3.Connection,
    tenant_id: str,
    *,
    threshold: float = DEFAULT_AUTO_CONFIRM_THRESHOLD,
    actor: str = "curator:auto",
) -> Digest:
    """Confirm every queued proposal at or above ``threshold``.

    Returns the digest. The digest is the human gate — not per item, but per
    day, which is a gate that survives contact with a busy principal.
    """
    digest = Digest(threshold=threshold)
    for proposal in queued(conn, tenant_id):
        if proposal["confidence"] < threshold:
            continue
        commitment_id = confirm(conn, tenant_id, proposal["id"], actor=actor, auto=True)
        candidate = json.loads(proposal["candidate"])
        digest.auto_confirmed.append(
            {
                "proposal_id": proposal["id"],
                "commitment_id": commitment_id,
                "confidence": proposal["confidence"],
                "direction": candidate["direction"],
                "statement": candidate["statement"],
                "due": candidate.get("due"),
                "source_ref": proposal["source_ref"],
            }
        )

    digest.still_queued = len(queued(conn, tenant_id))
    return digest


def undo(
    conn: sqlite3.Connection, tenant_id: str, commitment_id: str, *, actor: str, reason: str
) -> None:
    """Reverse an auto-confirmation.

    The commitment is voided rather than deleted — the register keeps its own
    history, including its mistakes, because "why did it think that" is a
    question worth being able to answer.
    """
    from .entities import void_commitment

    assert_no_secrets(reason, "curator_proposal.resolved_by")
    void_commitment(conn, commitment_id, f"{reason} (undone by {actor})")
    conn.execute(
        """
        UPDATE curator_proposal
        SET state = 'rejected', resolved_by = ?, resolved_at = ?, updated_at = ?
        WHERE tenant_id = ? AND written_record_id = ?
        """,
        (f"{actor}: undo — {reason}", now(), now(), tenant_id, commitment_id),
    )
