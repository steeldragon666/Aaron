/**
 * Approach.tsx — v2 Approach/methodology page.
 *
 * Detailed view of how we work — the four-phase engagement cycle and the
 * principles that sit underneath it. Composed from existing primitives:
 *
 *   HeroCentric → StepStack (4 phases with MonoBadge durations) →
 *   Principles grid (6-up mini Cards) → CTAStrip
 *
 * Route mirrors the legacy site: /about/approach.
 *
 * TODO: copy drafted 2026-04-22 — founder to validate tone and specifics
 * of the engagement cadence (weeks 3-6 is a rough scope band; real
 * engagements may flex).
 */

import SEO from '@/components/SEO';
import { Layout, Section } from '@/components-v2/layout';
import { HeroCentric, StepStack, CTAStrip } from '@/components-v2/sections';
import { Card } from '@/components-v2/ui';

// TODO: founder to validate engagement cadence — durations are placeholder.
// StepStack's `duration` prop renders as a MonoBadge next to the step title.
const PHASES = [
  {
    title: 'Discover',
    body: "We spend a week with your team. No assumptions, no SKU-pitching — we map what's actually happening, what's in the way, and where AI could meaningfully help.",
    duration: 'Week 1',
  },
  {
    title: 'Design',
    body: 'We scope the smallest thing that could deliver real value in a quarter, not a year. Co-designed with the people who will own it — not handed down in a slide deck.',
    duration: 'Week 2',
  },
  {
    title: 'Deliver',
    body: "Short sprints. You see working code every week, not status slides. We ship to your environment, against your data, with eval harnesses that stick around after we leave.",
    duration: 'Weeks 3-6',
  },
  {
    title: 'Embed',
    body: "We train your team to own what we built. Documentation, runbooks, and pairing sessions until the hand-over is real. The artefact stays; we leave.",
    duration: 'Ongoing',
  },
];

// TODO: founder to validate principles — drafted 2026-04-22.
// Six load-bearing principles that underpin how every engagement runs.
const PRINCIPLES = [
  {
    title: 'No junior bait-and-switch',
    body: 'The person who pitched the work is the person doing the work. No partner-sells-then-disappears.',
  },
  {
    title: 'Ship small, ship often',
    body: "You see working code every week — not a big-bang reveal at month three. If something's off, we catch it early.",
  },
  {
    title: 'Write code alongside your team',
    body: 'We pair with your engineers, not around them. Knowledge transfer is the work, not a phase at the end.',
  },
  {
    title: 'Budget caps, always',
    body: "Every engagement has a ceiling agreed up front. If we're burning through it, we stop and talk — we don't quietly extend the invoice.",
  },
  {
    title: 'Vendor-neutral recommendations',
    body: "No reseller agreements, no rebate schemes. When we recommend a tool it's because it fits your team and your data.",
  },
  {
    title: 'If we don\'t know, we say so',
    body: "We'd rather tell you the honest answer than invent one. That includes telling you when the right move is to not build something.",
  },
];

export default function Approach() {
  return (
    <Layout>
      <SEO
        title="Our approach"
        description="Three weeks. One artefact. No lock-in. How we run engagements — a four-phase methodology (Discover, Design, Deliver, Embed) and the principles that sit underneath."
      />

      <HeroCentric
        eyebrow="Approach"
        title="Three weeks. One artefact. No lock-in."
        lede="Every engagement runs the same four-phase cycle. We scope tight, build in the open, hand over ownership, and get out of the way. No retainers, no rebate kickbacks, no open-ended scope creep."
      />

      <StepStack
        eyebrow="The cycle"
        sectionTitle="Four phases. Roughly six weeks."
        lede="A shape, not a straitjacket — the specifics flex to the engagement, but the rhythm and the accountability don't."
        steps={PHASES}
      />

      {/* Principles grid — 3-up on lg, 2-up on md, stacked on mobile. Six
          mini Cards, each a principle that holds across every engagement. */}
      <Section
        eyebrow="How we hold ourselves accountable"
        title="The principles underneath."
        lede="Process is just the shape. These are the rules we enforce on ourselves — and the ones that tend to matter most when things get hard."
        tone="paper-2"
      >
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {PRINCIPLES.map((principle) => (
            <Card key={principle.title} className="flex flex-col">
              <h3 className="font-semibold text-[20px] leading-tight text-ink">
                {principle.title}
              </h3>
              <p className="mt-3 text-ink-2">{principle.body}</p>
            </Card>
          ))}
        </div>
      </Section>

      <CTAStrip
        tone="paper"
        title="See if the fit is right."
        lede="A 20-minute call, free. If the work isn't right for us, we'll tell you who else to talk to."
        primaryCta={{ label: 'Book a call', href: '/book' }}
      />
    </Layout>
  );
}
