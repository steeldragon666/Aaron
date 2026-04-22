/**
 * Home.tsx — v2 marketing home page.
 *
 * Strategic pivot (2026-04-22): repositioned from "vendor-neutral AI training
 * and consulting" to "Australia's sovereign applied AI company" around three
 * pillars:
 *
 *   1. Vertical SaaS for consequential industries (bioenergy, defence, mental
 *      health) — rendered via PillarGrid.
 *   2. The Omniscient Workforce — business agents as a service. Rendered as
 *      a custom 3-col persona grid because PillarGrid doesn't support
 *      subtitles.
 *   3. The Companion (Omni) — phone-native AI. Rendered in an InkSection for
 *      visual weight; it's the most distinctive pillar.
 *
 * Consulting/workshops is retained as a small, de-emphasised "also" section
 * so the linkable path exists without owning the headline.
 *
 * Composition:
 *   HeroSplit → TaglineBar → PillarGrid (Pillar 1) →
 *   Custom Section (Pillar 2) → InkSection (Pillar 3) →
 *   "Also" consulting Section → CaseGrid → StatsRow → TestimonialStrip → CTAStrip
 *
 * TODO: founder to validate copy — drafted 2026-04-22. Case studies, stats,
 * and testimonials still point at the same legacy content; they are flagged
 * for a follow-up pass once real pillar-specific material exists.
 */

import { Link } from 'wouter';
import SEO from '@/components/SEO';
import { Layout, InkSection, Section } from '@/components-v2/layout';
import { TaglineBar, BrainGraphic } from '@/components-v2/brand';
import {
  HeroSplit,
  PillarGrid,
  CaseGrid,
  StatsRow,
  TestimonialStrip,
  CTAStrip,
} from '@/components-v2/sections';
import { Card, Eyebrow, Lede } from '@/components-v2/ui';
import {
  Sprout,
  Shield,
  HeartHandshake,
  UserCircle2,
  BookOpen,
  Workflow,
  Megaphone,
  FileCheck,
  Code2,
} from 'lucide-react';

// Pillar 1 — Vertical SaaS. Each entry maps to a SERVICES slug in
// lib/data.ts so "Learn more →" resolves instead of 404ing.
const VERTICAL_SAAS_PILLARS = [
  {
    icon: Sprout,
    title: 'Bioenergy & agribusiness intelligence',
    description:
      'ABFI — bankability, feedstock matching, CORSIA compliance, grants. For producers, financiers, and regulators. The wedge is already cutting.',
    href: '/services/bioenergy',
  },
  {
    icon: Shield,
    title: 'Sovereign defence & industrial supply chain',
    description:
      'Speaks ASCA, DIDG, R&DTI. For prime contractors, defence-supply SMEs, and government buyers. Sovereign by default.',
    href: '/services/defence',
  },
  {
    icon: HeartHandshake,
    title: 'Mental health & NDIS-funded care',
    description:
      'Check-ys is the wedge. For NDIS providers, allied health practitioners, and participants. Built around the realities of funded care.',
    href: '/services/mental-health',
  },
];

// Pillar 2 — The Omniscient Workforce. Rendered as a custom 3-col card grid
// because PillarGrid doesn't surface subtitles and we want the role label
// under each persona name.
const WORKFORCE_PERSONAS = [
  {
    icon: UserCircle2,
    title: 'AI-EA',
    subtitle: 'Executive assistant',
    description:
      'Calendar, email, drafting, scheduling. The flagship persona.',
  },
  {
    icon: BookOpen,
    title: 'AI Associate',
    subtitle: 'Analyst / research',
    description: 'Brief synthesis, desk research, memo writing.',
  },
  {
    icon: Workflow,
    title: 'AI Operator',
    subtitle: 'Workflow execution',
    description:
      'Tickets, updates, reporting loops. Things that have to happen.',
  },
  {
    icon: Megaphone,
    title: 'AI BDR',
    subtitle: 'Prospecting & outreach',
    description: 'Inbound qualification, outbound sequencing.',
  },
  {
    icon: FileCheck,
    title: 'AI Compliance Officer',
    subtitle: 'Audits, reporting, grants',
    description: 'Boring in the best way.',
  },
  {
    icon: Code2,
    title: 'AI Engineer',
    subtitle: 'Code + devops',
    description: 'Ships. Ops. Reviews. Does not complain.',
  },
];

