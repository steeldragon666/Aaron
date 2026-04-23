import { HTMLAttributes, ReactNode, forwardRef } from 'react';
import { cn } from '@/lib/utils';
import { Container } from './Container';
import { Eyebrow, Lede } from '@/components-v2/ui';

/**
 * Flip-to-ink section for page pacing rhythm. Applies `.ink-section`
 * from `omniscient.css`, which inverts surface/foreground tokens
 * (paper text on ink ground, muted paragraph via color-mix) and keeps
 * the shared 48px / 96px vertical rhythm from `Section`.
 *
 * Design system rule: use at most ONE `InkSection` per long page —
 * it's a pacing device, not a generic ink surface. If you need an
 * ink-backed card or hero, use the relevant primitive instead.
 */

// `title` on HTMLAttributes is `string` (the tooltip attribute).
// We intentionally repurpose the prop name for the header block, so
// omit the native one from the base type.
interface InkSectionProps extends Omit<HTMLAttributes<HTMLElement>, 'title'> {
  eyebrow?: string;
  title?: ReactNode;
  lede?: ReactNode;
  fluid?: boolean;
}

export const InkSection = forwardRef<HTMLElement, InkSectionProps>(
  ({ eyebrow, title, lede, fluid, className, children, ...rest }, ref) => {
    const hasHeader = Boolean(eyebrow || title || lede);
    const header = hasHeader && (
      <div className="mb-10 lg:mb-12 max-w-3xl">
        {eyebrow && <Eyebrow className="mb-3">{eyebrow}</Eyebrow>}
        {title && <h2>{title}</h2>}
        {lede && <Lede className="mt-4">{lede}</Lede>}
      </div>
    );

    const inner = (
      <>
        {header}
        {children}
      </>
    );

    return (
      <section
        ref={ref}
        className={cn('ink-section py-12 lg:py-24', className)}
        {...rest}
      >
        {fluid ? inner : <Container>{inner}</Container>}
      </section>
    );
  },
);
InkSection.displayName = 'InkSection';
