# The Four / Agent Team — Consolidation Brief
### Executive summary, key features, and the decisions that have to be made before anything gets built

**Prepared:** 14 August 2026 · **Revision 2**
**Sources consolidated:** `CHARACTER_BIBLE.md`, `AGENT_CHARTERS.md`, `CURRENT_AWARENESS_PIPELINE.md`, `Agent Description And Appearance`, `agentoperatingdesign.pdf`, `personavisualpipeline.pdf`

---

## 0 · Revision 2 — decisions taken

Four decisions have been settled since rev 1. They change the economics materially and largely in your favour.

| Decision | Answer |
|---|---|
| **D-1 · Customer** | **Internal first, tenant-aware schema.** You are tenant zero; `tenant_id` on every record from day one. |
| **D-2 · Personas** | **The PDF four — Elena, Amara, Bram, Hugh.** Character Bible personas retired. `[see D-15]` |
| **S-4 · Engineering scope** | **Both** — physical/systems *and* software, carried by **one persona: Bram wears two hats.** No fifth face. `[D-16 closed — see §5a]` |
| **D-8 · Video** | Superseded by the stack decision below. |

### The resolved stack

| Layer | Choice | Runs where | Sovereign? |
|---|---|---|---|
| Reasoning — Prime Agent, all agents' thinking | **GLM-5.2** — ~753B MoE / ~40B active, 1M context, MIT licence | Self-hosted on the farm | **Yes** |
| Subagents | **5 × dense 27B**, finetuned from `junafinity/Qwen-3.8-27B-Uncensored` — Apache-2.0, vision head `[D-19 — see MODEL_AND_MIDDLEWARE_SPEC]` | Self-hosted | **Yes** |
| Avatar video | **LTX-2.5** — open weights, ≥16GB VRAM, permissive licence, free commercial use under $10M ARR, no branding requirement | Self-hosted | **Yes** |
| Voice | ~~ElevenLabs~~ → **open-weights TTS on-farm** `[D-14 — shortlist below]` | Self-hosted | **Yes** |
| Routing | **NeMo Switchyard** + Nemotron 3.5 Lightning *(under consideration)* `[D-17]` | Self-hosted | **Yes** |
| Middleware — agent loop, tools, permissions, coordinator | **Twelve-layer harness architecture** `[D-20 — see MODEL_AND_MIDDLEWARE_SPEC]` | Self-hosted | **Yes** |
| Long-horizon code/engineering | **DeepSeek V4 Pro**, sandboxed `[D-18]` | Self-hosted | **Yes** |
| Hardware | CMP 170HX, **80GB unlocked**, **PCIe ×16** | — | — |

**With ElevenLabs dropped, the stack has zero external API dependencies.** That is worth stating plainly, because it is now a *positioning* asset and not merely a cost one: every layer — reasoning, subagents, routing, video, voice — runs on hardware you own. Nothing about a client's data leaves the premises, and no vendor can reprice, deprecate or throttle you mid-contract. For a sovereign-AI pitch that is the whole argument, and until this turn it wasn't true.

### What this changes

**1 · The $3,300/month avatar cost line is gone.** It was ByteDance's licence rented through fal, not compute. LTX-2.5 needs ≥16GB and you have 80GB per card — it fits with four to five times headroom. Marginal cost becomes electricity: roughly **$5–50/month** rather than $3,300, and the sovereignty objection to the avatar layer disappears with it. LTX-2.5's own API is $0.09/sec at 720p — worth knowing as a burst-capacity fallback, but not as the primary path.

**2 · Most of `personavisualpipeline.pdf` §5 is now obsolete.** The 60-second cap, the hard-cut-on-content-boundary strategy, the B-roll seam bridges, the "never crossfade" warning — every one of those was a workaround for OmniHuman's generation limit. LTX-2.5 advertises **native multi-shot generation holding character, environment, lighting and voice consistent across cuts**. If that holds up in testing, the entire segment-stitching problem stops existing and the "shorten the report to 90 seconds" lever becomes an editorial choice rather than a cost-forced one. **Verify before rewriting the pipeline doc.**

**3 · The hardware objections from rev 1 are resolved.** 80GB per card holds GLM-5.2's weights across a small number of cards, and PCIe ×16 removes the interconnect bottleneck that made multi-GPU sharding impractical at ×4. *One thing still worth confirming: which PCIe generation the ×16 link negotiates at.* Gen 3/4 ×16 makes tensor parallelism comfortable; Gen 1 ×16 (~4GB/s) still favours pipeline parallelism — which `CURRENT_AWARENESS_PIPELINE` already assumes for the weekly deep scan, so either way the architecture holds.

**4 · GLM-5.2's 1M context simplifies the memory design.** The commitment register — Design B's stated moat — is small enough to sit **entirely in context** rather than being retrieved. That removes a whole class of retrieval-miss failure on the highest-value data in the system. Corpus and news still need RAG; the register does not. This is a genuine architectural saving and it wasn't available when either source document was written.

**5 · GLM-5.2 is the correct choice for this hardware — here is the defensible case for it.** Checked against the open-weights field as at August 2026:

| Model | Total / active | Licence | Self-hostable | Notes |
|---|---|---|---|---|
| **GLM-5.2** | ~753B / 40B | **MIT** | Yes | ~168 tok/s — roughly **3× its peers**. No vision. Shipped without vendor benchmarks. |
| Kimi K3 | 2.8T / 50B | *Modified* MIT | **No — API-only pending weight release** | Highest composite (AA Index 57, 4th globally). Native vision. Reported to need 64+ accelerators. |
| DeepSeek V4 Pro | 1.6T / 49B | MIT | Yes | Best-in-world LiveCodeBench (93.5%). **But a reported ~94% hallucination rate on AA-Omniscience.** |
| Qwen3.8-Max | 2.4T / 95B | Open weight | Yes | Largest active-parameter count in the class — most expensive to serve. |

**Three reasons it wins on your farm specifically:**

- **Smallest weight footprint in the frontier class.** 753B against 1.6T, 2.4T and 2.8T. On 80GB cards that is roughly a third to a quarter of the cards the alternatives need. K3 is out entirely — no weights released.
- **Throughput is the binding constraint, and GLM-5.2 wins it by ~3×.** Video render, LoRA training, the relevance classifier and live inference all compete for the same cards. Tokens-per-GPU-hour is the number that decides how much of the farm the agents can actually have.
- **Unmodified MIT.** K3's "modified MIT" is a clause set that would need reading before a multi-tenant commercial deployment. GLM-5.2's doesn't.

**And a reason to rule out the obvious challenger.** DeepSeek V4 Pro beats it on coding by a distance — and a reported ~94% hallucination rate on AA-Omniscience makes it *disqualifying* here, whatever its benchmark scores. AA-Omniscience measures whether a model knows what it doesn't know. That is the exact failure mode this entire system is built to avoid: Hugh's *"I don't have enough data to answer that,"* Bram's *measured / specified / assumed*, Elena's `[UNSUBSTANTIATED]` tag. A model that confabulates under evidence pressure would poison the AR ledger at the source, and every downstream guardrail would be papering over it.

