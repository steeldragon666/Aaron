import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { CaseGrid } from './CaseGrid';

const SAMPLE_CASES = [
  {
    industry: 'Healthcare',
    title: 'Radiology triage agent',
    outcome: '40% faster first-read on priority scans.',
    href: '/work/radiology',
  },
  {
    industry: 'Finance',
    title: 'KYC pipeline',
    outcome: 'Reduced manual review from 45min to 8min per applicant.',
    href: '/work/kyc',
  },
  {
    industry: 'Industrial',
    title: 'Predictive maintenance',
    outcome: 'Cut unplanned downtime by 27% across 14 sites.',
    href: '/work/maintenance',
  },
];

describe('CaseGrid', () => {
  it('renders the section title', () => {
    render(<CaseGrid sectionTitle="Selected work" cases={SAMPLE_CASES} />);
    expect(
      screen.getByRole('heading', { level: 2, name: /Selected work/i }),
    ).toBeInTheDocument();
  });

  it('renders eyebrow when provided', () => {
    render(<CaseGrid eyebrow="CASE STUDIES" cases={SAMPLE_CASES} />);
    expect(screen.getByText('CASE STUDIES')).toBeInTheDocument();
  });

  it('renders all case titles', () => {
    render(<CaseGrid cases={SAMPLE_CASES} />);
    expect(screen.getByText('Radiology triage agent')).toBeInTheDocument();
    expect(screen.getByText('KYC pipeline')).toBeInTheDocument();
    expect(screen.getByText('Predictive maintenance')).toBeInTheDocument();
  });

  it('renders each industry as an eyebrow', () => {
    render(<CaseGrid cases={SAMPLE_CASES} />);
    expect(screen.getByText('Healthcare')).toBeInTheDocument();
    expect(screen.getByText('Finance')).toBeInTheDocument();
    expect(screen.getByText('Industrial')).toBeInTheDocument();
  });

  it('renders outcome paragraphs', () => {
    render(<CaseGrid cases={SAMPLE_CASES} />);
    expect(screen.getByText(/40% faster first-read/i)).toBeInTheDocument();
  });

  it('renders a CTA link per case with correct href', () => {
    render(<CaseGrid cases={SAMPLE_CASES} />);
    const links = screen.getAllByRole('link', { name: /Read the case study/i });
    expect(links).toHaveLength(3);
    expect(links[0].getAttribute('href')).toBe('/work/radiology');
    expect(links[1].getAttribute('href')).toBe('/work/kyc');
    expect(links[2].getAttribute('href')).toBe('/work/maintenance');
  });

  it('renders first case as FeaturedCard with ink background', () => {
    const { container } = render(<CaseGrid cases={SAMPLE_CASES} />);
    const cards = container.querySelectorAll('[class*="bg-ink"], [class*="bg-paper"]');
    // First card should have bg-ink (FeaturedCard), others bg-paper (Card)
    const inkCards = container.querySelectorAll('[class*="bg-ink"]');
    expect(inkCards.length).toBeGreaterThanOrEqual(1);
    expect(cards.length).toBeGreaterThanOrEqual(3);
  });

  it('handles a single case gracefully', () => {
    render(<CaseGrid cases={[SAMPLE_CASES[0]]} />);
    expect(screen.getByText('Radiology triage agent')).toBeInTheDocument();
    expect(screen.getAllByRole('link', { name: /Read the case study/i })).toHaveLength(1);
  });

  it('handles two cases gracefully', () => {
    render(<CaseGrid cases={SAMPLE_CASES.slice(0, 2)} />);
    expect(screen.getAllByRole('link', { name: /Read the case study/i })).toHaveLength(2);
  });

  it('passes through custom className', () => {
    const { container } = render(
      <CaseGrid className="custom-grid" cases={SAMPLE_CASES} />,
    );
    expect(container.querySelector('.custom-grid')).toBeTruthy();
  });
});
