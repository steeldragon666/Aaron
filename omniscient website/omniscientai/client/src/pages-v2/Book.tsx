/**
 * Book.tsx — v2 dedicated booking page (/book).
 *
 * The Book page IS the conversion goal, so chrome is minimal: Nav stays (for
 * up-out navigation), Footer is hidden via Layout's `hideFooter`. The page
 * is a narrow Section wrapping the BookingForm primitive with a small intro
 * above it.
 *
 *   Layout(hideFooter) → narrow Section → intro (Eyebrow + H1 + Lede) →
 *                        BookingForm (services built from WORKSHOPS +
 *                        "discovery-call" + "custom")
 *
 * The submit handler is a local stub matching the pattern in Contact and
 * WorkshopDetail — logs, waits 800ms, resolves. Real backend wiring
 * (POST /api/book or similar) is Phase 12.
 *
 * TODO: copy drafted 2026-04-22 — founder to validate tone.
 */

import SEO from '@/components/SEO';
import { Layout, Section } from '@/components-v2/layout';
import { BookingForm } from '@/components-v2/sections';
import type { BookingFormData } from '@/components-v2/sections/BookingForm';
import { Display, Eyebrow, Lede } from '@/components-v2/ui';
import { WORKSHOPS } from '@/lib/data';

// Stub submit handler — same pattern as Contact / WorkshopDetail.
// The 800ms delay exercises BookingForm's submitting state so the button
// transitions to "Booking..." during the artificial wait.
// TODO: wire real backend in Phase 12.
const handleSubmit = async (data: BookingFormData): Promise<void> => {
  // eslint-disable-next-line no-console
  console.log('[v2 book submit]', data);
  await new Promise<void>((resolve) => setTimeout(resolve, 800));
};

// Build the BookingForm services list. `discovery-call` is the lowest-friction
// entry point (no prep, 20 min) and lives at the top. Each workshop from
// lib/data.ts is an explicit option, with priceRange used as the description
// (duration already lives in the label so the card gives a shape + a budget
// anchor at a glance). `custom` is the catch-all for teams whose shape
// doesn't match any workshop.
const services = [
  {
    value: 'discovery-call',
    label: 'Discovery call · 20 minutes',
    description: 'No prep needed',
  },
  ...WORKSHOPS.map((w) => ({
    value: w.slug,
    label: `${w.title} · ${w.duration}`,
    description: w.priceRange,
  })),
  {
    value: 'custom',
    label: 'Something custom',
    description: "We'll scope it together",
  },
];

export default function Book() {
  return (
    <Layout hideFooter>
      <SEO
        title="Book a call"
        description="20 minutes on your setup. No sales pitch — just a real conversation about what might work."
      />

      {/* Narrower max-w than standard Section — the wizard feels better
          constrained. Section default is max-w-[1200px] via Container; we
          override with an inner wrapper that caps at max-w-2xl. */}
      <Section className="py-16 lg:py-24">
        <div className="mx-auto max-w-2xl">
          <div className="mb-10 text-center">
            <Eyebrow className="mb-4 block">Book a call</Eyebrow>
            <Display as="h1">Let&apos;s talk.</Display>
            <Lede className="mt-6">
              20 minutes on your setup. No sales pitch — just a real
              conversation about what might work.
            </Lede>
          </div>

          <BookingForm services={services} onSubmit={handleSubmit} />
        </div>
      </Section>
    </Layout>
  );
}
