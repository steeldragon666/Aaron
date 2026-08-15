"""Test priority 3 — hash chain integrity, including tampering attempts.

Plus the ledger's three enforced rules: no prediction no AR, the cap of five
open ARs per agent, and scoring an AR nobody acted on.
"""

from __future__ import annotations

import json
import sqlite3

import pytest

from register.errors import (
    LedgerError,
    ModelBoundaryError,
    NoPredictionError,
    OpenARLimitError,
)
from register.ledger import (
    MAX_OPEN_ARS_PER_AGENT,
    ActionRequest,
    Prediction,
    append_ar,
    fold,
    open_ar_count,
    score,
    set_status,
    verify_chain,
)


def _ar(**overrides) -> ActionRequest:
    base = dict(
        agent="bram",
        claim="The 170HX cards will not report ECC errors, so burn-in is the only baseline available.",
        evidence=[
            "docs/hardware/170HX_BUILD_SPEC.md §RAM",
            "vendor datasheet, retrieved 2026-08-12",
        ],
        recommendation="Run 48h gpu-burn with checksum validation on card 1 before ordering the rest.",
        prediction=Prediction(
            statement="At least one of the eight cards shows a checksum mismatch within 48 hours.",
            resolves_on="2026-09-01",
            falsifiable_by="the gpu-burn log showing zero mismatches across all eight cards",
            confidence=0.6,
        ),
        decision_required_by="2026-08-20",
        owner="aaron",
        effort="hours",
        produced_by="glm-5.2",
    )
    base.update(overrides)
    return ActionRequest(**base)


# --- the three rules --------------------------------------------------------


def test_ar_without_a_falsifiable_prediction_is_rejected(world):
    with pytest.raises(NoPredictionError):
        append_ar(
            world.conn,
            world.tenant,
            _ar(prediction=Prediction("Things will improve.", "2026-09-01", "   ")),
        )


def test_ar_with_an_unparseable_resolution_date_is_rejected(world):
    with pytest.raises(NoPredictionError):
        append_ar(
            world.conn,
            world.tenant,
            _ar(prediction=Prediction("It lands.", "soon", "the log")),
        )


def test_ar_without_evidence_is_rejected(world):
    with pytest.raises(LedgerError):
        append_ar(world.conn, world.tenant, _ar(evidence=[]))


def test_sixth_open_ar_for_the_same_agent_is_rejected(world):
    for index in range(MAX_OPEN_ARS_PER_AGENT):
        append_ar(world.conn, world.tenant, _ar(claim=f"Claim {index} about the farm."))
    assert open_ar_count(world.conn, world.tenant, "bram") == MAX_OPEN_ARS_PER_AGENT

    with pytest.raises(OpenARLimitError):
        append_ar(world.conn, world.tenant, _ar(claim="One too many."))


def test_the_cap_is_per_agent(world):
    for index in range(MAX_OPEN_ARS_PER_AGENT):
        append_ar(world.conn, world.tenant, _ar(claim=f"Bram claim {index}."))
    # Hugh is unaffected by Bram's cap.
    hugh = append_ar(
        world.conn, world.tenant, _ar(agent="hugh", claim="Runway is 7 months, not 9.")
    )
    assert fold(world.conn, world.tenant, hugh)["agent"] == "hugh"


def test_closing_an_ar_makes_room_for_the_next(world):
    ids = [
        append_ar(world.conn, world.tenant, _ar(claim=f"Claim {i}."))
        for i in range(MAX_OPEN_ARS_PER_AGENT)
    ]
    set_status(world.conn, world.tenant, ids[0], "rejected", actor="aaron")
    assert open_ar_count(world.conn, world.tenant, "bram") == MAX_OPEN_ARS_PER_AGENT - 1
    append_ar(world.conn, world.tenant, _ar(claim="Now there is room."))


def test_unacted_ars_are_still_scored(world):
    ar_id = append_ar(world.conn, world.tenant, _ar())
    set_status(world.conn, world.tenant, ar_id, "rejected", actor="aaron", note="not this quarter")

    brier = score(world.conn, world.tenant, ar_id, outcome="correct", actor="aaron")

    row = world.conn.execute(
        "SELECT outcome, score, ar_was_acted_on FROM prediction WHERE ar_id = ?", (ar_id,)
    ).fetchone()
    assert row["outcome"] == "correct"
    assert row["ar_was_acted_on"] == 0  # the counterfactual, and it is recorded
    assert brier == pytest.approx((0.6 - 1.0) ** 2)
    assert row["score"] == pytest.approx(brier)


def test_brier_component_for_a_wrong_confident_prediction(world):
    ar_id = append_ar(
        world.conn,
        world.tenant,
        _ar(
            prediction=Prediction(
                "The RAM arrives before the cards.",
                "2026-09-15",
                "delivery dockets",
                confidence=0.9,
            )
        ),
    )
    set_status(world.conn, world.tenant, ar_id, "accepted", actor="aaron")
    brier = score(world.conn, world.tenant, ar_id, outcome="incorrect", actor="aaron")
    assert brier == pytest.approx(0.81)


def test_a_terminal_ar_cannot_be_reopened(world):
    ar_id = append_ar(world.conn, world.tenant, _ar())
    set_status(world.conn, world.tenant, ar_id, "executed", actor="aaron")
    with pytest.raises(LedgerError):
        set_status(world.conn, world.tenant, ar_id, "in_progress", actor="aaron")


