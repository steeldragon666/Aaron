/**
 * Smoke tests for the v2 Workshops overview page. Asserts the page
 * composes and the load-bearing bits land — hero, all workshops from
 * lib/data.ts, custom-workshop CTA card with correct slug, testimonials,
 * and final primary CTA.
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { HelmetProvider } from 'react-helmet-async';
import Workshops from './Workshops';
import { WORKSHOPS } from '@/lib/data';

function renderWorkshops() {
  return render(
    <HelmetProvider>
      <Workshops />
    </HelmetProvider>,
  );
}

describe('Workshops page', () => {
  it('renders hero title', () => {
    renderWorkshops();
    expect(
      screen.getByText(/Hands-on\. Vendor-neutral\. Built around your stack\./i),
    ).toBeInTheDocument();
  });

  it('renders all workshops from lib/data.ts', () => {
    renderWorkshops();
    for (const workshop of WORKSHOPS) {
      expect(screen.getByText(workshop.title)).toBeInTheDocument();
    }
  });

  it('renders a Book CTA linking to /workshops/{slug} for every workshop', () => {
    renderWorkshops();
    const links = screen.getAllByRole('link', { name: /Book this workshop/i });
    expect(links).toHaveLength(WORKSHOPS.length);
    for (const workshop of WORKSHOPS) {
      expect(
        links.some(
          (link) => link.getAttribute('href') === `/workshops/${workshop.slug}`,
        ),
      ).toBe(true);
    }
  });

  it('renders the custom-workshop CTA card linking to /workshops/custom', () => {
    renderWorkshops();
    expect(
      screen.getByRole('heading', { level: 2, name: /Need something different\?/i }),
    ).toBeInTheDocument();
    const customLink = screen.getByRole('link', {
      name: /Scope a custom workshop/i,
    });
    expect(customLink.getAttribute('href')).toBe('/workshops/custom');
  });

  it('renders the testimonial strip', () => {
    renderWorkshops();
    expect(
      screen.getByRole('heading', { level: 2, name: /After the workshop/i }),
    ).toBeInTheDocument();
    // All three testimonial attributions land on screen
    expect(screen.getByText(/James K\./i)).toBeInTheDocument();
    expect(screen.getByText(/Sarah M\./i)).toBeInTheDocument();
    expect(screen.getByText(/Priya R\./i)).toBeInTheDocument();
  });

  it('renders the final CTA link to /book', () => {
    renderWorkshops();
    const bookLinks = screen.getAllByRole('link', { name: /Book a workshop/i });
    expect(bookLinks.length).toBeGreaterThan(0);
    expect(
      bookLinks.some((link) => link.getAttribute('href') === '/book'),
    ).toBe(true);
  });
});
