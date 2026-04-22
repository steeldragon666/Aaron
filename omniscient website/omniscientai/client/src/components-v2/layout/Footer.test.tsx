import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Footer } from './Footer';

describe('Footer', () => {
  it('renders company wordmark', () => {
    render(<Footer />);
    expect(screen.getByText('Omniscient AI')).toBeInTheDocument();
  });

  it('renders company tagline', () => {
    render(<Footer />);
    expect(screen.getByText(/Vendor-neutral AI training/i)).toBeInTheDocument();
  });

  it('renders primary nav links', () => {
    render(<Footer />);
    expect(screen.getByRole('link', { name: /Workshops/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Services/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /About/i })).toBeInTheDocument();
  });

  it('renders legal links', () => {
    render(<Footer />);
    expect(screen.getByRole('link', { name: /Privacy/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Terms/i })).toBeInTheDocument();
  });

  it('renders contact email as mailto', () => {
    render(<Footer />);
    const email = screen.getByRole('link', { name: /hello@omniscientai.io/i });
    expect(email.getAttribute('href')).toBe('mailto:hello@omniscientai.io');
  });

  it('renders social icons with aria-labels', () => {
    render(<Footer />);
    expect(screen.getByRole('link', { name: /LinkedIn/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Twitter|X \(/i })).toBeInTheDocument();
  });

  it('renders copyright notice', () => {
    render(<Footer />);
    expect(screen.getByText(/© 2026 Omniscient AI/i)).toBeInTheDocument();
  });

  it('renders brand tagline in eyebrow style', () => {
    render(<Footer />);
    expect(screen.getByText(/INTELLIGENCE.*CONNECTIVITY.*INNOVATION/)).toBeInTheDocument();
  });
});
