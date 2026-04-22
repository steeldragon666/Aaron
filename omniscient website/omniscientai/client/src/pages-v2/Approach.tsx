/**
 * Approach.tsx — v2 Approach/methodology page.
 *
 * Strategic pivot (2026-04-22): the old "three weeks, one artefact, no
 * lock-in" framing was consulting-first. This page now reflects the
 * product + managed-service reality: products you subscribe to, agents
 * you hire per month, a sovereign platform we operate for you. The four
 * phases describe how a typical engagement unfolds for either a net-new
 * product buildout or an agent onboarding.
 *
 * Composition:
 *   HeroCentric → StepStack (4 phases with MonoBadge durations) →
 *   Principles grid (6-up mini Cards) → CTAStrip
 *
 * Route mirrors the legacy site: /about/approach.
 *
 * TODO: copy drafted 2026-04-22 — founder to validate tone, durations,
 * and the specific sovereign-hosting / no-kickbacks / managed-service
 * commitments.
 */

import SEO from '@/components/SEO';
import { Layout, Section } from '@/components-v2/layout';
import { HeroCentric, StepStack, CTAStrip } from '@/components-v2/sections';
import { Card } from '@/components-v2/ui';

// Four phases that hold across product buildouts and agent onboardings.
// StepStack auto-prefixes "01 / 02 / ..." numerals, so titles stay as
// plain nouns here — don't repeat the numeral in the title string.
// TODO: founder to validate — durations are a rhythm, not a contract.
const PHASES = [
  {
    title: 'Scope',
    body: "We spend 30-60 minutes on your actual situation — not a sales qualification call. If it's a product you should subscribe to, we route you there. If it's something we should build or an agent configuration we should onboard, we scope it.",
    duration: 'Week 0',
  },
  {
    title: 'Prototype',
    body: 'For new products: we build the smallest thing that proves the thesis, in two weeks. For agent onboarding: we configure, tune, and smoke-test one persona before expanding.',
    duration: 'Weeks 1-2',
  },
  {
    title: 'Operate',
    body: 'We run it. Monitoring, tuning, alerts, escalations — the things that make the difference between an AI that works and an AI that embarrasses you. You use the output.',
    duration: 'Ongoing',
  },
  {
    title: 'Expand',
    body: 'Once one thing is working, we scale the account: more personas, more verticals, the Companion for your execs. Or we leave well enough alone — boutique means knowing when to stop.',
    duration: 'When it makes sense',
  },
];

// Six load-bearing principles. Reflect the sovereign + managed-service
// + no-kickbacks positioning, not the old consulting boilerplate.
// TODO: founder to validate — the "Australian sovereign infra" claim
// especially should be tightened once the hosting story is nailed down.
const PRINCIPLES = [
  {
    title: 'Australian sovereign infra',
    body: "Our hosting stays in Australia by default. For defence and government, that's non-negotiable.",
  },
  {
    title: 'We operate what we build',
    body: "Managed service is the default. No hand-offs to a team that didn't build it.",
  },
  {
    title: 'Products over projects',
    body: 'Where we can, we sell you a subscription instead of a consulting engagement. Cheaper for you, better margins for us.',
  },
  {
    title: 'Human-in-the-loop, always',
    body: 'Agents run. Humans supervise. The one you call is still a person.',
  },
  {
    title: 'No kickbacks, ever',
    body: 'We have no reseller agreements. Vendor recommendations are honest.',
  },
  {
    title: 'Named practitioners',
    body: 'You get the senior person for the whole engagement. No junior bait-and-switch.',
  },
];

export default function Approach() {
  return (
    <Layout>
      <SEO
        title="Our approach"
        description="We build. We operate. You use. How a typical engagement unfolds — four phases that work across product buildouts and managed agent onboarding — plus the principles that sit underneath."
      />

      <HeroCentric
        eyebrow="Approach"
        title="We build. We operate. You use."
        lede="Our model is products you subscribe to, agents you hire per month, and a sovereign platform we run for you. Below is how a typical engagement unfolds when we build or onboard something together."
      />

      <StepStack
        eyebrow="The cycle"
        sectionTitle="Four phases. One rhythm."
        lede="A shape, not a straitjacket — the specifics flex to whether we're building something net-new or onboarding an agent, but the rhythm and the accountability don't."
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
        title="Ready to see how we'd work with you?"
        lede="Twenty-minute scope call. No slides. We figure out what fits and what doesn't."
        primaryCta={{ label: 'Book a call', href: '/book' }}
      />
    </Layout>
  );
}
