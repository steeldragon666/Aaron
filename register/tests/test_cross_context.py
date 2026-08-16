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
    create_person,
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


# --- there is no SQL fragment left to escape from ----------------------------


def test_query_no_longer_accepts_a_composed_sql_fragment(world):
    """The fix for a guard that could be walked: remove the thing it guarded.

    `query` used to take a `where` string interpolated inside
    `tenant_id = ? AND (...)`, protected by a paren-balance check. An
    independent reviewer walked it in one line — see the next test. The
    response was not to patch the checker but to delete the fragment: a
    character counter is not a SQL parser, and it cannot be made into one by
    fixing the case somebody demonstrated.
    """
    from register.access import Reader, query

    reader = Reader(tenant_id=world.tenant, actor="aaron", role="principal")
    with pytest.raises(TypeError):
        query(world.conn, reader, "commitment", where="1=1")  # type: ignore[call-arg]


def test_the_fragment_that_walked_the_old_guard_has_nowhere_to_go(world):
    """The specific bypass, kept as a test so it cannot come back.

    `"1=1 /* ' */ ) OR (1=1 /* ' */"` passed the balance check: the quote
    inside each block comment flipped the checker's quote state, so the `)`
    was never counted. SQLite strips comments, and the predicate became
    `tenant_id = ? AND (1=1) OR (1=1)` — every tenant's rows.

    There is now no parameter it can be passed to. If a future change
    reintroduces one, this fails.
    """
    import inspect

    from register.access import query

    params = inspect.signature(query).parameters
    assert "where" not in params
    assert "params" not in params
    assert "filters" in params


def test_a_filter_column_must_exist_on_the_entity(world):
    """Columns are checked against the schema, so the allowlist cannot drift."""
    from register.access import Filter, Reader, query
    from register.errors import InvariantError

    reader = Reader(tenant_id=world.tenant, actor="aaron", role="principal")
    with pytest.raises(InvariantError, match="no column"):
        query(world.conn, reader, "commitment", filters=[Filter("status) OR (1=1", "eq", "open")])
    with pytest.raises(InvariantError, match="no column"):
        query(world.conn, reader, "commitment", filters=[Filter("nonexistent", "eq", 1)])


def test_a_filter_op_must_be_on_the_map(world):
    from register.access import Filter, Reader, query
    from register.errors import InvariantError

    reader = Reader(tenant_id=world.tenant, actor="aaron", role="principal")
    with pytest.raises(InvariantError, match="unknown filter op"):
        query(world.conn, reader, "commitment", filters=[Filter("status", "= 1 OR 1", "open")])


def test_a_filter_value_is_bound_never_interpolated(world):
    """The value is the one thing a caller fully controls, so it is a parameter."""
    from register.access import Filter, Reader, query

    reader = Reader(tenant_id=world.tenant, actor="aaron", role="principal")
    hostile = "open') OR ('1'='1"
    assert query(world.conn, reader, "commitment", filters=[Filter("status", "eq", hostile)]) == []
    # The table is still there, which it would not be if values were
    # interpolated. Compared against the known count rather than asserted
    # non-None: a COUNT(*) always returns exactly one row, so `is not None`
    # could never have failed and was reassurance rather than a check.
    assert world.conn.execute("SELECT count(*) AS n FROM commitment").fetchone()["n"] == 0


def test_ordinary_filters_still_work(world):
    from register.access import Filter, Reader, query

    reader = Reader(tenant_id=world.tenant, actor="aaron", role="principal")
    assert query(world.conn, reader, "commitment", filters=[Filter("status", "eq", "open")]) == []
    assert (
        query(world.conn, reader, "commitment", filters=[Filter("status", "in", ["open", "void"])])
        == []
    )
    assert query(world.conn, reader, "commitment", filters=[Filter("due", "is_null")]) == []
    # An empty IN means nothing matches, rather than a syntax error.
    assert query(world.conn, reader, "commitment", filters=[Filter("status", "in", [])]) == []


