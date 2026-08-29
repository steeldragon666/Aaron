# Build Brief — Sprint 1

**Scope:** commitment register + hash-chained AR ledger, tenant zero only
**Duration:** two weeks
**Gate:** `no-mistakes` on every push, `--intent` referencing a spec or decision ID
**Out of scope:** everything else (see `CLAUDE.md`)

---

## 1 · Why this first

The register is the moat and everything filters against it. The AR ledger is the billable unit. Neither needs the GPU farm, so this track runs in parallel with hardware bring-up rather than waiting on it.

The milestone that matters is **the first scored prediction**. Sprint 1 builds the substrate that makes one possible.

---

## 2 · What to build

### 2.1 Register core

Entities per `ACTION_TIER_AND_REGISTER_SPEC.md` §4:

- `commitment` — the core record, with `direction`, `provenance`, `visibility`, `shareable_with`, `status`, `superseded_by`, `evidence_ref`, `last_action`
- `person` — relationship to principal, cadence, last substantive contact, open loops both directions, sensitivity flags
- `meeting` — attendees, brief issued, consent outcome, capture state, `gap_flag`
- `thread` — message chain, counterparty set, current authority tier
- `decision` — what was decided, the reasoning *at the time*, who was present, dependencies
- `exposure` — renewals, notice periods, deadlines
- `prediction` — links to AR

All carry the invariant fields. `shareable_with` defaults to the parties present at creation and nothing more.

### 2.2 Ingestion

Two paths only this sprint:

1. **Mailbox and calendar**, read-only, continuous
2. **Manual entry**

Transcripts, voice dumps and CRM come later. Build the ingest interface so adding a source is a new adapter, not a schema change.

Redaction runs **before** persistence, not after.

### 2.3 Extraction and the curator queue

Commitments extracted from conversational sources are *proposals*, not records. They land in a queue carrying a confidence score, the source reference, and the candidate fields.

Confirmation writes the record. Above a confidence threshold, auto-confirm with a daily digest of what was confirmed — a per-item human gate will be skipped by week six, and a design that assumes otherwise is wrong.

Facts from a source of truth (calendar entry, executed contract, structured field) write directly.

### 2.4 AR ledger

Hash-chained, append-only. Schema per `CONSOLIDATION_BRIEF.md` §3 Layer 2:

```
id / agent / tenant_id / claim / evidence / recommendation
prediction { statement, resolves_on, falsifiable_by }
decision_required_by / owner / effort / status / outcome / score
produced_by
```

Rules enforced in code, not convention:

- **No prediction, no AR.** Observations go to an appendix
- **Hard cap of five open ARs per agent**
- Unacted ARs are still scored — the counterfactual is the most valuable training data in the system

### 2.5 Visibility enforcement

Per-record, default-deny. Comp, personnel, board, M&A, legal and health default to `principal_only`. Every read is access-logged.

---

## 3 · Acceptance criteria

Sprint 1 is done when all of the following are true:

1. The register holds The Carbon Project's real commitments, ingested from a live mailbox and calendar
2. **Coverage ≥80%** measured against a manually compiled list of known commitments — the same gate Phase 0 sells to a client
3. Both directions are tracked: things owed by the principal and things owed to them
4. A commitment can be created, superseded and voided, with the chain intact and queryable
5. The ledger accepts an AR, rejects one without a falsifiable prediction, and rejects a sixth open AR for the same agent
6. Ledger hash chain verifies end to end
7. A `principal_only` record is provably invisible to an `all_users` reader — as a test, not an inspection
8. **Cross-context test passes:** a fact seeded from counterparty A cannot be retrieved in a context scoped to counterparty B
9. Every record carries all invariant fields; a migration attempting to add one to an existing table fails review
10. `no-mistakes` passes, with `--intent` present on every run in the sprint

---

## 4 · Test priorities

In order of consequence:

1. **Cross-context leak** — seed and attempt retrieval across counterparty boundaries. Adversarial, not happy-path
2. **Visibility bleed** — every visibility level against every reader role
3. **Hash chain integrity** — including tampering attempts
4. **Supersession** — a commitment superseded in a dark period must not be chased; `gap_flag` suppresses auto-action on affected threads
5. **Provenance** — nothing marked `inferred` is ever actionable without human confirmation

---

## 5 · Deliberately deferred

Do not build ahead into these, even where it looks cheap:

Send path and action tiers · watch feeds · scoring and calibration harness · shared/client split mechanics · persona voice pass · avatar and TTS · routing · `firstmate` · client console · agents two through four.

The action tier is fully specced and will be Sprint 2. Building it before the register is real means building it twice.

---

## 6 · Parallel track — hardware

Independent of the above, and the RAM is time-sensitive:

1. Confirm the card SKU — `lspci -nn | grep 20c2` (8 GB Hynix → 64 GB) vs `2082` (10 GB Samsung → 40 GB only)
2. Unlock one card on a spare host; verify 65536 MiB, count `POST-WRITE` lines, check `HW Power Brake Slowdown` is Not Active
3. 48-hour `gpu-burn` plus checksum validation — there is no ECC and no error telemetry, so this is the only error-rate baseline that will ever exist
4. **Buy the RAM now.** Prices are moving and fill rates are poor

Details in `docs/hardware/`.
