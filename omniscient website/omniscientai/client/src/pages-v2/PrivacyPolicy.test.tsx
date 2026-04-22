/**
 * Smoke tests for the v2 PrivacyPolicy page. Verifies the page composes —
 * hero, last-updated badge, ported legal section headings, and contact
 * mailto. ArticleBody internals and typography utility classes are covered
 * by ArticleBody.test.tsx.
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { HelmetProvider } from 'react-helmet-async';
import PrivacyPolicy from './PrivacyPolicy';

function renderPage() {
  return render(
    <HelmetProvider>
      <PrivacyPolicy />
    </HelmetProvider>,
  );
}

describe('PrivacyPolicy page', () => {
  it('renders the hero title as h1', () => {
    renderPage();
    expect(
      screen.getByRole('heading', { level: 1, name: /Privacy policy/i }),
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
      screen.getByRole('heading', { level: 2, name: /Information we collect/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: /Australian Privacy Principles/i,
      }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 2, name: /Cookies/i }),
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
