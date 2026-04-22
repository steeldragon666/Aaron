# OmniscientAI Website Redesign — Design Document

**Date**: 2026-04-22
**Status**: Approved; pending implementation plan
**Author**: Aaron (steeldragon666) with Claude
**Scope**: Complete redesign of `omniscientai.io` — all pages, new design system, full aesthetic pivot

---

## 1. Context & motivation

The current `omniscientai.io` is a React + Vite + TailwindCSS site with 22 pages, styled with a dark theme (cyan `#12B5CB` + tangerine accents), Space Grotesk headings, glass-card effects, retro grid backgrounds, and Framer Motion throughout. The codebase carries comments marking a prior "Dramatic Visual Redesign" attempt on `Home.tsx`.

A comprehensive brand design system has been commissioned externally and delivered as `Omniscient AI Design System.zip`. The new system is a **complete aesthetic reversal**:

- Dark → Paper-first (white canvas, near-black ink, electric blue accent)
- Retro-grid glow effects → Flat Bauhaus geometry
- Space Grotesk → Inter
- 16px radii → Tight 6-8px radii
- Gradient-heavy → Zero gradient washes
- "Dramatic visual" → "Confident, plainspoken, slightly swaggering"

The business is simultaneously expanding its remit beyond AI training for SMEs into **health technologies**, **defense hardware/software**, and **agentic ops tooling**. The visual identity must signal a boutique heavy-hitter firm — small team, big shoulders — not a startup, not an enterprise vendor, something between.

## 2. Decisions (brainstorming outcomes)

| Question | Decision |
|----------|----------|
| Motivation | **F — Complete strategic rebuild**. Keep only tech stack. |
| Positioning | Provided design system — boutique heavy-hitter; flat geometric; tri-tone ink/blue/paper |
| Scope | **Full site migration** (B). All pages redesigned before launch. |
| Interactive tools | **Keep Quiz + ROI Calculator** (strong lead-gen). Cut Document Analyser, Voice Consultant, Playground. |
| Brand graphic | **Static PNG** in hero corners (provided in design system zip). |
| Home positioning | **Tease the breadth, sell the training** — Home leads with AI training for SMEs, mentions 4 practice areas (Training / Health / Defense / Agentic Ops) in secondary section. |
| Execution approach | **B — New scaffold, port content**. Fresh `pages-v2/` + `components-v2/` built from provided UI kit; router flag flips at cutover. |

**Pages in v2 (20 total):**
Home, Services, Service Detail, Industries, Industry Detail, Workshops, Workshop Detail, About, Approach, Contact, Book, Custom Workshop, Insights, Insight Article, Privacy Policy, Terms, NotFound, Component Showcase (dev), AI Readiness Quiz, ROI Calculator.

**Removed entirely:** Document Analyser, Voice Consultant, Playground. 301 redirects preserve SEO equity.

**Removed components:** `GenerativeNeuralMesh`, `CustomCursor`, `ChatWidget`, `AIChatBox`, `AIOssistant`, `ManusDialog`, `LeadGate` (design system forbids floating chat bubbles and cursor effects).

## 3. Design system foundations

Source: `Omniscient AI Design System.zip` — delivered with `README.md`, `SKILL.md`, `colors_and_type.css`, brand assets, and reference UI kit components.

### 3.1 Palette (70/20/8/2 proportions)

| Role | Token | Hex |
|------|-------|-----|
| Primary text / illustration disc | `--ink` | `#0F1115` |
| Signature electric blue | `--blue` | `#2F7BFF` |
| Pressed / small-type blue | `--blue-deep` | `#1C4FD6` |
| Node glow / focus ring | `--blue-glow` | `#7AA8FF` |
| Canvas | `--paper` | `#FFFFFF` |
| Secondary surface | `--paper-2` | `#F4F6F9` |
| Hairline divider | `--line` | `#E4E7EC` |
| Secondary text | `--ink-2` | `#2A2F37` |
| Metadata | `--ink-3` | `#5B6270` |
| Success / Warn / Danger | — | Product UI only; never in marketing |

