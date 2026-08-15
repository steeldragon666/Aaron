"""The write boundary.

Everything that inserts or updates a register record goes through here, so
that the invariant check, the redaction check and the model boundary are
unavoidable rather than remembered.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

from .errors import InvariantError
from .invariants import (
    RECORD_TABLES,
    normalise_shareable_with,
    validate_invariants,
)
from .redaction import assert_no_secrets
from .routing import assert_may_produce

# Columns whose free text could carry a credential out of a source system and
# into the register. Checked on every write, per table.
_TEXT_COLUMNS: Mapping[str, tuple[str, ...]] = {
    "person": ("display_name", "relationship", "tenant_scoped_note"),
    "meeting": ("title", "capture_reason", "known_topics"),
    "thread": ("subject",),
    "commitment": ("statement", "last_action", "evidence_ref"),
    "decision": ("statement", "reasoning_at_time"),
    "exposure": ("description",),
    "prediction": ("statement", "falsifiable_by"),
    "curator_proposal": ("candidate",),
    "ingest_event": ("summary", "body"),
    "ar_ledger": ("payload",),
}


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def prepare(
    table: str, values: Mapping[str, Any], *, artifact: str = "register_record"
) -> dict[str, Any]:
    """Normalise, validate and secret-check a row before it is written."""
    if table not in RECORD_TABLES:
        raise InvariantError(f"{table} is not a record table")

    row = dict(values)
    row["shareable_with"] = normalise_shareable_with(row.get("shareable_with"))
    validate_invariants(table, row)
    assert_may_produce(str(row["produced_by"]), artifact)

    for column in _TEXT_COLUMNS.get(table, ()):
        assert_no_secrets(row.get(column), f"{table}.{column}")

    stamp = now()
    row.setdefault("created_at", stamp)
    if "updated_at" not in row and table != "ar_ledger":
        row["updated_at"] = stamp
    return row


def insert(
    conn: sqlite3.Connection,
    table: str,
    values: Mapping[str, Any],
    *,
    artifact: str = "register_record",
) -> str:
    """Insert one record and return its id."""
    row = prepare(table, values, artifact=artifact)
    columns = ", ".join(row)
    placeholders = ", ".join("?" for _ in row)
    conn.execute(
        f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
        tuple(row.values()),
    )
    return str(row.get("id", ""))


def update(
    conn: sqlite3.Connection,
    table: str,
    record_id: str,
    changes: Mapping[str, Any],
) -> None:
    """Update mutable fields of a record.

    The invariant fields are not updatable here. ``visibility`` narrows or
    widens a record's audience and ``shareable_with`` crosses a context
    boundary; both have their own named paths so that neither can happen as a
    side effect of a routine field update.
    """
    if table not in RECORD_TABLES:
        raise InvariantError(f"{table} is not a record table")
    forbidden = {"tenant_id", "shareable_with", "provenance", "produced_by", "id"} & set(changes)
    if forbidden:
        raise InvariantError(
            f"{table}: {', '.join(sorted(forbidden))} may not be changed by a field update"
        )

    row = dict(changes)
    for column in _TEXT_COLUMNS.get(table, ()):
        if column in row:
            assert_no_secrets(row[column], f"{table}.{column}")
    row["updated_at"] = now()

    assignments = ", ".join(f"{column} = ?" for column in row)
    conn.execute(
        f"UPDATE {table} SET {assignments} WHERE id = ?",
        (*row.values(), record_id),
    )
