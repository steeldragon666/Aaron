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
                                     # (and, advisory only, who has gone quieter than their cadence)
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
tools/no-mistakes --intent-from-commit          # reads the id out of HEAD's subject
tools/no-mistakes --intent-from-commit HEAD~1   # or any other commit
tools/no-mistakes --intent-from-commit --intent-only   # resolve the id, run nothing
```

It also runs in CI on every push and every pull request, which is the version
that counts — see "The gate, and where it runs" below.

---

## How it is put together

| Module | What it holds |
|---|---|
| `migrations/0001_initial.sql` | The whole schema. Every record table carries the invariant set from this first migration. |
| `invariants.py` | The invariant field set, the visibility defaults, and what "actionable" means. |
| `store.py` | The write boundary: invariant check, secret check, model boundary. Nothing writes around it. |
| `access.py` | Visibility, the cross-context rule, the access log, and the one path that widens `shareable_with`. |
| `entities.py` | The seven entities, supersession, dark meetings, gap suppression, open loops, derived contact and cadence. |
| `ledger.py` | The hash-chained AR ledger and the three rules it enforces. |
| `ingest/` | Adapter interface plus mailbox, calendar and manual. Read-only, local, no sockets. |
| `redaction.py` | Runs before persistence, never after. |
| `extract.py` | Rule-based commitment extraction into candidates. |
| `curator.py` | The proposal queue, confirmation, auto-confirm and the daily digest. |
| `coverage.py` | Scores the register against the manual list. |
| `routing.py` | The model boundary — CLAUDE.md §6, enforced before a router exists. |

### Decisions taken here, where the spec was silent

Six choices the spec did not settle. Each is cheap to reverse except the
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
implementation detail. `docs/TENANT_ZERO_MAILBOX.md` is the tenant-zero version
of that sync: `mbsync` over IMAP, outbound-only, no vendor integration.

**The secret check has two classes, and they get opposite treatment.** The
matcher is deliberately aggressive, so a policy of one response for everything
had to be wrong in one direction or the other.

*Human free-text is redacted in place and the write succeeds.* A rejection
reason, a widening justification, a gap note, an AR status note — all boxes a
person types into. Refusing the write means someone typing "the password is
wrong in their instructions" into a rejection reason has their action blocked,
and people who get blocked learn to route around checks. That is a strictly
worse outcome than a lost span: the rejection still needs to happen, so it
happens somewhere the audit trail cannot see.

*Machine-generated text is refused outright.* A credential in an extractor
candidate, an AR claim or a prediction is a defect in the producer, not a
typist's slip. There is nobody to inconvenience and nothing worth preserving,
so the write fails at the point the defect was introduced.

`store._HUMAN_TEXT_COLUMNS` and `store._MACHINE_TEXT_COLUMNS` are the
classification, and `test_invariants.py` fails if a record table is in neither
— so a new table's text is a decision someone makes rather than a check
someone forgets.

**`last_substantive_contact` is derived, not classified.** Deciding which
inbound message counts as "substantive" is a rule the brief never settled, and
a classifier guessing at it would put an invented date in front of a cadence
alert. Instead it is a `MAX` over records that are already first-class and
already carry provenance: meetings attended, and commitments made or acted on
with that person. Dark meetings count — the register knows they were in a room
together even when it does not know what was said. Voided commitments do not.

The derived version's failure mode is a date *older* than reality, which
produces an alert the principal dismisses. The classifier's failure mode is a
date *newer* than reality, which produces silence about a relationship that has
actually gone cold — the exact thing tracking cadence was for. Erring toward
noise is correct here.

Cadence is advisory and structurally cannot become an action:
`cadence_alerts()` writes nothing, and `may_chase()` does not consult it. Both
are asserted in `test_cadence.py` rather than left as intent.

---

## Acceptance criteria — where each one stands

Against `docs/BUILD_BRIEF_SPRINT_1.md` §3.

| # | Criterion | State |
|---|---|---|
| 1 | Register holds real commitments from a live mailbox and calendar | **Mechanism built; sync specified, not yet run.** Adapters, ingest, dedupe and redaction are done and tested against fixtures. The connection is no longer an open question — `docs/TENANT_ZERO_MAILBOX.md` is the tenant-zero sync, and it is an afternoon on the farm host, not a code change here. |
| 2 | Coverage ≥80% against a manually compiled list | **Instrument built, number not yet measured.** `register coverage` computes and renders it, and the matcher is tested for not being generous. Expect the first real figure to be well under 80% — see below, because what you do about that is the part that matters. |
| 3 | Both directions tracked | Done — `direction` on every commitment, `open_loops()` splits by it, tested. |
| 4 | Create, supersede and void with the chain intact and queryable | Done — `supersession_chain()`, `live_commitment()`, cycle-refused, tested. |
| 5 | Ledger accepts an AR, rejects one without a falsifiable prediction, rejects a sixth open AR | Done, tested. |
| 6 | Ledger hash chain verifies end to end | Done — `verify_chain()`, plus tamper, delete and reorder tests that drop the triggers first. |
| 7 | `principal_only` provably invisible to an `all_users` reader | Done — the full four-by-four matrix is asserted, not sampled. |
| 8 | Cross-context test passes | Done — `tests/test_cross_context.py`, adversarial across single reads, scoped queries, constructor defaults, widening and tenancy. |
| 9 | Every record carries all invariant fields; a retrofitting migration fails review | Done — and "fails review" is mechanical: `tests/test_migration_guard.py` parses every migration and fails any that adds an invariant column to an existing table. |
| 10 | `no-mistakes` passes with `--intent` on every run | Gate implemented at `tools/no-mistakes`, run log at `.no-mistakes/runs.jsonl`, and run in CI on every push and pull request. See "The gate, and where it runs" below — where it runs turned out to matter more than what it checks. |

### What is not done, and why

**Criteria 1 and 2 need a mailbox nobody has pointed at this yet.** Everything
upstream of the connection is built and tested: adapters, idempotent ingest,
redaction before persistence, extraction, the curator queue, the coverage
instrument. The connection itself is now specified —
`docs/TENANT_ZERO_MAILBOX.md` — as `mbsync` pulling IMAP into a local Maildir
on the farm: outbound-only, no vendor integration, no OAuth app, on-prem data.
That is deliberately not the connectivity design for client one, which needs
OAuth and per-tenant credential storage; it is the smallest thing that produces
a real coverage number. Once the Maildir exists, `register ingest` through
`register coverage` produces the number without further code.

**Expect that number to be well under 80%, and do not tune the rules to move
it.** The extraction rules were written against fixtures. Real mail is worse,
and a low figure is the first honest measurement this system has produced.
Tuning rules against one mailbox until it goes green is overfitting to one
person's writing habits — the rules stop generalising, client one is worse than
the honest number here, and the metric has stopped measuring anything. It is
sycophancy in a different costume: optimising the score instead of the thing
the score stood in for. `docs/TENANT_ZERO_MAILBOX.md` §4 has what to do
instead.

**`no-mistakes` was referred to but not supplied.** CLAUDE.md names it as an
existing tool; the handoff pack does not contain it. `tools/no-mistakes` is a
local implementation of the gate as described — intent required and validated,
format, lint, types and tests, every run appended to a JSONL log with the
commit it ran against. If the original exists elsewhere, set `NO_MISTAKES` to
its path and this script delegates to it while keeping the intent bookkeeping.

### The unguarded reads

`read_one`, `query` and `filter_readable` take a `Reader`, run `evaluate` and
write the access log. They are not the only way to get a record out. Nine
module-level functions — `open_loops`, `dark_periods`, `supersession_chain`,
`live_commitment`, `cadence_alerts`, `queued`, `fold`, `fold_all`, `measure` —
run their own SQL and return full rows to anyone holding the connection.

Raised by an independent review of the PR, and worth stating plainly rather
than filing under "known".

It is not a live leak in Sprint 1: there is no send path, no agent and no
counterparty-scoped caller, and CLAUDE.md §4 specifies the check *in the send
path*, which is Sprint 2 by construction. But "not currently exploited"
describes today's callers rather than the code. When the send path is built,
`open_loops` is the obvious thing to reach for — right shape, already there —
and using it bypasses the check silently. That is the same structural mistake
as a gate that runs only where the author chooses to run it: enforcement you
have to opt into is a convention.

`access.UNGUARDED_READS` names each one with the reason it may skip the Reader,
and `tests/test_read_surface.py` fails on any public function in the read
modules that is in neither that map nor `NOT_A_READ`. That is not enforcement
and is not claimed as such — it converts an omission nobody notices into a
decision someone records. `UNGUARDED_READS` is also the work list for Sprint 2:
everything in it that the send path wants has to be re-expressed through a
Reader first.

### What the second reader found

A full CodeRabbit review was run on the PR rather than accepting the draft
skip. Two constraints here are enforced by code written and tested by the same
agent, and single-party verification is the failure mode this product is sold
against. It found things the tests did not.

Fixed, with a regression test for each:

| | What was wrong |
|---|---|
| `routing.py` | The `human:` / `rules:` escape ran *before* the code-only check and returned early, so `human:deepseek-v4-pro` wrote Action Requests. `produced_by` is caller-supplied free text, so a prefix is a label anyone can type — it cannot be the thing that decides. Capability check first now. |
| `store.update` | `visibility` was absent from the forbidden set the docstring promised, so a routine field update could widen a `principal_only` record to `all_users` with no role check, no reason and no audit line. The test that should have caught it named the invariant in its title and then did not check it. |
| `store.update`, `supersede_commitment`, `void_commitment` | Keyed on record id alone. An id was enough to mutate another tenant's record. `tenant_id` is now a required keyword and part of the predicate. |
| `supersede_commitment` | Selected `status` and never read it, so superseding an already-superseded commitment silently overwrote the link and made a branch of the chain unreachable. |
| `curator.confirm` | Two independent writes on an autocommit connection. A failure between them left the commitment written and the proposal still queued, so the next `auto_confirm` wrote a *second* commitment for the same sentence. One transaction, plus a `state = 'queued'` predicate. |
| `ledger.score`, `append_ar` | Projection written before the ledger entry. See "the ledger and its projection" in `test_ledger.py`. |
| `extract.py` | Emitted naive local timestamps into `made_at` while `store.now()` emits UTC-aware. `derived_last_substantive_contact` takes a `MAX` over exactly those columns as text — so it could return a date *newer* than reality, silently suppressing the cadence alert the derivation exists to raise. |
| `parse_shareable_with` | Unguarded `json.loads` raised `JSONDecodeError` out of the middle of an access decision. An unreadable sharing list now denies, like the sibling branch for an unknown `visibility`. |
| `access.query` | `where` and `order_by` are interpolated. `"1=1) OR (1=1"` closed the tenant scope's brackets early. Nothing foreign was returned — `filter_readable` still denied on the tenant check — but every foreign record id landed in this tenant's `access_log`. `order_by` is an allowlist; `where` must balance. |
| `db.transaction` | A failed `COMMIT` left the transaction open, so the next `BEGIN` raised an unrelated error over the real one. |

Raised and **not** taken, with reasons: routing every read through a `Reader`
(see "The unguarded reads" above — the send path it would protect is Sprint 2,
and the classification guard is the proportionate half); a required as-of date
on AR claims (deferred deliberately, with `payload_schema_version` in place so
adding it later is a payload change rather than a retrofit); and the
documentation reconciliations it found across the handoff pack — persona names,
pricing status, hardware baselines. Those last are real inconsistencies in the
source documents and are listed in the PR thread, but resolving them is a
product decision rather than a code change.

### The gate, and where it runs

A verification gate that runs only where the author chooses to run it is a
convention with a CLI attached. Whoever pushes decides whether it ran, and an
agent pushing its own work is deciding about itself. The original point of
CLAUDE.md §7 is that the gate is a *mechanism* — something the author cannot
route around — and running it locally does not deliver that.

`.github/workflows/no-mistakes.yml` runs the same checks on a clean checkout,
on every push and every pull request, and reports against the commit whether or
not anyone asked. It reads the intent id out of the commit subject via
`--intent-from-commit`, which makes the other half of the convention
machine-checked too: a commit whose subject carries no decision, spec item or
AR id fails the gate.

The gate now has tests of its own (`tests/test_gate.py`), which it did not
before and should have from the start. It shipped broken twice in a row, both
times the same way — the intent id read off the wrong commit, first because a
`pull_request` checkout is a merge commit whose subject is GitHub's rather than
the author's, then because the fix threaded a ref parameter through the flag
and through `commit_subject` but not through the call between them. CI caught
both, which is the argument for CI; a verification tool with no verification of
its own is the wrong place to be leaning on that. Those tests invoke
`--intent-only` rather than the full gate, because the gate runs pytest and
pytest would run them again.

**Branch protection.** CI is necessary and not sufficient. Until
`no-mistakes / gate` is a *required* status check on the default branch, a red
run is a red badge rather than a closed door. That setting lives in repository
settings, not in this repository, so it is the one part of §7 that a commit
cannot deliver:

> Settings → Branches → add a rule for the default branch → Require status
> checks to pass before merging → select `gate`. Also tick "Do not allow
> bypassing the above settings", or an administrator — including an
> administrator acting on an agent's behalf — is exactly the route-around the
> rule exists to close.

**Sprint 2 hooks that exist but do nothing.** `thread.authority_tier` is stored
and never read; `entities.may_chase()` returns the verdict a send path would
consult but nothing sends. Both are there so the send path is built against a
check that already exists and is already tested, rather than the reverse.
`CLAUDE.md` §5 — class H blocked at T4 forever, class G never above T1 — is
enforced in the send path, so it is Sprint 2 by construction. Nothing here can
send, which is the only enforcement available until there is a send to block.

**No as-of date on AR claims.** `CLAUDE.md` conventions ask that every
world-fact claim carry one. There are no system prompts yet and no agent
writing claims, so the field is deferred to the first agent that writes one.

What is *not* deferred is the ability to add it safely.
`ar_ledger.payload_schema_version` exists from migration 0001 and every append
stamps `PAYLOAD_SCHEMA_VERSION` into the payload itself. "It's only a payload
change" is true exactly until the payload is unversioned JSON written by four
agents, at which point telling a v1 body from a v2 body means guessing at its
shape — the same retrofit class as a missing invariant, arriving through a
door nobody was watching. One integer now buys the migration later.

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

Plus one the brief does not list, added after an audit against `CLAUDE.md` §3:

| — · Log hygiene | `test_log_hygiene.py` | Both halves of the secret check. Human free-text — a rejection reason, a widening justification, a gap note, an AR status or scoring note — is redacted in place and the action still completes, including on a deliberate false positive. Machine-generated text — an extractor candidate, an AR claim, a prediction — is refused, and a refused write leaves the record untouched rather than half-applied. |
| — · Cadence | `test_cadence.py` | That `last_substantive_contact` comes from records rather than a classifier, and that a cadence alert writes nothing and cannot make anything chaseable. |
| — · Read surface | `test_read_surface.py` | That every public function which hands back record content is classified — see "The unguarded reads" below. |

---

## What to do next

Sprint 2 is the action tier and the send path, fully specced in
`docs/ACTION_TIER_AND_REGISTER_SPEC.md` §1–2. Before that:

1. **Run the mailbox sync.** `docs/TENANT_ZERO_MAILBOX.md`, on the farm host.
   It unblocks acceptance 1 and 2, which are the day-7 client artifact, and it
   is the only remaining item that produces a number rather than more code.
   Record whatever coverage comes back. Do not tune toward it.
1b. **Turn on branch protection.** One repository setting, and without it the
   gate is advisory. See "The gate, and where it runs".
2. **Run the abstention eval on GLM-5.2** — the ten insufficient-data questions
   and five tax-referral questions from `AGENT_CHARTERS`. A day's work, and it
   de-risks everything above it. If the model will not abstain, nothing built
   on it can be trusted.
3. **Score something.** The register now makes a scored prediction possible,
   which was the whole point of building it first. Until scoring is live the
   agents' adversarial stance is unverified, and a persuasive flatterer is
   worse than an obvious one.