**Proportion enforcement**: ~70% paper, 20% ink, 8% blue, 2% glow on any given screen. Blue is a scalpel, not a paint roller. Hero blocks and CTAs earn the blue; body type stays ink.

### 3.2 Typography

- **Display + UI face**: Inter (variable, 400-800). Substitution for a purchased face — swap when/if provided.
- **Mono face**: JetBrains Mono. Used for code, numeric tables, hashtag strings, and `MonoBadge` elements.
- **No serifs.** The brand is flat-geometric; serifs fight the illustration.

Scale (see `colors_and_type.css` for canonical tokens):

| Role | Size | Weight | Tracking | Leading |
|------|------|--------|----------|---------|
| Hero | clamp(48px, 7vw, 96px) | 700 | -0.03em | 0.95 |
| H1 | 56px | 700 | -0.025em | 1.05 |
| H2 | 36px | 700 | -0.02em | 1.1 |
| H3 | 22px | 600 | -0.02em | 1.1 |
| Body | 17px | 400 | 0 | 1.55 |
| Eyebrow | 12px | 600 | 0.14em | 1.2 (UPPERCASE) |

### 3.3 Voice & copy rules

- **"We"** for Omniscient; **"you / your team"** for reader; **"I"** only for founder quotes.
- Short sentences. Declarative. Cut adverbs. Lead with verb.
- Sentence case for body, buttons, card titles.
- `UPPERCASE` only for eyebrows and the signature `INTELLIGENCE // CONNECTIVITY // INNOVATION` tagline — tracked 0.14em, one per page max.
- Title Case only for proper nouns and program names.
- **No emoji** in product or marketing copy (social hashtags exempt).
- `→` arrow as signature CTA marker.
- Proof points to surface early: vendor-neutral, Melbourne, boutique/heavy-hitter, three practice areas.

### 3.4 Visual rules (non-negotiable)

- **No gradient washes.** Single exception: 2-stop blue → blue-deep fill on badges / pressed button states.
- **No skeuomorphism, no soft 3D, no airbrush.** Flat geometric DNA.
- **No floating chat bubbles. No floating CTAs.** Single anchored footer, sticky translucent top nav.
- **No custom cursors.** Breaks the flat rule.
- **Tight radii.** Cards 8px, buttons 6px, inputs 6px, pills 999px. Never 16px+ on product chrome.
- **Hairline borders.** 1px `--line` dividers; 1.5px `--ink` for emphasised card outlines.
- **Section break pattern.** Flip one section to `--ink` (near-black) with inverted tokens inside — this is the primary pacing device. Not gradients, not photos.
- **Hero composition.** 55/45 copy-graphic asymmetry lifted from the brand's social hero card.
- **Brand graphic.** Drop `brand-graphic-circles.png` or `brand-graphic-horizontal.png` in hero corners at 20-40% viewport width. Never recolor. Never recompose.
- **Animation.** 160-220ms base, `cubic-bezier(0.2, 0.9, 0.2, 1)`. No bounces, no elastic. Hover: 1px lift + darken. Press: drop lift + 4% darken. Node pulse (2s loop) reserved for hero only.

### 3.5 Product UI allowances

On tool pages (Quiz, ROI Calculator) and in-product empty/loading states, the design system permits:

- Semantic accents — `--success`, `--warn`, `--danger` — for status and validation.
- 4px blue-dot grid backgrounds in empty states and skeleton screens.
- Denser spacing (4/8px) than marketing (which uses 24/32/48/64).

These allowances **do not extend to marketing pages.**

## 4. Technical architecture

### 4.1 Folder structure (during build phase)

