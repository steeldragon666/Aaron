# Subagent Base Model and Middleware — Specification

**Prepared:** 26 August 2026
**Records:** D-19 (subagent base model), D-20 (middleware reference architecture)
**Closes:** S-11 (which Qwen3.8 variant), and the vision gap raised at `CONSOLIDATION_BRIEF` §0 item 6
**Companion to:** `CONSOLIDATION_BRIEF.md` §0 (the resolved stack), `CLAUDE.md` §2 and §6

> **Nothing in this document is in Sprint 1 scope.** Sprint 1 is the commitment register and the
> hash-chained AR ledger, tenant zero, and nothing else (`BUILD_BRIEF_SPRINT_1.md`). This is the
> settled-stack record that Sprint 2 builds against. It changes no code today.

---

## D-19 · Subagent tier — five small dense models on a named base

**Decision.** The subagent tier is **five small dense models**, each finetuned from a single base
checkpoint:

**`junafinity/Qwen-3.8-27B-Uncensored`** — https://huggingface.co/junafinity/Qwen-3.8-27B-Uncensored

This replaces "Qwen3.8 (variant TBC)" in the `CONSOLIDATION_BRIEF` §0 stack table and answers S-11.

### What the checkpoint actually is

Verified against the Hugging Face model card, 26 August 2026:

| Property | Value | Why it matters here |
|---|---|---|
| Parameters | **27.78B** | Dense, not MoE — every parameter is resident and active. Sizing is straightforward; there is no active-parameter discount. |
| Architecture | `qwen3_5`, `AutoModelForMultimodalLM` | — |
| Task | **`image-text-to-text`** | **It has a vision head.** This is the mitigation §0 item 6 asked for and the "pick a variant with a vision head" instruction in S-11. |
| Base model | `Qwen/Qwen3.8-27B`, finetuned | Upstream is the stock Qwen release, not an unknown lineage. |
| Licence | **Apache-2.0** | Clean for multi-tenant commercial deployment. No modified-MIT clause set to read, unlike the K3 problem in §0. |
| Tags | `abliterated`, `uncensored`, `zerofuse` | See the abstention caveat below — this is the one that needs work before committing. |
| Downloads / likes | 361 / 2 | A low-traffic community checkpoint. Treat it as unproven until it passes our own evals; it carries no external validation. |

**Two things this closes at once.** It gives the subagent tier a named, licence-clean checkpoint,
and it closes the vision gap in a text-only reasoning stack without adding a sixth model to serve.
Amara's Figma frames, Hugh's scanned invoices and Bram's dashboards all convert to structured text
through the same model that does the subagent work.

### Sizing against the farm

Farm: **8 × CMP 170HX**. Using the build spec's own figures — 512 GB host RAM sized to match VRAM
1:1, and a **GLM-5.2 W4A16 quant of 388 GB** (`170HX_BUILD_SPEC.md`) — the reasoning model leaves
roughly **124 GB** of VRAM for everything else.

| Configuration | Weights (5 models) | Co-resident with GLM-5.2? |
|---|---|---|
| bf16 | ~278 GB | **No** — does not fit at all |
| W8A8 | ~139 GB | **No** — overruns the remainder |
| W4A16 | ~70–85 GB with activations | **Yes, but tight** — before KV cache, video and TTS |
| 1 base W8A8 + 5 LoRA adapters | ~30 GB | **Comfortably** |

**Consequence to decide, not assumed:** five *separately finetuned full-weight* models and
"one shared base + five adapters" are different decisions with a ~4× VRAM difference between them,
and D-13 already recommended the second (GLM reasons, a small per-persona LoRA does the voice pass).
Five full finetunes are viable only at 4-bit and only if the five are not all resident at once —
which is compatible with the Q8 compute window (2am–6am for the eight-card block, a small resident
model on 1–2 cards during business hours) but not with five agents answering concurrently in the
2–5 minute response target. **Recorded as S-15.**

### Constraint checks

- **§2, no external calls.** Weights are downloaded once, at build time, and served on the farm.
  The model card lists a `featherless-ai` inference provider: **that path must never be used.**
  It is a hosted API and would breach the zero-external-dependency claim on a client-context path.
  Pull weights, pin the revision hash, serve locally.
- **§6, model boundary.** These five are subagents, not verifiable-artifact generators. The
  DeepSeek V4 boundary is unaffected. What *does* change is §6's enforcement point — see D-20.
- **Provenance.** Pin the exact commit SHA of the checkpoint in the serving config. A community
  repo can be updated or withdrawn; `produced_by` is meaningless if the weights behind a label moved.

### The caveat that matters: abliteration versus abstention

`CONSOLIDATION_BRIEF` §0 item 5 sets the rule for the reasoning model: **run an abstention eval,
not a capability eval** — the ten questions where the correct answer is "insufficient data", and the
five that must trigger the tax-agent referral. DeepSeek V4 Pro was ruled out on exactly this ground.

That rule applies with more force to an abliterated model, not less. Abliteration works by removing
the direction in activation space along which the model refuses. **"I don't have enough data to
answer that" is a refusal.** The technique is aimed at the same behaviour this system depends on:
Hugh's insufficient-data answer, Bram's *measured / specified / assumed*, Elena's `[UNSUBSTANTIATED]`
tag. There is a real possibility that the property being removed for convenience is the property
being sold.

