/**
 * PrivacyPolicy.tsx — v2 Privacy Policy page (/privacy-policy).
 *
 * Legal text is ported verbatim from the legacy page at
 * client/src/pages/PrivacyPolicy.tsx — legal copy is not rewritten in the
 * redesign. The v2 shell uses HeroCentric for the top block and ArticleBody
 * for the prose section. A MonoBadge at the top of the body carries the
 * "last updated" date.
 *
 * Composition:
 *
 *   Layout -> HeroCentric (narrow, eyebrow "Legal", title "Privacy policy") ->
 *   ArticleBody (MonoBadge last-updated + ported legal sections)
 */

import SEO from '@/components/SEO';
import { Layout } from '@/components-v2/layout';
import { HeroCentric, ArticleBody } from '@/components-v2/sections';
import { MonoBadge } from '@/components-v2/ui';

export default function PrivacyPolicy() {
  return (
    <Layout>
      <SEO
        title="Privacy policy"
        description="How OmniscientAI collects, uses, and protects your personal information. Compliant with the Australian Privacy Principles."
      />

      <HeroCentric
        eyebrow="Legal"
        title="Privacy policy"
        className="pb-8 lg:pb-12"
      />

      <ArticleBody>
        <p className="not-prose mb-8">
          <MonoBadge>Last updated: March 2026</MonoBadge>
        </p>

        <h2>1. Information we collect</h2>
        <p>
          We collect information you provide directly to us, including your
          name, email address, company name, phone number, and any other
          information you choose to provide when filling out forms, booking
          sessions, or contacting us.
        </p>
        <p>
          We also automatically collect certain information when you visit
          our website, including your IP address, browser type, operating
          system, referring URLs, and information about how you interact
          with our website.
        </p>

        <h2>2. How we use your information</h2>
        <p>
          We use the information we collect to provide, maintain, and
          improve our services, to process bookings and enquiries, to send
          you relevant communications about our workshops and services, and
          to comply with legal obligations.
        </p>

        <h2>3. Information sharing</h2>
        <p>
          We do not sell, trade, or otherwise transfer your personal
          information to third parties. We may share information with
          trusted service providers who assist us in operating our website
          and conducting our business, provided they agree to keep this
          information confidential.
        </p>

        <h2>4. Data security</h2>
        <p>
          We implement appropriate technical and organisational measures to
          protect your personal information against unauthorised access,
          alteration, disclosure, or destruction. However, no method of
          transmission over the internet is 100% secure.
        </p>

        <h2>5. Australian Privacy Principles</h2>
        <p>
          We comply with the Australian Privacy Principles (APPs) contained
          in the Privacy Act 1988 (Cth). You have the right to access and
          correct your personal information. To make a request, please
          contact us at{' '}
          <a href="mailto:hello@omniscientai.com.au">
            hello@omniscientai.com.au
          </a>
          .
        </p>

        <h2>6. Cookies</h2>
        <p>
          Our website uses cookies and similar tracking technologies to
          enhance your browsing experience and analyse website traffic. You
          can control cookie settings through your browser preferences.
        </p>

        <h2>7. Contact us</h2>
        <p>
          If you have any questions about this Privacy Policy, please
          contact us at:
        </p>
        <p>
          <strong>OmniscientAI</strong>
          <br />
          Email:{' '}
          <a href="mailto:hello@omniscientai.com.au">
            hello@omniscientai.com.au
          </a>
          <br />
          Location: Melbourne CBD, VIC 3000
          <br />
          ABN: 12 345 678 901
        </p>
      </ArticleBody>
    </Layout>
  );
}
