/**
 * Home.tsx — v2 marketing home page.
 *
 * First real v2 page. Composed from existing section primitives:
 *   HeroSplit → TaglineBar → PillarGrid → InkSection manifesto →
 *   WorkshopCardGrid → CaseGrid → StatsRow → TestimonialStrip → CTAStrip
 *
 * All copy is placeholder-but-shippable (drafted 2026-04-22 following the
 * voice guide in docs/design-system/README.md). TODO comments flag the
 * specific items that need founder validation before Phase 12 production
 * flip — pillar descriptions, manifesto, case studies, stats, testimonials.
 */

import SEO from '@/components/SEO';
import { Layout, InkSection } from '@/components-v2/layout';
import { TaglineBar } from '@/components-v2/brand';
import {
  HeroSplit,
  PillarGrid,
  WorkshopCardGrid,
  CaseGrid,
  StatsRow,
  TestimonialStrip,
  CTAStrip,
} from '@/components-v2/sections';
import { GraduationCap, Activity, Shield, Bot } from 'lucide-react';

// TODO: founder to review pillar copy — drafted 2026-04-22
const PILLARS = [
  {
    icon: GraduationCap,
    title: 'AI training',
    description:
      'Hands-on workshops that leave your team with a shippable artefact. Vendor-neutral — we have no kickbacks from Anthropic, OpenAI, or anyone else.',
    href: '/services/training',
  },
  {
    icon: Activity,
    title: 'Health technologies',
    description:
      'Clinical AI work with a serious respect for regulation, privacy, and the consequences of getting it wrong. Built alongside named medical practitioners.',
    href: '/industries/health',
  },
  {
    icon: Shield,
    title: 'Defense hardware & software',
    description:
      'Hardened systems and agentic tooling for defense contexts. Air-gapped when it needs to be. Integrity-first engineering.',
    href: '/industries/defense',
  },
  {
    icon: Bot,
    title: 'Agentic ops',
    description:
      'Marketing and ops agents that do one job well. Designed to be owned by the team that uses them, not locked into a vendor.',
    href: '/services/agentic-ops',
  },
];

// TODO: manifesto copy — drafted 2026-04-22, founder to validate tone
const MANIFESTO_PARAGRAPHS = [
  "Every major AI vendor has a commercial interest in making you use more of their product. Partners get kickbacks. Training is pitched around the SKU. That's fine — but it's not what you want when you're trying to figure out what's actually going to work for your team.",
  'We\'re not a reseller. We don\'t get paid when you adopt Claude instead of GPT, or Llama instead of Gemini. Our job is to put the right tool in the right hands — and sometimes the right answer is "not yet, and here\'s what to build in-house first."',
  "That's also why we insist on shipping an artefact at the end of every engagement. If you can't point at the thing that's different after we leave, we haven't done our job.",
];

const WORKSHOPS = [
  {
    slug: 'ai-readiness',
    title: 'AI Readiness Workshop',
    description:
      "A 2-day hands-on assessment of where AI can save your team real hours, and where it can't. Leaves you with a prioritised 90-day action plan.",
    duration: '2 days',
    format: 'In-person, Melbourne',
    price: 'From $4,995 AUD',
  },
  {
    slug: 'exec-briefing',
    title: 'Executive AI Briefing',
    description:
      'Half-day briefing for leadership teams. What the landscape actually looks like right now, where the money is, and what to stop wasting time on.',
    duration: '4 hours',
    format: 'In-person or remote',
    price: 'From $2,495 AUD',
  },
  {
    slug: 'custom-training',
    title: 'Custom team training',
    description:
      'Scoped to your workflow. We build the training from your actual tasks and tooling — not generic case studies.',
    duration: 'Bespoke',
    format: 'In-person, Melbourne',
    price: 'Quote on scope',
  },
];

// TODO: replace with real case studies before launch; currently anonymized drafts
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

// TODO: validate numbers with founder — these are placeholder
const STATS = [
  { value: '50+', label: 'Workshops delivered' },
  { value: '12', label: 'Industries served' },
  { value: '4.9/5', label: 'Participant satisfaction' },
  { value: '8hrs', label: 'Avg. time saved weekly' },
];

// TODO: replace with real testimonials — placeholder drafts
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
        title="Vendor-neutral AI training for Melbourne SMEs"
        description="Short engagements, named practitioners, and an artefact at the end of every workshop. Practical AI for real teams."
      />

      <HeroSplit
        eyebrow="INTELLIGENCE // CONNECTIVITY // INNOVATION"
        title="Unleashing the power of intelligent connections."
        lede="Vendor-neutral AI training and consulting for Melbourne SMEs. We work in short engagements with named practitioners — every workshop leaves your team with a shippable artefact."
        primaryCta={{ label: 'Book a 20-minute call', href: '/book' }}
        secondaryCta={{ label: 'See the workshops', href: '/workshops' }}
        graphic="circles"
      />

      <TaglineBar align="center" className="mt-4 mb-4" />

      <PillarGrid
        eyebrow="What we do"
        sectionTitle="Four practice areas. One standard."
        lede="Every engagement ends with an artefact your team owns — not a slide deck, not a dependency on us."
        pillars={PILLARS}
      />

      <InkSection
        eyebrow="Why vendor-neutral"
        title="We don't take kickbacks. That's the point."
      >
        <div className="max-w-3xl space-y-5 text-[18px] leading-[1.6] text-paper/80">
          {MANIFESTO_PARAGRAPHS.map((paragraph, idx) => (
            <p key={idx}>{paragraph}</p>
          ))}
        </div>
      </InkSection>

      <WorkshopCardGrid
        eyebrow="Workshops"
        sectionTitle="Three ways to start."
        workshops={WORKSHOPS}
      />

      <CaseGrid
        eyebrow="Case studies"
        sectionTitle="What it looks like in practice."
        cases={CASES}
      />

      <StatsRow
        eyebrow="By the numbers"
        sectionTitle="Six years. Real outcomes."
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
        title="Ready to put AI to work?"
        lede="A 20-minute call is free. No sales pitch — just a conversation about what might actually help."
        primaryCta={{ label: 'Book a call', href: '/book' }}
        secondaryCta={{ label: 'Download the AI readiness quiz', href: '/quiz' }}
      />
    </Layout>
  );
}
