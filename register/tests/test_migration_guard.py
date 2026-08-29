"""Acceptance 9 — every record carries all invariant fields, and a migration
attempting to add one to an existing table fails review.

The second half is what this file is really for. "Fails review" is only real if
review is mechanical, so the check is a test: parse every migration, and fail
if any of them introduces a record table without the invariant set, or adds an
invariant column to a table that an earlier migration already created.

That second rule is the expensive one. Retrofitting ``tenant_id``,
``visibility`` or ``shareable_with`` rewrites every row written before it
existed — CLAUDE.md calls it the single most expensive mistake available in
this codebase, and this is the thing standing in front of it.
"""

from __future__ import annotations

import re

import pytest

from register.db import _migration_files
from register.invariants import (
    EXEMPT_TABLES,
    INVARIANT_FIELDS,
    RECORD_TABLES,
)

_CREATE_TABLE = re.compile(
    r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-z_]+)\s*\((.*?)\n\)\s*;",
    re.IGNORECASE | re.DOTALL,
)
_ALTER_ADD = re.compile(r"ALTER\s+TABLE\s+([a-z_]+)\s+ADD\s+(?:COLUMN\s+)?([a-z_]+)", re.IGNORECASE)


def _tables_by_migration() -> list[tuple[str, dict[str, str]]]:
    out: list[tuple[str, dict[str, str]]] = []
    for name, sql in _migration_files():
        tables = {match[1].lower(): match[2] for match in _CREATE_TABLE.finditer(sql)}
        out.append((name, tables))
    return out


def _all_tables() -> dict[str, str]:
    merged: dict[str, str] = {}
    for _, tables in _tables_by_migration():
        merged.update(tables)
    return merged


def test_every_record_table_declares_every_invariant_field():
    tables = _all_tables()
    for table in sorted(RECORD_TABLES):
        assert table in tables, f"{table} is declared a record table but no migration creates it"
        body = tables[table]
        for column in INVARIANT_FIELDS:
            assert re.search(rf"^\s*{column}\b", body, re.MULTILINE), (
                f"{table} is missing the invariant column {column}. Add it in the "
                "migration that creates the table — never in a later one."
            )


def test_commitment_carries_direction():
    body = _all_tables()["commitment"]
    assert re.search(r"^\s*direction\b", body, re.MULTILINE)


def test_no_table_is_unaccounted_for():
    """Every created table is either a record table or an explained exemption."""
    for table in _all_tables():
        assert table in RECORD_TABLES or table in EXEMPT_TABLES, (
            f"{table} is created by a migration but is neither a record table nor "
            "an exempt one. Decide which it is — an unclassified table is a table "
            "whose visibility rules nobody has thought about."
        )


def test_every_exemption_carries_a_reason():
    for table, reason in EXEMPT_TABLES.items():
        assert reason.strip(), f"{table} is exempt with no reason given"


def test_no_migration_retrofits_an_invariant_onto_an_existing_table():
    seen: set[str] = set()
    for name, tables in _tables_by_migration():
        sql = dict(_migration_files())[name]
        for table, column in _ALTER_ADD.findall(sql):
            if table.lower() in seen and column.lower() in INVARIANT_FIELDS:
                pytest.fail(
                    f"{name} adds the invariant column {column} to the existing table "
                    f"{table}. This rewrites every row written before it existed. "
                    "Every record carries the full set from the migration that creates it."
                )
        seen.update(tables)


def test_every_record_table_has_a_tenant_scoped_index_or_primary_key():
    """A record table without a tenant-scoped access path invites a full scan
    that crosses tenants."""
    joined = "\n".join(sql for _, sql in _migration_files())
    for table in sorted(RECORD_TABLES):
        if table == "ar_ledger":
            assert "ar_ledger_ar_idx" in joined
            continue
        assert re.search(
            rf"CREATE\s+(?:UNIQUE\s+)?INDEX\s+\w+\s+ON\s+{table}\s*\(\s*tenant_id", joined
        ), f"{table} has no index leading with tenant_id"


def test_shareable_with_defaults_to_deny_in_the_schema():
    for table, body in _all_tables().items():
        if table not in RECORD_TABLES:
            continue
        match = re.search(
            r"^\s*shareable_with\s+TEXT\s+NOT\s+NULL\s+DEFAULT\s+'(\[\])'", body, re.MULTILINE
        )
        assert match, (
            f"{table}.shareable_with must default to '[]' — default deny, never default allow"
        )


def test_migrations_are_applied_and_recorded(conn):
    names = {row["name"] for row in conn.execute("SELECT name FROM schema_migrations")}
    assert names == {name for name, _ in _migration_files()}


def test_migrate_is_idempotent(conn):
    from register.db import migrate

    assert migrate(conn) == []