// TODO: replace with real case studies aligned to the three pillars before
// launch. Current entries carried over from the legacy Home — kept to avoid
// an empty CaseGrid, but founder should swap these for bioenergy / defence /
// mental-health and Workforce deployments.
const CASES = [
  {
    industry: 'Financial services',
    title: 'Cut underwriting review time by 60% with a targeted internal agent',
    outcome:
      'A 2-week pilot turned into a standing tool used by the whole underwriting team.',
    href: '/insights/financial-services-underwriting',
  },
  {
    industry: 'Allied health',
    title: 'Clinical note summarisation that practitioners actually trust',
    outcome:
      'Built with the clinicians, not for them — the key to the adoption curve going vertical.',
    href: '/insights/clinical-notes',
  },
  {
    industry: 'Manufacturing',
    title: 'From Excel chaos to a single source of operational truth',
    outcome:
      'Six months of work, most of it process design. The AI part was the last 10%.',
    href: '/insights/manufacturing-ops',
  },
];

// TODO: validate numbers with founder — these are placeholder and still
// training/workshop flavoured. Swap for SaaS-flavoured metrics (ARR, seats,
// verticals served) before launch.
const STATS = [
  { value: '50+', label: 'Workshops delivered' },
  { value: '12', label: 'Industries served' },
  { value: '4.9/5', label: 'Participant satisfaction' },
  { value: '8hrs', label: 'Avg. time saved weekly' },
];

// TODO: replace with real testimonials — placeholder drafts carried over
// from the legacy Home.
const TESTIMONIALS = [
  {
    quote:
      "They didn't sell us a platform. They sold us two weeks of their attention, and we came out with something our team actually uses every day.",
    name: 'Sarah M.',
    role: 'COO',
    company: 'Mid-market logistics firm',
  },
  {
    quote:
      "The workshop didn't feel like a workshop. It felt like we hired a senior engineer for two days and came out with a working tool.",
    name: 'James K.',
    role: 'Head of operations',
    company: 'Healthcare services provider',
  },
  {
    quote:
      'Boutique in the best sense — small enough that we got the partner, not a junior. We asked for a strategy and got both strategy and code.',
    name: 'Priya R.',
    role: 'Founder',
    company: 'B2B SaaS startup',
  },
];

