# CLAUDE.md

Operating instructions for this repository. Read before touching anything.

---

## What this is

A private executive intelligence service. Four named AI agents — Elena (Marketing), Amara (Design), Bram (Engineering, physical and software), Hugh (CFO/COO) — track a principal's commitments and propose dated, falsifiable Action Requests against them.

The buyer is a founder, CEO or senior executive. **$5,000/month**, plus a **$1,500 seven-day setup fee**. Sold as a professional management tool, not an AI service. The product promise is that it is *only theirs*: dedicated hardware, no external inference, nothing entering any training loop outside the client's own tenant.

Entity: **The Carbon Project**. Runs on an 8× CMP 170HX farm. Target capacity 4–5 clients per farm.

Full context in `docs/`. Start with `CONSOLIDATION_BRIEF.md` §0 for the settled stack, then `ACTION_TIER_AND_REGISTER_SPEC.md` for what we are building now.

---

## Non-negotiable constraints

These are enforcement requirements, not style preferences. If a change would violate one, stop and raise it rather than working around it.

### 1 · Schema invariants

Every record in the system carries, from the first migration:

```
tenant_id        # even though there is currently one tenant
visibility       # principal_only | principal_and_ea | leadership | all_users
shareable_with   # array of counterparty ids — DEFAULT DENY, never default allow
provenance       # verbatim | paraphrase | inferred
produced_by      # model identifier, even while there is only one model
```

Commitment records additionally carry `direction` (`by_principal | to_principal | witnessed`).

**Do not introduce a record type without these fields.** Each one is a retrofit that rewrites every row written before it existed. This is the single most expensive mistake available in this codebase.

### 2 · No external calls on any client-context path

The entire stack is self-hosted: GLM-5.2 reasoning, Qwen3.8 subagents, LTX-2.5 video, open-weights TTS. **Zero external API dependencies is a contractual product claim, not a preference.** Do not add an SDK, a hosted model call, a telemetry endpoint or a CDN dependency to any code path that touches client data. If something appears to need one, raise it.

### 3 · Secrets and plaintext hygiene

Client material passes through logs, KV cache, transcripts, backups and the register. The privacy claim has to be true at the log layer, not only at the perimeter.

- Redaction at ingest, before anything is persisted
- No credential or secret in plaintext in the register, the ledger, or any log
- Assume any string that reaches a log is recoverable by anyone with host access

### 4 · The cross-context rule

An agent may reference to a counterparty **only** facts that counterparty is already party to, or that are explicitly listed in that record's `shareable_with`.

Implement as a hard check in the send path — a query the message must pass — **not** as a system-prompt instruction. This is the failure that loses a client, and prompt-level constraints do not survive long context.

### 5 · Blocked actions are blocked in code

Class H — final negotiation, procurement sign-off, contract signing — is `T4` at every phase forever. Reading, briefing and drafting are permitted; the send is blocked. Enforce in the send path.

Class G — anything that creates a binding commitment — never rises above `T1` (draft only), regardless of scorecard.

See `ACTION_TIER_AND_REGISTER_SPEC.md` §1 for the full matrix.

### 6 · Model boundary

Where DeepSeek V4 Pro is used, it may generate **code, tests, migrations, configs and build artifacts that are verified by execution**. It must never generate an Action Request, an evidence block, a claim about the world, a prediction, or client-facing prose. Enforce at the routing layer.

### 7 · Verification gate

`no-mistakes` gates every push. No exceptions, including for "trivial" changes.

Every run carries `--intent` pointing at the decision or spec ID that motivated the work — `D-11`, `A-4`, `S-13`, or a section reference. Once Action Requests exist, `--intent` points at AR IDs instead. This produces the unbroken chain from decision through commit to scored outcome, and it is also the audit trail the product sells.

**`firstmate` is not in scope yet.** It arrives once the register schema and AR ledger are stable and covered by tests, scoped to the write tier only, with Relay permanently off.

---

## Current build state

**Settled:** the stack (GLM-5.2 / Qwen3.8 / LTX-2.5 / open TTS, all self-hosted); the four personas; Bram covers both physical and software engineering; internal-first with tenant-aware schema; the onboarding ladder (Phase 0 Instrument → 1 Shadow → 2 Supervised → 3 Bounded, promoted on measured performance, never on time); pricing; the action tier and register spec.

**Open, and does not block current work:**

| ID | Question | Working assumption |
|---|---|---|
| Q8 | Compute window | 2am–6am for the eight-card block; a small resident model on 1–2 cards serves briefs and the 2–5 min response target during business hours |
| Q11 | Shared-harness promotion | **Build for KEEP** — it is the superset. Dropping later is free; retrofitting is not |
| — | Day-7 deliverable and billing start | Register plus coverage statement at day 7; billing start unresolved |
| — | Connectivity to M365 / Google / CRM | Unresolved |

---

## Sprint 1 — the only thing in scope right now

See `docs/BUILD_BRIEF_SPRINT_1.md`.

Build the **commitment register** and the **hash-chained AR ledger**, pointed at The Carbon Project as tenant zero. Nothing else.

**Explicitly out of scope until a prediction has been scored:** avatar and video pipeline, TTS, persona LoRAs, NeMo Switchyard routing, DeepSeek V4, `firstmate`, agents two through four, the client console.

The instruction from the source design stands: *do not build four agents and four clients before a single prediction has been scored.*

---

## Conventions

- **Tests before merge.** "Verified by execution" is only a guardrail where tests exist; thin coverage turns the gate into theatre.
- **Commits reference an intent ID** in the subject line, matching the `--intent` passed to `no-mistakes`.
- **Migrations are additive and reversible.** No destructive migration without an explicit decision recorded in `docs/`.
- **Write governance:** facts from a source of truth (calendar, executed contract, CRM field) write freely. Anything derived from conversation, news or inference is a *proposal* into the curator queue.
- **Today's date goes into every system prompt.** Every world-fact claim carries an as-of date.
- Ask rather than assume when a spec is silent. Guessing at a schema decision here is expensive.

---

## Glossary

| Term | Meaning |
|---|---|
| **AR** | Action Request — the billable unit. A dated, owned, falsifiable proposal with a predicted outcome. No prediction, no AR |
| **Commitment register** | Per-client live record of everything decided, promised, owed or exposed. The moat. Everything filters against it |
| **Shared harness** | Procedural knowledge, cross-client. Contains no client facts or names. Human-reviewed diff to promote |
| **Client harness** | Factual, per-tenant, isolated. Contains everything confidential |
| **Phase 0–3** | The onboarding and authority ladder. Promotion is a human decision reviewing a scorecard |
| **T0–T4** | Action authority tiers: observe / draft / send-with-hold / send / blocked |
| **Class A–I** | Action classes, from chase through to commitment-creating. See the spec |
| **Dark meeting** | A meeting where transcription consent was declined. Produces an empty record with `gap_flag: true` — never silence |
| **Tenant zero** | The Carbon Project. Inside the shared-harness boundary |

---

## The failure this system is designed against

Sycophancy drift: AR acceptance rate climbing toward 100% while prediction accuracy stays flat. The agent has learned what gets approved rather than what is true.

The only instrument that detects it is scoring. Until the scoring harness is live, the agents' adversarial stance is entirely unverified — and a persuasive flatterer is worse than an obvious one.

**Score something early.**
