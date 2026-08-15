# Commitment register + AR ledger — Sprint 1

Scope is `docs/BUILD_BRIEF_SPRINT_1.md`. Specification is
`docs/ACTION_TIER_AND_REGISTER_SPEC.md`. Constraints are `CLAUDE.md`.

The register is the moat and everything filters against it; the AR ledger is
the billable unit. Neither needs the GPU farm, which is why this track runs in
parallel with hardware bring-up rather than behind it.

Nothing here sends anything. The send path, the action tiers, watch feeds, the
scoring harness, personas, video, TTS, routing and agents two through four are
all deliberately out of scope — see the brief's §5.

---

## Running it

```bash
cd register
python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'
.venv/bin/python -m pytest
```

A Phase 0 instrumentation week, end to end:

```bash
register init --zero --principal-email aaron@carbonproject.com.au --principal-name Aaron
register ingest --mailbox ~/mail/Inbox --calendar ~/calendars/
register propose --senders senders.json
register queue                       # what is waiting for a human
register digest --threshold 0.85     # auto-confirm the confident ones, print the digest
register loops                       # open commitments, both directions, plus dark periods
register coverage known.json         # the day-7 artifact
register reads                       # the access log
```

The ledger, which no agent writes to yet:

```bash
register ar-add first-ar.json        # rejected unless the prediction is falsifiable
register ars
register ar-status ar_01M0… rejected --note "not this quarter"
register ar-score  ar_01M0… correct  # unacted ARs are scored too — that is the point
register verify                      # hash chain, end to end
```

`known.json` is the manually compiled list of commitments the principal knows
about — a JSON array of `{statement, direction, counterparty, due}`. It is the
ground truth the coverage number is measured against, and the point of it is
that the client can falsify the number by naming something missing.

Every push goes through the gate:

```bash
tools/no-mistakes --intent S-4
```

---

## How it is put together

| Module | What it holds |
|---|---|
| `migrations/0001_initial.sql` | The whole schema. Every record table carries the invariant set from this first migration. |
| `invariants.py` | The invariant field set, the visibility defaults, and what "actionable" means. |
| `store.py` | The write boundary: invariant check, secret check, model boundary. Nothing writes around it. |
| `access.py` | Visibility, the cross-context rule, the access log, and the one path that widens `shareable_with`. |
| `entities.py` | The seven entities, supersession, dark meetings, gap suppression, open loops. |
| `ledger.py` | The hash-chained AR ledger and the three rules it enforces. |
| `ingest/` | Adapter interface plus mailbox, calendar and manual. Read-only, local, no sockets. |
| `redaction.py` | Runs before persistence, never after. |
| `extract.py` | Rule-based commitment extraction into candidates. |
| `curator.py` | The proposal queue, confirmation, auto-confirm and the daily digest. |
| `coverage.py` | Scores the register against the manual list. |
| `routing.py` | The model boundary — CLAUDE.md §6, enforced before a router exists. |

### Decisions taken here, where the spec was silent

Four choices the spec did not settle. Each is cheap to reverse except the
first, which is noted for that reason.

**Python 3.11 and SQLite, standard library only.** No runtime dependency, so
there is no SDK, no driver and no hosted call anywhere on a client-context
path — CLAUDE.md §2 is structural rather than a policy someone enforces at
review. The register is small enough to sit entirely in GLM-5.2's context
(CONSOLIDATION_BRIEF §0.4), so this store is an audit and query surface, not a
retrieval engine under load. The SQL is ANSI-shaped; the SQLite-specific parts
are the `AUTOINCREMENT` columns and the append-only triggers. Postgres, if a
second tenant ever needs row-level security, is a migration rather than a
rewrite. Python rather than TypeScript because everything this will eventually
sit next to — vLLM, the ingestion subagent, the DuckDB financial store — is
Python.

**`shareable_with` may be omitted at the call site; nothing else may.** Omitting
it means nobody, which is the safe reading. Raising instead would push a caller
into supplying a value they had not thought about, and the value reached for
under that pressure is a wide one. The other four invariants have no safe
default and are refused when absent.

**Extraction is rules, not a model.** Not a placeholder: a rule set has a fixed,
inspectable recall, so when coverage lands at 62% you can read the rules and
see which phrasing was missed. The interface is what matters — a model-backed
extractor is a swap of `extract.py`, not a schema change.

**Adapters read local files, not provider APIs.** Connectivity from M365,
Google Workspace or a CRM to an on-prem farm is an open item in both CLAUDE.md
and ACTION_TIER §7. Until it is settled, the sync that lands mail on local disk
is the boundary. An adapter that opens a socket is a decision, not an
implementation detail.

---

## Acceptance criteria — where each one stands

