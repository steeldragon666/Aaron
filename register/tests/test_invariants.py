"""Acceptance 9, write side — no record type reaches the database without the
full invariant set, and nothing defaults to allow.
"""

from __future__ import annotations

import pytest

from register.errors import InvariantError, ModelBoundaryError
from register.invariants import (
    INVARIANT_FIELDS,
    RECORD_TABLES,
    normalise_shareable_with,
    parse_shareable_with,
    validate_invariants,
)
from register.store import insert, prepare


def _valid(world) -> dict:
    return {
        "id": "cm_test",
        "tenant_id": world.tenant,
        "direction": "by_principal",
        "statement": "I'll send the schedule.",
        "made_at": "2026-08-10T09:00:00+00:00",
        "source_type": "manual",
        "confidence": 1.0,
        "visibility": "principal_and_ea",
        "shareable_with": [],
        "provenance": "verbatim",
        "produced_by": "human:manual",
    }


@pytest.mark.parametrize("field", [f for f in INVARIANT_FIELDS if f != "shareable_with"])
def test_a_missing_invariant_field_is_refused(world, field):
    values = _valid(world)
    values.pop(field)
    with pytest.raises(InvariantError, match=field):
        insert(world.conn, "commitment", values)


def test_an_omitted_shareable_with_denies_rather_than_raising(world):
    """The one invariant that is allowed to be absent at the call site.

    ``shareable_with`` is the only one where omission has a safe meaning:
    nobody. Raising instead would tempt a caller into passing a value they had
    not thought about, and the value they reach for under that pressure is a
    wide one. Every other invariant field has no safe default and must be
    supplied.
    """
    values = _valid(world)
    values.pop("shareable_with")
    insert(world.conn, "commitment", values)
    row = world.conn.execute(
        "SELECT shareable_with FROM commitment WHERE id = 'cm_test'"
    ).fetchone()
    assert row["shareable_with"] == "[]"


def test_validate_invariants_still_requires_the_field_to_exist(world):
    values = _valid(world)
    values.pop("shareable_with")
    with pytest.raises(InvariantError, match="shareable_with"):
        validate_invariants("commitment", values)


def test_a_commitment_without_direction_is_refused(world):
    values = _valid(world)
    values.pop("direction")
    with pytest.raises(InvariantError, match="direction"):
        insert(world.conn, "commitment", values)


def test_an_unregistered_table_is_refused(world):
    with pytest.raises(InvariantError):
        validate_invariants("shadow_notes", _valid(world))


def test_every_record_table_is_reachable_through_the_write_boundary():
    from register.store import _TEXT_COLUMNS

    unchecked = RECORD_TABLES - set(_TEXT_COLUMNS)
    assert not unchecked, (
        f"{sorted(unchecked)} have no columns registered for the secret check — "
        "add them, even if the tuple is empty, so the omission is deliberate"
    )


def test_shareable_with_normalises_to_a_sorted_deduplicated_array():
    assert normalise_shareable_with(None) == "[]"
    assert normalise_shareable_with([]) == "[]"
    assert normalise_shareable_with(["b", "a", "b"]) == '["a","b"]'
    assert parse_shareable_with('["a","b"]') == ["a", "b"]


def test_shareable_with_rejects_a_wildcard():
    with pytest.raises(InvariantError, match="wildcard"):
        normalise_shareable_with(["*"])


def test_shareable_with_rejects_a_non_array():
    with pytest.raises(InvariantError):
        normalise_shareable_with({"everyone": True})


def test_prepare_stamps_created_and_updated(world):
    row = prepare("commitment", _valid(world))
    assert row["created_at"] and row["updated_at"]
    assert row["shareable_with"] == "[]"


def test_a_code_only_model_may_not_write_a_register_record(world):
    values = _valid(world)
    values["produced_by"] = "deepseek-v4-pro-0815"
    with pytest.raises(ModelBoundaryError):
        insert(world.conn, "commitment", values)


def test_a_code_only_model_may_still_produce_code():
    from register.routing import assert_may_produce

    assert_may_produce("deepseek-v4-pro", "code")
    assert_may_produce("deepseek-v4-pro", "migration")
    with pytest.raises(ModelBoundaryError):
        assert_may_produce("deepseek-v4-pro", "prediction")


def test_the_database_rejects_a_bad_enum_even_if_the_validator_is_bypassed(world):
    """Belt and braces: the CHECK constraints stand on their own."""
    import sqlite3

    with pytest.raises(sqlite3.IntegrityError):
        world.conn.execute(
            """
            INSERT INTO commitment
                (id, tenant_id, direction, statement, made_at, source_type, confidence,
                 status, visibility, shareable_with, provenance, produced_by, created_at, updated_at)
            VALUES ('cm_raw', ?, 'sideways', 's', '2026-08-10', 'manual', 1.0,
                    'open', 'principal_only', '[]', 'verbatim', 'human:manual', 'now', 'now')
            """,
            (world.tenant,),
        )
