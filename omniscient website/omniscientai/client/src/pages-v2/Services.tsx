/**
 * Services.tsx — v2 Services overview page.
 *
 * Strategic pivot (2026-04-22): mirrors the new 3-pillar structure from
 * Home — vertical SaaS, the Omniscient Workforce, the Companion — with
 * consulting/workshops as a de-emphasised tail section.
 *
 * Composition:
 *   HeroCentric → Pillar 1 products (card grid) → Pillar 2 workforce
 *   personas (card grid) → Pillar 3 Companion (InkSection) → Consulting +
 *   workshops (de-emphasised Section) → InkSection "How we work" →
 *   CTAStrip
 *
 * The SERVICES array in lib/data.ts now carries the new vertical SaaS,
 * workforce, and companion entries so /services/:slug links all resolve.
 * Legacy consulting entries (ai-strategy-consulting, ai-readiness-
 * assessment) remain at the tail of SERVICES for backwards links.
 *
 * TODO: service copy drafted 2026-04-22 — founder to validate
 */

import { Link } from 'wouter';
import SEO from '@/components/SEO';
import { Layout, InkSection, Section } from '@/components-v2/layout';
import {
  HeroCentric,
  CTAStrip,
} from '@/components-v2/sections';
import { Card, CTALink, Eyebrow, Lede } from '@/components-v2/ui';
import { BrainGraphic } from '@/components-v2/brand';
import {
  Sprout,
  Shield,
  HeartHandshake,
  UserCircle2,
  BookOpen,
  Workflow,
  Megaphone,
  FileCheck,
  Code2,
  type LucideIcon,
} from 'lucide-react';
import { SERVICES } from '@/lib/data';

// Pillar 1 — Vertical SaaS products. Keyed by SERVICES slug so the card
// derives title/description from data.ts; the icon lives here because
// SERVICES entries don't carry Lucide references.
const VERTICAL_SAAS_SLUGS = ['bioenergy', 'defence', 'mental-health'] as const;
const VERTICAL_SAAS_ICONS: Record<string, LucideIcon> = {
  bioenergy: Sprout,
  defence: Shield,
  'mental-health': HeartHandshake,
};

// Pillar 2 — Workforce personas. Defined inline rather than pulling from
// SERVICES because the umbrella "workforce" SERVICES entry doesn't carry
// per-persona records yet. Keep these in sync with Home.tsx — if they
// diverge often, extract into a shared module.
const WORKFORCE_PERSONAS = [
  {
    icon: UserCircle2,
    title: 'AI-EA',
    subtitle: 'Executive assistant',
    description: 'Calendar, email, drafting, scheduling. The flagship persona.',
  },
  {
    icon: BookOpen,
    title: 'AI Associate',
    subtitle: 'Analyst / research',
    description: 'Brief synthesis, desk research, memo writing.',
  },
  {
    icon: Workflow,
    title: 'AI Operator',
    subtitle: 'Workflow execution',
    description: 'Tickets, updates, reporting loops. Things that have to happen.',
  },
  {
    icon: Megaphone,
    title: 'AI BDR',
    subtitle: 'Prospecting & outreach',
    description: 'Inbound qualification, outbound sequencing.',
  },
  {
    icon: FileCheck,
    title: 'AI Compliance Officer',
    subtitle: 'Audits, reporting, grants',
    description: 'Boring in the best way.',
  },
  {
    icon: Code2,
    title: 'AI Engineer',
    subtitle: 'Code + devops',
    description: 'Ships. Ops. Reviews. Does not complain.',
  },
];

