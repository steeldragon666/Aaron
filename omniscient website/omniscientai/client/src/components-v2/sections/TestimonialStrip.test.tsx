import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { TestimonialStrip } from './TestimonialStrip';

const SAMPLE_TESTIMONIALS = [
  {
    quote:
      "They moved faster than any consultancy we've worked with. The agent was in production before our security review finished.",
    name: 'Priya Shah',
    role: 'COO',
    company: 'Acme Health',
  },
  {
    quote:
      'Named practitioners, short engagement, no 40-slide deck. Exactly what we needed at our size.',
    name: 'Tom Whitaker',
    role: 'Head of Operations',
    company: 'Northbridge Group',
  },
  {
    quote:
      'The eval harness alone was worth the engagement. Our team ships confidently now.',
    name: 'Mei Lin',
    role: 'Engineering Lead',
    company: 'Harbour Freight AU',
  },
];

describe('TestimonialStrip', () => {
  it('renders the section title', () => {
    render(
      <TestimonialStrip
        sectionTitle="What clients say"
        testimonials={SAMPLE_TESTIMONIALS}
      />,
    );
    expect(
      screen.getByRole('heading', { level: 2, name: /What clients say/i }),
    ).toBeInTheDocument();
  });

  it('renders all testimonial quotes', () => {
    render(<TestimonialStrip testimonials={SAMPLE_TESTIMONIALS} />);
    expect(
      screen.getByText(/moved faster than any consultancy/i),
    ).toBeInTheDocument();
    expect(screen.getByText(/Named practitioners, short engagement/i)).toBeInTheDocument();
    expect(screen.getByText(/eval harness alone was worth/i)).toBeInTheDocument();
  });

  it('renders all attributions (name, role, company)', () => {
    render(<TestimonialStrip testimonials={SAMPLE_TESTIMONIALS} />);
    expect(screen.getByText('Priya Shah')).toBeInTheDocument();
    expect(screen.getByText(/COO/)).toBeInTheDocument();
    expect(screen.getByText(/Acme Health/)).toBeInTheDocument();
    expect(screen.getByText('Tom Whitaker')).toBeInTheDocument();
    expect(screen.getByText('Mei Lin')).toBeInTheDocument();
  });

  it('renders no star-rating elements (design system rule)', () => {
    const { container } = render(
      <TestimonialStrip testimonials={SAMPLE_TESTIMONIALS} />,
    );
    // The design system forbids star ratings. Guard against accidental
    // reintroduction by asserting no common star-glyph/icon renders.
    expect(container.textContent).not.toMatch(/★/);
    expect(container.textContent).not.toMatch(/☆/);
    expect(container.querySelector('[data-lucide="star"]')).toBeNull();
    expect(container.querySelector('.lucide-star')).toBeNull();
  });

  it('renders eyebrow when provided', () => {
    render(
      <TestimonialStrip eyebrow="CLIENTS" testimonials={SAMPLE_TESTIMONIALS} />,
    );
    expect(screen.getByText('CLIENTS')).toBeInTheDocument();
  });

  it('renders paper tone by default', () => {
    const { container } = render(
      <TestimonialStrip testimonials={SAMPLE_TESTIMONIALS} />,
    );
    const sectionEl = container.querySelector('section');
    expect(sectionEl?.className).toMatch(/bg-paper\b/);
  });

  it('renders paper-2 tone when tone="paper-2"', () => {
    const { container } = render(
      <TestimonialStrip tone="paper-2" testimonials={SAMPLE_TESTIMONIALS} />,
    );
    const sectionEl = container.querySelector('section');
    expect(sectionEl?.className).toMatch(/bg-paper-2/);
  });

  it('passes through custom className', () => {
    const { container } = render(
      <TestimonialStrip
        className="custom-testimonials"
        testimonials={SAMPLE_TESTIMONIALS}
      />,
    );
    expect(container.querySelector('.custom-testimonials')).toBeTruthy();
  });
});
