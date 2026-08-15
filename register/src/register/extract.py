"""Commitment extraction — deterministic, rule-based.

This extractor is rules, not a model, and that is a deliberate Sprint 1 choice
rather than a placeholder for one. Two reasons:

1. The register has to be *measurable* before it can be improved. A rule set
   has a fixed, inspectable recall; when coverage comes out at 62% you can read
   the rules and see which phrasing was missed. A model's miss is a shrug.
2. GLM-5.2 is not standing up yet, and building the extraction interface
   against a model that is not there would mean building it twice.

The interface is the part that matters: an extractor takes an ingest event and
returns :class:`Candidate` values, and the curator queue takes candidates. A
model-backed extractor is a swap of this module, not a schema change.

Everything this produces is a *proposal*. Commitments extracted from
conversational sources are never records until they are confirmed —
ACTION_TIER §4, write governance.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any

EXTRACTOR_ID = "rules:commitment-extractor@1"

# --- sentence splitting -----------------------------------------------------

_SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")

# Quoted-reply and signature boundaries. Text below one of these belongs to an
# earlier message and must not be re-extracted, or every reply in a thread
# proposes the same commitment again.
_QUOTE_BOUNDARY = re.compile(
    r"^(?:>|On .{0,80}\bwrote:|-{2,}\s*Original Message|From:\s|Sent from my )",
    re.MULTILINE,
)


def sentences(text: str) -> list[str]:
    body = _QUOTE_BOUNDARY.split(text, maxsplit=1)[0] if text else ""
    return [s.strip() for s in _SENTENCE.split(body) if s.strip()]


# --- commitment patterns ----------------------------------------------------


@dataclass(frozen=True)
class Pattern:
    name: str
    regex: re.Pattern[str]
    # Who ends up owing the thing, given who is speaking.
    speaker_owes: bool
    base_confidence: float


PROMISE_PATTERNS: tuple[Pattern, ...] = (
    Pattern(
        "first_person_will",
        re.compile(r"\b(?:I|we)\s*(?:'ll|\s+will|\s+shall)\b", re.IGNORECASE),
        speaker_owes=True,
        base_confidence=0.80,
    ),
    Pattern(
        "first_person_going_to",
        re.compile(r"\b(?:I|we)\s*(?:'m|\s+am|\s+are|'re)\s+going\s+to\b", re.IGNORECASE),
        speaker_owes=True,
        base_confidence=0.75,
    ),
    Pattern(
        "first_person_undertaking",
        re.compile(
            r"\b(?:I|we)\s+(?:can|'ll\s+try\s+to)?\s*(?:send|get|revert|come\s+back|follow\s+up|"
            r"circulate|share|draft|confirm|forward|write|deliver|provide)\b",
            re.IGNORECASE,
        ),
        speaker_owes=True,
        base_confidence=0.65,
    ),
    Pattern(
        "let_me",
        re.compile(
            r"\blet\s+me\s+(?:send|get|check|confirm|come\s+back|dig|pull)\b", re.IGNORECASE
        ),
        speaker_owes=True,
        base_confidence=0.65,
    ),
    Pattern(
        "request_of_other",
        re.compile(
            r"\b(?:could|can|would)\s+you\b.*?\b(?:send|share|confirm|forward|provide|get|let\s+me\s+know)\b",
            re.IGNORECASE | re.DOTALL,
        ),
        speaker_owes=False,
        base_confidence=0.55,
    ),
    Pattern(
        "please_do",
        re.compile(
            r"\bplease\s+(?:send|share|confirm|forward|provide|review|sign)\b", re.IGNORECASE
        ),
        speaker_owes=False,
        base_confidence=0.55,
    ),
)

# Hedges drop confidence rather than blocking extraction: a hedged commitment is
# still worth surfacing, it just should not auto-confirm.
_HEDGES = re.compile(
    r"\b(?:maybe|might|possibly|if\s+I\s+(?:can|get)|hopefully|try\s+to|no\s+promises|"
    r"probably|at\s+some\s+point|in\s+due\s+course)\b",
    re.IGNORECASE,
)

# Negations that mean the opposite of a commitment.
_NEGATIONS = re.compile(
    r"\b(?:I|we)\s*(?:won'?t|will\s+not|can'?t|cannot|am\s+not\s+able\s+to)\b", re.IGNORECASE
)


# --- due dates --------------------------------------------------------------

_WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

_MONTHS = {
    m: i + 1
    for i, m in enumerate(
        [
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
        ]
    )
}

_ISO_DATE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
_DAY_MONTH = re.compile(
    r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(" + "|".join(_MONTHS) + r")\b", re.IGNORECASE
)
_MONTH_DAY = re.compile(
    r"\b(" + "|".join(_MONTHS) + r")\s+(\d{1,2})(?:st|nd|rd|th)?\b", re.IGNORECASE
)
_BY_WEEKDAY = re.compile(
    r"\b(?:by|before|on|this|next)\s+(" + "|".join(_WEEKDAYS) + r")\b", re.IGNORECASE
)
_TOMORROW = re.compile(r"\btomorrow\b", re.IGNORECASE)
_END_OF_WEEK = re.compile(r"\b(?:end\s+of\s+(?:the\s+)?week|EOW)\b", re.IGNORECASE)
_END_OF_MONTH = re.compile(r"\b(?:end\s+of\s+(?:the\s+)?month|EOM)\b", re.IGNORECASE)
_NEXT_WEEK = re.compile(r"\bnext\s+week\b", re.IGNORECASE)


def parse_due(text: str, reference: date) -> str | None:
    """Best-effort due date, or ``None``.

    Returning ``None`` is the correct answer far more often than a guess is. A
    wrong due date turns into a chase on the wrong day, which costs the
    principal more than the missing date does.
    """
    match = _ISO_DATE.search(text)
    if match:
        try:
            return date(int(match[1]), int(match[2]), int(match[3])).isoformat()
        except ValueError:
            return None

    match = _DAY_MONTH.search(text)
    if match:
        return _with_year(int(match[1]), _MONTHS[match[2].lower()], reference)

    match = _MONTH_DAY.search(text)
    if match:
        return _with_year(int(match[2]), _MONTHS[match[1].lower()], reference)

    if _TOMORROW.search(text):
        return (reference + timedelta(days=1)).isoformat()

    match = _BY_WEEKDAY.search(text)
    if match:
        target = _WEEKDAYS[match[1].lower()]
        ahead = (target - reference.weekday()) % 7
        ahead = ahead or 7  # "by Monday" said on a Monday means the next one
        return (reference + timedelta(days=ahead)).isoformat()

    if _END_OF_WEEK.search(text):
        return (reference + timedelta(days=(4 - reference.weekday()) % 7)).isoformat()

    if _NEXT_WEEK.search(text):
        return (reference + timedelta(days=(7 - reference.weekday()) + 4)).isoformat()

    if _END_OF_MONTH.search(text):
        if reference.month == 12:
            return date(reference.year, 12, 31).isoformat()
        return (date(reference.year, reference.month + 1, 1) - timedelta(days=1)).isoformat()

    return None


def _with_year(day: int, month: int, reference: date) -> str | None:
    for year in (reference.year, reference.year + 1):
        try:
            candidate = date(year, month, day)
        except ValueError:
            return None
        if candidate >= reference - timedelta(days=180):
            return candidate.isoformat()
    return None


# --- candidates -------------------------------------------------------------


@dataclass(frozen=True)
class Candidate:
    """A proposed commitment. Not a record until confirmed."""

    statement: str
    direction: str
    confidence: float
    pattern: str
    counterparty_email: str | None
    due: str | None
    made_at: str
    source_type: str
    provenance: str = "verbatim"
    shareable_with_emails: Sequence[str] = field(default_factory=tuple)
    notes: Mapping[str, Any] = field(default_factory=dict)


def extract_from_event(
    event: Mapping[str, Any],
    *,
    principal_emails: Sequence[str],
    sender: str | None = None,
    participants: Sequence[str] = (),
    reference: date | None = None,
) -> list[Candidate]:
    """Pull commitment candidates out of one ingest event.

    ``sender`` decides direction. Without it, direction cannot be established
    from the text alone, and the extractor returns nothing rather than guessing
    — a commitment filed in the wrong direction produces a chase aimed at the
    wrong person, which is worse than a missed one.
    """
    if not sender:
        return []

    principals = {e.lower() for e in principal_emails}
    sender = sender.lower()
    sender_is_principal = sender in principals

    others = sorted({p.lower() for p in participants} - principals - {sender})
    counterparty = sender if not sender_is_principal else (others[0] if others else None)

    occurred = event.get("occurred_at")
    made_at = str(occurred) if occurred else datetime.now().isoformat(timespec="seconds")
    ref = reference or _reference_date(made_at)

    text = "\n".join(filter(None, [str(event.get("summary") or ""), str(event.get("body") or "")]))
    source_type = (
        "email" if event.get("adapter") == "mailbox" else str(event.get("adapter") or "manual")
    )
    if source_type == "calendar":
        # A calendar entry is a source of truth about the meeting, not about
        # what anyone promised in it.
        return []

    out: list[Candidate] = []
    for sentence in sentences(text):
        if _NEGATIONS.search(sentence):
            continue
        for pattern in PROMISE_PATTERNS:
            if not pattern.regex.search(sentence):
                continue

            owed_by_sender = pattern.speaker_owes
            owes_principal = owed_by_sender == sender_is_principal
            direction = "by_principal" if owes_principal else "to_principal"

            confidence = pattern.base_confidence
            due = parse_due(sentence, ref)
            if due:
                confidence += 0.10
            if _HEDGES.search(sentence):
                confidence -= 0.25
            if len(sentence) > 400:
                # A commitment buried in a wall of text is more likely a false
                # positive on a stray phrase.
                confidence -= 0.10
            confidence = round(max(0.05, min(0.99, confidence)), 2)

            out.append(
                Candidate(
                    statement=sentence,
                    direction=direction,
                    confidence=confidence,
                    pattern=pattern.name,
                    counterparty_email=counterparty,
                    due=due,
                    made_at=made_at,
                    source_type=source_type,
                    provenance="verbatim",
                    # The parties present on the source item, principal
                    # included — consistent with how create_meeting defaults to
                    # its attendees. Nobody who was not on the item.
                    shareable_with_emails=tuple(
                        sorted({sender, *(p.lower() for p in participants)})
                    ),
                    notes={"sender": sender, "sender_is_principal": sender_is_principal},
                )
            )
            break  # one candidate per sentence, strongest pattern first

    return out


def _reference_date(made_at: str) -> date:
    try:
        return datetime.fromisoformat(made_at).date()
    except ValueError:
        return datetime.now().date()