def test_order_by_is_an_allowlist_not_a_fragment(world):
    from register.access import Reader, query
    from register.errors import InvariantError

    reader = Reader(tenant_id=world.tenant, actor="aaron", role="principal")
    with pytest.raises(InvariantError, match="order_by"):
        query(world.conn, reader, "commitment", order_by="created_at; DROP TABLE commitment")
    query(world.conn, reader, "commitment", order_by="made_at")


# --- the fourth id-only write path ------------------------------------------


def test_reconcile_gap_cannot_clear_another_tenants_dark_meeting(world):
    """Found by asking the reviewer whether the set of three was complete.

    It was not. `reconcile_gap` keyed on `meeting_id` alone, so a meeting id
    was enough to clear another tenant's `gap_flag` — and `gap_flag` is what
    suppresses a chase on a commitment a dark meeting could have superseded.
    The consequence was not a stray edit but an unsuppressed chase going out
    in a tenant nobody had touched.
    """
    from register.entities import create_tenant, reconcile_gap, record_dark_meeting
    from register.errors import RegisterError

    other = create_tenant(world.conn, "Gap Co", tenant_id="tn_gapco")
    intruder = create_person(
        world.conn,
        tenant_id=other,
        display_name="Their Principal",
        email="them@other.test",
        is_principal=True,
        produced_by="human:manual",
    )
    meeting_id = record_dark_meeting(
        world.conn,
        tenant_id=other,
        title="Their private conversation",
        starts_at="2026-08-14T02:00:00+00:00",
        attendees=[intruder],
        known_topics=["their pricing"],
        produced_by="human:calendar-sync",
    )

    with pytest.raises(RegisterError, match="no meeting"):
        reconcile_gap(world.conn, meeting_id, "not mine to clear", tenant_id=world.tenant)

    row = world.conn.execute(
        "SELECT gap_flag, capture_reason FROM meeting WHERE id = ?", (meeting_id,)
    ).fetchone()
    assert row["gap_flag"] == 1, "another tenant's gap was cleared"
    assert "not mine to clear" not in (row["capture_reason"] or "")


def test_reconcile_gap_still_works_inside_its_own_tenant(world):
    from register.entities import reconcile_gap, record_dark_meeting

    meeting_id = record_dark_meeting(
        world.conn,
        tenant_id=world.tenant,
        title="Henderson pricing",
        starts_at="2026-08-14T02:00:00+00:00",
        attendees=[world.principal, world.henderson],
        known_topics=["price"],
        produced_by="human:calendar-sync",
    )
    reconcile_gap(world.conn, meeting_id, "voice dump, 90s", tenant_id=world.tenant)
    row = world.conn.execute("SELECT gap_flag FROM meeting WHERE id = ?", (meeting_id,)).fetchone()
    assert row["gap_flag"] == 0


# --- order_by is checked against the entity, not just the union --------------


def test_order_by_must_be_a_column_of_this_entity(world):
    """Passing the global allowlist is necessary and not sufficient.

    `_ORDER_COLUMNS` is the union of natural orderings across every entity, so
    `made_at` is on it — it is a real `commitment` column. It is not a `person`
    column, and ordering a person query by it used to reach SQLite and come
    back as a bare `OperationalError` from a statement the caller never wrote.

    Raised by an independent reviewer. Not a security hole — the allowlist is a
    fixed frozenset, so nothing was injectable — but an API that answers an
    invalid request with a driver error is one whose contract is decided by
    whatever SQLite happens to do.
    """
    import sqlite3

    from register.access import Reader, query
    from register.errors import InvariantError

    reader = Reader(tenant_id=world.tenant, actor="aaron", role="principal")

    with pytest.raises(InvariantError, match="no column 'made_at' to order by"):
        query(world.conn, reader, "person", order_by="made_at")

    # And the failure is ours, not the driver's.
    try:
        query(world.conn, reader, "person", order_by="made_at")
    except sqlite3.OperationalError:  # pragma: no cover - the regression
        pytest.fail("an invalid order_by reached SQLite")
    except InvariantError:
        pass