**So the revised caution is narrower and more useful.** Not "verify the model is good" — it's the strongest fit available. Rather: **GLM-5.2 is the one model in the class that shipped with no vendor benchmarks, and the public composites don't measure the thing you actually need**, which is calibration and abstention, not capability. `AGENT_CHARTERS` already specifies the right instrument — *"10 questions where the correct answer is 'insufficient data'"* and the five that must trigger the tax-agent referral. **Run those as an abstention eval before committing, not a capability eval.** If GLM-5.2 answers the insufficient-data questions confidently, nothing built on top of it can be trusted, and you want to know that in week one rather than month six.

**6 · The gap nobody has costed: GLM-5.2 has no vision.** K3 does; GLM-5.2 doesn't. Look at the read tiers in `agentoperatingdesign.pdf` §3 — Amara needs Figma frames and session recordings; Hugh needs invoices and contracts, which arrive as scanned PDFs more often than not; Bram needs dashboards and screenshots. That is a real capability hole in a text-only reasoning stack. **Mitigation, consistent with the stack already chosen:** a small vision-capable Qwen3.8 variant as an ingestion subagent that converts images and documents to structured text, which GLM then reasons over. Costs one more model to serve; avoids re-architecting around a vision model that needs three times the cards.

---

## 1 · Executive summary

You have **two complete, high-quality, and largely incompatible designs for the same product**, written from different starting assumptions and never reconciled.

**Design A — "The Four"** (`CHARACTER_BIBLE`, `AGENT_CHARTERS`, `CURRENT_AWARENESS_PIPELINE`)
An internal executive team for **your own business**. Four adversarial personas — Priya Raman (Marketing), Ingrid Vos (Finance), Yusuf Karim (Engineering), Juno Park (Design) — built as LoRA-tuned specialists on sovereign on-prem hardware, with a curated corpus, an evidence standard per role, Australian regulatory guardrails (ACL, ACCC, WCAG 2.2, AS/NZS), mandatory disclosure at the protocol layer, and a **dissent log** as the primary artifact. The value proposition is *better decisions for Aaron*.

**Design B — "Omniscient AI"** (`agentoperatingdesign.pdf`, `personavisualpipeline.pdf`)
A **multi-tenant client service**. Four differently-named, differently-bodied personas — Elena (Marketing), Amara (Design), Bram (Engineering), Hugh (CFO/COO) — delivered to paying clients as daily video standups and weekly reports. The atomic unit is an **Action Request** carrying a falsifiable, dated, scored prediction. The moat is a per-client **commitment register**. The value proposition is *a scored consulting team you rent*.

Both designs are internally coherent. Neither is a subset of the other. **They disagree on the four things that matter most:** who the customer is, what the agents' output actually *is*, how persona identity is technically held stable, and whether the system is sovereign or API-dependent.

### The three findings that should change what you do next

**1. The business model fork is the only decision that matters right now.** Internal team and client service imply different corpora, different guardrails, different economics, and different personas. Every other contradiction in this document resolves automatically once this one is settled. Building further before settling it means building twice.

**2. Design B has the commercial engine; Design A has the quality engine — and each is missing the other's.**
Design B contributes the two ideas that make this billable: *predictive accuracy as the anti-sycophancy training signal* (explicitly flagged in the source as "the single most important line in this document"), and the Action Request as a unit that can be priced, counted, and scored. Design A contributes the ideas that make the output trustworthy: evidence standards, regulatory guardrails, disclosure, dissent logging, and a genuinely engineered adversarial stance per role. **A merged system takes B's spine and A's flesh.** Neither alone is sellable — B without A's guardrails will eventually publish an unsubstantiated environmental claim; A without B's scoring will drift into an articulate flatterer with no way to detect it.

**3. The avatar layer is the single largest threat to the economics and to the positioning.**
At fal's ~$0.16/second, four personas × 3-minute daily video = **~$3,300 per client per month in render alone** — 65% of a $5k/month contract before compute, staff or margin. Worse, OmniHuman is ByteDance API-only and cannot run on the 170HX farm, which directly contradicts the sovereign on-prem positioning that is presumably the reason the farm exists. Meanwhile `CHARACTER_BIBLE` states plainly: *"Most of your interaction will be text, not video."* **The daily-video assumption is unbudgeted, off-strategy, and probably unnecessary.** It should survive only if a client is explicitly paying for it.

### Where the value actually is

The source material already says this in two places and it's worth stating once more in one place. In `CHARACTER_BIBLE`: *"Prep, not performance, is where the value is… the highest-return use of all four isn't fronting the conversation — it's the thirty minutes before it."* In `agentoperatingdesign`: *"Reports are a delivery format. They create no value on their own and they can't be scored."*

**The billable product is the Action Request and the commitment register that generates it. The faces are marketing for the product, not the product.** Any build sequencing that puts the visual pipeline before the AR ledger has the priority inverted.

---

## 2 · What all sources actually agree on (the spine)

This survives the merge regardless of which way the decisions below go. Treat it as settled.

| # | Agreed principle | Source |
|---|---|---|
| 1 | **Four agents: Marketing, Finance, Engineering, Design.** Role coverage is identical across both designs. | All |
| 2 | **Adversarial by construction.** Sycophancy is the named primary failure mode. Agreement between agents is a defect, not a feature. | Charters §design principles; Operating §9 "consensus collapse" |
| 3 | **Dissent must be recorded and reviewed on a cycle.** | Charters "dissent log"; Operating §9 "require dissent to be recorded" |
| 4 | **Build one agent end-to-end before building four.** | Charters "build order"; Operating §10 |
| 5 | **Start with the Engineer.** Same three reasons in both: most objectively verifiable output, easiest to score, hardest stance to get right. | Charters (Yusuf); Operating §10 (Bram) |
| 6 | **Never fine-tune knowledge.** Weights carry *how to think*; currency comes from retrieval and watch feeds. | Awareness §principle; implied throughout Operating |
| 7 | **Personas fully synthetic. No real person's face or voice.** | Charters; Bible |
| 8 | **Every claim carries a source; unsourced claims are marked, not smoothed.** | Charters (all four evidence standards); Operating (AR `evidence:` block) |
| 9 | **Humans commit; agents prepare.** Contracts, sign-offs, safety certification, ATO matters escalate. | Bible cross-cutting rule 2; Operating phase ladder |
| 10 | **Visual identity must be locked and versioned.** A drifting face reads as fake faster than anything else. | Bible; Pipeline §1 |
| 11 | **Distinctive over glamorous.** Over-polished synthetic presenters trip uncanny-valley scepticism in exactly the B2B audience you want. | Charters; consistent with Pipeline's "no retouching / natural skin texture" prompts |
| 12 | **Watch feeds must be narrow and maintained.** 5–10 sources per agent, not a hundred. | Awareness; Operating §3 |

---

## 3 · Key features — the consolidated system

Presented as the merged architecture, with the contested elements flagged `[see D-n]` and cross-referenced to the decision register in §4.

### Layer 1 — Identity and persona

