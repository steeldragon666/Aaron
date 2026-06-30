import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { WorkshopCardGrid } from './WorkshopCardGrid';

const SAMPLE_WORKSHOPS = [
  {
    slug: 'ai-fundamentals-sme',
    title: 'AI Fundamentals for SMEs',
    description: 'A two-day foundation covering LLMs, RAG, and agentic patterns.',
    duration: '2 days',
    format: 'In-person, Melbourne',
    price: '$4,995 AUD',
  },
  {
    slug: 'clinical-ai-primer',
    title: 'Clinical AI Primer',
    description: 'Safe adoption patterns for regulated healthcare settings.',
    duration: '1 day',
    format: 'Hybrid',
    price: 'From $2,495',
    imageUrl: '/images/workshop-clinical.jpg',
  },
  {
    slug: 'agentic-ops-lab',
    title: 'Agentic Ops Lab',
    description: 'Build an internal agent that actually ships to production.',
    duration: '3 days',
    format: 'In-person, Sydney',
    price: '$6,995 AUD',
  },
];

describe('WorkshopCardGrid', () => {
  it('renders the section title', () => {
    render(
      <WorkshopCardGrid
        sectionTitle="Workshop catalog"
        workshops={SAMPLE_WORKSHOPS}
      />,
    );
    expect(
      screen.getByRole('heading', { level: 2, name: /Workshop catalog/i }),
    ).toBeInTheDocument();
  });

  it('renders eyebrow when provided', () => {
    render(
      <WorkshopCardGrid eyebrow="UPCOMING" workshops={SAMPLE_WORKSHOPS} />,
    );
    expect(screen.getByText('UPCOMING')).toBeInTheDocument();
  });

  it('renders all workshop titles', () => {
    render(<WorkshopCardGrid workshops={SAMPLE_WORKSHOPS} />);
    expect(screen.getByText('AI Fundamentals for SMEs')).toBeInTheDocument();
    expect(screen.getByText('Clinical AI Primer')).toBeInTheDocument();
    expect(screen.getByText('Agentic Ops Lab')).toBeInTheDocument();
  });

  it('renders workshop descriptions', () => {
    render(<WorkshopCardGrid workshops={SAMPLE_WORKSHOPS} />);
    expect(screen.getByText(/two-day foundation/i)).toBeInTheDocument();
  });

  it('renders duration / format / price meta for each workshop', () => {
    render(<WorkshopCardGrid workshops={SAMPLE_WORKSHOPS} />);
    expect(screen.getByText(/2 days/i)).toBeInTheDocument();
    expect(screen.getByText(/In-person, Melbourne/i)).toBeInTheDocument();
    expect(screen.getByText(/\$4,995 AUD/i)).toBeInTheDocument();
  });

  it('renders a Book CTA linking to /workshops/{slug}', () => {
    render(<WorkshopCardGrid workshops={SAMPLE_WORKSHOPS} />);
    const links = screen.getAllByRole('link', { name: /Book this workshop/i });
    expect(links).toHaveLength(3);
    expect(links[0].getAttribute('href')).toBe('/workshops/ai-fundamentals-sme');
    expect(links[1].getAttribute('href')).toBe('/workshops/clinical-ai-primer');
    expect(links[2].getAttribute('href')).toBe('/workshops/agentic-ops-lab');
  });

  it('renders image when imageUrl provided', () => {
    const { container } = render(
      <WorkshopCardGrid workshops={[SAMPLE_WORKSHOPS[1]]} />,
    );
    const img = container.querySelector('img');
    expect(img).toBeTruthy();
    expect(img?.getAttribute('src')).toBe('/images/workshop-clinical.jpg');
  });

  it('does not render image when imageUrl absent', () => {
    const { container } = render(
      <WorkshopCardGrid workshops={[SAMPLE_WORKSHOPS[0]]} />,
    );
    expect(container.querySelector('img')).toBeNull();
  });

  it('passes through custom className', () => {
    const { container } = render(
      <WorkshopCardGrid className="custom-grid" workshops={SAMPLE_WORKSHOPS} />,
    );
    expect(container.querySelector('.custom-grid')).toBeTruthy();
  });
});
