import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { HeroSplit } from './HeroSplit';

describe('HeroSplit', () => {
  it('renders the title as an h1', () => {
    render(<HeroSplit title="Hello world" />);
    expect(
      screen.getByRole('heading', { level: 1, name: /Hello world/i }),
    ).toBeInTheDocument();
  });

  it('renders eyebrow when provided', () => {
    render(<HeroSplit eyebrow="Featured" title="T" />);
    expect(screen.getByText('Featured')).toBeInTheDocument();
  });

  it('renders lede when provided', () => {
    render(<HeroSplit title="T" lede="Subheading copy" />);
    expect(screen.getByText('Subheading copy')).toBeInTheDocument();
  });

  it('renders primary CTA with href and arrow', () => {
    render(
      <HeroSplit title="T" primaryCta={{ label: 'Book a call', href: '/book' }} />,
    );
    const link = screen.getByRole('link', { name: /Book a call/i });
    expect(link.getAttribute('href')).toBe('/book');
    expect(link.textContent).toContain('→');
  });

  it('renders secondary CTA without an arrow', () => {
    render(
      <HeroSplit
        title="T"
        primaryCta={{ label: 'A', href: '/a' }}
        secondaryCta={{ label: 'See our work', href: '/work' }}
      />,
    );
    const link = screen.getByRole('link', { name: /See our work/i });
    expect(link.getAttribute('href')).toBe('/work');
    expect(link.textContent).not.toContain('→');
  });

  it('renders BrainGraphic with circles variant by default', () => {
    const { container } = render(<HeroSplit title="T" />);
    const img = container.querySelector('img');
    expect(img?.getAttribute('src')).toContain('brand-graphic-circles');
  });

  it('renders BrainGraphic with horizontal variant when graphic="horizontal"', () => {
    const { container } = render(<HeroSplit title="T" graphic="horizontal" />);
    const img = container.querySelector('img');
    expect(img?.getAttribute('src')).toContain('brand-graphic-horizontal');
  });
});
