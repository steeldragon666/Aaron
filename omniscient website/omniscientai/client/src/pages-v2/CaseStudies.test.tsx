/**
 * Smoke tests for the v2 Case studies overview page. Introduced
 * 2026-04-23 to fix the /_v2/case-studies 404 from Nav and validate the
 * pillar-organised composition.
 *
 * Per the Home.test.tsx / Industries.test.tsx pattern, we only validate
 * the load-bearing composition bits — primitives have their own tests.
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { HelmetProvider } from 'react-helmet-async';
import CaseStudies from './CaseStudies';

function renderCaseStudies() {
  return render(
    <HelmetProvider>
      <CaseStudies />
    </HelmetProvider>,
  );
}

describe('CaseStudies page', () => {
  it('renders the hero title', () => {
    renderCaseStudies();
    expect(
      screen.getByText(/Sovereign AI in practice\./i),
    ).toBeInTheDocument();
  });

  it('renders all three Pillar 1 vertical case titles', () => {
    renderCaseStudies();
    expect(
      screen.getByRole('heading', {
        level: 3,
        name: /CORSIA compliance reporting in weeks, not months/i,
      }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', {
        level: 3,
        name: /Bankability analysis for a prime contractor shortlist/i,
      }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', {
        level: 3,
        name: /NDIS-compliant session notes at practitioner speed/i,
      }),
    ).toBeInTheDocument();
  });

  it('renders all three Pillar 2 workforce case titles', () => {
    renderCaseStudies();
    expect(
      screen.getByRole('heading', {
        level: 3,
        name: /AI-EA for a CEO of a listed industrial firm/i,
      }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', {
        level: 3,
        name: /AI Compliance Officer for an R&DTI claim/i,
      }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', {
        level: 3,
        name: /AI BDR supporting a 3-person founding team/i,
      }),
    ).toBeInTheDocument();
  });

  it('renders the "THE PATTERN" InkSection', () => {
    renderCaseStudies();
    expect(screen.getByText(/THE PATTERN/i)).toBeInTheDocument();
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: /What's common across every engagement\./i,
      }),
    ).toBeInTheDocument();
  });

  it('renders the final CTA linking to /book', () => {
    renderCaseStudies();
    const bookLinks = screen.getAllByRole('link', { name: /Book a call/i });
    expect(bookLinks.length).toBeGreaterThan(0);
    expect(
      bookLinks.some((link) => link.getAttribute('href') === '/book'),
    ).toBe(true);
  });

  it('links each case to its matching /services/{slug} page', () => {
    renderCaseStudies();
    const readLinks = screen.getAllByRole('link', {
      name: /Read the case study/i,
    });
    const hrefs = readLinks.map((link) => link.getAttribute('href'));
    // Pillar 1 vertical cases resolve to their pillar SERVICES slugs.
    expect(hrefs).toContain('/services/bioenergy');
    expect(hrefs).toContain('/services/defence');
    expect(hrefs).toContain('/services/mental-health');
    // All three Pillar 2 cases currently point at /services/workforce.
    expect(
      hrefs.filter((href) => href === '/services/workforce').length,
    ).toBeGreaterThanOrEqual(3);
  });
});
