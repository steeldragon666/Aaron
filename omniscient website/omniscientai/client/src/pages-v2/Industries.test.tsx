/**
 * Smoke tests for the v2 Industries overview page. Strategic pivot
 * (2026-04-22): verifies the page is composed around three Pillar 1
 * verticals (bioenergy, defence, mental health) rather than a generic
 * INDUSTRIES catalog, and that each card links to its /services/:slug
 * detail page.
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { HelmetProvider } from 'react-helmet-async';
import Industries from './Industries';

function renderIndustries() {
  return render(
    <HelmetProvider>
      <Industries />
    </HelmetProvider>,
  );
}

describe('Industries page', () => {
  it('renders hero title', () => {
    renderIndustries();
    expect(
      screen.getByText(/Three verticals we go deep in\./i),
    ).toBeInTheDocument();
  });

  it('renders all three vertical titles as h3 headings', () => {
    renderIndustries();
    expect(
      screen.getByRole('heading', {
        level: 3,
        name: /Bioenergy & agribusiness/i,
      }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', {
        level: 3,
        name: /Sovereign defence & industrial supply chain/i,
      }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', {
        level: 3,
        name: /Mental health & NDIS-funded care/i,
      }),
    ).toBeInTheDocument();
  });

  it('links each vertical card to its /services/{slug} detail page', () => {
    renderIndustries();
    const learnMoreLinks = screen.getAllByRole('link', { name: /Learn more/i });
    const hrefs = learnMoreLinks.map((link) => link.getAttribute('href'));
    expect(hrefs).toContain('/services/bioenergy');
    expect(hrefs).toContain('/services/defence');
    expect(hrefs).toContain('/services/mental-health');
  });

  it('renders the "NOT YOUR INDUSTRY?" off-ramp section', () => {
    renderIndustries();
    expect(screen.getByText(/NOT YOUR INDUSTRY\?/i)).toBeInTheDocument();
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: /The Workforce and the Companion work everywhere/i,
      }),
    ).toBeInTheDocument();
    const seeAllLink = screen.getByRole('link', { name: /See all services/i });
    expect(seeAllLink.getAttribute('href')).toBe('/services');
  });

  it('renders the final CTA link to /book', () => {
    renderIndustries();
    const bookLinks = screen.getAllByRole('link', { name: /Book a call/i });
    expect(bookLinks.length).toBeGreaterThan(0);
    expect(
      bookLinks.some((link) => link.getAttribute('href') === '/book'),
    ).toBe(true);
  });
});
