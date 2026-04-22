/**
 * Workshops.tsx — v2 Workshops overview page.
 *
 * Catalog page listing every workshop. Drives traffic to individual
 * workshop detail pages and to the custom-workshop intake. Composed from
 * existing section primitives and data from `lib/data.ts`:
 *
 *   HeroCentric → WorkshopCardGrid (from WORKSHOPS, via adapter) →
 *   Custom-workshop inline CTA card (paper-2) →
 *   TestimonialStrip → CTAStrip
 *
 * The legacy `WORKSHOPS` schema in `lib/data.ts` uses different field names
 * than the `Workshop` type expected by `WorkshopCardGrid` (`heroImage` vs
 * `imageUrl`, `priceRange` vs `price`). We run a local `toCardWorkshop`
 * adapter rather than touching `lib/data.ts` or the section primitive.
 *
 * TODO: workshop copy drafted 2026-04-22 — founder to validate
 */

import SEO from '@/components/SEO';
import { Layout } from '@/components-v2/layout';
import {
  HeroCentric,
  WorkshopCardGrid,
  TestimonialStrip,
  CTAStrip,
} from '@/components-v2/sections';
import { Card, CTALink } from '@/components-v2/ui';
import { WORKSHOPS } from '@/lib/data';

// Adapter: map the legacy WORKSHOPS item shape to the `Workshop` prop shape
// expected by `WorkshopCardGrid`. We don't modify `lib/data.ts` or the
// primitive — the adapter lives here so the two can evolve independently.
type CardWorkshop = {
  slug: string;
  title: string;
  description: string;
  duration: string;
  format: string;
  price: string;
  imageUrl?: string;
};

function toCardWorkshop(
  w: (typeof WORKSHOPS)[number],
): CardWorkshop {
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

// TODO: replace with real testimonials — reuses Home's pattern; this set is
// deliberately workshop-weighted to read as proof for the catalog page.
const TESTIMONIALS = [
  {
    quote:
      "The workshop didn't feel like a workshop. It felt like we hired a senior engineer for two days and came out with a working tool.",
    name: 'James K.',
    role: 'Head of operations',
    company: 'Healthcare services provider',
  },
  {
    quote:
      "They didn't sell us a platform. They sold us two days of their attention, and our team came out with something we actually use every week.",
    name: 'Sarah M.',
    role: 'COO',
    company: 'Mid-market logistics firm',
  },
  {
    quote:
      "We'd done other 'AI training' before — this was the first time anyone showed us how to actually run a prompt against our real data.",
    name: 'Priya R.',
    role: 'Founder',
    company: 'B2B SaaS startup',
  },
];

export default function Workshops() {
  return (
    <Layout>
      <SEO
        title="Workshops"
        description="Hands-on, vendor-neutral AI workshops built around your actual workflow. Every workshop leaves your team with a shippable artefact, not a slide deck."
      />

      <HeroCentric
        eyebrow="Workshops"
        title="Hands-on training, when it makes sense."
        lede="Most customers use our products and agents. Some need their team trained up first — these workshops are for them. Vendor-neutral, named practitioners, shippable artefact."
      />

      <WorkshopCardGrid
        eyebrow="Catalog"
        sectionTitle="Pick the one that fits."
        workshops={WORKSHOPS.map(toCardWorkshop)}
      />

      {/* Custom-workshop inline CTA card — Section wrapper uses paper-2 tone
          so it pacing-breaks from the workshop grid above. A single Card
          across the full container width with a CTALink to the custom intake. */}
      <section className="py-12 lg:py-24 bg-paper-2">
        <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
          <Card tone="paper-2" className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
            <div className="md:max-w-2xl">
              <h2 className="font-semibold text-[28px] leading-tight text-ink">
                Need something different?
              </h2>
              <p className="mt-3 text-ink-2 text-[18px] leading-[1.55]">
                We build custom training from your actual workflow. Tell us
                what your team is trying to ship this quarter and we'll scope
                a workshop to match — not a generic deck, not the same slides
                everyone else gets.
              </p>
            </div>
            <CTALink
              href="/workshops/custom"
              className="text-blue text-[16px] whitespace-nowrap"
            >
              Scope a custom workshop
            </CTALink>
          </Card>
        </div>
      </section>

      <TestimonialStrip
        eyebrow="What people say"
        sectionTitle="After the workshop."
        testimonials={TESTIMONIALS}
      />

      <CTAStrip
        title="Ready to book?"
        lede="Pick a workshop above or book a 20-minute call and we'll help you figure out which one's right."
        primaryCta={{ label: 'Book a workshop', href: '/book' }}
        secondaryCta={{ label: 'Talk to us first', href: '/contact' }}
      />
    </Layout>
  );
}
