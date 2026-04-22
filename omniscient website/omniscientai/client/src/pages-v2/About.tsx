/**
 * About.tsx — v2 About page.
 *
 * Tells the "why we exist" story. Composed from existing section primitives:
 *
 *   HeroCentric → Story block (narrow Section) → Values grid (4-up, mix of
 *   Card + FeaturedCard for emphasis) → Practitioners grid (3-up, placeholder
 *   bios) → InkSection "How we work" → CTAStrip
 *
 * Flags two major blocks of content as TODO for founder input:
 *   1. The "why we exist" story paragraphs (drafted placeholder, needs the
 *      real founder narrative before launch).
 *   2. The practitioner bios — names, roles, photos. These are PLACEHOLDER
 *      and marked as a blocker in code comments; no fake names shipped.
 */

import SEO from '@/components/SEO';
import { Layout, InkSection, Section } from '@/components-v2/layout';
import { HeroCentric, CTAStrip } from '@/components-v2/sections';
import { Card, FeaturedCard } from '@/components-v2/ui';

// TODO: founder to validate/replace — drafted 2026-04-22.
// Three paragraphs of "why Omniscient exists" narrative. Placeholder voice
// follows the tone guide in docs/design-system/README.md.
const STORY_PARAGRAPHS = [
  "Omniscient started because the big consulting firms couldn't say no. Every answer was billable, every engagement was twelve months, and every recommendation pointed at whichever vendor was paying the highest kickback that quarter. Good people, trapped inside a business model that rewarded sprawl.",
  "We do the opposite. Short engagements. One artefact at the end. A named practitioner doing the work — not a partner pitching and a junior delivering. If the right answer is \"don't build this yet,\" we say so, because we're not paid to ship lines of code.",
  "We're vendor-neutral by design, not by slogan. No reseller agreements, no partner tiers, no rebate schemes. When we recommend a tool, it's because it fits your team and your data — full stop.",
];

// TODO: founder to validate values copy — drafted 2026-04-22.
// Four values, one marked for emphasis via FeaturedCard (ink tone) to break
// the visual rhythm of a plain 4-up grid.
const VALUES = [
  {
    title: 'Vendor-neutral',
    body: 'No kickbacks. No partner tiers. No lock-in. We recommend the tool that fits your team, even when that means recommending nothing at all.',
    emphasised: true,
  },
  {
    title: 'Named practitioners',
    body: 'You get the senior person who scoped the work. No partner-pitch-then-junior-delivery handoff. The person writing the code sat in the kickoff meeting.',
    emphasised: false,
  },
  {
    title: 'Ship artefacts',
    body: 'Every engagement produces something tangible — working code, a trained capability, a documented process. If you can\'t point at it, we haven\'t done our job.',
    emphasised: false,
  },
  {
    title: 'Short engagements',
    body: 'Boutique-scale. Roughly three weeks, not a six-month retainer. We scope tight, deliver, and get out of your way.',
    emphasised: false,
  },
];

// TODO: BLOCKER — founder to provide real practitioner names, roles, and
// photos before launch. The current bios are structural placeholders only.
// Do NOT ship this to production without real content — fake names on an
// About page destroy the vendor-neutrality pitch the page is selling.
const PRACTITIONERS = [
  {
    // TODO: founder input required
    name: 'Founder / Principal',
    role: 'TBD',
    bio: 'Placeholder bio — the founder\'s background, what they\'ve shipped, why they started Omniscient. Needs real copy from the founder before launch.',
  },
  {
    // TODO: founder input required
    name: 'Senior Practitioner',
    role: 'TBD',
    bio: 'Placeholder bio — a senior practitioner who works on engagements alongside the founder. Background, specialism, what they bring. Needs real copy.',
  },
  {
    // TODO: founder input required
    name: 'Senior Practitioner',
    role: 'TBD',
    bio: 'Placeholder bio — second senior practitioner. Same slot as above. Real name, role, photo, and bio required before launch.',
  },
];

