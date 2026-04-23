/**
 * Smoke tests for the v2 Home page. We don't re-validate every section
 * primitive here (those have their own test suites) — we only assert that
 * the page composes together and the load-bearing copy lands on screen.
 *
 * Updated 2026-04-22 for the sovereign applied AI positioning pivot. The
 * page now surfaces three pillars: vertical SaaS (bioenergy, defence,
 * mental health), the Omniscient Workforce, and the Companion (Omni).
 *
 * `HelmetProvider` wraps the render so react-helmet-async inside the SEO
 * component doesn't warn. The Layout's Nav and Footer render with plain
 * anchors, so no Router context is required.
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { HelmetProvider } from 'react-helmet-async';
import Home from './Home';

function renderHome() {
  return render(
    <HelmetProvider>
      <Home />
    </HelmetProvider>,
  );
}

describe('Home page', () => {
  it('renders the sovereign applied AI hero title', () => {
    renderHome();
    expect(
      screen.getByText(/Australia's sovereign applied AI company\./i),
    ).toBeInTheDocument();
  });

  it('renders all three vertical SaaS pillar titles', () => {
    renderHome();
    expect(
      screen.getByText('Bioenergy & agribusiness intelligence'),
    ).toBeInTheDocument();
    expect(
      screen.getByText('Sovereign defence & industrial supply chain'),
    ).toBeInTheDocument();
    expect(
      screen.getByText('Mental health & NDIS-funded care'),
    ).toBeInTheDocument();
  });

  it('renders the Omniscient Workforce pillar heading', () => {
    renderHome();
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: /The Omniscient Workforce\./i,
      }),
    ).toBeInTheDocument();
  });

  it('renders the Companion / Omni pillar heading', () => {
    renderHome();
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: /The Companion\..*pocket/i,
      }),
    ).toBeInTheDocument();
  });

  it('renders at least a few workforce personas', () => {
    renderHome();
    // Spot-check three of the six personas render — the full list is
    // rendered inline in Home.tsx, so if one fails they all fail.
    expect(screen.getByRole('heading', { level: 3, name: /AI-EA/i }))
      .toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 3, name: /AI Associate/i }))
      .toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 3, name: /AI Engineer/i }))
      .toBeInTheDocument();
  });

  it('renders the de-emphasised consulting + workshops section', () => {
    renderHome();
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: /Consulting \+ workshops, when you need them\./i,
      }),
    ).toBeInTheDocument();
    // At least one link to /workshops should exist.
    const workshopLinks = screen.getAllByRole('link', {
      name: /See the workshops/i,
    });
    expect(
      workshopLinks.some((link) => link.getAttribute('href') === '/workshops'),
    ).toBe(true);
  });

  it('renders the final CTA link to /book', () => {
    renderHome();
    const bookLinks = screen.getAllByRole('link', { name: /Book a call/i });
    expect(bookLinks.length).toBeGreaterThan(0);
    // At least one of them points at /book
    expect(bookLinks.some((link) => link.getAttribute('href') === '/book'))
      .toBe(true);
  });
});
