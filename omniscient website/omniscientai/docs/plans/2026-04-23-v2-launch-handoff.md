# OmniscientAI v2 Redesign — Launch Handoff

**Date:** 2026-04-23
**Branch:** `feat/v2-redesign`
**Status:** All code work complete. 74 commits on the branch. Ready for staging + production cutover.

---

## What's shipped

| Layer | What | Tests |
|-------|------|-------|
| Tokens | `omniscient.css` scoped to `.v2`, Tailwind aliases, theme helper | — |
| UI primitives (14) | Button, Card, FeaturedCard, Eyebrow, Display, Lede, MonoBadge, CTALink, Input, Textarea, Select, Slider, RadioCard, CheckboxCard | 114 |
| Layout (6) | Container, Section, InkSection, Nav, Footer, Layout | 48 |
| Brand (3) | Logo, BrainGraphic, TaglineBar | 18 |
| Sections (14) | HeroSplit, HeroCentric, PillarGrid, CaseGrid, WorkshopCardGrid, StatsRow, StepStack, FAQAccordion, TestimonialStrip, CTAStrip, BookingForm, ContactForm, ArticleHeader, ArticleBody | 122 |
| Pages (20) | Home, Services, ServiceDetail, Industries, IndustryDetail, Workshops, WorkshopDetail, About, Approach, Contact, Book, CustomWorkshop, Insights, InsightArticle, AIReadinessQuiz, ROICalculator, PrivacyPolicy, Terms, NotFound, ComponentShowcase | 109 |
| **Total** | **57 files, ~411 tests** | **411** |

Plus: 5 PNG brand assets, design system reference at `docs/design-system/`, redirects for cut tools, expanded sitemap.

---

## Dev-time preview

```powershell
cd "C:\Users\Aaron\omniscient website\omniscientai"
pnpm dev
```

Open:
- `http://localhost:3000/` — current dark-theme site (unchanged, production-safe)
- `http://localhost:3000/_v2/` — new v2 Home
- `http://localhost:3000/_v2/services` — v2 Services
- `http://localhost:3000/_v2/_showcase` — full component showcase (every primitive, every section)

Any URL under `/_v2/*` renders the v2 version; legacy `/` (no prefix) is untouched until the env flag flips.

---

## Content blockers — founder to resolve before production flip

Search the codebase for `TODO:` comments. Key items:

1. **Pillar copy** (Health Technologies / Defense Systems / Agentic Ops) — 3 paragraphs, ~80-100 words each. Currently drafted placeholder in `Home.tsx` and `Services.tsx`.
2. **"Why vendor-neutral" manifesto** on Home InkSection — 3 paragraphs, ~150-200 words. Drafted in `Home.tsx`.
3. **Case studies** — 3 cases on Home + industry-specific on IndustryDetail pages. Currently anonymized drafts; need real cases or decide to keep anonymized.
4. **Named-practitioner bios** on About page — currently generic placeholder slots (no fake names shipped). Need real names, roles, 80-120 word bios.
5. **Stats numbers** (50+ workshops, 12 industries, 4.9/5, 8hrs) — validate against actual figures.
6. **Testimonials** (3 on Home, 3 on Workshops) — currently drafted placeholder; replace with real quotes before flip.
7. **Service pricing** — inline map in `ServiceDetail.tsx` with drafted "from $X,XXX" figures. Validate.
8. **Article content** — `INSIGHTS` data in `lib/data.ts` has no `content` field; article bodies render a placeholder paragraph. Add real content or mark articles draft/WIP.

You can flip to production with these placeholder still in place (the site will render), but they should be replaced before the cutover is announced.

---

## Production cutover — step-by-step

### Step 1 — Commit the design + plan + handoff docs (if not yet)

```powershell
cd "C:\Users\Aaron\omniscient website\omniscientai"
git status
# Verify docs/plans/*.md are committed
```

All currently committed as of this handoff.

### Step 2 — Merge `feat/v2-redesign` to main

Either via PR (recommended for review) or direct merge:

```powershell
git checkout main
git merge feat/v2-redesign
```

**No deployment happens yet** — production still shows the dark-theme site because `VITE_USE_V2` defaults to `false`.

### Step 3 — Staging deploy with v2 flag ON

On your deploy platform (Render or Google Cloud Run, per `render.yaml` / `app.yaml`):

