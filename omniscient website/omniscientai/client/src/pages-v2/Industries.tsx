/**
 * Industries.tsx — v2 Industries overview page.
 *
 * Catalog page listing the industries we work in. Each card drives to the
 * industry detail page (Phase 7+). Composed from existing section primitives
 * and data from `lib/data.ts`:
 *
 *   HeroCentric → Industries card grid (derived from INDUSTRIES) →
 *   CaseGrid (tagged-industry featured cases) → CTAStrip (ink tone)
 *
 * `INDUSTRIES` in `lib/data.ts` does not carry Lucide icon names, so we map
 * each slug to an icon inline (adapter pattern — don't modify lib/data.ts).
 * The mapping mirrors the legacy Industries page's icon order.
 *
 * TODO: industry copy drafted 2026-04-22 — founder to validate
 */

import SEO from '@/components/SEO';
import { Layout } from '@/components-v2/layout';
import { HeroCentric, CaseGrid, CTAStrip } from '@/components-v2/sections';
import { Card, CTALink } from '@/components-v2/ui';
import {
  Briefcase,
  HeartPulse,
  Factory,
  ShoppingBag,
  Building2,
  type LucideIcon,
} from 'lucide-react';
import { INDUSTRIES } from '@/lib/data';

// Adapter: map industry slug → Lucide icon. INDUSTRIES entries in lib/data.ts
// don't carry an icon field. Fallback is a generic Building2.
const INDUSTRY_ICONS: Record<string, LucideIcon> = {
  'professional-services': Briefcase,
  healthcare: HeartPulse,
  manufacturing: Factory,
  retail: ShoppingBag,
};

// TODO: replace with real industry-tagged case studies before launch.
// Same placeholder pattern as Home — tagged to industries present on the
// page so the signal reads as "here's what we've done in these sectors".
const CASES = [
  {
    industry: 'Healthcare',
    title: 'Clinical note summarisation that practitioners actually trust',
    outcome:
      'Built with the clinicians, not for them — the key to the adoption curve going vertical.',
    href: '/insights/clinical-notes',
  },
  {
    industry: 'Professional services',
    title: 'Cut underwriting review time by 60% with a targeted internal agent',
    outcome:
      'A 2-week pilot turned into a standing tool used by the whole underwriting team.',
    href: '/insights/financial-services-underwriting',
  },
  {
    industry: 'Manufacturing',
    title: 'From Excel chaos to a single source of operational truth',
    outcome:
      'Six months of work, most of it process design. The AI part was the last 10%.',
    href: '/insights/manufacturing-ops',
  },
];

export default function Industries() {
  return (
    <Layout>
      <SEO
        title="Industries"
        description="AI training and consulting tuned to the realities of your sector. Healthcare, professional services, manufacturing, retail — we tailor workshops and engagements to the regulation and workflow you actually work under."
      />

      <HeroCentric
        eyebrow="Industries"
        title="AI that knows the floor it's walking on."
        lede="Every industry has its own data, its own regulation, and its own ways of working. We tailor workshops and engagements to the reality you're already operating in — no generic case studies, no trying to make your business fit a template."
      />

      {/* Industries card grid — 4-up on lg, 2-up on md. Derived from
          INDUSTRIES in lib/data.ts. Icon comes from the local adapter. */}
      <section className="py-12 lg:py-24">
        <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {INDUSTRIES.map((industry) => {
              const Icon = INDUSTRY_ICONS[industry.slug] ?? Building2;
              return (
                <Card key={industry.slug} className="flex flex-col">
                  <Icon className="h-8 w-8 text-ink" aria-hidden />
                  <h3 className="mt-5 font-semibold text-[22px] leading-tight text-ink">
                    {industry.title}
                  </h3>
                  <p className="mt-3 text-ink-2">{industry.subtitle}</p>
                  <CTALink
                    href={`/industries/${industry.slug}`}
                    className="mt-5 text-blue"
                  >
                    See how we work here
                  </CTALink>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      <CaseGrid
        eyebrow="In practice"
        sectionTitle="What it looks like on the ground."
        cases={CASES}
      />

      <CTAStrip
        tone="ink"
        title="Does your industry fit?"
        lede="If you're not sure, ask. A 20-minute call is free and we'll tell you honestly whether the work is a fit — and who else to talk to if it isn't."
        primaryCta={{ label: 'Talk to us', href: '/contact' }}
      />
    </Layout>
  );
}
