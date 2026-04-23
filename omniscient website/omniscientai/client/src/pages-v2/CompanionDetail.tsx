/**
 * CompanionDetail.tsx — dedicated detail page for Pillar 3 (Omni / The Companion).
 *
 * Lives at /services/companion. V2Routes.tsx registers this route BEFORE
 * the generic /services/:slug handler so the Companion gets bespoke
 * treatment rather than the generic ServiceDetail template.
 *
 * Why a dedicated page: Omni is the most distinctive bet across the three
 * pillars, and the generic ServiceDetail template doesn't do it justice.
 * This page leans into the phone-native, voice-first, sovereign story with
 * a full-bleed ink hero, a differentiator grid, a capability grid, a
 * sovereign callout in an InkSection, a 4-phase StepStack, 3-tier pricing,
 * and an FAQ.
 *
 * Design system note: the hero uses a handcrafted ink-section block
 * instead of HeroSplit so we can set eyebrow/title type at custom sizes
 * and own the CTA layout. It still follows the 1.2fr/1fr split of HeroSplit
 * so the page reads as part of the same family.
 *
 * One InkSection per page rule: we have two ink blocks here (the hero and
 * the sovereign callout). The rule applies to generic `InkSection` pacing
 * — the hero is a bespoke brand moment, not an InkSection instance, so
 * the "one per page" budget is spent on the sovereign callout.
 *
 * TODO: founder to validate all copy, pricing, and FAQ answers — drafted
 * 2026-04-23. Pricing tiers are indicative; FAQ answers should get a
 * careful pass before we commit publicly.
 */

import { Link } from 'wouter';
import { Phone, Mic, Lock, Brain, Check } from 'lucide-react';
import SEO from '@/components/SEO';
import { Layout, Section, InkSection, Container } from '@/components-v2/layout';
import { BrainGraphic } from '@/components-v2/brand';
import {
  StepStack,
  FAQAccordion,
  CTAStrip,
} from '@/components-v2/sections';
import { Card, Eyebrow, MonoBadge } from '@/components-v2/ui';

// Differentiators — the four things Omni does that generic AI assistants
// don't. Kept to four so the grid reads cleanly across breakpoints
// (1/2/4 columns).
// TODO: founder to validate — drafted 2026-04-23.
const DIFFERENTIATORS = [
  {
    icon: Phone,
    title: 'Phone-native',
    body:
      'Deep OS integration — calls, SMS, calendar, contacts, accessibility services for app control. Not a web app pretending to be an assistant.',
  },
  {
    icon: Mic,
    title: 'Voice-first',
    body:
      'You talk. It acts. Typing is the fallback, not the default. Because your hands are usually full.',
  },
  {
    icon: Brain,
    title: 'Persistent memory',
    body:
      "Remembers your life — people, projects, preferences, patterns. Gets more useful the longer you use it. Forgets what you tell it to forget.",
  },
  {
    icon: Lock,
    title: 'Yours alone',
    body:
      "Not a shared model training on your data. Not phoning home to California. Not built into someone else's ecosystem play.",
  },
];

// Capabilities — deliberately specific and phone-native. Avoid vague
// "AI-powered" claims; each line describes a concrete behaviour.
// TODO: founder to validate — drafted 2026-04-23. The worst thing we could
// do here is sound generic.
const CAPABILITIES = [
  'Makes your calls — restaurants, doctor receptions, utility providers.',
  'Triages your inbox and drafts replies in your voice.',
  "Runs your day — 'what's next?', 'push my 2pm an hour', 'remind me when I'm in the car'.",
  'Navigates apps you use — books Ubers, orders groceries, responds to delivery SMS.',
  'Briefs you before meetings — reads linked docs, pulls relevant history.',
  "Captures what you say — 'file this under project X' from any voice note.",
  "Works offline for common tasks — doesn't fall over on a flaky connection.",
  'Escalates to a human ops team (ours) when something is beyond its scope.',
];

