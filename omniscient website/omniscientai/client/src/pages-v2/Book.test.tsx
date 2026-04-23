/**
 * Smoke tests for the v2 Book page. Verifies the page composes — hero intro,
 * BookingForm mounted, service options wired from WORKSHOPS + the fixed
 * discovery-call / custom options, and the Footer absent (the page sets
 * hideFooter on Layout because the page itself IS the conversion goal).
 *
 * BookingForm internals (validation, step navigation, submit flow) are
 * covered by BookingForm.test.tsx.
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { HelmetProvider } from 'react-helmet-async';
import Book from './Book';
import { WORKSHOPS } from '@/lib/data';

function renderBook() {
  return render(
    <HelmetProvider>
      <Book />
    </HelmetProvider>,
  );
}

describe('Book page', () => {
  it('renders hero intro (eyebrow, h1, lede)', () => {
    renderBook();
    expect(
      screen.getByRole('heading', { level: 1, name: /Let's talk\./i }),
    ).toBeInTheDocument();
    // "Book a call" appears both in the Nav (as a CTA link) and the page
    // eyebrow — getAllByText covers both instances, we just need >=1.
    expect(screen.getAllByText(/Book a call/i).length).toBeGreaterThan(0);
    expect(
      screen.getByText(/20 minutes on your setup\. No sales pitch/i),
    ).toBeInTheDocument();
  });

  it('renders the BookingForm (step 1 service selection)', () => {
    renderBook();
    // Step 1 heading inside BookingForm
    expect(
      screen.getByRole('heading', { level: 3, name: /What are you booking\?/i }),
    ).toBeInTheDocument();
    // Progress indicator confirms the wizard is mounted
    expect(screen.getByText(/Step 1 of 3/i)).toBeInTheDocument();
  });

  it('renders discovery call, every workshop, and a custom service option', () => {
    renderBook();
    // Discovery call (fixed) — labels the RadioCard
    expect(
      screen.getByLabelText(/Discovery call · 20 minutes/i),
    ).toBeInTheDocument();
    // Every workshop from lib/data.ts as an option
    for (const w of WORKSHOPS) {
      const labelPattern = new RegExp(
        `${w.title.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')} · ${w.duration.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`,
        'i',
      );
      expect(screen.getByLabelText(labelPattern)).toBeInTheDocument();
    }
    // Custom catch-all
    expect(screen.getByLabelText(/Something custom/i)).toBeInTheDocument();
  });

  it('does not render the Footer (copyright absent)', () => {
    renderBook();
    // Footer.tsx renders "© 2026 Omniscient AI. All rights reserved." — the
    // fingerprint for Footer presence. hideFooter should strip it.
    expect(
      screen.queryByText(/© 2026 Omniscient AI\. All rights reserved\./i),
    ).not.toBeInTheDocument();
    // Footer also carries the INTELLIGENCE // CONNECTIVITY // INNOVATION
    // tagline — belt-and-braces check.
    expect(
      screen.queryByText(/INTELLIGENCE \/\/ CONNECTIVITY \/\/ INNOVATION/i),
    ).not.toBeInTheDocument();
  });
});
