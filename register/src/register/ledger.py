"""The Action Request ledger — append-only, hash-chained.

The AR is the billable unit: a dated, owned, falsifiable proposal with a
predicted outcome. No prediction, no AR.

Three rules are enforced here in code rather than by convention, because each
one is a rule that gets bent under pressure:

* **No prediction, no AR.** Observations go to an appendix. An AR without a
  falsifiable prediction is a report, and reports cannot be scored.
* **Hard cap of five open ARs per agent.** Anti volume-padding. The cap counts
  open ARs, so closing one is what makes room for the next.
* **Unacted ARs are still scored.** The counterfactual is the most valuable
  training data in the system, and it is only available if the prediction was
  recorded and resolved whether or not anybody acted on it.

Nothing in the ledger is ever updated. Status changes, outcomes and scores are
appended as further entries, and an AR's current state is a fold over its
entries. The chain covers every entry, so a tampered payload anywhere breaks
verification from that point on.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Any

from .canonical import GENESIS_HASH, canonical_json, chain_hash
from .errors import (
    ChainBroken,
    LedgerError,
    NoPredictionError,
    OpenARLimitError,
)
from .ids import new_id
from .invariants import default_visibility, normalise_shareable_with, validate_invariants
from .redaction import assert_no_secrets
from .routing import assert_may_produce
from .store import now

MAX_OPEN_ARS_PER_AGENT = 5

OPEN_STATUSES = frozenset({"proposed", "accepted", "in_progress"})
TERMINAL_STATUSES = frozenset({"executed", "rejected", "expired", "void"})
ALL_STATUSES = OPEN_STATUSES | TERMINAL_STATUSES

EFFORT_LEVELS = frozenset({"minutes", "hours", "days", "weeks"})


@dataclass(frozen=True)
class Prediction:
    """The thing that makes an AR an AR.

    ``falsifiable_by`` is not decoration: it names the observation that would
    show the prediction wrong. A prediction nobody could falsify cannot be
    scored, and an unscoreable AR is exactly the artifact this system exists to
    refuse.
    """

    statement: str
    resolves_on: str  # ISO date
    falsifiable_by: str
    confidence: float | None = None

    def validate(self) -> None:
        if not self.statement.strip():
            raise NoPredictionError("prediction.statement is empty")
        if not self.falsifiable_by.strip():
            raise NoPredictionError(
                "prediction.falsifiable_by is empty — name the observation that "
                "would show this wrong, or this is an observation, not an AR"
            )
        try:
            date.fromisoformat(self.resolves_on)
        except (TypeError, ValueError) as exc:
            raise NoPredictionError(
                f"prediction.resolves_on {self.resolves_on!r} is not an ISO date"
            ) from exc
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise NoPredictionError("prediction.confidence must be between 0 and 1")

    def as_dict(self) -> dict[str, Any]:
        return {
            "statement": self.statement,
            "resolves_on": self.resolves_on,
            "falsifiable_by": self.falsifiable_by,
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class ActionRequest:
    agent: str
    claim: str
    evidence: Sequence[str]
    recommendation: str
    prediction: Prediction
    decision_required_by: str
    owner: str
    effort: str
    visibility: str | None = None
    shareable_with: Sequence[str] = field(default_factory=tuple)
    produced_by: str = ""
    provenance: str = "paraphrase"
    categories: Sequence[str] = field(default_factory=tuple)

    def validate(self) -> None:
        if not self.agent.strip():
            raise LedgerError("agent is required")
        if not self.claim.strip():
            raise LedgerError("claim is required")
        if not self.evidence:
            raise LedgerError(
                "evidence is required — every claim carries a source; "
                "unsourced claims are marked, not smoothed"
            )
        if not self.recommendation.strip():
            raise LedgerError("recommendation is required")
        if not self.owner.strip():
            raise LedgerError("owner is required — an AR nobody owns is an observation")
        if self.effort not in EFFORT_LEVELS:
            raise LedgerError(f"effort must be one of {sorted(EFFORT_LEVELS)}")
        try:
            date.fromisoformat(self.decision_required_by)
        except (TypeError, ValueError) as exc:
            raise LedgerError("decision_required_by must be an ISO date") from exc
        if not self.produced_by.strip():
            raise LedgerError("produced_by is required, even while there is only one model")
        self.prediction.validate()


# --- appending --------------------------------------------------------------


def _head(conn: sqlite3.Connection) -> tuple[int, str]:
    """Return ``(seq, entry_hash)`` of the last entry, or the genesis pair."""
    row = conn.execute("SELECT seq, entry_hash FROM ar_ledger ORDER BY seq DESC LIMIT 1").fetchone()
    if row is None:
        return 0, GENESIS_HASH
    return int(row["seq"]), str(row["entry_hash"])


def _append(
    conn: sqlite3.Connection,
    *,
    tenant_id: str,
    ar_id: str,
    entry_kind: str,
    agent: str,
    payload: Mapping[str, Any],
    visibility: str,
    shareable_with: Iterable[str],
    provenance: str,
    produced_by: str,
) -> str:
    payload_json = canonical_json(payload)
    assert_no_secrets(payload_json, "ar_ledger.payload")

    row = {
        "tenant_id": tenant_id,
        "ar_id": ar_id,
        "entry_kind": entry_kind,
        "agent": agent,
        "payload": payload_json,
        "visibility": visibility,
        "shareable_with": normalise_shareable_with(list(shareable_with)),
        "provenance": provenance,
        "produced_by": produced_by,
    }
    validate_invariants("ar_ledger", row)
    assert_may_produce(produced_by, "action_request")

    prev_seq, prev_hash = _head(conn)
    seq = prev_seq + 1
    entry_hash = chain_hash(seq, prev_hash, payload_json)

    conn.execute(
        """
        INSERT INTO ar_ledger
            (seq, tenant_id, ar_id, entry_kind, agent, payload, prev_hash, entry_hash,
             appended_at, visibility, shareable_with, provenance, produced_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            seq,
            row["tenant_id"],
            row["ar_id"],
            row["entry_kind"],
            row["agent"],
            row["payload"],
            prev_hash,
            entry_hash,
            now(),
            row["visibility"],
            row["shareable_with"],
            row["provenance"],
            row["produced_by"],
        ),
    )
    return entry_hash


