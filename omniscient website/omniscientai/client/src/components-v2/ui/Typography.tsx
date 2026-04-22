import { ElementType, HTMLAttributes, Ref, forwardRef } from 'react';
import { cn } from '@/lib/utils';

// Thin wrappers over utility classes in omniscient.css. Each component exposes
// a small constrained `as` prop for semantic flexibility. Since the rendered
// tag varies, the forwarded ref is typed to the common `HTMLElement` base and
// the `Component` is cast to a single `ElementType` to satisfy TypeScript.

interface EyebrowProps extends HTMLAttributes<HTMLElement> {
  as?: 'span' | 'div' | 'p';
}

export const Eyebrow = forwardRef<HTMLElement, EyebrowProps>(
  ({ as = 'span', className, children, ...rest }, ref) => {
    const Component = as as ElementType;
    return (
      <Component ref={ref as Ref<HTMLElement>} className={cn('eyebrow', className)} {...rest}>
        {children}
      </Component>
    );
  },
);
Eyebrow.displayName = 'Eyebrow';

interface DisplayProps extends HTMLAttributes<HTMLElement> {
  as?: 'h1' | 'h2' | 'div';
}

export const Display = forwardRef<HTMLElement, DisplayProps>(
  ({ as = 'h1', className, children, ...rest }, ref) => {
    const Component = as as ElementType;
    return (
      <Component ref={ref as Ref<HTMLElement>} className={cn('display', className)} {...rest}>
        {children}
      </Component>
    );
  },
);
Display.displayName = 'Display';

interface LedeProps extends HTMLAttributes<HTMLElement> {
  as?: 'p' | 'div';
}

export const Lede = forwardRef<HTMLElement, LedeProps>(
  ({ as = 'p', className, children, ...rest }, ref) => {
    const Component = as as ElementType;
    return (
      <Component ref={ref as Ref<HTMLElement>} className={cn('lede', className)} {...rest}>
        {children}
      </Component>
    );
  },
);
Lede.displayName = 'Lede';

interface MonoBadgeProps extends HTMLAttributes<HTMLElement> {
  as?: 'span' | 'div';
}

export const MonoBadge = forwardRef<HTMLElement, MonoBadgeProps>(
  ({ as = 'span', className, children, ...rest }, ref) => {
    const Component = as as ElementType;
    return (
      <Component ref={ref as Ref<HTMLElement>} className={cn('mono-badge', className)} {...rest}>
        {children}
      </Component>
    );
  },
);
MonoBadge.displayName = 'MonoBadge';
