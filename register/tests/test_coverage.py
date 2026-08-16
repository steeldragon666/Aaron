"""Acceptance 2 — coverage ≥80% against a manually compiled list.

The gate itself is measured against a real mailbox, which is an environment
connection this repository does not have. What is tested here is the
instrument: that it counts what it claims to count, that it is not generous,
and that it names what is missing — because the coverage number is only worth
anything if the principal can falsify it by pointing at a gap.
"""

from __future__ import annotations

import json

import pytest

from register.coverage import KnownCommitment, load_known, measure, similarity
from register.entities import create_commitment


def _seed(world, statement: str, direction: str = "to_principal", counterparty=None) -> str:
    return create_commitment(
        world.conn,
        tenant_id=world.tenant,
        direction=direction,
        statement=statement,
        made_at="2026-08-10T09:00:00+00:00",
        source_type="email",
        provenance="verbatim",
        produced_by="human:manual",
        counterparty_id=counterparty if counterparty is not None else world.henderson,
    )


def test_similarity_ignores_filler_words():
    assert similarity("I'll send the revised figures", "send revised figures") > 0.6
    assert similarity("I'll send the revised figures", "book the venue for October") < 0.1


def test_a_matching_entry_counts(world):
    _seed(world, "Ruth will send the revised Henderson figures by Friday.")
    known = [
        KnownCommitment(
            statement="Ruth sends revised figures",
            direction="to_principal",
            counterparty="ruth@henderson.example",
        )
    ]
    report = measure(world.conn, world.tenant, known)
    assert report.matched == 1
    assert report.coverage == 1.0
    assert report.passes


def test_the_wrong_direction_does_not_count(world):
    _seed(world, "Ruth will send the revised figures.", direction="to_principal")
    known = [KnownCommitment(statement="Ruth sends revised figures", direction="by_principal")]
    report = measure(world.conn, world.tenant, known)
    assert report.matched == 0
    assert not report.passes


def test_the_wrong_counterparty_does_not_count(world):
    _seed(world, "Ruth will send the revised figures.", counterparty=world.henderson)
    known = [
        KnownCommitment(
            statement="Ruth sends revised figures",
            direction="to_principal",
            counterparty="deals@veldt.example",
        )
    ]
    assert measure(world.conn, world.tenant, known).matched == 0


def test_one_register_entry_cannot_cover_two_known_commitments(world):
    _seed(world, "Ruth will send the revised figures.")
    known = [
        KnownCommitment("Ruth sends revised figures", "to_principal"),
        KnownCommitment("Ruth sends the revised figures", "to_principal"),
    ]
    report = measure(world.conn, world.tenant, known)
    assert report.matched == 1
    assert report.coverage == 0.5


def test_the_report_names_what_is_missing(world):
    _seed(world, "Ruth will send the revised figures.")
    known = [
        KnownCommitment("Ruth sends revised figures", "to_principal"),
        KnownCommitment("Book the Burdekin site visit", "by_principal"),
    ]
    report = measure(world.conn, world.tenant, known)
    assert report.matched == 1
    assert [m.known.statement for m in report.unmatched] == ["Book the Burdekin site visit"]
    rendered = report.render()
    assert "Burdekin" in rendered
    assert "BELOW THE 80% GATE" in rendered


def test_the_gate_is_eighty_percent(world):
    for index in range(8):
        _seed(world, f"Commitment number {index} about the Henderson schedule.")
    known = [
        KnownCommitment(f"Commitment number {i} about the Henderson schedule", "to_principal")
        for i in range(10)
    ]
    report = measure(world.conn, world.tenant, known)
    assert report.matched == 8
    assert report.coverage == pytest.approx(0.8)
    assert report.passes

    report_nine = measure(
        world.conn,
        world.tenant,
        [*known[:11], KnownCommitment("A tenth thing entirely", "to_principal")],
    )
    assert not report_nine.passes


def test_voided_entries_do_not_inflate_coverage(world):
    from register.entities import void_commitment

    commitment_id = _seed(world, "Ruth will send the revised figures.")
    void_commitment(world.conn, commitment_id, "never said", tenant_id=world.tenant)
    known = [KnownCommitment("Ruth sends revised figures", "to_principal")]
    assert measure(world.conn, world.tenant, known).matched == 0


def test_loading_the_manual_list(tmp_path):
    path = tmp_path / "known.json"
    path.write_text(
        json.dumps(
            [
                {
                    "statement": "Ruth sends revised figures",
                    "direction": "to_principal",
                    "counterparty": "ruth@henderson.example",
                    "due": "2026-08-14",
                }
            ]
        ),
        encoding="utf-8",
    )
    known = load_known(path)
    assert known[0].counterparty == "ruth@henderson.example"


def test_a_malformed_manual_list_is_refused(tmp_path):
    path = tmp_path / "known.json"
    path.write_text(json.dumps([{"statement": "no direction given"}]), encoding="utf-8")
    with pytest.raises(ValueError, match="direction"):
        load_known(path)