# --- the chain --------------------------------------------------------------


def test_chain_verifies_end_to_end(world):
    ids = [append_ar(world.conn, world.tenant, _ar(claim=f"Claim {i}.")) for i in range(3)]
    set_status(world.conn, world.tenant, ids[0], "accepted", actor="aaron")
    score(world.conn, world.tenant, ids[0], outcome="correct", actor="aaron")

    report = verify_chain(world.conn)
    assert report.ok
    assert report.entries == 5  # 3 opens + 1 status + 1 outcome
    assert report.broken_at is None


def test_tampering_with_a_payload_breaks_the_chain(world):
    append_ar(world.conn, world.tenant, _ar())
    ar_id = append_ar(world.conn, world.tenant, _ar(claim="Second claim."))
    append_ar(world.conn, world.tenant, _ar(claim="Third claim."))

    # The trigger blocks the honest route.
    with pytest.raises(sqlite3.DatabaseError, match="append-only"):
        world.conn.execute("UPDATE ar_ledger SET payload = '{}' WHERE ar_id = ?", (ar_id,))

    # So tamper the way an attacker with host access would: drop the trigger
    # first. The chain must still catch it.
    world.conn.execute("DROP TRIGGER ar_ledger_no_update")
    row = world.conn.execute(
        "SELECT seq, payload FROM ar_ledger WHERE ar_id = ?", (ar_id,)
    ).fetchone()
    payload = json.loads(row["payload"])
    payload["claim"] = "A claim that was never made."
    world.conn.execute(
        "UPDATE ar_ledger SET payload = ? WHERE seq = ?",
        (json.dumps(payload, sort_keys=True, separators=(",", ":")), row["seq"]),
    )

    report = verify_chain(world.conn)
    assert not report.ok
    assert report.broken_at == row["seq"]
    assert "tampered" in report.detail


def test_deleting_an_entry_breaks_the_chain(world):
    for index in range(3):
        append_ar(world.conn, world.tenant, _ar(claim=f"Claim {index}."))

    with pytest.raises(sqlite3.DatabaseError, match="append-only"):
        world.conn.execute("DELETE FROM ar_ledger WHERE seq = 2")

    world.conn.execute("DROP TRIGGER ar_ledger_no_delete")
    world.conn.execute("DELETE FROM ar_ledger WHERE seq = 2")

    report = verify_chain(world.conn)
    assert not report.ok
    assert report.broken_at == 3
    assert "sequence gap" in report.detail


def test_reordering_entries_breaks_the_chain(world):
    a = append_ar(world.conn, world.tenant, _ar(claim="First."))
    append_ar(world.conn, world.tenant, _ar(claim="Second."))
    set_status(world.conn, world.tenant, a, "accepted", actor="aaron")

    world.conn.execute("DROP TRIGGER ar_ledger_no_update")
    # Swap two payloads. Every hash stays syntactically valid; the chain does not.
    rows = world.conn.execute("SELECT seq, payload FROM ar_ledger ORDER BY seq").fetchall()
    world.conn.execute(
        "UPDATE ar_ledger SET payload = ? WHERE seq = ?", (rows[1]["payload"], rows[0]["seq"])
    )
    world.conn.execute(
        "UPDATE ar_ledger SET payload = ? WHERE seq = ?", (rows[0]["payload"], rows[1]["seq"])
    )

    assert not verify_chain(world.conn).ok


def test_ledger_is_append_only_by_trigger(world):
    ar_id = append_ar(world.conn, world.tenant, _ar())
    with pytest.raises(sqlite3.DatabaseError, match="append-only"):
        world.conn.execute("UPDATE ar_ledger SET agent = 'elena' WHERE ar_id = ?", (ar_id,))
    with pytest.raises(sqlite3.DatabaseError, match="append-only"):
        world.conn.execute("DELETE FROM ar_ledger WHERE ar_id = ?", (ar_id,))


def test_status_changes_append_rather_than_mutate(world):
    ar_id = append_ar(world.conn, world.tenant, _ar())
    set_status(world.conn, world.tenant, ar_id, "accepted", actor="aaron")
    set_status(world.conn, world.tenant, ar_id, "executed", actor="aaron")

    kinds = [
        row["entry_kind"]
        for row in world.conn.execute(
            "SELECT entry_kind FROM ar_ledger WHERE ar_id = ? ORDER BY seq", (ar_id,)
        )
    ]
    assert kinds == ["open", "status", "status"]
    assert fold(world.conn, world.tenant, ar_id)["status"] == "executed"
    assert verify_chain(world.conn).ok


# --- the model boundary -----------------------------------------------------


def test_a_code_only_model_may_not_produce_an_action_request(world):
    with pytest.raises(ModelBoundaryError):
        append_ar(world.conn, world.tenant, _ar(produced_by="deepseek-v4-pro"))


def test_produced_by_is_recorded_on_every_entry(world):
    """S-13: the field exists before the data that depends on it."""
    ar_id = append_ar(world.conn, world.tenant, _ar())
    set_status(world.conn, world.tenant, ar_id, "accepted", actor="aaron")
    produced = {
        row["produced_by"]
        for row in world.conn.execute("SELECT produced_by FROM ar_ledger WHERE ar_id = ?", (ar_id,))
    }
    assert produced == {"glm-5.2"}
