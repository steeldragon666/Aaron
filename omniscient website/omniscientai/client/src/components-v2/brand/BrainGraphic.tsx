import { ImgHTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

/**
 * Decorative connectome illustration placer. Renders one of two brand
 * graphics in one of three size presets (viewport-width with a max cap),
 * as a purely decorative image.
 *
 * Variants:
 * - `circles` (default) — square lockup, for square-ish contexts
 * - `horizontal` — wide horizontal band, for full-width accents
 *
 * Sizes (applied via Tailwind arbitrary-value classes):
 * - `hero` (default) — `w-[40vw] max-w-[540px]`
 * - `section` — `w-[25vw] max-w-[320px]`
 * - `corner` — `w-[15vw] max-w-[200px]`
 *
 * Always rendered as `aria-hidden` with `alt=""` — the surrounding copy
 * carries the semantic meaning. This follows the WAI-ARIA decorative
 * image pattern.
 *
 * No animation. Pulsing-nodes variants are reserved for Phase 7 hero.
 *
 * No forwardRef — this is a terminal brand element, not a compositional
 * primitive.
 */

type Variant = 'circles' | 'horizontal';
type Size = 'hero' | 'section' | 'corner';

interface BrainGraphicProps extends Omit<ImgHTMLAttributes<HTMLImageElement>, 'src' | 'alt'> {
  variant?: Variant;
  size?: Size;
}

const sources: Record<Variant, string> = {
  circles: '/brand/brand-graphic-circles.png',
  horizontal: '/brand/brand-graphic-horizontal.png',
};

const sizes: Record<Size, string> = {
  hero: 'w-[40vw] max-w-[540px]',
  section: 'w-[25vw] max-w-[320px]',
  corner: 'w-[15vw] max-w-[200px]',
};

export function BrainGraphic({
  variant = 'circles',
  size = 'hero',
  className,
  ...rest
}: BrainGraphicProps) {
  return (
    <img
      src={sources[variant]}
      alt=""
      aria-hidden="true"
      className={cn(sizes[size], className)}
      {...rest}
    />
  );
}
