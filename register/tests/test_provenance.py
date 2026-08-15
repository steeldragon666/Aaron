"""Test priority 5 — provenance.

BUILD_BRIEF §4.5: nothing marked ``inferred`` is ever actionable without human
confirmation.

ACTION_TIER §4: ``provenance`` is what stops the agent chasing something nobody
said — never chase on ``inferred``; surface it to the principal as a question
instead.
"""

from __future__ import annotations

import pytest

from register.entities import assert_chaseable, create_commitment, may_chase
from register.errors import ProvenanceError
from register.invariants import PROVENANCE_LEVELS, is_actionable


def _commitment(world, provenance: str) -> dict:
    commitment_id = create_commitment(
        world.conn,
        tenant_id=world.tenant,
        direction="to_principal",
        statement="Ruth will send the figures.",
        made_at="2026-08-10T09:00:00+00:00",
        source_type="email",
        provenance=provenance,
        produced_by="human:manual",
        counterparty_id=world.henderson,
    )
    return dict(
        world.conn.execute("SELECT * FROM commitment WHERE id = ?", (commitment_id,)).fetchone()
    )


@pytest.mark.parametrize("provenance", PROVENANCE_LEVELS)
def test_only_verbatim_and_paraphrase_are_actionable(world, provenance):
    record = _commitment(world, provenance)
    verdict = may_chase(world.conn, record)
    assert verdict.allowed == (provenance != "inferred")
    assert is_actionable(provenance) == (provenance != "inferred")


def test_chasing_an_inferred_commitment_raises_rather_than_silently_skipping(world):
    record = _commitment(world, "inferred")
    with pytest.raises(ProvenanceError, match="surface to the principal as a question"):
        assert_chaseable(world.conn, record)


def test_confirming_an_inferred_commitment_is_an_explicit_rewrite(world):
    """There is no in-place promotion from inferred to actionable.

    ``provenance`` cannot be changed by a field update (it is on the forbidden
    list in :mod:`register.store`), so a human confirming an inference writes a
    new record and supersedes the old one. The inference stays in the history,
    which is what makes "why did it think that" answerable.
    """
    from register.entities import live_commitment, supersede_commitment
    from register.errors import InvariantError
    from register.store import update

    inferred = _commitment(world, "inferred")
    with pytest.raises(InvariantError):
        update(world.conn, "commitment", inferred["id"], {"provenance": "verbatim"})

    confirmed_id = create_commitment(
        world.conn,
        tenant_id=world.tenant,
        direction="to_principal",
        statement="Ruth will send the figures.",
        made_at=inferred["made_at"],
        source_type="manual",
        provenance="verbatim",
        produced_by="human:manual",
        counterparty_id=world.henderson,
    )
    supersede_commitment(world.conn, old_id=inferred["id"], new_id_=confirmed_id)

    live = live_commitment(world.conn, inferred["id"])
    assert live["id"] == confirmed_id
    assert may_chase(world.conn, live).allowed


def test_provenance_is_required_and_constrained(world):
    from register.errors import InvariantError
    from register.invariants import validate_invariants

    base = {
        "tenant_id": world.tenant,
        "visibility": "principal_and_ea",
        "shareable_with": "[]",
        "produced_by": "human:manual",
        "direction": "by_principal",
    }
    with pytest.raises(InvariantError, match="provenance"):
        validate_invariants("commitment", {**base, "provenance": None})
    with pytest.raises(InvariantError, match="provenance"):
        validate_invariants("commitment", {**base, "provenance": "probably"})
    validate_invariants("commitment", {**base, "provenance": "verbatim"})
