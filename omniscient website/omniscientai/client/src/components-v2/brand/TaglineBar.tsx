import { HTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

/**
 * Signature brand tagline rendered as an eyebrow-styled row:
 *
 *   INTELLIGENCE // CONNECTIVITY // INNOVATION
 *
 * Styled via the `.eyebrow` utility (12px / 600 / UPPERCASE /
 * tracking 0.14em / `--ink-3`). The `//` separators are dimmed to
 * ~60% opacity so they recede visually but remain readable.
 *
 * Design system rule: **max one TaglineBar per page.** This is a
 * signature element — overuse dilutes the effect. Prefer the
 * `Eyebrow` primitive for generic eyebrow text.
 *
 * No forwardRef — this is a terminal brand element, not a
 * compositional primitive.
 */

type Align = 'left' | 'center' | 'right';

interface TaglineBarProps extends HTMLAttributes<HTMLDivElement> {
  align?: Align;
}

const alignClasses: Record<Align, string> = {
  left: 'text-left',
  center: 'text-center',
  right: 'text-right',
};

export function TaglineBar({ align = 'left', className, ...rest }: TaglineBarProps) {
  return (
    <div className={cn('eyebrow', alignClasses[align], className)} {...rest}>
      INTELLIGENCE
      <span className="mx-2 opacity-60">//</span>
      CONNECTIVITY
      <span className="mx-2 opacity-60">//</span>
      INNOVATION
    </div>
  );
}
