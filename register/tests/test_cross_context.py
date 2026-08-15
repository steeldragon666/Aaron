"""Test priority 1 — cross-context leak.

BUILD_BRIEF §4: seed and attempt retrieval across counterparty boundaries.
Adversarial, not happy-path.

The rule (CLAUDE.md §4, ACTION_TIER §3): an agent may reference to a
counterparty only facts that counterparty is already party to, or that are
explicitly listed in that record's ``shareable_with``.

These tests attack it from every direction available to a caller: the
single-record read, the scoped query, the entity constructors' defaults, the
widening path, and the ledger. If any of them can be made to return a fact
outside its shareable set, the product's highest-consequence constraint is
broken.
"""

from __future__ import annotations

import pytest

from register.access import Reader, query, read_one, widen_shareable_with
from register.entities import (
    create_commitment,
    create_decision,
    create_exposure,
    create_meeting,
    create_thread,
)
from register.errors import AccessDenied, CrossContextViolation, InvariantError
from register.invariants import parse_shareable_with


def _seed_henderson_fact(world) -> str:
    """A fact known only to Henderson."""
    return create_commitment(
        world.conn,
        tenant_id=world.tenant,
        direction="to_principal",
        statement="Ruth will send the revised Henderson figures by Friday.",
        made_at="2026-08-10T09:00:00+00:00",
        source_type="email",
        provenance="verbatim",
        produced_by="human:manual",
        counterparty_id=world.henderson,
    )


def test_fact_from_counterparty_a_is_invisible_in_counterparty_b_context(world):
    commitment_id = _seed_henderson_fact(world)

    to_veldt = Reader(
        tenant_id=world.tenant, actor="bram", role="principal", counterparty_scope=world.veldt
    )
    with pytest.raises(CrossContextViolation):
        read_one(world.conn, to_veldt, "commitment", commitment_id)

    # And it must not appear in a scoped listing either — a caller must not be
    # able to infer its existence from a query.
    assert query(world.conn, to_veldt, "commitment") == []


def test_fact_is_visible_in_its_own_counterparty_context(world):
    commitment_id = _seed_henderson_fact(world)
    to_henderson = Reader(
        tenant_id=world.tenant, actor="bram", role="principal", counterparty_scope=world.henderson
    )
    record = read_one(world.conn, to_henderson, "commitment", commitment_id)
    assert record is not None
    assert record["id"] == commitment_id


def test_internal_read_is_unscoped_and_still_sees_it(world):
    """The rule constrains what may be *said to* a counterparty, not what the
    principal may see about their own business."""
    commitment_id = _seed_henderson_fact(world)
    internal = Reader(tenant_id=world.tenant, actor="aaron", role="principal")
    assert read_one(world.conn, internal, "commitment", commitment_id) is not None


@pytest.mark.parametrize(
    "constructor,kwargs,expected_key",
    [
        (
            create_commitment,
            dict(
                direction="by_principal",
                statement="I'll send the deck.",
                made_at="2026-08-10T09:00:00+00:00",
                source_type="email",
                provenance="verbatim",
            ),
            "counterparty",
        ),
        (
            create_exposure,
            dict(kind="renewal", description="Hosting renews", provenance="verbatim"),
            "counterparty",
        ),
    ],
)
def test_constructors_default_to_the_parties_present(world, constructor, kwargs, expected_key):
    record_id = constructor(
        world.conn,
        tenant_id=world.tenant,
        produced_by="human:manual",
        counterparty_id=world.henderson,
        **kwargs,
    )
    table = "commitment" if constructor is create_commitment else "exposure"
    row = world.conn.execute(
        f"SELECT shareable_with FROM {table} WHERE id = ?", (record_id,)
    ).fetchone()
    assert parse_shareable_with(row["shareable_with"]) == [world.henderson]


def test_commitment_with_no_counterparty_defaults_to_deny(world):
    commitment_id = create_commitment(
        world.conn,
        tenant_id=world.tenant,
        direction="by_principal",
        statement="I'll rewrite the pricing model.",
        made_at="2026-08-10T09:00:00+00:00",
        source_type="manual",
        provenance="verbatim",
        produced_by="human:manual",
    )
    row = world.conn.execute(
        "SELECT shareable_with FROM commitment WHERE id = ?", (commitment_id,)
    ).fetchone()
    assert parse_shareable_with(row["shareable_with"]) == []

    for counterparty in (world.henderson, world.veldt):
        scoped = Reader(
            tenant_id=world.tenant, actor="bram", role="principal", counterparty_scope=counterparty
        )
        with pytest.raises(CrossContextViolation):
            read_one(world.conn, scoped, "commitment", commitment_id)


