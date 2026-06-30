/**
 * WorkshopDetail.tsx — v2 workshop detail page (/workshops/:slug).
 *
 * Looks up the workshop by slug from WORKSHOPS in lib/data.ts. If the
 * slug doesn't match a known workshop, renders a small "Not found"
 * fallback with a link back to /workshops.
 *
 * Composition (valid slug):
 *
 *   Layout → back-link (CTALink) →
 *   HeroSplit (title, lede, MonoBadge meta row) →
 *   2-column layout on lg: page content + sticky BookingForm sidebar
 *     content column:
 *       "Who it's for" checklist (2-col Card on paper-2)
 *       Module agenda (StepStack)
 *       Outcomes (numbered Card grid)
 *       FAQAccordion
 *     sidebar (lg:sticky lg:top-24):
 *       BookingForm with workshop as selected service
 *   On mobile, BookingForm renders below the FAQ as a standalone section.
 *   CTAStrip at the bottom of the page.
 *
 * Workshop data in lib/data.ts is richer than services/industries — it
 * carries modules, outcomes, whoIsItFor, faqs, testimonials, and pricing.
 * We use that richer data directly and drop inline adapters only where
 * section primitives need a specific prop shape.
 *
 * The BookingForm's onSubmit is a local stub that logs + resolves after
 * 500ms (matches the Contact page's pattern). Phase 12 wires the real
 * backend.
 */

import { useParams } from 'wouter';
import { Check, Target, Zap, Award, Lightbulb, Rocket } from 'lucide-react';
import SEO from '@/components/SEO';
import { Layout, Section } from '@/components-v2/layout';
import {
  HeroSplit,
  StepStack,
  FAQAccordion,
  CTAStrip,
  BookingForm,
} from '@/components-v2/sections';
import type { BookingFormData } from '@/components-v2/sections/BookingForm';
import {
  Card,
  CTALink,
  Eyebrow,
  MonoBadge,
} from '@/components-v2/ui';
import { WORKSHOPS } from '@/lib/data';

// Outcome icons rotate through a small set — purely decorative. If the
// workshop has more outcomes than icons, we cycle from the start.
const OUTCOME_ICONS = [Target, Zap, Award, Lightbulb, Rocket];

// Stub submit handler — same pattern as the Book and Contact pages.
// Phase 12 wires the real backend (POST /api/book or similar).
const handleBookingSubmit = async (data: BookingFormData): Promise<void> => {
  // eslint-disable-next-line no-console
  console.log('[v2 workshop booking submit]', data);
  await new Promise<void>((resolve) => setTimeout(resolve, 500));
};

// Fallback rendered when the slug doesn't match a known workshop.
function WorkshopNotFound() {
  return (
    <Layout>
      <SEO
        title="Workshop not found"
        description="We couldn't find that workshop."
      />
      <Section>
        <div className="max-w-xl">
          <Eyebrow className="mb-4 block">404</Eyebrow>
          <h1 className="display mb-4">Workshop not found</h1>
          <p className="lede mb-8">
            We couldn&apos;t find a workshop matching that URL. It may have
            been renamed or moved.
          </p>
          <CTALink href="/workshops" className="text-blue">
            Back to workshops
          </CTALink>
        </div>
      </Section>
    </Layout>
  );
}

