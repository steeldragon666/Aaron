/**
 * Smoke tests for the v2 Terms page. Verifies the page composes — hero,
 * last-updated badge, ported legal section headings, and contact mailto.
 * ArticleBody internals and typography utility classes are covered by
 * ArticleBody.test.tsx.
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { HelmetProvider } from 'react-helmet-async';
import Terms from './Terms';

function renderPage() {
  return render(
    <HelmetProvider>
      <Terms />
    </HelmetProvider>,
  );
}

describe('Terms page', () => {
  it('renders the hero title as h1', () => {
    renderPage();
    expect(
      screen.getByRole('heading', { level: 1, name: /Terms of service/i }),
    ).toBeInTheDocument();
  });

  it('renders the Legal eyebrow', () => {
    renderPage();
    expect(screen.getByText(/^Legal$/i)).toBeInTheDocument();
  });

  it('renders the last-updated badge', () => {
    renderPage();
    expect(screen.getByText(/Last updated: March 2026/i)).toBeInTheDocument();
  });

  it('renders key section headings ported from legacy', () => {
    renderPage();
    expect(
      screen.getByRole('heading', { level: 2, name: /^1\. Services$/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 2, name: /Cancellation policy/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 2, name: /Vendor neutrality/i }),
    ).toBeInTheDocument();
  });

  it('renders a contact mailto link', () => {
    renderPage();
    const links = screen.getAllByRole('link', {
      name: /hello@omniscientai\.com\.au/i,
    });
    expect(
      links.some(
        (link) =>
          link.getAttribute('href') === 'mailto:hello@omniscientai.com.au',
      ),
    ).toBe(true);
  });
});
