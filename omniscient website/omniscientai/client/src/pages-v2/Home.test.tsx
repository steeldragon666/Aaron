/**
 * Smoke tests for the v2 Home page. We don't re-validate every section
 * primitive here (those have their own test suites) — we only assert that
 * the page composes together and the load-bearing copy lands on screen.
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
  it('renders hero title', () => {
    renderHome();
    expect(screen.getByText(/Unleashing the power of intelligent connections/i))
      .toBeInTheDocument();
  });

  it('renders all pillar titles', () => {
    renderHome();
    expect(screen.getByText('AI training')).toBeInTheDocument();
    expect(screen.getByText('Health technologies')).toBeInTheDocument();
    // "Defense" alone appears in multiple places (e.g. pillar description as
    // well as the heading). Match the full pillar title to disambiguate.
    expect(screen.getByText('Defense hardware & software')).toBeInTheDocument();
    expect(screen.getByText('Agentic ops')).toBeInTheDocument();
  });

  it('renders the vendor-neutral manifesto heading', () => {
    renderHome();
    expect(screen.getByText(/don't take kickbacks/i)).toBeInTheDocument();
  });

  it('renders workshop cards', () => {
    renderHome();
    expect(screen.getByText('AI Readiness Workshop')).toBeInTheDocument();
    expect(screen.getByText('Executive AI Briefing')).toBeInTheDocument();
    expect(screen.getByText('Custom team training')).toBeInTheDocument();
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
