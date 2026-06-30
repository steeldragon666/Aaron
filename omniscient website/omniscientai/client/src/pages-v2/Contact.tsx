/**
 * Contact.tsx — v2 Contact page.
 *
 * The whole page is the CTA. Narrow HeroCentric, then a two-column layout:
 * ContactForm on the left (primary surface), contact details sidebar on
 * the right. Stacks on mobile. No closing CTAStrip — the page itself IS
 * the book-a-call prompt.
 *
 *   HeroCentric (narrow) → 2-column grid [ContactForm | details sidebar]
 *
 * `handleSubmit` is a local stub that logs submissions and resolves after
 * 500ms. Real backend wiring is Phase 12 polish — the ContactForm primitive
 * already handles loading/success/error states against the promise we return.
 */

import SEO from '@/components/SEO';
import { Linkedin, Twitter } from 'lucide-react';
import { Layout, Section } from '@/components-v2/layout';
import { HeroCentric, ContactForm } from '@/components-v2/sections';
// ContactFormData is only exported from the module file (not the barrel
// re-export), so pull the type directly from the source.
import type { ContactFormData } from '@/components-v2/sections/ContactForm';
import { Card, MonoBadge } from '@/components-v2/ui';

// Stub submit handler — Phase 7 copy-porting only. Real backend wiring
// (POST to /api/contact, toast confirmation, etc.) is Phase 12 polish.
// The 500ms delay exercises the ContactForm's loading state so the button
// transitions to "Sending..." during the artificial wait.
const handleSubmit = async (data: ContactFormData): Promise<void> => {
  // eslint-disable-next-line no-console
  console.log('[v2 contact submit]', data);
  await new Promise<void>((resolve) => setTimeout(resolve, 500));
};

export default function Contact() {
  return (
    <Layout>
      <SEO
        title="Contact"
        description="Get in touch with Omniscient AI. A 20-minute call, or a short message if you'd rather write. Based in Melbourne, Australia."
      />

      {/* Narrow hero — the page is already a form; the hero shouldn't dominate. */}
      <HeroCentric
        eyebrow="Contact"
        title="Let's talk."
        lede="A 20-minute call, or a short message if you'd rather write. We reply within two business days."
        className="pb-8 lg:pb-12"
      />

      {/* Two-column layout: form (2fr) + details sidebar (1fr). Stacks on
          mobile. Custom Section wrapper since we're not using Section's
          built-in header block here. */}
      <Section className="pt-0 lg:pt-0">
        <div className="grid grid-cols-1 lg:grid-cols-[2fr_1fr] gap-12">
          {/* Left: contact form */}
          <div>
            <ContactForm onSubmit={handleSubmit} />
          </div>

          {/* Right: details sidebar — paper-2 Card, single column of
              key contact info and socials. */}
          <aside>
            <Card tone="paper-2" className="flex flex-col gap-5">
              <h2 className="font-semibold text-[22px] leading-tight text-ink">
                Find us
              </h2>

              <div>
                <div className="text-[13px] uppercase tracking-wide text-ink-2 mb-1">
                  Email
                </div>
                <a
                  href="mailto:hello@omniscientai.io"
                  className="text-blue font-semibold hover:underline"
                >
                  hello@omniscientai.io
                </a>
              </div>

              <div>
                <div className="text-[13px] uppercase tracking-wide text-ink-2 mb-1">
                  Location
                </div>
                <div className="text-ink">Melbourne, Australia</div>
              </div>

              <div>
                <div className="text-[13px] uppercase tracking-wide text-ink-2 mb-2">
                  Hours
                </div>
                <MonoBadge>Mon–Fri, 9am–5pm AEST</MonoBadge>
              </div>

              <div>
                <div className="text-[13px] uppercase tracking-wide text-ink-2 mb-2">
                  Social
                </div>
                {/* Socials mirror the Footer — LinkedIn + Twitter/X. Keep in
                    sync with Footer.tsx if socials change. */}
                <div className="flex items-center gap-3">
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
            </Card>
          </aside>
        </div>
      </Section>
    </Layout>
  );
}
