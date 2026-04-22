/**
 * Smoke tests for the v2 IndustryDetail page. Exercises the dynamic-slug
 * route with an in-memory location at /industries/{slug}. Asserts
 * composition — hero "AI for X" title, use-case cards, featured case,
 * workshop grid, final CTA — plus the 404-style fallback.
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { HelmetProvider } from 'react-helmet-async';
import { Route, Router, Switch } from 'wouter';
import { memoryLocation } from 'wouter/memory-location';
import IndustryDetail from './IndustryDetail';
import { INDUSTRIES, WORKSHOPS } from '@/lib/data';

function renderAt(path: string) {
  const { hook } = memoryLocation({ path, static: true });
  return render(
    <HelmetProvider>
      <Router hook={hook}>
        <Switch>
          <Route path="/industries/:slug" component={IndustryDetail} />
          <Route component={IndustryDetail} />
        </Switch>
      </Router>
    </HelmetProvider>,
  );
}

const VALID_INDUSTRY = INDUSTRIES.find((i) => i.slug === 'healthcare')!;

describe('IndustryDetail page', () => {
  it('renders the "AI for {industry}" title as h1 when the slug is valid', () => {
    renderAt(`/industries/${VALID_INDUSTRY.slug}`);
    expect(
      screen.getByRole('heading', {
        level: 1,
        name: `AI for ${VALID_INDUSTRY.title}.`,
      }),
    ).toBeInTheDocument();
  });

  it('renders use-case cards derived from industry.useCases', () => {
    renderAt(`/industries/${VALID_INDUSTRY.slug}`);
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: /Where AI earns its keep/i,
      }),
    ).toBeInTheDocument();
    // Every use case from the data shows up on screen.
    for (const useCase of VALID_INDUSTRY.useCases.slice(0, 6)) {
      expect(screen.getByText(useCase)).toBeInTheDocument();
    }
  });

  it('renders a featured case with the "Read the case study" link', () => {
    renderAt(`/industries/${VALID_INDUSTRY.slug}`);
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: /What it looks like on the ground/i,
      }),
    ).toBeInTheDocument();
    const caseLink = screen.getByRole('link', {
      name: /Read the case study/i,
    });
    expect(caseLink).toBeInTheDocument();
    expect(caseLink.getAttribute('href')).toBeTruthy();
  });

  it('renders the WorkshopCardGrid with all flagship workshops', () => {
    renderAt(`/industries/${VALID_INDUSTRY.slug}`);
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: /Workshops relevant to your industry/i,
      }),
    ).toBeInTheDocument();
    // Each workshop title appears on screen (WorkshopCardGrid uses the
    // adapter defined in the page).
    for (const workshop of WORKSHOPS) {
      expect(screen.getByText(workshop.title)).toBeInTheDocument();
    }
  });

  it('renders the final CTA link to /contact', () => {
    renderAt(`/industries/${VALID_INDUSTRY.slug}`);
    const ctaLinks = screen.getAllByRole('link', { name: /Talk to us/i });
    expect(ctaLinks.length).toBeGreaterThan(0);
    expect(
      ctaLinks.some((link) => link.getAttribute('href') === '/contact'),
    ).toBe(true);
  });

  it('renders the back-link to /industries', () => {
    renderAt(`/industries/${VALID_INDUSTRY.slug}`);
    const backLink = screen.getByTestId('back-to-industries');
    expect(backLink.getAttribute('href')).toBe('/industries');
  });

  it('renders a 404-style fallback when the slug does not match', () => {
    renderAt('/industries/this-industry-does-not-exist');
    expect(
      screen.getByRole('heading', { level: 1, name: /Industry not found/i }),
    ).toBeInTheDocument();
    const backLinks = screen.getAllByRole('link', { name: /Back to industries/i });
    expect(
      backLinks.some((link) => link.getAttribute('href') === '/industries'),
    ).toBe(true);
  });
});
