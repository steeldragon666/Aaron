/**
 * Smoke tests for the v2 WorkshopDetail page. Exercises the dynamic-slug
 * route with an in-memory location at /workshops/{slug}. Asserts
 * composition — hero title, meta row, who-it's-for checklist, module
 * agenda, outcomes, FAQ, BookingForm presence, and final CTA — plus the
 * 404-style fallback.
 *
 * BookingForm internals (validation, multi-step nav, submit flow) are
 * covered by BookingForm.test.tsx. Here we only verify the form is
 * mounted in both the desktop sticky sidebar and the mobile fallback
 * section, and that the workshop's slug drives the radio-card label.
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { HelmetProvider } from 'react-helmet-async';
import { Route, Router, Switch } from 'wouter';
import { memoryLocation } from 'wouter/memory-location';
import WorkshopDetail from './WorkshopDetail';
import { WORKSHOPS } from '@/lib/data';

function renderAt(path: string) {
  const { hook } = memoryLocation({ path, static: true });
  return render(
    <HelmetProvider>
      <Router hook={hook}>
        <Switch>
          <Route path="/workshops/:slug" component={WorkshopDetail} />
          <Route component={WorkshopDetail} />
        </Switch>
      </Router>
    </HelmetProvider>,
  );
}

const VALID_WORKSHOP = WORKSHOPS[0]; // 'ai-for-business-leaders'

describe('WorkshopDetail page', () => {
  it('renders the workshop title as the hero h1 when the slug is valid', () => {
    renderAt(`/workshops/${VALID_WORKSHOP.slug}`);
    expect(
      screen.getByRole('heading', { level: 1, name: VALID_WORKSHOP.title }),
    ).toBeInTheDocument();
  });

  it('renders the meta row with duration, format, and price', () => {
    renderAt(`/workshops/${VALID_WORKSHOP.slug}`);
    const metaRow = screen.getByTestId('workshop-meta-row');
    expect(metaRow).toBeInTheDocument();
    expect(metaRow.textContent).toContain(VALID_WORKSHOP.duration);
    expect(metaRow.textContent).toContain(VALID_WORKSHOP.format);
    expect(metaRow.textContent).toContain(VALID_WORKSHOP.priceRange);
  });

  it("renders the 'Who it's for' checklist with every whoIsItFor item", () => {
    renderAt(`/workshops/${VALID_WORKSHOP.slug}`);
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: /Built for teams who've tried the slide-deck version/i,
      }),
    ).toBeInTheDocument();
    for (const item of VALID_WORKSHOP.whoIsItFor) {
      expect(screen.getByText(item)).toBeInTheDocument();
    }
  });

  it('renders the module agenda (StepStack) with every module', () => {
    renderAt(`/workshops/${VALID_WORKSHOP.slug}`);
    expect(
      screen.getByRole('heading', { level: 2, name: /What you'll cover/i }),
    ).toBeInTheDocument();
    for (const module of VALID_WORKSHOP.modules) {
      expect(
        screen.getByRole('heading', { level: 3, name: module.title }),
      ).toBeInTheDocument();
    }
  });

  it('renders the outcomes grid with every outcome', () => {
    renderAt(`/workshops/${VALID_WORKSHOP.slug}`);
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: /What you'll walk away with/i,
      }),
    ).toBeInTheDocument();
    for (const outcome of VALID_WORKSHOP.outcomes) {
      expect(screen.getByText(outcome)).toBeInTheDocument();
    }
  });

  it('renders the FAQAccordion with every workshop FAQ', () => {
    renderAt(`/workshops/${VALID_WORKSHOP.slug}`);
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: /The questions we hear most/i,
      }),
    ).toBeInTheDocument();
    // Each FAQ question renders as a button label.
    for (const faq of VALID_WORKSHOP.faqs) {
      expect(
        screen.getByRole('button', { name: new RegExp(faq.q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i') }),
      ).toBeInTheDocument();
    }
  });

  it('renders the BookingForm in both the sticky sidebar and mobile section', () => {
    renderAt(`/workshops/${VALID_WORKSHOP.slug}`);
    // Sticky sidebar present
    const sidebar = screen.getByTestId('sticky-booking-sidebar');
    expect(sidebar).toBeInTheDocument();
    // Mobile booking section present
    const mobile = screen.getByTestId('mobile-booking-form');
    expect(mobile).toBeInTheDocument();
    // Both mount a BookingForm — step 1 heading should land twice
    const stepHeadings = screen.getAllByText(/What are you booking\?/i);
    expect(stepHeadings.length).toBe(2);
    // Workshop title appears as a radio-card label in each BookingForm
    const workshopRadios = screen.getAllByLabelText(
      new RegExp(VALID_WORKSHOP.title, 'i'),
    );
    expect(workshopRadios.length).toBeGreaterThanOrEqual(1);
  });

  it('renders the back-link to /workshops', () => {
    renderAt(`/workshops/${VALID_WORKSHOP.slug}`);
    const backLink = screen.getByTestId('back-to-workshops');
    expect(backLink.getAttribute('href')).toBe('/workshops');
  });

  it("renders the primary 'Book this workshop' CTA with the slug in the href", () => {
    renderAt(`/workshops/${VALID_WORKSHOP.slug}`);
    const bookCtas = screen.getAllByRole('link', {
      name: /Book this workshop/i,
    });
    expect(
      bookCtas.some(
        (link) =>
          link.getAttribute('href') ===
          `/book?workshop=${VALID_WORKSHOP.slug}`,
      ),
    ).toBe(true);
  });

  it('renders a 404-style fallback when the slug does not match', () => {
    renderAt('/workshops/this-workshop-does-not-exist');
    expect(
      screen.getByRole('heading', { level: 1, name: /Workshop not found/i }),
    ).toBeInTheDocument();
    const backLinks = screen.getAllByRole('link', { name: /Back to workshops/i });
    expect(
      backLinks.some((link) => link.getAttribute('href') === '/workshops'),
    ).toBe(true);
  });
});
