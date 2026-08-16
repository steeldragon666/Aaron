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

**What this module is, and what it is not.**

It is a *labelling* check. ``produced_by`` is a caller-supplied string at every
write site, so this catches an honest mistake — a call site that names a
code-only model for an asserting artifact — and it cannot stop a caller that
labels DeepSeek output ``glm-5.2``. An independent reviewer made the point
directly, and it is right: no amount of matching makes a caller-controlled
string trustworthy, and the unicode-confusable and separator-variant evasions
are symptoms rather than the disease.

That is stated here rather than fixed here because the fix does not exist yet.
CLAUDE.md §6 says *enforce at the routing layer*, and there is no routing layer
— no router, no agent, no authenticated producer, nothing that could supply an
execution identity for this to check against. Building an identity system for a
single caller would be inventing the shape of Sprint 2's router by guessing at
it.

**The requirement this places on the router, when it lands (D-17):** capability
must be derived from *which engine actually ran*, established by the routing
layer itself and not passed in as an argument. ``produced_by`` stays as
provenance metadata on the record — it is genuinely useful for that, and CLAUDE
.md requires it — but it must stop being the thing that decides. Until then,
treat a passing :func:`assert_may_produce` as "no call site is obviously
mislabelled", never as "a code-only model did not write this".
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
    """Raise unless ``produced_by`` *claims* to be permitted to generate ``artifact``.

    A labelling check, not a boundary — see the module docstring. It rejects a
    call site that names a code-only model for an asserting artifact. It cannot
    reject a caller that names a permitted one, because the name is the only
    evidence it has.
    """
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
