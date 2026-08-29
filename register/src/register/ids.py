"""Record identifiers.

Prefixed ULID-ish ids: sortable by creation time, prefixed so that an id in a
log line says what it is without a lookup. Generated locally — no external
service, per CLAUDE.md §2.
"""

from __future__ import annotations

import os
import time

_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"  # Crockford base32, no I/L/O/U

PREFIXES = {
    "tenant": "tn",
    "person": "pe",
    "meeting": "mt",
    "thread": "th",
    "commitment": "cm",
    "decision": "dc",
    "exposure": "ex",
    "prediction": "pr",
    "curator_proposal": "cq",
    "ingest_event": "ie",
    "ar": "ar",
}


def _encode(value: int, length: int) -> str:
    out = []
    for _ in range(length):
        value, rem = divmod(value, 32)
        out.append(_ALPHABET[rem])
    return "".join(reversed(out))


def new_id(kind: str) -> str:
    """Return a new sortable id for ``kind``."""
    try:
        prefix = PREFIXES[kind]
    except KeyError as exc:  # pragma: no cover - programmer error
        raise KeyError(f"no id prefix registered for {kind!r}") from exc
    millis = int(time.time() * 1000)
    randomness = int.from_bytes(os.urandom(10), "big")
    return f"{prefix}_{_encode(millis, 10)}{_encode(randomness, 16)}"
