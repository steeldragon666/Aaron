/**
 * CustomWorkshop.tsx — v2 custom workshop intake page (/workshops/custom).
 *
 * Replaces the V2Placeholder that was previously mapped to /workshops/custom.
 * Teams whose shape doesn't match the three catalog workshops land here to
 * request a scoped-from-scratch engagement.
 *
 *   Layout → HeroCentric → Requirements form (paper-2 Card) →
 *   StepStack "How we scope" (4 steps) → CTAStrip paper (questions → /contact)
 *
 * Form fields: org size, industry, goals (Textarea), preferred format,
 * budget range, name, email, submit. Industry options are ported from
 * INDUSTRIES in lib/data.ts so the taxonomy stays aligned with the rest of
 * the site. The submit handler is a local 500ms-delay stub matching Contact
 * / Book / WorkshopDetail patterns — real backend wiring is Phase 12.
 *
 * TODO: copy drafted 2026-04-22 — founder to validate tone and scoping
 * phase durations.
 */

import { useState, type FormEvent } from 'react';
import SEO from '@/components/SEO';
import { Layout } from '@/components-v2/layout';
import { HeroCentric, StepStack, CTAStrip } from '@/components-v2/sections';
import {
  Card,
  Input,
  Select,
  Textarea,
  Lede,
  MonoBadge,
} from '@/components-v2/ui';
import { cn } from '@/lib/utils';
import { INDUSTRIES } from '@/lib/data';

export interface CustomWorkshopFormData {
  orgSize: string;
  industry: string;
  goals: string;
  format: string;
  budget: string;
  name: string;
  email: string;
}

const ORG_SIZE_OPTIONS = [
  { value: '1-10', label: '1–10' },
  { value: '11-50', label: '11–50' },
  { value: '51-200', label: '51–200' },
  { value: '200+', label: '200+' },
];

const FORMAT_OPTIONS = [
  { value: 'in-person', label: 'In-person' },
  { value: 'remote', label: 'Remote' },
  { value: 'hybrid', label: 'Hybrid' },
];

const BUDGET_OPTIONS = [
  { value: 'under-5k', label: 'Under $5k' },
  { value: '5-15k', label: '$5–15k' },
  { value: '15-30k', label: '$15–30k' },
  { value: '30k+', label: '$30k+' },
  { value: 'not-sure', label: 'Not sure' },
];

// Scoping phases rendered by the StepStack. Mirrors the shape used on
// ServiceDetail so the page reads as part of the same engagement system.
// TODO: founder to validate — durations are drafted 2026-04-22.
const SCOPING_STEPS = [
  {
    title: 'Intake call',
    body: "A 30-minute call on your requirements. We don't pitch — we listen for what you're actually trying to solve and who's going to own it.",
    duration: '30 min',
  },
  {
    title: 'Workflow audit',
    body: "We shadow your team for half a day. Real tasks, real tools, real constraints — so the workshop we scope matches the ground you're standing on.",
    duration: 'Half day',
  },
  {
    title: 'Scope doc',
    body: 'Fixed price, fixed timeline, no surprises. A 2-page scope doc covering what we cover, what we leave, and what your team walks away with.',
    duration: '48 hrs',
  },
  {
    title: 'Decision',
    body: 'You pick a workshop shape, or we revise once. If the scope still isn\'t right after a revision, we hand you back to the catalog — no hard sell.',
    duration: 'Your call',
  },
];

// Shared button style — matches the Button primary+lg variant used
// elsewhere (BookingForm, ContactForm). Kept inline so this form stays a
// self-contained page-local component.
const buttonBase =
  'inline-flex items-center gap-2 font-semibold rounded-md ' +
  'px-[22px] py-[14px] text-[15px] ' +
  'transition-[transform,background-color,filter] duration-[180ms] ' +
  'ease-[cubic-bezier(0.2,0.9,0.2,1)] ' +
  'hover:-translate-y-px active:translate-y-0 active:brightness-[.96] ' +
  'disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:translate-y-0 ' +
  'focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2 ' +
  'cursor-pointer';
const primaryBtn = cn(buttonBase, 'bg-blue text-paper border-0 hover:bg-blue-deep');

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// Stub submit handler — same pattern as Contact / Book / WorkshopDetail.
// TODO: wire real backend in Phase 12.
const handleSubmit = async (data: CustomWorkshopFormData): Promise<void> => {
  // eslint-disable-next-line no-console
  console.log('[v2 custom workshop submit]', data);
  await new Promise<void>((resolve) => setTimeout(resolve, 500));
};

