import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { GraduationCap, Activity, Shield, Bot } from 'lucide-react';
import { PillarGrid } from './PillarGrid';

const SAMPLE_PILLARS = [
  { icon: GraduationCap, title: 'AI Training', description: 'Workshops for SMEs' },
  { icon: Activity, title: 'Health', description: 'Clinical AI' },
  { icon: Shield, title: 'Defense', description: 'Hardened systems' },
  { icon: Bot, title: 'Agentic Ops', description: 'Marketing + ops agents' },
];

describe('PillarGrid', () => {
  it('renders the section title', () => {
    render(<PillarGrid sectionTitle="Practice areas" pillars={SAMPLE_PILLARS} />);
    expect(
      screen.getByRole('heading', { level: 2, name: /Practice areas/i }),
    ).toBeInTheDocument();
  });

  it('renders all pillars', () => {
    render(<PillarGrid pillars={SAMPLE_PILLARS} />);
    expect(screen.getByText('AI Training')).toBeInTheDocument();
    expect(screen.getByText('Health')).toBeInTheDocument();
    expect(screen.getByText('Defense')).toBeInTheDocument();
    expect(screen.getByText('Agentic Ops')).toBeInTheDocument();
  });

  it('renders descriptions', () => {
    render(<PillarGrid pillars={SAMPLE_PILLARS} />);
    expect(screen.getByText('Workshops for SMEs')).toBeInTheDocument();
    expect(screen.getByText('Clinical AI')).toBeInTheDocument();
  });

  it('renders pillar titles as h3 headings', () => {
    render(<PillarGrid pillars={SAMPLE_PILLARS} />);
    expect(
      screen.getByRole('heading', { level: 3, name: /AI Training/i }),
    ).toBeInTheDocument();
  });

  it('renders icons as SVG elements', () => {
    const { container } = render(<PillarGrid pillars={SAMPLE_PILLARS} />);
    const svgs = container.querySelectorAll('svg');
    expect(svgs.length).toBe(SAMPLE_PILLARS.length);
  });

  it('renders Learn more link when href provided', () => {
    const pillars = [{ ...SAMPLE_PILLARS[0], href: '/services/training' }];
    render(<PillarGrid pillars={pillars} />);
    const link = screen.getByRole('link', { name: /Learn more/i });
    expect(link).toBeInTheDocument();
    expect(link.getAttribute('href')).toBe('/services/training');
  });

  it('does not render Learn more link when href absent', () => {
    render(<PillarGrid pillars={SAMPLE_PILLARS} />);
    expect(screen.queryByRole('link', { name: /Learn more/i })).not.toBeInTheDocument();
  });

  it('renders eyebrow when provided', () => {
    render(<PillarGrid eyebrow="WHAT WE DO" pillars={SAMPLE_PILLARS} />);
    expect(screen.getByText('WHAT WE DO')).toBeInTheDocument();
  });

  it('renders lede when provided', () => {
    render(
      <PillarGrid
        lede="Four practice areas, one consultancy."
        pillars={SAMPLE_PILLARS}
      />,
    );
    expect(screen.getByText(/Four practice areas/i)).toBeInTheDocument();
  });

  it('passes through custom className', () => {
    const { container } = render(
      <PillarGrid className="custom-grid" pillars={SAMPLE_PILLARS} />,
    );
    expect(container.querySelector('.custom-grid')).toBeTruthy();
  });
});
