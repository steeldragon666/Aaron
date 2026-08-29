"""Ingestion, redaction and extraction.

Acceptance 1's mechanism: mailbox and calendar, read-only and continuous, plus
manual entry. The live-mailbox half of acceptance 1 is an environment
connection, not code — see README, "What is not done".

The redaction tests are the ones with teeth. CLAUDE.md §3: redaction runs
before anything is persisted, and any string that reaches a log is assumed
recoverable by anyone with host access.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from register.extract import extract_from_event, parse_due, sentences
from register.ingest import ingest, unprocessed_events
from register.ingest.calendar import CalendarAdapter, parse_ics
from register.ingest.mailbox import MailboxAdapter
from register.ingest.manual import ManualAdapter, manual_item
from register.redaction import assert_no_secrets, redact

MBOX = """From ruth@henderson.example Mon Aug 10 09:00:00 2026
From: Ruth Henderson <ruth@henderson.example>
To: Aaron <aaron@carbonproject.com.au>
Subject: Revised figures
Date: Mon, 10 Aug 2026 09:00:00 +1000
Message-ID: <first@henderson.example>

Thanks for the call. I'll send the revised figures by Friday.
The staging password is hunter2hunter2 in case you need it.

From aaron@carbonproject.com.au Mon Aug 10 11:00:00 2026
From: Aaron <aaron@carbonproject.com.au>
To: Ruth Henderson <ruth@henderson.example>
Subject: Re: Revised figures
Date: Mon, 10 Aug 2026 11:00:00 +1000
Message-ID: <second@carbonproject.com.au>
In-Reply-To: <first@henderson.example>

Appreciated. I'll get you the updated schedule by 2026-08-14.

On Mon, 10 Aug 2026, Ruth Henderson wrote:
> I'll send the revised figures by Friday.
"""

ICS = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:evt-henderson-review
SUMMARY:Henderson supply review
DESCRIPTION:Revised unit price and the delivery window.\\nBring the schedule.
DTSTART:20260811T010000Z
DTEND:20260811T020000Z
ORGANIZER:mailto:aaron@carbonproject.com.au
ATTENDEE;CN=Ruth Henderson;ROLE=REQ-PARTICIPANT:mailto:ruth@henderson.example
END:VEVENT
BEGIN:VEVENT
UID:evt-veldt
SUMMARY:Veldt diligence
DTSTART:20260812T230000Z
ATTENDEE;CN=Veldt Capital:mailto:deals@veldt.example
END:VEVENT
END:VCALENDAR
"""


@pytest.fixture
def mbox_path(tmp_path) -> Path:
    path = tmp_path / "inbox.mbox"
    path.write_text(MBOX, encoding="utf-8")
    return path


@pytest.fixture
def ics_path(tmp_path) -> Path:
    path = tmp_path / "calendar.ics"
    path.write_text(ICS, encoding="utf-8")
    return path


# --- redaction --------------------------------------------------------------


@pytest.mark.parametrize(
    "text,label",
    [
        ("the password: hunter2hunter2 is live", "labelled_secret"),
        ("key AKIAIOSFODNN7EXAMPLE rotated", "aws_access_key"),
        ("token ghp_abcdefghijklmnopqrstuvwxyz0123456789", "github_token"),
        ("use sk-abcdefghijklmnopqrstuvwx for now", "openai_style_key"),
        ("https://admin:s3cret@internal.example/db", "basic_auth_url"),
        ("-----BEGIN RSA PRIVATE KEY-----\nabc\n-----END RSA PRIVATE KEY-----", "private_key"),
    ],
)
def test_secrets_are_redacted(text, label):
    outcome = redact(text)
    assert outcome.count >= 1
    assert label in outcome.labels
    assert "hunter2hunter2" not in outcome.text
    assert "s3cret" not in outcome.text


def test_ordinary_prose_is_left_alone():
    text = "I'll send the revised figures by Friday, invoice 4051 attached."
    assert redact(text).clean
    assert redact(text).text == text


def test_a_long_reference_number_is_not_mistaken_for_a_card():
    assert redact("Our purchase order is 1234567890123456789").clean


def test_a_real_card_number_is_redacted():
    outcome = redact("card 4111111111111111 on file")
    assert "card_number" in outcome.labels
    assert "4111111111111111" not in outcome.text


