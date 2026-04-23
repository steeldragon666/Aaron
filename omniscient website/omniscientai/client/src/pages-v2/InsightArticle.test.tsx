/**
 * Smoke tests for the v2 InsightArticle page. Exercises the dynamic-slug
 * route with an in-memory location at /insights/{slug}. Asserts composition
 * -- back-link, ArticleHeader, ArticleBody placeholder, related articles
 * grid (excludes current insight), CTAStrip -- plus the 404-style
 * fallback for unknown slugs.
 *
 * ArticleHeader / ArticleBody internals are covered by their own test
 * suites.
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { HelmetProvider } from 'react-helmet-async';
import { Route, Router, Switch } from 'wouter';
import { memoryLocation } from 'wouter/memory-location';
import InsightArticle from './InsightArticle';
import { INSIGHTS } from '@/lib/data';

function renderAt(path: string) {
  const { hook } = memoryLocation({ path, static: true });
  return render(
    <HelmetProvider>
      <Router hook={hook}>
        <Switch>
          <Route path="/insights/:slug" component={InsightArticle} />
          <Route component={InsightArticle} />
        </Switch>
      </Router>
    </HelmetProvider>,
  );
}

const VALID_INSIGHT = INSIGHTS[0];

describe('InsightArticle page', () => {
  it('renders the article title as the ArticleHeader h1 when the slug is valid', () => {
    renderAt(`/insights/${VALID_INSIGHT.slug}`);
    expect(
      screen.getByRole('heading', { level: 1, name: VALID_INSIGHT.title }),
    ).toBeInTheDocument();
  });

  it('renders the ArticleHeader metadata (category, author, read time)', () => {
    renderAt(`/insights/${VALID_INSIGHT.slug}`);
    // Category eyebrow (also appears on related cards, so getAllByText with
    // a length check covers the duplication.)
    expect(screen.getAllByText(VALID_INSIGHT.categoryLabel).length).toBeGreaterThan(0);
    // Author name shows up in both the header badge and the bio section.
    expect(screen.getAllByText(VALID_INSIGHT.author).length).toBeGreaterThan(0);
    // Read time badge — may also appear on related cards matching the same
    // duration, so use getAllByText.
    expect(screen.getAllByText(VALID_INSIGHT.readTime).length).toBeGreaterThan(0);
  });

  it('renders the ArticleBody (placeholder content rendered)', () => {
    renderAt(`/insights/${VALID_INSIGHT.slug}`);
    // Placeholder copy rendered inside ArticleBody.
    expect(
      screen.getByText(/This article is being written/i),
    ).toBeInTheDocument();
  });

  it('renders related articles excluding the current insight', () => {
    renderAt(`/insights/${VALID_INSIGHT.slug}`);
    const related = screen.getByTestId('related-articles');
    expect(related).toBeInTheDocument();
    // Related grid has up to 3 cards, each an anchor to another insight.
    const anchors = related.querySelectorAll('a');
    expect(anchors.length).toBeGreaterThan(0);
    expect(anchors.length).toBeLessThanOrEqual(3);
    // None of the related anchors should point at the current insight.
    for (const a of Array.from(anchors)) {
      expect(a.getAttribute('href')).not.toBe(
        `/insights/${VALID_INSIGHT.slug}`,
      );
    }
    // The related card titles must come from INSIGHTS, not from the
    // current article.
    const otherInsights = INSIGHTS.filter((i) => i.slug !== VALID_INSIGHT.slug);
    for (const a of Array.from(anchors)) {
      const href = a.getAttribute('href');
      expect(
        otherInsights.some((i) => href === `/insights/${i.slug}`),
      ).toBe(true);
    }
  });

  it('renders the back-link to /insights', () => {
    renderAt(`/insights/${VALID_INSIGHT.slug}`);
    const backLink = screen.getByTestId('back-to-insights');
    expect(backLink.getAttribute('href')).toBe('/insights');
  });

  it('renders the closing CTAStrip linking to /book', () => {
    renderAt(`/insights/${VALID_INSIGHT.slug}`);
    expect(
      screen.getByRole('heading', { level: 2, name: /Like this\?/i }),
    ).toBeInTheDocument();
    const bookLinks = screen.getAllByRole('link', { name: /Book a call/i });
    expect(
      bookLinks.some((link) => link.getAttribute('href') === '/book'),
    ).toBe(true);
  });

  it('renders a 404-style fallback when the slug does not match', () => {
    renderAt('/insights/this-article-does-not-exist');
    expect(
      screen.getByRole('heading', { level: 1, name: /Article not found/i }),
    ).toBeInTheDocument();
    const backLinks = screen.getAllByRole('link', {
      name: /Back to field notes/i,
    });
    expect(
      backLinks.some((link) => link.getAttribute('href') === '/insights'),
    ).toBe(true);
  });
});
