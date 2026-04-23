import { AnchorHTMLAttributes, HTMLAttributes, forwardRef, Ref } from 'react';
import { cn } from '@/lib/utils';

type Tone = 'paper' | 'paper-2';

type CardAsDiv = {
  as?: 'div';
} & HTMLAttributes<HTMLDivElement>;

type CardAsAnchor = {
  as: 'a';
} & AnchorHTMLAttributes<HTMLAnchorElement>;

type CardProps = (CardAsDiv | CardAsAnchor) & {
  tone?: Tone;
};

// 2026-04-23 style pass: on hover, cards now shift their border from
// --line to --blue alongside the existing shadow bump, so the hover gives
// a subtle colour signal in addition to elevation. Transition targets both
// box-shadow and border-color so the fade stays smooth.
const base =
  'block border border-line rounded-lg p-6 ' +
  'transition-[box-shadow,border-color] duration-[180ms] ease-[cubic-bezier(0.2,0.9,0.2,1)] ' +
  'hover:border-blue ' +
  'hover:shadow-[0_1px_2px_rgb(15_17_21_/_0.06),_0_1px_1px_rgb(15_17_21_/_0.04)]';

const tones: Record<Tone, string> = {
  paper: 'bg-paper',
  'paper-2': 'bg-paper-2',
};

export const Card = forwardRef<HTMLElement, CardProps>((props, ref) => {
  const { tone = 'paper', className, children, ...rest } = props;
  const as = 'as' in props && props.as === 'a' ? 'a' : 'div';
  const isAnchor = as === 'a';

  const classes = cn(
    base,
    tones[tone],
    isAnchor &&
      'cursor-pointer focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2',
    className,
  );

  if (isAnchor) {
    const anchorProps = rest as AnchorHTMLAttributes<HTMLAnchorElement> & { as?: unknown };
    const { as: _discard, ...anchorRest } = anchorProps;
    void _discard;
    return (
      <a ref={ref as Ref<HTMLAnchorElement>} className={classes} {...anchorRest}>
        {children}
      </a>
    );
  }

  const divProps = rest as HTMLAttributes<HTMLDivElement> & { as?: unknown };
  const { as: _discard, ...divRest } = divProps;
  void _discard;
  return (
    <div ref={ref as Ref<HTMLDivElement>} className={classes} {...divRest}>
      {children}
    </div>
  );
});
Card.displayName = 'Card';

// FeaturedCard — ink background variant. Same polymorphic `as` support.
// Stronger shadow-2 on hover for extra emphasis on the featured card in a grid.
const featuredBase =
  'block bg-ink text-paper border-0 rounded-lg p-6 ' +
  'transition-shadow duration-[180ms] ease-[cubic-bezier(0.2,0.9,0.2,1)] ' +
  'hover:shadow-[0_10px_24px_rgb(15_17_21_/_0.08),_0_2px_6px_rgb(15_17_21_/_0.06)]';

type FeaturedAsDiv = { as?: 'div' } & HTMLAttributes<HTMLDivElement>;
type FeaturedAsAnchor = { as: 'a' } & AnchorHTMLAttributes<HTMLAnchorElement>;
type FeaturedCardProps = FeaturedAsDiv | FeaturedAsAnchor;

export const FeaturedCard = forwardRef<HTMLElement, FeaturedCardProps>((props, ref) => {
  const { className, children, ...rest } = props;
  const as = 'as' in props && props.as === 'a' ? 'a' : 'div';
  const isAnchor = as === 'a';

  const classes = cn(
    featuredBase,
    isAnchor &&
      'cursor-pointer focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2',
    className,
  );

  if (isAnchor) {
    const anchorProps = rest as AnchorHTMLAttributes<HTMLAnchorElement> & { as?: unknown };
    const { as: _discard, ...anchorRest } = anchorProps;
    void _discard;
    return (
      <a ref={ref as Ref<HTMLAnchorElement>} className={classes} {...anchorRest}>
        {children}
      </a>
    );
  }

  const divProps = rest as HTMLAttributes<HTMLDivElement> & { as?: unknown };
  const { as: _discard, ...divRest } = divProps;
  void _discard;
  return (
    <div ref={ref as Ref<HTMLDivElement>} className={classes} {...divRest}>
      {children}
    </div>
  );
});
FeaturedCard.displayName = 'FeaturedCard';