def test_assert_no_secrets_raises_on_the_write_path():
    with pytest.raises(ValueError, match="refusing to persist"):
        assert_no_secrets("api_key=abcdef123456", "commitment.statement")


def test_redaction_runs_before_persistence(world, mbox_path):
    report = ingest(
        world.conn, world.tenant, MailboxAdapter(mbox_path), produced_by="human:mailbox-sync"
    )
    assert report.persisted == 2
    assert report.redactions >= 1

    bodies = [
        row["body"]
        for row in world.conn.execute(
            "SELECT body FROM ingest_event WHERE tenant_id = ?", (world.tenant,)
        )
    ]
    assert all("hunter2hunter2" not in body for body in bodies)
    assert any("[REDACTED:labelled_secret]" in body for body in bodies)


# --- mailbox ----------------------------------------------------------------


def test_mailbox_adapter_reads_headers_and_plain_body(mbox_path):
    items = list(MailboxAdapter(mbox_path).read())
    assert [item.source_id for item in items] == [
        "<first@henderson.example>",
        "<second@carbonproject.com.au>",
    ]
    assert items[0].summary == "Revised figures"
    assert "revised figures by Friday" in items[0].body
    assert items[0].metadata["from"] == ["ruth@henderson.example"]
    assert set(items[0].participants) == {"ruth@henderson.example", "aaron@carbonproject.com.au"}
    assert items[0].occurred_at.startswith("2026-08-10T09:00:00")


def test_ingest_is_idempotent_across_reruns(world, mbox_path):
    first = ingest(world.conn, world.tenant, MailboxAdapter(mbox_path), produced_by="human:sync")
    second = ingest(world.conn, world.tenant, MailboxAdapter(mbox_path), produced_by="human:sync")
    assert first.persisted == 2
    assert second.persisted == 0
    assert second.duplicates == 2


# --- calendar ---------------------------------------------------------------


def test_ics_parsing_handles_folding_escapes_and_attendees(ics_path):
    events = list(parse_ics(ics_path.read_text(encoding="utf-8")))
    assert [e["uid"] for e in events] == ["evt-henderson-review", "evt-veldt"]
    assert events[0]["starts_at"] == "2026-08-11T01:00:00+00:00"
    assert "Bring the schedule." in events[0]["description"]
    assert events[0]["attendees"][0]["email"] == "ruth@henderson.example"


def test_calendar_adapter_yields_participants_including_the_organizer(ics_path):
    items = list(CalendarAdapter(ics_path).read())
    assert set(items[0].participants) == {
        "ruth@henderson.example",
        "aaron@carbonproject.com.au",
    }


def test_calendar_adapter_reads_a_directory(tmp_path, ics_path):
    directory = tmp_path / "cal"
    directory.mkdir()
    (directory / "a.ics").write_text(ics_path.read_text(encoding="utf-8"), encoding="utf-8")
    assert len(list(CalendarAdapter(directory).read())) == 2


def test_an_unparseable_date_is_left_absent_rather_than_guessed():
    events = list(parse_ics("BEGIN:VEVENT\nUID:x\nDTSTART:next tuesday\nEND:VEVENT\n"))
    assert events[0]["starts_at"] is None


# --- adapters are interchangeable -------------------------------------------


def test_adding_a_source_is_a_new_adapter_not_a_schema_change(world):
    adapter = ManualAdapter(
        [manual_item(source_id="note-1", summary="Told Ruth we would ship Friday.")]
    )
    report = ingest(world.conn, world.tenant, adapter, produced_by="human:manual")
    assert report.persisted == 1
    row = world.conn.execute(
        "SELECT adapter, summary FROM ingest_event WHERE source_id = 'note-1'"
    ).fetchone()
    assert row["adapter"] == "manual"


def test_unprocessed_events_excludes_anything_already_proposed(world, mbox_path):
    ingest(world.conn, world.tenant, MailboxAdapter(mbox_path), produced_by="human:sync")
    assert len(unprocessed_events(world.conn, world.tenant)) == 2


# --- extraction -------------------------------------------------------------


def test_sentences_stop_at_the_quoted_reply():
    body = "I'll get you the schedule.\n\nOn Mon, Ruth Henderson wrote:\n> I'll send the figures."
    assert sentences(body) == ["I'll get you the schedule."]


