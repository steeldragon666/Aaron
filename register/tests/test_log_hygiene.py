"""CLAUDE.md §3 — no credential in plaintext in the register, the ledger, or any log.

`test_ingest.py` covers redaction on the ingest path. This file covers the
other half, which is easier to miss: the human free-text fields that reach
persistence through a named function rather than through the ingest pipeline.

A rejection reason, a widening justification, a gap-reconciliation note, an AR
status note — each is a box a human types into, and a human pasting a
credential into a box is the ordinary case, not the adversarial one. Each of
these writes through raw SQL or through the ledger, so each needs the check
named at its own call site; there is no single choke point that catches them.
"""

from __future__ import annotations

import pytest

from register.access import Reader, widen_shareable_with
from register.curator import reject, undo
from register.entities import (
    create_commitment,
    reconcile_gap,
    record_dark_meeting,
)
from register.ledger import ActionRequest, Prediction, append_ar, score, set_status

SECRET = "the staging password is hunter2hunter2"


def _commitment(world) -> str:
    return create_commitment(
        world.conn,
        tenant_id=world.tenant,
        direction="to_principal",
        statement="Ruth will send the figures.",
        made_at="2026-08-10T09:00:00+00:00",
        source_type="email",
        provenance="verbatim",
        produced_by="human:manual",
        counterparty_id=world.henderson,
    )


def _ar(**overrides) -> ActionRequest:
    base = dict(
        agent="bram",
        claim="The cards report no ECC errors.",
        evidence=["docs/hardware/170HX_BUILD_SPEC.md"],
        recommendation="Burn one card for 48 hours first.",
        prediction=Prediction(
            "A checksum mismatch appears within 48 hours.",
            "2026-09-01",
            "the gpu-burn log",
            confidence=0.6,
        ),
        decision_required_by="2026-08-20",
        owner="aaron",
        effort="hours",
        produced_by="glm-5.2",
    )
    base.update(overrides)
    return ActionRequest(**base)


def test_a_widening_reason_cannot_carry_a_credential_into_the_access_log(world):
    commitment_id = _commitment(world)
    principal = Reader(tenant_id=world.tenant, actor="aaron", role="principal")

    with pytest.raises(ValueError, match="refusing to persist"):
        widen_shareable_with(
            world.conn, principal, "commitment", commitment_id, [world.veldt], reason=SECRET
        )

    rows = world.conn.execute("SELECT reason FROM access_log").fetchall()
    assert all("hunter2hunter2" not in row["reason"] for row in rows)


def test_a_rejection_reason_cannot_carry_a_credential(world):
    from register.extract import EXTRACTOR_ID
    from register.ids import new_id
    from register.store import insert

    proposal_id = new_id("curator_proposal")
    insert(
        world.conn,
        "curator_proposal",
        {
            "id": proposal_id,
            "tenant_id": world.tenant,
            "target_entity": "commitment",
            "candidate": "{}",
            "confidence": 0.5,
            "source_ref": "ie_x",
            "state": "queued",
            "visibility": "principal_and_ea",
            "shareable_with": [],
            "provenance": "inferred",
            "produced_by": EXTRACTOR_ID,
        },
    )
    with pytest.raises(ValueError, match="refusing to persist"):
        reject(world.conn, world.tenant, proposal_id, actor="aaron", reason=SECRET)

    row = world.conn.execute(
        "SELECT state, resolved_by FROM curator_proposal WHERE id = ?", (proposal_id,)
    ).fetchone()
    assert row["state"] == "queued"  # the write did not happen at all
    assert row["resolved_by"] is None


def test_an_undo_reason_cannot_carry_a_credential(world):
    commitment_id = _commitment(world)
    with pytest.raises(ValueError, match="refusing to persist"):
        undo(world.conn, world.tenant, commitment_id, actor="aaron", reason=SECRET)

    row = world.conn.execute(
        "SELECT status, last_action FROM commitment WHERE id = ?", (commitment_id,)
    ).fetchone()
    assert row["status"] == "open"
    assert row["last_action"] is None


def test_a_gap_reconciliation_note_cannot_carry_a_credential(world):
    meeting_id = record_dark_meeting(
        world.conn,
        tenant_id=world.tenant,
        title="Henderson pricing",
        starts_at="2026-08-14T02:00:00+00:00",
        attendees=[world.principal, world.henderson],
        known_topics=["price"],
        produced_by="human:calendar-sync",
    )
    with pytest.raises(ValueError, match="refusing to persist"):
        reconcile_gap(world.conn, meeting_id, SECRET)

    row = world.conn.execute("SELECT gap_flag FROM meeting WHERE id = ?", (meeting_id,)).fetchone()
    assert row["gap_flag"] == 1  # the gap did not clear on a refused write


def test_an_ar_status_note_cannot_carry_a_credential(world):
    ar_id = append_ar(world.conn, world.tenant, _ar())
    with pytest.raises(ValueError, match="refusing to persist"):
        set_status(world.conn, world.tenant, ar_id, "accepted", actor="aaron", note=SECRET)

    payloads = [
        row["payload"] for row in world.conn.execute("SELECT payload FROM ar_ledger").fetchall()
    ]
    assert all("hunter2hunter2" not in payload for payload in payloads)


def test_an_ar_scoring_note_cannot_carry_a_credential(world):
    ar_id = append_ar(world.conn, world.tenant, _ar())
    with pytest.raises(ValueError, match="refusing to persist"):
        score(world.conn, world.tenant, ar_id, outcome="correct", actor="aaron", note=SECRET)


def test_a_refused_write_leaves_the_record_untouched(world):
    """The check runs before the write, so a refusal is not a partial update."""
    ar_id = append_ar(world.conn, world.tenant, _ar())
    before = world.conn.execute("SELECT count(*) AS n FROM ar_ledger").fetchone()["n"]
    with pytest.raises(ValueError):
        set_status(world.conn, world.tenant, ar_id, "accepted", actor="aaron", note=SECRET)
    after = world.conn.execute("SELECT count(*) AS n FROM ar_ledger").fetchone()["n"]
    assert before == after


def test_an_ordinary_reason_still_writes(world):
    """The guard must not make the honest path unusable."""
    commitment_id = _commitment(world)
    principal = Reader(tenant_id=world.tenant, actor="aaron", role="principal")
    widening = widen_shareable_with(
        world.conn,
        principal,
        "commitment",
        commitment_id,
        [world.veldt],
        reason="disclosed in the data room on 14 Aug",
    )
    assert widening.added == [world.veldt]
