# Action Tier and Register Specification

**Prepared:** 15 August 2026 · Revision 1
**Companion to:** `CONSOLIDATION_BRIEF.md`, `AGENT_CHARTERS.md`, `agentoperatingdesign.pdf` §4 and §8
**Status:** settled where marked, flagged where open. Build-blocking items 1 and 2 of 4.

---

## 0 · Settled inputs this spec is built on

| # | Decision |
|---|---|
| A-1 | The agent **sends** on the principal's behalf. |
| A-2 | It acts **as itself** — signs under agent name, role and AI-agent identifier. Never as the principal. |
| A-3 | **All surfaces** in scope: email, calendar, messaging, CRM, documents. |
| A-4 | **Permanent carve-outs:** final negotiation, procurement sign-off, contract signing. Read, brief and draft are allowed in all three; only the send is blocked. |
| A-5 | Everything is tracked in **both directions** — owed by and owed to. |
| A-6 | **Multi-user.** Principal, EA, and relevant direct reports. |
| A-7 | Pre-meeting brief, then a **consent prompt 5 minutes prior**. Refusal means the meeting goes **dark** — per-meeting, not standing. |
| A-8 | Ad-hoc response target **2–5 minutes**. |

---

## 1 · The authority model

Authority is assigned by **action class**, not by surface. Whether something goes out over email or Slack changes almost nothing; whether it creates a commitment, and to whom, changes everything.

Five tiers:

| Tier | Name | Behaviour |
|---|---|---|
| **T0** | Observe | Reads. Produces nothing outbound. |
| **T1** | Draft | Produces the artifact, queues it. A human sends. |
| **T2** | Send with hold | Sends under the agent's identity after a hold window. Recallable inside the window. |
| **T3** | Send | Sends immediately. Logged, and reported in the next digest. |
| **T4** | Blocked | Never sends, at any phase, regardless of scorecard. |

**Default hold window: 30 minutes.** No outbound between 22:00 and 06:00 local unless explicitly marked urgent by the principal — a 3am send reads as automation and undoes the identity work in one message.

### Action classes

| Class | Description | Commitment weight |
|---|---|---|
| **A** | Status query and chase — *"still waiting on the Henderson figures"* | None |
| **B** | Scheduling — propose, hold, move, decline, reschedule | Low |
| **C** | Acknowledgement — *"received, reverting Thursday"* | Low |
| **D** | Information supply — sends a document already cleared for that counterparty | Low |
| **E** | Introduction — making one, or following up one the principal promised | Medium — spends the principal's relationship capital |
| **F** | Substantive correspondence — expresses a position, an opinion, or new information | High |
| **G** | Commitment-creating — accepts terms, confirms scope, agrees a binding date | Very high |
| **H** | Carve-outs (A-4) | Absolute |
| **I** | Internal writes — CRM records, doc updates, register entries. No external counterparty | None externally |

### The matrix

| Phase | A | B | C | D | E | F | G | H | I |
|---|---|---|---|---|---|---|---|---|---|
| **0 · Instrument** (days 1–7) | T0 | T0 | T0 | T0 | T0 | T0 | T0 | T4 | T1 |
| **1 · Shadow** (wks 2–6) | T1 | T1 | T1 | T1 | T1 | T1 | T1 | T4 | T3 |
| **2 · Supervised** (wks 7–14) | T2 | T2 | T2 | T2 | T1 | T1 | T1 | T4 | T3 |
| **3 · Bounded** | T3 | T3 | T3 | T2 | T2 | T2 | T1 | T4 | T3 |

**Class G never rises above T1.** Anything that binds the principal gets a human hand on it permanently, even at full autonomy. Class H never leaves T4.

**Promotion is per class, not global** — consistent with §8's rule that promotion is a human decision reviewing a scorecard. A client can run A–D at Phase 3 while E–F sit at Phase 2 indefinitely. Time-based promotion remains worthless.

### The Shadow phase is where the training data comes from

At Phase 1 every class drafts into a queue that is never sent. The principal marks each one **would have sent / would have edited / would not have sent**. That is the eval set for this client, it costs them a few minutes a day, and it is the only way to reach Phase 2 with evidence rather than optimism. It also gives them something to react to from week two, which matters given how the fee is structured.

