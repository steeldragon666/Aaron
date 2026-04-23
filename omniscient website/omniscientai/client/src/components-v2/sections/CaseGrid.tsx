import { Link } from 'wouter';
import { cn } from '@/lib/utils';
import { Card, FeaturedCard, Eyebrow, CTALink } from '@/components-v2/ui';
import { Section } from '@/components-v2/layout';

/**
 * CaseGrid — 3-up grid of case studies.
 *
 * First card is a FeaturedCard (ink background) used as the hero of the grid,
 * the remaining two are standard paper Cards. Each card contains industry
 * eyebrow, title, 1-sentence outcome, and a "Read the case study" CTA.
 *
 * Layout: single column on mobile, 2-up at md, 3-up at lg.
 * Works gracefully with 1-3 cases.
 */

interface CaseStudy {
  /** Industry tag shown as eyebrow above title. */
  industry: string;
  title: string;
  /** 1-sentence result statement. */
  outcome: string;
  href: string;
}

interface CaseGridProps {
  eyebrow?: string;
  sectionTitle?: string;
  /** Up to 3 cases; the first is rendered as a FeaturedCard. */
  cases: CaseStudy[];
  className?: string;
}

// Matches the design system a:hover border-current underline pattern so the
// link reads well on the ink-background FeaturedCard (CTALink's default
// inherits `currentColor` which becomes text-paper there — but we keep the
// styling explicit here for the "on ink" context).
const inkCtaClass =
  'inline-flex items-center gap-1 font-medium text-paper ' +
  'border-b border-transparent hover:border-current ' +
  'transition-colors duration-[180ms] ease-[cubic-bezier(0.2,0.9,0.2,1)] ' +
  'focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2';

export function CaseGrid({ eyebrow, sectionTitle, cases, className }: CaseGridProps) {
  return (
    <Section eyebrow={eyebrow} title={sectionTitle} className={cn(className)}>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {cases.map((study, idx) => {
          const isFeatured = idx === 0;
          // Multiple cases may share the same href (e.g. the CaseStudies
          // overview points three workforce stories at /services/workforce),
          // so we key off (title + href) rather than href alone to avoid
          // React's "same key" warning when a pillar grid duplicates.
          const key = `${study.title}|${study.href}`;
          const titleHeading = (
            <h3 className="mt-3 font-semibold text-[22px] leading-tight">
              {study.title}
            </h3>
          );

          if (isFeatured) {
            return (
              <FeaturedCard key={key} className="flex flex-col">
                <Eyebrow className="text-paper/70">{study.industry}</Eyebrow>
                {titleHeading}
                <p className="mt-3 text-paper/80">{study.outcome}</p>
                <Link href={study.href} className={cn('mt-5', inkCtaClass)}>
                  Read the case study <span aria-hidden>→</span>
                </Link>
              </FeaturedCard>
            );
          }

          return (
            <Card key={key} className="flex flex-col">
              <Eyebrow>{study.industry}</Eyebrow>
              {titleHeading}
              <p className="mt-3 text-ink-2">{study.outcome}</p>
              <CTALink href={study.href} className="mt-5 text-blue">
                Read the case study
              </CTALink>
            </Card>
          );
        })}
      </div>
    </Section>
  );
}
