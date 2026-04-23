/**
 * Smoke tests for the v2 Services overview page.
 *
 * Updated 2026-04-22 for the sovereign applied AI positioning pivot. The
 * page now surfaces three pillars (vertical SaaS, Workforce, Companion)
 * with consulting/workshops retained as a de-emphasised tail section.
 *
 * Per the pattern established in Home.test.tsx, we don't re-validate
 * primitives here — only the load-bearing composition bits.
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
      screen.getByText(
        /Products, platforms, and agents — operated as managed services\./i,
      ),
    ).toBeInTheDocument();
  });

  it('renders all three vertical SaaS products', () => {
    renderServices();
    const bioenergy = SERVICES.find((s) => s.slug === 'bioenergy');
    const defence = SERVICES.find((s) => s.slug === 'defence');
    const mentalHealth = SERVICES.find((s) => s.slug === 'mental-health');
    expect(bioenergy).toBeDefined();
    expect(defence).toBeDefined();
    expect(mentalHealth).toBeDefined();
    expect(screen.getByText(bioenergy!.title)).toBeInTheDocument();
    expect(screen.getByText(defence!.title)).toBeInTheDocument();
    expect(screen.getByText(mentalHealth!.title)).toBeInTheDocument();
  });

  it('links each vertical SaaS product to /services/{slug}', () => {
    renderServices();
    const links = screen.getAllByRole('link', { name: /Learn more/i });
    for (const slug of ['bioenergy', 'defence', 'mental-health']) {
      expect(
        links.some((link) => link.getAttribute('href') === `/services/${slug}`),
      ).toBe(true);
    }
  });

  it('renders the Workforce pillar with persona cards', () => {
    renderServices();
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: /The Omniscient Workforce\./i,
      }),
    ).toBeInTheDocument();
    // Spot-check that the personas render as h3 cards.
    expect(screen.getByRole('heading', { level: 3, name: /AI-EA/i }))
      .toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: /AI Compliance Officer/i }),
    ).toBeInTheDocument();
  });

  it('renders the Companion pillar with a link to /services/companion', () => {
    renderServices();
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: /The Companion\..*pocket/i,
      }),
    ).toBeInTheDocument();
    const omniLinks = screen.getAllByRole('link', {
      name: /Learn more about Omni/i,
    });
    expect(
      omniLinks.some(
        (link) => link.getAttribute('href') === '/services/companion',
      ),
    ).toBe(true);
  });

  it('renders the de-emphasised consulting/workshops tail section', () => {
    renderServices();
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: /Consulting \+ workshops, when you need them\./i,
      }),
    ).toBeInTheDocument();
    // Legacy consulting services still need to be linkable from here.
    const legacy = SERVICES.find((s) => s.slug === 'ai-strategy-consulting');
    expect(legacy).toBeDefined();
    expect(screen.getByText(legacy!.title)).toBeInTheDocument();
    // Workshops link still present.
    const workshopLinks = screen.getAllByRole('link', {
      name: /See the workshops/i,
    });
    expect(
      workshopLinks.some((link) => link.getAttribute('href') === '/workshops'),
    ).toBe(true);
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
