/**
 * Smoke tests for the v2 About page. Same pattern as Home/Services/Industries
 * — assert the page composes and the load-bearing copy lands on screen. We
 * don't re-validate section primitives (they have their own tests).
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { HelmetProvider } from 'react-helmet-async';
import About from './About';

function renderAbout() {
  return render(
    <HelmetProvider>
      <About />
    </HelmetProvider>,
  );
}

describe('About page', () => {
  it('renders hero title', () => {
    renderAbout();
    expect(
      screen.getByText(/A boutique, built for the real world\./i),
    ).toBeInTheDocument();
  });

  it('renders the "Why we exist" story heading', () => {
    renderAbout();
    expect(
      screen.getByRole('heading', { level: 2, name: /Why we exist/i }),
    ).toBeInTheDocument();
  });

  it('renders all four value headings', () => {
    renderAbout();
    expect(
      screen.getByRole('heading', { level: 3, name: /Vendor-neutral/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: /Named practitioners/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: /Ship artefacts/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: /Short engagements/i }),
    ).toBeInTheDocument();
  });

  it('renders at least one placeholder practitioner bio', () => {
    renderAbout();
    // Placeholder bios all start with "Placeholder bio" — assert at least
    // one renders so the practitioners section is present. Real bios will
    // replace these before launch.
    const placeholders = screen.getAllByText(/Placeholder bio/i);
    expect(placeholders.length).toBeGreaterThan(0);
  });

  it('renders the "Small team. Big shoulders." InkSection heading', () => {
    renderAbout();
    expect(
      screen.getByRole('heading', { level: 2, name: /Small team\. Big shoulders\./i }),
    ).toBeInTheDocument();
  });

  it('renders the final CTA link to /contact', () => {
    renderAbout();
    const ctaLinks = screen.getAllByRole('link', { name: /Get in touch/i });
    expect(ctaLinks.length).toBeGreaterThan(0);
    expect(
      ctaLinks.some((link) => link.getAttribute('href') === '/contact'),
    ).toBe(true);
  });
});