1. Create a staging environment pointing at `main` (if one doesn't exist already).
2. Set env var `VITE_USE_V2=true` for the staging environment only.
3. Trigger a deploy of `main`.

### Step 4 — Staging QA

Walk through every URL on staging. Checklist per page:

**Critical path (Home, Services, Workshops, Book, Contact):**
- [ ] Page renders without errors
- [ ] Fonts load (Inter headings, JetBrains Mono for numerals)
- [ ] Brand graphic image loads in hero
- [ ] Primary + secondary CTAs fire the correct URLs
- [ ] Forms submit end-to-end (Contact, Book, Custom Workshop, Quiz completion, ROI calculation)
- [ ] Responsive at 375/768/1024/1440 widths
- [ ] Keyboard nav works (Tab through, visible focus rings)
- [ ] Nav + Footer render correctly

**Visual spot checks (per design doc §8.1):**
- [ ] ~70% paper / 20% ink / 8% blue proportion on each page
- [ ] Max 1 InkSection per long page (Home, Services, About)
- [ ] Max 1 `INTELLIGENCE // CONNECTIVITY // INNOVATION` tagline per page
- [ ] No emoji in marketing copy
- [ ] Sentence case on body / buttons; UPPERCASE only on eyebrows
- [ ] No gradient washes

**Lighthouse** (Chrome DevTools → Lighthouse tab, mobile profile):
- [ ] Home: Perf / A11y / Best Practices / SEO all ≥ 90
- [ ] Services: ditto
- [ ] Workshops: ditto
- [ ] Book: ditto

If any drop below 90, the most likely culprit is the brand PNG sizes. Convert to WebP as a Phase 13 polish.

**Redirects** (test with curl or browser with dev-tools Network tab showing 301 status):
- [ ] `staging.url/document-analyser` → 301 → `/services`
- [ ] `staging.url/voice-consultant` → 301 → `/services`
- [ ] `staging.url/playground` → 301 → `/`

### Step 5 — Production flip

Assuming staging QA is clean:

1. On production deploy environment: set `VITE_USE_V2=true`.
2. Trigger a production deploy.
3. Monitor for 30 minutes:
   - Sentry error rate (baseline vs. current)
   - GA live view — traffic unaffected
   - Manual: visit homepage, book a call, submit contact form

**If anything breaks:** set `VITE_USE_V2=false` on production, redeploy (3-minute rollback). Old code is still intact.

### Step 6 — 24-hour stability watch

Monitor thresholds:

| Metric | Alarm threshold |
|--------|------------------|
| Sentry error rate | +50% vs 7-day median |
| 404 rate | +20% |
| Contact + Book submissions | -25% week-over-week |
| GA bounce rate | +15% |

If any alarm fires, diagnose. Rollback via env flag if structural.

### Step 7 — Legacy cleanup PR (T+24h, assuming stable)

On a fresh branch `feat/v2-cleanup`:

```powershell
git checkout -b feat/v2-cleanup

# Delete legacy pages (will be replaced by pages-v2)
git rm -r client/src/pages

# Rename v2 → canonical
git mv client/src/pages-v2 client/src/pages
git mv client/src/components-v2/brand client/src/components/brand-v2
git mv client/src/components-v2/layout client/src/components/layout-v2
git mv client/src/components-v2/sections client/src/components/sections-v2
git mv client/src/components-v2/ui client/src/components/ui-v2
```

Then:
- Manually edit all imports: `@/components-v2/*` → `@/components/*-v2/*` (or drop the `-v2` suffix entirely if you're confident nothing clashes with shadcn/ui)
- Delete the legacy `components/` subfolders that are no longer used (keep `SEO.tsx`, `ErrorBoundary.tsx`, `Map.tsx`, `ui/` shadcn primitives — audit during this task)
- Delete `client/src/lib/theme-v2.ts` and the `.v2` scope wrapper — tokens become canonical under `:root`
- Strip out the `USE_V2` flag and router branching in `App.tsx`
- Remove legacy dark-theme tokens from `index.css`
- Remove the `.v2` class from `Layout` components

Run `pnpm check` + `pnpm build` + `pnpm test --run` to verify zero regressions. Open PR. The diff should be LARGE (lots of deletes) but visually produce zero change.

**Do NOT start this until the v2 flip has been stable in production for 24 hours.**

---

## Phase 13 — Ship gate (after cleanup)

| Task | What | Where |
|------|------|-------|
| 13.1 | OG social share image (1200×630) at `client/public/og-default.png` | Compose using `brand-graphic-horizontal.png` on ink bg + tagline |
| 13.2 | Submit new sitemap to Google Search Console | `https://search.google.com/search-console` |
| 13.3 | WebP conversion for brand PNGs if Lighthouse <90 | Use `sharp` CLI or `imagemin` |
| 13.4 | Self-host Inter + JetBrains Mono if font FOUT visible | Drop into `client/public/fonts/`, swap `@import` for `@font-face` |
| 13.5 | Monitoring runbook | `docs/runbook/v2-monitoring.md` |
| 13.6 | Retrospective after 2 weeks | `docs/plans/2026-xx-xx-v2-redesign-retro.md` |

None are blockers for the cutover itself.

---

## Rollback path

**Fastest (3 min):** set `VITE_USE_V2=false` on production env, redeploy. Site returns to dark-theme legacy.

**If env flag won't propagate:** platform-level rollback to the last known-good deploy (both Render and Cloud Run support this).

**Both paths work** because the legacy code (`client/src/pages/*`, `client/src/components/*`) is fully intact until Step 7 cleanup. Don't run Step 7 until you're confident.

---

## Commits on `feat/v2-redesign` (74 total, newest first)

Final commits: `3c072d0 deploy: add 301 redirects for cut tools + expand sitemap`
...and back through each phase's work.

Run `git log --oneline feat/v2-redesign ^main` to see them all.

---

## Questions / issues during cutover

Send a message with:
- Which step you're on (1-7)
- What you're seeing (error, visual issue, unexpected behavior)
- Screenshot if relevant

I can diagnose and adjust anything.
