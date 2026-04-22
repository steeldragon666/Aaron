import { AnchorHTMLAttributes, forwardRef } from 'react';
import { Link } from 'wouter';
import { cn } from '@/lib/utils';

interface CTALinkProps extends AnchorHTMLAttributes<HTMLAnchorElement> {
  external?: boolean;
}

const base =
  'inline-flex items-center gap-1 font-medium ' +
  'border-b border-transparent hover:border-current ' +
  'transition-colors duration-[180ms] ease-[cubic-bezier(0.2,0.9,0.2,1)] ' +
  'focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2';

/**
 * Decide whether the href points at a client-side route. We route via wouter
 * under a nested router at `/_v2` in dev preview, and at app-root in
 * production (USE_V2=true). Anything that's not a root-relative path
 * (mailto:, tel:, https:, #hash, or any href marked `external`) stays a
 * plain <a>.
 */
function isInternalHref(href: string | undefined): boolean {
  if (!href) return false;
  if (!href.startsWith('/')) return false;
  // `//example.com` is protocol-relative → external, not a wouter route.
  if (href.startsWith('//')) return false;
  return true;
}

export const CTALink = forwardRef<HTMLAnchorElement, CTALinkProps>(
  ({ external, className, children, href, ...rest }, ref) => {
    const arrow = external ? '↗' : '→';
    const classes = cn(base, className);
    const shouldRouteInternally = !external && isInternalHref(href);

    if (shouldRouteInternally && href) {
      // wouter's Link renders an <a> with a client-side click handler. Under
      // a nested Router (e.g. `<Route path="/_v2" nest>`), it prepends the
      // nest base automatically, so `/workshops` resolves to `/_v2/workshops`
      // in dev preview and stays `/workshops` in production.
      return (
        <Link ref={ref} href={href} className={classes} {...rest}>
          {children}
          <span aria-hidden>{arrow}</span>
        </Link>
      );
    }

    return (
      <a
        ref={ref}
        href={href}
        className={classes}
        target={external ? '_blank' : undefined}
        rel={external ? 'noopener noreferrer' : undefined}
        {...rest}
      >
        {children}
        <span aria-hidden>{arrow}</span>
      </a>
    );
  }
);
CTALink.displayName = 'CTALink';
