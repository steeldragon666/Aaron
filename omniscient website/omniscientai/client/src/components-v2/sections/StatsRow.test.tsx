import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { StatsRow } from './StatsRow';

const SAMPLE_STATS = [
  { value: '50+', label: 'Workshops delivered' },
  { value: '12', label: 'Industries' },
  { value: '4.9/5', label: 'Satisfaction' },
  { value: '8hrs', label: 'Saved per week' },
];

describe('StatsRow', () => {
  it('renders all stat values', () => {
    render(<StatsRow stats={SAMPLE_STATS} />);
    expect(screen.getByText('50+')).toBeInTheDocument();
    expect(screen.getByText('12')).toBeInTheDocument();
    expect(screen.getByText('4.9/5')).toBeInTheDocument();
    expect(screen.getByText('8hrs')).toBeInTheDocument();
  });

  it('renders all stat labels', () => {
    render(<StatsRow stats={SAMPLE_STATS} />);
    expect(screen.getByText('Workshops delivered')).toBeInTheDocument();
    expect(screen.getByText('Industries')).toBeInTheDocument();
    expect(screen.getByText('Satisfaction')).toBeInTheDocument();
    expect(screen.getByText('Saved per week')).toBeInTheDocument();
  });

  it('renders the section title when provided', () => {
    render(<StatsRow sectionTitle="By the numbers" stats={SAMPLE_STATS} />);
    expect(
      screen.getByRole('heading', { level: 2, name: /By the numbers/i }),
    ).toBeInTheDocument();
  });

  it('renders eyebrow when provided', () => {
    render(<StatsRow eyebrow="IMPACT" stats={SAMPLE_STATS} />);
    expect(screen.getByText('IMPACT')).toBeInTheDocument();
  });

  it('renders a default paper-toned section', () => {
    const { container } = render(<StatsRow stats={SAMPLE_STATS} />);
    // Default Section has bg-paper; InkSection would be marked with ink-section class
    const sectionEl = container.querySelector('section');
    expect(sectionEl?.className).not.toMatch(/ink-section/);
    expect(sectionEl?.className).toMatch(/bg-paper\b/);
  });

  it('renders paper-2 tone when tone="paper-2"', () => {
    const { container } = render(<StatsRow tone="paper-2" stats={SAMPLE_STATS} />);
    const sectionEl = container.querySelector('section');
    expect(sectionEl?.className).toMatch(/bg-paper-2/);
  });

  it('renders ink tone via InkSection when tone="ink"', () => {
    const { container } = render(<StatsRow tone="ink" stats={SAMPLE_STATS} />);
    const sectionEl = container.querySelector('section');
    expect(sectionEl?.className).toMatch(/ink-section/);
  });

  it('handles 3 stats', () => {
    render(<StatsRow stats={SAMPLE_STATS.slice(0, 3)} />);
    expect(screen.getByText('50+')).toBeInTheDocument();
    expect(screen.getByText('12')).toBeInTheDocument();
    expect(screen.getByText('4.9/5')).toBeInTheDocument();
    expect(screen.queryByText('8hrs')).not.toBeInTheDocument();
  });

  it('passes through custom className', () => {
    const { container } = render(
      <StatsRow className="custom-stats" stats={SAMPLE_STATS} />,
    );
    expect(container.querySelector('.custom-stats')).toBeTruthy();
  });
});
