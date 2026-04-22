/**
 * Smoke tests for the v2 Approach page. Verifies the page composes — hero,
 * four-phase StepStack, principles grid, final CTA. Primitive internals are
 * covered by the StepStack/CTAStrip test suites.
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { HelmetProvider } from 'react-helmet-async';
import Approach from './Approach';

function renderApproach() {
  return render(
    <HelmetProvider>
      <Approach />
    </HelmetProvider>,
  );
}

describe('Approach page', () => {
  it('renders hero title', () => {
    renderApproach();
    expect(
      screen.getByText(/Three weeks\. One artefact\. No lock-in\./i),
    ).toBeInTheDocument();
  });

  it('renders all four phase titles', () => {
    renderApproach();
    expect(
      screen.getByRole('heading', { level: 3, name: /^Discover$/ }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: /^Design$/ }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: /^Deliver$/ }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: /^Embed$/ }),
    ).toBeInTheDocument();
  });

  it('renders phase duration badges (Week 1, Weeks 3-6, Ongoing)', () => {
    renderApproach();
    expect(screen.getByText(/Week 1/i)).toBeInTheDocument();
    expect(screen.getByText(/Weeks 3-6/i)).toBeInTheDocument();
    expect(screen.getByText(/Ongoing/i)).toBeInTheDocument();
  });

  it('renders at least three principles', () => {
    renderApproach();
    expect(
      screen.getByRole('heading', { level: 3, name: /No junior bait-and-switch/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: /Ship small, ship often/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: /Vendor-neutral recommendations/i }),
    ).toBeInTheDocument();
  });

  it('renders the final CTA link to /book', () => {
    renderApproach();
    const bookLinks = screen.getAllByRole('link', { name: /Book a call/i });
    expect(bookLinks.length).toBeGreaterThan(0);
    expect(
      bookLinks.some((link) => link.getAttribute('href') === '/book'),
    ).toBe(true);
  });
});
