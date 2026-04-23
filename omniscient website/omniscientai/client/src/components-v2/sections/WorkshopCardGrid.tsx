import { Link } from 'wouter';
import { cn } from '@/lib/utils';
import { Card, MonoBadge } from '@/components-v2/ui';
import { Section } from '@/components-v2/layout';

/**
 * WorkshopCardGrid — 3-up responsive grid of workshop catalog cards.
 *
 * Each card is a Card containing an optional 16:9 image, a meta-badge row
 * (duration · format · price), a title, a short description, and a
 * full-width primary-button anchor ("Book this workshop →") that links to
 * `/workshops/{slug}`.
 *
 * Layout: single column on mobile, 2-up at md, 3-up at lg.
 */

interface Workshop {
  slug: string;
  title: string;
  description: string;
  /** e.g. "2 days" */
  duration: string;
  /** e.g. "In-person, Melbourne" or "Hybrid" */
  format: string;
  /** e.g. "$4,995 AUD" or "From $4,995" */
  price: string;
  /** Optional workshop hero image (16:9). */
  imageUrl?: string;
}

interface WorkshopCardGridProps {
  eyebrow?: string;
  sectionTitle?: string;
  workshops: Workshop[];
  className?: string;
}

// Matches Button primary+md — full-width on card so the CTA spans the
// entire card footer for a strong "Book now" rail. Kept in sync with
// Button.tsx's primary+md variant.
const primaryCtaClass =
  'inline-flex items-center justify-center gap-2 w-full rounded-md bg-blue text-paper ' +
  'px-[18px] py-[12px] text-[14px] font-semibold ' +
  'transition-[transform,background-color,filter] duration-[180ms] ' +
  'ease-[cubic-bezier(0.2,0.9,0.2,1)] ' +
  'hover:-translate-y-px hover:bg-blue-deep active:translate-y-0 active:brightness-[.96] ' +
  'focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2';

export function WorkshopCardGrid({
  eyebrow,
  sectionTitle,
  workshops,
  className,
}: WorkshopCardGridProps) {
  return (
    <Section eyebrow={eyebrow} title={sectionTitle} className={cn(className)}>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {workshops.map((workshop) => (
          <Card key={workshop.slug} className="flex flex-col !p-0 overflow-hidden">
            {workshop.imageUrl && (
              <div className="aspect-[16/9] w-full overflow-hidden bg-paper-2">
                <img
                  src={workshop.imageUrl}
                  alt=""
                  className="h-full w-full object-cover"
                />
              </div>
            )}
            <div className="flex flex-col flex-1 p-6">
              <div className="flex flex-wrap items-center gap-x-2 gap-y-1 text-ink-3">
                <MonoBadge>{workshop.duration}</MonoBadge>
                <span aria-hidden>·</span>
                <MonoBadge>{workshop.format}</MonoBadge>
                <span aria-hidden>·</span>
                <MonoBadge>{workshop.price}</MonoBadge>
              </div>
              <h3 className="mt-4 font-semibold text-[22px] leading-tight text-ink">
                {workshop.title}
              </h3>
              <p className="mt-3 text-ink-2">{workshop.description}</p>
              <div className="mt-auto pt-6">
                <Link href={`/workshops/${workshop.slug}`} className={primaryCtaClass}>
                  Book this workshop <span aria-hidden>→</span>
                </Link>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </Section>
  );
}
