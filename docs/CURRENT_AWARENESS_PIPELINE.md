# Current Awareness Pipeline
### Keeping the four agents genuinely current in their fields

---

## The principle

**Never fine-tune knowledge.** A LoRA teaches an agent *how to think and write* in its role. It cannot keep it current, and attempting it means permanent retraining against a moving target. Currency comes from three layers, none of which touch the weights:

| Layer | Mechanism | Latency | Answers |
|---|---|---|---|
| **Ambient** | Scheduled ingestion → corpus → morning briefing | Daily | "What changed while I slept" |
| **On-demand** | Live web search tool | Seconds | The long tail |
| **Watchlist** | Triggered alerts on specific signals | Minutes–hours | "This needs you now" |

---

## Sources by agent

Start with **five to ten per agent**, not a hundred. Feeds break, noise compounds, and a pipeline you can't maintain is worse than none.

### Head Engineer
- arXiv API, filtered by category + keyword (cs.LG, cs.AI, cs.DC, plus your domain)
- GitHub Releases API for your actual stack: vLLM, PyTorch, Prime Agent, quantisation toolchains
- NVIDIA developer blog + driver release notes (you're driver-pinned — you need to know what you're *not* installing)
- Standards Australia updates for applicable AS/NZS
- CVE/NVD feed filtered to your dependencies
- Hacker News + Lobsters, relevance-filtered hard

### Financial Officer
- **RBA** — cash rate decisions, statements, Statement on Monetary Policy
- **ATO** — rulings, determinations, RDTI program changes (RSS available)
- **ABS** — CPI, wage price index, business indicators
- **AASB** — standard amendments
- Business.gov.au grants and program announcements
- FX and any commodity series relevant to your business
- Industry benchmark publications

### Marketing Manager
- **ACCC** — media releases and enforcement priorities, **especially environmental claims guidance**
- Competitor sites: pricing pages, blogs, changelogs — fetched on schedule with diffing
- Platform policy changelogs: YouTube, Meta, Google Ads, LinkedIn
- Search trend data for your category
- Trade press for your verticals

### Designer
- WCAG / W3C working drafts and updates
- Browser release notes (CSS and platform features)
- Design system releases from the systems you borrow from
- Tooling: Figma changelog, relevant library releases

### The underrated channel
**A dedicated mailbox subscribed to the best newsletters in each field.** Parse inbound mail into the corpus. Signal density per unit of engineering effort is far higher than scraping, and it sidesteps the terms-of-service and legal exposure that large-scale scraping carries. Prefer **RSS, API, and newsletter** over scraping in every case where a choice exists.

---

## Pipeline

```
sources (RSS · API · mailbox · scheduled fetch+diff)
        ↓
   dedupe (content hash + near-duplicate detection)
        ↓
   RELEVANCE CLASSIFIER  ← 8B model on the services card
   scores each item 0–1 against each agent's interest profile
   threshold-gated; everything below the line is archived, not indexed
        ↓
   summarise + extract dated claims
        ↓
   embed → index with freshness metadata → route to agent corpus slice(s)
        ↓
   curator queue (nightly review, same gate as all other memory writes)
```

**The relevance classifier is not optional.** Without it the agents drown, retrieval precision collapses, and the whole corpus degrades. It's the cheapest component and the one that determines whether this works.

---

## Freshness schema

Extends the corpus metadata from the main architecture. These five fields are what stop an agent confidently quoting a superseded cash rate.

```yaml
observed_at:   <utc>              # when we ingested it
event_date:    <utc>              # when the thing actually happened
validity:      point_in_time      # | current_until_superseded | evergreen
confidence:    primary            # | secondary_reporting | rumour | speculation
half_life:     30d                # relevance decay constant
supersedes:    <sha256 | null>
```

- `validity: current_until_superseded` + `supersedes` handles the cash-rate problem: the old value stays retrievable for history but never surfaces as current.
- `half_life` drives a recency decay in ranking — 7 days for platform policy, 30 for market data, ∞ for a standard.
- `confidence` carries through to the agent's output. A rumour must be *stated* as a rumour.

---

## Retrieval-time handling

**Classify the query first.** "What is the current cash rate" and "how does monetary policy transmission work" need opposite retrieval profiles. Currency questions boost recency hard; mechanism questions ignore it entirely. Getting this wrong in either direction is the most common failure in news-augmented RAG.

**Inject today's date into every system prompt.** Trivial, constantly forgotten, and the cause of an enormous share of confused temporal reasoning.

**Require an as-of date on every world-fact claim.** Make "my information is current to X" a normal, expected behaviour rather than a hedge. An agent that says "as of the 14th" is more useful than one that sounds certain.

---

## The morning briefing

The curator agent already runs nightly on the services card. Extend it to produce a per-agent briefing:

1. **What changed** in your field in the last 24 hours
2. **What it means for our live work** — cross-referenced against active projects, not generic
3. **What needs Aaron's decision**, with the recommendation and the deadline

Injected into each agent's opening context. Item 2 is the one that makes this valuable rather than a news feed with extra steps — the difference between "vLLM released 0.x" and "vLLM 0.x changes the Marlin kernel path we depend on; here's the risk to our pinned build."

## The weekly deep scan

A natural **DEEP mode** task. Once a week, the 235B+ model reads the full week across all four domains at once and looks for cross-domain patterns no individual agent can see — the regulatory change that alters the unit economics that invalidates the positioning. That's an hour of pipeline-parallel inference on a Sunday night and it's exactly the kind of long-horizon, capacity-over-speed work the mode-switching architecture exists for.

---

## Guardrails

- **State the as-of date** for any claim about the world
- **Distinguish primary source from reporting.** "The RBA said" and "the AFR reported the RBA will" are different claims
- **Never launder a rumour into a fact** — the `confidence` field must survive into the output
- **Agents don't decide what to remember from news.** Proposals go to the curator queue like every other memory write. News is the highest-volume, lowest-signal input you have; it's exactly where unmanaged memory rots fastest
- **Cite or don't claim.** If it isn't in the corpus and search didn't find it, the answer is "I don't know," not a plausible reconstruction

---

## Build effort, honestly

Two to three weeks for a working version across four agents, then ongoing maintenance — feeds break, sites restructure, relevance profiles drift. Budget an hour a week.

Sequence it: **one agent, five sources, classifier, briefing.** Run it a fortnight. You'll discover that half your chosen sources are noise and two you didn't think of are essential, and you'd rather learn that once than four times.
