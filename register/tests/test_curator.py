"""The curator queue and write governance.

ACTION_TIER §4: commitments extracted from conversation are proposals, not
records. Above a confidence threshold they auto-confirm with a daily digest,
because a per-item human gate gets skipped by week six.
"""

from __future__ import annotations

import json
from datetime import date

import pytest
from tests.test_ingest import MBOX

from register.curator import (
    DEFAULT_AUTO_CONFIRM_THRESHOLD,
    auto_confirm,
    confirm,
    principal_emails,
    propose_from_events,
    queued,
    reject,
    resolve_person,
    undo,
)
from register.errors import RegisterError
from register.ingest import ingest, unprocessed_events
from register.ingest.mailbox import MailboxAdapter
from register.invariants import parse_shareable_with


@pytest.fixture
def ingested(world, tmp_path):
    path = tmp_path / "inbox.mbox"
    path.write_text(MBOX, encoding="utf-8")
    ingest(world.conn, world.tenant, MailboxAdapter(path), produced_by="human:mailbox-sync")
    events = unprocessed_events(world.conn, world.tenant)
    senders = {
        events[0]["id"]: "ruth@henderson.example",
        events[1]["id"]: "aaron@carbonproject.com.au",
    }
    participants = {
        event["id"]: ["ruth@henderson.example", "aaron@carbonproject.com.au"] for event in events
    }
    return events, senders, participants


def test_principal_is_discoverable(world):
    assert principal_emails(world.conn, world.tenant) == ["aaron@carbonproject.com.au"]


def test_extraction_produces_proposals_not_records(world, ingested):
    events, senders, participants = ingested
    report = propose_from_events(
        world.conn,
        world.tenant,
        events=events,
        senders=senders,
        participants=participants,
        reference=date(2026, 8, 10),
    )
    assert report.proposed >= 2

    # Nothing has been written to the register yet.
    count = world.conn.execute(
        "SELECT count(*) AS n FROM commitment WHERE tenant_id = ?", (world.tenant,)
    ).fetchone()["n"]
    assert count == 0
    assert len(queued(world.conn, world.tenant)) == report.proposed


def test_confirming_writes_a_commitment_scoped_to_the_parties_present(world, ingested):
    events, senders, participants = ingested
    propose_from_events(
        world.conn,
        world.tenant,
        events=events,
        senders=senders,
        participants=participants,
        reference=date(2026, 8, 10),
    )
    proposal = queued(world.conn, world.tenant)[0]

    commitment_id = confirm(world.conn, world.tenant, proposal["id"], actor="human:principal")
    row = world.conn.execute("SELECT * FROM commitment WHERE id = ?", (commitment_id,)).fetchone()

    assert row["provenance"] == "verbatim"
    assert row["evidence_ref"] == proposal["source_ref"]
    assert row["produced_by"].startswith("rules:")

    # shareable_with is the parties on the source item, resolved to person ids.
    shareable = parse_shareable_with(row["shareable_with"])
    people = {
        r["id"]: r["email"]
        for r in world.conn.execute(
            "SELECT id, email FROM person WHERE tenant_id = ?", (world.tenant,)
        )
    }
    assert {people[pid] for pid in shareable} == {
        "ruth@henderson.example",
        "aaron@carbonproject.com.au",
    }


def test_a_proposal_cannot_be_confirmed_twice(world, ingested):
    events, senders, participants = ingested
    propose_from_events(
        world.conn, world.tenant, events=events, senders=senders, participants=participants
    )
    proposal = queued(world.conn, world.tenant)[0]
    confirm(world.conn, world.tenant, proposal["id"], actor="human:principal")
    with pytest.raises(RegisterError, match="already"):
        confirm(world.conn, world.tenant, proposal["id"], actor="human:principal")


