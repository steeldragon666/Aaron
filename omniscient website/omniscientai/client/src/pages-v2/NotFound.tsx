/**
 * NotFound.tsx — v2 404 page (catchall route).
 *
 * Replaces the V2Placeholder stand-in at the end of V2Routes. Minimal,
 * centered layout with a display "404", a friendly line, and two CTAs
 * back into the site. A corner BrainGraphic adds a small decorative
 * accent without dominating the screen.
 *
 *   Layout -> centered div (min-h-[70vh] grid place-items-center) with
 *             404 display, eyebrow, lede, primary+secondary CTAs, and a
 *             corner BrainGraphic.
 */

import SEO from '@/components/SEO';
import { Layout } from '@/components-v2/layout';
import { Display, Eyebrow, Lede } from '@/components-v2/ui';
import { BrainGraphic } from '@/components-v2/brand';

// Matches Button primary+lg — keep aligned with
// client/src/components-v2/ui/Button.tsx if its primary styling changes.
// (Mirrors the inline CTA styling used in HeroCentric.tsx.)
const primaryCtaClass =
  'inline-flex items-center gap-2 rounded-md bg-blue text-paper ' +
  'px-[22px] py-[14px] text-[15px] font-semibold ' +
  'transition-[transform,background-color,filter] duration-[180ms] ' +
  'ease-[cubic-bezier(0.2,0.9,0.2,1)] ' +
  'hover:-translate-y-px hover:bg-blue-deep active:translate-y-0 active:brightness-[.96] ' +
  'focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2';

// Matches Button secondary+lg.
const secondaryCtaClass =
  'inline-flex items-center gap-2 rounded-md bg-paper text-ink ' +
  'border-[1.5px] border-ink px-[21px] py-[13px] text-[15px] font-semibold ' +
  'transition-[transform,background-color] duration-[180ms] ' +
  'ease-[cubic-bezier(0.2,0.9,0.2,1)] ' +
  'hover:-translate-y-px hover:bg-paper-2 active:translate-y-0 ' +
  'focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2';

export default function NotFound() {
  return (
    <Layout>
      <SEO
        title="Page not found"
        description="The page you're looking for doesn't exist or has moved."
      />

      <section className="relative min-h-[70vh] grid place-items-center bg-paper overflow-hidden">
        {/* Corner decoration — purely decorative, sits in the bottom-right. */}
        <div
          aria-hidden
          className="pointer-events-none absolute bottom-6 right-6 opacity-60"
        >
          <BrainGraphic variant="circles" size="corner" />
        </div>

        <div className="relative text-center max-w-xl px-6">
          <Display as="h1" className="mb-4">
            404
          </Display>
          <Eyebrow className="mb-4 block">Page not found</Eyebrow>
          <Lede className="mb-8">
            The page you&apos;re looking for doesn&apos;t exist or has moved.
          </Lede>
          <div className="flex flex-wrap justify-center gap-3">
            <a href="/" className={primaryCtaClass}>
              Back to home <span aria-hidden>→</span>
            </a>
            <a href="/workshops" className={secondaryCtaClass}>
              Browse workshops
            </a>
          </div>
        </div>
      </section>
    </Layout>
  );
}