@pytest.mark.parametrize(
    "text,expected",
    [
        ("by 2026-08-14", "2026-08-14"),
        ("by 14 August", "2026-08-14"),
        ("by August 14", "2026-08-14"),
        ("tomorrow", "2026-08-11"),
        ("by Friday", "2026-08-14"),
        ("end of the week", "2026-08-14"),
        ("end of the month", "2026-08-31"),
        ("at some point", None),
        ("soon", None),
    ],
)
def test_due_dates_are_parsed_or_left_alone(text, expected):
    assert parse_due(text, date(2026, 8, 10)) == expected


def test_direction_follows_the_sender(world):
    event = {
        "id": "ie_1",
        "adapter": "mailbox",
        "summary": "Revised figures",
        "body": "I'll send the revised figures by Friday.",
        "occurred_at": "2026-08-10T09:00:00+00:00",
    }
    principal = ["aaron@carbonproject.com.au"]

    from_counterparty = extract_from_event(
        event,
        principal_emails=principal,
        sender="ruth@henderson.example",
        participants=["ruth@henderson.example", *principal],
    )
    assert [c.direction for c in from_counterparty] == ["to_principal"]
    assert from_counterparty[0].counterparty_email == "ruth@henderson.example"
    assert from_counterparty[0].due == "2026-08-14"

    from_principal = extract_from_event(
        event,
        principal_emails=principal,
        sender="aaron@carbonproject.com.au",
        participants=["ruth@henderson.example", *principal],
    )
    assert [c.direction for c in from_principal] == ["by_principal"]


def test_a_request_reverses_who_owes(world):
    event = {
        "id": "ie_2",
        "adapter": "mailbox",
        "summary": "Figures",
        "body": "Could you send the revised figures by Friday?",
        "occurred_at": "2026-08-10T09:00:00+00:00",
    }
    principal = ["aaron@carbonproject.com.au"]

    principal_asks = extract_from_event(
        event,
        principal_emails=principal,
        sender="aaron@carbonproject.com.au",
        participants=["ruth@henderson.example", *principal],
    )
    assert [c.direction for c in principal_asks] == ["to_principal"]

    counterparty_asks = extract_from_event(
        event,
        principal_emails=principal,
        sender="ruth@henderson.example",
        participants=["ruth@henderson.example", *principal],
    )
    assert [c.direction for c in counterparty_asks] == ["by_principal"]


def test_without_a_sender_the_extractor_declines_rather_than_guesses():
    event = {"id": "ie_3", "adapter": "mailbox", "summary": "x", "body": "I'll send it Friday."}
    assert (
        extract_from_event(event, principal_emails=["aaron@carbonproject.com.au"], sender=None)
        == []
    )


def test_negations_are_not_commitments():
    event = {
        "id": "ie_4",
        "adapter": "mailbox",
        "summary": "x",
        "body": "I won't be able to send the figures this week.",
        "occurred_at": "2026-08-10T09:00:00+00:00",
    }
    assert (
        extract_from_event(event, principal_emails=["a@b.example"], sender="ruth@henderson.example")
        == []
    )


def test_hedging_lowers_confidence_below_the_auto_confirm_threshold():
    base = {
        "id": "ie_5",
        "adapter": "mailbox",
        "summary": "x",
        "occurred_at": "2026-08-10T09:00:00+00:00",
    }
    firm = extract_from_event(
        {**base, "body": "I will send the figures by Friday."},
        principal_emails=["a@b.example"],
        sender="ruth@henderson.example",
    )
    hedged = extract_from_event(
        {**base, "body": "I will maybe send the figures by Friday if I can."},
        principal_emails=["a@b.example"],
        sender="ruth@henderson.example",
    )
    assert firm[0].confidence > hedged[0].confidence
    assert hedged[0].confidence < 0.85


def test_a_calendar_event_proposes_no_commitments():
    """A calendar entry is a source of truth about the meeting, not about what
    anyone promised in it."""
    event = {
        "id": "ie_6",
        "adapter": "calendar",
        "summary": "Henderson review",
        "body": "I'll bring the schedule.",
        "occurred_at": "2026-08-11T01:00:00+00:00",
    }
    assert extract_from_event(event, principal_emails=["a@b.example"], sender="a@b.example") == []