```
client/src/
├── index.css                  ← current dark-theme tokens (UNTOUCHED)
├── styles/
│   └── omniscient.css         ← NEW — ported from colors_and_type.css, scoped to .v2
├── App.tsx                    ← router; env-flag-driven V2Routes vs LegacyRoutes
├── pages/                     ← current pages (UNTOUCHED until cutover)
├── pages-v2/                  ← NEW home for redesigned pages
├── components/                ← current components (UNTOUCHED until cutover)
├── components-v2/
│   ├── brand/                 ← Logo, BrainGraphic, TaglineBar
│   ├── layout/                ← Nav, Footer, Layout, Container, Section, InkSection
│   ├── ui/                    ← Button, Card, FeaturedCard, Eyebrow, Display, Lede,
│   │                            MonoBadge, CTALink, Input, Textarea, Select,
│   │                            Slider, RadioCard, CheckboxCard
│   └── sections/              ← HeroSplit, HeroCentric, PillarGrid, CaseGrid,
│                                WorkshopCardGrid, StepStack, FAQAccordion,
│                                TestimonialStrip, StatsRow, CTAStrip,
│                                BookingForm, ContactForm, ArticleHeader, ArticleBody
└── lib/
    └── theme-v2.ts            ← scope flag + conditional theme class
```

### 4.2 Token scoping strategy

All new tokens live inside a `.v2` class wrapper in `omniscient.css`:

```css
.v2 {
  --ink: #0F1115;
  --blue: #2F7BFF;
  /* ... */
}
```

The v2 `Layout` component wraps page children in `<div className="v2">` — this is the ONLY place the scope class is applied. Dark-theme tokens in `index.css` remain untouched; they apply wherever `.v2` is not present.

### 4.3 Tailwind v4 integration

`index.css` gets additive `@theme inline` entries that reference the new tokens. This makes utilities like `bg-paper`, `text-ink`, `border-line`, `font-display` work in v2 components. Because Tailwind reads CSS custom properties at resolve time, scope is automatically respected.

### 4.4 Router architecture

```tsx
const USE_V2 = import.meta.env.VITE_USE_V2 === "true";
return <Switch>{USE_V2 ? <V2Routes /> : <LegacyRoutes />}</Switch>;
```

In dev, both mount under path prefixes (`/` = legacy, `/v2/*` = new) to support side-by-side comparison during development.

### 4.5 Custom utility classes

Five utility classes in `omniscient.css` for patterns Tailwind doesn't cover:

- `.v2 .eyebrow` — 12px / 600 / UPPERCASE / tracking 0.14em
- `.v2 .display` — clamp(48px, 7vw, 96px) / 700 / -0.03em / 0.95
- `.v2 .lede` — 20px / 1.45 / `--ink-600`
- `.v2 .mono-badge` — JetBrains Mono / 12px / hairline border
- `.v2 .ink-section` — flip-to-ink section pattern (bg: ink, inverts nested tokens)

## 5. Component library (23 components)

### 5.1 Brand layer (3)

- `Logo` — 3 variants: stacked, horizontal, mark-only. Uses imported PNG assets.
- `BrainGraphic` — static PNG connectome. Props: `variant` (circles / horizontal), `size` (hero / section / corner).
- `TaglineBar` — `INTELLIGENCE // CONNECTIVITY // INNOVATION` signature. Max 1 per page.

### 5.2 Layout layer (6)

- `Nav` — sticky translucent, `backdrop-filter: saturate(1.2) blur(14px)`, 1px `--line` bottom border.
- `Footer` — 3-column with wordmark. Uses `logo-horizontal-with-graphic.png`.
- `Layout` — wraps v2 pages, adds `.v2` class, injects Nav + Footer.
- `Container` — max-width 1240px centered. Replaces inline max-widths.
- `Section` — default paper section with 96px vertical rhythm (48px mobile).
- `InkSection` — flip-to-ink variant. 1 per long page max.

### 5.3 UI primitives (14)

