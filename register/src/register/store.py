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
from .redaction import assert_no_secrets, redact
from .routing import assert_may_produce

# Every column whose free text could carry a credential into the register is
# checked on write — but the two classes get different treatment, and the
# difference matters more than the check does.
#
# **Human free-text is redacted in place.** Someone typing "the password is
# wrong" into a rejection reason must not have their action blocked. People who
# get blocked learn to route around the check, and a guardrail that trains
# people to avoid it is worse than no guardrail: it removes the behaviour from
# the audited path entirely. The matched span is replaced and the rest of the
# sentence persists, so the field keeps its meaning and the log keeps its
# evidence.
_HUMAN_TEXT_COLUMNS: Mapping[str, tuple[str, ...]] = {
    "person": ("display_name", "relationship", "tenant_scoped_note"),
    "meeting": ("title", "capture_reason", "known_topics"),
    "thread": ("subject",),
    "commitment": ("statement", "last_action"),
    "decision": ("statement", "reasoning_at_time"),
    "exposure": ("description",),
    # Already redacted by the ingest pipeline; this is the backstop, and a
    # backstop that refuses would drop a whole message over one false positive.
    "ingest_event": ("summary", "body"),
}

# **Machine-generated text is refused.** A secret here is not a typo, it is a
# bug in whatever produced the value — an extractor that swept a credential
# into a candidate, or a model that emitted one into an Action Request. There
# is no user to inconvenience and nothing to preserve, so the write fails loudly
# and the caller finds out at the point the defect was introduced.
_MACHINE_TEXT_COLUMNS: Mapping[str, tuple[str, ...]] = {
    "commitment": ("evidence_ref",),
    "prediction": ("statement", "falsifiable_by"),
    "curator_proposal": ("candidate",),
    "ar_ledger": ("payload",),
}


def _scrub(row: dict[str, Any], table: str) -> int:
    """Redact human columns in place, refuse machine ones. Returns redactions."""
    redactions = 0
    for column in _HUMAN_TEXT_COLUMNS.get(table, ()):
        value = row.get(column)
        if isinstance(value, str) and value:
            outcome = redact(value)
            if not outcome.clean:
                row[column] = outcome.text
                redactions += outcome.count
    for column in _MACHINE_TEXT_COLUMNS.get(table, ()):
        if column in row:
            assert_no_secrets(row.get(column), f"{table}.{column}")
    return redactions


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

    _scrub(row, table)

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
    *,
    tenant_id: str,
) -> None:
    """Update mutable fields of a record.

    ``tenant_id`` is required and is part of the predicate, not a courtesy
    argument. Every read path in this codebase scopes by tenant; this path did
    not, so a caller holding an id could mutate another tenant's record. Making
    it a required keyword means the predicate cannot be forgotten at a call
    site — the same reason `shareable_with` defaults to deny rather than to the
    value a hurried caller would have reached for.

    The invariant fields are not updatable here. ``visibility`` narrows or
    widens a record's audience and ``shareable_with`` crosses a context
    boundary; both have their own named paths so that neither can happen as a
    side effect of a routine field update.
    """
    if table not in RECORD_TABLES:
        raise InvariantError(f"{table} is not a record table")
    # `visibility` belongs here and was missing, which made the docstring above
    # a description of the intent rather than of the code. `access.evaluate`
    # decides readership from this column, so `update(conn, "commitment", cid,
    # {"visibility": "all_users"})` widened a `principal_only` record's audience
    # with no role check, no stated reason and no `access_log` line — the three
    # things `widen_shareable_with` requires for the sibling operation.
    forbidden = {
        "tenant_id",
        "visibility",
        "shareable_with",
        "provenance",
        "produced_by",
        "id",
    } & set(changes)
    if forbidden:
        raise InvariantError(
            f"{table}: {', '.join(sorted(forbidden))} may not be changed by a field update"
        )

    row = dict(changes)
    _scrub(row, table)
    row["updated_at"] = now()

    assignments = ", ".join(f"{column} = ?" for column in row)
    cursor = conn.execute(
        f"UPDATE {table} SET {assignments} WHERE id = ? AND tenant_id = ?",
        (*row.values(), record_id, tenant_id),
    )
    if cursor.rowcount == 0:
        # Either no such record, or it belongs to another tenant. The caller is
        # told the same thing in both cases: a miss must not be a probe that
        # reveals whether an id exists somewhere else.
        raise InvariantError(f"{table}/{record_id} not found in tenant {tenant_id}")
