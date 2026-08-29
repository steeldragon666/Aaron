"""Every way out of the database is classified, or this fails.

Raised by an independent review of the PR: `open_loops`, `dark_periods`,
`fold`, `queued` and friends run their own SQL and return full record rows
without a :class:`Reader`, without `evaluate` and without an access-log entry.
A caller working in a counterparty's context can call them with a `tenant_id`
alone and get facts that counterparty is not party to.

Two things are true about that at once, and both matter.

**It is not a live leak in Sprint 1.** There is no send path, no agent and no
counterparty-scoped caller — the only caller is a CLI the principal runs
against their own register. CLAUDE.md §4 specifies the check *in the send
path*, and the send path is Sprint 2 by construction.

**It is still the failure mode worth designing against.** "Not currently
exploited" describes today's callers, not the code. When the send path is
built, the obvious thing to reach for is `open_loops` — it is there, it returns
exactly the right shape, and using it bypasses the check silently. That is the
same structural mistake as a verification gate that only runs where the author
chooses to run it: enforcement you have to opt into is a convention.

This test does not fix that. It makes it impossible to add another unguarded
read without saying so — the same move as the human/machine column split and
the migration guard. `access.UNGUARDED_READS` is also the work list for the
Sprint 2 send path: everything in it that the send path wants must be
re-expressed through a Reader first.
"""

from __future__ import annotations

import importlib
import inspect

import pytest

from register.access import NOT_A_READ, UNGUARDED_READS

# Modules deliberately outside the scan, and why each one is. Everything else
# in the package is scanned, so a new module is a failure until someone triages
# it — the hardcoded list this replaced omitted `register.ingest`, whose
# `unprocessed_events` runs SQL and returns full rows. A completeness guard with
# a blind spot is the specific thing this file exists to prevent, so it had to
# stop being a list somebody remembers to extend.
NOT_SCANNED: dict[str, str] = {
    "access": "the guarded path itself — its own reads take a Reader",
    "store": "the write boundary; covered by test_invariants",
    "db": "connections and migrations, no record reads",
    "cli": "the caller, exercised through the commands it runs",
    "canonical": "hashing, no database",
    "errors": "exception types",
    "ids": "identifier generation",
    "invariants": "field validation, no database",
    "redaction": "string matching, no database",
    "routing": "the model boundary, no database",
    "extract": "pure functions over message text",
}


def _scanned_modules() -> list[str]:
    """Every module in the package that is not explicitly excluded."""
    import pkgutil

    import register

    names = []
    for info in pkgutil.iter_modules(register.__path__):
        if info.name.startswith("_") or info.name in NOT_SCANNED:
            continue
        names.append(info.name)
    return sorted(names)


def _public_functions() -> dict[str, object]:
    found: dict[str, object] = {}
    for name in _scanned_modules():
        module = importlib.import_module(f"register.{name}")
        for attr, value in vars(module).items():
            if attr.startswith("_") or not inspect.isfunction(value):
                continue
            if value.__module__ != module.__name__:  # re-exported import
                continue
            found[f"{name}.{attr}"] = value
    return found


def test_the_exclusion_list_names_only_modules_that_exist():
    """A stale exclusion silently shrinks the scan."""
    import pkgutil

    import register

    present = {info.name for info in pkgutil.iter_modules(register.__path__)}
    stale = sorted(set(NOT_SCANNED) - present)
    assert not stale, f"{stale} are excluded from the scan but no longer exist"


def test_the_scan_reaches_the_ingest_package():
    """The blind spot that made this discovery necessary, pinned."""
    assert "ingest" in _scanned_modules()


def test_every_public_function_is_classified():
    """A new read that nobody triaged fails here rather than shipping quietly."""
    functions = _public_functions()
    classified = set(UNGUARDED_READS) | set(NOT_A_READ)

    unclassified = sorted(set(functions) - classified)
    assert not unclassified, (
        f"{unclassified} are in neither access.UNGUARDED_READS nor access.NOT_A_READ.\n"
        "Decide which: does this hand back record content? If so it belongs in "
        "UNGUARDED_READS with the reason it is allowed to skip the Reader, and it "
        "goes on the Sprint 2 send-path work list. If it returns an id, a count or "
        "nothing, say so in NOT_A_READ."
    )


def test_the_classification_does_not_name_functions_that_no_longer_exist():
    """A stale allowlist entry reads as coverage it is not providing."""
    functions = _public_functions()
    stale = sorted((set(UNGUARDED_READS) | set(NOT_A_READ)) - set(functions))
    assert not stale, f"{stale} are classified but no longer exist"


def test_no_function_is_classified_both_ways():
    overlap = sorted(set(UNGUARDED_READS) & set(NOT_A_READ))
    assert not overlap, f"{overlap} classified as both a record read and not a read"


@pytest.mark.parametrize("name", sorted(UNGUARDED_READS))
def test_every_unguarded_read_carries_a_reason(name):
    """An empty reason is an entry someone added to silence the test."""
    reason = UNGUARDED_READS[name]
    assert len(reason.strip()) > 30, f"{name}: say why this may skip the Reader"


def test_the_access_aware_path_actually_takes_a_reader():
    """The other half: the functions that are supposed to be guarded, are."""
    from register import access

    for name in ("read_one", "query", "filter_readable", "widen_shareable_with"):
        params = list(inspect.signature(getattr(access, name)).parameters)
        assert "reader" in params, f"access.{name} no longer takes a Reader"


def test_an_unguarded_read_really_does_return_content_the_reader_path_would_gate(world):
    """Demonstrates the finding rather than asserting it in prose.

    `principal_only` is the strictest visibility there is. The Reader path
    denies it to an `all_users` reader; `open_loops` hands the same row back to
    anyone holding the connection. This test passing is the *statement of the
    gap*, not an approval of it — it fails the day the send path is wired
    through `open_loops`, which is exactly when someone should look.
    """
    from register.access import Reader, read_one
    from register.entities import create_commitment, open_loops
    from register.errors import AccessDenied

    commitment_id = create_commitment(
        world.conn,
        tenant_id=world.tenant,
        direction="by_principal",
        statement="I'll fund the Henderson earn-out personally if it comes to it.",
        made_at="2026-08-10T09:00:00+00:00",
        source_type="manual",
        provenance="verbatim",
        produced_by="human:manual",
        visibility="principal_only",
    )

    broad = Reader(tenant_id=world.tenant, actor="someone", role="user")
    with pytest.raises(AccessDenied):
        read_one(world.conn, broad, "commitment", commitment_id)

    unguarded = open_loops(world.conn, world.tenant)["by_principal"]
    assert any(row["id"] == commitment_id for row in unguarded)
    assert "entities.open_loops" in UNGUARDED_READS