- `Button` — Primary (blue fill) + Secondary (ink outline) + Ghost. 6px radius. 1px lift on hover. `→` arrow support.
- `Card` — Flat bordered, 8px radius, `--line` border, `--shadow-1` on hover only.
- `FeaturedCard` — Ink-flipped variant. For one-per-grid emphasis.
- `Eyebrow`, `Display`, `Lede` — typography primitives wrapping utility classes.
- `MonoBadge` — small hairline-border mono text (pricing, duration, stats).
- `CTALink` — underline-on-hover with `→`.
- `Input`, `Textarea`, `Select` — form primitives. 6px radius. `--blue-glow` focus ring.
- `Slider` — for ROI Calculator. 6px track, `--ink-100` bg, `--blue` fill, 16px thumb with `--shadow-1`.
- `RadioCard`, `CheckboxCard` — large-tap-target Card-styled variants for Quiz question steps.

### 5.4 Section patterns (14)

Composable sections, 4-7 per page:

- `HeroSplit` — 55/45 copy-graphic.
- `HeroCentric` — stacked copy over optional narrow graphic.
- `PillarGrid` — 4-up Training / Health / Defense / Agentic Ops.
- `CaseGrid` — 3 case tiles, 1 featured.
- `WorkshopCardGrid` — 3-up with pricing, duration, `→` CTA.
- `StepStack` — numbered steps with ink-line dividers.
- `FAQAccordion` — hairline dividers, `+` toggle.
- `TestimonialStrip` — 3 horizontal quotes (no stars — too consumer).
- `StatsRow` — 4-column mono numerals.
- `CTAStrip` — book-a-call prompt, paper or ink variant.
- `BookingForm` — multi-step wizard.
- `ContactForm` — Card on paper-2 bg.
- `ArticleHeader`, `ArticleBody` — long-form.

## 6. Page structure (20 pages)

### 6.1 Marketing core (10)

- **Home**: Nav + HeroSplit + TaglineBar + PillarGrid + InkSection (manifesto) + WorkshopCardGrid + CaseGrid + StatsRow + TestimonialStrip + CTAStrip + Footer.
- **Services**: HeroCentric + service cards + PillarGrid + InkSection + CTAStrip.
- **Service Detail**: HeroSplit + what-you-get + StepStack + pricing MonoBadge + FAQ + CTAStrip.
- **Industries**: HeroCentric + 4-up industry cards + CaseGrid + CTAStrip.
- **Industry Detail**: HeroSplit + use cases + featured case + WorkshopCardGrid (filtered) + CTAStrip.
- **Workshops**: HeroCentric + WorkshopCardGrid (all) + custom workshop CTA + TestimonialStrip + CTAStrip.
- **Workshop Detail**: HeroSplit (pricing/duration/format as MonoBadges) + Who it's for checklist + 4-module StepStack + outcomes + FAQ + sticky BookingForm sidebar.
- **About**: HeroCentric + story + 4-value FeaturedCard grid + practitioner bios + InkSection + CTAStrip.
- **Approach**: HeroCentric + StepStack (4-phase methodology) + principles grid + CTAStrip.
- **Contact**: HeroCentric (narrow) + ContactForm + details sidebar + hours MonoBadge.

### 6.2 Conversion actions (2)

- **Book**: 3-step booking wizard. Minimal chrome, sticky summary Card.
- **Custom Workshop**: HeroCentric + requirements form + "How we scope" StepStack + CTAStrip.

### 6.3 Content (2)

- **Insights**: HeroCentric + category filter + featured FeaturedCard + article grid.
- **Insight Article**: ArticleHeader + ArticleBody (65-75ch line length) + author bio Card + related grid + CTAStrip.

### 6.4 Tools — product UI (2)

- **AI Readiness Quiz**: multi-step wizard. Category badges + progress bar + RadioCard/CheckboxCard per step + result screen with score + Book CTA. Semantic accents and dot-grid backgrounds permitted.
- **ROI Calculator**: 2-column. Inputs panel (sliders, industry select, numerics) + results panel (live MonoBadge stats, featured savings number in Display size).

### 6.5 Legal & utility (4)

