import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';
import { Section, InkSection } from '@/components-v2/layout';
import { Lede } from '@/components-v2/ui';

/**
 * CTAStrip — centered book-a-call prompt.
 *
 * Renders at the bottom of most marketing pages. Two tones:
 *   - paper (default) — wraps in <Section>
 *   - ink — wraps in <InkSection> for a dramatic closing pacing moment
 *
 * Primary CTA is a blue button (allowed on both paper and ink).
 * Secondary CTA is an outline link; on ink tone, the outline flips to
 * paper-bordered text-on-ink.
 *
 * Button is rendered as a plain <a> with button-matching styles since the
 * Button primitive is a <button>-only element.
 */

interface CTAStripProps {
  eyebrow?: string;
  title: ReactNode;
  lede?: ReactNode;
  primaryCta: { label: string; href: string };
  secondaryCta?: { label: string; href: string };
  /** Surface tone. Defaults to `paper`. */
  tone?: 'paper' | 'ink';
  className?: string;
}

// Base shared by both CTA anchors — mirrors Button primary+lg without the
// button-only `cursor: pointer` defaults (anchors already get it).
const ctaBase =
  'inline-flex items-center gap-2 rounded-md font-semibold ' +
  'px-[22px] py-[14px] text-[15px] ' +
  'transition-[transform,background-color,filter] duration-[180ms] ' +
  'ease-[cubic-bezier(0.2,0.9,0.2,1)] ' +
  'hover:-translate-y-px active:translate-y-0 active:brightness-[.96] ' +
  'focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2';

const primaryCtaClass = cn(ctaBase, 'bg-blue text-paper border-0 hover:bg-blue-deep');

const secondaryCtaPaperClass = cn(
  ctaBase,
  'bg-paper text-ink border-[1.5px] border-ink hover:bg-paper-2',
);

const secondaryCtaInkClass = cn(
  ctaBase,
  'bg-transparent text-paper border-[1.5px] border-paper hover:bg-white/10',
);

export function CTAStrip({
  eyebrow,
  title,
  lede,
  primaryCta,
  secondaryCta,
  tone = 'paper',
  className,
}: CTAStripProps) {
  const content = (
    <div className="text-center">
      {lede && (
        <Lede className="mt-4 mx-auto max-w-2xl">{lede}</Lede>
      )}
      <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
        <a href={primaryCta.href} className={primaryCtaClass}>
          {primaryCta.label}
          <span aria-hidden>→</span>
        </a>
        {secondaryCta && (
          <a
            href={secondaryCta.href}
            className={tone === 'ink' ? secondaryCtaInkClass : secondaryCtaPaperClass}
          >
            {secondaryCta.label}
          </a>
        )}
      </div>
    </div>
  );

  // Section/InkSection render eyebrow + title left-aligned by default; we want
  // them centered here, so we pass the title through and rely on a wrapper
  // style override via the header `max-w-3xl` + centering classes below.
  //
  // Simpler path: pass title+eyebrow directly to Section/InkSection but also
  // add a `text-center` override on the section className so the header block
  // inherits alignment, and recentre the `max-w-3xl` container.
  if (tone === 'ink') {
    return (
      <InkSection
        eyebrow={eyebrow}
        title={title}
        className={cn(
          '[&_>_div_>_div:first-child]:mx-auto [&_>_div_>_div:first-child]:text-center',
          className,
        )}
      >
        {content}
      </InkSection>
    );
  }

  return (
    <Section
      eyebrow={eyebrow}
      title={title}
      className={cn(
        '[&_>_div_>_div:first-child]:mx-auto [&_>_div_>_div:first-child]:text-center',
        className,
      )}
    >
      {content}
    </Section>
  );
}