export default function CustomWorkshop() {
  const [data, setData] = useState<CustomWorkshopFormData>({
    orgSize: '',
    industry: '',
    goals: '',
    format: '',
    budget: '',
    name: '',
    email: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [succeeded, setSucceeded] = useState(false);

  const update = <K extends keyof CustomWorkshopFormData>(
    key: K,
    value: CustomWorkshopFormData[K],
  ) => {
    setData((prev) => ({ ...prev, [key]: value }));
  };

  const valid =
    Boolean(data.goals.trim()) &&
    Boolean(data.name.trim()) &&
    Boolean(data.email) &&
    EMAIL_RE.test(data.email);

  const onFormSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!valid || submitting) return;
    setSubmitting(true);
    try {
      await handleSubmit(data);
      setSucceeded(true);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Layout>
      <SEO
        title="Custom workshop"
        description="Built from your actual workflow. We scope a workshop from your team's real tasks, tools, and constraints — not a generic deck."
      />

      <HeroCentric
        eyebrow="Custom workshop"
        title="Built from your actual workflow."
        lede="Generic case studies don't help. We scope a workshop from your team's real tasks, tools, and constraints."
      />

      {/* Requirements form — paper-2 Card constrained to readable width. */}
      <section className="py-12 lg:py-24">
        <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
          <div className="mx-auto max-w-2xl">
            {succeeded ? (
              <Card tone="paper-2" aria-live="polite">
                <h2 className="font-semibold text-[22px] leading-tight text-ink">
                  Thanks — we&apos;ll be in touch.
                </h2>
                <Lede className="mt-3">
                  Your custom workshop request is in. A named practitioner
                  will reply within one business day to book the intake call.
                </Lede>
              </Card>
            ) : (
              <Card tone="paper-2">
                <div className="mb-5">
                  <MonoBadge>Scope request</MonoBadge>
                </div>
                <form className="flex flex-col gap-4" onSubmit={onFormSubmit} noValidate>
                  <Select
                    label="Org size"
                    value={data.orgSize}
                    onChange={(e) => update('orgSize', e.target.value)}
                  >
                    <option value="" disabled>
                      Choose one
                    </option>
                    {ORG_SIZE_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </Select>

                  <Select
                    label="Industry"
                    value={data.industry}
                    onChange={(e) => update('industry', e.target.value)}
                  >
                    <option value="" disabled>
                      Choose one
                    </option>
                    {/* Industries ported from INDUSTRIES in lib/data.ts so
                        the taxonomy stays aligned across the site. */}
                    {INDUSTRIES.map((industry) => (
                      <option key={industry.slug} value={industry.slug}>
                        {industry.title}
                      </option>
                    ))}
                    <option value="other">Other</option>
                  </Select>

                  <Textarea
                    label="Goals *"
                    rows={4}
                    value={data.goals}
                    onChange={(e) => update('goals', e.target.value)}
                    required
                    hint="Describe what success looks like — what does your team walk away able to do?"
                  />

                  <Select
                    label="Preferred format"
                    value={data.format}
                    onChange={(e) => update('format', e.target.value)}
                  >
                    <option value="" disabled>
                      Choose one
                    </option>
                    {FORMAT_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </Select>

                  <Select
                    label="Budget range"
                    value={data.budget}
                    onChange={(e) => update('budget', e.target.value)}
                  >
                    <option value="" disabled>
                      Choose one
                    </option>
                    {BUDGET_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </Select>

                  <Input
                    label="Name *"
                    type="text"
                    value={data.name}
                    onChange={(e) => update('name', e.target.value)}
                    required
                    autoComplete="name"
                  />

                  <Input
                    label="Email *"
                    type="email"
                    value={data.email}
                    onChange={(e) => update('email', e.target.value)}
                    required
                    autoComplete="email"
                  />

                  <div className="mt-2">
                    <button
                      type="submit"
                      className={primaryBtn}
                      disabled={!valid || submitting}
                    >
                      {submitting ? 'Sending...' : 'Request scope call'}
                      {!submitting && <span aria-hidden>→</span>}
                    </button>
                  </div>
                </form>
              </Card>
            )}
          </div>
        </div>
      </section>

      <StepStack
        eyebrow="How we scope"
        sectionTitle="Four steps from question to scope."
        steps={SCOPING_STEPS}
      />

      <CTAStrip
        tone="paper"
        title="Questions before the form?"
        lede="If you'd rather talk through the shape first, book a 20-minute call. No sales pitch, and no pressure to fill anything in afterwards."
        primaryCta={{ label: 'Book a call', href: '/contact' }}
      />
    </Layout>
  );
}