def test_rejecting_writes_nothing_and_keeps_the_signal(world, ingested):
    events, senders, participants = ingested
    propose_from_events(
        world.conn, world.tenant, events=events, senders=senders, participants=participants
    )
    proposal = queued(world.conn, world.tenant)[0]

    reject(
        world.conn, world.tenant, proposal["id"], actor="human:principal", reason="that was a joke"
    )

    assert world.conn.execute("SELECT count(*) AS n FROM commitment").fetchone()["n"] == 0
    row = world.conn.execute(
        "SELECT state, resolved_by FROM curator_proposal WHERE id = ?", (proposal["id"],)
    ).fetchone()
    assert row["state"] == "rejected"
    assert "joke" in row["resolved_by"]


def test_auto_confirm_takes_the_confident_ones_and_reports_them(world, ingested):
    events, senders, participants = ingested
    propose_from_events(
        world.conn,
        world.tenant,
        events=events,
        senders=senders,
        participants=participants,
        reference=date(2026, 8, 10),
    )
    before = len(queued(world.conn, world.tenant))

    digest = auto_confirm(world.conn, world.tenant, threshold=0.85)

    assert digest.threshold == 0.85
    assert digest.auto_confirmed, "a firm dated promise should clear 0.85"
    for item in digest.auto_confirmed:
        assert item["confidence"] >= 0.85
        assert item["commitment_id"]
    assert digest.still_queued == before - len(digest.auto_confirmed)

    states = {
        row["state"]
        for row in world.conn.execute(
            "SELECT state FROM curator_proposal WHERE written_record_id IS NOT NULL"
        )
    }
    assert states == {"auto_confirmed"}


def test_below_the_threshold_nothing_is_written(world, ingested):
    events, senders, participants = ingested
    propose_from_events(
        world.conn, world.tenant, events=events, senders=senders, participants=participants
    )
    digest = auto_confirm(world.conn, world.tenant, threshold=0.999)
    assert digest.is_empty()
    assert world.conn.execute("SELECT count(*) AS n FROM commitment").fetchone()["n"] == 0


def test_undo_voids_rather_than_deletes(world, ingested):
    events, senders, participants = ingested
    propose_from_events(
        world.conn,
        world.tenant,
        events=events,
        senders=senders,
        participants=participants,
        reference=date(2026, 8, 10),
    )
    digest = auto_confirm(world.conn, world.tenant, threshold=0.85)
    commitment_id = digest.auto_confirmed[0]["commitment_id"]

    undo(
        world.conn,
        world.tenant,
        commitment_id,
        actor="human:principal",
        reason="Ruth never said that",
    )

    row = world.conn.execute(
        "SELECT status, last_action FROM commitment WHERE id = ?", (commitment_id,)
    ).fetchone()
    assert row["status"] == "void"
    assert "never said that" in row["last_action"]
    # The proposal is marked rejected so the extractor's rules can be tuned on it.
    assert (
        world.conn.execute(
            "SELECT state FROM curator_proposal WHERE written_record_id = ?", (commitment_id,)
        ).fetchone()["state"]
        == "rejected"
    )


def test_resolve_person_is_idempotent_and_marks_the_inference(world):
    first = resolve_person(
        world.conn, world.tenant, "  NewPerson@Example.com ", produced_by="rules:x"
    )
    second = resolve_person(
        world.conn, world.tenant, "newperson@example.com", produced_by="rules:x"
    )
    assert first == second
    row = world.conn.execute(
        "SELECT provenance, email FROM person WHERE id = ?", (first,)
    ).fetchone()
    assert row["provenance"] == "paraphrase"  # the address is verbatim, the identity is not
    assert row["email"] == "newperson@example.com"


def test_the_default_threshold_is_stated_rather_than_implied():
    assert 0.0 < DEFAULT_AUTO_CONFIRM_THRESHOLD < 1.0


def test_the_candidate_payload_is_inspectable(world, ingested):
    events, senders, participants = ingested
    propose_from_events(
        world.conn, world.tenant, events=events, senders=senders, participants=participants
    )
    candidate = json.loads(queued(world.conn, world.tenant)[0]["candidate"])
    assert {"statement", "direction", "provenance", "pattern"} <= set(candidate)
