/**
 * Smoke tests for the v2 Services overview page. Per the pattern established
 * in Home.test.tsx, we don't re-validate primitives here — only the load-
 * bearing composition bits: hero landing, every service from lib/data.ts
 * rendering with the correct slug link, pillar grid presence, and final CTA.
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { HelmetProvider } from 'react-helmet-async';
import Services from './Services';
import { SERVICES } from '@/lib/data';

function renderServices() {
  return render(
    <HelmetProvider>
      <Services />
    </HelmetProvider>,
  );
}

describe('Services page', () => {
  it('renders hero title', () => {
    renderServices();
    expect(
      screen.getByText(/Short engagements\. Named practitioners\. An artefact at the end\./i),
    ).toBeInTheDocument();
  });

  it('renders all services from lib/data.ts', () => {
    renderServices();
    for (const svc of SERVICES) {
      expect(screen.getByText(svc.title)).toBeInTheDocument();
    }
  });

  it('links each service to /services/{slug}', () => {
    renderServices();
    const links = screen.getAllByRole('link', { name: /Learn more/i });
    // At minimum there's one Learn more per service plus pillar links
    expect(links.length).toBeGreaterThanOrEqual(SERVICES.length);
    for (const svc of SERVICES) {
      expect(
        links.some((link) => link.getAttribute('href') === `/services/${svc.slug}`),
      ).toBe(true);
    }
  });

  it('renders pillar grid with four practice areas', () => {
    renderServices();
    expect(screen.getByText('AI training')).toBeInTheDocument();
    expect(screen.getByText('Health technologies')).toBeInTheDocument();
    expect(screen.getByText('Defense hardware & software')).toBeInTheDocument();
    expect(screen.getByText('Agentic ops')).toBeInTheDocument();
  });

  it('renders the approach InkSection', () => {
    renderServices();
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: /Three weeks\. One artefact\. No lock-in\./i,
      }),
    ).toBeInTheDocument();
  });

  it('renders the final CTA link to /book', () => {
    renderServices();
    const ctaLinks = screen.getAllByRole('link', {
      name: /Let's see if we're a fit/i,
    });
    expect(ctaLinks.length).toBeGreaterThan(0);
    expect(
      ctaLinks.some((link) => link.getAttribute('href') === '/book'),
    ).toBe(true);
  });
});
