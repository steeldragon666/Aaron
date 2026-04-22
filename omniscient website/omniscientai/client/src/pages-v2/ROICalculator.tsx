/**
 * ROICalculator.tsx — v2 AI ROI calculator (/roi-calculator).
 *
 * Simple live-update tool that estimates time and cost savings from AI
 * automation. Five inputs (industry, team size, hours/week on manual tasks,
 * hourly rate, efficiency gain) feed a rough formula and render the key
 * numbers in a paper-2 Card on the right.
 *
 *   Layout → HeroCentric (narrow) → 2-column grid:
 *     · Inputs Card (left)  — Select + four Sliders
 *     · Results Card (right) — MonoBadge hrs/week + Display annual savings
 *                              + payback sentence + disclaimer
 *   → CTAStrip → /book
 *
 * The legacy ROICalculator used a more complex formula (employees × hours
 * × rate × industry automation rate × 48 weeks, plus an implementation cost
 * + ROI percent). We simplified to the formula in the phase 10 spec — an
 * efficiency-gain slider that the user controls directly — because the new
 * v2 design language is "rough estimate, not a quote". Industry is kept as
 * a Select for continuity but is not used in the math by default. Payback
 * assumes a flat $10k engagement cost (the low end of our typical scoping).
 *
 * Product UI — semantic accents (--blue for savings emphasis) are allowed.
 *
 * TODO: copy drafted 2026-04-22 — founder to validate formulas and the
 * $10k payback anchor against actual engagement pricing.
 */

import { useMemo, useState } from 'react';
import SEO from '@/components/SEO';
import { Layout } from '@/components-v2/layout';
import { HeroCentric, CTAStrip } from '@/components-v2/sections';
import {
  Card,
  Eyebrow,
  MonoBadge,
  Select,
  Slider,
} from '@/components-v2/ui';
import { INDUSTRIES } from '@/lib/data';

// AUD currency formatting. Intl.NumberFormat gives us the thousands separator
// automatically — we prefix the "$" ourselves and suffix " AUD" so the number
// reads naturally alongside the other mono-numerals in the results Card.
const audFormatter = new Intl.NumberFormat('en-AU', {
  maximumFractionDigits: 0,
});

function formatAud(value: number): string {
  return `$${audFormatter.format(Math.round(value))} AUD`;
}

// Payback period assumes $10k engagement cost — see the payback sentence
// comment in the JSX below.
const DEFAULT_PAYBACK_COST = 10_000;

function formatPayback(annualSavings: number): string {
  if (annualSavings <= 0) {
    return "Hard to estimate payback at these numbers — adjust the sliders to see a range.";
  }
  const months = DEFAULT_PAYBACK_COST / (annualSavings / 12);
  if (months < 1) {
    return 'Pays back in under a month at a typical $10k engagement.';
  }
  return `Pays back in ~${Math.round(months)} month${Math.round(months) === 1 ? '' : 's'} at a typical $10k engagement.`;
}

