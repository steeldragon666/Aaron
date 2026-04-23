/**
 * Smoke tests for the v2 CompanionDetail page. Asserts the bespoke
 * Companion page composes together — hero, differentiators, capabilities,
 * sovereign callout, how-it-works, pricing tiers, FAQ, and final CTA.
 *
 * Uses a memory-location router so wouter <Link>s inside the page render
 * without a real browser history. HelmetProvider wraps the render so the
 * SEO component inside Layout doesn't warn.
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { HelmetProvider } from 'react-helmet-async';
import { Router } from 'wouter';
import { memoryLocation } from 'wouter/memory-location';
import CompanionDetail from './CompanionDetail';

function renderPage() {
  const { hook } = memoryLocation({ path: '/services/companion', static: true });
  return render(
    <HelmetProvider>
      <Router hook={hook}>
        <CompanionDetail />
      </Router>
    </HelmetProvider>,
  );
}

describe('CompanionDetail page', () => {
  it('renders the bespoke Omni hero title as h1', () => {
    renderPage();
    expect(
      screen.getByRole('heading', {
        level: 1,
        name: /An AI that lives in your pocket\. Not in a chat window\./i,
      }),
    ).toBeInTheDocument();
    // Hero eyebrow identifies the page as Pillar 3 / Omni.
    expect(screen.getByText(/PILLAR 3 · OMNI/i)).toBeInTheDocument();
  });

  it('renders all four differentiator titles', () => {
    renderPage();
    expect(
      screen.getByRole('heading', { level: 3, name: /Phone-native/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: /Voice-first/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: /Persistent memory/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: /Yours alone/i }),
    ).toBeInTheDocument();
  });

  it('renders the capabilities checklist with every capability line', () => {
    renderPage();
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: /Real agency, not reactive prompting\./i,
      }),
    ).toBeInTheDocument();
    // Spot-check a few concrete phone-native capabilities land.
    expect(
      screen.getByText(/Makes your calls/i),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Triages your inbox and drafts replies in your voice\./i),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Briefs you before meetings/i),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Works offline for common tasks/i),
    ).toBeInTheDocument();
  });

  it('renders the sovereign callout InkSection', () => {
    renderPage();
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: /Doesn't phone home to California\./i,
      }),
    ).toBeInTheDocument();
  });

  it('renders the how-it-works StepStack with all four phases', () => {
    renderPage();
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: /From installed to indispensable in a week\./i,
      }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: /Install/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: /Seed/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: /^Live$/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: /Evolve/i }),
    ).toBeInTheDocument();
  });

  it('renders all three pricing tiers with their prices', () => {
    renderPage();
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: /Plans that match your life\./i,
      }),
    ).toBeInTheDocument();
    // Tier names
    expect(screen.getByText('Consumer')).toBeInTheDocument();
    expect(screen.getByText('Pro')).toBeInTheDocument();
    expect(screen.getByText('Enterprise')).toBeInTheDocument();
    // Tier prices
    expect(screen.getByText('$30')).toBeInTheDocument();
    expect(screen.getByText('$80')).toBeInTheDocument();
    expect(screen.getByText(/From \$200/i)).toBeInTheDocument();
  });

  it('renders the FAQ accordion with all question triggers', () => {
    renderPage();
    expect(
      screen.getByRole('heading', { level: 2, name: /Honest answers\./i }),
    ).toBeInTheDocument();
    // Each FAQ question is a button trigger (accordion). Spot-check three.
    expect(
      screen.getByRole('button', { name: /Is my data private\?/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('button', {
        name: /How is this different from Siri \/ Google Assistant \/ Copilot\?/i,
      }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /When can I get one\?/i }),
    ).toBeInTheDocument();
  });

  it('renders the final CTA with a link to /book', () => {
    renderPage();
    expect(
      screen.getByRole('heading', { level: 2, name: /Ready to meet Omni\?/i }),
    ).toBeInTheDocument();
    const bookLinks = screen.getAllByRole('link', { name: /Book a call/i });
    expect(bookLinks.length).toBeGreaterThan(0);
    expect(
      bookLinks.some((link) => link.getAttribute('href') === '/book'),
    ).toBe(true);
  });
});
