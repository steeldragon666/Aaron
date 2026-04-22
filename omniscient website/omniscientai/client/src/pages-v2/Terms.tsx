/**
 * Terms.tsx — v2 Terms of service page (/terms).
 *
 * Legal text is ported verbatim from the legacy page at
 * client/src/pages/Terms.tsx — legal copy is not rewritten in the redesign.
 * The v2 shell uses HeroCentric for the top block and ArticleBody for the
 * prose section. A MonoBadge at the top of the body carries the "last
 * updated" date.
 *
 * Composition:
 *
 *   Layout -> HeroCentric (narrow, eyebrow "Legal", title "Terms of service") ->
 *   ArticleBody (MonoBadge last-updated + ported legal sections)
 */

import SEO from '@/components/SEO';
import { Layout } from '@/components-v2/layout';
import { HeroCentric, ArticleBody } from '@/components-v2/sections';
import { MonoBadge } from '@/components-v2/ui';

export default function Terms() {
  return (
    <Layout>
      <SEO
        title="Terms of service"
        description="Terms governing your use of OmniscientAI workshops and consulting services."
      />

      <HeroCentric
        eyebrow="Legal"
        title="Terms of service"
        className="pb-8 lg:pb-12"
      />

      <ArticleBody>
        <p className="not-prose mb-8">
          <MonoBadge>Last updated: March 2026</MonoBadge>
        </p>

        <h2>1. Services</h2>
        <p>
          OmniscientAI provides AI training workshops, consulting services,
          and related educational content for businesses. Our services are
          designed to help organisations understand, evaluate, and implement
          AI solutions in a vendor-neutral manner.
        </p>

        <h2>2. Booking and payment</h2>
        <p>
          Workshop bookings are confirmed upon receipt of payment or a
          signed agreement. Prices are quoted in Australian Dollars (AUD)
          and are exclusive of GST unless otherwise stated. We accept
          payment via bank transfer and major credit cards.
        </p>

        <h2>3. Cancellation policy</h2>
        <p>
          Cancellations made more than 14 days before the scheduled workshop
          will receive a full refund. Cancellations made 7–14 days before
          will receive a 50% refund. Cancellations made less than 7 days
          before are non-refundable. Rescheduling is available at no
          additional cost with at least 7 days&apos; notice.
        </p>

        <h2>4. Intellectual property</h2>
        <p>
          All workshop materials, content, and resources provided by
          OmniscientAI remain our intellectual property. Participants may
          use materials for internal business purposes but may not
          redistribute, resell, or publish them without written permission.
        </p>

        <h2>5. Limitation of liability</h2>
        <p>
          Our workshops and consulting services provide general guidance
          and training. We do not guarantee specific business outcomes. Our
          liability is limited to the fees paid for the specific service in
          question. We are not liable for any indirect, consequential, or
          incidental damages.
        </p>

        <h2>6. Vendor neutrality</h2>
        <p>
          OmniscientAI maintains vendor neutrality in all our training and
          consulting engagements. We do not receive commissions or referral
          fees from AI tool vendors. Any tool recommendations are based
          solely on suitability for the client&apos;s needs.
        </p>

        <h2>7. Governing law</h2>
        <p>
          These terms are governed by the laws of the State of Victoria,
          Australia. Any disputes will be resolved in the courts of
          Victoria.
        </p>

        <h2>8. Contact</h2>
        <p>
          For questions about these terms, contact us at{' '}
          <a href="mailto:hello@omniscientai.com.au">
            hello@omniscientai.com.au
          </a>
          .
        </p>
      </ArticleBody>
    </Layout>
  );
}