export default function About() {
  return (
    <Layout>
      <SEO
        title="About"
        description="A boutique AI consultancy built around named practitioners, vendor-neutral advice, and short engagements that ship real artefacts. Learn why Omniscient exists and how we work."
      />

      <HeroCentric
        eyebrow="About us"
        title="A boutique, built for the real world."
        lede="We exist because the big firms couldn't say no. Short engagements, named practitioners, and advice that doesn't come with a vendor rebate attached."
      />

      {/* Story block — narrow max-w Section for long-form reading rhythm. */}
      <Section>
        <div className="max-w-2xl">
          <h2 className="font-semibold text-[32px] leading-tight text-ink">
            Why we exist
          </h2>
          <div className="mt-6 space-y-5 text-[18px] leading-[1.6] text-ink-2">
            {STORY_PARAGRAPHS.map((paragraph, idx) => (
              <p key={idx}>{paragraph}</p>
            ))}
          </div>
        </div>
      </Section>

      {/* Values grid — 4-up on lg, 2-up on md. One card is FeaturedCard (ink
          tone) for emphasis; the rest are standard paper Cards. */}
      <Section
        eyebrow="What we stand for"
        title="Four values. No exceptions."
        tone="paper-2"
      >
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {VALUES.map((value) =>
            value.emphasised ? (
              <FeaturedCard key={value.title} className="flex flex-col">
                <h3 className="font-semibold text-[22px] leading-tight text-paper">
                  {value.title}
                </h3>
                <p className="mt-3 text-paper/80">{value.body}</p>
              </FeaturedCard>
            ) : (
              <Card key={value.title} className="flex flex-col">
                <h3 className="font-semibold text-[22px] leading-tight text-ink">
                  {value.title}
                </h3>
                <p className="mt-3 text-ink-2">{value.body}</p>
              </Card>
            ),
          )}
        </div>
      </Section>

      {/* Practitioners grid — 3-up on lg, stacked on md. PLACEHOLDER BIOS:
          flagged in PRACTITIONERS consts above. Blocker for founder input
          before launch. */}
      <Section
        eyebrow="The team"
        title="Named practitioners, not a partner-pitch machine."
        lede="You work with the person who scoped the engagement. No handoffs, no juniors, no partner-sells-then-disappears."
      >
        <div className="grid md:grid-cols-3 gap-6">
          {PRACTITIONERS.map((person, idx) => (
            <Card key={idx} className="flex flex-col">
              {/* TODO: add photo when founder provides headshot */}
              <div
                className="h-32 w-32 rounded-full bg-paper-2 border border-line"
                aria-hidden
              />
              <h3 className="mt-5 font-semibold text-[22px] leading-tight text-ink">
                {person.name}
              </h3>
              <p className="mt-1 text-[14px] uppercase tracking-wide text-ink-2">
                {person.role}
              </p>
              <p className="mt-3 text-ink-2">{person.bio}</p>
            </Card>
          ))}
        </div>
      </Section>

      <InkSection
        eyebrow="How we work"
        title="Small team. Big shoulders."
      >
        <div className="max-w-3xl space-y-5 text-[18px] leading-[1.6] text-paper/80">
          <p>
            We're deliberately small. Every engagement gets a named
            practitioner who owns the work end-to-end — and who's accountable
            when it ships. That's how we keep the quality bar high and the
            feedback loop tight.
          </p>
          <p>
            Small doesn't mean limited. We pull in specialist collaborators
            when the work needs it, and our boutique scale means we can move
            faster than a firm with fifty layers of review.
          </p>
        </div>
      </InkSection>

      <CTAStrip
        tone="paper"
        title="Want to meet us?"
        lede="A 20-minute call, free, no pitch deck. We'll tell you honestly whether the work is a fit — and who else to talk to if it isn't."
        primaryCta={{ label: 'Get in touch', href: '/contact' }}
      />
    </Layout>
  );
}
