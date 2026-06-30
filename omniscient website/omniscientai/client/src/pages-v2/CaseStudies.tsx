/**
 * CaseStudies.tsx — v2 Case studies overview page.
 *
 * Fixes the /_v2/case-studies 404 from the nav by standing up a real
 * overview surface. Pillar-organised grid: three Pillar 1 vertical SaaS
 * cases up top, three Pillar 2 Workforce cases below, with a single
 * InkSection between to articulate the shared pattern, then a closing
 * CTA.
 *
 * Composition:
 *   HeroCentric → CaseGrid (Pillar 1 verticals) → CaseGrid (Pillar 2
 *   workforce) → InkSection "The pattern" → CTAStrip
 *
 * Each case links to the matching /services/:slug product page so the
 * overview can double as a directed traffic source into Pillar 1/2
 * deep pages. Content is placeholder until we have named + approved
 * cases — flagged below.
 */

import SEO from '@/components/SEO';
import { Layout, InkSection } from '@/components-v2/layout';
import { HeroCentric, CaseGrid, CTAStrip } from '@/components-v2/sections';
import { BrainGraphic } from '@/components-v2/brand';

// TODO: replace with real named + approved cases — drafted 2026-04-23,
// currently placeholder. Numbers are illustrative and must be validated
// before anything is published externally.
const VERTICAL_CASES = [
  {
    industry: 'Bioenergy',
    title: 'CORSIA compliance reporting in weeks, not months',
    outcome:
      'An ASX-listed energy producer cut their annual attestation cycle from 14 weeks to 3 with automated evidence capture.',
    href: '/services/bioenergy',
  },
  {
    industry: 'Defence supply',
    title: 'Bankability analysis for a prime contractor shortlist',
    outcome:
      'Shortened the vetting of 42 Tier-2 suppliers from a 6-week manual review to an overnight automated pass with human review of only 7 edge cases.',
    href: '/services/defence',
  },
  {
    industry: 'Mental health',
    title: 'NDIS-compliant session notes at practitioner speed',
    outcome:
      'Allied health team saved 8 hours a week per practitioner on documentation while raising audit-pass rates from 78% to 97%.',
    href: '/services/mental-health',
  },
];

// TODO: replace with real named + approved cases — drafted 2026-04-23,
// currently placeholder.
const WORKFORCE_CASES = [
  {
    industry: 'Executive ops',
    title: 'AI-EA for a CEO of a listed industrial firm',
    outcome:
      'Inbox triaged, calendar actively managed, and meeting briefs prepped — recovering ~12 hours per week for strategic work.',
    href: '/services/workforce',
  },
  {
    industry: 'R&D compliance',
    title: 'AI Compliance Officer for an R&DTI claim',
    outcome:
      'Defensible activity records generated continuously through the year, reducing claim prep from 2 weeks to 2 days.',
    href: '/services/workforce',
  },
  {
    industry: 'Sales ops',
    title: 'AI BDR supporting a 3-person founding team',
    outcome:
      'Outbound sequences for 300+ prospects/week while the founders stayed in flow on product. Generated 8 qualified discovery calls in month one.',
    href: '/services/workforce',
  },
];

export default function CaseStudies() {
  return (
    <Layout>
      <SEO
        title="Case studies — OmniscientAI"
        description="How we've applied sovereign AI across bioenergy, defence, and mental health."
      />

      <HeroCentric
        eyebrow="Case studies"
        title="Sovereign AI in practice."
        lede="Real work with Australian organisations across our three pillars. Anonymised where we have to, named where we can."
      />

      <CaseGrid
        eyebrow="VERTICAL SAAS"
        sectionTitle="Pillar 1 — Products in production."
        cases={VERTICAL_CASES}
      />

      {/* Visual beat between the two CaseGrids — a cropped horizontal band
          of the connectome brand graphic, faded so it pacing-breaks without
          stealing focus. aria-hidden via BrainGraphic. */}
      <div className="flex justify-center py-4">
        <BrainGraphic
          variant="horizontal"
          size="section"
          className="opacity-30 w-full max-w-[640px]"
        />
      </div>

      <CaseGrid
        eyebrow="WORKFORCE"
        sectionTitle="Pillar 2 — Agents at work."
        cases={WORKFORCE_CASES}
      />

      {/* Sovereign + managed-service callout — single InkSection per page
          per the design system rule. Articulates the shared pattern across
          everything above. */}
      <InkSection eyebrow="THE PATTERN" title="What's common across every engagement.">
        <div className="max-w-3xl mx-auto">
          <p className="text-paper/85 text-[18px] leading-relaxed mb-4">
            Every one starts with a customer who needs AI to <em>do work</em>,
            not chat. Every one runs on Australian infrastructure. And every
            one has an ops layer — us — supervising, tuning, and escalating
            when the agent hits its edges.
          </p>
          <p className="text-paper/85 text-[18px] leading-relaxed">
            That pattern is what the platform is.
          </p>
        </div>
      </InkSection>

      <CTAStrip
        tone="paper"
        title="Could this be your case study next?"
        lede="Twenty minutes. We'll tell you what we could build for you, and what it costs."
        primaryCta={{ label: 'Book a call', href: '/book' }}
      />
    </Layout>
  );
}
