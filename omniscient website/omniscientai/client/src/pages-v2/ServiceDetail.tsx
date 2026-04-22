/**
 * ServiceDetail.tsx — v2 service detail page (/services/:slug).
 *
 * Looks up the service by slug from SERVICES in lib/data.ts. If the slug
 * doesn't match a known service, renders a small "Not found" fallback
 * with a link back to /services.
 *
 * Composition (valid slug):
 *
 *   Layout → back-link (CTALink) → HeroSplit → "What you'll get" checklist →
 *   StepStack (engagement phases) → centered pricing block →
 *   FAQAccordion → CTAStrip (ink tone)
 *
 * SERVICES entries in lib/data.ts don't carry pricing, engagement phases,
 * or FAQs — those are drafted inline here and flagged with TODO.
 *
 * TODO: service detail copy drafted 2026-04-22 — founder to validate
 */

import { useParams } from 'wouter';
import { Check } from 'lucide-react';
import SEO from '@/components/SEO';
import { Layout, Section } from '@/components-v2/layout';
import {
  HeroSplit,
  StepStack,
  FAQAccordion,
  CTAStrip,
} from '@/components-v2/sections';
import { CTALink, Eyebrow, MonoBadge } from '@/components-v2/ui';
import { SERVICES } from '@/lib/data';

// TODO: engagement phases drafted 2026-04-22 — same shape across services
// for now. Once each service has bespoke phases, move this into SERVICES
// in lib/data.ts and drive the StepStack from it.
const ENGAGEMENT_PHASES = [
  {
    title: 'Scoping call',
    body: 'A 45-minute call to understand your goals, constraints, and the team we\'ll be working with. Free, no sales pitch.',
    duration: '45 min',
  },
  {
    title: 'Statement of work',
    body: 'A 2-page SOW with a fixed scope, fixed price, and a named practitioner. We send it within 48 hours of the scoping call.',
    duration: '48 hrs',
  },
  {
    title: 'The work',
    body: 'Weekly sync with your team, async updates in the shared channel, and working artefacts from week one. No twelve-month roadmaps.',
    duration: '~3 weeks',
  },
  {
    title: 'Handover',
    body: 'Documentation, a recorded walkthrough, and a half-day of follow-up support after delivery. Then we\'re gone — no retainer lock-in.',
    duration: 'Week 4',
  },
];

// TODO: service pricing drafted 2026-04-22 — founder to validate.
// SERVICES in lib/data.ts doesn't carry price yet; starts-at values land
// here per slug. Falls through to a generic "Custom quote" line if absent.
const SERVICE_PRICING: Record<string, { from: string; format: string; duration: string }> = {
  'ai-strategy-consulting': {
    from: 'From $12,500 AUD',
    format: 'Fixed-scope engagement',
    duration: '3 weeks',
  },
  'ai-readiness-assessment': {
    from: 'From $7,500 AUD',
    format: 'Fixed-scope engagement',
    duration: '2 weeks',
  },
};

// TODO: service FAQs drafted 2026-04-22 — founder to validate.
// Generic for now; will tailor per service once we have real inbound
// questions from the Contact form.
const SERVICE_FAQS = [
  {
    q: 'Who is this for?',
    a: 'Founder-led teams and SME leadership groups who want a practical AI strategy without the overhead of a twelve-month consulting engagement. If you\'re shopping for a reseller or a partner-tier vendor, we\'re not a fit.',
  },
  {
    q: 'How long does it take?',
    a: 'Most engagements run 2–3 weeks end to end. We scope in week one, deliver in week two, and hand over in week three. Longer engagements are quoted separately if the scope demands it.',
  },
  {
    q: "What if we're not ready?",
    a: "We'll tell you at the scoping call. If the work doesn't fit or your team isn't ready, we'll recommend what to do first — even if that means not hiring us yet.",
  },
  {
    q: 'Do you lock us into a retainer?',
    a: "No. Every engagement is fixed-scope and fixed-price. We don't do month-on-month retainers unless you ask for one after delivery.",
  },
  {
    q: 'Who will actually be doing the work?',
    a: 'The named practitioner who scopes the work is the person doing the work. No partner-pitch-then-junior-delivery handoff.',
  },
];

