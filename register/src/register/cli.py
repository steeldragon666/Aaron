"""Command line for the register.

Enough to run a real Phase 0 instrumentation week: point it at a mailbox and a
calendar, look at what it proposed, confirm, and measure coverage.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .coverage import load_known, measure
from .curator import auto_confirm, confirm, principal_emails, propose_from_events, queued, reject
from .db import open_register
from .entities import create_person, create_tenant, dark_periods, open_loops
from .errors import LedgerError
from .ingest import ingest, unprocessed_events
from .ingest.calendar import CalendarAdapter
from .ingest.mailbox import MailboxAdapter
from .ledger import (
    ALL_STATUSES,
    ActionRequest,
    Prediction,
    append_ar,
    fold_all,
    score,
    set_status,
    verify_chain,
)

DEFAULT_DB = "register.sqlite3"


def _conn(args: argparse.Namespace):
    return open_register(args.db)


def cmd_init(args: argparse.Namespace) -> int:
    conn = _conn(args)
    existing = conn.execute("SELECT id FROM tenant WHERE id = ?", (args.tenant,)).fetchone()
    if existing is None:
        create_tenant(conn, args.name, is_zero=args.zero, tenant_id=args.tenant)
        print(f"tenant {args.tenant} created ({args.name})")
    else:
        print(f"tenant {args.tenant} already present")

    if args.principal_email:
        row = conn.execute(
            "SELECT id FROM person WHERE tenant_id = ? AND email = ?",
            (args.tenant, args.principal_email.lower()),
        ).fetchone()
        if row is None:
            pid = create_person(
                conn,
                tenant_id=args.tenant,
                display_name=args.principal_name or args.principal_email,
                email=args.principal_email.lower(),
                is_principal=True,
                produced_by="human:manual",
                relationship="principal",
            )
            print(f"principal {args.principal_email} created as {pid}")
    return 0


def cmd_ingest(args: argparse.Namespace) -> int:
    conn = _conn(args)
    total = 0
    if args.mailbox:
        report = ingest(
            conn, args.tenant, MailboxAdapter(args.mailbox), produced_by="human:mailbox-sync"
        )
        print(
            f"mailbox : {report.seen} seen, {report.persisted} new, "
            f"{report.duplicates} already known, {report.redactions} redactions"
        )
        total += report.persisted
    if args.calendar:
        report = ingest(
            conn, args.tenant, CalendarAdapter(args.calendar), produced_by="human:calendar-sync"
        )
        print(
            f"calendar: {report.seen} seen, {report.persisted} new, "
            f"{report.duplicates} already known, {report.redactions} redactions"
        )
        total += report.persisted
    if not args.mailbox and not args.calendar:
        print("nothing to ingest: pass --mailbox and/or --calendar", file=sys.stderr)
        return 2
    print(f"{total} new ingest events")
    return 0


def cmd_propose(args: argparse.Namespace) -> int:
    conn = _conn(args)
    if not principal_emails(conn, args.tenant):
        print(
            "no principal on this tenant — run `register init --principal-email` first; "
            "direction cannot be established without one",
            file=sys.stderr,
        )
        return 2

    senders: dict[str, str] = {}
    participants: dict[str, list[str]] = {}
    if args.senders:
        raw = json.loads(Path(args.senders).read_text(encoding="utf-8"))
        senders = {k: str(v) for k, v in raw.get("senders", {}).items()}
        participants = {k: list(v) for k, v in raw.get("participants", {}).items()}

    events = unprocessed_events(conn, args.tenant)
    report = propose_from_events(
        conn, args.tenant, events=events, senders=senders, participants=participants
    )
    print(f"{report.events_read} events read, {report.proposed} proposals queued")
    return 0


def cmd_queue(args: argparse.Namespace) -> int:
    conn = _conn(args)
    rows = queued(conn, args.tenant)
    if not rows:
        print("curator queue is empty")
        return 0
    for row in rows:
        candidate = json.loads(row["candidate"])
        print(
            f"{row['id']}  {row['confidence']:.2f}  {candidate['direction']:<13} "
            f"due {candidate.get('due') or '—':<12} {candidate['statement'][:80]}"
        )
    return 0


def cmd_confirm(args: argparse.Namespace) -> int:
    conn = _conn(args)
    commitment_id = confirm(conn, args.tenant, args.proposal, actor=args.actor)
    print(f"wrote commitment {commitment_id}")
    return 0


def cmd_reject(args: argparse.Namespace) -> int:
    conn = _conn(args)
    reject(conn, args.tenant, args.proposal, actor=args.actor, reason=args.reason)
    print(f"rejected {args.proposal}")
    return 0


def cmd_digest(args: argparse.Namespace) -> int:
    conn = _conn(args)
    digest = auto_confirm(conn, args.tenant, threshold=args.threshold)
    if digest.is_empty():
        print(f"nothing auto-confirmed at or above {digest.threshold:.2f}")
    else:
        print(f"Auto-confirmed at or above {digest.threshold:.2f}:")
        for item in digest.auto_confirmed:
            print(
                f"  {item['confidence']:.2f}  {item['direction']:<13} "
                f"due {item['due'] or '—':<12} {item['statement'][:80]}"
            )
    print(f"{digest.still_queued} still waiting for a human")
    return 0


def cmd_loops(args: argparse.Namespace) -> int:
    conn = _conn(args)
    loops = open_loops(conn, args.tenant)
    for direction in ("by_principal", "to_principal", "witnessed"):
        rows = loops[direction]
        print(f"\n{direction} ({len(rows)})")
        for row in rows:
            print(f"  due {row['due'] or '—':<12} {row['statement'][:90]}")

    gaps = dark_periods(conn, args.tenant)
    if gaps:
        print(f"\nDark periods — no record of what was agreed ({len(gaps)}):")
        for gap in gaps:
            print(f"  {gap['starts_at']}  {gap['title']}")
    return 0


def cmd_ar_add(args: argparse.Namespace) -> int:
    """Append an AR from a JSON file.

    Sprint 1 has no agents, so the first ARs are written by hand. The rules the
    ledger enforces — a falsifiable prediction, evidence, an owner, the cap of
    five open per agent — apply identically either way, which is the point of
    having a way to do this before the agents exist.
    """
    conn = _conn(args)
    body = json.loads(Path(args.file).read_text(encoding="utf-8"))
    prediction = body.pop("prediction", {})
    ar = ActionRequest(prediction=Prediction(**prediction), **body)
    try:
        ar_id = append_ar(conn, args.tenant, ar)
    except LedgerError as exc:
        print(f"rejected: {exc}", file=sys.stderr)
        return 1
    print(f"appended {ar_id}")
    return 0


def cmd_ar_status(args: argparse.Namespace) -> int:
    conn = _conn(args)
    try:
        set_status(conn, args.tenant, args.ar, args.status, actor=args.actor, note=args.note)
    except LedgerError as exc:
        print(f"rejected: {exc}", file=sys.stderr)
        return 1
    print(f"{args.ar} → {args.status}")
    return 0


def cmd_ar_score(args: argparse.Namespace) -> int:
    """Resolve a prediction. Unacted ARs are scored too — that is the point."""
    conn = _conn(args)
    try:
        brier = score(conn, args.tenant, args.ar, outcome=args.outcome, actor=args.actor)
    except LedgerError as exc:
        print(f"rejected: {exc}", file=sys.stderr)
        return 1
    if brier != brier:  # NaN — no stated confidence, so no calibration component
        print(f"{args.ar} resolved {args.outcome} (no stated confidence, accuracy only)")
    else:
        print(f"{args.ar} resolved {args.outcome}, Brier component {brier:.3f}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    conn = _conn(args)
    report = verify_chain(conn)
    if report.ok:
        print(f"ledger chain verified: {report.entries} entries, head {report.head[:16]}…")
        return 0
    print(
        f"LEDGER CHAIN BROKEN at seq {report.broken_at}: {report.detail}",
        file=sys.stderr,
    )
    return 1


def cmd_ars(args: argparse.Namespace) -> int:
    conn = _conn(args)
    states = fold_all(conn, args.tenant)
    if not states:
        print("no ARs")
        return 0
    for ar_id, state in sorted(states.items(), key=lambda kv: kv[1].get("opened_at", "")):
        print(
            f"{ar_id}  {state['agent']:<8} {state['status']:<11} "
            f"resolves {state['prediction']['resolves_on']}  {state['claim'][:70]}"
        )
    return 0


def cmd_coverage(args: argparse.Namespace) -> int:
    conn = _conn(args)
    known = load_known(args.known)
    report = measure(conn, args.tenant, known)
    print(report.render())
    return 0 if report.passes else 1


def cmd_reads(args: argparse.Namespace) -> int:
    """Show the access log — the audit trail the product sells."""
    conn = _conn(args)
    rows = conn.execute(
        """
        SELECT at, actor, actor_role, counterparty_scope, entity, record_id, decision, reason
        FROM access_log WHERE tenant_id = ?
        ORDER BY id DESC LIMIT ?
        """,
        (args.tenant, args.limit),
    ).fetchall()
    for row in rows:
        scope = f" →{row['counterparty_scope']}" if row["counterparty_scope"] else ""
        print(
            f"{row['at']}  {row['decision']:<5} {row['actor']}/{row['actor_role']}{scope}  "
            f"{row['entity']}/{row['record_id']}  {row['reason']}"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="register", description=__doc__)
    parser.add_argument(
        "--db", default=DEFAULT_DB, help=f"register database (default {DEFAULT_DB})"
    )
    parser.add_argument("--tenant", default="tn_carbonproject", help="tenant id")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="create the tenant and its principal")
    p.add_argument("--name", default="The Carbon Project")
    p.add_argument("--zero", action="store_true", help="mark as tenant zero")
    p.add_argument("--principal-email")
    p.add_argument("--principal-name")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("ingest", help="read a mailbox and/or a calendar")
    p.add_argument("--mailbox", help="Maildir directory or mbox file")
    p.add_argument("--calendar", help=".ics file or a directory of them")
    p.set_defaults(func=cmd_ingest)

    p = sub.add_parser("propose", help="extract commitment candidates into the curator queue")
    p.add_argument("--senders", help="JSON file mapping ingest event ids to senders/participants")
    p.set_defaults(func=cmd_propose)

    p = sub.add_parser("queue", help="show the curator queue")
    p.set_defaults(func=cmd_queue)

    p = sub.add_parser("confirm", help="confirm one proposal")
    p.add_argument("proposal")
    p.add_argument("--actor", default="human:principal")
    p.set_defaults(func=cmd_confirm)

    p = sub.add_parser("reject", help="reject one proposal")
    p.add_argument("proposal")
    p.add_argument("--actor", default="human:principal")
    p.add_argument("--reason", default="")
    p.set_defaults(func=cmd_reject)

    p = sub.add_parser("digest", help="auto-confirm above threshold and print the daily digest")
    p.add_argument("--threshold", type=float, default=0.85)
    p.set_defaults(func=cmd_digest)

    p = sub.add_parser("loops", help="open commitments, both directions, plus dark periods")
    p.set_defaults(func=cmd_loops)

    p = sub.add_parser("ar-add", help="append an Action Request from a JSON file")
    p.add_argument("file")
    p.set_defaults(func=cmd_ar_add)

    p = sub.add_parser("ar-status", help="append a status change to an AR")
    p.add_argument("ar")
    p.add_argument("status", choices=sorted(ALL_STATUSES))
    p.add_argument("--actor", default="human:principal")
    p.add_argument("--note", default="")
    p.set_defaults(func=cmd_ar_status)

    p = sub.add_parser("ar-score", help="resolve an AR's prediction — acted on or not")
    p.add_argument("ar")
    p.add_argument("outcome", choices=["correct", "incorrect", "unresolved", "void"])
    p.add_argument("--actor", default="human:principal")
    p.set_defaults(func=cmd_ar_score)

    p = sub.add_parser("verify", help="verify the AR ledger hash chain end to end")
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("ars", help="list Action Requests and their current state")
    p.set_defaults(func=cmd_ars)

    p = sub.add_parser("coverage", help="score the register against a manual commitment list")
    p.add_argument("known", help="JSON array of known commitments")
    p.set_defaults(func=cmd_coverage)

    p = sub.add_parser("reads", help="show the access log")
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_reads)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