---

## 2 · Identity, and the signature block

Every outbound message carries, non-overridably:

```
Bram Visser · Engineering · AI agent
Working for <Principal>, The Carbon Project
Replies reach me. For a human: <escalation address>
```

**Implications to build for:**

- Each agent needs a **real mailbox** on the domain, with sender reputation, SPF/DKIM/DMARC, and a monitored reply path. Four agents, four addresses.
- Replies land with the agent. It handles them within its class authority and escalates on trigger.
- Sending as the agent means the **principal's own sender reputation is never at risk** — a quiet but real benefit of A-2.

### Escalation triggers — hand off and stop

Carried from `AGENT_CHARTERS`, plus two new:

- Counterparty expresses frustration
- A commitment is about to be made
- Anything legally binding
- Counterparty appears confused about AI status
- Confidence below threshold
- **New:** counterparty asks to speak to a person — immediate handoff, no further sends on that thread
- **New:** thread crosses into a class-H context (negotiation, procurement, signing) — the whole thread drops to T1

### Rate limits — the reputational guardrail

An agent that chases three times in a day costs the principal more than it saves.

- One chase per thread per **72 hours**
- Maximum **3 outbound per counterparty per week** across all classes
- Chase escalation ladder is fixed: nudge → nudge with deadline → escalate to principal. It never sends a fourth.

---

## 3 · The cross-context rule

**This is the highest-consequence constraint in the product**, and it does not exist in the current corpus.

An executive's position depends partly on holding information asymmetrically. An agent with full read access across every thread, meeting and document is one careless sentence away from telling counterparty A something it learned from counterparty B. That is not a privacy breach in the technical sense — nothing left the perimeter — but it is the failure that loses the client.

**The rule:** an agent may reference to a counterparty only facts that counterparty is already party to, or that are explicitly marked shareable with them.

This makes `shareable_with[]` a required field on every register record, defaulting to **the parties present when it was created** and nothing else. Widening is a deliberate act. Test it adversarially before Phase 2: seed the register with a fact known only to one counterparty and confirm it never surfaces elsewhere.

---

## 4 · Register schema — the delta

The existing register is company-shaped: contracts, dependencies, public statements, regulatory exposure. This buyer's small things are people-shaped. Same architecture, new entity types, and one new capture path.

### Core record — Commitment

```yaml
id:
tenant_id:
direction:        by_principal | to_principal | witnessed
counterparty_id:
statement:        # as close to the words used as capture allows
made_at:
made_in:          # meeting_id | thread_id | call_id | manual
source_type:      transcript | email | document | voice_dump | manual
provenance:       verbatim | paraphrase | inferred
confidence:       0–1
due:
status:           open | met | missed | superseded | void
owner:
visibility:       principal_only | principal_and_ea | leadership | all_users
shareable_with:   []
evidence_ref:
superseded_by:
last_action:      # what the agent last did about it, and when
```

`direction` is what turns a memory into a chase mechanic. `provenance` is what stops it chasing something nobody said — **never chase on `inferred`; surface it to the principal as a question instead.**

### Supporting entities

| Entity | Purpose |
|---|---|
| **Person** | Relationship to principal, cadence, last substantive contact, open loops both directions, sensitivity flags |
| **Meeting** | Attendees, brief issued, consent outcome, capture state |
| **Thread** | Message chain, counterparty set, current authority tier |
| **Decision** | What was decided, the reasoning *at the time*, who was in the room, what it depends on |
| **Exposure** | Renewals, notice periods, deadlines — carried unchanged |
| **Prediction** | Existing AR linkage — carried unchanged |

### Visibility is per record, not per tenant

A-6 makes this structural. Comp, personnel, board matters, M&A, legal exposure and anything health-related default to `principal_only`, **default-deny not default-allow**. Retrofitting a visibility field later is the same class of mistake as retrofitting `tenant_id`, and for the same reason: every record written before it exists is wrong.

### Write governance

Consistent with D-7 option C:

- Facts from a **source of truth** — calendar entries, executed contracts, CRM fields — write freely. Re-derivable, auditable.
- Commitments extracted from **conversation** are *proposals*. They enter the curator queue and the principal or EA confirms. At scale, auto-confirm above a confidence threshold with a daily digest of what was confirmed, rather than a per-item gate that gets skipped by week six.

---

## 5 · Capture, including the dark case

| Path | Cadence | Notes |
|---|---|---|
| Mailbox and calendar | Continuous | Primary source. Cheapest, highest coverage |
| Meeting transcript | Per meeting, consented | Highest quality. Consent prompt at T−5 min |
| Principal voice dump | On demand | 60 seconds after a meeting. Their own account — no consent question arises |
| Documents and CRM | Continuous read | Structured, writes freely |
| Manual entry | Any time | EA and principal |

### Consent

The T−5 prompt must know **who is on the call**, not merely ask the principal. Recording consent varies by state and several are all-party. The prompt therefore reads attendees from the calendar entry and applies the strictest applicable rule. Treat this as a legal check before Phase 2, not a build detail.

### Dark meetings must be loud in the register

A refused meeting produces **no content but a mandatory record**:

```yaml
meeting_id:
capture: none
reason: consent_declined
attendees:
known_topics:     # from the brief that was issued beforehand
gap_flag: true
```

Without this the register develops holes it does not know about — and the agent will confidently chase commitments that were superseded in a room it never entered. With it, the agent can say *"I have no record of what was agreed on the 14th"*, which is the honest and far more useful answer.

**Offer the voice dump immediately after every dark meeting.** It is the cheapest possible recovery and it keeps the gap from compounding.

**The pre-meeting brief still goes out regardless** — it is built entirely from the principal's own data and precedes the consent question.

*Some rooms it simply doesn't enter* is a good line for the pitch, and it is now true by construction.

---

## 6 · Failure modes to instrument

| Failure | Signal | Mitigation |
|---|---|---|
| **Cross-context leak** | Fact appears with a counterparty outside `shareable_with` | Adversarial test before Phase 2; hard block, not a prompt instruction |
| **Chase loop** | Repeat outbound on a thread with no reply | 72h per-thread limit; fixed 3-step ladder |
| **Dead thread revival** | Outbound on a commitment already met elsewhere | Status reconciliation before every send |
| **Stale state after a dark meeting** | Chase issued on a commitment from a gapped period | `gap_flag` suppresses auto-send for affected threads until reconciled |
| **Tone mismatch** | Counterparty escalates or goes quiet after agent contact | Per-counterparty contact outcome tracking |
| **Visibility bleed** | A `principal_only` record surfaces to EA or reports | Access log, monthly audit |
| **Register rot** | Time-to-signal rising | Monthly audit against source systems — carried from §9 |

---

## 7 · What this spec does not settle

Carried forward, in order:

1. **The window (Q8).** Recommendation stands: 2am–6am for the eight-card block, with a small resident model on one or two cards serving briefs, tracking and the 2–5 minute response target during business hours. This is also the S-12 priority policy.
2. **Shared-harness promotion (Q11).** Recommendation stands: keep it, narrow the warranty to procedural-only, client-entities-excluded, human-reviewed, auditable on request. Tenant zero being inside the boundary makes the cold-start argument much weaker, which is what makes keeping it safe.
3. **The day-7 deliverable and when the $5k starts.** The register plus a coverage statement is the natural day-7 artifact, verified by the principal naming what's missing. Whether billing begins day 8 or week 7 is the largest churn variable in the model.
4. **Connectivity** — how M365, Google Workspace or the CRM reaches an on-prem farm.
5. **Redaction and log hygiene at ingest** — so the privacy claim is true at the log layer, not only at the perimeter.
6. **The contract wrapper** — warranty wording, liability cap, PI and cyber cover, Privacy Act applicability, minimum term.

---

*Prepared from the project corpus and the decisions taken in session on 15 August 2026. Where this spec extends beyond the corpus — the authority tiers, the cross-context rule, the dark-meeting record and the visibility field — it is marked as new rather than presented as settled.*
