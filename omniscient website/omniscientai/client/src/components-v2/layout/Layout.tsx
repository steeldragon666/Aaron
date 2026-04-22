import { ReactNode } from 'react';
import { Nav } from './Nav';
import { Footer } from './Footer';

/**
 * Thin page wrapper: skip-to-content link, Nav, <main>, Footer.
 *
 * `hideNav` and `hideFooter` exist for minimal-chrome contexts
 * (e.g. the Book page). The skip link is always first so keyboard
 * users can jump past the nav — it targets <main id="main">, which
 * also serves as the landmark for assistive tech.
 */

interface LayoutProps {
  children: ReactNode;
  hideNav?: boolean;
  hideFooter?: boolean;
}

export function Layout({ children, hideNav, hideFooter }: LayoutProps) {
  return (
    <>
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:bg-ink focus:text-paper focus:px-4 focus:py-2 focus:rounded-md focus:z-[70]"
      >
        Skip to content
      </a>
      {!hideNav && <Nav />}
      <main id="main">{children}</main>
      {!hideFooter && <Footer />}
    </>
  );
}
