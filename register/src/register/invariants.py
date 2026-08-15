"""Schema invariants — CLAUDE.md §1.

Every record in the system carries tenant_id, visibility, shareable_with,
provenance and produced_by. Commitment records additionally carry direction.

These are validated here, at the write boundary, as well as by CHECK
constraints in the migration. Two independent checks because each catches a
different mistake: the CHECK catches a bad value, this catches a missing field
and a default-allow ``shareable_with``.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from typing import Any

from .errors import InvariantError

# --- the invariant field set -----------------------------------------------

INVARIANT_FIELDS: tuple[str, ...] = (
    "tenant_id",
    "visibility",
    "shareable_with",
    "provenance",
    "produced_by",
)

VISIBILITY_LEVELS: tuple[str, ...] = (
    "principal_only",
    "principal_and_ea",
    "leadership",
    "all_users",
)

PROVENANCE_LEVELS: tuple[str, ...] = ("verbatim", "paraphrase", "inferred")

DIRECTIONS: tuple[str, ...] = ("by_principal", "to_principal", "witnessed")

# Tables that hold client records and therefore must carry the full invariant
# set. Adding an entity means adding it here as well as to the migration; the
# migration guard test cross-checks the two lists against each other.
RECORD_TABLES: frozenset[str] = frozenset(
    {
        "person",
        "meeting",
        "thread",
        "commitment",
        "decision",
        "exposure",
        "prediction",
        "ar_ledger",
        "curator_proposal",
        "ingest_event",
    }
)

# Tables deliberately outside the invariant set, each with the reason it is
# outside. The guard test reads this map; an unexplained exemption fails.
EXEMPT_TABLES: Mapping[str, str] = {
    "tenant": "tenancy root — a tenant cannot carry its own tenant_id meaningfully",
    "meeting_attendee": "join table — visibility is the parent meeting's, reads go through it",
    "thread_counterparty": "join table — visibility is the parent thread's, reads go through it",
    "decision_participant": "join table — visibility is the parent decision's, reads go through it",
    "access_log": "audit log, not a client record — carries no payload by design",
    "schema_migrations": "migration bookkeeping",
}

# Categories that default to principal_only rather than inheriting a wider
# default. ACTION_TIER_AND_REGISTER_SPEC §4: default-deny, not default-allow.
SENSITIVE_CATEGORIES: frozenset[str] = frozenset(
    {"comp", "personnel", "board", "m_and_a", "legal", "health"}
)


def default_visibility(categories: Iterable[str] | None = None) -> str:
    """The visibility a record gets when nobody has said otherwise.

    Sensitive categories collapse to ``principal_only``. Everything else lands
    at ``principal_and_ea`` — the principal and their EA, and nobody wider.
    There is no code path that defaults a record to ``all_users``.
    """
    cats = set(categories or ())
    if cats & SENSITIVE_CATEGORIES:
        return "principal_only"
    return "principal_and_ea"


def normalise_shareable_with(value: Any) -> str:
    """Coerce ``shareable_with`` to a canonical JSON array of counterparty ids.

    ``None`` becomes ``[]`` — deny — never a wildcard. There is deliberately no
    representation for "shareable with everyone"; widening is per-counterparty
    and is a deliberate act each time.
    """
    if value is None:
        return "[]"
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive
            raise InvariantError(f"shareable_with is not valid JSON: {exc}") from exc
    else:
        parsed = value
    if not isinstance(parsed, (list, tuple, set, frozenset)):
        raise InvariantError("shareable_with must be a list of counterparty ids")
    ids = sorted({str(item) for item in parsed})
    if "*" in ids:
        raise InvariantError(
            "shareable_with must not contain a wildcard — widening is per-counterparty"
        )
    return json.dumps(ids, separators=(",", ":"))


def parse_shareable_with(value: str | None) -> list[str]:
    if not value:
        return []
    parsed = json.loads(value)
    return [str(item) for item in parsed]


def validate_invariants(table: str, values: Mapping[str, Any]) -> None:
    """Raise :class:`InvariantError` unless ``values`` carries the full set."""
    if table not in RECORD_TABLES:
        if table in EXEMPT_TABLES:
            return
        raise InvariantError(
            f"unknown table {table!r}: add it to RECORD_TABLES or EXEMPT_TABLES "
            "with the reason it holds no client record"
        )

    missing = [f for f in INVARIANT_FIELDS if values.get(f) in (None, "")]
    if missing:
        raise InvariantError(
            f"{table}: missing invariant field(s) {', '.join(missing)}. "
            "Every record carries these from the first migration; retrofitting "
            "one rewrites every row written before it existed."
        )

    if values["visibility"] not in VISIBILITY_LEVELS:
        raise InvariantError(
            f"{table}: visibility {values['visibility']!r} not one of {VISIBILITY_LEVELS}"
        )
    if values["provenance"] not in PROVENANCE_LEVELS:
        raise InvariantError(
            f"{table}: provenance {values['provenance']!r} not one of {PROVENANCE_LEVELS}"
        )

    # shareable_with must be present as a normalised JSON array. Absent is
    # deny, which is fine; a non-array is a bug.
    parse_shareable_with(values["shareable_with"])

    if table == "commitment":
        direction = values.get("direction")
        if direction not in DIRECTIONS:
            raise InvariantError(
                f"commitment: direction {direction!r} not one of {DIRECTIONS}. "
                "direction is what turns a memory into a chase mechanic."
            )


def is_actionable(provenance: str) -> bool:
    """Whether a record may be acted on without a human confirming it first.

    ACTION_TIER_AND_REGISTER_SPEC §4: never chase on ``inferred`` — surface it
    to the principal as a question instead.
    """
    return provenance in ("verbatim", "paraphrase")
