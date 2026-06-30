import { HTMLAttributes, ReactNode, forwardRef } from 'react';
import { cn } from '@/lib/utils';
import { Container } from './Container';
import { Eyebrow, Lede } from '@/components-v2/ui';

// Canonical paper section with the standard v2 vertical rhythm
// (48px / 96px top+bottom) and an optional header block (eyebrow + title + lede)
// rendered inside the shared Container. Pass `fluid` for full-bleed children
// (e.g. hero canvases that want to own the gutters themselves).

type Tone = 'paper' | 'paper-2';

// `title` on HTMLAttributes is `string` (the tooltip attribute).
// We intentionally repurpose the prop name for the header block, so
// omit the native one from the base type.
interface SectionProps extends Omit<HTMLAttributes<HTMLElement>, 'title'> {
  tone?: Tone;
  eyebrow?: string;
  title?: ReactNode;
  lede?: ReactNode;
  fluid?: boolean;
}

const tones: Record<Tone, string> = {
  paper: 'bg-paper',
  'paper-2': 'bg-paper-2',
};

export const Section = forwardRef<HTMLElement, SectionProps>(
  (
    { tone = 'paper', eyebrow, title, lede, fluid, className, children, ...rest },
    ref,
  ) => {
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
        className={cn('py-12 lg:py-24', tones[tone], className)}
        {...rest}
      >
        {fluid ? inner : <Container>{inner}</Container>}
      </section>
    );
  },
);
Section.displayName = 'Section';