def open_ar_count(conn: sqlite3.Connection, tenant_id: str, agent: str) -> int:
    return sum(
        1
        for state in fold_all(conn, tenant_id).values()
        if state["agent"] == agent and state["status"] in OPEN_STATUSES
    )


def append_ar(conn: sqlite3.Connection, tenant_id: str, ar: ActionRequest) -> str:
    """Append a new AR. Returns its id.

    Raises :class:`NoPredictionError` if the prediction is missing or
    unfalsifiable, and :class:`OpenARLimitError` on the sixth open AR for the
    same agent.
    """
    ar.validate()

    if open_ar_count(conn, tenant_id, ar.agent) >= MAX_OPEN_ARS_PER_AGENT:
        raise OpenARLimitError(
            f"{ar.agent} already has {MAX_OPEN_ARS_PER_AGENT} open ARs. "
            "Close one before proposing another — the cap is the anti-padding rule."
        )

    ar_id = new_id("ar")
    visibility = ar.visibility or default_visibility(ar.categories)
    payload = {
        "id": ar_id,
        "agent": ar.agent,
        "tenant_id": tenant_id,
        "claim": ar.claim,
        "evidence": list(ar.evidence),
        "recommendation": ar.recommendation,
        "prediction": ar.prediction.as_dict(),
        "decision_required_by": ar.decision_required_by,
        "owner": ar.owner,
        "effort": ar.effort,
        "status": "proposed",
        "outcome": None,
        "score": None,
        "produced_by": ar.produced_by,
    }

    _append(
        conn,
        tenant_id=tenant_id,
        ar_id=ar_id,
        entry_kind="open",
        agent=ar.agent,
        payload=payload,
        visibility=visibility,
        shareable_with=ar.shareable_with,
        provenance=ar.provenance,
        produced_by=ar.produced_by,
    )

    # Projection for scoring. The ledger is the record of truth; this table is
    # the queryable view of the outstanding predictions.
    from .store import insert as _insert

    _insert(
        conn,
        "prediction",
        {
            "id": new_id("prediction"),
            "tenant_id": tenant_id,
            "ar_id": ar_id,
            "agent": ar.agent,
            "statement": ar.prediction.statement,
            "resolves_on": ar.prediction.resolves_on,
            "falsifiable_by": ar.prediction.falsifiable_by,
            "stated_confidence": ar.prediction.confidence,
            "outcome": None,
            "score": None,
            "resolved_at": None,
            "ar_was_acted_on": None,
            "visibility": visibility,
            "shareable_with": list(ar.shareable_with),
            "provenance": ar.provenance,
            "produced_by": ar.produced_by,
        },
        artifact="prediction",
    )
    return ar_id


