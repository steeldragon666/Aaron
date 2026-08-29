"""Error types.

Each of these corresponds to a constraint in CLAUDE.md that is enforced in
code rather than in a prompt. Where a caller catches one of these, it is
catching a guardrail firing — log it, do not swallow it.
"""

from __future__ import annotations


class RegisterError(Exception):
    """Base for everything raised by this package."""


class InvariantError(RegisterError):
    """A record was written without the full invariant field set (CLAUDE.md §1)."""


class AccessDenied(RegisterError):
    """A read was refused by visibility or by the cross-context rule (§4)."""


class CrossContextViolation(AccessDenied):
    """A fact was requested in a counterparty context it is not shareable with.

    Separate from :class:`AccessDenied` because this is the failure that loses a
    client, and it should be greppable in the logs on its own.
    """


class LedgerError(RegisterError):
    """The AR ledger rejected an append, or failed verification."""


class NoPredictionError(LedgerError):
    """No prediction, no AR. Observations go to an appendix."""


class OpenARLimitError(LedgerError):
    """Hard cap of five open ARs per agent."""


class ChainBroken(LedgerError):
    """Hash chain verification failed — a link does not match its payload."""


class ModelBoundaryError(RegisterError):
    """A code-only model tried to produce a claim about the world (CLAUDE.md §6)."""


class GapSuppressed(RegisterError):
    """Auto-action refused because the affected period has a gap_flag."""


class ProvenanceError(RegisterError):
    """An inferred record was pushed down an actionable path without confirmation."""