- **Privacy Policy, Terms**: HeroCentric narrow + ArticleBody + last-updated MonoBadge.
- **NotFound**: Centered Display "404" + lede + back CTAs + corner BrainGraphic.
- **Component Showcase** (dev-only): gallery of every v2 component. Not in nav.

### 6.6 Copy porting strategy

Two passes:
1. **Direct port (~70%)**: Existing body copy dropped into new sections verbatim; casing fixed (Title Case → sentence case).
2. **Rewrite (~30%)**: Headlines, eyebrows, CTAs — rewritten to match "confident, plainspoken, slightly swaggering" voice.

### 6.7 New copy required

- 3 pillar descriptions (Health / Defense / Agentic Ops): 80-100 words each.
- "Why vendor-neutral" manifesto (Home InkSection): 150-200 words.
- 3 case studies (if no real ones exist): 400-600 words each. Fallback: generic engagement summaries.
- Named-practitioner bios: 80-120 words each.
- New 404 copy: 40 words.

## 7. Router switchover plan

### 7.1 URL preservation (1:1 map)

All 16 core marketing URLs preserved unchanged. Quiz and ROI Calculator URLs preserved. Three tool URLs get 301 redirects:

| Current | New | Status |
|---------|-----|--------|
| `/` through `/terms` | unchanged | Redesigned |
| `/quiz`, `/roi-calculator` | unchanged | Redesigned |
| `/document-analyser` | — | 301 → `/services` |
| `/voice-consultant` | — | 301 → `/services` |
| `/playground` | — | 301 → `/` |

Redirects served at platform level (`render.yaml` / `app.yaml`).

### 7.2 Cutover sequence

1. **Pre-flight** (T-60 min): all 20 v2 pages merged, QA complete, Lighthouse baseline captured.
2. **Staging deploy** (T-30 min): `VITE_USE_V2=true` on staging, smoke-test all 20 URLs.
3. **Production flip** (T-0): deploy with env flag on. Monitor 30 min for Sentry errors, 404 spikes, form drops.
4. **Cleanup** (T+24h, stable): delete `pages/`, `components/`, `index.css` tokens; rename `-v2` suffixes off; remove env flag and router branch. Visually identical PR.

### 7.3 Rollback path

If production breaks after flip: flip `VITE_USE_V2=false` → redeploy (~3 min recovery). Old code remains intact until Stage 4 cleanup, so rollback is always an env change — never a revert.

### 7.4 Asset migration

All design system PNG assets land in `client/public/brand/`:
- `logo-brain-stacked.png`, `logo-horizontal-with-graphic.png`, `logo-mark-circle.png`
- `brand-graphic-circles.png`, `brand-graphic-horizontal.png`

Favicon from `logo-mark-circle.png` (16/32/180/512). OG image from `brand-graphic-horizontal.png` on ink background. Manifest theme color `#0F1115`.

## 8. QA & testing

### 8.1 Per-page checklist (gating)

- Visual: 70/20/8/2 proportion; max 1 tagline; max 1 InkSection; no emoji in marketing; sentence case; brand graphic unrecolored; no gradients.
- Type: Inter loaded; 65-75ch line length; fluid hero clamp; distinct H1/H2/H3.
- Interaction: cursor-pointer; translateY(-1px) hover (no scale); visible focus ring; `→` on primary CTAs.
- Responsive: 375/768/1024/1440 pass; nav collapses < 768; HeroSplit stacks on mobile.
- A11y: 4.5:1 contrast; alt text; form labels wired; `prefers-reduced-motion` respected; keyboard nav; ARIA labels; skip-to-content.
- Performance: Lighthouse ≥ 90 across Perf/A11y/SEO/Best Practices; LCP < 2.5s; CLS < 0.1; WebP with JPG fallback; lazy-load non-hero.

### 8.2 Testing layers

