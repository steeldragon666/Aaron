import { AnchorHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

interface CTALinkProps extends AnchorHTMLAttributes<HTMLAnchorElement> {
  external?: boolean;
}

const base =
  'inline-flex items-center gap-1 font-medium ' +
  'border-b border-transparent hover:border-current ' +
  'transition-colors duration-[180ms] ease-[cubic-bezier(0.2,0.9,0.2,1)] ' +
  'focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2';

export const CTALink = forwardRef<HTMLAnchorElement, CTALinkProps>(
  ({ external, className, children, ...rest }, ref) => (
    <a
      ref={ref}
      className={cn(base, className)}
      target={external ? '_blank' : undefined}
      rel={external ? 'noopener noreferrer' : undefined}
      {...rest}
    >
      {children}
      <span aria-hidden>{external ? '↗' : '→'}</span>
    </a>
  )
);
CTALink.displayName = 'CTALink';
