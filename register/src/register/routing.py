"""The model boundary — CLAUDE.md §6.

    Where DeepSeek V4 Pro is used, it may generate code, tests, migrations,
    configs and build artifacts that are verified by execution. It must never
    generate an Action Request, an evidence block, a claim about the world, a
    prediction, or client-facing prose.

Routing itself (NeMo Switchyard, D-17) is out of scope for Sprint 1, and
deliberately so: introducing a router before a single prediction has been
scored means that when an AR turns out wrong you cannot tell whether the model
was wrong or the router picked the wrong model.

What is in scope now is the boundary, because ``produced_by`` is being written
from this sprint onward. Encoding the rule here means the check exists before
the router does, rather than being a convention someone remembers to add.
"""

from __future__ import annotations

import re

from .errors import ModelBoundaryError

# Models permitted to generate code and build artifacts only. Matched against
# ``produced_by`` case-insensitively as a substring, because model identifiers
# arrive with version suffixes and serving-stack prefixes.
CODE_ONLY_MODELS: tuple[str, ...] = ("deepseek",)

# Artifact kinds that assert something about the world. A code-only model that
# produces one of these is asserting rather than generating-and-verifying, and
# its hallucination rate becomes live inside the artifact the business is
# scored on.
ASSERTING_ARTIFACTS: frozenset[str] = frozenset(
    {
        "action_request",
        "evidence",
        "claim",
        "prediction",
        "client_prose",
        "register_record",
    }
)

VERIFIABLE_ARTIFACTS: frozenset[str] = frozenset(
    {"code", "test", "migration", "config", "build_artifact"}
)

_HUMAN = re.compile(r"^human:", re.IGNORECASE)
_RULES = re.compile(r"^rules:", re.IGNORECASE)


def is_code_only(produced_by: str) -> bool:
    lowered = produced_by.lower()
    return any(marker in lowered for marker in CODE_ONLY_MODELS)


def assert_may_produce(produced_by: str, artifact: str) -> None:
    """Raise unless ``produced_by`` is permitted to generate ``artifact``."""
    if not produced_by:
        raise ModelBoundaryError("produced_by is required on every artifact")
    if artifact not in ASSERTING_ARTIFACTS | VERIFIABLE_ARTIFACTS:
        raise ValueError(f"unknown artifact kind {artifact!r}")

    if artifact in VERIFIABLE_ARTIFACTS:
        return

    # Order matters here, and it used to be the other way round.
    #
    # `produced_by` is caller-supplied free text at every call site. When the
    # `human:` / `rules:` escape ran first, `human:deepseek-v4-pro` and
    # `rules:deepseek-extractor@1` both returned early and a code-only model
    # could write an Action Request, a prediction or a claim about the world.
    # A prefix is a label anyone can type, so it cannot be the thing that
    # decides. Establish that the identifier does not name a code-only model
    # first; only then does the provenance class get to speak.
    if is_code_only(produced_by):
        raise ModelBoundaryError(
            f"{produced_by} may not produce {artifact!r}. It generates code, tests, "
            "migrations, configs and build artifacts verified by execution — never "
            "an Action Request, an evidence block, a claim about the world, a "
            "prediction, or client-facing prose (CLAUDE.md §6)."
        )

    # Humans and deterministic rule extractors may assert. The boundary is
    # about model capability, not provenance class, so this is an allow rather
    # than the gate — and it is now unreachable for a code-only identifier.
    if _HUMAN.match(produced_by) or _RULES.match(produced_by):
        return
