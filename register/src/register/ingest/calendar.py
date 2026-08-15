"""Calendar adapter — read-only, local iCalendar files.

A minimal RFC 5545 reader, deliberately hand-rolled rather than taken from a
package: CLAUDE.md §2 rules out adding a dependency to a client-context path,
and the subset of iCalendar a calendar export actually uses is small.

Calendar entries are a *source of truth* in the write-governance sense
(ACTION_TIER §4): the meeting happened, the attendees are structured data, and
the record is re-derivable from the file. So calendar-derived meetings write
directly rather than entering the curator queue. Commitments *inferred from*
the existence of a meeting are a different thing entirely and still go through
the queue.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path

from . import SourceItem


def _unfold(text: str) -> list[str]:
    """Undo RFC 5545 line folding: a leading space or tab continues the line."""
    lines: list[str] = []
    for raw in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if raw[:1] in (" ", "\t") and lines:
            lines[-1] += raw[1:]
        else:
            lines.append(raw)
    return lines


def _unescape(value: str) -> str:
    return (
        value.replace("\\n", "\n")
        .replace("\\N", "\n")
        .replace("\\,", ",")
        .replace("\\;", ";")
        .replace("\\\\", "\\")
    )


def _split_property(line: str) -> tuple[str, dict[str, str], str]:
    name_part, _, value = line.partition(":")
    pieces = name_part.split(";")
    name = pieces[0].upper()
    params: dict[str, str] = {}
    for piece in pieces[1:]:
        key, _, val = piece.partition("=")
        params[key.upper()] = val.strip('"')
    return name, params, _unescape(value)


def _to_iso(value: str) -> str | None:
    """Convert an iCalendar date-time to ISO 8601, best effort.

    Handles ``YYYYMMDDTHHMMSSZ``, ``YYYYMMDDTHHMMSS`` and ``YYYYMMDD``. A value
    this cannot parse is returned as ``None`` rather than guessed at — a wrong
    date in the register is worse than an absent one.
    """
    value = value.strip()
    if len(value) == 8 and value.isdigit():
        return f"{value[0:4]}-{value[4:6]}-{value[6:8]}"
    if len(value) in (15, 16) and value[8:9] == "T":
        stem = f"{value[0:4]}-{value[4:6]}-{value[6:8]}T{value[9:11]}:{value[11:13]}:{value[13:15]}"
        return stem + ("+00:00" if value.endswith("Z") else "")
    return None


def parse_ics(text: str) -> Iterator[dict[str, object]]:
    """Yield one dict per VEVENT."""
    current: dict[str, object] | None = None
    for line in _unfold(text):
        if not line.strip():
            continue
        name, params, value = _split_property(line)

        if name == "BEGIN" and value == "VEVENT":
            current = {"attendees": [], "organizer": None}
            continue
        if name == "END" and value == "VEVENT":
            if current is not None:
                yield current
            current = None
            continue
        if current is None:
            continue

        if name == "UID":
            current["uid"] = value
        elif name == "SUMMARY":
            current["summary"] = value
        elif name == "DESCRIPTION":
            current["description"] = value
        elif name == "DTSTART":
            current["starts_at"] = _to_iso(value)
        elif name == "DTEND":
            current["ends_at"] = _to_iso(value)
        elif name == "ATTENDEE":
            address = value.split(":")[-1].strip().lower()
            if address:
                attendees = current["attendees"]
                assert isinstance(attendees, list)
                attendees.append(
                    {"email": address, "name": params.get("CN", ""), "role": params.get("ROLE", "")}
                )
        elif name == "ORGANIZER":
            current["organizer"] = value.split(":")[-1].strip().lower()

    if current is not None:  # pragma: no cover - unterminated VEVENT
        yield current


class CalendarAdapter:
    """Reads ``.ics`` files from a path — a single file or a directory of them."""

    name = "calendar"

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def _files(self) -> Iterable[Path]:
        if self.path.is_dir():
            return sorted(self.path.glob("*.ics"))
        return [self.path]

    def read(self) -> Iterator[SourceItem]:
        for file in self._files():
            text = file.read_text(encoding="utf-8", errors="replace")
            for event in parse_ics(text):
                uid = str(event.get("uid") or "")
                if not uid:
                    continue
                attendees = event.get("attendees") or []
                assert isinstance(attendees, list)
                emails = sorted(
                    {str(a["email"]) for a in attendees if isinstance(a, dict) and a.get("email")}
                )
                organizer = event.get("organizer")
                if isinstance(organizer, str) and organizer:
                    emails = sorted(set(emails) | {organizer})

                starts_at = event.get("starts_at")
                yield SourceItem(
                    source_id=uid,
                    kind="calendar",
                    summary=str(event.get("summary") or "(untitled)"),
                    body=str(event.get("description") or ""),
                    occurred_at=starts_at if isinstance(starts_at, str) else None,
                    participants=emails,
                    metadata={
                        "ends_at": event.get("ends_at"),
                        "organizer": organizer,
                        "attendees": attendees,
                    },
                )
