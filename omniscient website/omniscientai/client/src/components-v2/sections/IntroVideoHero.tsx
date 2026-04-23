import { useEffect, useRef, useState } from 'react';
import { Link } from 'wouter';
import { cn } from '@/lib/utils';
import { Container } from '@/components-v2/layout';

/**
 * Landing hero that autoplays the Omniscient AI intro video.
 *
 * Iframes `/video/intro.html?embed=1` — the designer-delivered React
 * animation running as a standalone HTML experience in `public/video/`.
 * Embed mode hides the playback bar + tweaks panel so only the canvas
 * renders.
 *
 * When the video finishes (120s) OR the user clicks Skip, we:
 *   - reveal the text CTA row below the canvas
 *   - let the user scroll or click Continue to see the rest of the page
 *
 * The video keeps playing after completion (just sits on the final frame)
 * — we don't tear down the iframe unless the user navigates away.
 *
 * Falls back gracefully if JS is disabled or the iframe fails: the CTA
 * row is always rendered, just without the video context.
 */

interface IntroVideoHeroProps {
  primaryCta?: { label: string; href: string };
  secondaryCta?: { label: string; href: string };
  postVideoTitle?: string;
  postVideoLede?: string;
}

export function IntroVideoHero({
  primaryCta = { label: 'See what we build', href: '/services' },
  secondaryCta = { label: 'Book a call', href: '/book' },
  postVideoTitle = "Australia's sovereign applied AI company.",
  postVideoLede = "We build the products, platforms, and agents that modernise our most consequential industries — and operate them as managed services so our customers don't have to.",
}: IntroVideoHeroProps) {
  const [done, setDone] = useState(false);
  const iframeRef = useRef<HTMLIFrameElement | null>(null);

  useEffect(() => {
    const onMessage = (e: MessageEvent) => {
      if (e.data && typeof e.data === 'object' && e.data.type === 'omniscient-intro-done') {
        setDone(true);
      }
    };
    window.addEventListener('message', onMessage);
    return () => window.removeEventListener('message', onMessage);
  }, []);

  const skip = () => {
    // Tell the iframe to short-circuit its timer (symmetric), and mark done
    // locally so the CTA row appears immediately.
    iframeRef.current?.contentWindow?.postMessage({ type: 'omniscient-intro-skip' }, '*');
    setDone(true);
  };

  return (
    <section className="relative bg-paper">
      {/* Video canvas — 16:9 aspect, full width, capped so it doesn't
          get absurd on ultrawide displays. */}
      <div className="relative w-full bg-paper border-b border-line">
        <div className="relative w-full" style={{ paddingTop: '56.25%' }}>
          <iframe
            ref={iframeRef}
            src="/video/intro.html?embed=1"
            title="Omniscient AI intro"
            className="absolute inset-0 w-full h-full"
            loading="eager"
            /* sandbox-free on purpose: the iframe is same-origin and needs
               to postMessage the parent. Restricting sandbox breaks that. */
          />

          {/* Skip button — top right, always visible while video plays. */}
          {!done && (
            <button
              type="button"
              onClick={skip}
              className={cn(
                'absolute top-4 right-4 z-10',
                'inline-flex items-center gap-2 rounded-md',
                'bg-ink/80 text-paper backdrop-blur',
                'px-3 py-2 text-[13px] font-medium',
                'hover:bg-ink transition-colors',
                'focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2',
              )}
              aria-label="Skip intro video"
            >
              Skip intro →
            </button>
          )}
        </div>
      </div>

      {/* Text CTA row under the video. Always rendered, emphasised once
          the video finishes. */}
      <Container>
        <div
          className={cn(
            'py-12 lg:py-16 transition-opacity duration-500',
            done ? 'opacity-100' : 'opacity-90',
          )}
        >
          <div className="max-w-3xl">
            <div aria-hidden className="h-[3px] w-16 bg-blue mb-6" />
            <h1 className="display mb-5">{postVideoTitle}</h1>
            <p className="lede mb-8">{postVideoLede}</p>
            <div className="flex flex-wrap gap-3">
              <Link
                href={primaryCta.href}
                className={cn(
                  'inline-flex items-center gap-2 rounded-md bg-blue text-paper',
                  'px-[22px] py-[14px] text-[15px] font-semibold',
                  'transition-[transform,background-color,filter] duration-[180ms]',
                  'ease-[cubic-bezier(0.2,0.9,0.2,1)]',
                  'hover:-translate-y-px hover:bg-blue-deep active:translate-y-0 active:brightness-[.96]',
                  'focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2',
                )}
              >
                {primaryCta.label} <span aria-hidden>→</span>
              </Link>
              <Link
                href={secondaryCta.href}
                className={cn(
                  'inline-flex items-center gap-2 rounded-md bg-paper text-ink',
                  'border-[1.5px] border-ink px-[21px] py-[13px] text-[15px] font-semibold',
                  'transition-[transform,background-color] duration-[180ms]',
                  'ease-[cubic-bezier(0.2,0.9,0.2,1)]',
                  'hover:-translate-y-px hover:bg-paper-2 active:translate-y-0',
                  'focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2',
                )}
              >
                {secondaryCta.label}
              </Link>
            </div>
          </div>
        </div>
      </Container>
    </section>
  );
}