export default function ROICalculator() {
  const [industry, setIndustry] = useState<string>(INDUSTRIES[0]?.slug ?? '');
  const [teamSize, setTeamSize] = useState(20);
  const [hoursPerWeek, setHoursPerWeek] = useState(15);
  const [hourlyRate, setHourlyRate] = useState(150);
  const [efficiencyGain, setEfficiencyGain] = useState(30);

  const results = useMemo(() => {
    const hoursSavedPerWeek =
      (teamSize * hoursPerWeek * efficiencyGain) / 100;
    const annualHoursSaved = hoursSavedPerWeek * 52;
    const annualSavings = annualHoursSaved * hourlyRate;
    return {
      hoursSavedPerWeek,
      annualHoursSaved,
      annualSavings,
    };
  }, [teamSize, hoursPerWeek, efficiencyGain, hourlyRate]);

  return (
    <Layout>
      <SEO
        title="AI ROI Calculator"
        description="Rough estimate of what AI could save your team in under 30 seconds. Not a quote — just a reality check."
      />

      <HeroCentric
        eyebrow="Calculator"
        title="What could AI save your team?"
        lede="Rough estimate in under 30 seconds. Not a quote — just a reality check."
      />

      <section className="pb-16 lg:pb-24">
        <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
          <div className="grid gap-8 lg:grid-cols-2">
            {/* Inputs */}
            <Card tone="paper-2" className="flex flex-col gap-6">
              <div>
                <Eyebrow className="mb-3 block">Your team</Eyebrow>
                <h2 className="font-semibold text-[22px] leading-tight text-ink">
                  Tell us the shape.
                </h2>
              </div>

              <Select
                label="Industry"
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                hint="We use this for context — the numbers below are what actually drive the estimate."
              >
                {INDUSTRIES.map((ind) => (
                  <option key={ind.slug} value={ind.slug}>
                    {ind.title}
                  </option>
                ))}
                <option value="other">Other</option>
              </Select>

              <Slider
                label="Team size"
                min={1}
                max={200}
                value={teamSize}
                onChange={(e) => setTeamSize(Number(e.target.value))}
                valueDisplay={(v) => `${v} people`}
                data-testid="team-size-slider"
              />

              <Slider
                label="Hours/week on manual tasks"
                min={0}
                max={40}
                value={hoursPerWeek}
                onChange={(e) => setHoursPerWeek(Number(e.target.value))}
                valueDisplay={(v) => `${v} hrs/week`}
                hint="Per person — rough guess is fine."
                data-testid="hours-slider"
              />

              <Slider
                label="Average hourly rate"
                min={50}
                max={500}
                value={hourlyRate}
                onChange={(e) => setHourlyRate(Number(e.target.value))}
                valueDisplay={(v) => `$${v} AUD`}
                data-testid="rate-slider"
              />

              <Slider
                label="Estimated efficiency gain"
                min={5}
                max={80}
                value={efficiencyGain}
                onChange={(e) => setEfficiencyGain(Number(e.target.value))}
                valueDisplay={(v) => `${v}%`}
                hint="How much time AI might save on those manual tasks."
                data-testid="efficiency-slider"
              />
            </Card>

            {/* Results */}
            <Card tone="paper" className="flex flex-col gap-8">
              <div>
                <Eyebrow className="mb-3 block">Estimated savings</Eyebrow>
                <h2 className="font-semibold text-[22px] leading-tight text-ink">
                  What that could look like.
                </h2>
              </div>

              <div className="flex flex-col gap-2">
                <span className="text-[14px] font-medium text-ink-3">
                  Hours saved per week
                </span>
                <div>
                  <MonoBadge
                    className="text-[20px] px-3 py-1.5"
                    data-testid="hours-saved"
                  >
                    {Math.round(results.hoursSavedPerWeek)} hrs/week
                  </MonoBadge>
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <span className="text-[14px] font-medium text-ink-3">
                  Annual cost savings
                </span>
                <div
                  className="font-bold text-[48px] lg:text-[64px] leading-none tracking-[-0.02em] text-blue"
                  style={{ fontFamily: 'var(--font-mono)' }}
                  data-testid="annual-savings"
                >
                  {formatAud(results.annualSavings)}
                </div>
              </div>

              <div className="flex flex-col gap-2 pt-2 border-t border-line">
                <span className="text-[14px] font-medium text-ink-3">
                  Payback period
                </span>
                <p className="text-ink-2 leading-relaxed">
                  {formatPayback(results.annualSavings)}
                </p>
              </div>

              <p className="text-[13px] text-ink-3 leading-relaxed">
                These are rough estimates based on the numbers you picked —
                real engagements vary with implementation quality, use-case
                selection, and how much of the gain sticks after hand-over.
              </p>
            </Card>
          </div>
        </div>
      </section>

      <CTAStrip
        tone="ink"
        title="Ready for real numbers?"
        lede="The calculator is deliberately rough. A 20-minute scoping call is free and gives you a proper estimate — what would actually move, what wouldn't, and what that might cost."
        primaryCta={{ label: 'Book a scoping call', href: '/book' }}
      />
    </Layout>
  );
}
