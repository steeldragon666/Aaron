"""Test priority 4 — supersession, and the dark-meeting interaction.

BUILD_BRIEF §4.4: a commitment superseded in a dark period must not be chased;
``gap_flag`` suppresses auto-action on affected threads.

BUILD_BRIEF §3.4: a commitment can be created, superseded and voided, with the
chain intact and queryable.
"""

from __future__ import annotations

import pytest
from tests.conftest import OTHER_TENANT

from register.entities import (
    create_commitment,
    dark_periods,
    live_commitment,
    may_chase,
    reconcile_gap,
    record_dark_meeting,
    supersede_commitment,
    supersession_chain,
    void_commitment,
)
from register.errors import GapSuppressed, RegisterError


def _commitment(world, statement: str, *, made_at="2026-08-10T09:00:00+00:00", **kwargs) -> str:
    return create_commitment(
        world.conn,
        tenant_id=world.tenant,
        direction="to_principal",
        statement=statement,
        made_at=made_at,
        source_type="email",
        provenance="verbatim",
        produced_by="human:manual",
        counterparty_id=world.henderson,
        **kwargs,
    )


def test_create_supersede_void_with_the_chain_intact(world):
    first = _commitment(world, "Ruth will send figures by Friday.")
    second = _commitment(world, "Ruth will send figures by the following Tuesday.")
    supersede_commitment(world.conn, tenant_id=world.tenant, old_id=first, new_id_=second)

    chain = supersession_chain(world.conn, first)
    assert [row["id"] for row in chain] == [first, second]
    assert chain[0]["status"] == "superseded"
    assert live_commitment(world.conn, first)["id"] == second

    void_commitment(world.conn, second, "Ruth left the company", tenant_id=world.tenant)
    assert live_commitment(world.conn, first)["status"] == "void"
    # Nothing was deleted — the history is still walkable.
    assert len(supersession_chain(world.conn, first)) == 2


def test_a_three_link_chain_resolves_to_the_last(world):
    a = _commitment(world, "Draft by Monday.")
    b = _commitment(world, "Draft by Wednesday.")
    c = _commitment(world, "Draft by Friday.")
    supersede_commitment(world.conn, tenant_id=world.tenant, old_id=a, new_id_=b)
    supersede_commitment(world.conn, tenant_id=world.tenant, old_id=b, new_id_=c)
    assert [row["id"] for row in supersession_chain(world.conn, a)] == [a, b, c]
    assert live_commitment(world.conn, a)["id"] == c


def test_a_commitment_cannot_supersede_itself_or_form_a_cycle(world):
    a = _commitment(world, "One.")
    b = _commitment(world, "Two.")
    with pytest.raises(RegisterError):
        supersede_commitment(world.conn, tenant_id=world.tenant, old_id=a, new_id_=a)

    supersede_commitment(world.conn, tenant_id=world.tenant, old_id=a, new_id_=b)
    with pytest.raises(RegisterError):
        supersede_commitment(world.conn, tenant_id=world.tenant, old_id=b, new_id_=a)


def test_a_superseded_commitment_is_not_chased(world):
    a = _commitment(world, "Figures by Friday.")
    b = _commitment(world, "Figures by Tuesday.")
    supersede_commitment(world.conn, tenant_id=world.tenant, old_id=a, new_id_=b)

    row = dict(world.conn.execute("SELECT * FROM commitment WHERE id = ?", (a,)).fetchone())
    verdict = may_chase(world.conn, row)
    assert not verdict.allowed


def test_a_dark_meeting_produces_a_loud_record(world):
    meeting_id = record_dark_meeting(
        world.conn,
        tenant_id=world.tenant,
        title="Henderson pricing",
        starts_at="2026-08-14T02:00:00+00:00",
        attendees=[world.principal, world.henderson],
        known_topics=["revised unit price", "delivery window"],
        produced_by="human:calendar-sync",
    )
    row = world.conn.execute("SELECT * FROM meeting WHERE id = ?", (meeting_id,)).fetchone()
    assert row["capture"] == "none"
    assert row["consent_outcome"] == "declined"
    assert row["capture_reason"] == "consent_declined"
    assert row["gap_flag"] == 1
    assert row["brief_issued"] == 1  # the brief precedes the consent question
    assert "revised unit price" in row["known_topics"]

    gaps = dark_periods(world.conn, world.tenant)
    assert [g["id"] for g in gaps] == [meeting_id]


def test_a_commitment_made_in_a_dark_meeting_is_not_chased(world):
    meeting_id = record_dark_meeting(
        world.conn,
        tenant_id=world.tenant,
        title="Henderson pricing",
        starts_at="2026-08-14T02:00:00+00:00",
        attendees=[world.principal, world.henderson],
        known_topics=["price"],
        produced_by="human:calendar-sync",
    )
    commitment_id = _commitment(
        world,
        "Ruth said she would confirm the price.",
        made_at="2026-08-14T02:30:00+00:00",
        made_in=meeting_id,
        made_in_kind="meeting",
    )
    row = dict(
        world.conn.execute("SELECT * FROM commitment WHERE id = ?", (commitment_id,)).fetchone()
    )
    verdict = may_chase(world.conn, row)
    assert not verdict.allowed
    assert verdict.reason.startswith("gap_flag")


