"""Manual entry — the EA and the principal, at any time.

Manual entries are a source of truth: a human typed them, so they write
directly rather than entering the curator queue. The adapter shape exists so
that manual entry shares the redaction and dedupe path with everything else
rather than getting a private back door into the register.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence

from . import SourceItem


class ManualAdapter:
    name = "manual"

    def __init__(self, items: Sequence[SourceItem]) -> None:
        self._items = list(items)

    def read(self) -> Iterator[SourceItem]:
        yield from self._items


def manual_item(
    *,
    source_id: str,
    summary: str,
    body: str = "",
    occurred_at: str | None = None,
    participants: Sequence[str] = (),
) -> SourceItem:
    return SourceItem(
        source_id=source_id,
        kind="manual",
        summary=summary,
        body=body,
        occurred_at=occurred_at,
        participants=tuple(participants),
    )