def test_an_entity_specific_order_column_still_works(world):
    from register.access import Reader, query

    reader = Reader(tenant_id=world.tenant, actor="aaron", role="principal")
    query(world.conn, reader, "commitment", order_by="made_at")  # commitment has it
    query(world.conn, reader, "person", order_by="created_at")  # everything has it


def test_an_oversized_in_list_is_refused_with_a_number(world):
    """Past SQLite's bind ceiling this failed as an opaque driver error."""
    from register.access import MAX_IN_VALUES, Filter, Reader, query
    from register.errors import InvariantError

    reader = Reader(tenant_id=world.tenant, actor="aaron", role="principal")
    too_many = [f"cm_{n}" for n in range(MAX_IN_VALUES + 1)]
    with pytest.raises(InvariantError, match=f"more than the {MAX_IN_VALUES}"):
        query(world.conn, reader, "commitment", filters=[Filter("id", "in", too_many)])

    at_the_limit = [f"cm_{n}" for n in range(MAX_IN_VALUES)]
    assert query(world.conn, reader, "commitment", filters=[Filter("id", "in", at_the_limit)]) == []


def test_widening_cannot_reach_into_another_tenant(world):
    """Defence in depth: `read_one` already proved ownership, and this asks again.

    A write that is safe only because of what a caller did twenty lines earlier
    is the one a later refactor breaks silently.

    Asserted behaviourally rather than by matching the SQL text, which was the
    first version of this test. A source-text assertion breaks on a reformat
    while the predicate stays correct, and passes if the string turns up in a
    comment — it tests the spelling, not the property.
    """
    from register.entities import create_tenant

    other = create_tenant(world.conn, "Widening Co", tenant_id="tn_widening")
    theirs = create_commitment(
        world.conn,
        tenant_id=other,
        direction="to_principal",
        statement="Their commitment, not ours to share.",
        made_at="2026-08-10T09:00:00+00:00",
        source_type="email",
        provenance="verbatim",
        produced_by="human:manual",
    )
    before = world.conn.execute(
        "SELECT shareable_with FROM commitment WHERE id = ?", (theirs,)
    ).fetchone()["shareable_with"]

    # A principal of *this* tenant, holding the other tenant's record id.
    principal = Reader(tenant_id=world.tenant, actor="aaron", role="principal")
    with pytest.raises((AccessDenied, LookupError)):
        widen_shareable_with(
            world.conn, principal, "commitment", theirs, [world.veldt], reason="not mine to widen"
        )

    after = world.conn.execute(
        "SELECT shareable_with FROM commitment WHERE id = ?", (theirs,)
    ).fetchone()["shareable_with"]
    assert after == before, "another tenant's sharing list was widened"


def test_many_individually_legal_in_filters_cannot_exceed_the_bind_ceiling(world):
    """`MAX_IN_VALUES` bounds one filter and said nothing about a query.

    `filters` is an unbounded sequence, so 66 legal 500-value `IN` filters bind
    33,001 variables and fail at the driver — the opaque error the per-filter
    cap existed to prevent, reached by a different route. Raised by an
    independent reviewer as an incomplete fix, which it was.
    """
    from register.access import MAX_BOUND_PARAMS, MAX_IN_VALUES, Filter, Reader, query
    from register.errors import InvariantError

    reader = Reader(tenant_id=world.tenant, actor="aaron", role="principal")
    each = [f"cm_{n}" for n in range(MAX_IN_VALUES)]
    filters = [Filter("id", "in", each)] * (MAX_BOUND_PARAMS // MAX_IN_VALUES + 2)

    with pytest.raises(InvariantError, match="more than the"):
        query(world.conn, reader, "commitment", filters=filters)