| Feature | Specification | Status |
|---|---|---|
| Four named personas | Marketing, Finance, Engineering, Design | Agreed; **names and bodies contested** `[D-2]` |
| Functional charter per persona | Owns / does not own / adversarial stance / evidence standard / hard guardrails / corpus slice / tools / artifacts / voice | Complete in `AGENT_CHARTERS` for Design A personas only |
| Character bible per persona | Locked vs Variable appearance, writing signature, verbal signatures, physicality, voice profile | Complete in `CHARACTER_BIBLE` for Design A personas only |
| Counterparty engagement map | Who each agent deals with, what that counterparty scans for, which trait is the asset, register shift, human-must-front boundary | **Unique to `CHARACTER_BIBLE` — the strongest commercial asset in the whole corpus.** No equivalent in Design B. Preserve regardless. |
| Disclosure identifier | Name + role + "AI agent", non-overridable, at protocol layer: on-screen, video description, phone greeting, written-output footer | In Design A only; **entirely absent from both PDFs** `[D-9]` |
| Visual consistency method | LoRA vs Midjourney seed + omni-reference | **Direct contradiction** `[D-3]` |
| Voice | One cloned reference read per persona, 3–5 min clean audio, versioned; per-persona pitch/rate/pause/non-verbals | Specified in Design A; Design B says only "add TTS on top" |

### Layer 2 — Output and value

| Feature | Specification | Status |
|---|---|---|
| **Action Request** | `id / agent / client / claim / evidence / recommendation / prediction{statement, resolves_on, falsifiable_by} / decision_required_by / owner / effort / status / outcome / score` | Design B. **Adopt — this is the billable unit.** |
| No prediction → no AR | Observations go to appendix | Design B |
| Hard cap 5 open ARs per agent | Anti volume-padding | Design B |
| Score unacted ARs too | The counterfactual is the most valuable training data | Design B |
| Role artifacts | Positioning docs, three-statement models, technical specs, design systems, risk registers, variance analyses, RDTI substantiation schedules | Design A. Merge as *wrappers* around ARs, not as the unit of value |
| Dissent log | Recorded when the director overrules; reviewed quarterly | Both |
| Board meeting vs sequenced standup | Independent-then-synthesise vs sequential-with-prior-transcript | **Direct contradiction** `[D-6]` |

### Layer 3 — Knowledge and currency

| Feature | Specification | Status |
|---|---|---|
| Three currency layers | Ambient (daily ingest → briefing) · On-demand (live search) · Watchlist (triggered alerts) | Design A |
| Relevance filter | 8B classifier scoring 0–1 against agent interest profile **vs** commitment-register entity matching | **Contradiction** `[D-5]` |
| Freshness schema | `observed_at / event_date / validity / confidence / half_life / supersedes` | Design A. **Adopt — solves the superseded-cash-rate problem.** |
| Retrieval query classification | Currency questions boost recency; mechanism questions ignore it | Design A |
| Today's date injected into every system prompt | Trivial, constantly forgotten | Design A |
| As-of date on every world-fact claim | "My information is current to X" as normal behaviour | Design A |
| **Commitment register** | Contracts and key dates, dependencies, decisions and reasoning, public statements, deadlines/renewals/notice periods, outstanding predictions | Design B. **Adopt — described as the moat, and it is.** Works for an internal build too. |
| Curator gate on memory writes | Nightly review queue; agents propose, don't commit | Design A |
| Shared vs client harness split | Procedural knowledge shared; factual knowledge tenant-isolated; promotion is a human-reviewed diff | Design B. Only meaningful if multi-tenant `[D-1]` |
| Memory write governance | Curator gate on everything **vs** free write within tenant container | **Contradiction** `[D-7]` |

### Layer 4 — Measurement and improvement

| Feature | Specification | Status |
|---|---|---|
| **Predictive accuracy (Brier) as primary signal** | Explicitly chosen over approval, readership, or acceptance because it cannot be gamed by agreeableness | Design B. **Adopt — the single highest-value idea in the corpus.** |
| Calibration | 70%-confident claims right 70% of the time | Design B |
| AR acceptance rate target 40–70% | 100% means it's only proposing safe things | Design B |
| Execution rate of accepted ARs >70% | Low means recommendations aren't actionable | Design B |
| Time-to-signal, falling | Days between event and flag | Design B |
| **The alarm:** acceptance ↑ while accuracy flat | The Factorio failure in slow motion — agent has learned what gets approved, not what's true | Design B |
| Per-agent eval sets | 50 marketing briefs / 50 finance queries + 10 insufficient-data + 5 tax-referral / 30 feasibility + 10 planted flaws + 10 optimistic timelines / 30 design briefs + 10 a11y traps | Design A. **Adopt — these are the acceptance tests.** |
| Monthly outcome review | The actual training loop. Skip it and the agents accumulate rather than improve | Design B |
| Quarterly harness promotion review | Human-approved shared-layer diff; also the audit trail | Design B |

### Layer 5 — Guardrails and compliance

| Feature | Applies to | Status |
|---|---|---|
| ACL s18 / s29 — no unsubstantiated performance claims | Marketing | Design A only |
| **ACCC environmental-claims substantiation** — refuse to draft, cite the guidance | Marketing | Design A only. **Non-negotiable given carbonproject.com.au** — greenwashing is a standing ACCC enforcement priority and you are in the exposed category |
| No fake/incentivised reviews; comparative claims need data on file | Marketing | Design A only |
| Registered-tax-agent referral on any lodgement/deductibility/ATO question | Finance | Design A only |
| Forecast never presented as fact; assumptions in a dedicated section; accounting profit distinguished from cash in every report | Finance | Design A only |
| AS/NZS compliance flagged; hazard section on safety-relevant designs; no sign-off where a failure mode has no detection path | Engineering | Design A only |
| WCAG 2.2 AA as floor, ratios checked not eyeballed; no dark patterns ever | Design | Design A only |
| Escalation triggers (frustration / commitment being made / legally binding / counterparty confused about AI status / confidence below threshold) | All | Design A only |
| Cross-tenant leak scan on shared diffs | All | Design B only |
| EU AI Act Article 50 audit trail | All | Design B — **jurisdictionally questionable** `[D-10]` |

### Layer 6 — Infrastructure and economics

| Feature | Specification | Status |
|---|---|---|
| 170HX farm | LoRA training, vLLM inference, 8B classifier on services card, 235B+ weekly DEEP scan | Design A |
| Prime Agent Continual Harness | Self-rewriting prompts, skills, memory, sub-agent definitions | Design B. **Sits awkwardly with per-agent LoRA** `[D-4]` |
| OmniHuman 1.5 render | 60s @ 720p / 30s @ 1080p cap; ~$0.16/sec; ByteDance API only; not self-hostable | Design B. **Off-strategy and expensive** `[D-8]` |
| Midjourney master portraits | Fixed seed, `--style raw`, 3:4, mid-chest, neutral-pleasant closed lip, ≥1536px, omni-reference for variants, shared `--sref` across all four | Design B. Prompts are written and good |
| Segment stitching | Hard cuts on content boundaries, or B-roll bridges; never crossfade | Design B |
| Cost levers | Shorten to 60–90s · rotate video/text · weekly video only · open-weights fallback · cache opener/closer (20–30% saving alone) | Design B |
| Pricing / floor price | Only stated as an implication ($3.3k render on a $5k contract). **No actual pricing model exists in any document.** | **Gap** `[D-11]` |

