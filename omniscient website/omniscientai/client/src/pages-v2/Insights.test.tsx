/**
 * Smoke tests for the v2 Insights index page. Verifies the page composes —
 * hero, category filter pills, featured article in its prominent slot, and
 * the article grid with the remaining INSIGHTS. Also exercises filter
 * interaction: clicking a category pill should narrow the grid to only
 * articles in that category and hide the featured slot.
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect } from 'vitest';
import { HelmetProvider } from 'react-helmet-async';
import Insights from './Insights';
import { INSIGHTS } from '@/lib/data';

function renderPage() {
  return render(
    <HelmetProvider>
      <Insights />
    </HelmetProvider>,
  );
}

// Newest INSIGHT (matches the page's own sort — lex compare on ISO date).
const sortedInsights = [...INSIGHTS].sort((a, b) => b.date.localeCompare(a.date));
const featuredInsight = sortedInsights[0];

describe('Insights index page', () => {
  it('renders hero title and lede', () => {
    renderPage();
    expect(
      screen.getByRole('heading', {
        level: 1,
        name: /What we're learning as we go/i,
      }),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        /Short pieces on AI, consulting, and the stuff that actually ships/i,
      ),
    ).toBeInTheDocument();
  });

  it('renders every insight (featured in its slot, rest in the grid)', () => {
    renderPage();
    // All INSIGHTS titles should appear somewhere on the page.
    for (const insight of INSIGHTS) {
      expect(screen.getByText(insight.title)).toBeInTheDocument();
    }
  });

  it('renders the featured article in a prominent FeaturedCard slot', () => {
    renderPage();
    const featuredSlot = screen.getByTestId('featured-article');
    expect(featuredSlot).toBeInTheDocument();
    expect(featuredSlot.textContent).toContain(featuredInsight.title);
    // The FeaturedCard is an anchor to /insights/{slug}.
    const anchor = featuredSlot.querySelector('a');
    expect(anchor?.getAttribute('href')).toBe(`/insights/${featuredInsight.slug}`);
  });

  it('links each article card to /insights/:slug', () => {
    renderPage();
    const grid = screen.getByTestId('insights-grid');
    // Every grid card is an anchor. The grid excludes the featured article on
    // the default "All" view, so expected count is INSIGHTS.length - 1.
    const anchors = grid.querySelectorAll('a');
    expect(anchors.length).toBe(INSIGHTS.length - 1);
    // Each anchor points at /insights/{slug} for an insight other than the
    // featured one.
    const nonFeatured = INSIGHTS.filter((i) => i.slug !== featuredInsight.slug);
    for (const insight of nonFeatured) {
      const match = Array.from(anchors).find(
        (a) => a.getAttribute('href') === `/insights/${insight.slug}`,
      );
      expect(match).toBeTruthy();
    }
  });

  it('filters the grid when a category pill is clicked', async () => {
    const user = userEvent.setup();
    renderPage();
    // Pick a category that has multiple articles — "AI for Business"
    // carries at least two entries in lib/data.ts.
    const target = INSIGHTS.find((i) => i.categoryLabel === 'AI for Business');
    if (!target) throw new Error('Expected an "AI for Business" insight in data');

    const pillRow = screen.getByTestId('category-filter-pills');
    const pill = Array.from(pillRow.querySelectorAll('button')).find(
      (b) => b.textContent?.trim() === 'AI for Business',
    );
    expect(pill).toBeTruthy();
    await user.click(pill!);

    // Pill is now selected
    expect(pill).toHaveAttribute('aria-pressed', 'true');

    // Featured slot hides when a category is active — the full-width
    // featured article should be gone so the view reads as a filtered grid.
    expect(screen.queryByTestId('featured-article')).not.toBeInTheDocument();

    // Grid now contains exactly the articles in that category, and nothing
    // from other categories.
    const matching = INSIGHTS.filter(
      (i) => i.categoryLabel === 'AI for Business',
    );
    const nonMatching = INSIGHTS.filter(
      (i) => i.categoryLabel !== 'AI for Business',
    );
    for (const insight of matching) {
      expect(screen.getByText(insight.title)).toBeInTheDocument();
    }
    for (const insight of nonMatching) {
      expect(screen.queryByText(insight.title)).not.toBeInTheDocument();
    }
  });
});