def set_status(
    conn: sqlite3.Connection,
    tenant_id: str,
    ar_id: str,
    status: str,
    *,
    actor: str,
    note: str = "",
) -> str:
    """Append a status change. The previous entry is left untouched."""
    if status not in ALL_STATUSES:
        raise LedgerError(f"unknown AR status {status!r}")
    state = fold(conn, tenant_id, ar_id)
    if state is None:
        raise LedgerError(f"no such AR: {ar_id}")
    if state["status"] in TERMINAL_STATUSES and status in OPEN_STATUSES:
        raise LedgerError(
            f"AR {ar_id} is {state['status']} and cannot be reopened — propose a new AR instead"
        )

    return _append(
        conn,
        tenant_id=tenant_id,
        ar_id=ar_id,
        entry_kind="status",
        agent=state["agent"],
        payload={"id": ar_id, "status": status, "actor": actor, "note": note},
        visibility=state["visibility"],
        shareable_with=state["shareable_with"],
        provenance=state["provenance"],
        produced_by=state["produced_by"],
    )


def score(
    conn: sqlite3.Connection,
    tenant_id: str,
    ar_id: str,
    *,
    outcome: str,
    actor: str,
    resolved_at: str | None = None,
    note: str = "",
) -> float:
    """Resolve an AR's prediction and record its Brier component.

    Scoring does not care whether the AR was acted on. An AR the principal
    declined still had a prediction attached, and whether that prediction came
    true is the counterfactual — the most valuable training data in the system,
    and the only thing that distinguishes an agent that is right from one that
    has learned what gets approved.
    """
    if outcome not in ("correct", "incorrect", "unresolved", "void"):
        raise LedgerError(f"unknown outcome {outcome!r}")

    state = fold(conn, tenant_id, ar_id)
    if state is None:
        raise LedgerError(f"no such AR: {ar_id}")

    row = conn.execute(
        "SELECT * FROM prediction WHERE tenant_id = ? AND ar_id = ?", (tenant_id, ar_id)
    ).fetchone()
    if row is None:  # pragma: no cover - append_ar always writes one
        raise LedgerError(f"AR {ar_id} has no prediction projection")

    brier = _brier(row["stated_confidence"], outcome)
    was_acted_on = state["status"] in ("accepted", "in_progress", "executed")
    stamp = resolved_at or datetime.now(UTC).date().isoformat()

    conn.execute(
        """
        UPDATE prediction
        SET outcome = ?, score = ?, resolved_at = ?, ar_was_acted_on = ?, updated_at = ?
        WHERE tenant_id = ? AND ar_id = ?
        """,
        (outcome, brier, stamp, 1 if was_acted_on else 0, now(), tenant_id, ar_id),
    )

    _append(
        conn,
        tenant_id=tenant_id,
        ar_id=ar_id,
        entry_kind="outcome",
        agent=state["agent"],
        payload={
            "id": ar_id,
            "outcome": outcome,
            "score": brier,
            "was_acted_on": was_acted_on,
            "resolved_at": stamp,
            "actor": actor,
            "note": note,
        },
        visibility=state["visibility"],
        shareable_with=state["shareable_with"],
        provenance=state["provenance"],
        produced_by=state["produced_by"],
    )
    return brier if brier is not None else float("nan")