def test_a_later_dark_meeting_suppresses_an_earlier_commitment(world):
    """The case the brief names: superseded in a room the agent never entered."""
    commitment_id = _commitment(
        world, "Ruth will send figures by Friday.", made_at="2026-08-10T09:00:00+00:00"
    )
    row = dict(
        world.conn.execute("SELECT * FROM commitment WHERE id = ?", (commitment_id,)).fetchone()
    )
    assert may_chase(world.conn, row).allowed

    meeting_id = record_dark_meeting(
        world.conn,
        tenant_id=world.tenant,
        title="Henderson catch-up",
        starts_at="2026-08-12T02:00:00+00:00",
        attendees=[world.principal, world.henderson],
        known_topics=["figures"],
        produced_by="human:calendar-sync",
    )
    assert not may_chase(world.conn, row).allowed

    from register.entities import assert_chaseable

    with pytest.raises(GapSuppressed):
        assert_chaseable(world.conn, row)

    # The voice dump is the recovery, and it clears the gap.
    reconcile_gap(
        world.conn, meeting_id, "principal voice dump, 90s, recorded 12 Aug", tenant_id=world.tenant
    )
    assert may_chase(world.conn, row).allowed
    assert dark_periods(world.conn, world.tenant) == []

    # The declined consent stays on the record forever; only the gap clears.
    after = world.conn.execute("SELECT * FROM meeting WHERE id = ?", (meeting_id,)).fetchone()
    assert after["consent_outcome"] == "declined"


def test_a_dark_meeting_with_a_different_counterparty_does_not_suppress(world):
    commitment_id = _commitment(world, "Ruth will send figures by Friday.")
    record_dark_meeting(
        world.conn,
        tenant_id=world.tenant,
        title="Veldt diligence",
        starts_at="2026-08-12T02:00:00+00:00",
        attendees=[world.principal, world.veldt],
        known_topics=["valuation"],
        produced_by="human:calendar-sync",
    )
    row = dict(
        world.conn.execute("SELECT * FROM commitment WHERE id = ?", (commitment_id,)).fetchone()
    )
    assert may_chase(world.conn, row).allowed


def test_reconciling_a_gap_requires_saying_how(world):
    meeting_id = record_dark_meeting(
        world.conn,
        tenant_id=world.tenant,
        title="Henderson pricing",
        starts_at="2026-08-14T02:00:00+00:00",
        attendees=[world.principal, world.henderson],
        known_topics=["price"],
        produced_by="human:calendar-sync",
    )
    with pytest.raises(ValueError):
        reconcile_gap(world.conn, meeting_id, "   ", tenant_id=world.tenant)


def test_both_directions_are_tracked(world):
    """Acceptance 3: things owed by the principal and things owed to them."""
    from register.entities import open_loops

    owed_by = create_commitment(
        world.conn,
        tenant_id=world.tenant,
        direction="by_principal",
        statement="I'll send Ruth the revised schedule.",
        made_at="2026-08-10T09:00:00+00:00",
        source_type="email",
        provenance="verbatim",
        produced_by="human:manual",
        counterparty_id=world.henderson,
    )
    owed_to = _commitment(world, "Ruth will send the figures.")

    loops = open_loops(world.conn, world.tenant)
    assert [row["id"] for row in loops["by_principal"]] == [owed_by]
    assert [row["id"] for row in loops["to_principal"]] == [owed_to]

    scoped = open_loops(world.conn, world.tenant, counterparty_id=world.veldt)
    assert scoped["by_principal"] == [] and scoped["to_principal"] == []


def test_a_commitment_cannot_be_superseded_twice(world):
    """The second call used to overwrite the first link and lose a branch.

    ``status`` was selected and never read, so superseding an already-superseded
    commitment silently repointed ``superseded_by``. :func:`supersession_chain`
    walks that column, so the overwritten replacement became unreachable — the
    register lost a version of what was agreed, which is the one thing this
    function exists to preserve.
    """
    a = _commitment(world, "Ruth will send the figures by Friday.")
    b = _commitment(world, "Ruth will send the figures by Monday.")
    c = _commitment(world, "Ruth will send the figures next quarter.")

    supersede_commitment(world.conn, tenant_id=world.tenant, old_id=a, new_id_=b)
    with pytest.raises(RegisterError, match="already superseded"):
        supersede_commitment(world.conn, tenant_id=world.tenant, old_id=a, new_id_=c)

    assert [row["id"] for row in supersession_chain(world.conn, a)] == [a, b]

    # The live record at the end of the chain is the one to supersede.
    supersede_commitment(world.conn, tenant_id=world.tenant, old_id=b, new_id_=c)
    assert [row["id"] for row in supersession_chain(world.conn, a)] == [a, b, c]


def test_supersession_cannot_reach_across_tenants(world):
    """Two ids used to be enough to link one client's record into another's chain.

    Uses the fixture's real second tenant rather than an invented id. A tenant
    that does not exist makes the predicate fail for two reasons at once —
    wrong owner *and* absent — so the test would pass even if ownership were
    never checked. One real client reaching into another's register is the case
    the title claims, and now the case it runs.
    """
    a = _commitment(world, "Ruth will send the figures by Friday.")
    b = _commitment(world, "Ruth will send the figures by Monday.")

    with pytest.raises(LookupError):
        supersede_commitment(world.conn, tenant_id=OTHER_TENANT, old_id=a, new_id_=b)

    result = world.conn.execute(
        "SELECT superseded_by, status FROM commitment WHERE id = ?", (a,)
    ).fetchone()
    assert result["superseded_by"] is None
    assert result["status"] == "open"


def test_voiding_cannot_reach_across_tenants(world):
    from register.errors import InvariantError

    a = _commitment(world, "Ruth will send the figures by Friday.")
    with pytest.raises(InvariantError, match="not found in tenant"):
        void_commitment(world.conn, a, "not mine to void", tenant_id=OTHER_TENANT)
    row = world.conn.execute("SELECT status FROM commitment WHERE id = ?", (a,)).fetchone()
    assert row["status"] == "open"
