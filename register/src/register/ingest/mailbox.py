"""Mailbox adapter — read-only, local, continuous.

Reads a Maildir or an mbox from local disk. Both are what a mail sync drops on
an on-prem host, and neither requires this process to hold a credential or open
a socket. The provider connection itself (M365, Google Workspace) is an open
item; see :mod:`register.ingest`.

Read-only is structural, not a promise: :mod:`mailbox` is opened without write
access and nothing here calls a mutating method.
"""

from __future__ import annotations

import email.policy
import mailbox
from collections.abc import Iterator
from email.message import EmailMessage
from email.utils import getaddresses, parsedate_to_datetime
from pathlib import Path

from . import SourceItem

_POLICY = email.policy.default


def _addresses(message: EmailMessage, *headers: str) -> list[str]:
    raw: list[tuple[str, str]] = []
    for header in headers:
        values = message.get_all(header, [])
        raw.extend(getaddresses([str(v) for v in values]))
    return sorted({addr.lower() for _, addr in raw if addr})


def _plain_body(message: EmailMessage) -> str:
    try:
        part = message.get_body(preferencelist=("plain",))
    except Exception:  # pragma: no cover - malformed message
        part = None
    if part is None:
        return ""
    try:
        content = part.get_content()
    except Exception:  # pragma: no cover - undecodable payload
        return ""
    return content if isinstance(content, str) else ""


def _occurred_at(message: EmailMessage) -> str | None:
    raw = message.get("Date")
    if not raw:
        return None
    try:
        return parsedate_to_datetime(str(raw)).isoformat()
    except (TypeError, ValueError):
        return None


class MailboxAdapter:
    """Yields one :class:`SourceItem` per message.

    ``source_id`` is the RFC 5322 Message-ID where present, which makes re-runs
    idempotent across a resync. Messages without one fall back to a path-derived
    key, which is stable for Maildir and stable-enough for mbox.
    """

    name = "mailbox"

    def __init__(self, path: str | Path, *, limit: int | None = None) -> None:
        self.path = Path(path)
        self.limit = limit

    def _open(self) -> mailbox.Mailbox:
        if self.path.is_dir():
            return mailbox.Maildir(str(self.path), factory=None, create=False)
        return mailbox.mbox(str(self.path), factory=None, create=False)

    def read(self) -> Iterator[SourceItem]:
        box = self._open()
        try:
            for index, key in enumerate(box.keys()):
                if self.limit is not None and index >= self.limit:
                    break
                raw = box.get_bytes(key)
                message = email.message_from_bytes(raw, policy=_POLICY)
                assert isinstance(message, EmailMessage)

                message_id = str(message.get("Message-ID") or "").strip()
                source_id = message_id or f"{self.path.name}:{key}"
                subject = str(message.get("Subject") or "(no subject)")

                yield SourceItem(
                    source_id=source_id,
                    kind="email",
                    summary=subject,
                    body=_plain_body(message),
                    occurred_at=_occurred_at(message),
                    participants=_addresses(message, "From", "To", "Cc"),
                    metadata={
                        "from": _addresses(message, "From"),
                        "to": _addresses(message, "To", "Cc"),
                        "message_id": message_id,
                        "in_reply_to": str(message.get("In-Reply-To") or "") or None,
                        "thread_ref": str(message.get("References") or "").split()[:1],
                    },
                )
        finally:
            box.close()