def _brier(confidence: float | None, outcome: str) -> float | None:
    """Brier component for a single binary prediction.

    ``None`` when the prediction carried no stated confidence, or when the
    outcome cannot be scored. A prediction with no confidence is still resolved
    and still counted — it just contributes to accuracy rather than to
    calibration.
    """
    if outcome in ("unresolved", "void") or confidence is None:
        return None
    actual = 1.0 if outcome == "correct" else 0.0
    return (float(confidence) - actual) ** 2


# --- reading ----------------------------------------------------------------


def _fold_entries(entries: Sequence[Mapping[str, Any]]) -> dict[str, Any] | None:
    state: dict[str, Any] | None = None
    for entry in entries:
        payload = json.loads(entry["payload"])
        if entry["entry_kind"] == "open":
            state = dict(payload)
            state["visibility"] = entry["visibility"]
            state["shareable_with"] = json.loads(entry["shareable_with"])
            state["provenance"] = entry["provenance"]
            state["produced_by"] = entry["produced_by"]
            state["opened_at"] = entry["appended_at"]
        elif state is None:  # pragma: no cover - defensive
            continue
        elif entry["entry_kind"] == "status":
            state["status"] = payload["status"]
        elif entry["entry_kind"] == "outcome":
            state["outcome"] = payload["outcome"]
            state["score"] = payload["score"]
            state["was_acted_on"] = payload["was_acted_on"]
        elif entry["entry_kind"] == "void":
            state["status"] = "void"
    return state


def fold(conn: sqlite3.Connection, tenant_id: str, ar_id: str) -> dict[str, Any] | None:
    entries = conn.execute(
        "SELECT * FROM ar_ledger WHERE tenant_id = ? AND ar_id = ? ORDER BY seq",
        (tenant_id, ar_id),
    ).fetchall()
    return _fold_entries(entries)


def fold_all(conn: sqlite3.Connection, tenant_id: str) -> dict[str, dict[str, Any]]:
    """Current state of every AR for a tenant, keyed by AR id."""
    entries = conn.execute(
        "SELECT * FROM ar_ledger WHERE tenant_id = ? ORDER BY seq", (tenant_id,)
    ).fetchall()
    grouped: dict[str, list[Mapping[str, Any]]] = {}
    for entry in entries:
        grouped.setdefault(entry["ar_id"], []).append(entry)
    out: dict[str, dict[str, Any]] = {}
    for ar_id, rows in grouped.items():
        state = _fold_entries(rows)
        if state is not None:
            out[ar_id] = state
    return out


# --- verification -----------------------------------------------------------


@dataclass(frozen=True)
class ChainReport:
    entries: int
    head: str
    ok: bool
    broken_at: int | None = None
    detail: str = ""


def verify_chain(conn: sqlite3.Connection, *, raise_on_break: bool = False) -> ChainReport:
    """Walk the whole chain and recompute every link.

    The chain is global rather than per-tenant. With one tenant that choice is
    invisible; with several it means a tenant cannot be silently removed from
    the ledger without breaking verification for everyone, which is the
    property worth having.
    """
    rows = conn.execute("SELECT * FROM ar_ledger ORDER BY seq").fetchall()
    prev_hash = GENESIS_HASH
    expected_seq = 1

    for row in rows:
        seq = int(row["seq"])
        if seq != expected_seq:
            report = ChainReport(
                len(rows),
                prev_hash,
                False,
                seq,
                f"sequence gap: expected {expected_seq}, found {seq}",
            )
            if raise_on_break:
                raise ChainBroken(report.detail)
            return report
        if row["prev_hash"] != prev_hash:
            report = ChainReport(
                len(rows), prev_hash, False, seq, f"prev_hash mismatch at seq {seq}"
            )
            if raise_on_break:
                raise ChainBroken(report.detail)
            return report

        recomputed = chain_hash(seq, prev_hash, row["payload"])
        if recomputed != row["entry_hash"]:
            report = ChainReport(len(rows), prev_hash, False, seq, f"payload tampered at seq {seq}")
            if raise_on_break:
                raise ChainBroken(report.detail)
            return report

        prev_hash = str(row["entry_hash"])
        expected_seq += 1

    return ChainReport(len(rows), prev_hash, True)
