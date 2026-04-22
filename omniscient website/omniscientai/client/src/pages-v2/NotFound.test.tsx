/**
 * Smoke tests for the v2 NotFound page. Verifies the page composes — 404
 * display, "Page not found" eyebrow, and the two CTAs pointing at / and
 * /workshops.
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { HelmetProvider } from 'react-helmet-async';
import NotFound from './NotFound';

function renderPage() {
  return render(
    <HelmetProvider>
      <NotFound />
    </HelmetProvider>,
  );
}

describe('NotFound page', () => {
  it('renders the 404 text', () => {
    renderPage();
    expect(screen.getByText(/^404$/)).toBeInTheDocument();
  });

  it('renders the "Page not found" eyebrow', () => {
    renderPage();
    expect(screen.getByText(/Page not found/i)).toBeInTheDocument();
  });

  it('renders a "Back to home" link pointing at /', () => {
    renderPage();
    const link = screen.getByRole('link', { name: /Back to home/i });
    expect(link.getAttribute('href')).toBe('/');
  });

  it('renders a "Browse workshops" link pointing at /workshops', () => {
    renderPage();
    const link = screen.getByRole('link', { name: /Browse workshops/i });
    expect(link.getAttribute('href')).toBe('/workshops');
  });
});
