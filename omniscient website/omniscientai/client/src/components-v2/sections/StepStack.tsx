import { cn } from '@/lib/utils';
import { MonoBadge } from '@/components-v2/ui';
import { Section } from '@/components-v2/layout';

/**
 * StepStack — numbered vertical list of steps.
 *
 * Used on Approach page (4-phase methodology) and Workshop Detail (module
 * agenda). Each step has a large mono numeral (01, 02, ...), an h3 title,
 * a body paragraph, and an optional duration MonoBadge.
 *
 * Layout: numeral inline with title row on desktop (two-column grid with a
 * fixed ~80px numeral column), numeral stacked above content on mobile.
 * Top-hairline dividers between steps (except the first).
 */

interface Step {
  title: string;
  body: string;
  /** e.g. "45 min" — rendered as a MonoBadge next to the title. */
  duration?: string;
}

interface StepStackProps {
  eyebrow?: string;
  sectionTitle?: string;
  lede?: string;
  steps: Step[];
  className?: string;
}

export function StepStack({
  eyebrow,
  sectionTitle,
  lede,
  steps,
  className,
}: StepStackProps) {
  return (
    <Section
      eyebrow={eyebrow}
      title={sectionTitle}
      lede={lede}
      className={cn(className)}
    >
      <ol className="list-none p-0 m-0">
        {steps.map((step, idx) => {
          const numeral = String(idx + 1).padStart(2, '0');
          return (
            <li
              key={step.title}
              className={cn(
                'grid grid-cols-1 md:grid-cols-[80px_1fr] gap-y-4 md:gap-x-8 py-8',
                idx !== 0 && 'border-t border-line',
              )}
            >
              <div
                aria-hidden
                className="font-mono text-[48px] font-medium leading-none text-ink"
              >
                {numeral}
              </div>
              <div>
                <div className="flex flex-wrap items-center gap-3">
                  <h3 className="font-semibold text-[22px] leading-tight text-ink">
                    {step.title}
                  </h3>
                  {step.duration && <MonoBadge>{step.duration}</MonoBadge>}
                </div>
                <p className="mt-3 text-ink-2">{step.body}</p>
              </div>
            </li>
          );
        })}
      </ol>
    </Section>
  );
}
