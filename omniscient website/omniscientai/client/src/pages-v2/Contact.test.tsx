/**
 * Smoke tests for the v2 Contact page. Verifies the page composes — hero,
 * ContactForm presence (via labelled fields), email mailto link, location,
 * hours badge, and social icons. ContactForm internals (validation, submit
 * flow, etc.) are covered by ContactForm.test.tsx.
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { HelmetProvider } from 'react-helmet-async';
import Contact from './Contact';

function renderContact() {
  return render(
    <HelmetProvider>
      <Contact />
    </HelmetProvider>,
  );
}

describe('Contact page', () => {
  it('renders hero title', () => {
    renderContact();
    expect(
      screen.getByRole('heading', { level: 1, name: /Let's talk\./i }),
    ).toBeInTheDocument();
  });

  it('renders the ContactForm (labelled fields present)', () => {
    renderContact();
    // ContactForm renders labelled Name/Email/Message inputs — asserting
    // those land proves the form is mounted.
    expect(screen.getByLabelText(/Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Message/i)).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /Send message/i }),
    ).toBeInTheDocument();
  });

  it('renders the hello@omniscientai.io mailto link', () => {
    renderContact();
    const emailLinks = screen.getAllByRole('link', {
      name: /hello@omniscientai\.io/i,
    });
    // Mailto must be present at least once (sidebar; footer also includes
    // the same address, which is expected).
    expect(
      emailLinks.some(
        (link) => link.getAttribute('href') === 'mailto:hello@omniscientai.io',
      ),
    ).toBe(true);
  });

  it('renders location (Melbourne) and hours badge', () => {
    renderContact();
    // Melbourne also appears in the footer tagline area, so just assert
    // it shows up on screen — content smoke test.
    expect(screen.getAllByText(/Melbourne, Australia/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/Mon–Fri, 9am–5pm AEST/i)).toBeInTheDocument();
  });

  it('renders LinkedIn and Twitter social links in the sidebar', () => {
    renderContact();
    // Both socials render in the footer too — `getAllByLabelText` handles
    // the duplicate gracefully.
    const linkedinLinks = screen.getAllByLabelText('LinkedIn');
    const twitterLinks = screen.getAllByLabelText('Twitter (X)');
    expect(linkedinLinks.length).toBeGreaterThan(0);
    expect(twitterLinks.length).toBeGreaterThan(0);
  });
});
