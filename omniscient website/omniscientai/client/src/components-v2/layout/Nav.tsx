import { useEffect, useState } from 'react';
import { Menu, X } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Top-level site nav. Sticky translucent header on desktop with a
 * full-screen ink-section drawer on mobile (<768px).
 *
 * Uses a plain anchor for the "Book a call" CTA styled to match the
 * primary Button (Button is button-only; wrapping it in <a> would nest
 * interactive controls). Keep styling in sync with Button.tsx primary.
 *
 * The 32px circle next to the wordmark is a stand-in for the upcoming
 * Phase 4 Logo component.
 */

const links = [
  { label: 'Workshops', href: '/workshops' },
  { label: 'Services', href: '/services' },
  { label: 'Case studies', href: '/case-studies' },
  { label: 'About', href: '/about' },
];

// Matches Button primary+md — keep these classes aligned with
// client/src/components-v2/ui/Button.tsx if it changes.
const ctaBase =
  'inline-flex items-center gap-2 font-semibold rounded-md ' +
  'transition-[transform,background-color,filter] duration-[180ms] ' +
  'ease-[cubic-bezier(0.2,0.9,0.2,1)] ' +
  'hover:-translate-y-px active:translate-y-0 active:brightness-[.96] ' +
  'focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2 ' +
  'bg-blue text-paper hover:bg-blue-deep';

const wordmarkStyle = {
  fontFamily: 'var(--font-display)',
  letterSpacing: '-0.01em',
} as const;

export function Nav() {
  const [open, setOpen] = useState(false);

  // Escape closes the drawer
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false);
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [open]);

  // Lock body scroll while the drawer is open.
  useEffect(() => {
    if (!open) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = prev;
    };
  }, [open]);

  return (
    <>
      <header className="sticky top-0 z-50 bg-paper/70 backdrop-blur-xl backdrop-saturate-150 border-b border-line">
        <div className="mx-auto max-w-[1240px] flex h-16 items-center justify-between px-6 lg:px-[72px]">
          {/* Logo */}
          <a href="/" className="flex items-center gap-2.5 shrink-0">
            <span className="h-8 w-8 rounded-full bg-ink" aria-hidden />
            <span className="text-[18px] font-bold text-ink" style={wordmarkStyle}>
              Omniscient AI
            </span>
          </a>

          {/* Desktop links */}
          <nav className="hidden md:flex items-center gap-7 text-[14px] font-medium text-ink-2">
            {links.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="transition-colors hover:text-ink"
              >
                {link.label}
              </a>
            ))}
          </nav>

          {/* Desktop CTA + Mobile hamburger */}
          <div className="flex items-center gap-2">
            <a
              href="/book"
              className={cn('hidden md:inline-flex', ctaBase, 'px-4 py-2 text-[14px]')}
            >
              Book a call
              <span aria-hidden>→</span>
            </a>
            <button
              type="button"
              className="md:hidden inline-flex h-10 w-10 items-center justify-center rounded-md border border-line text-ink hover:bg-paper-2 focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2 cursor-pointer"
              aria-label="Open menu"
              aria-expanded={open}
              onClick={() => setOpen(true)}
            >
              <Menu className="h-5 w-5" strokeWidth={1.75} />
            </button>
          </div>
        </div>
      </header>

      {/* Mobile drawer — full-screen ink-section overlay */}
      {open && (
        <div
          className="fixed inset-0 z-[60] ink-section flex flex-col"
          role="dialog"
          aria-modal="true"
          aria-label="Site menu"
        >
          <div className="flex h-16 items-center justify-between px-6 border-b border-white/10">
            <span className="text-[18px] font-bold" style={wordmarkStyle}>
              Omniscient AI
            </span>
            <button
              type="button"
              aria-label="Close menu"
              onClick={() => setOpen(false)}
              className="inline-flex h-10 w-10 items-center justify-center rounded-md hover:bg-white/10 focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2 cursor-pointer"
            >
              <X className="h-5 w-5" strokeWidth={1.75} />
            </button>
          </div>
          <nav className="flex flex-col gap-6 p-6 text-[22px] font-semibold">
            {links.map((link) => (
              <a
                key={link.href}
                href={link.href}
                onClick={() => setOpen(false)}
                className="hover:text-blue-glow transition-colors"
              >
                {link.label}
              </a>
            ))}
          </nav>
          <div className="mt-auto p-6 border-t border-white/10">
            <a
              href="/book"
              onClick={() => setOpen(false)}
              className={cn(
                ctaBase,
                'w-full justify-center px-[22px] py-[14px] text-[15px]',
              )}
            >
              Book a call
              <span aria-hidden>→</span>
            </a>
          </div>
        </div>
      )}
    </>
  );
}
