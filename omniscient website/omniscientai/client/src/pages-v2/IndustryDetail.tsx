/**
 * IndustryDetail.tsx — v2 industry detail page (/industries/:slug).
 *
 * Looks up the industry by slug from INDUSTRIES in lib/data.ts. If the slug
 * doesn't match a known industry, renders a small "Not found" fallback
 * with a link back to /industries.
 *
 * Composition (valid slug):
 *
 *   Layout → back-link (CTALink) → HeroSplit ("AI for {industry}") →
 *   Use-case card grid (3-up from common use cases) →
 *   Featured case study (FeaturedCard) →
 *   WorkshopCardGrid (all flagship workshops relevant to the industry) →
 *   CTAStrip (paper tone)
 *
 * INDUSTRIES entries in lib/data.ts don't tag workshops or cases per
 * industry. We show all three flagship workshops on every industry page
 * until that tagging lands. Featured case is drafted per-industry via a
 * local map.
 *
 * TODO: industry detail copy drafted 2026-04-22 — founder to validate
 */

import { useParams } from 'wouter';
import SEO from '@/components/SEO';
import { Layout, Section } from '@/components-v2/layout';
import {
  HeroSplit,
  WorkshopCardGrid,
  CTAStrip,
} from '@/components-v2/sections';
import {
  Card,
  CTALink,
  FeaturedCard,
  Eyebrow,
  MonoBadge,
} from '@/components-v2/ui';
import { INDUSTRIES, WORKSHOPS } from '@/lib/data';

// Adapter: legacy WORKSHOPS shape → Workshop type expected by
// WorkshopCardGrid. Same adapter as Workshops.tsx — kept local to avoid
// reaching into the overview page module.
function toCardWorkshop(w: (typeof WORKSHOPS)[number]) {
  return {
    slug: w.slug,
    title: w.title,
    description: w.description,
    duration: w.duration,
    format: w.format,
    price: w.priceRange,
    imageUrl: w.heroImage,
  };
}

// TODO: featured case copy drafted 2026-04-22 — replace with real tagged
// case studies once they land. Keyed by industry slug so each industry
// page gets a contextually-relevant lead case; falls back to a generic
// cross-industry case if the slug isn't in the map.
const FEATURED_CASE_BY_INDUSTRY: Record<
  string,
  { industry: string; title: string; outcome: string; href: string }
> = {
  'professional-services': {
    industry: 'Professional services',
    title: 'Cut underwriting review time by 60% with a targeted internal agent',
    outcome:
      'A 2-week pilot turned into a standing tool used by the whole underwriting team.',
    href: '/insights/financial-services-underwriting',
  },
  healthcare: {
    industry: 'Healthcare',
    title: 'Clinical note summarisation that practitioners actually trust',
    outcome:
      'Built with the clinicians, not for them — the key to the adoption curve going vertical.',
    href: '/insights/clinical-notes',
  },
  manufacturing: {
    industry: 'Manufacturing',
    title: 'From Excel chaos to a single source of operational truth',
    outcome:
      'Six months of work, most of it process design. The AI part was the last 10%.',
    href: '/insights/manufacturing-ops',
  },
  retail: {
    industry: 'Retail',
    title: 'Inventory forecasting that finally reflects reality',
    outcome:
      'Weekly stock-out rate dropped from 14% to 4% inside a quarter — zero new hires.',
    href: '/insights/retail-forecasting',
  },
};

// Fallback rendered when the slug doesn't match a known industry.
function IndustryNotFound() {
  return (
    <Layout>
      <SEO
        title="Industry not found"
        description="We couldn't find that industry."
      />
      <Section>
        <div className="max-w-xl">
          <Eyebrow className="mb-4 block">404</Eyebrow>
          <h1 className="display mb-4">Industry not found</h1>
          <p className="lede mb-8">
            We couldn&apos;t find an industry matching that URL. It may have
            been renamed or moved.
          </p>
          <CTALink href="/industries" className="text-blue">
            Back to industries
          </CTALink>
        </div>
      </Section>
    </Layout>
  );
}

export default function IndustryDetail() {
  const params = useParams<{ slug: string }>();
  const slug = params.slug;
  const industry = INDUSTRIES.find((i) => i.slug === slug);

  if (!industry) {
    return <IndustryNotFound />;
  }

  const featuredCase =
    FEATURED_CASE_BY_INDUSTRY[industry.slug] ??
    FEATURED_CASE_BY_INDUSTRY['professional-services'];

  return (
    <Layout>
      <SEO
        title={`AI for ${industry.title}`}
        description={industry.description}
      />

      {/* Back-link — same pattern as ServiceDetail. */}
      <div className="max-w-[1200px] mx-auto px-6 lg:px-8 pt-12">
        <CTALink
          href="/industries"
          className="text-sm text-ink-3"
          data-testid="back-to-industries"
        >
          Industries
        </CTALink>
      </div>

      <HeroSplit
        eyebrow={industry.title}
        title={`AI for ${industry.title}.`}
        lede={industry.description}
        primaryCta={{ label: 'Book a call', href: '/book' }}
        secondaryCta={{ label: 'See all industries', href: '/industries' }}
        graphic="circles"
      />

      {/* Use-case list — 3-up Card grid derived from industry.useCases.
          Each card surfaces one use case as a mini case-study prompt.
          TODO: founder to validate per-industry copy and swap generic
          framing when real use-case details land. */}
      <Section
        eyebrow="Use cases"
        title={`Where AI earns its keep in ${industry.title.toLowerCase()}.`}
      >
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {industry.useCases.slice(0, 6).map((useCase, idx) => (
            <Card key={useCase} className="flex flex-col">
              <MonoBadge>{`0${idx + 1}`}</MonoBadge>
              <p className="mt-4 text-[17px] leading-snug text-ink font-medium">
                {useCase}
              </p>
            </Card>
          ))}
        </div>
      </Section>

      {/* Featured case study — FeaturedCard on ink, single-up full width.
          Reuses the visual pattern from the Home + Industries overview
          CaseGrid but rendered inline here so the page reads as
          "in this industry, we have done: X". */}
      <Section eyebrow="In practice" title="What it looks like on the ground.">
        <FeaturedCard className="flex flex-col">
          <Eyebrow className="text-paper/70">{featuredCase.industry}</Eyebrow>
          <h3 className="mt-3 font-semibold text-[28px] leading-tight">
            {featuredCase.title}
          </h3>
          <p className="mt-4 text-paper/80 text-[17px] leading-relaxed max-w-2xl">
            {featuredCase.outcome}
          </p>
          <a
            href={featuredCase.href}
            className={
              'inline-flex items-center gap-1 font-medium text-paper mt-6 ' +
              'border-b border-transparent hover:border-current ' +
              'transition-colors duration-[180ms] ease-[cubic-bezier(0.2,0.9,0.2,1)] ' +
              'focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2 ' +
              'w-fit'
            }
          >
            Read the case study <span aria-hidden>→</span>
          </a>
        </FeaturedCard>
      </Section>

      <WorkshopCardGrid
        eyebrow="Workshops"
        sectionTitle="Workshops relevant to your industry."
        workshops={WORKSHOPS.map(toCardWorkshop)}
      />

      <CTAStrip
        tone="paper"
        title={`Let's talk ${industry.title.toLowerCase()} specifics.`}
        lede="A 20-minute call is free. Tell us the workflow you're trying to change and we'll tell you honestly whether AI is the right lever."
        primaryCta={{ label: 'Talk to us', href: '/contact' }}
      />
    </Layout>
  );
}
