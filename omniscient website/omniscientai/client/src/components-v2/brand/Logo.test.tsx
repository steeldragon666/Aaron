import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Logo } from './Logo';

describe('Logo', () => {
  it('renders stacked variant by default', () => {
    render(<Logo />);
    const img = screen.getByRole('img');
    expect(img.getAttribute('src')).toBe('/brand/logo-brain-stacked.png');
  });

  it('renders horizontal variant', () => {
    render(<Logo variant="horizontal" />);
    expect(screen.getByRole('img').getAttribute('src')).toBe(
      '/brand/logo-horizontal-with-graphic.png',
    );
  });

  it('renders mark variant', () => {
    render(<Logo variant="mark" />);
    expect(screen.getByRole('img').getAttribute('src')).toBe(
      '/brand/logo-mark-circle.png',
    );
  });

  it('uses default alt text', () => {
    render(<Logo />);
    expect(screen.getByRole('img').getAttribute('alt')).toBe('Omniscient AI');
  });

  it('accepts custom alt text', () => {
    render(<Logo alt="Custom" />);
    expect(screen.getByRole('img').getAttribute('alt')).toBe('Custom');
  });

  it('accepts custom width', () => {
    render(<Logo width={300} />);
    expect(screen.getByRole('img').getAttribute('width')).toBe('300');
  });
});
