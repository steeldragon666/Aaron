/**
 * Services.tsx — v2 Services overview page.
 *
 * Catalog page listing every consulting engagement we offer. Drives traffic
 * to the individual service detail pages. Composed from existing section
 * primitives and data from `lib/data.ts`:
 *
 *   HeroCentric → Service card grid (derived from SERVICES) →
 *   PillarGrid (breadth signal) → InkSection "How we work" pacer → CTAStrip
 *
 * `SERVICES` in `lib/data.ts` does not carry Lucide icon names, so we map
 * each slug to an icon inline (adapter pattern, per plan: don't modify
 * lib/data.ts). The fallback is `Compass` — the same default the legacy
 * Services page uses.
 *
 * TODO: service copy drafted 2026-04-22 — founder to validate
 */

import SEO from '@/components/SEO';
import { Layout, InkSection } from '@/components-v2/layout';
import {
  HeroCentric,
  PillarGrid,
  CTAStrip,
} from '@/components-v2/sections';
import { Card, CTALink } from '@/components-v2/ui';
import {
  Compass,
  BarChart3,
  GraduationCap,
  Activity,
  Shield,
  Bot,
  type LucideIcon,
} from 'lucide-react';
import { SERVICES } from '@/lib/data';

// Adapter: map service slug → Lucide icon. SERVICES entries in lib/data.ts
// don't carry an icon field, and we don't want to modify that file, so we
// keep the mapping local to this page.
const SERVICE_ICONS: Record<string, LucideIcon> = {
  'ai-strategy-consulting': Compass,
  'ai-readiness-assessment': BarChart3,
};

// TODO: founder to review pillar copy — duplicated from Home page temporarily
// to signal breadth across the Services catalog. If Home copy changes, sync
// here too. Once these stabilise, extract into a shared constants module.
const PILLARS = [
  {
    icon: GraduationCap,
    title: 'AI training',
    description:
      'Hands-on workshops that leave your team with a shippable artefact. Vendor-neutral — we have no kickbacks from Anthropic, OpenAI, or anyone else.',
    href: '/services/training',
  },
  {
    icon: Activity,
    title: 'Health technologies',
    description:
      'Clinical AI work with a serious respect for regulation, privacy, and the consequences of getting it wrong. Built alongside named medical practitioners.',
    href: '/industries/health',
  },
  {
    icon: Shield,
    title: 'Defense hardware & software',
    description:
      'Hardened systems and agentic tooling for defense contexts. Air-gapped when it needs to be. Integrity-first engineering.',
    href: '/industries/defense',
  },
  {
    icon: Bot,
    title: 'Agentic ops',
    description:
      'Marketing and ops agents that do one job well. Designed to be owned by the team that uses them, not locked into a vendor.',
    href: '/services/agentic-ops',
  },
];

// TODO: approach copy drafted 2026-04-22 — founder to validate tone
const APPROACH_PARAGRAPHS = [
  "Every engagement runs for roughly three weeks. We scope together, build in the open, and leave you with something your team owns outright — working software, a documented process, or a trained capability. Not a slide deck.",
  "We don't do month-on-month retainers unless you ask for one. We don't do vendor rebates. We don't hand you off to juniors halfway through. The person who pitched the work is the person doing the work.",
  "If three weeks isn't enough, we'll tell you at the scoping call and we'll tell you why. If it's too much, we'll cut scope before we take the cheque.",
];

export default function Services() {
  return (
    <Layout>
      <SEO
        title="Services"
        description="Short-form AI consulting engagements for Melbourne SMEs. Named practitioners, vendor-neutral advice, and an artefact your team owns at the end."
      />

      <HeroCentric
        eyebrow="Services"
        title="Short engagements. Named practitioners. An artefact at the end."
        lede="Boutique AI consulting for teams that want to get on with it. Vendor-neutral strategy, hands-on build, and the practitioner who scoped the work doing the work."
      />

      {/* Service cards grid — derived from SERVICES in lib/data.ts.
          Each card is a paper Card with an icon, title, short description,
          and a CTALink to the detail page. 2-up at md, stays 2-up at lg
          since the catalog is small. */}
      <section className="py-12 lg:py-24">
        <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-6">
            {SERVICES.map((service) => {
              const Icon = SERVICE_ICONS[service.slug] ?? Compass;
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
        </div>
      </section>

      <PillarGrid
        eyebrow="What we do"
        sectionTitle="Four practice areas. One standard."
        lede="Services sit inside four practice areas. Every engagement ends with an artefact your team owns — not a slide deck, not a dependency on us."
        pillars={PILLARS}
      />

      <InkSection
        eyebrow="APPROACH"
        title="Three weeks. One artefact. No lock-in."
      >
        <div className="max-w-3xl space-y-5 text-[18px] leading-[1.6] text-paper/80">
          {APPROACH_PARAGRAPHS.map((paragraph, idx) => (
            <p key={idx}>{paragraph}</p>
          ))}
        </div>
      </InkSection>

      <CTAStrip
        title="Let's see if we're a fit."
        lede="A 20-minute call, no sales pitch. If the work isn't right for us we'll tell you who else to talk to."
        primaryCta={{ label: "Let's see if we're a fit", href: '/book' }}
      />
    </Layout>
  );
}
