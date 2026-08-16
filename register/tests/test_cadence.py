"""`last_substantive_contact` is derived, and cadence is advisory.

Two properties matter here and neither is about accuracy.

**It is derived from records, not classified from prose.** Meetings attended
and commitments made or acted on are first-class, carry provenance, and
demonstrably happened. A classifier deciding which inbound email counts as
"substantive" would be guessing at a rule the brief never settled.

**It errs toward silence.** The failure mode of the derived version is a date
that is older than reality. That produces a cadence alert the principal can
dismiss. The opposite error — a date that is newer than reality — produces
silence about a relationship that has actually gone cold, which is the thing
tracking cadence was supposed to catch.

And cadence never reaches the send path. It is a read-side computation that
writes nothing and that :func:`may_chase` does not consult.
"""

from __future__ import annotations

from register.entities import (
    CadenceAlert,
    cadence_alerts,
    create_commitment,
    create_meeting,
    create_person,
    derived_last_substantive_contact,
    may_chase,
    record_dark_meeting,
    refresh_last_substantive_contact,
)


def _cadenced(world, days: int = 30, name: str = "Cadenced Person") -> str:
    return create_person(
        world.conn,
        tenant_id=world.tenant,
        display_name=name,
        email=f"{name.split()[0].lower()}@example.test",
        cadence_days=days,
        produced_by="human:manual",
    )


# --- derivation -------------------------------------------------------------


def test_with_no_records_there_is_no_derived_contact(world):
    person = _cadenced(world)
    assert derived_last_substantive_contact(world.conn, world.tenant, person) is None


def test_a_meeting_attended_counts(world):
    person = _cadenced(world)
    create_meeting(
        world.conn,
        tenant_id=world.tenant,
        title="Quarterly review",
        starts_at="2026-07-02T01:00:00+00:00",
        produced_by="human:calendar-sync",
        attendees=[world.principal, person],
    )
    assert derived_last_substantive_contact(world.conn, world.tenant, person) == (
        "2026-07-02T01:00:00+00:00"
    )


def test_a_dark_meeting_still_counts_as_contact(world):
    """Attendance is known from the calendar even when the content is not.

    The register has no idea what was said, which is what `gap_flag` records.
    It does know they were in a room together, and that is enough to stop a
    cadence alert firing on a relationship that is plainly alive.
    """
    person = _cadenced(world)
    record_dark_meeting(
        world.conn,
        tenant_id=world.tenant,
        title="Private conversation",
        starts_at="2026-07-20T01:00:00+00:00",
        attendees=[world.principal, person],
        known_topics=["pricing"],
        produced_by="human:calendar-sync",
    )
    assert derived_last_substantive_contact(world.conn, world.tenant, person) == (
        "2026-07-20T01:00:00+00:00"
    )


def test_a_commitment_counts_and_the_most_recent_source_wins(world):
    person = _cadenced(world)
    create_meeting(
        world.conn,
        tenant_id=world.tenant,
        title="Early meeting",
        starts_at="2026-06-01T01:00:00+00:00",
        produced_by="human:calendar-sync",
        attendees=[world.principal, person],
    )
    create_commitment(
        world.conn,
        tenant_id=world.tenant,
        direction="to_principal",
        statement="They will send the schedule.",
        made_at="2026-08-01T09:00:00+00:00",
        source_type="email",
        provenance="verbatim",
        produced_by="human:manual",
        counterparty_id=person,
    )
    assert derived_last_substantive_contact(world.conn, world.tenant, person) == (
        "2026-08-01T09:00:00+00:00"
    )


def test_a_voided_commitment_does_not_count(world):
    """A commitment withdrawn as never-real is not evidence of contact."""
    from register.entities import void_commitment

    person = _cadenced(world)
    commitment_id = create_commitment(
        world.conn,
        tenant_id=world.tenant,
        direction="to_principal",
        statement="They will send the schedule.",
        made_at="2026-08-01T09:00:00+00:00",
        source_type="email",
        provenance="verbatim",
        produced_by="human:manual",
        counterparty_id=person,
    )
    void_commitment(world.conn, commitment_id, "never said")
    assert derived_last_substantive_contact(world.conn, world.tenant, person) is None


