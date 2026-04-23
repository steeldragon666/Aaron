/**
 * Industries.tsx — v2 Industries overview page.
 *
 * Strategic pivot (2026-04-22): drops the generic industry catalog in favour
 * of the three verticals we actually serve via Pillar 1 (Vertical SaaS) —
 * bioenergy & agribusiness, sovereign defence & industrial supply chain, and
 * mental health & NDIS-funded care. The page still acknowledges that our
 * Pillar 2 workforce and Pillar 3 Companion work horizontally, so non-vertical
 * prospects still have a route in.
 *
 * Composition:
 *   HeroCentric → 3-up vertical card grid (paper) →
 *   InkSection "Why these" (single pacer) →
 *   "Not your industry?" Section → CTAStrip
 *
 * Each vertical card links directly to its `/services/:slug` detail page,
 * not a separate `/industries/:slug` — they're the same wedges.
 *
 * TODO: copy drafted 2026-04-22 — founder to validate claims, especially
 * the ABFI / Check-ys / ASCA specifics and any regulatory references.
 */

import { Link } from 'wouter';
import SEO from '@/components/SEO';
import { Layout, InkSection, Section } from '@/components-v2/layout';
import { HeroCentric, CTAStrip } from '@/components-v2/sections';
import { Card, CTALink, Eyebrow, Lede } from '@/components-v2/ui';
import { Sprout, Shield, HeartHandshake, type LucideIcon } from 'lucide-react';

// The three verticals Pillar 1 goes deep in. Each `href` resolves to the
// matching SERVICES entry in lib/data.ts so "Learn more →" doesn't 404.
const VERTICALS: Array<{
  icon: LucideIcon;
  title: string;
  description: string;
  href: string;
}> = [
  {
    icon: Sprout,
    title: 'Bioenergy & agribusiness',
    description:
      'Bankability, feedstock matching, CORSIA compliance, R&D grants. For producers, financiers, and regulators moving billions through the energy transition.',
    href: '/services/bioenergy',
  },
  {
    icon: Shield,
    title: 'Sovereign defence & industrial supply chain',
    description:
      "Speaks ASCA, DIDG, R&DTI. For prime contractors, defence-supply SMEs, and government buyers who can't send their data to California.",
    href: '/services/defence',
  },
  {
    icon: HeartHandshake,
    title: 'Mental health & NDIS-funded care',
    description:
      'Built around the realities of funded care — not an afterthought bolted onto a general-purpose tool. For NDIS providers, allied health practitioners, and participants.',
    href: '/services/mental-health',
  },
];

export default function Industries() {
  return (
    <Layout>
      <SEO
        title="Industries"
        description="Three verticals we go deep in: bioenergy & agribusiness, sovereign defence & industrial supply chain, and mental health & NDIS-funded care."
      />

      <HeroCentric
        eyebrow="Industries"
        title="Three verticals we go deep in."
        lede="We don't try to be horizontal. We pick industries where we have unfair advantage, then build the products, data, and tooling they actually need."
      />

      {/* 3-up vertical card grid — collapses to 1-col on mobile. Each card
          links to its /services/:slug detail page, not /industries/:slug. */}
      <Section>
        <div className="grid md:grid-cols-3 gap-6">
          {VERTICALS.map((vertical) => {
            const Icon = vertical.icon;
            return (
              <Card key={vertical.title} className="flex flex-col">
                <Icon className="h-8 w-8 text-blue" aria-hidden />
                <h3 className="mt-5 font-semibold text-[22px] leading-tight text-ink">
                  {vertical.title}
                </h3>
                <p className="mt-3 text-ink-2">{vertical.description}</p>
                <CTALink
                  href={vertical.href}
                  className="mt-5 text-blue"
                >
                  Learn more
                </CTALink>
              </Card>
            );
          })}
        </div>
      </Section>

      {/* Why these — the page's one InkSection, per the design-system rule
          of at most one per page. Acts as a mid-page pacer. */}
      <InkSection
        eyebrow="WHY THESE"
        title="Consequential, regulated, underserved."
      >
        <div className="max-w-3xl mx-auto">
          <p className="text-paper/85 text-[18px] leading-relaxed mb-4">
            Every one of these industries carries real-world weight — energy
            transition, national security, mental health outcomes. None of
            them are well served by generic AI tooling that treats their
            compliance, data, and workflow realities as edge cases.
          </p>
          <p className="text-paper/85 text-[18px] leading-relaxed">
            That&apos;s the wedge. Build the tool that actually speaks the
            language. Operate it as a managed service so the customer
            doesn&apos;t carry the ML ops burden. Let the industry keep its
            sovereignty.
          </p>
        </div>
      </InkSection>

      {/* Not your industry? — short, honest off-ramp for horizontal prospects
          toward Pillars 2 and 3. Centered in a paper-2 tone for pacing. */}
      <Section tone="paper-2">
        <div className="max-w-3xl mx-auto text-center">
          <Eyebrow className="mb-3 block">NOT YOUR INDUSTRY?</Eyebrow>
          <h2 className="font-semibold text-[32px] leading-tight text-ink mb-4">
            The Workforce and the Companion work everywhere.
          </h2>
          <Lede className="mb-6">
            Our Pillar 2 agents (AI-EA, Associate, Operator, BDR, Compliance,
            Engineer) and Pillar 3 Companion (Omni) aren&apos;t vertical-bound.
            They work for any organisation that wants real AI agency without
            being locked into Microsoft or Google.
          </Lede>
          <Link
            href="/services"
            className="inline-flex items-center gap-2 text-ink font-medium border-b border-ink/20 hover:border-ink pb-1 transition-colors"
          >
            See all services <span aria-hidden>→</span>
          </Link>
        </div>
      </Section>

      <CTAStrip
        tone="paper"
        title="Does your industry fit?"
        lede="Twenty minutes. We'll tell you whether we should build something for you, or point you at someone who should."
        primaryCta={{ label: 'Book a call', href: '/book' }}
      />
    </Layout>
  );
}