export default function Services() {
  // Pre-resolve SERVICES entries for the three vertical SaaS pillars so the
  // TypeScript narrowing is explicit and the page still renders if data.ts
  // is missing an entry (we filter out undefined).
  const verticalSaaSServices = VERTICAL_SAAS_SLUGS.map((slug) =>
    SERVICES.find((s) => s.slug === slug),
  ).filter((s): s is NonNullable<typeof s> => Boolean(s));

  // Legacy consulting lines — rendered in the de-emphasised tail section so
  // they're still linkable without stealing the headline.
  const LEGACY_CONSULTING_SLUGS = [
    'ai-strategy-consulting',
    'ai-readiness-assessment',
  ];
  const legacyServices = LEGACY_CONSULTING_SLUGS.map((slug) =>
    SERVICES.find((s) => s.slug === slug),
  ).filter((s): s is NonNullable<typeof s> => Boolean(s));

  return (
    <Layout>
      <SEO
        title="Services — Products, platforms, and agents."
        description="Sovereign applied AI across three pillars: vertical SaaS, the Omniscient Workforce, and the Companion. Plus consulting when you need it."
      />

      <HeroCentric
        eyebrow="Services"
        title="Products, platforms, and agents — operated as managed services."
        lede="Three pillars. Three bets we're willing to build the company around. Vertical SaaS where we have unfair advantage, a managed workforce of AI agents, and a phone-native companion you actually own."
      />

      {/* Pillar 1 — Vertical SaaS products. 3-up card grid derived from
          SERVICES in lib/data.ts. Each card links to /services/:slug. */}
      <Section
        eyebrow="PILLAR 1"
        title="Vertical SaaS for industries we understand."
        lede="We pick verticals where we have unfair advantage and build the software, data, and workflow tools they actually need."
      >
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {verticalSaaSServices.map((service) => {
            const Icon = VERTICAL_SAAS_ICONS[service.slug] ?? Sprout;
            return (
              <Card key={service.slug} className="flex flex-col">
                <Icon className="h-8 w-8 text-ink" aria-hidden />
                <h3 className="mt-5 font-semibold text-[22px] leading-tight text-ink">
                  {service.title}
                </h3>
                <p className="mt-3 text-ink-2">{service.description}</p>
                <CTALink
                  href={`/services/${service.slug}`}
                  className="mt-5 text-blue"
                >
                  Learn more
                </CTALink>
              </Card>
            );
          })}
        </div>
      </Section>

      {/* Pillar 2 — Workforce personas. 3-up grid with subtitles under each
          persona name. Mirrors the Home layout so the two pages read the
          same shape of information. */}
      <Section
        eyebrow="PILLAR 2"
        title="The Omniscient Workforce."
        lede="A managed workforce of AI agents, each specialised to a real role. Sell per-agent per month; we monitor and tune them."
        tone="paper-2"
      >
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {WORKFORCE_PERSONAS.map((persona) => {
            const Icon = persona.icon;
            return (
              <Card key={persona.title} className="flex flex-col">
                <Icon className="h-6 w-6 text-ink mb-4" aria-hidden />
                <h3 className="font-semibold text-[22px] leading-tight text-ink mb-1">
                  {persona.title}
                </h3>
                <div className="text-[14px] text-ink-3 mb-3">
                  {persona.subtitle}
                </div>
                <p className="text-ink-2">{persona.description}</p>
              </Card>
            );
          })}
        </div>
        <div className="mt-10">
          <CTALink href="/services/workforce" className="text-blue">
            See how the Workforce is provisioned
          </CTALink>
        </div>
      </Section>

      {/* Pillar 3 — The Companion (Omni). Rendered in an InkSection for
          visual weight — same device as Home, per the design-system rule of
          at-most-one InkSection per page. */}
      <InkSection
        eyebrow="PILLAR 3"
        title="The Companion. An AI that lives in your pocket."
      >
        <div className="grid md:grid-cols-2 gap-12 items-center max-w-4xl mx-auto">
          <div>
            <p className="text-paper/80 text-[18px] leading-relaxed mb-4">
              Phone-native. Voice-first. Persistent memory. Integrates with
              your OS — calls, SMS, calendar, contacts, accessibility
              services. Makes your calls. Books your day. Runs your errands.
            </p>
            <p className="text-paper/80 text-[18px] leading-relaxed mb-6">
              Consumer subscription or an enterprise perk for executives at
              our platform customers. For defence and government users, a
              sovereign option that doesn&apos;t phone home to California.
            </p>
            <Link
              href="/services/companion"
              className="inline-flex items-center gap-2 text-paper border-b border-paper/40 hover:border-paper pb-1 transition-colors"
            >
              Learn more about Omni <span aria-hidden>→</span>
            </Link>
          </div>
          <div className="flex justify-center">
            <BrainGraphic variant="circles" size="section" />
          </div>
        </div>
      </InkSection>

      {/* Consulting + workshops — de-emphasised tail. Small cards, not a
          headline, so the option stays linkable without hijacking the
          narrative. */}
      <Section tone="paper-2">
        <div className="max-w-3xl mb-8">
          <Eyebrow className="mb-3 block">ALSO</Eyebrow>
          <h2 className="font-semibold text-[32px] leading-tight text-ink mb-4">
            Consulting + workshops, when you need them.
          </h2>
          <Lede>
            Sometimes the right answer isn&apos;t a product — it&apos;s a
            strategic engagement. Vendor-neutral advice, named practitioners,
            and an artefact at the end.
          </Lede>
        </div>
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {legacyServices.map((service) => (
            <Card key={service.slug} className="flex flex-col">
              <h3 className="font-semibold text-[20px] leading-tight text-ink">
                {service.title}
              </h3>
              <p className="mt-3 text-ink-2">{service.description}</p>
              <CTALink
                href={`/services/${service.slug}`}
                className="mt-5 text-blue"
              >
                Learn more
              </CTALink>
            </Card>
          ))}
        </div>
        <div>
          <Link
            href="/workshops"
            className="inline-flex items-center gap-2 text-ink font-medium border-b border-ink/20 hover:border-ink pb-1 transition-colors"
          >
            See the workshops <span aria-hidden>→</span>
          </Link>
        </div>
      </Section>

      <CTAStrip
        title="Let's see what we could build for you."
        lede="A 20-minute call. We'll tell you exactly what we could build and what it costs — or who else you should talk to if we're not the fit."
        primaryCta={{ label: "Let's see if we're a fit", href: '/book' }}
      />
    </Layout>
  );
}
