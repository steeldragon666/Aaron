/**
 * Smoke tests for the v2 Industries overview page. Same pattern as
 * Home.test.tsx / Services.test.tsx — assert the page composes correctly
 * and the load-bearing copy/data lands on screen.
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { HelmetProvider } from 'react-helmet-async';
import Industries from './Industries';
import { INDUSTRIES } from '@/lib/data';

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
      screen.getByText(/AI that knows the floor it's walking on/i),
    ).toBeInTheDocument();
  });

  it('renders all industries from lib/data.ts as h3 headings', () => {
    renderIndustries();
    // Industry titles also appear as eyebrows on cases below, so we match
    // the heading role specifically — that's the card h3 for the industry.
    for (const industry of INDUSTRIES) {
      expect(
        screen.getByRole('heading', { level: 3, name: industry.title }),
      ).toBeInTheDocument();
    }
  });

  it('links each industry to /industries/{slug}', () => {
    renderIndustries();
    const links = screen.getAllByRole('link', { name: /See how we work here/i });
    expect(links).toHaveLength(INDUSTRIES.length);
    for (const industry of INDUSTRIES) {
      expect(
        links.some(
          (link) => link.getAttribute('href') === `/industries/${industry.slug}`,
        ),
      ).toBe(true);
    }
  });

  it('renders the case grid', () => {
    renderIndustries();
    expect(
      screen.getByRole('heading', { level: 2, name: /What it looks like on the ground/i }),
    ).toBeInTheDocument();
    const caseLinks = screen.getAllByRole('link', { name: /Read the case study/i });
    expect(caseLinks.length).toBeGreaterThanOrEqual(3);
  });

  it('renders the final CTA link to /contact', () => {
    renderIndustries();
    const ctaLinks = screen.getAllByRole('link', { name: /Talk to us/i });
    expect(ctaLinks.length).toBeGreaterThan(0);
    expect(
      ctaLinks.some((link) => link.getAttribute('href') === '/contact'),
    ).toBe(true);
  });
});
