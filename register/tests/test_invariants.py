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
    """Each record table must be classified for the secret check.

    Human free-text is redacted in place, machine-generated text is refused. A
    table in neither map is a table nobody decided about, which in practice
    means its text is unchecked.
    """
    from register.store import _HUMAN_TEXT_COLUMNS, _MACHINE_TEXT_COLUMNS

    classified = set(_HUMAN_TEXT_COLUMNS) | set(_MACHINE_TEXT_COLUMNS)
    unchecked = RECORD_TABLES - classified
    assert not unchecked, (
        f"{sorted(unchecked)} are classified as neither human free-text nor "
        "machine-generated. Decide which, so the omission is deliberate."
    )


def test_no_column_is_both_human_and_machine():
    """A column cannot be redacted and refused at once."""
    from register.store import _HUMAN_TEXT_COLUMNS, _MACHINE_TEXT_COLUMNS

    for table in set(_HUMAN_TEXT_COLUMNS) & set(_MACHINE_TEXT_COLUMNS):
        overlap = set(_HUMAN_TEXT_COLUMNS[table]) & set(_MACHINE_TEXT_COLUMNS[table])
        assert not overlap, f"{table}: {sorted(overlap)} classified as both"


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


# --- the model boundary cannot be laundered by a prefix ----------------------


@pytest.mark.parametrize(
    "produced_by",
    [
        "deepseek-v4-pro",
        "human:deepseek-v4-pro",
        "rules:deepseek-extractor@1",
        "HUMAN:DeepSeek-V4-Pro",
    ],
)
@pytest.mark.parametrize("artifact", ["action_request", "prediction", "register_record"])
def test_a_prefix_cannot_launder_a_code_only_model(produced_by, artifact):
    """CLAUDE.md §6, and the order of two checks decided whether it held.

    `produced_by` is caller-supplied free text at every call site, so the
    `human:` / `rules:` prefix is a label anyone can type. It used to be
    evaluated first and returned early, which meant `human:deepseek-v4-pro`
    wrote an Action Request. The capability check goes first now; the
    provenance class only speaks once the identifier is known not to name a
    code-only model.
    """
    from register.routing import assert_may_produce

    with pytest.raises(ModelBoundaryError):
        assert_may_produce(produced_by, artifact)


def test_a_prefixed_human_who_is_not_a_code_only_model_may_still_assert():
    from register.routing import assert_may_produce

    assert_may_produce("human:manual", "action_request")
    assert_may_produce("rules:extractor@1", "register_record")
    assert_may_produce("glm-5.2", "prediction")


def test_a_code_only_model_may_still_produce_code_under_a_prefix():
    """The escape is about asserting, not about the prefix being suspicious."""
    from register.routing import assert_may_produce

    assert_may_produce("human:deepseek-v4-pro", "code")
    assert_may_produce("deepseek-v4-pro", "migration")


# --- an unreadable sharing list denies -------------------------------------


def test_a_corrupt_shareable_with_raises_rather_than_parsing_to_nothing():
    """An unparseable sharing list is not evidence that anybody may see it."""
    with pytest.raises(InvariantError, match="not valid JSON"):
        parse_shareable_with("{not json")

    with pytest.raises(InvariantError, match="JSON array"):
        parse_shareable_with('{"everyone": true}')


def test_an_empty_shareable_with_is_still_nobody():
    assert parse_shareable_with(None) == []
    assert parse_shareable_with("") == []
    assert parse_shareable_with("[]") == []


# --- the model boundary is a labelling check, and says so --------------------


def test_a_mislabelled_call_site_is_caught():
    """What the check does do: reject a code-only identifier, prefix or not."""
    from register.errors import ModelBoundaryError
    from register.routing import assert_may_produce

    for identifier in (
        "deepseek-v4-pro",
        "human:deepseek-v4-pro",  # the prefix laundering the reviewer found
        "rules:deepseek-extractor@1",
        "DeepSeek-V4",
        "openrouter/deepseek-v4",
    ):
        with pytest.raises(ModelBoundaryError):
            assert_may_produce(identifier, "prediction")


def test_the_boundary_cannot_stop_a_caller_that_lies():
    """What it does not do, asserted so nobody mistakes it for enforcement.

    An independent reviewer's finding, and it is correct: `produced_by` is a
    caller-supplied string, so a caller labelling DeepSeek output `glm-5.2`
    passes. There is no fix available in Sprint 1 — CLAUDE.md §6 says enforce
    at the routing layer, and there is no routing layer, no agent and no
    authenticated producer to derive an execution identity from.

    This test exists so the limit is recorded as a known property rather than
    discovered later as a surprise. When D-17 lands, capability must come from
    which engine actually ran, and this test should start failing.
    """
    from register.routing import assert_may_produce

    # A lie. Nothing here can detect it, and pretending otherwise is worse
    # than saying so.
    assert_may_produce("glm-5.2", "action_request")
    assert_may_produce("human:manual", "prediction")


def test_the_module_documents_that_it_is_not_a_boundary():
    """A future reader must not take a passing check for a guarantee."""
    from register import routing

    doc = (routing.__doc__ or "") + (routing.assert_may_produce.__doc__ or "")
    assert "labelling" in doc.lower()
    assert "routing layer" in doc.lower()
