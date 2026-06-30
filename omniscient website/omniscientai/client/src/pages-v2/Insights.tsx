/**
 * Insights.tsx — v2 Insights / field notes index (/insights).
 *
 * Article index. Composition:
 *
 *   Layout → HeroCentric → category filter pills →
 *   FeaturedCard (first INSIGHT, full-width anchor) →
 *   3-up grid of remaining INSIGHTS (filtered by category)
 *
 * Category filter state lives on the page. The pill row derives from the
 * unique `category` values on INSIGHTS, always prefixed with "All". Clicking
 * a pill updates state; the featured article only shows when `All` is
 * selected (so the category view stays a clean grid). When a category is
 * selected, every matching article renders in the grid.
 *
 * INSIGHTS in lib/data.ts doesn't carry an image field — cards are
 * image-less for now. The data.ts shape has: slug, title, category,
 * categoryLabel, author, date, readTime, featured, excerpt.
 *
 * TODO: copy drafted 2026-04-22 — founder to validate tone.
 */

import { useMemo, useState } from 'react';
import SEO from '@/components/SEO';
import { Layout } from '@/components-v2/layout';
import { HeroCentric } from '@/components-v2/sections';
import { Card, FeaturedCard, Eyebrow, Lede, MonoBadge } from '@/components-v2/ui';
import { cn } from '@/lib/utils';
import { INSIGHTS } from '@/lib/data';

const ALL = 'all';

export default function Insights() {
  const [category, setCategory] = useState<string>(ALL);

  // Derive the category filter options from the data. Preserve first-seen
  // order so "ai-for-business" (the first insight's category) sits first,
  // followed by "ai-governance", etc. Pair each with its pretty label from
  // categoryLabel for display.
  const categories = useMemo(() => {
    const seen = new Map<string, string>();
    for (const insight of INSIGHTS) {
      if (!seen.has(insight.category)) {
        seen.set(insight.category, insight.categoryLabel);
      }
    }
    return Array.from(seen, ([value, label]) => ({ value, label }));
  }, []);

  // Sort newest first by `date` (ISO YYYY-MM-DD sorts lexicographically).
  // The featured article is the most recent — the first entry after sort.
  const sortedInsights = useMemo(
    () => [...INSIGHTS].sort((a, b) => b.date.localeCompare(a.date)),
    [],
  );

  const featured = sortedInsights[0];
  // Everything except the featured article is eligible for the grid. We
  // apply the category filter here. When "all" is selected we exclude the
  // featured from the grid so it only appears in its prominent slot; when
  // a specific category is selected we include matching articles regardless.
  const gridInsights = useMemo(() => {
    if (category === ALL) {
      return sortedInsights.slice(1);
    }
    return sortedInsights.filter((i) => i.category === category);
  }, [category, sortedInsights]);

  const showFeatured = category === ALL;

  // Format ISO date (YYYY-MM-DD) to a compact display like "15 Feb 2025".
  // We keep the formatter inline because the page is the only caller.
  const fmtDate = (iso: string) => {
    const d = new Date(iso);
    return d.toLocaleDateString('en-AU', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  };

  return (
    <Layout>
      <SEO
        title="Insights"
        description="Short pieces on AI, consulting, and the stuff that actually ships. Field notes from the work."
      />

      <HeroCentric
        eyebrow="Field notes"
        title="What we're learning as we go."
        lede="Short pieces on AI, consulting, and the stuff that actually ships."
      />

      {/* Category filter pills — horizontal row, wraps on narrow widths. */}
      <section className="py-8">
        <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
          <div
            role="group"
            aria-label="Filter by category"
            data-testid="category-filter-pills"
            className="flex flex-wrap items-center gap-2"
          >
            <FilterPill
              label="All"
              selected={category === ALL}
              onClick={() => setCategory(ALL)}
            />
            {categories.map((cat) => (
              <FilterPill
                key={cat.value}
                label={cat.label}
                selected={category === cat.value}
                onClick={() => setCategory(cat.value)}
              />
            ))}
          </div>
        </div>
      </section>

      {/* Featured article — only visible on the "All" view. Anchor
          FeaturedCard spanning full width, larger copy. */}
      {showFeatured && featured && (
        <section className="pb-12 lg:pb-16" data-testid="featured-article">
          <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
            <FeaturedCard
              as="a"
              href={`/insights/${featured.slug}`}
              className="flex flex-col gap-4"
            >
              <div className="flex flex-wrap items-center gap-2">
                <Eyebrow className="text-paper">{featured.categoryLabel}</Eyebrow>
                <span aria-hidden className="text-paper/50">
                  ·
                </span>
                <MonoBadge className="text-paper/80">
                  {featured.readTime}
                </MonoBadge>
              </div>
              <h2 className="font-semibold text-[32px] lg:text-[40px] leading-tight text-paper max-w-3xl">
                {featured.title}
              </h2>
              <Lede className="text-paper/80 max-w-3xl">
                {featured.excerpt}
              </Lede>
              <div className="mt-2 text-paper font-medium inline-flex items-center gap-1">
                Read the piece
                <span aria-hidden>→</span>
              </div>
            </FeaturedCard>
          </div>
        </section>
      )}

      {/* Article grid — 3-up on lg, 2-up on md, stacked on mobile. */}
      <section className="pb-16 lg:pb-24">
        <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
          {gridInsights.length === 0 ? (
            <p className="text-ink-2" data-testid="empty-insights">
              No field notes in this category yet. Check back soon.
            </p>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="insights-grid">
              {gridInsights.map((insight) => (
                <Card
                  key={insight.slug}
                  as="a"
                  href={`/insights/${insight.slug}`}
                  className="flex flex-col"
                >
                  <div className="flex items-center gap-2">
                    <Eyebrow>{insight.categoryLabel}</Eyebrow>
                    <span aria-hidden className="text-ink-3">
                      ·
                    </span>
                    <MonoBadge>{insight.readTime}</MonoBadge>
                  </div>
                  <h3 className="mt-4 font-semibold text-[22px] leading-tight text-ink">
                    {insight.title}
                  </h3>
                  <p className="mt-3 text-ink-2">{insight.excerpt}</p>
                  <div className="mt-5 text-[13px] text-ink-3">
                    {fmtDate(insight.date)}
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      </section>
    </Layout>
  );
}

/**
 * Internal filter pill button — selected state gets an ink fill, others
 * sit on paper-2 with a line border. Kept inline because only this page
 * uses it (so far).
 */
interface FilterPillProps {
  label: string;
  selected: boolean;
  onClick: () => void;
}

const pillBase =
  'rounded-full px-4 py-1.5 text-[14px] font-medium transition-colors ' +
  'duration-[180ms] ease-[cubic-bezier(0.2,0.9,0.2,1)] cursor-pointer ' +
  'focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2';

function FilterPill({ label, selected, onClick }: FilterPillProps) {
  return (
    <button
      type="button"
      aria-pressed={selected}
      onClick={onClick}
      className={cn(
        pillBase,
        selected
          ? 'bg-ink text-paper border border-ink hover:bg-ink/90'
          : 'bg-paper-2 text-ink border border-line hover:bg-paper-2/80',
      )}
    >
      {label}
    </button>
  );
}
