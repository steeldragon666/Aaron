import { ReactNode } from 'react';
import { cn } from '@/lib/utils';
import { Display, Eyebrow, Lede } from '@/components-v2/ui';
import { BrainGraphic } from '@/components-v2/brand';
import { Container } from '@/components-v2/layout';

/**
 * HeroSplit — 55/45 asymmetric hero.
 *
 * Copy occupies the left 1.3fr column, the decorative BrainGraphic
 * fills the 1fr column on the right. On mobile the grid collapses to
 * a single column and the graphic stacks below the copy.
 *
 * CTAs: primary (filled blue, with → arrow) + optional secondary
 * (ink-outline, no arrow). Both render as plain `<a>` elements because
 * Button is button-only — the primary styling mirrors Button's primary+lg
 * variant and the same pattern used in Nav.tsx.
 */

interface CtaProps {
  label: string;
  href: string;
}

interface HeroSplitProps {
  eyebrow?: string;
  title: ReactNode;
  lede?: ReactNode;
  primaryCta?: CtaProps;
  secondaryCta?: CtaProps;
  graphic?: 'circles' | 'horizontal';
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

export function HeroSplit({
  eyebrow,
  title,
  lede,
  primaryCta,
  secondaryCta,
  graphic = 'circles',
  className,
}: HeroSplitProps) {
  return (
    <section className={cn('py-16 lg:py-24', className)}>
      <Container>
        <div className="grid lg:grid-cols-[1.3fr_1fr] gap-12 lg:gap-16 items-center">
          <div className="max-w-[640px]">
            {eyebrow && <Eyebrow className="mb-5 block">{eyebrow}</Eyebrow>}
            <Display as="h1">{title}</Display>
            {lede && <Lede className="mt-6">{lede}</Lede>}
            {(primaryCta || secondaryCta) && (
              <div className="mt-8 flex flex-wrap gap-3">
                {primaryCta && (
                  <a href={primaryCta.href} className={primaryCtaClass}>
                    {primaryCta.label} <span aria-hidden>→</span>
                  </a>
                )}
                {secondaryCta && (
                  <a href={secondaryCta.href} className={secondaryCtaClass}>
                    {secondaryCta.label}
                  </a>
                )}
              </div>
            )}
          </div>
          <div className="flex justify-center lg:justify-end">
            <BrainGraphic variant={graphic} size="hero" />
          </div>
        </div>
      </Container>
    </section>
  );
}