// Fallback rendered when the slug doesn't match a known service. Kept simple
// — a heading, a back-link, and a link to the overview page.
function ServiceNotFound() {
  return (
    <Layout>
      <SEO
        title="Service not found"
        description="We couldn't find that service."
      />
      <Section>
        <div className="max-w-xl">
          <Eyebrow className="mb-4 block">404</Eyebrow>
          <h1 className="display mb-4">Service not found</h1>
          <p className="lede mb-8">
            We couldn&apos;t find a service matching that URL. It may have been
            renamed or moved.
          </p>
          <CTALink href="/services" className="text-blue">
            Back to services
          </CTALink>
        </div>
      </Section>
    </Layout>
  );
}

export default function ServiceDetail() {
  const params = useParams<{ slug: string }>();
  const slug = params.slug;
  const service = SERVICES.find((s) => s.slug === slug);

  if (!service) {
    return <ServiceNotFound />;
  }

  const pricing = SERVICE_PRICING[service.slug];

  return (
    <Layout>
      <SEO
        title={service.title}
        description={service.description}
      />

      {/* Back-link sits above the hero, inside the Layout's <main>.
          Rendered as a small-type CTALink — CTALink appends a trailing
          arrow which reads fine here ("return to services →"). */}
      <div className="max-w-[1200px] mx-auto px-6 lg:px-8 pt-12">
        <CTALink
          href="/services"
          className="text-sm text-ink-3"
          data-testid="back-to-services"
        >
          Services
        </CTALink>
      </div>

      <HeroSplit
        title={service.title}
        lede={service.description}
        primaryCta={{ label: 'Book a call', href: '/book' }}
        secondaryCta={{ label: 'See all services', href: '/services' }}
        graphic="circles"
      />

      {/* What you'll get — 2-column checklist. Derived from SERVICES.features
          in lib/data.ts. Each bullet is a Check icon + text block. */}
      <Section eyebrow="What you'll get" title="Outcomes, not deliverables.">
        <ul className="grid md:grid-cols-2 gap-x-8 gap-y-4 list-none p-0 m-0">
          {service.features.map((feature) => (
            <li key={feature} className="flex items-start gap-3 text-ink">
              <Check
                className="h-5 w-5 text-blue mt-0.5 shrink-0"
                strokeWidth={2}
                aria-hidden
              />
              <span className="text-[17px] leading-relaxed text-ink-2">
                {feature}
              </span>
            </li>
          ))}
        </ul>
      </Section>

      <StepStack
        eyebrow="How we work"
        sectionTitle="Four phases. Three weeks. One artefact."
        steps={ENGAGEMENT_PHASES}
      />

      {/* Pricing block — centered eyebrow + from-price, MonoBadges row for
          delivery format / duration, and a small note about custom scope.
          Wrapped in a paper-2 Section for pacing against the surrounding
          paper tones. */}
      <Section tone="paper-2">
        <div className="mx-auto max-w-2xl text-center">
          <Eyebrow className="mb-3 block">Investment</Eyebrow>
          <h2 className="font-semibold text-[32px] leading-tight text-ink">
            {pricing ? pricing.from : 'From $7,500 AUD'}
          </h2>
          {pricing && (
            <div className="mt-5 flex flex-wrap items-center justify-center gap-2 text-ink-3">
              <MonoBadge>{pricing.format}</MonoBadge>
              <span aria-hidden>·</span>
              <MonoBadge>{pricing.duration}</MonoBadge>
            </div>
          )}
          <p className="mt-5 text-ink-2 text-[16px]">
            Custom quote on scope. Every engagement starts with a free
            45-minute scoping call before any work lands.
          </p>
        </div>
      </Section>

      <FAQAccordion
        eyebrow="FAQ"
        sectionTitle="The questions we hear most."
        items={SERVICE_FAQS}
      />

      <CTAStrip
        tone="ink"
        title="Ready to start?"
        lede="A 20-minute call is free. If the work isn't right for us we'll tell you who else to talk to."
        primaryCta={{ label: 'Book a call', href: '/book' }}
      />
    </Layout>
  );
}
