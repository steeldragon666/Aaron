import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Nav } from './Nav';

describe('Nav', () => {
  it('renders the wordmark', () => {
    render(<Nav />);
    // Wordmark appears in both header and (when open) drawer. At least one is always rendered.
    expect(screen.getAllByText('Omniscient AI').length).toBeGreaterThanOrEqual(1);
  });

  it('renders desktop link items', () => {
    render(<Nav />);
    expect(screen.getByRole('link', { name: /Workshops/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Services/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Case studies/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /About/i })).toBeInTheDocument();
  });

  it('renders Book a call CTA', () => {
    render(<Nav />);
    // Use more specific query since there will also be a mobile Book CTA
    const ctas = screen.getAllByRole('link', { name: /Book a call/i });
    expect(ctas.length).toBeGreaterThanOrEqual(1);
  });

  it('hamburger menu is closed by default', () => {
    render(<Nav />);
    // Menu button should exist, but overlay should not be visible
    const menuBtn = screen.getByRole('button', { name: /open menu/i });
    expect(menuBtn).toBeInTheDocument();
    expect(menuBtn.getAttribute('aria-expanded')).toBe('false');
  });

  it('opens mobile drawer when hamburger clicked', () => {
    render(<Nav />);
    const menuBtn = screen.getByRole('button', { name: /open menu/i });
    fireEvent.click(menuBtn);
    // After click, aria-expanded should be true
    expect(menuBtn.getAttribute('aria-expanded')).toBe('true');
    // Close button should now be present
    expect(screen.getByRole('button', { name: /close menu/i })).toBeInTheDocument();
  });

  it('closes mobile drawer when close button clicked', () => {
    render(<Nav />);
    const menuBtn = screen.getByRole('button', { name: /open menu/i });
    fireEvent.click(menuBtn);
    const closeBtn = screen.getByRole('button', { name: /close menu/i });
    fireEvent.click(closeBtn);
    expect(menuBtn.getAttribute('aria-expanded')).toBe('false');
  });

  it('closes mobile drawer on Escape key', () => {
    render(<Nav />);
    fireEvent.click(screen.getByRole('button', { name: /open menu/i }));
    fireEvent.keyDown(document, { key: 'Escape' });
    // aria-expanded back to false
    const menuBtn = screen.getByRole('button', { name: /open menu/i });
    expect(menuBtn.getAttribute('aria-expanded')).toBe('false');
  });

  it('logo link points to /', () => {
    render(<Nav />);
    const logo = screen.getAllByRole('link').find(
      (l) => l.textContent?.includes('Omniscient AI'),
    );
    expect(logo?.getAttribute('href')).toBe('/');
  });
});
