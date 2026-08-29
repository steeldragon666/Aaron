"""Canonical JSON and hashing.

The ledger's hash chain is only as good as the determinism of the bytes it
hashes. Everything that goes into a hash goes through :func:`canonical_json`
first: sorted keys, no insignificant whitespace, UTF-8, no NaN.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

GENESIS_HASH = "0" * 64


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def chain_hash(seq: int, prev_hash: str, payload_json: str) -> str:
    """Hash one ledger link.

    ``seq`` is inside the hash so that reordering entries breaks the chain even
    if every payload is untouched.
    """
    return sha256_hex(f"{seq}\n{prev_hash}\n{payload_json}")
