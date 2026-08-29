"""CLAUDE.md §3 — no credential in plaintext in the register, the ledger, or any log.

`test_ingest.py` covers redaction on the ingest path. This file covers the
other half: text that reaches persistence through a named function rather than
through the ingest pipeline.

The two classes get different treatment, and the split is the point.

**Human free-text is redacted in place and the action succeeds.** A rejection
reason, a widening justification, a gap-reconciliation note, an AR status note
— each is a box a human types into. Blocking the action over a false positive
does not protect anything: the person still needs to reject the proposal, so
they do it by another route, and the behaviour leaves the audited path
entirely. A guardrail that teaches people to avoid it is worse than none.

**Machine-generated text is refused.** A credential in an extractor's candidate
or a model's Action Request is a defect in the producer, not a typist's slip.
There is no one to inconvenience and nothing worth preserving, so the write
fails at the point the defect was introduced.
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

# The false positive that must not block anyone. The matcher is deliberately
# aggressive, so this trips it — and a rejection reason is exactly where a
# person would write it.
FALSE_POSITIVE = "rejected because the password is wrong in their instructions"


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


def _queued_proposal(world) -> str:
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
    return proposal_id


# --- human free-text: redacted in place, action succeeds --------------------


def test_a_widening_reason_is_redacted_but_the_widening_happens(world):
    commitment_id = _commitment(world)
    principal = Reader(tenant_id=world.tenant, actor="aaron", role="principal")

    widening = widen_shareable_with(
        world.conn, principal, "commitment", commitment_id, [world.veldt], reason=SECRET
    )

    assert widening.added == [world.veldt]  # the act was not blocked
    reasons = [r["reason"] for r in world.conn.execute("SELECT reason FROM access_log")]
    assert all("hunter2hunter2" not in r for r in reasons)
    assert any("[REDACTED:" in r for r in reasons)


def test_a_rejection_reason_is_redacted_but_the_rejection_happens(world):
    proposal_id = _queued_proposal(world)

    reject(world.conn, world.tenant, proposal_id, actor="aaron", reason=SECRET)

    row = world.conn.execute(
        "SELECT state, resolved_by FROM curator_proposal WHERE id = ?", (proposal_id,)
    ).fetchone()
    assert row["state"] == "rejected"  # the action completed
    assert "hunter2hunter2" not in row["resolved_by"]
    assert "[REDACTED:" in row["resolved_by"]


def test_a_false_positive_does_not_block_the_action(world):
    """The case the redact-in-place rule exists for.

    "the password is wrong" trips an aggressive matcher and contains no secret.
    The reason loses a span and keeps its meaning; the rejection still happens.
    """
    proposal_id = _queued_proposal(world)

    reject(world.conn, world.tenant, proposal_id, actor="aaron", reason=FALSE_POSITIVE)

    row = world.conn.execute(
        "SELECT state, resolved_by FROM curator_proposal WHERE id = ?", (proposal_id,)
    ).fetchone()
    assert row["state"] == "rejected"
    assert "rejected because" in row["resolved_by"]  # the sense survives


def test_an_undo_reason_is_redacted_but_the_undo_happens(world):
    commitment_id = _commitment(world)

    undo(world.conn, world.tenant, commitment_id, actor="aaron", reason=SECRET)

    row = world.conn.execute(
        "SELECT status, last_action FROM commitment WHERE id = ?", (commitment_id,)
    ).fetchone()
    assert row["status"] == "void"  # the undo completed
    assert "hunter2hunter2" not in row["last_action"]


def test_a_gap_reconciliation_note_is_redacted_but_the_gap_clears(world):
    meeting_id = record_dark_meeting(
        world.conn,
        tenant_id=world.tenant,
        title="Henderson pricing",
        starts_at="2026-08-14T02:00:00+00:00",
        attendees=[world.principal, world.henderson],
        known_topics=["price"],
        produced_by="human:calendar-sync",
    )

    reconcile_gap(world.conn, meeting_id, SECRET, tenant_id=world.tenant)

    row = world.conn.execute(
        "SELECT gap_flag, capture_reason FROM meeting WHERE id = ?", (meeting_id,)
    ).fetchone()
    assert row["gap_flag"] == 0  # the gap cleared
    assert "hunter2hunter2" not in row["capture_reason"]


def test_an_ar_status_note_is_redacted_but_the_status_changes(world):
    ar_id = append_ar(world.conn, world.tenant, _ar())

    set_status(world.conn, world.tenant, ar_id, "accepted", actor="aaron", note=SECRET)

    from register.ledger import fold

    assert fold(world.conn, world.tenant, ar_id)["status"] == "accepted"
    payloads = [r["payload"] for r in world.conn.execute("SELECT payload FROM ar_ledger")]
    assert all("hunter2hunter2" not in p for p in payloads)


def test_an_ar_scoring_note_is_redacted_but_the_score_lands(world):
    ar_id = append_ar(world.conn, world.tenant, _ar())

    score(world.conn, world.tenant, ar_id, outcome="correct", actor="aaron", note=SECRET)

    row = world.conn.execute("SELECT outcome FROM prediction WHERE ar_id = ?", (ar_id,)).fetchone()
    assert row["outcome"] == "correct"
    payloads = [r["payload"] for r in world.conn.execute("SELECT payload FROM ar_ledger")]
    assert all("hunter2hunter2" not in p for p in payloads)


def test_a_commitment_statement_typed_by_a_human_is_redacted_not_refused(world):
    commitment_id = create_commitment(
        world.conn,
        tenant_id=world.tenant,
        direction="by_principal",
        statement=f"I'll set up their access — {SECRET}.",
        made_at="2026-08-10T09:00:00+00:00",
        source_type="manual",
        provenance="verbatim",
        produced_by="human:manual",
    )
    row = world.conn.execute(
        "SELECT statement FROM commitment WHERE id = ?", (commitment_id,)
    ).fetchone()
    assert "hunter2hunter2" not in row["statement"]
    assert "set up their access" in row["statement"]


# --- machine-generated: refused ---------------------------------------------


def test_an_extractor_candidate_carrying_a_secret_is_refused(world):
    """A credential in a candidate is a bug in the extractor, not a typo."""
    from register.extract import EXTRACTOR_ID
    from register.ids import new_id
    from register.store import insert

    with pytest.raises(ValueError, match="refusing to persist"):
        insert(
            world.conn,
            "curator_proposal",
            {
                "id": new_id("curator_proposal"),
                "tenant_id": world.tenant,
                "target_entity": "commitment",
                "candidate": f'{{"statement": "{SECRET}"}}',
                "confidence": 0.5,
                "source_ref": "ie_x",
                "state": "queued",
                "visibility": "principal_and_ea",
                "shareable_with": [],
                "provenance": "inferred",
                "produced_by": EXTRACTOR_ID,
            },
        )


def test_an_ar_claim_carrying_a_secret_is_refused(world):
    """The claim is model output. A secret there is a defect at the source."""
    with pytest.raises(ValueError, match="refusing to persist"):
        append_ar(world.conn, world.tenant, _ar(claim=f"Their staging box is open — {SECRET}."))


def test_a_refused_machine_write_leaves_the_ledger_untouched(world):
    append_ar(world.conn, world.tenant, _ar())
    before = world.conn.execute("SELECT count(*) AS n FROM ar_ledger").fetchone()["n"]
    with pytest.raises(ValueError):
        append_ar(world.conn, world.tenant, _ar(claim=f"Second claim — {SECRET}."))
    after = world.conn.execute("SELECT count(*) AS n FROM ar_ledger").fetchone()["n"]
    assert before == after


def test_a_prediction_carrying_a_secret_is_refused(world):
    with pytest.raises(ValueError, match="refusing to persist"):
        append_ar(
            world.conn,
            world.tenant,
            _ar(
                prediction=Prediction(
                    f"They rotate it — {SECRET}.", "2026-09-01", "the audit log", confidence=0.5
                )
            ),
        )


# --- the honest path is unchanged -------------------------------------------


def test_an_ordinary_reason_still_writes_verbatim(world):
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
    row = world.conn.execute(
        "SELECT reason FROM access_log WHERE reason LIKE 'widened%' ORDER BY id DESC LIMIT 1"
    ).fetchone()
    assert "disclosed in the data room on 14 Aug" in row["reason"]
    assert "[REDACTED:" not in row["reason"]