// How-it-works — the 4-phase onboarding story. Uses StepStack so each
// phase gets a numeral and a short body paragraph.
// TODO: founder to validate — drafted 2026-04-23.
const HOW_IT_WORKS_STEPS = [
  {
    title: 'Install',
    body:
      'You install Omni from the app store. Sign in. Grant the permissions you want. Revoke what you don\'t. Nothing happens until you say so.',
  },
  {
    title: 'Seed',
    body:
      'Omni spends the first day learning — your calendar, contacts, email patterns. You can review and edit what it\'s learned at any point.',
  },
  {
    title: 'Live',
    body:
      'It\'s now in your pocket. Talk to it like a person. It gets better the more you use it. You stop re-explaining context.',
  },
  {
    title: 'Evolve',
    body:
      'Add skills. Connect more tools. Deepen its knowledge of your work. Cap it at what you want it to know — nothing more.',
  },
];

// Pricing tiers — three tiers that map to consumer / pro / enterprise.
// The enterprise tier is intentionally priced "from $200 / executive /
// month" to anchor it against the per-seat SaaS math and to hint at
// sovereign hosting as the upsell lever.
// TODO: founder to validate — drafted 2026-04-23. Numbers are indicative.
const PRICING_TIERS = [
  {
    name: 'Consumer',
    price: '$30',
    cadence: '/ month',
    description: 'For personal use. Full capability. Fair-use limits.',
    features: [
      'Every capability on this page',
      'Fair-use daily limits',
      'Community support',
      'Your data stays in Australia',
    ],
  },
  {
    name: 'Pro',
    price: '$80',
    cadence: '/ month',
    description:
      'For executives, founders, and power users. Higher capacity, priority ops, integrations with work tools.',
    features: [
      'Higher daily capacity',
      'Priority ops team escalation',
      'Work-tool integrations (Gmail, Slack, calendar, docs)',
      'Advanced memory controls',
    ],
  },
  {
    name: 'Enterprise',
    price: 'From $200',
    cadence: '/ executive / month',
    description:
      'Sovereign hosting, SSO, admin dashboard, compliance review. Part of the Omniscient platform deal.',
    features: [
      'Sovereign / on-shore hosting',
      'SSO + admin dashboard',
      'Compliance review and audit logging',
      'Bundled with the Omniscient platform',
    ],
  },
];

// FAQ — honest, short answers. Each is 2-3 sentences. Flagged TODO so
// the founder can sharpen each before we commit them publicly.
// TODO: founder to validate every answer — drafted 2026-04-23.
const FAQ_ITEMS = [
  {
    q: 'Is my data private?',
    a: "Yes. Your memory, voice model, and conversation history live on Australian infrastructure with encryption at rest. You can audit what Omni knows, delete anything you want it to forget, and revoke its access to any OS capability with one toggle. We don't train shared models on your data.",
  },
  {
    q: 'What happens if my phone breaks?',
    a: "Your memory and settings are encrypted and synced to your Omni account, so a new device restores cleanly. The on-device model is re-provisioned at install; no data is lost in the transfer. You own the keys — losing those is the only failure mode we can't recover from, which is deliberate.",
  },
  {
    q: 'Does it work offline?',
    a: "For common tasks — reading the calendar, drafting a message, dictating a note, running a saved workflow — yes. For tasks that need the internet (making a call, booking a ride, web search), it queues the action and runs it as soon as you're back online. It doesn't fall over on a flaky connection.",
  },
  {
    q: 'Can my company deploy it for our exec team?',
    a: "Yes — that's the Enterprise tier. You get sovereign hosting, SSO, an admin dashboard, per-seat compliance review, and audit logging. It plugs into the same Omniscient platform that powers the workforce agents and the vertical SaaS products.",
  },
  {
    q: 'How is this different from Siri / Google Assistant / Copilot?',
    a: "Those are reactive prompt surfaces tied to a platform vendor's ecosystem. Omni is agentic — it acts on your behalf across apps — and it's yours alone, not a wedge for someone else's cloud. Sovereign hosting and persistent memory are the two lines none of those platforms cross.",
  },
  {
    q: 'What phones does it work on?',
    a: 'Android first — that\'s where the OS-level integrations we need are actually available. iOS is on the roadmap, gated by what Apple will let us do at the system level. We\'ll be upfront about that boundary rather than shipping something crippled.',
  },
  {
    q: 'When can I get one?',
    a: "We're running a waitlist right now, onboarding in cohorts. Flagship launch lands later in 2026. Book a call if you want to jump the line for your team.",
  },
];

