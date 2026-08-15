"""Test priority 2 — visibility bleed.

BUILD_BRIEF §3 acceptance 7: a ``principal_only`` record is provably invisible
to an ``all_users`` reader — as a test, not an inspection.

Every visibility level is checked against every reader role, so the matrix is
asserted in full rather than sampled.
"""

from __future__ import annotations

import itertools

import pytest

from register.access import ROLES, VISIBILITY_READERS, Reader, query, read_one
from register.entities import create_commitment
from register.errors import AccessDenied
from register.invariants import SENSITIVE_CATEGORIES, VISIBILITY_LEVELS, default_visibility


def _commitment(world, visibility: str) -> str:
    return create_commitment(
        world.conn,
        tenant_id=world.tenant,
        direction="by_principal",
        statement=f"A {visibility} commitment.",
        made_at="2026-08-10T09:00:00+00:00",
        source_type="manual",
        provenance="verbatim",
        produced_by="human:manual",
        visibility=visibility,
    )


@pytest.mark.parametrize("visibility,role", list(itertools.product(VISIBILITY_LEVELS, ROLES)))
def test_full_visibility_matrix(world, visibility, role):
    commitment_id = _commitment(world, visibility)
    reader = Reader(tenant_id=world.tenant, actor=f"actor-{role}", role=role)
    permitted = role in VISIBILITY_READERS[visibility]

    if permitted:
        assert read_one(world.conn, reader, "commitment", commitment_id) is not None
    else:
        with pytest.raises(AccessDenied):
            read_one(world.conn, reader, "commitment", commitment_id)


def test_principal_only_is_invisible_to_an_all_users_reader(world):
    commitment_id = _commitment(world, "principal_only")
    reader = Reader(tenant_id=world.tenant, actor="report", role="user")

    with pytest.raises(AccessDenied):
        read_one(world.conn, reader, "commitment", commitment_id)

    # And it is absent from the listing, not merely redacted within it.
    listed = query(world.conn, reader, "commitment")
    assert all(row["id"] != commitment_id for row in listed)


@pytest.mark.parametrize("category", sorted(SENSITIVE_CATEGORIES))
def test_sensitive_categories_default_to_principal_only(world, category):
    assert default_visibility([category]) == "principal_only"
    commitment_id = create_commitment(
        world.conn,
        tenant_id=world.tenant,
        direction="by_principal",
        statement=f"Something touching {category}.",
        made_at="2026-08-10T09:00:00+00:00",
        source_type="manual",
        provenance="verbatim",
        produced_by="human:manual",
        categories=[category],
    )
    row = world.conn.execute(
        "SELECT visibility FROM commitment WHERE id = ?", (commitment_id,)
    ).fetchone()
    assert row["visibility"] == "principal_only"


def test_no_default_path_produces_all_users(world):
    """Nothing gets to ``all_users`` by omission — only by being asked for."""
    assert default_visibility() == "principal_and_ea"
    assert default_visibility([]) == "principal_and_ea"
    assert default_visibility(["routine"]) == "principal_and_ea"

    commitment_id = create_commitment(
        world.conn,
        tenant_id=world.tenant,
        direction="by_principal",
        statement="No visibility argument was passed.",
        made_at="2026-08-10T09:00:00+00:00",
        source_type="manual",
        provenance="verbatim",
        produced_by="human:manual",
    )
    row = world.conn.execute(
        "SELECT visibility FROM commitment WHERE id = ?", (commitment_id,)
    ).fetchone()
    assert row["visibility"] != "all_users"


def test_unknown_visibility_denies_rather_than_admits(world):
    """A level this code does not recognise must not become readable by accident."""
    from register.access import evaluate

    record = {"tenant_id": world.tenant, "visibility": "everyone_forever", "shareable_with": "[]"}
    for role in ROLES:
        decision = evaluate(Reader(tenant_id=world.tenant, actor="x", role=role), record)
        assert not decision.allowed
        assert decision.reason.startswith("visibility_unknown")


def test_every_read_is_logged_allowed_or_denied(world):
    commitment_id = _commitment(world, "principal_only")
    principal = Reader(tenant_id=world.tenant, actor="aaron", role="principal")
    report = Reader(tenant_id=world.tenant, actor="dr", role="user")

    read_one(world.conn, principal, "commitment", commitment_id)
    with pytest.raises(AccessDenied):
        read_one(world.conn, report, "commitment", commitment_id)

    rows = world.conn.execute(
        "SELECT actor, decision FROM access_log WHERE record_id = ? ORDER BY id",
        (commitment_id,),
    ).fetchall()
    assert [(r["actor"], r["decision"]) for r in rows] == [("aaron", "allow"), ("dr", "deny")]


def test_visibility_cannot_be_changed_by_a_generic_field_update(world):
    from register.errors import InvariantError
    from register.store import update

    commitment_id = _commitment(world, "principal_only")
    for forbidden in ("tenant_id", "shareable_with", "provenance", "produced_by"):
        with pytest.raises(InvariantError):
            update(world.conn, "commitment", commitment_id, {forbidden: "anything"})
