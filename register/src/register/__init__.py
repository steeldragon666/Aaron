"""The commitment register and the Action Request ledger.

Sprint 1, tenant zero only. See ``docs/BUILD_BRIEF_SPRINT_1.md`` for scope and
``docs/ACTION_TIER_AND_REGISTER_SPEC.md`` for the specification this implements.

Nothing in this package sends anything, and nothing in it calls out to a
network. The send path and the action tiers are Sprint 2.
"""

from __future__ import annotations

from .db import migrate, open_register
from .errors import (
    AccessDenied,
    ChainBroken,
    CrossContextViolation,
    GapSuppressed,
    InvariantError,
    LedgerError,
    ModelBoundaryError,
    NoPredictionError,
    OpenARLimitError,
    ProvenanceError,
    RegisterError,
)

__all__ = [
    "AccessDenied",
    "ChainBroken",
    "CrossContextViolation",
    "GapSuppressed",
    "InvariantError",
    "LedgerError",
    "ModelBoundaryError",
    "NoPredictionError",
    "OpenARLimitError",
    "ProvenanceError",
    "RegisterError",
    "migrate",
    "open_register",
]

__version__ = "0.1.0"