export default function WorkshopDetail() {
  const params = useParams<{ slug: string }>();
  const slug = params.slug;
  const workshop = WORKSHOPS.find((w) => w.slug === slug);

  if (!workshop) {
    return <WorkshopNotFound />;
  }

  // BookingForm service options — the current workshop as the primary
  // option, plus a catch-all "custom" choice that routes to the custom
  // workshop intake. Description on the primary surfaces duration so the
  // user sees the scope they're booking.
  const bookingServices = [
    {
      value: workshop.slug,
      label: workshop.title,
      description: workshop.duration,
    },
    {
      value: 'custom',
      label: 'Something custom instead',
      description: 'Tell us what you need',
    },
  ];

  // Adapter: workshop.modules → StepStack's Step shape. lib/data.ts uses
  // `description` for the module body; StepStack expects `body`. Keep the
  // adapter local to avoid touching lib/data.ts.
  const moduleSteps = workshop.modules.map((m) => ({
    title: m.title,
    body: m.description,
    duration: m.duration,
  }));

  const bookingForm = (
    <BookingForm services={bookingServices} onSubmit={handleBookingSubmit} />
  );

  return (
    <Layout>
      <SEO
        title={workshop.title}
        description={workshop.description}
      />

      {/* Back-link — same pattern as ServiceDetail / IndustryDetail. */}
      <div className="max-w-[1200px] mx-auto px-6 lg:px-8 pt-12">
        <CTALink
          href="/workshops"
          className="text-sm text-ink-3"
          data-testid="back-to-workshops"
        >
          Workshops
        </CTALink>
      </div>

      <HeroSplit
        eyebrow={workshop.subtitle}
        title={workshop.title}
        lede={workshop.description}
        primaryCta={{
          label: 'Book this workshop',
          href: `/book?workshop=${workshop.slug}`,
        }}
        secondaryCta={{ label: 'See all workshops', href: '/workshops' }}
        graphic="circles"
      />

      {/* Meta row — duration / format / price as MonoBadges. Sits below
          the hero as its own strip so the hero's Lede stays a clean
          paragraph. */}
      <div className="max-w-[1200px] mx-auto px-6 lg:px-8 -mt-8 lg:-mt-12 mb-4">
        <div
          className="flex flex-wrap items-center gap-2 text-ink-3"
          data-testid="workshop-meta-row"
        >
          <MonoBadge>{workshop.duration}</MonoBadge>
          <span aria-hidden>·</span>
          <MonoBadge>{workshop.format}</MonoBadge>
          <span aria-hidden>·</span>
          <MonoBadge>{workshop.priceRange}</MonoBadge>
        </div>
      </div>

      {/* 2-column layout: page content on the left, sticky BookingForm
          on the right (lg+). On mobile, only the content column renders
          here — the BookingForm shows up as its own section below the
          FAQ (see the mobile booking section further down). */}
      <Section>
        <div className="grid grid-cols-1 lg:grid-cols-[2fr_1fr] gap-8 lg:gap-12">
          <div className="flex flex-col gap-16 lg:gap-24">
            {/* Who it's for — 2-column Card on paper-2 with Check icons. */}
            <div>
              <Eyebrow className="mb-3 block">Who it&apos;s for</Eyebrow>
              <h2 className="font-semibold text-[32px] leading-tight text-ink mb-6">
                Built for teams who&apos;ve tried the slide-deck version.
              </h2>
              <Card tone="paper-2">
                <ul className="grid md:grid-cols-2 gap-x-8 gap-y-4 list-none p-0 m-0">
                  {workshop.whoIsItFor.map((item) => (
                    <li key={item} className="flex items-start gap-3 text-ink">
                      <Check
                        className="h-5 w-5 text-blue mt-0.5 shrink-0"
                        strokeWidth={2}
                        aria-hidden
                      />
                      <span className="text-[17px] leading-relaxed text-ink-2">
                        {item}
                      </span>
                    </li>
                  ))}
                </ul>
              </Card>
            </div>

            {/* Module agenda — StepStack from workshop.modules. The
                section header is owned by StepStack's own eyebrow/title
                slots, so we don't need an outer wrapper. */}
            <StepStack
              eyebrow="Agenda"
              sectionTitle="What you'll cover."
              steps={moduleSteps}
              className="!py-0 lg:!py-0"
            />

            {/* Outcomes — numbered Card grid. Each outcome gets a Lucide
                icon (cycling) + the outcome text. 2-up on md, 1-up on
                mobile so the text stays readable. */}
            <div>
              <Eyebrow className="mb-3 block">Outcomes</Eyebrow>
              <h2 className="font-semibold text-[32px] leading-tight text-ink mb-6">
                What you&apos;ll walk away with.
              </h2>
              <div className="grid md:grid-cols-2 gap-6">
                {workshop.outcomes.map((outcome, idx) => {
                  const Icon = OUTCOME_ICONS[idx % OUTCOME_ICONS.length];
                  return (
                    <Card key={outcome} className="flex flex-col">
                      <div className="flex items-center gap-3">
                        <MonoBadge>{`0${idx + 1}`}</MonoBadge>
                        <Icon
                          className="h-5 w-5 text-blue"
                          strokeWidth={1.75}
                          aria-hidden
                        />
                      </div>
                      <p className="mt-4 text-[17px] leading-relaxed text-ink">
                        {outcome}
                      </p>
                    </Card>
                  );
                })}
              </div>
            </div>

            {/* FAQ accordion from workshop.faqs. */}
            <FAQAccordion
              eyebrow="FAQ"
              sectionTitle="The questions we hear most."
              items={workshop.faqs}
              className="!py-0 lg:!py-0"
            />
          </div>

          {/* Sticky sidebar — desktop only. Hidden on mobile; a matching
              section below renders the same BookingForm inline. */}
          <aside className="hidden lg:block" data-testid="sticky-booking-sidebar">
            <div className="lg:sticky lg:top-24">
              <div className="mb-4">
                <Eyebrow className="mb-2 block">Book this workshop</Eyebrow>
                <p className="text-ink-2 text-[15px] leading-relaxed">
                  Secure your team&apos;s spot. A named practitioner
                  confirms within one business day.
                </p>
              </div>
              {bookingForm}
            </div>
          </aside>
        </div>
      </Section>

      {/* Mobile-only BookingForm section — mirrors the sidebar content.
          Hidden on lg+ where the sticky sidebar owns this slot. */}
      <Section
        tone="paper-2"
        className="lg:hidden"
        eyebrow="Book this workshop"
        title="Secure your team's spot."
        lede="A named practitioner confirms within one business day."
      >
        <div data-testid="mobile-booking-form">{bookingForm}</div>
      </Section>

      <CTAStrip
        tone="paper"
        title="Not sure this is the right fit?"
        lede="Book a 20-minute call and we'll help you figure out which workshop — or whether a custom scope is closer to what you need."
        primaryCta={{ label: 'Book a 20-min call', href: '/book' }}
        secondaryCta={{ label: 'See all workshops', href: '/workshops' }}
      />
    </Layout>
  );
}
