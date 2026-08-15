"""Ingestion.

Two paths this sprint: mailbox and calendar, read-only and continuous; and
manual entry. Transcripts, voice dumps and CRM come later, and the point of
this interface is that adding one of them is a new adapter, not a schema
change.

Every adapter yields :class:`SourceItem` values. The pipeline redacts, dedupes
and persists them; the adapter itself never touches the database, which is
what keeps "add a source" from turning into "change the register".

**No network.** Both adapters here read from the local filesystem — a Maildir
or mbox, and ``.ics`` files. Connectivity from M365, Google Workspace or a CRM
to an on-prem farm is an open item (CLAUDE.md, and ACTION_TIER §7 item 4), and
until it is settled the sync that lands mail on local disk is the boundary. An
adapter that opens a socket is a decision, not an implementation detail, and it
belongs on the other side of that item.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol

from ..ids import new_id
from ..invariants import default_visibility
from ..redaction import redact
from ..store import insert


@dataclass(frozen=True)
class SourceItem:
    """One item as an adapter found it, before redaction or persistence."""

    source_id: str  # adapter-native, stable across re-runs — the dedupe key
    kind: str  # 'email' | 'calendar' | 'manual'
    summary: str
    body: str = ""
    occurred_at: str | None = None
    participants: Sequence[str] = field(default_factory=tuple)  # email addresses
    metadata: dict[str, Any] = field(default_factory=dict)


class Adapter(Protocol):
    """A source of items. Read-only by construction — there is no write hook."""

    name: str

    def read(self) -> Iterator[SourceItem]: ...


def _sender(item: SourceItem) -> str | None:
    """The address the item came from, where the adapter knew it.

    Direction cannot be established without it, so it is stored rather than
    recovered later from a body that has already been redacted.
    """
    senders = item.metadata.get("from") or []
    if senders:
        return str(senders[0]).lower()
    organizer = item.metadata.get("organizer")
    return str(organizer).lower() if organizer else None


@dataclass
class IngestReport:
    seen: int = 0
    persisted: int = 0
    duplicates: int = 0
    redactions: int = 0
    event_ids: list[str] = field(default_factory=list)


def ingest(
    conn: sqlite3.Connection,
    tenant_id: str,
    adapter: Adapter,
    *,
    produced_by: str,
    visibility: str | None = None,
) -> IngestReport:
    """Pull everything the adapter has, redact it, and persist what is new.

    Redaction runs before the insert, not after. Nothing unredacted reaches
    the database, and nothing unredacted is logged on the way through.
    """
    report = IngestReport()
    for item in adapter.read():
        report.seen += 1

        existing = conn.execute(
            "SELECT id FROM ingest_event WHERE tenant_id = ? AND adapter = ? AND source_id = ?",
            (tenant_id, adapter.name, item.source_id),
        ).fetchone()
        if existing is not None:
            report.duplicates += 1
            continue

        clean_summary = redact(item.summary)
        clean_body = redact(item.body)
        redactions = clean_summary.count + clean_body.count
        report.redactions += redactions

        event_id = new_id("ingest_event")
        insert(
            conn,
            "ingest_event",
            {
                "id": event_id,
                "tenant_id": tenant_id,
                "adapter": adapter.name,
                "source_id": item.source_id,
                "occurred_at": item.occurred_at,
                "summary": clean_summary.text,
                "body": clean_body.text,
                "redaction_count": redactions,
                "sender": _sender(item),
                "participants": json.dumps(
                    sorted({p.lower() for p in item.participants}), separators=(",", ":")
                ),
                # An ingested item is visible to the principal and their EA and
                # nobody wider until something classifies it.
                "visibility": visibility or default_visibility(),
                # Default deny. The parties on the item are resolved to person
                # ids by the extractor, which is what sets shareable_with on
                # the records derived from it.
                "shareable_with": [],
                "provenance": "verbatim",
                "produced_by": produced_by,
            },
        )
        report.persisted += 1
        report.event_ids.append(event_id)

    return report


def unprocessed_events(
    conn: sqlite3.Connection, tenant_id: str, adapters: Iterable[str] | None = None
) -> list[dict[str, Any]]:
    """Ingest events that have not yet produced a curator proposal."""
    clause = ""
    params: list[Any] = [tenant_id]
    if adapters:
        names = list(adapters)
        clause = f" AND adapter IN ({', '.join('?' for _ in names)})"
        params.extend(names)

    rows = conn.execute(
        f"""
        SELECT e.*
        FROM ingest_event e
        WHERE e.tenant_id = ?{clause}
          AND NOT EXISTS (
              SELECT 1 FROM curator_proposal p
              WHERE p.tenant_id = e.tenant_id AND p.source_ref = e.id
          )
        ORDER BY e.occurred_at IS NULL, e.occurred_at, e.created_at
        """,
        params,
    ).fetchall()
    return [dict(row) for row in rows]