def test_meeting_thread_and_decision_default_to_their_attendees(world):
    meeting_id = create_meeting(
        world.conn,
        tenant_id=world.tenant,
        title="Henderson supply review",
        starts_at="2026-08-11T01:00:00+00:00",
        produced_by="human:calendar-sync",
        attendees=[world.principal, world.henderson],
    )
    thread_id = create_thread(
        world.conn,
        tenant_id=world.tenant,
        subject="Revised figures",
        produced_by="human:mailbox-sync",
        counterparties=[world.henderson],
    )
    decision_id = create_decision(
        world.conn,
        tenant_id=world.tenant,
        statement="Hold the Henderson order until the figures land.",
        reasoning_at_time="Unit economics do not clear at the quoted price.",
        decided_at="2026-08-11T02:00:00+00:00",
        produced_by="human:manual",
        participants=[world.principal],
    )

    to_veldt = Reader(
        tenant_id=world.tenant, actor="hugh", role="principal", counterparty_scope=world.veldt
    )
    for entity, record_id in (
        ("meeting", meeting_id),
        ("thread", thread_id),
        ("decision", decision_id),
    ):
        with pytest.raises(CrossContextViolation):
            read_one(world.conn, to_veldt, entity, record_id)


def test_widening_is_the_only_way_across_and_it_is_the_principals_act(world):
    commitment_id = _seed_henderson_fact(world)
    to_veldt = Reader(
        tenant_id=world.tenant, actor="hugh", role="principal", counterparty_scope=world.veldt
    )
    with pytest.raises(CrossContextViolation):
        read_one(world.conn, to_veldt, "commitment", commitment_id)

    ea = Reader(tenant_id=world.tenant, actor="ea", role="ea")
    with pytest.raises(AccessDenied):
        widen_shareable_with(
            world.conn, ea, "commitment", commitment_id, [world.veldt], reason="for the raise deck"
        )

    principal = Reader(tenant_id=world.tenant, actor="aaron", role="principal")
    with pytest.raises(ValueError):
        widen_shareable_with(
            world.conn, principal, "commitment", commitment_id, [world.veldt], reason="  "
        )

    widening = widen_shareable_with(
        world.conn,
        principal,
        "commitment",
        commitment_id,
        [world.veldt],
        reason="disclosed in the data room",
    )
    assert widening.added == [world.veldt]
    assert read_one(world.conn, to_veldt, "commitment", commitment_id) is not None


def test_wildcard_shareable_with_is_refused(world):
    with pytest.raises(InvariantError, match="wildcard"):
        create_commitment(
            world.conn,
            tenant_id=world.tenant,
            direction="by_principal",
            statement="Anyone may see this.",
            made_at="2026-08-10T09:00:00+00:00",
            source_type="manual",
            provenance="verbatim",
            produced_by="human:manual",
            shareable_with=["*"],
        )


def test_tenant_isolation_holds_even_for_a_principal(world):
    commitment_id = _seed_henderson_fact(world)
    other = Reader(tenant_id="tn_other", actor="someone", role="principal")
    # read_one scopes by id, so the record is found and then denied on tenancy.
    with pytest.raises(AccessDenied):
        read_one(world.conn, other, "commitment", commitment_id)
    assert query(world.conn, other, "commitment") == []


def test_every_denied_read_leaves_a_deny_line(world):
    commitment_id = _seed_henderson_fact(world)
    to_veldt = Reader(
        tenant_id=world.tenant, actor="bram", role="principal", counterparty_scope=world.veldt
    )
    with pytest.raises(CrossContextViolation):
        read_one(world.conn, to_veldt, "commitment", commitment_id)

    row = world.conn.execute(
        """
        SELECT decision, reason, counterparty_scope FROM access_log
        WHERE record_id = ? ORDER BY id DESC LIMIT 1
        """,
        (commitment_id,),
    ).fetchone()
    assert row["decision"] == "deny"
    assert row["reason"].startswith("cross_context_denied")
    assert row["counterparty_scope"] == world.veldt
