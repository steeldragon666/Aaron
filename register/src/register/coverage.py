"""Coverage measurement.

Acceptance criterion 2 of Sprint 1: **coverage ≥80%** measured against a
manually compiled list of known commitments — the same gate Phase 0 sells to a
client, so the tool that measures it is a deliverable and not a test fixture.

The manual list is the ground truth. It is compiled by a human who knows what
they promised, and the register is scored against it. The number that comes out
of here is the day-7 artifact.

Matching is intentionally conservative: a register entry counts as covering a
known commitment only when the statement, the counterparty and the direction
all line up. A generous matcher would produce a coverage figure that looks good
and means nothing, and the whole point of the number is that a client can
falsify it by naming what is missing.
"""

from __future__ import annotations

import json
import re
import sqlite3
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_WORD = re.compile(r"[a-z0-9]+")
_STOPWORDS = frozenset(
    [
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "been",
        "by",
        "for",
        "from",
        "has",
        "have",
        "i",
        "if",
        "in",
        "is",
        "it",
        "its",
        "me",
        "my",
        "of",
        "on",
        "or",
        "our",
        "that",
        "the",
        "their",
        "them",
        "they",
        "this",
        "to",
        "was",
        "we",
        "will",
        "with",
        "you",
        "your",
        "ll",
        "re",
    ]
)


def _stem(word: str) -> str:
    """Trim a plural or third-person ``s``, and nothing else.

    The manual list is written by a human describing a commitment ("Ruth sends
    the figures") while the register holds the words used ("I'll send the
    figures by Friday"). That one inflection is enough to push a real match
    under the threshold. Anything more aggressive than this starts collapsing
    words that mean different things, which is the opposite of the failure
    worth avoiding here.
    """
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def _tokens(text: str) -> set[str]:
    """Content words only.

    Pure digits are dropped: a date written into a statement ("by 2026-08-14")
    contributes tokens that identify nothing — the due date has its own field
    and is not what makes two descriptions of the same promise the same promise.
    Left in, they dilute the overlap and sink real matches.
    """
    return {
        _stem(w)
        for w in _WORD.findall(text.lower())
        if w not in _STOPWORDS and len(w) > 2 and not w.isdigit()
    }


def similarity(left: str, right: str) -> float:
    """Jaccard overlap on stemmed content words. Cheap, deterministic, explainable."""
    a, b = _tokens(left), _tokens(right)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


@dataclass(frozen=True)
class KnownCommitment:
    """One entry from the manually compiled list."""

    statement: str
    direction: str
    counterparty: str | None = None
    due: str | None = None
    note: str = ""

    @staticmethod
    def from_dict(raw: dict[str, Any]) -> KnownCommitment:
        missing = {"statement", "direction"} - set(raw)
        if missing:
            raise ValueError(f"known commitment missing {', '.join(sorted(missing))}: {raw}")
        return KnownCommitment(
            statement=str(raw["statement"]),
            direction=str(raw["direction"]),
            counterparty=(str(raw["counterparty"]).lower() if raw.get("counterparty") else None),
            due=raw.get("due"),
            note=str(raw.get("note", "")),
        )


def load_known(path: str | Path) -> list[KnownCommitment]:
    """Load the manual list. JSON — one array of objects."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("the manual commitment list must be a JSON array")
    return [KnownCommitment.from_dict(item) for item in raw]


@dataclass
class Match:
    known: KnownCommitment
    commitment_id: str | None
    score: float
    reason: str


@dataclass
class CoverageReport:
    total_known: int = 0
    matched: int = 0
    matches: list[Match] = field(default_factory=list)
    unmatched: list[Match] = field(default_factory=list)
    register_size: int = 0
    threshold: float = 0.34

    @property
    def coverage(self) -> float:
        if not self.total_known:
            return 0.0
        return self.matched / self.total_known

    @property
    def passes(self) -> bool:
        return self.coverage >= 0.80

    def render(self) -> str:
        lines = [
            "Coverage against the manually compiled list",
            "-" * 44,
            f"known commitments : {self.total_known}",
            f"found in register : {self.matched}",
            f"register entries  : {self.register_size}",
            f"coverage          : {self.coverage:.1%}  "
            f"({'PASS' if self.passes else 'BELOW THE 80% GATE'})",
        ]
        if self.unmatched:
            lines += ["", "Not found — this is the list to hand the principal:"]
            for miss in self.unmatched:
                who = f" [{miss.known.counterparty}]" if miss.known.counterparty else ""
                lines.append(f"  · ({miss.known.direction}){who} {miss.known.statement}")
        return "\n".join(lines)


def _counterparty_labels(conn: sqlite3.Connection, tenant_id: str) -> dict[str, set[str]]:
    """Map person id to the strings a human might have used to name them."""
    out: dict[str, set[str]] = {}
    for row in conn.execute(
        "SELECT id, display_name, email FROM person WHERE tenant_id = ?", (tenant_id,)
    ):
        labels = {str(row["display_name"]).lower()}
        if row["email"]:
            email = str(row["email"]).lower()
            labels.add(email)
            labels.add(email.split("@")[0])
        out[str(row["id"])] = labels
    return out


def measure(
    conn: sqlite3.Connection,
    tenant_id: str,
    known: Sequence[KnownCommitment],
    *,
    threshold: float = 0.34,
    statuses: Iterable[str] = ("open", "met", "missed", "superseded"),
) -> CoverageReport:
    """Score the register against the manual list."""
    status_list = list(statuses)
    rows = conn.execute(
        f"""
        SELECT id, statement, direction, counterparty_id, due, status
        FROM commitment
        WHERE tenant_id = ? AND status IN ({", ".join("?" for _ in status_list)})
        """,
        (tenant_id, *status_list),
    ).fetchall()
    entries = [dict(row) for row in rows]
    labels = _counterparty_labels(conn, tenant_id)

    report = CoverageReport(total_known=len(known), register_size=len(entries), threshold=threshold)
    claimed: set[str] = set()

    for item in known:
        best: tuple[float, dict[str, Any] | None] = (0.0, None)
        for candidate in entries:
            if candidate["id"] in claimed:
                continue
            if candidate["direction"] != item.direction:
                continue
            if item.counterparty:
                entry_labels = labels.get(str(candidate["counterparty_id"]), set())
                if not any(
                    item.counterparty in label or label in item.counterparty
                    for label in entry_labels
                ):
                    continue
            score = similarity(item.statement, str(candidate["statement"]))
            if score > best[0]:
                best = (score, candidate)

        score, entry = best
        if entry is not None and score >= threshold:
            claimed.add(str(entry["id"]))
            match = Match(item, str(entry["id"]), score, "matched")
            report.matches.append(match)
            report.matched += 1
        else:
            reason = "no register entry with this direction and counterparty"
            if entry is not None:
                reason = f"closest entry scored {score:.2f}, below the {threshold:.2f} threshold"
            report.unmatched.append(Match(item, None, score, reason))

    return report
