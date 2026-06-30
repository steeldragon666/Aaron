import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { HeroCentric } from './HeroCentric';

describe('HeroCentric', () => {
  it('renders the title as an h1', () => {
    render(<HeroCentric title="Hello world" />);
    expect(
      screen.getByRole('heading', { level: 1, name: /Hello world/i }),
    ).toBeInTheDocument();
  });

  it('renders eyebrow when provided', () => {
    render(<HeroCentric eyebrow="About us" title="T" />);
    expect(screen.getByText('About us')).toBeInTheDocument();
  });

  it('renders lede when provided', () => {
    render(<HeroCentric title="T" lede="Subheading copy" />);
    expect(screen.getByText('Subheading copy')).toBeInTheDocument();
  });

  it('renders primary CTA with href and arrow', () => {
    render(
      <HeroCentric title="T" primaryCta={{ label: 'Meet the team', href: '/about' }} />,
    );
    const link = screen.getByRole('link', { name: /Meet the team/i });
    expect(link.getAttribute('href')).toBe('/about');
    expect(link.textContent).toContain('→');
  });

  it('renders secondary CTA without an arrow', () => {
    render(
      <HeroCentric
        title="T"
        primaryCta={{ label: 'A', href: '/a' }}
        secondaryCta={{ label: 'Learn more', href: '/more' }}
      />,
    );
    const link = screen.getByRole('link', { name: /Learn more/i });
    expect(link.getAttribute('href')).toBe('/more');
    expect(link.textContent).not.toContain('→');
  });

  it('does not render BrainGraphic by default', () => {
    const { container } = render(<HeroCentric title="T" />);
    expect(container.querySelector('img')).toBeNull();
  });

  it('renders BrainGraphic when showGraphic=true', () => {
    const { container } = render(<HeroCentric title="T" showGraphic />);
    const img = container.querySelector('img');
    expect(img).not.toBeNull();
    expect(img?.getAttribute('src')).toContain('brand-graphic-circles');
  });

  it('applies text-center to the section wrapper', () => {
    const { container } = render(<HeroCentric title="T" />);
    const section = container.querySelector('section');
    expect(section?.className).toMatch(/text-center/);
  });
});
