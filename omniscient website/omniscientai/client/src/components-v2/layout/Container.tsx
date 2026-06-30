import { ElementType, HTMLAttributes, Ref, forwardRef } from 'react';
import { cn } from '@/lib/utils';

// Shared max-width + horizontal gutter wrapper for v2 layout.
// Centered at 1240px, 24px side padding on mobile, 72px from the lg breakpoint up.
// Polymorphic `as` so callers can pick the right semantic element without
// duplicating spacing/width logic.

interface ContainerProps extends HTMLAttributes<HTMLElement> {
  as?: 'div' | 'section' | 'main' | 'article';
}

export const Container = forwardRef<HTMLElement, ContainerProps>(
  ({ as = 'div', className, children, ...rest }, ref) => {
    const Component = as as ElementType;
    return (
      <Component
        ref={ref as Ref<HTMLElement>}
        className={cn('w-full max-w-[1240px] mx-auto px-6 lg:px-[72px]', className)}
        {...rest}
      >
        {children}
      </Component>
    );
  },
);
Container.displayName = 'Container';
