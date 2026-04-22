import { Linkedin, Twitter } from 'lucide-react';
import { Container } from './Container';
import { Eyebrow } from '@/components-v2/ui';

/**
 * Site footer rendered on the --paper-2 tone so it separates visually
 * from the paper content above. Three-column grid on desktop, stacked
 * on mobile, capped off by a hairline-bordered bottom row with copyright
 * and the INTELLIGENCE // CONNECTIVITY // INNOVATION tagline.
 *
 * The 32px circle next to the wordmark is a stand-in for the upcoming
 * Phase 4 Logo component — keep it in sync with Nav.tsx for now.
 */

const navLinks = [
  { label: 'Workshops', href: '/workshops' },
  { label: 'Services', href: '/services' },
  { label: 'Case studies', href: '/case-studies' },
  { label: 'About', href: '/about' },
];

const legalLinks = [
  { label: 'Privacy policy', href: '/privacy' },
  { label: 'Terms', href: '/terms' },
];

const wordmarkStyle = {
  fontFamily: 'var(--font-display)',
  letterSpacing: '-0.01em',
} as const;

export function Footer() {
  return (
    <footer className="bg-paper-2 py-16 lg:py-24">
      <Container>
        <div className="grid grid-cols-1 gap-12 md:grid-cols-3 md:gap-8">
          {/* Col 1: Wordmark + tagline */}
          <div>
            <div className="flex items-center gap-2.5">
              <span className="h-8 w-8 rounded-full bg-ink" aria-hidden />
              <span className="text-[18px] font-bold text-ink" style={wordmarkStyle}>
                Omniscient AI
              </span>
            </div>
            <p className="mt-4 text-[14px] leading-relaxed text-ink-2 max-w-xs">
              Vendor-neutral AI training and consulting for Melbourne SMEs.
            </p>
          </div>

          {/* Col 2: Nav + legal links */}
          <nav className="flex flex-col gap-2 text-[14px] font-medium text-ink-2">
            {navLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="transition-colors hover:text-ink w-fit"
              >
                {link.label}
              </a>
            ))}
            {legalLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="transition-colors hover:text-ink w-fit"
              >
                {link.label}
              </a>
            ))}
          </nav>

          {/* Col 3: Contact */}
          <div className="flex flex-col gap-2 text-[14px] text-ink-2">
            <a
              href="mailto:hello@omniscientai.io"
              className="transition-colors hover:text-ink w-fit font-medium"
            >
              hello@omniscientai.io
            </a>
            <span>Melbourne, Australia</span>
            <div className="mt-3 flex items-center gap-3">
              <a
                href="https://www.linkedin.com/"
                aria-label="LinkedIn"
                className="text-ink transition-colors hover:text-ink-2"
                target="_blank"
                rel="noopener noreferrer"
              >
                <Linkedin className="h-5 w-5" strokeWidth={1.75} aria-hidden />
              </a>
              <a
                href="https://twitter.com/"
                aria-label="Twitter (X)"
                className="text-ink transition-colors hover:text-ink-2"
                target="_blank"
                rel="noopener noreferrer"
              >
                <Twitter className="h-5 w-5" strokeWidth={1.75} aria-hidden />
              </a>
            </div>
          </div>
        </div>

        {/* Bottom row */}
        <div className="mt-12 flex flex-col gap-4 border-t border-line pt-6 md:flex-row md:items-center md:justify-between">
          <span className="text-[13px] text-ink-2">
            © 2026 Omniscient AI. All rights reserved.
          </span>
          <Eyebrow>INTELLIGENCE // CONNECTIVITY // INNOVATION</Eyebrow>
        </div>
      </Container>
    </footer>
  );
}