export default function Home() {
  return (
    <Layout>
      <SEO
        title="OmniscientAI — Australia's sovereign applied AI company"
        description="We build the products, platforms, and agents that modernise our most consequential industries — and operate them as managed services so our customers don't have to."
      />

      <HeroSplit
        eyebrow="INTELLIGENCE // CONNECTIVITY // INNOVATION"
        title="Australia's sovereign applied AI company."
        lede="We build the products, platforms, and agents that modernise our most consequential industries — and operate them as managed services so our customers don't have to."
        primaryCta={{ label: 'See what we build', href: '/services' }}
        secondaryCta={{ label: 'Book a call', href: '/book' }}
        graphic="circles"
      />

      <TaglineBar align="center" className="mt-4 mb-4" />

      {/* Pillar 1 — Vertical SaaS. Uses the existing PillarGrid primitive
          with only three entries; the grid happily collapses 4-up to 3-up
          when the pillars array is shorter. */}
      <PillarGrid
        eyebrow="PILLAR 1"
        sectionTitle="Vertical SaaS for industries we understand."
        lede="We pick verticals where we have unfair advantage and build the software, data, and workflow tools they actually need. Product lines with their own roadmaps, P&Ls, and brands."
        pillars={VERTICAL_SAAS_PILLARS}
      />

      {/* Pillar 2 — The Omniscient Workforce. Custom 3-col grid so each card
          can carry an icon + title + subtitle + description. PillarGrid is
          tight on that shape. */}
      <Section
        eyebrow="PILLAR 2"
        title="The Omniscient Workforce."
        lede="A managed workforce of AI agents, each specialised to a real role. Not a chatbot. Not a prompt template. A specialist you hire per month."
        tone="paper-2"
      >
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {WORKFORCE_PERSONAS.map((persona) => {
            const Icon = persona.icon;
            return (
              <Card key={persona.title} className="flex flex-col">
                <Icon className="h-6 w-6 text-ink mb-4" aria-hidden />
                <h3 className="font-semibold text-[22px] leading-tight text-ink mb-1">
                  {persona.title}
                </h3>
                <div className="text-[14px] text-ink-3 mb-3">
                  {persona.subtitle}
                </div>
                <p className="text-ink-2">{persona.description}</p>
              </Card>
            );
          })}
        </div>
      </Section>

      {/* Pillar 3 — The Companion. Rendered in an InkSection for visual
          weight — it's the most distinctive / newest pillar. Per the
          design system rule, at most one InkSection per page — we spend
          our one on Omni. */}
      <InkSection
        eyebrow="PILLAR 3"
        title="The Companion. An AI that lives in your pocket, not in a chat window."
      >
        <div className="grid md:grid-cols-2 gap-12 items-center max-w-4xl mx-auto">
          <div>
            <p className="text-paper/80 text-[18px] leading-relaxed mb-4">
              Every major AI lives in a chat window on a desktop. Omni is
              different. It&apos;s phone-native. Voice-first. It remembers
              your life. It makes your calls, books your days, runs your
              errands.
            </p>
            <p className="text-paper/80 text-[18px] leading-relaxed mb-6">
              Integrates with your OS: calls, SMS, calendar, contacts,
              accessibility services. Yours alone — not Sam Altman&apos;s,
              not Sundar&apos;s. For defence and government users, it
              doesn&apos;t phone home to California.
            </p>
            <Link
              href="/services/companion"
              className="inline-flex items-center gap-2 text-paper border-b border-paper/40 hover:border-paper pb-1 transition-colors"
            >
              Learn more about Omni <span aria-hidden>→</span>
            </Link>
          </div>
          <div className="flex justify-center">
            {/* TODO: swap for a phone mockup image when design delivers one.
                BrainGraphic holds the space and stays on-brand. */}
            <BrainGraphic variant="circles" size="section" />
          </div>
        </div>
      </InkSection>

      {/* "Also" — consulting & workshops, de-emphasised. Kept so the option
          still exists for folks who need it, without owning the headline. */}
      <Section tone="paper-2">
        <div className="max-w-3xl mx-auto text-center">
          <Eyebrow className="mb-3 block">ALSO</Eyebrow>
          <h2 className="font-semibold text-[32px] leading-tight text-ink mb-4">
            Consulting + workshops, when you need them.
          </h2>
          <Lede className="mb-6">
            Sometimes the right answer isn&apos;t a product — it&apos;s a
            strategic engagement. We still do that. Vendor-neutral. Named
            practitioners. An artefact at the end.
          </Lede>
          <Link
            href="/workshops"
            className="inline-flex items-center gap-2 text-ink font-medium border-b border-ink/20 hover:border-ink pb-1 transition-colors"
          >
            See the workshops <span aria-hidden>→</span>
          </Link>
        </div>
      </Section>

      <CaseGrid
        eyebrow="Case studies"
        sectionTitle="What it looks like in practice."
        cases={CASES}
      />

      <StatsRow
        eyebrow="By the numbers"
        sectionTitle="Real outcomes, not slide deck numbers."
        stats={STATS}
        tone="paper-2"
      />

      <TestimonialStrip
        eyebrow="What people say"
        sectionTitle="The reviews we actually care about."
        testimonials={TESTIMONIALS}
      />

      <CTAStrip
        tone="paper"
        title="Ready to operate an AI workforce?"
        lede="A 20-minute call. We'll tell you exactly what we could build for you, and what it costs."
        primaryCta={{ label: 'Book a call', href: '/book' }}
      />
    </Layout>
  );
}