// Primary CTA class — mirrors the HeroSplit primary button so the
// Companion hero reads as part of the same family. Kept local because we
// want it on ink ground here, which the shared class doesn't assume.
const primaryCtaClass =
  'inline-flex items-center gap-2 rounded-md bg-blue text-paper ' +
  'px-[22px] py-[14px] text-[15px] font-semibold ' +
  'transition-[transform,background-color,filter] duration-[180ms] ' +
  'ease-[cubic-bezier(0.2,0.9,0.2,1)] ' +
  'hover:-translate-y-px hover:bg-blue-deep active:translate-y-0 active:brightness-[.96] ' +
  'focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2';

// Paper-outline button for the secondary hero CTA on the ink hero.
const secondaryCtaInkClass =
  'inline-flex items-center gap-2 rounded-md bg-transparent text-paper ' +
  'border-[1.5px] border-paper px-[21px] py-[13px] text-[15px] font-semibold ' +
  'transition-[transform,background-color] duration-[180ms] ' +
  'ease-[cubic-bezier(0.2,0.9,0.2,1)] ' +
  'hover:-translate-y-px hover:bg-white/10 active:translate-y-0 ' +
  'focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2';

export default function CompanionDetail() {
  return (
    <Layout>
      <SEO
        title="The Companion — OmniscientAI"
        description="Omni: an AI that lives in your pocket, not in a chat window. Phone-native, voice-first, sovereign."
      />

      {/* Hero — full-bleed ink block, not HeroSplit. The Companion is our
          most distinctive bet and deserves a bespoke visual moment.
          Structure mirrors HeroSplit's 1.2fr/1fr grid so the page reads as
          part of the same family. */}
      <section className="ink-section">
        <Container>
          <div className="py-20 lg:py-32 grid lg:grid-cols-[1.2fr_1fr] gap-12 lg:gap-16 items-center">
            <div>
              <Eyebrow className="mb-6 block text-paper/60">
                PILLAR 3 · OMNI
              </Eyebrow>
              <h1 className="display text-paper mb-6">
                An AI that lives in your pocket. Not in a chat window.
              </h1>
              <p className="text-paper/85 text-[20px] leading-[1.45] mb-8 max-w-xl">
                Every major AI lives behind a login. Omni is different.
                Phone-native, voice-first, and yours alone — not Sam
                Altman&apos;s, not Sundar&apos;s.
              </p>
              <div className="flex flex-wrap gap-3">
                <Link href="/book" className={primaryCtaClass}>
                  Join the waitlist <span aria-hidden>→</span>
                </Link>
                <a href="#how-it-works" className={secondaryCtaInkClass}>
                  How it works
                </a>
              </div>
            </div>
            <div className="flex justify-center lg:justify-end">
              {/* TODO: replace BrainGraphic with an actual phone mockup
                  image once design delivers one. */}
              <BrainGraphic variant="circles" size="hero" />
            </div>
          </div>
        </Container>
      </section>

      {/* Differentiators — 4-up grid on desktop, 2-up at md, 1 at sm.
          Each card carries an icon + title + short body. */}
      <Section
        eyebrow="WHAT'S DIFFERENT"
        title="Four things every other AI misses."
      >
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {DIFFERENTIATORS.map((d) => {
            const Icon = d.icon;
            return (
              <Card key={d.title} className="flex flex-col">
                <Icon className="h-8 w-8 text-ink" aria-hidden />
                <h3 className="mt-5 font-semibold text-[22px] leading-tight text-ink">
                  {d.title}
                </h3>
                <p className="mt-3 text-ink-2">{d.body}</p>
              </Card>
            );
          })}
        </div>
      </Section>

      {/* Capabilities — 2-column checklist rendered like ServiceDetail's
          "What you'll get" list. Each line is a concrete phone-native
          behaviour; no vague "AI-powered" claims. */}
      <Section
        eyebrow="CAPABILITIES"
        title="Real agency, not reactive prompting."
        tone="paper-2"
      >
        <ul className="grid md:grid-cols-2 gap-x-8 gap-y-4 list-none p-0 m-0">
          {CAPABILITIES.map((capability) => (
            <li key={capability} className="flex items-start gap-3 text-ink">
              <Check
                className="h-5 w-5 text-blue mt-0.5 shrink-0"
                strokeWidth={2}
                aria-hidden
              />
              <span className="text-[17px] leading-relaxed text-ink-2">
                {capability}
              </span>
            </li>
          ))}
        </ul>
      </Section>

      {/* Sovereign callout — the one InkSection on the page. Gets the
          sovereignty story its own stage separate from the hero so the
          message lands rather than getting lost in a long page. */}
      <InkSection
        eyebrow="SOVEREIGN BY DEFAULT"
        title="Doesn't phone home to California."
      >
        <div className="max-w-3xl mx-auto">
          <p className="text-paper/85 text-[18px] leading-relaxed mb-4">
            Omni&apos;s memory, voice model, and conversation history stay on
            Australian infrastructure. For defence, government, and regulated
            industries, that&apos;s not a nice-to-have — it&apos;s the table
            stakes that disqualified every other option.
          </p>
          <p className="text-paper/85 text-[18px] leading-relaxed">
            You can audit what it knows. Delete what it remembers. Revoke its
            access to any OS capability with one toggle. Its memory is
            encrypted at rest with keys you control.
          </p>
        </div>
      </InkSection>

      {/* How it works — 4-phase StepStack. The #how-it-works id is the
          anchor target for the hero secondary CTA. */}
      <div id="how-it-works">
        <StepStack
          eyebrow="HOW IT WORKS"
          sectionTitle="From installed to indispensable in a week."
          steps={HOW_IT_WORKS_STEPS}
        />
      </div>

      {/* Pricing — 3-tier card grid. Each tier has name, price + cadence,
          short description, and a feature bullet list. The Enterprise
          tier is the one that bundles sovereign hosting. */}
      <Section
        eyebrow="PRICING"
        title="Plans that match your life."
        tone="paper-2"
      >
        <div className="grid md:grid-cols-3 gap-6">
          {PRICING_TIERS.map((tier) => (
            <Card key={tier.name} className="flex flex-col">
              <div className="mb-2">
                <MonoBadge>{tier.name}</MonoBadge>
              </div>
              <div className="mt-2 flex items-baseline gap-2">
                <span className="font-semibold text-[32px] leading-none text-ink">
                  {tier.price}
                </span>
                <span className="text-ink-3 text-[14px]">{tier.cadence}</span>
              </div>
              <p className="mt-4 text-ink-2">{tier.description}</p>
              <ul className="mt-5 list-none p-0 m-0 space-y-2">
                {tier.features.map((feature) => (
                  <li
                    key={feature}
                    className="flex items-start gap-2 text-ink-2 text-[15px]"
                  >
                    <Check
                      className="h-4 w-4 text-blue mt-0.5 shrink-0"
                      strokeWidth={2}
                      aria-hidden
                    />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
            </Card>
          ))}
        </div>
      </Section>

      <FAQAccordion
        eyebrow="QUESTIONS"
        sectionTitle="Honest answers."
        items={FAQ_ITEMS}
      />

      <CTAStrip
        tone="paper"
        title="Ready to meet Omni?"
        lede="We're onboarding the first wave of customers now. Book a call and we'll get you on the list."
        primaryCta={{ label: 'Book a call', href: '/book' }}
      />
    </Layout>
  );
}