- **Unit** (Vitest, existing): utility logic, button states, form validation, slider clamping.
- **Visual regression**: `ComponentShowcase` page as manual surface. Storybook deferred post-launch.
- **Cross-browser smoke**: Chrome, Safari, Firefox, Edge on Mac + iOS Safari.
- **Forms**: end-to-end submission on staging for Contact, Book (3 steps), Custom Workshop, Quiz, ROI Calculator.
- **SEO**: post-flip Screaming Frog crawl; zero 404s on indexed URLs; JSON-LD validates.

### 8.3 Post-flip monitoring (72h)

| Metric | Alarm threshold |
|--------|------------------|
| Sentry error rate | +50% vs 7-day median |
| 404 rate | +20% |
| Contact + Book submissions | -25% week-over-week |
| Bounce rate (GA) | +15% |
| Organic impressions | Monitor daily for 2 weeks |

Any alarm fires in 72h → diagnose before cleanup. Structural issue → env-flag rollback, investigate.

### 8.4 Ship gate

1. All 20 pages pass QA checklist.
2. All forms tested end-to-end on staging.
3. Lighthouse ≥ 90 on Home, Services, Workshops, Book.
4. Redirects verified as 301.
5. Sitemap regenerated; Search Console updated.
6. Rollback path rehearsed.

## 9. Out of scope (explicit non-goals)

- Backend / API changes. Forms continue posting to existing endpoints.
- Database schema changes.
- Content management system. Copy lives in page components; a CMS is a future consideration.
- Internationalization. English-only. Australian English spelling where relevant.
- Dark mode toggle for v2. The brand is paper-first. If a dark variant is ever needed, it's the single-section-flip pattern, not a full dark theme.
- Blog authoring tooling. Insights articles remain hand-authored Markdown/TSX until there's volume to justify tooling.
- Analytics rework. Existing GA / tracking continues; no new instrumentation in this phase.
- Storybook or visual regression automation. `ComponentShowcase` page is the manual surface; automation is a follow-up.

## 10. Open questions for implementation

These are flagged to resolve during writing-plans / implementation, not brainstorming:

1. **Mobile nav design** — the provided UI kit only shows desktop Nav. Hamburger menu pattern to be designed in Phase 1 of implementation, following flat Bauhaus rules (no drawer scrim gradients; ink-flip full-screen or hairline-border dropdown).
2. **Case studies** — whether real case content exists. If not, the `CaseGrid` on Home either gets generic engagement summaries (no named clients) or is replaced with a featured WorkshopCardGrid tile.
3. **Pillar copy** — Health / Defense / Agentic Ops descriptions. Aaron to provide positioning, or Claude drafts during Home implementation for review.
4. **Named-practitioner bios** — required for About page. List of practitioners + bios needed from Aaron.
5. **Purchased display font** — if Neue Haas Grotesk, GT America, or Söhne has been licensed, drop files in `client/public/fonts/` before Phase 2 and swap `@import` for `@font-face`. Otherwise Inter ships.
6. **Lighthouse threshold** — 90 is the target; drop to 85 only if brand-graphic PNG size requires it. WebP conversion should keep us at 90.
7. **AIChatBox / LeadGate** — removed in v2 per design system rules. Decide if a non-floating re-implementation is ever desired (e.g. inline chat on Contact page), or permanently cut.

## 11. Success criteria

- All 20 pages ship with visual fidelity to the design system (70/20/8/2; flat geometric; no forbidden patterns).
- No regression in Contact / Book form submissions (week-over-week) after flip.
- Lighthouse ≥ 90 on critical paths.
- Zero 404s on previously-indexed URLs.
- Site positioning visibly shifts from "training consultancy" to "boutique heavy-hitter firm with broad remit" — validated by founder review.
- Codebase simpler post-cleanup: old dark-theme components removed, single design system in play.

## 12. Next step

This document is the approved design. The next step is the **implementation plan**, produced by the `superpowers:writing-plans` skill — a phase-by-phase task breakdown with acceptance criteria per phase, ordered for incremental delivery and reviewability.
