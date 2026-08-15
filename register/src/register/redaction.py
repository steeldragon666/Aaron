"""Redaction at ingest — CLAUDE.md §3.

Client material passes through logs, KV cache, transcripts, backups and the
register. The privacy claim has to be true at the log layer, not only at the
perimeter, so redaction runs *before* anything is persisted rather than on the
way out.

Assume any string that reaches a log is recoverable by anyone with host access.
This module is what makes that assumption survivable.

Scope note: this catches credentials and secrets. It is deliberately not a PII
scrubber — the register's whole job is to hold who said what to whom, and
redacting names would empty it. Personal information is protected by
``visibility`` and ``shareable_with``, not by redaction.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

PLACEHOLDER = "[REDACTED:{label}]"


@dataclass(frozen=True)
class Rule:
    label: str
    pattern: re.Pattern[str]


# Ordered: the more specific patterns run first so a private key block is not
# partially eaten by the generic high-entropy rule.
RULES: tuple[Rule, ...] = (
    Rule(
        "private_key",
        re.compile(
            r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
            re.DOTALL,
        ),
    ),
    Rule("aws_access_key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    Rule("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    Rule("slack_token", re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}\b")),
    Rule("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    Rule("openai_style_key", re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}\b")),
    Rule("jwt", re.compile(r"\beyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\b")),
    Rule(
        "basic_auth_url",
        re.compile(r"\b([a-z][a-z0-9+.\-]*://)[^\s/:@]+:[^\s/@]+@"),
    ),
    # ``is`` is accepted as a separator alongside ``:`` and ``=`` because
    # "the staging password is hunter2" is how a credential actually arrives in
    # an email, and a rule that only catches the machine-shaped form catches the
    # form that was least likely to leak. It over-fires on "the password is
    # wrong", which costs a placeholder in a log line and nothing else.
    Rule(
        "labelled_secret",
        re.compile(
            r"(?i)\b(?:password|passwd|passphrase|secret|api[_\- ]?key|access[_\- ]?token"
            r"|client[_\- ]?secret|bearer)\b\s*(?:[:=]|\bis\b)\s*\"?[^\s\"',;]{6,}\"?"
        ),
    ),
    Rule(
        "card_number",
        re.compile(r"\b(?:\d[ \-]?){13,19}\b"),
    ),
)


@dataclass(frozen=True)
class RedactionResult:
    text: str
    count: int
    labels: tuple[str, ...]

    @property
    def clean(self) -> bool:
        return self.count == 0


def _luhn_ok(digits: str) -> bool:
    total = 0
    for index, char in enumerate(reversed(digits)):
        digit = int(char)
        if index % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def redact(text: str | None) -> RedactionResult:
    """Return ``text`` with secrets replaced by labelled placeholders."""
    if not text:
        return RedactionResult(text or "", 0, ())

    labels: list[str] = []
    result = text

    for rule in RULES:

        def _replace(match: re.Match[str], label: str = rule.label) -> str:
            if label == "card_number":
                digits = re.sub(r"\D", "", match.group(0))
                # Long digit runs are usually reference numbers, not cards.
                # Only redact when the run actually checksums as a card.
                if not (13 <= len(digits) <= 19 and _luhn_ok(digits)):
                    return match.group(0)
            if label == "basic_auth_url":
                labels.append(label)
                return f"{match.group(1)}[REDACTED:credentials]@"
            labels.append(label)
            return PLACEHOLDER.format(label=label)

        result = rule.pattern.sub(_replace, result)

    return RedactionResult(result, len(labels), tuple(labels))


def assert_no_secrets(text: str | None, where: str) -> None:
    """Fail loudly if ``text`` still carries a secret.

    Called on the write path for the register, the ledger and any log line, so
    that a rule gap surfaces as an exception during development rather than as
    a plaintext credential in a backup two months later.
    """
    outcome = redact(text)
    if not outcome.clean:
        raise ValueError(
            f"{where}: refusing to persist text containing {', '.join(sorted(set(outcome.labels)))}"
        )
