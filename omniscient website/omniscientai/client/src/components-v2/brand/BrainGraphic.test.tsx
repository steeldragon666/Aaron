import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { BrainGraphic } from './BrainGraphic';

describe('BrainGraphic', () => {
  it('renders circles variant by default', () => {
    render(<BrainGraphic data-testid="bg" />);
    expect(screen.getByTestId('bg').getAttribute('src')).toBe(
      '/brand/brand-graphic-circles.png',
    );
  });

  it('renders horizontal variant', () => {
    render(<BrainGraphic variant="horizontal" data-testid="bg" />);
    expect(screen.getByTestId('bg').getAttribute('src')).toBe(
      '/brand/brand-graphic-horizontal.png',
    );
  });

  it('is decorative (aria-hidden + empty alt)', () => {
    render(<BrainGraphic data-testid="bg" />);
    const img = screen.getByTestId('bg');
    expect(img.getAttribute('aria-hidden')).toBe('true');
    expect(img.getAttribute('alt')).toBe('');
  });

  it('applies hero size classes by default', () => {
    render(<BrainGraphic data-testid="bg" />);
    expect(screen.getByTestId('bg').className).toMatch(/max-w-\[540px\]/);
  });

  it('applies section size classes', () => {
    render(<BrainGraphic size="section" data-testid="bg" />);
    expect(screen.getByTestId('bg').className).toMatch(/max-w-\[320px\]/);
  });

  it('applies corner size classes', () => {
    render(<BrainGraphic size="corner" data-testid="bg" />);
    expect(screen.getByTestId('bg').className).toMatch(/max-w-\[200px\]/);
  });

  it('passes through className', () => {
    render(<BrainGraphic className="custom" data-testid="bg" />);
    expect(screen.getByTestId('bg').className).toMatch(/custom/);
  });
});