---

## 4 · Decision register — the contradictions

Ordered by leverage. D-1 and D-2 unblock most of the rest.

---

### D-1 · Who is the customer? *(blocks almost everything)*

**The conflict.** `AGENT_CHARTERS` and `CURRENT_AWARENESS_PIPELINE` describe an internal team for one business: "what needs **Aaron's** decision", your codebase, your Xero, your RDTI claim, your design system. `agentoperatingdesign.pdf` describes a multi-tenant service: `client: acme-pty-ltd`, per-tenant harnesses, an unbilled Phase 0–1, churn risk in month one, a $5k/month contract.

**Consequences of getting it wrong.** Multi-tenancy is not a feature you add later — it determines the memory architecture, the shared/isolated split, the review gate, and whether corpus content can be reused at all. Building single-tenant then retrofitting means rewriting the memory layer.

| Option | What it means |
|---|---|
| **A · Internal only** | One corpus, no tenancy split, no unbilled onboarding. Value is your own decision quality. Fastest to something working. Not billable. |
| **B · Client service only** | Full tenancy split from day one, AR ledger per client, onboarding ladder, floor price. Billable, slower, higher build cost. |
| **C · Internal first, productise later** *(recommended)* | Build single-tenant **but design the memory schema tenant-aware from day one** — a `tenant_id` on every record and the shared/client harness distinction respected even when there is only one tenant. You are the first client. Your own business becomes the reference case and the eval set. Costs perhaps 10% extra now, saves a rewrite. |

**Question to answer:** Is the first paying customer someone other than you, and if so — when?

---

### D-2 · Which four people are these? *(blocks all visual and voice work)*

**The conflict.** Two complete and irreconcilable persona sets.

