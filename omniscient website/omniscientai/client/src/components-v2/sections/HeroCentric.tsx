import { ReactNode } from 'react';
import { Link } from 'wouter';
import { cn } from '@/lib/utils';
import { Display, Eyebrow, Lede } from '@/components-v2/ui';
import { BrainGraphic } from '@/components-v2/brand';
import { Container } from '@/components-v2/layout';

/**
 * HeroCentric — centered single-column hero.
 *
 * Used on pages that don't need the asymmetric split (About, Approach,
 * Contact, Insights). Stacked vertically and text-centered, with the
 * title and lede constrained for readability. Optionally renders a
 * narrow BrainGraphic below the CTAs via `showGraphic`.
 */

interface CtaProps {
  label: string;
  href: string;
}

interface HeroCentricProps {
  eyebrow?: string;
  title: ReactNode;
  lede?: ReactNode;
  primaryCta?: CtaProps;
  secondaryCta?: CtaProps;
  showGraphic?: boolean;
  graphicVariant?: 'circles' | 'horizontal';
  className?: string;
}

// Matches Button primary+lg — keep aligned with
// client/src/components-v2/ui/Button.tsx if its primary styling changes.
const primaryCtaClass =
  'inline-flex items-center gap-2 rounded-md bg-blue text-paper ' +
  'px-[22px] py-[14px] text-[15px] font-semibold ' +
  'transition-[transform,background-color,filter] duration-[180ms] ' +
  'ease-[cubic-bezier(0.2,0.9,0.2,1)] ' +
  'hover:-translate-y-px hover:bg-blue-deep active:translate-y-0 active:brightness-[.96] ' +
  'focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2';

// Matches Button secondary+lg.
const secondaryCtaClass =
  'inline-flex items-center gap-2 rounded-md bg-paper text-ink ' +
  'border-[1.5px] border-ink px-[21px] py-[13px] text-[15px] font-semibold ' +
  'transition-[transform,background-color] duration-[180ms] ' +
  'ease-[cubic-bezier(0.2,0.9,0.2,1)] ' +
  'hover:-translate-y-px hover:bg-paper-2 active:translate-y-0 ' +
  'focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2';

export function HeroCentric({
  eyebrow,
  title,
  lede,
  primaryCta,
  secondaryCta,
  showGraphic = false,
  graphicVariant = 'circles',
  className,
}: HeroCentricProps) {
  return (
    <section className={cn('py-16 lg:py-24 text-center', className)}>
      <Container>
        <div className="flex flex-col items-center">
          {eyebrow && <Eyebrow className="mb-5 block">{eyebrow}</Eyebrow>}
          <Display as="h1" className="max-w-4xl mx-auto">
            {title}
          </Display>
          {lede && <Lede className="mt-6 max-w-2xl mx-auto">{lede}</Lede>}
          {(primaryCta || secondaryCta) && (
            <div className="mt-8 flex flex-wrap justify-center gap-3">
              {primaryCta && (
                <Link href={primaryCta.href} className={primaryCtaClass}>
                  {primaryCta.label} <span aria-hidden>→</span>
                </Link>
              )}
              {secondaryCta && (
                <Link href={secondaryCta.href} className={secondaryCtaClass}>
                  {secondaryCta.label}
                </Link>
              )}
            </div>
          )}
          {showGraphic && (
            <div className="mt-12 flex justify-center">
              <BrainGraphic variant={graphicVariant} size="section" />
            </div>
          )}
        </div>
      </Container>
    </section>
  );
}
