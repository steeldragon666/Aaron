import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { CTAStrip } from './CTAStrip';

describe('CTAStrip', () => {
  it('renders the title', () => {
    render(
      <CTAStrip
        title="Ready to ship something real?"
        primaryCta={{ label: 'Book a call', href: '/book' }}
      />,
    );
    expect(
      screen.getByRole('heading', { level: 2, name: /Ready to ship/i }),
    ).toBeInTheDocument();
  });

  it('renders the primary CTA with arrow and correct href', () => {
    render(
      <CTAStrip
        title="Ready to ship something real?"
        primaryCta={{ label: 'Book a call', href: '/book' }}
      />,
    );
    const link = screen.getByRole('link', { name: /Book a call/i });
    expect(link).toBeInTheDocument();
    expect(link.getAttribute('href')).toBe('/book');
    // The arrow glyph is rendered as `→` inside an aria-hidden span.
    expect(link.textContent).toMatch(/→/);
  });

  it('renders the secondary CTA when provided', () => {
    render(
      <CTAStrip
        title="Ready?"
        primaryCta={{ label: 'Book a call', href: '/book' }}
        secondaryCta={{ label: 'See our work', href: '/work' }}
      />,
    );
    const link = screen.getByRole('link', { name: /See our work/i });
    expect(link).toBeInTheDocument();
    expect(link.getAttribute('href')).toBe('/work');
  });

  it('does not render secondary CTA when absent', () => {
    render(
      <CTAStrip
        title="Ready?"
        primaryCta={{ label: 'Book a call', href: '/book' }}
      />,
    );
    // Only the primary link should be present.
    expect(screen.getAllByRole('link')).toHaveLength(1);
  });

  it('renders paper tone by default (no ink-section class)', () => {
    const { container } = render(
      <CTAStrip
        title="Ready?"
        primaryCta={{ label: 'Book a call', href: '/book' }}
      />,
    );
    const sectionEl = container.querySelector('section');
    expect(sectionEl?.className).not.toMatch(/ink-section/);
    expect(sectionEl?.className).toMatch(/bg-paper\b/);
  });

  it('renders ink tone via InkSection when tone="ink"', () => {
    const { container } = render(
      <CTAStrip
        tone="ink"
        title="Ready?"
        primaryCta={{ label: 'Book a call', href: '/book' }}
      />,
    );
    const sectionEl = container.querySelector('section');
    expect(sectionEl?.className).toMatch(/ink-section/);
  });

  it('renders eyebrow and lede when provided', () => {
    render(
      <CTAStrip
        eyebrow="LET'S TALK"
        title="Ready to ship?"
        lede="Short engagements, named practitioners, no slide decks."
        primaryCta={{ label: 'Book a call', href: '/book' }}
      />,
    );
    expect(screen.getByText("LET'S TALK")).toBeInTheDocument();
    expect(screen.getByText(/Short engagements/i)).toBeInTheDocument();
  });

  it('passes through custom className', () => {
    const { container } = render(
      <CTAStrip
        className="custom-cta"
        title="Ready?"
        primaryCta={{ label: 'Book a call', href: '/book' }}
      />,
    );
    expect(container.querySelector('.custom-cta')).toBeTruthy();
  });
});
