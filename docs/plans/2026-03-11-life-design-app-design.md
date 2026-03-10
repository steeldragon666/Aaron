# Life Design App — Product Design Document

**Date:** 2026-03-11
**Status:** Approved

## Vision

A cross-platform well-being companion that helps people intentionally design their lives by tracking 8 health dimensions, surfacing patterns through visual dashboards and AI-powered insights, and adapting depth to the user's needs.

## Target Audience

Self-improvement-minded adults 25-45, building as a product for others (not personal tool).

## Platforms

- Web: Next.js (dashboard, marketing, web check-in)
- Mobile: Expo/React Native (primary daily experience — iOS + Android)

---

## Core Features

### 1. Daily Check-In (Adaptive Depth)

**Quick mode (~30s):**
- Overall mood slider (1-10)
- Swipeable cards to score each dimension (1-10)
- Mentor reaction

**Deep mode (~5min, triggered adaptively):**
- App detects low/unusual scores or patterns
- Offers guided reflection prompts
- Optional encrypted journal note

**8 Life Dimensions:**
1. Mental Health
2. Physical Health
3. Financial Health
4. Spiritual Health
5. Sexual Health
6. Personal Growth
7. Asset/Material Health
8. Social/Relational Health

### 2. AI Mentor System

**Mentor types:**
- Pre-built personas (famous people, historical figures, musicians, leaders)
- Custom mentors (user-described personalities)
- Hybrid mentors (blend 2-3 personas with adjustable weight slider)

**Interaction modes:**
- Check-in reactions — mentor comments on scores in character after each check-in
- On-demand chat — conversational UI to ask advice, get pep talks, talk through problems
- Mentor has context of user's check-in history and trends

**Persona engine:**
- LLM system prompt encoding speech patterns, values, catchphrases, motivational style
- Hybrid blending via weighted system prompt composition
- Safety guardrails: no medical/financial/legal advice, content filtering, "AI-generated inspired by" disclaimer

### 3. Dashboard & Analytics

**Visual dashboards:**
- Wheel of Life radar chart (7-day / 30-day / all-time toggle)
- Per-dimension trend lines (sparklines)
- Streak counter
- Weekly/monthly summaries

**AI-powered insights:**
- Trend detection (3+ day consistent changes)
- Cross-dimension correlation (e.g., physical health predicts mental health with 2-day lag)
- Integration-enriched patterns (calendar busyness → mental health drops)
- Delivered through mentor's voice

**Processing:**
- Nightly batch job via Supabase Edge Functions
- LLM translates statistical findings into natural language
- Runs on aggregated metrics only (never encrypted text)

### 4. Integration Layer

| Dimension | Integrations | Data Pulled |
|-----------|-------------|-------------|
| Financial | Plaid, Stripe, Akahu | Spending categories, balances, savings rate |
| Physical | Strava, Apple Health, Google Fit, Fitbit, Oura | Steps, workouts, sleep, heart rate |
| Mental | Google Calendar, screen time APIs | Busyness, focus time |
| Social | Instagram, contacts API | Engagement frequency |
| Personal Growth | Gmail, Kindle/reading APIs | Learning activity |
| Spiritual | Calendar events, Headspace | Practice frequency |
| Asset | Property APIs, crypto wallets, investment platforms | Net worth tracking |
| Sexual | Manual tracking only | Self-reported |

**Design principles:**
- Zero integrations required — works fully on check-ins alone
- Progressive enrichment — each source makes insights smarter
- Metrics only — store computed summaries, not raw data (reduces liability)
- User controls everything — connect/disconnect anytime

---

## Architecture

### Monorepo Structure

```
life-design/
├── apps/
│   ├── web/          # Next.js
│   └── mobile/       # Expo/React Native
├── packages/
│   ├── core/         # Shared TS: models, scoring, validation
│   ├── ai/           # Mentor persona engine, insight generation
│   └── ui/           # Shared design tokens, theme
├── supabase/         # DB migrations, edge functions, RLS policies
└── docs/
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Web | Next.js 14+ (App Router) |
| Mobile | Expo / React Native |
| Shared Logic | TypeScript (Turborepo monorepo) |
| Backend / DB | Supabase (Postgres + Auth + Edge Functions + Realtime) |
| AI / LLM | Claude API |
| Integrations | OAuth + background sync via Edge Functions |
| Encryption | Client-side E2E for journals/chat; queryable columns for scores |
| Hosting | Vercel (web) + EAS (mobile builds) |
| Monorepo | Turborepo |

### Data Model

| Entity | Key Fields |
|--------|-----------|
| User | id, email, display_name, created_at, subscription_tier |
| CheckIn | id, user_id, date, overall_mood (1-10), duration_type (quick/deep) |
| DimensionScore | id, checkin_id, dimension (enum), score (1-10), note (encrypted) |
| Mentor | id, name, type (preset/custom/hybrid), persona_prompt, sources[] |
| UserMentor | user_id, mentor_id, blend_weight, is_active |
| MentorMessage | id, user_id, mentor_id, trigger (checkin/chat), content, created_at |
| Insight | id, user_id, type (trend/correlation/alert), content, dimensions[], created_at |
| Integration | id, user_id, provider, access_token (encrypted), last_sync, status |
| IntegrationMetric | id, integration_id, dimension, metric_name, value, period_start, period_end |

### Privacy & Encryption (Hybrid Model)

- Dimension scores: stored as queryable integers (enables server-side analytics)
- Journal notes & chat messages: encrypted client-side before storage (zero-knowledge)
- Integration tokens: encrypted at rest
- Mentor persona prompts: not encrypted (not sensitive)
- Auth: Supabase Auth (email + Google + Apple social logins)
- Row-level security on all user data

### Monetisation

Not determined yet. Architecture supports adding a billing layer (Stripe) later with subscription tiers gating features like AI insights, mentor chat, or integration count.

---

## User Flows

### Onboarding
1. Sign up (email / Google / Apple)
2. Select/reorder life dimensions
3. Choose or create mentor (or skip)
4. Guided first check-in

### Daily Check-In
1. Open app → overall mood slider
2. Quick score each dimension (swipeable cards)
3. Adaptive: app detects unusual score → offers reflection prompt
4. Optional journal note
5. Mentor reacts
6. See today's snapshot

### Key Screens
- **Home**: Today's check-in + mentor message
- **Dashboard**: Wheel of Life + trends + insight cards
- **Mentor**: Active mentor, chat interface, switch/edit mentor
- **Integrations**: Connected sources, connect new
- **Profile/Settings**: Dimension customisation, notifications, privacy, data export