**Gate, before any of the five is finetuned:** run the base checkpoint through the same abstention
eval specified for GLM-5.2, and run stock `Qwen/Qwen3.8-27B` through it as a control. If the
abliterated model abstains materially less often than its own base, the uncensored variant is the
wrong starting point for this product and the stock model should be finetuned instead. This is a
one-afternoon test and it is cheaper than discovering the answer through a poisoned AR ledger.

---

## D-20 · Middleware — build against the published Claude Code harness architecture

**Decision.** The agent middleware — the layer between the register and the models — is built to the
twelve-layer architecture described in
["The Leaked Claude Code 1.2 Harness"](https://eli5defi.substack.com/p/the-leaked-claude-code-12-harness),
rather than being invented from scratch.

**Provenance, stated plainly.** The article is a **descriptive write-up: it publishes no source
code.** What we take from it is an architecture — a component list and how the parts relate. That
is the right thing to take. **Do not ingest, vendor or transcribe leaked proprietary source into
this repository**, whatever surfaces later; the implementation is ours. This distinction is the
whole of the licensing position and it should survive any future temptation.

### The twelve layers, mapped to this system

Layer names are the article's; the mapping and the verdicts are ours.

| # | Layer | Relevance here | Status |
|---|---|---|---|
| 1 | Streaming | Token-by-token to the console; matters for the 2–5 min response target feeling responsive. | Sprint 2 |
| 2 | Retry logic | Local vLLM calls fail differently to network APIs — retry on OOM and queue timeouts, not HTTP. | Sprint 2 |
| 3 | Error handling | Route failure classes: model error vs tool error vs **invariant refusal**. An `InvariantError` must never be retried into success. | Sprint 2 |
| 4 | Context assembly | Directly serves §0 item 4: the register sits **in context**, not retrieved. This layer is where that ordering is decided. | Sprint 2 |
| 5 | Tool registration (`buildTool`) | The natural home for the **send-path check** (§4) and the **class G/H block** (§5) — declared per tool, not remembered per prompt. | Sprint 2 |
| 6 | Command parsing (Bash AST) | Structural parse before classification. Same lesson as `_assert_balanced`: substring matching on a command string is walkable, an AST is not. | Sprint 2 |
| 7 | Execution sandboxing | The **D-18 DeepSeek V4 sandbox** already specified. | Sprint 2 |
| 8 | Permission architecture | Approval state across sessions maps onto the **T0–T4 tiers** and the Phase 0–3 ladder. Class H stays T4 forever regardless of accumulated approvals. | Sprint 2 |
| 9 | Three-tier context compression | Needed once transcripts are long. **Compression is a redaction boundary** — §3 applies to summaries, which are new persisted text. | Sprint 2 |
| 10 | Cross-session memory | This is the **client harness**, and it is already tenant-scoped by the register schema. | Exists in part |
| 11 | Dream system — idle-time consolidation | Maps onto the Q8 2am–6am window. **Gated:** `CONSOLIDATION_BRIEF` D-4 says the harness must not self-modify until predictive scoring is live. Background consolidation that rewrites procedure is exactly that. | Blocked on scoring |
| 12 | Multi-agent coordinator | Spawns the five D-19 subagents, collects and synthesises. The natural home for the D-17 router. | Sprint 2 |

### Why this is worth adopting rather than improvising

**It gives §6 a real enforcement point.** `routing.py` currently documents its own limitation:
`produced_by` is a caller-supplied string, so the model boundary is a labelling check and not a
boundary. CLAUDE.md §6 says enforce at the *routing layer* — and layers 5, 7 and 12 together are
that routing layer. A coordinator that dispatches to an engine knows which engine ran. Stamping
`produced_by` from the dispatcher rather than from an argument converts the weakest claim in the
Sprint 1 code into an enforced one, and it also satisfies the D-17 schema requirement that every AR
record the model that produced it.

**And the ordering is already right.** Layers 1–9 are plumbing that can be built and tested now;
layer 11 is gated on scoring; layer 12 is where routing goes once there is a single-model baseline
to measure it against. That is the same sequencing D-17 argued for on independent grounds.

---

## Open questions raised by these two decisions

| # | Item | Question |
|---|---|---|
| S-15 | **What are the five, and are they five weight sets or five adapters?** | Four personas plus one ingestion/vision model? Or five roles including the relevance classifier? And full finetunes versus one base with five LoRA adapters — a ~4× VRAM difference, and D-13 already recommends adapters. Answer this before any training run: it determines whether five agents can answer concurrently or only in sequence. |
| S-16 | **Does the subagent model absorb the 8B relevance classifier?** | Carried over from S-11 and still unanswered. `CURRENT_AWARENESS_PIPELINE` specifies a separate 8B classifier. Consolidating to one small model for classification, subagent work, the voice pass and vision ingestion is simpler to run and to reason about — but it is a decision, not a default. |
| S-17 | **Abliteration versus abstention** | Does the uncensored checkpoint abstain as readily as its own base? Run the eval before finetuning. If it does not, use stock `Qwen/Qwen3.8-27B` instead — the vision head and the licence are properties of the base, not of the abliteration. |