Against `docs/BUILD_BRIEF_SPRINT_1.md` §3.

| # | Criterion | State |
|---|---|---|
| 1 | Register holds real commitments from a live mailbox and calendar | **Mechanism built, not connected.** Adapters, ingest, dedupe and redaction are done and tested against fixtures. Pointing them at the real mailbox is a connection this repository does not have — see below. |
| 2 | Coverage ≥80% against a manually compiled list | **Instrument built, number not yet measurable.** `register coverage` computes and renders it, and the matcher is tested for not being generous. The figure itself follows criterion 1. |
| 3 | Both directions tracked | Done — `direction` on every commitment, `open_loops()` splits by it, tested. |
| 4 | Create, supersede and void with the chain intact and queryable | Done — `supersession_chain()`, `live_commitment()`, cycle-refused, tested. |
| 5 | Ledger accepts an AR, rejects one without a falsifiable prediction, rejects a sixth open AR | Done, tested. |
| 6 | Ledger hash chain verifies end to end | Done — `verify_chain()`, plus tamper, delete and reorder tests that drop the triggers first. |
| 7 | `principal_only` provably invisible to an `all_users` reader | Done — the full four-by-four matrix is asserted, not sampled. |
| 8 | Cross-context test passes | Done — `tests/test_cross_context.py`, adversarial across single reads, scoped queries, constructor defaults, widening and tenancy. |
| 9 | Every record carries all invariant fields; a retrofitting migration fails review | Done — and "fails review" is mechanical: `tests/test_migration_guard.py` parses every migration and fails any that adds an invariant column to an existing table. |
| 10 | `no-mistakes` passes with `--intent` on every run | Gate implemented at `tools/no-mistakes`, run log at `.no-mistakes/runs.jsonl`. See the provenance note below. |

### What is not done, and why

**Criteria 1 and 2 need a mailbox this repository cannot reach.** Everything
upstream of the connection is built and tested: adapters, idempotent ingest,
redaction before persistence, extraction, the curator queue, the coverage
instrument. What is missing is the sync that puts The Carbon Project's mail and
calendar on local disk — and how M365 or Google Workspace reaches an on-prem
farm is listed as unresolved in CLAUDE.md and ACTION_TIER §7.4. That is a
decision, not a gap in this code. Once a Maildir exists, `register ingest`
through `register coverage` produces the number without further code.

**`no-mistakes` was referred to but not supplied.** CLAUDE.md names it as an
existing tool; the handoff pack does not contain it. `tools/no-mistakes` is a
local implementation of the gate as described — intent required and validated,
format, lint, types and tests, every run appended to a JSONL log with the
commit it ran against. If the original exists elsewhere, set `NO_MISTAKES` to
its path and this script delegates to it while keeping the intent bookkeeping.

**Sprint 2 hooks that exist but do nothing.** `thread.authority_tier` is stored
and never read; `entities.may_chase()` returns the verdict a send path would
consult but nothing sends. Both are there so the send path is built against a
check that already exists and is already tested, rather than the reverse.

---

## The five test priorities

In the brief's order of consequence.

| Priority | File | What it attacks |
|---|---|---|
| 1 · Cross-context leak | `test_cross_context.py` | Seeds a fact from counterparty A and tries to retrieve it in a context scoped to B, through every read path available to a caller. |
| 2 · Visibility bleed | `test_visibility.py` | Every visibility level against every reader role; sensitive-category defaults; unknown levels deny rather than admit. |
| 3 · Hash chain integrity | `test_ledger.py` | Tamper, delete and reorder — each after dropping the append-only trigger, which is what an attacker with host access would do. |
| 4 · Supersession | `test_supersession.py` | Chains, cycles, voiding, and `gap_flag` suppressing a chase on a commitment that a dark meeting could have superseded. |
| 5 · Provenance | `test_provenance.py` | Nothing marked `inferred` is actionable, and there is no in-place promotion — confirming an inference writes a new record and supersedes the old one. |

---

## What to do next

Sprint 2 is the action tier and the send path, fully specced in
`docs/ACTION_TIER_AND_REGISTER_SPEC.md` §1–2. Before that:

1. **Settle the mailbox connection.** It blocks acceptance 1 and 2, and those
   two are the day-7 client artifact.
2. **Run the abstention eval on GLM-5.2** — the ten insufficient-data questions
   and five tax-referral questions from `AGENT_CHARTERS`. A day's work, and it
   de-risks everything above it. If the model will not abstain, nothing built
   on it can be trusted.
3. **Score something.** The register now makes a scored prediction possible,
   which was the whole point of building it first. Until scoring is live the
   agents' adversarial stance is unverified, and a persuasive flatterer is
   worse than an obvious one.
