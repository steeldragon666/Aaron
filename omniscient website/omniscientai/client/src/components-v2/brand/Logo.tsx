import { ImgHTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

/**
 * Brand logomark. Thin wrapper over the three PNG assets in
 * `client/public/brand/`, selected via the `variant` prop:
 *
 * - `stacked` (default) — square brain lockup, for avatars / deck covers
 * - `horizontal` — wide lockup for email sigs / deck headers
 * - `mark` — standalone black disc mark, for bullets / nav / favicons
 *
 * Height auto-scales from width via CSS (`height: auto`) so callers only
 * ever set one dimension. Default width is 200 and default alt is
 * "Omniscient AI".
 *
 * No forwardRef — this is a terminal brand element, not a compositional
 * primitive. Consumers that need a ref can render their own <img>.
 */

type Variant = 'stacked' | 'horizontal' | 'mark';

interface LogoProps extends Omit<ImgHTMLAttributes<HTMLImageElement>, 'src' | 'alt'> {
  variant?: Variant;
  width?: number | string;
  alt?: string;
}

const sources: Record<Variant, string> = {
  stacked: '/brand/logo-brain-stacked.png',
  horizontal: '/brand/logo-horizontal-with-graphic.png',
  mark: '/brand/logo-mark-circle.png',
};

export function Logo({
  variant = 'stacked',
  width = 200,
  alt = 'Omniscient AI',
  className,
  style,
  ...rest
}: LogoProps) {
  return (
    <img
      src={sources[variant]}
      alt={alt}
      width={width}
      className={cn(className)}
      style={{ height: 'auto', ...style }}
      {...rest}
    />
  );
}