| Role | Design A (Bible/Charters) | Design B (PDFs) |
|---|---|---|
| Marketing | **Priya Raman**, 38, Sydney, South Asian, ex-journalist | **Elena**, 45, Southern European, editorial/athletic |
| Finance | **Ingrid Vos**, 52, Dutch-Australian, **female**, ex-audit, startup that failed | **Hugh**, 55, Anglo-Australian, **male**, CFO/**COO** |
| Engineering | **Yusuf Karim**, 45, MENA, ex-field engineer | **Bram**, 46, Dutch, desk-built |
| Design | **Juno Park**, 33, Korean, ex-editorial | **Amara**, 28, Filipino/Nigerian |

Note this is not a naming difference — it is different ages, genders, ethnicities, backstories, and in the finance role a different scope (CFO vs CFO/COO).

| Option | What it means |
|---|---|
| **A · Adopt Design A wholesale** *(recommended)* | The Bible personas have full psychological specs, verbal signatures, writing signatures, and — critically — a **counterparty engagement map** that has no equivalent in Design B. The traits are *derived from the adversarial stance*, which is why they work. Cost: the four Midjourney prompts must be rewritten. That is an afternoon. |
| **B · Adopt Design B wholesale** | Portrait prompts and seeds already written and presumably rendered. Cost: throw away the entire Character Bible, including the engagement map. |
| **C · Design A characters, Design B ages/roles** | Keeps Hugh's COO scope and the older marketing lead. Requires rewriting both. |

**Sub-questions if A:** Does Finance stay female (Ingrid)? Does Finance absorb COO scope? Does the Design lead stay 33, or shift toward Amara's 28?

**Question to answer:** Have the Design B masters already been rendered and approved, and is there sunk cost — or is this still open?

---

### D-3 · How is facial identity technically locked?

**The conflict.** `CHARACTER_BIBLE`: *"Don't rely on seeds and prompts alone; they drift, and drift is what makes synthetic presenters read as fake."* → generate 20–40 references, cull to 15–20, **train a character LoRA**, lock and version it. `personavisualpipeline.pdf` §1: *"Consistency lever: Fixed integer seed + identical params"* → Midjourney master + `--oref`/`--cref` for variants.

These are opposite prescriptions and the Bible explicitly names the PDF's method as the failure mode.

| Option | What it means |
|---|---|
| **A · LoRA** | Genuine identity lock, trains in <1hr on a single 170HX, runs on your own hardware, no per-image API cost, unlimited variants. Requires a working SD/Flux training stack. |
| **B · Midjourney seed + omni-reference** | Zero infrastructure, works today, better out-of-box aesthetic quality. Drifts on novel poses/wardrobe/lighting. Per-image cost. Subject to Midjourney's parameter changes between versions (the PDF itself flags this). |
| **C · Midjourney to generate the training set → LoRA to lock it** *(recommended)* | Use MJ for the 20–40 high-quality references — it's the better generator. Cull. Train the LoRA. Then all downstream variants come off your own hardware, indefinitely, consistently, and on-strategy for sovereignty. This is the synthesis both documents are circling. |

> **REVISED (rev 2).** Option C stands, but the LoRA target changes. You are no longer rendering through OmniHuman, so identity does not need to survive a handoff between two vendors' models — it needs to be held inside **LTX-2.5**. Sequence: Midjourney masters (already written, already seeded) → cull to 15–20 → **train a character LoRA on LTX-2.5 per persona** → all stills and video come off the farm from there. 80GB cards make this training comfortable rather than marginal. Note the precedent: the LTX line already has community talking-head AV LoRAs, so this is a trodden path rather than research.

**Question to answer:** Is there a working image/video-model training pipeline on the farm today, or is that itself a project?

---

### D-4 · LoRA specialisation vs Prime Agent self-rewriting harness

**The conflict.** `AGENT_CHARTERS` specifies a per-agent LoRA (~2–5k examples, tuned for register and structure). `agentoperatingdesign.pdf` §0 specifies Prime Agent's Continual Harness, which *rewrites its own prompts, skills, memory and sub-agent definitions* — and warns via the Factorio result that it will optimise whatever signal you give it.

These are two different mechanisms for making an agent good at its role, with different failure modes (LoRA: stale, expensive to update, but stable and auditable. Harness: adapts continuously, but can drift, thrash, or learn to game).

| Option | What it means |
|---|---|
| **A · LoRA only** | Stable, auditable, cheap at inference. Updating means retraining. No self-improvement loop. |
| **B · Harness only** | Adapts continuously. Requires the full scoring apparatus to be running before it's safe — otherwise it optimises for approval. |
| **C · LoRA for register, harness for procedure, gated** *(recommended)* | LoRA fixes *how the agent writes and structures* — slow-moving, so retraining is rare. Harness accumulates *what worked* — fast-moving, gated by the quarterly human-reviewed diff already specified in Design B. Voice is frozen; method evolves. |

**Prerequisite regardless:** the harness must not be allowed to self-modify until predictive scoring is live. Design B says this in effect; make it explicit — and it matters more now, not less, because GLM-5.2 is a far more capable engine to point at a badly-chosen objective. A more capable model does not make the Factorio failure less likely; it makes it faster and more plausible.

> **REVISED (rev 2) — the LoRA target has to move.** With GLM-5.2 doing all agents' reasoning through Prime Agent, per-agent LoRAs on a 753B MoE are a serious training build *and* an awkward serving problem (multiple adapters, pipeline-parallel, one shared model). But dropping LoRA entirely throws away the Character Bible's whole thesis: that register and structure are what make an agent's output land.
>
> **Proposed split — see D-13.** GLM-5.2 reasons, unadapted and shared. A small **per-persona LoRA on the Qwen3.8 subagent** does the final voice pass, rewriting GLM's output into that persona's register. Cheap to train (~2–5k examples, exactly what `AGENT_CHARTERS` specifies), cheap to serve, trivially versionable, and it keeps the reasoning model single, shared and auditable — which is also what the shared/client harness split wants.

---

### D-5 · How is incoming news filtered?

**The conflict.** `CURRENT_AWARENESS_PIPELINE`: an **8B relevance classifier** scores each item 0–1 against each agent's *interest profile*, threshold-gated. Described as "not optional… the cheapest component and the one that determines whether this works." `agentoperatingdesign.pdf` §4: *"The filter for every external item is: does this affect something in the register? If not, discard it — don't summarise it."* And §3: *"Watch named entities, not topics. 'Marketing trends' produces slop."*

Interest-profile scoring is topical. Register matching is entity-based. They will produce materially different feeds — and Design B is arguing that Design A's approach produces noise.

| Option | What it means |
|---|---|
| **A · Interest-profile classifier** | Catches things you don't yet know you care about. Higher volume, lower precision. |
| **B · Register-entity matching** | Everything surfaced is actionable by construction. Blind to anything not already in the register — misses the new competitor, the emerging regulation. |
| **C · Register first, classifier second, separate channels** *(recommended)* | Register hits are **Action Requests** (interrupt-worthy, high precision). Classifier hits are **the weekly scan** (discovery, tolerable noise, never interrupts). This maps exactly onto the existing daily/weekly cadence split and resolves the tension without losing either capability. |

---

### D-6 · Board meeting or sequenced standup?

**The conflict — and this one is sharp.** `AGENT_CHARTERS`: *"Each writes an independent position before seeing the others — **this is the important part**, because sequential review anchors everyone to whoever went first."* `agentoperatingdesign.pdf` §6: *"Generate in order, feeding each agent the prior transcript… it's the difference between a team and a playlist."* Hugh opens, Bram reacts, Amara reacts, Elena reacts, Hugh closes.

Design B's method is precisely the anchoring failure Design A warns against. Design A's method produces four disconnected monologues, which is Design B's "playlist" complaint. Both critiques are correct.

| Option | What it means |
|---|---|
| **A · Always independent** | Maximum diversity of position, no anchoring. Reads as four separate reports. |
| **B · Always sequenced** | Feels like a team. Systematically under-samples disagreement — and consensus collapse is a named alarm in the same document. |
| **C · Independent for decisions, sequenced for standups** *(recommended)* | Two different rituals for two different jobs. **Decision/board mode:** independent positions written blind, then one synthesis round, then recommendation with dissents recorded — for anything consequential. **Standup mode:** sequenced, for daily continuity and narrative. Explicitly measure disagreement rate in standup mode; if it trends to zero, the alarm has fired. |

---

### D-7 · Who is allowed to write to memory?

**The conflict.** `CURRENT_AWARENESS_PIPELINE`: *"Agents don't decide what to remember from news. Proposals go to the curator queue like every other memory write."* Nightly human/curator gate on **all** writes. `agentoperatingdesign.pdf` §2: client harness is *"Writable by: agent, within its own tenant container"* — only the **shared** layer is gated.

| Option | What it means |
|---|---|
| **A · Gate everything** | Highest quality, no rot. Becomes a daily human chore that will be skipped by week six. |
| **B · Gate shared layer only** | Scales. Client-layer rot is the known risk, which Design B mitigates with a monthly register audit. |
| **C · Gate by record type** *(recommended)* | Facts derived from a connected source of truth (Xero, GitHub, a filed contract) write freely — they're re-derivable and auditable. Facts derived from **news, inference, or conversation** go to the curator queue. This matches where rot actually comes from: Design A's own text says news is "the highest-volume, lowest-signal input you have… exactly where unmanaged memory rots fastest." |

---

### D-8 · Video cadence and the avatar layer *(largest cost decision)*

**The conflict.** `CHARACTER_BIBLE`: *"Most of your interaction will be **text**, not video."* `personavisualpipeline.pdf` §5–6 and `agentoperatingdesign.pdf` §5: daily standup, 60–90s video per agent, four agents, every business day. Plus: OmniHuman is API-only and cannot run on the farm — the PDF itself raises this and leaves it open.

**The numbers, from the source:** 3 min × 4 personas × 22 days = **$2,534/month**, +30% for retakes ≈ **$3,300**, +TTS. Against a $5k/month contract that is 65% of revenue before anything else.

| Option | What it means |
|---|---|
| **A · Daily video, all four** | $3.3k/client/month. Off-strategy (API dependency). Impressive demo. Almost certainly loss-making below ~$15k/month contracts. |
| **B · Weekly video standup, daily text** *(recommended)* | ~$150–300/month render. Video becomes an event rather than wallpaper. Text is where the substance lives anyway — the Bible says so explicitly. |
| **C · Open-weights talking head for cadence, OmniHuman for showpieces** | Preserves sovereignty for the routine case; keeps quality where a client sees it. Adds a model to run and maintain. |
| **D · No video at all in v1** | Fastest path to a scored prediction. Faces stay as stills in written reports. Defer the entire pipeline. |

**Apply regardless of choice:** cache openers/closers per wardrobe variant (20–30% saving, per the source), and set a monitored per-client render ceiling.

> **RESOLVED (rev 2) — this decision is largely dissolved.** With LTX-2.5 self-hosted on 80GB cards, render cost falls from ~$3,300/month to power, and the API-dependency objection disappears. Daily video is now **affordable**, so the question becomes editorial rather than financial: *is a daily talking head the best use of the reader's attention?* `CHARACTER_BIBLE`'s answer — "most of your interaction will be text" — was an editorial judgement, not a cost one, and it still stands on its own merits. The opener/closer caching lever is now pointless; drop it. The per-client render ceiling is now a GPU-hours ceiling, not a dollar ceiling, and it competes with inference for the same cards — **that** is the real constraint to monitor.
>
> **Three things to verify before committing the cadence:**
> 1. **Does LTX-2.5 do audio-driven lip-sync natively, or via a LoRA/pipeline?** The 2.3 generation had explicit LipSync and LipDub modes plus community talking-head AV LoRAs. If 2.5 needs the same, that's an extra component to stand up — not a blocker, but not free either.
> 2. **Render throughput on 170HX.** The published 10-second-clip-in-6.8-seconds figure is on 2× GB200, which is a different universe of silicon. Measure your own seconds-of-video-per-GPU-hour before promising a daily cadence, because that number sets how much of the farm video eats.
> 3. **The $10M ARR licence threshold.** Free commercial use below it. Note it now so it isn't a surprise later.

**Question that still matters:** Is the video the thing a client is actually buying, or the thing that makes the first sales call land? The cost answer has changed; the strategic answer hasn't.

---

### D-9 · Disclosure — present in one design, absent from the other

**The conflict.** `CHARACTER_BIBLE` and `AGENT_CHARTERS` mandate a permanent, non-overridable "name, role, AI agent" identifier — on-screen at first appearance, in every video description, in the phone greeting, in the footer of every written output, *built at the protocol layer so it cannot be configured off* — and argue it's a **commercial asset**: a journalist finds a disclosed AI that did its homework more interesting, not less; a vendor takes it more seriously, because it signals process.

Neither PDF mentions disclosure anywhere. The visual pipeline's pre-render checklist has nine items and disclosure is not one of them. The persona prompts are optimised for photorealism — "natural skin texture with visible pores, no retouching."

This is a gap rather than a considered disagreement, but it needs to be closed deliberately.

| Option | What it means |
|---|---|
| **A · Full protocol-layer disclosure** *(recommended)* | As the Bible specifies. Removes ACL misleading-conduct exposure, satisfies platform likeness/synthetic-media policies, and — per the Bible's own argument — is a differentiator rather than a cost. |
| **B · Disclosure in client contracts only** | Client knows; downstream recipients of agent-drafted material may not. Exposed if agents ever contact third parties. |
| **C · Case by case** | Not recommended. "Configurable disclosure" is the thing that becomes a headline. |

**Question to answer:** Do agents ever contact third parties directly (journalists, vendors, prospects), or only ever produce material a human sends? The Bible's engagement map assumes direct contact; if that's real, A is the only defensible answer.

---

### D-10 · Which jurisdiction's AI rules are we designing to?

`agentoperatingdesign.pdf` §2 cites **EU AI Act Article 50** as the reason for the promotion audit trail. Everything else in the corpus is Australian — ACL, ACCC, ATO, RDTI, RBA, ABS, AASB, AS/NZS, business.gov.au. The user is Australian.

| Option | What it means |
|---|---|
| **A · Australian only** | Correct today for domestic clients. ACL is the operative instrument; Australia's AI framework is guidance-based, not yet an EU-equivalent statute. |
| **B · Design to EU Article 50 as the ceiling** *(recommended)* | Transparency obligations for synthetic content and AI interaction are the strictest published standard and are being converged toward. Designing to it costs little (you're already doing disclosure and audit trails) and removes a future rework. |

---

### D-11 · Pricing and the floor price *(the gap)*

**Nothing in any document states what this costs a client, what it costs you, or what the margin is.** The only economic fact in the corpus is that avatar render alone is $3.3k/client/month at daily-3-minute cadence, and the source calls that "the number that sets your floor price."

Given the stated objective of **value creation and billable products**, this is the most consequential missing artifact.

**Questions to answer:**
1. What does a client pay per month, and for what unit — seats, agents, ARs, or a flat retainer?
2. Are Phase 0–1 (weeks 1–6, per Operating §8) unbilled, discounted, or charged as a setup fee? The source says be honest about this at signature.
3. What's the fully-loaded COGS per client — render + inference + watch-feed maintenance + the human review time the gates require?
4. Is value attributable to executed ARs actually agreed with the client, as §7 Layer 2 requires — and if so, is there a success-fee component?

---

### D-12 · Brand and entity name

`agentoperatingdesign.pdf` and `personavisualpipeline.pdf` are both headed **"Omniscient AI"**. The project is titled **"170HX agent team"**. Your domain is **carbonproject.com.au**.

Three names, unclear relationship. Is Omniscient AI a product brand under The Carbon Project, a separate entity, or a working title? This determines whose ACL exposure the marketing agent's claims attach to, whose ABN is on the contract, and which brand the four personas represent.

---

### D-13 · Where does persona register actually live? *(new in rev 2)*

Follows from the stack decision. GLM-5.2 does all the thinking for all agents. If nothing else changes, all four personas become the same model wearing four different system prompts — which is precisely the *"one agent with four voices"* failure `AGENT_CHARTERS` opens by warning against.

| Option | What it means |
|---|---|
| **A · Prompt and corpus only** | Zero training cost. Persona differentiation is shallow and drifts under long context; GLM's own register bleeds through. Adequate for a v1 demo, thin for a product. |
| **B · Per-agent LoRA on GLM-5.2** | Deepest differentiation, matches `AGENT_CHARTERS` literally. Expensive to train on a 753B MoE and awkward to serve four adapters against one shared pipeline-parallel model. |
| **C · GLM reasons, per-persona Qwen3.8 LoRA does the voice pass** *(recommended)* | GLM-5.2 produces the substance — evidence, reasoning, the Action Request. A small per-persona LoRA rewrites it into that persona's register: Hugh's assumptions-first structure, Bram's *measured/specified/assumed* labelling, Elena's leads-with-the-point paragraphs, Amara's justify-against-user-need. ~2–5k examples each, exactly the volume `AGENT_CHARTERS` specifies. Cheap, versionable, and it keeps one shared auditable reasoning model. |

**Risk to watch under C:** a voice pass can quietly launder a hedge into a certainty. The rewrite must be constrained to register, never content — and the evidence block and prediction must pass through byte-identical. Make that a test, not a hope.

---

### D-14 · Voice — **ElevenLabs dropped. Now: which open TTS?** *(revised rev 3)*

Dropping ElevenLabs closes the last sovereignty hole **and resolves the consent trap by construction**, which is worth spelling out because it was the sharper of the two risks.

**The trap that no longer applies.** `CHARACTER_BIBLE` specifies *"Clone one reference read per persona, 3–5 minutes of clean audio."* Had that reference read come from a **real human**, it would have reintroduced exactly the likeness, consent and passing-off exposure that `AGENT_CHARTERS`' "fully synthetic personas only — no real person's face or voice" rule exists to eliminate, on the layer where it is hardest to detect after the fact. Going open-weights doesn't automatically fix this — most open TTS models clone zero-shot from a reference clip, so **the rule still has to be enforced deliberately: the reference clip must itself be synthetic.** Design or synthesise each persona's reference voice, archive it, version it, and never point the cloner at a person.

**Shortlist, as at August 2026:**

| Model | Licence | Why it's on the list |
|---|---|---|
| **VibeVoice** | MIT | Built for **professional long-form** — reportedly ~90 minutes of continuous audio in a single pass. Directly matches the use case; removes any script-length ceiling. **Lead candidate.** |
| **Higgs Audio v2** | Apache-2.0 | Reported to win most **emotion** benchmarks. Relevant because `CHARACTER_BIBLE` says the characteristic non-verbals — the four-second pause, the mid-sentence laugh, the "hmm" — *"do more for perceived realism than any amount of model quality."* Prosody control is the feature that matters here, not raw fidelity. |
| **Chatterbox** | MIT | Zero-shot cloning plus an emotion-exaggeration dial; reported to beat ElevenLabs in blind preference testing. |
| **CosyVoice 2** | Apache-2.0 | Instruction-level emotion control, tuned for real-time — the option if voice ever goes interactive (the phone greeting in the disclosure spec). |
| **Kokoro-82M** | Apache-2.0 | Preset voices only, no cloning — but tiny and fast. Useful as a draft/preview voice so you're not spending farm time rendering final audio on every take. |
| ~~XTTS v2~~ | **CPML — non-commercial** | **Rule out.** A non-commercial licence in a billable product is exactly the trap that is cheap to avoid now and expensive to discover at contract stage. |

**Recommended:** VibeVoice as the primary, Higgs Audio v2 evaluated head-to-head on the non-verbals specifically. Kokoro for drafts.

**The one thing to test before committing:** open TTS accent control is materially weaker than ElevenLabs'. The Character Bible's voice designs lean hard on accent — Australian with Dutch consonants, Australian with Indian-English rhythm. Whichever persona set survives, **generate a test read of each persona's actual script style before locking the model**, because "Australian professional male, 55" is a much harder ask of open TTS than of a commercial API.

---

### D-17 · NeMo Switchyard routing — right idea, wrong week *(new rev 3)*

NVIDIA shipped **Nemotron 3.5 Lightning** (30B MoE, ~3B active) and the **NeMo Switchyard** router in mid-August 2026. Switchyard is fully open source, provider-agnostic, routes across Nemotron, DeepSeek V4, Qwen, Kimi and commercial models, carries routing state across an agent session, and switches mid-task. LangChain's benchmark reported a 74% cost reduction against a frontier-only baseline.

**Why it fits this system better than average:**

- It **directly addresses S-12 (GPU contention)** — infrastructure signals including system load are one of its three routing inputs, which is precisely the problem created by video render, LoRA training, the classifier and live inference sharing one farm.
- It is the **clean mechanism for the D-18 sandbox** below: "DeepSeek V4 for code, never for claims" becomes an enforced routing policy rather than a convention someone remembers.
- **Nemotron 3.5 Lightning at ~3B active is a serious candidate for the subagent tier** — cheaper to serve than most Qwen3.8 variants, leaving farm capacity for GLM-5.2 and video. Worth benchmarking against whichever Qwen variant S-11 lands on.

**Two reasons not to adopt it yet:**

1. **It is days old.** Putting brand-new routing infrastructure inside the reasoning path before a single prediction has been scored means that when an Action Request turns out wrong, you cannot tell whether the model was wrong or the router picked the wrong model. Establish the single-model GLM-5.2 baseline first, *then* introduce routing and measure whether it moved the Brier score. That ordering is free; the reverse is not recoverable.
2. **Routing breaks the measurement layer unless the schema changes.** This is the concrete consequence and it needs writing down now: the whole Layer 4 apparatus — prediction accuracy, calibration, "an agent that's 70% sure should be right 70% of the time" — assumes a stable thing being scored. Route mid-task and you are scoring *a system*, not a model, and you lose the ability to tell whether a routing policy change improved or degraded calibration.

> **Schema addition, required before any routing goes live:** every Action Request records the **model or models that produced it**, and per-segment provenance where a task was routed across more than one. Without it, the calibration data becomes uninterpretable the day routing is switched on — and calibration data is the one asset in this system that cannot be regenerated retrospectively.

---

### D-18 · DeepSeek V4 Pro for long-horizon engineering and coding *(new rev 3)*

**The instinct is right, and the reasoning is worth making explicit.** Hallucination rate matters where a claim cannot be checked. In coding it can: the compiler, the test suite and CI falsify the output within seconds. That makes a high-capability, high-hallucination model *safe in the one domain where verification is automatic and instant* — and DeepSeek V4 Pro's 93.5% LiveCodeBench and 80.6% SWE-bench are the best available. Use it there.

**But the boundary has to be hard, and enforced rather than remembered:**

> **DeepSeek V4 Pro may generate code, tests, migrations, configs and build artifacts that are verified by execution. It must never generate an Action Request, an evidence block, a claim about the world, a prediction, or client-facing prose.**

The moment it is *asserting* rather than *generating-and-verifying*, the reported ~94% AA-Omniscience hallucination rate is live — and it would be live inside exactly the artifact the whole business is scored on. Encode this as a Switchyard routing policy (D-17), not as a convention.

**Two practical questions:**

1. **Capacity.** V4 Pro is 1.6T — roughly 20 cards at 80GB, on top of GLM-5.2's ~10. Does the farm hold both resident? If not, V4 runs as a scheduled batch job in GLM's idle windows, which suits long-horizon coding work anyway — it is the least latency-sensitive thing in the system.
2. **Test coverage becomes load-bearing.** "Verified by execution" is only a real guardrail where tests actually exist. Thin coverage turns the compiler check into theatre. If V4 is doing long-horizon engineering, `AGENT_CHARTERS`' test-strategy ownership stops being a nice-to-have and becomes the thing holding the sandbox shut.

---

## 5 · Secondary items to resolve (lower leverage, still real)

| # | Item | Conflict |
|---|---|---|
| S-1 | **Finance scope** | Charters: "Financial Officer", explicitly does *not* own tax filing or statutory accounts. Operating: "Hugh — CFO/**COO**", with spend authorisation requests in the write tier. Does the finance agent own operations, and can it authorise spend? |
| S-2 | **Marketing seniority** | "Marketing Manager" (Charters) vs "Marketing Director" (PDF). Affects register with counterparties. |
| S-3 | **Corpus source of financial truth** | Charters: "Financial facts come from the Tier 3 structured store — DuckDB, queried with SQL — never from RAG over prose." Operating §3 read tier: Xero, bank feeds, Stripe/PayPal, payroll direct. Is DuckDB the mandatory intermediate layer, or do agents query source systems live? |
| S-4 | **Engineering scope** | Charters' Yusuf is a *physical/systems* engineer — AS/NZS 3000, plants, commissioning, tolerances, contract manufacturers, steel-capped boots. Operating's Bram is a *software* engineer — GitHub, Sentry, CVEs, Node EOL, cloud billing. **These are different professions.** Which one does the business actually need? |
| S-5 | **Watch-feed ownership** | Awareness assigns Standards Australia + arXiv + NVIDIA to Engineering; Operating assigns CVEs + framework EOL + provider status. Follows from S-4. |
| S-6 | **Weekly deep scan vs monthly outcome review** | Awareness specifies a Sunday-night 235B cross-domain scan. Operating specifies a monthly scored-prediction review as "the training loop". Both are worth doing; confirm they're separate rituals and who consumes each. |
| S-7 | **Video length vs report length** | Pipeline says 90 seconds "is almost certainly better content" than 3 minutes. Operating §5 says 60–90s per agent per day. Broadly compatible — but confirm the standard is 90s, and that scripts are written to it rather than trimmed to it. |
| S-8 | **Number of watch sources** | Awareness: 5–10 per agent to start. Operating: scoped strictly to register entities. Compatible under D-5 option C, but the initial source list needs to be written down per agent for the first build. |
| S-9 | **Voice profiles for whichever personas win** | Bible's voice specs (Dutch consonants on Ingrid, Indian-English rhythm on Priya) are tied to Design A heritages and become invalid if D-2 goes the other way. |
| S-10 | **"Agent Description And Appearance" doc** | Contains only the words "Physical attributes". Either populate it or delete it — an empty doc in a project corpus is a retrieval hazard. |
| S-11 | **Which Qwen3.8 variant?** *(rev 2 — **closed** 26 Aug)* | Answered by **D-19**: `junafinity/Qwen-3.8-27B-Uncensored`, 27.78B dense, Apache-2.0, and it carries the vision head this row asked for. Two parts remain open and move to **S-15/S-16/S-17** in `MODEL_AND_MIDDLEWARE_SPEC.md`: whether the five are weight sets or adapters, whether they absorb the 8B relevance classifier, and whether an abliterated checkpoint still abstains. |
| S-12 | **GPU contention** *(rev 2, updated rev 3)* | Video render, LoRA training, the classifier, the weekly deep scan, TTS, DeepSeek V4 batch coding and live GLM-5.2 inference now all compete for the same farm. There is no scheduler or priority policy in any document. **NeMo Switchyard partially addresses this** (system load is a routing signal) but it routes between models, it does not schedule GPU time across workload classes. You still need a priority policy: decide what gets pre-empted when a client is waiting. |
| S-13 | **Model provenance in the AR schema** *(rev 3)* | Required before routing goes live — see D-17. Add `produced_by:` to the Action Request schema now, even while there is only one model, so the field exists before the data that depends on it. |
| S-14 | **Voice reference archive** *(rev 3)* | Whichever TTS wins, each persona's synthetic reference clip becomes a locked, versioned asset in the same class as the character LoRA. Store it in version control alongside the Midjourney seeds. A regenerated voice is a different person to the audience — `CHARACTER_BIBLE` is explicit on this and it applies identically to open-weights models. |

---

## 5a · Still open from rev 2

Two questions raised by the decisions taken, not yet answered.

### D-15 · Port the engagement map onto the PDF four?

You retired the Character Bible personas, which retires Priya, Ingrid, Yusuf and Juno. But the **counterparty engagement map** in that document — who each role deals with, what that counterparty is scanning for, which trait is the commercial asset, how register shifts, and where a human must front — is **role logic, not identity logic**. It ports onto Elena, Amara, Bram and Hugh essentially unchanged, and it remains the single strongest piece of commercial thinking in the corpus. Recommend rewriting it onto the new four rather than losing it.

Also carried over regardless of persona set: the per-role **evidence standards**, **hard guardrails** (ACL/ACCC, tax-agent referral, AS/NZS, WCAG 2.2 AA), **escalation triggers** and **eval sets** from `AGENT_CHARTERS`. None of those are identity-bound either.

### D-16 · Five roles, four faces — **CLOSED: Bram wears two hats**

Engineering covers both physical/systems and software under one persona. No fifth face, voice, or LoRA. Four personas stand.

**What this requires to work, since the two hats are genuinely different professions:**

1. **Two labelled corpus slices, not one merged pile.** Physical: AS/NZS standards, component datasheets, commissioning records, plant post-mortems. Software: the dependency manifest, CI logs, incident history, the codebase. Merged retrieval will surface a datasheet tolerance when asked about a CVE. Tag at ingestion.
2. **Two watch feeds, separately scoped.** Physical: Standards Australia, supplier notices, certifier bulletins. Software: CVE/NVD filtered to the actual manifest, framework EOL dates, provider deprecations. `agentoperatingdesign.pdf` §3 is right that Bram has the highest-signal feed of the four — but that claim is only true of the *software* half. The physical half is slower and needs a different relevance threshold, or it will be drowned out.
3. **Declare the hat in every output.** Bram's adversarial stance is the same question — *"is that measured or specified?"* — but it means different things pointed at a datasheet than at a CVSS score. Each Action Request should state which domain it comes from, so the evidence standard being applied is legible.
4. **Two eval sets.** `AGENT_CHARTERS` specifies 30 feasibility questions, 10 designs with planted flaws, 10 optimistic timelines. Run that twice — once physical, once software. Bram is the first agent built, so this is where the whole approach gets proven or doesn't.

**The failure mode to watch:** a merged engineer that is mediocre at both rather than sharp at either. If the dissent log after a quarter shows Bram's software objections consistently landing and his physical ones consistently vague — or the reverse — that's the signal to split him after all. Cheap to detect, and it costs nothing to design the corpus so the split stays possible later.

---

## 6 · Recommended path, if the recommendations above are taken

This is not a plan you've approved; it's what falls out of the recommended options, offered so you can see the shape.

**Now — decisions only, no build.** *D-1, D-2, D-8, D-14 (drop ElevenLabs) and D-16 settled.* Remaining: **D-11 (pricing)**, **D-13 (where persona register lives)**, **D-15 (port the engagement map onto the new four)**, plus **which open TTS** and **whether routing is in scope for v1 (D-17)**. All cost an hour, none require hardware.

**Week 0 — the abstention eval.** Before anything is built on GLM-5.2, run the 10 insufficient-data questions and 5 tax-referral questions from `AGENT_CHARTERS` against it. This is a day's work and it de-risks every subsequent week. If the model won't abstain, nothing above it can be trusted.

**Weeks 1–2 — the ledger, not the faces.** Commitment register schema and ingestion. AR data model, hash-chained. Both designs say this is first; the visual pipeline is a distraction until an AR exists.

**Weeks 2–5 — one agent, end to end.** Engineering (both designs agree), on your own business as tenant zero. Read tooling → register-scoped watch feed → ARs with dated predictions → the 30/10/10 eval set from `AGENT_CHARTERS`.

**Week 6 — the first scored prediction.** This is the milestone that tells you whether the whole approach works. `agentoperatingdesign.pdf` §10 closes with the right instruction: *"Do not build four agents and four clients before a single prediction has been scored."*

**Then, and only then:** scoring harness → shared/client split → **Switchyard routing, measured against the single-model Brier baseline** → remaining three agents → visual pipeline.

*Rev 3 note on ordering:* routing (D-17) and DeepSeek V4 (D-18) are both improvements to a system that does not exist yet. Every one of them adds a variable that makes the first scored prediction harder to interpret. Get one agent, one model, one scored prediction — then optimise. The stack you now have is good enough to start with and will still be there in six weeks.

---

## 7 · One risk worth naming explicitly

Both documents identify sycophancy as the primary failure mode, and Design B gives you the instrument to detect it: **AR acceptance rate climbing toward 100% while prediction accuracy stays flat.**

That instrument only works if predictions are being scored. Until the scoring harness is live, you have four articulate, well-characterised, adversarially-styled agents whose adversarial stance is **entirely unverified** — and a persuasive flatterer is worse than an obvious one. The character work in `CHARACTER_BIBLE` is genuinely excellent, and that is exactly what makes this risk sharp: it will *sound* like rigour before it *is* rigour.

Score something early.

---

*Prepared from project corpus only. No external sources consulted. Every claim above traces to one of the six source documents; where the sources disagree, both positions are quoted rather than reconciled silently.*
