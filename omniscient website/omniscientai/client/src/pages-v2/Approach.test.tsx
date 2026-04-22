/**
 * Smoke tests for the v2 Approach page. Strategic pivot (2026-04-22):
 * verifies the page reflects the product + managed-service model
 * ("We build. We operate. You use.") with the new four-phase cycle
 * (Scope / Prototype / Operate / Expand) and the sovereign + managed-
 * service principles. Primitive internals are covered by the StepStack
 * and CTAStrip test suites.
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
      screen.getByText(/We build\. We operate\. You use\./i),
    ).toBeInTheDocument();
  });

  it('renders all four phase titles', () => {
    renderApproach();
    expect(
      screen.getByRole('heading', { level: 3, name: /^Scope$/ }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: /^Prototype$/ }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: /^Operate$/ }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: /^Expand$/ }),
    ).toBeInTheDocument();
  });

  it('renders phase duration badges', () => {
    renderApproach();
    expect(screen.getByText(/Week 0/i)).toBeInTheDocument();
    expect(screen.getByText(/Weeks 1-2/i)).toBeInTheDocument();
    expect(screen.getByText(/^Ongoing$/i)).toBeInTheDocument();
    expect(screen.getByText(/When it makes sense/i)).toBeInTheDocument();
  });

  it('renders at least three principles reflecting sovereign + managed-service positioning', () => {
    renderApproach();
    expect(
      screen.getByRole('heading', { level: 3, name: /Australian sovereign infra/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: /We operate what we build/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: /No kickbacks, ever/i }),
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
