/**
 * Smoke tests for the v2 CustomWorkshop page. Verifies the page composes —
 * hero, requirements form (all required fields present), StepStack "How we
 * scope" with four phases, and the closing CTAStrip that routes to /contact.
 *
 * Form submit internals (client validation, loading state, success swap) are
 * left out — the primitive-level Input/Select/Textarea suites cover the
 * field primitives, and the page's submit handler is a stub.
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { HelmetProvider } from 'react-helmet-async';
import CustomWorkshop from './CustomWorkshop';

function renderPage() {
  return render(
    <HelmetProvider>
      <CustomWorkshop />
    </HelmetProvider>,
  );
}

describe('CustomWorkshop page', () => {
  it('renders hero title', () => {
    renderPage();
    expect(
      screen.getByRole('heading', {
        level: 1,
        name: /Built from your actual workflow\./i,
      }),
    ).toBeInTheDocument();
  });

  it('renders all required form fields (org size, industry, goals, format, budget, name, email)', () => {
    renderPage();
    // Selects + Inputs — labelled with their prop-level label strings.
    expect(screen.getByLabelText(/Org size/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Industry/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Goals/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Preferred format/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Budget range/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
    // Submit button
    expect(
      screen.getByRole('button', { name: /Request scope call/i }),
    ).toBeInTheDocument();
  });

  it('renders StepStack with four scoping phases', () => {
    renderPage();
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: /Four steps from question to scope/i,
      }),
    ).toBeInTheDocument();
    // Each of the four phase titles lands as an h3.
    expect(
      screen.getByRole('heading', { level: 3, name: /Intake call/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: /Workflow audit/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: /^Scope doc$/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: /^Decision$/i }),
    ).toBeInTheDocument();
  });

  it('renders the CTAStrip linking to /contact', () => {
    renderPage();
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: /Questions before the form\?/i,
      }),
    ).toBeInTheDocument();
    const bookLinks = screen.getAllByRole('link', { name: /Book a call/i });
    expect(
      bookLinks.some((link) => link.getAttribute('href') === '/contact'),
    ).toBe(true);
  });
});
