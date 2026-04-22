/**
 * InsightArticle.tsx — v2 long-form article page (/insights/:slug).
 *
 * Looks up the article by slug from INSIGHTS in lib/data.ts. Unknown slugs
 * render a small 404-style fallback with a link back to /insights.
 *
 * Composition (valid slug):
 *
 *   Layout -> back-link (CTALink "Field notes" -> /insights) ->
 *   ArticleHeader (category, title, lede, author · date · read time) ->
 *   ArticleBody (article content -- placeholder for now, data has no body) ->
 *   Author bio Card (paper-2) ->
 *   Related articles grid (3-up, excludes current) ->
 *   CTAStrip "Like this? Book a call to discuss"
 *
 * INSIGHTS in lib/data.ts currently has no `content` field -- we render a
 * placeholder paragraph. When authored body copy lands in lib/data.ts (as
 * a JSX-safe renderer, e.g. a component or a sanitized-HTML string), swap
 * the placeholder branch below for the real render path. The `excerpt`
 * field is passed to ArticleHeader as the lede for now.
 *
 * TODO: drafted 2026-04-22 -- founder to validate tone. When real body
 * copy is authored, add a `content` field to INSIGHTS and render it here.
 */

import { useParams } from 'wouter';
import SEO from '@/components/SEO';
import { Layout, Section } from '@/components-v2/layout';
import {
  ArticleHeader,
  ArticleBody,
  CTAStrip,
} from '@/components-v2/sections';
import {
  Card,
  CTALink,
  Eyebrow,
  MonoBadge,
} from '@/components-v2/ui';
import { INSIGHTS } from '@/lib/data';

/**
 * Format an ISO (YYYY-MM-DD) date to en-AU "15 Feb 2025". Kept inline --
 * Insights index uses the same shape, but duplicating avoids creating a
 * one-function util file for two callers.
 */
function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString('en-AU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

// Fallback rendered when the slug doesn't match a known insight. Kept
// consistent with ServiceNotFound / IndustryNotFound / WorkshopNotFound.
function InsightNotFound() {
  return (
    <Layout>
      <SEO
        title="Article not found"
        description="We couldn't find that article."
      />
      <Section>
        <div className="max-w-xl">
          <Eyebrow className="mb-4 block">404</Eyebrow>
          <h1 className="display mb-4">Article not found</h1>
          <p className="lede mb-8">
            We couldn&apos;t find an article matching that URL. It may have
            been renamed or moved.
          </p>
          <CTALink href="/insights" className="text-blue">
            Back to field notes
          </CTALink>
        </div>
      </Section>
    </Layout>
  );
}

export default function InsightArticle() {
  const params = useParams<{ slug: string }>();
  const slug = params.slug;
  const insight = INSIGHTS.find((i) => i.slug === slug);

  if (!insight) {
    return <InsightNotFound />;
  }

  // Related articles -- every insight except the current one. Cap at 3 to
  // keep the grid clean; the set doesn't need to be category-matched yet
  // (INSIGHTS is small and "more field notes" reads fine across categories).
  const related = INSIGHTS.filter((i) => i.slug !== insight.slug).slice(0, 3);

  return (
    <Layout>
      <SEO title={insight.title} description={insight.excerpt} />

      {/* Back-link sits above the ArticleHeader. Same pattern as
          ServiceDetail / WorkshopDetail -- small-type CTALink. */}
      <div className="max-w-[1200px] mx-auto px-6 lg:px-8 pt-12">
        <CTALink
          href="/insights"
          className="text-sm text-ink-3"
          data-testid="back-to-insights"
        >
          Field notes
        </CTALink>
      </div>

      <ArticleHeader
        category={insight.categoryLabel}
        title={insight.title}
        // INSIGHTS uses `excerpt` as the summary line -- pass that through
        // as the ArticleHeader's lede so the header block has a pull-quote.
        lede={insight.excerpt}
        author={insight.author}
        publishDate={formatDate(insight.date)}
        readTime={insight.readTime}
      />

      <ArticleBody>
        {/* INSIGHTS in lib/data.ts doesn't carry a `content` field yet, so
            we render a placeholder with onward links. Once the data grows
            body copy, replace this block with the real render path. */}
        <p>
          This article is being written. In the meantime, the{' '}
          <a href="/insights">field notes index</a> has our published
          pieces.
        </p>
        <p>
          If you&apos;d like to chat about what&apos;s covered here,{' '}
          <a href="/book">book a 20-minute call</a> -- we&apos;re happy
          to walk through the specifics.
        </p>
      </ArticleBody>

      {/* Author bio -- small paper-2 Card at the bottom of the body. */}
      <Section tone="paper-2">
        <div className="mx-auto max-w-[800px]">
          <Card tone="paper-2" className="flex items-start gap-5">
            <div className="h-14 w-14 rounded-full bg-ink shrink-0" aria-hidden />
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <Eyebrow>About the author</Eyebrow>
              </div>
              <h3 className="mt-2 font-semibold text-[20px] leading-tight text-ink">
                {insight.author}
              </h3>
              <p className="mt-2 text-ink-2">
                {/* TODO: swap for real author bio copy when authors are
                    named individuals rather than the "OmniscientAI Team"
                    byline. */}
                Field notes from the OmniscientAI team -- working
                vendor-neutral with Melbourne SMEs on AI strategy,
                workshops, and practical engagements.
              </p>
            </div>
          </Card>
        </div>
      </Section>

      {/* Related articles -- 3-up grid, same card pattern as the Insights
          index. Excludes the current article. */}
      {related.length > 0 && (
        <Section eyebrow="Keep reading" title="More field notes.">
          <div
            className="grid md:grid-cols-2 lg:grid-cols-3 gap-6"
            data-testid="related-articles"
          >
            {related.map((relatedInsight) => (
              <Card
                key={relatedInsight.slug}
                as="a"
                href={`/insights/${relatedInsight.slug}`}
                className="flex flex-col"
              >
                <div className="flex items-center gap-2">
                  <Eyebrow>{relatedInsight.categoryLabel}</Eyebrow>
                  <span aria-hidden className="text-ink-3">
                    ·
                  </span>
                  <MonoBadge>{relatedInsight.readTime}</MonoBadge>
                </div>
                <h3 className="mt-4 font-semibold text-[22px] leading-tight text-ink">
                  {relatedInsight.title}
                </h3>
                <p className="mt-3 text-ink-2">{relatedInsight.excerpt}</p>
              </Card>
            ))}
          </div>
        </Section>
      )}

      <CTAStrip
        tone="paper"
        title="Like this?"
        lede="Book a call to discuss what you're working on. 20 minutes, no sales pitch."
        primaryCta={{ label: 'Book a call', href: '/book' }}
        secondaryCta={{ label: 'More field notes', href: '/insights' }}
      />
    </Layout>
  );
}