def test_refresh_writes_the_cache_and_is_idempotent(world):
    person = _cadenced(world)
    create_meeting(
        world.conn,
        tenant_id=world.tenant,
        title="Review",
        starts_at="2026-07-02T01:00:00+00:00",
        produced_by="human:calendar-sync",
        attendees=[world.principal, person],
    )

    assert refresh_last_substantive_contact(world.conn, world.tenant) >= 1
    row = world.conn.execute(
        "SELECT last_substantive_contact FROM person WHERE id = ?", (person,)
    ).fetchone()
    assert row["last_substantive_contact"] == "2026-07-02T01:00:00+00:00"

    assert refresh_last_substantive_contact(world.conn, world.tenant) == 0


# --- alerts are advisory ----------------------------------------------------


def test_a_quiet_relationship_produces_an_alert(world):
    person = _cadenced(world, days=30)
    create_meeting(
        world.conn,
        tenant_id=world.tenant,
        title="Last contact",
        starts_at="2026-06-01T01:00:00+00:00",
        produced_by="human:calendar-sync",
        attendees=[world.principal, person],
    )
    refresh_last_substantive_contact(world.conn, world.tenant)

    alerts = cadence_alerts(world.conn, world.tenant, as_of="2026-08-15")
    assert [a.person_id for a in alerts] == [person]
    assert alerts[0].days_since == 75


def test_a_recent_relationship_produces_none(world):
    person = _cadenced(world, days=30)
    create_meeting(
        world.conn,
        tenant_id=world.tenant,
        title="Recent",
        starts_at="2026-08-10T01:00:00+00:00",
        produced_by="human:calendar-sync",
        attendees=[world.principal, person],
    )
    refresh_last_substantive_contact(world.conn, world.tenant)
    assert cadence_alerts(world.conn, world.tenant, as_of="2026-08-15") == []


def test_a_person_with_no_stated_cadence_is_never_alerted(world):
    """A cadence nobody set is not a cadence the register gets to invent."""
    create_person(
        world.conn,
        tenant_id=world.tenant,
        display_name="No Cadence",
        email="nocadence@example.test",
        produced_by="human:manual",
    )
    assert cadence_alerts(world.conn, world.tenant, as_of="2026-08-15") == []


def test_never_contacted_is_flagged_rather_than_hidden(world):
    person = _cadenced(world, days=30)
    alerts = cadence_alerts(world.conn, world.tenant, as_of="2026-08-15")
    assert [a.person_id for a in alerts] == [person]
    assert alerts[0].never_contacted
    assert alerts[0].days_since is None


def test_a_cadence_alert_does_not_make_anything_chaseable(world):
    """The structural claim: cadence is advisory and cannot become an action.

    An overdue relationship changes nothing about what the agent may do. There
    is no commitment to chase — the silence *is* the observation — and nothing
    in the send path reads a cadence alert.
    """
    person = _cadenced(world, days=1)
    commitment_id = create_commitment(
        world.conn,
        tenant_id=world.tenant,
        direction="to_principal",
        statement="They said they would think about it.",
        made_at="2026-06-01T09:00:00+00:00",
        source_type="email",
        provenance="inferred",  # not actionable, and cadence must not change that
        produced_by="human:manual",
        counterparty_id=person,
    )
    refresh_last_substantive_contact(world.conn, world.tenant)

    assert cadence_alerts(world.conn, world.tenant, as_of="2026-08-15")

    row = dict(
        world.conn.execute("SELECT * FROM commitment WHERE id = ?", (commitment_id,)).fetchone()
    )
    assert not may_chase(world.conn, row).allowed


def test_cadence_alerts_write_nothing(world):
    person = _cadenced(world, days=1)
    assert person
    before = world.conn.execute("SELECT count(*) AS n FROM commitment").fetchone()["n"]
    accesses = world.conn.execute("SELECT count(*) AS n FROM access_log").fetchone()["n"]

    cadence_alerts(world.conn, world.tenant, as_of="2026-08-15")

    assert world.conn.execute("SELECT count(*) AS n FROM commitment").fetchone()["n"] == before
    assert world.conn.execute("SELECT count(*) AS n FROM access_log").fetchone()["n"] == accesses


def test_the_alert_carries_what_a_digest_needs(world):
    person = _cadenced(world, days=30, name="Ruth Henderson")
    alerts = cadence_alerts(world.conn, world.tenant, as_of="2026-08-15")
    assert isinstance(alerts[0], CadenceAlert)
    assert alerts[0].display_name == "Ruth Henderson"
    assert alerts[0].cadence_days == 30
    assert alerts[0].person_id == person
