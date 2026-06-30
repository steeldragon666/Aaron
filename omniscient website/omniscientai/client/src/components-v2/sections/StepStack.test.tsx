import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { StepStack } from './StepStack';

const SAMPLE_STEPS = [
  {
    title: 'Discover',
    body: 'Map the current workflow end-to-end and surface the real blockers.',
    duration: '1 week',
  },
  {
    title: 'Design',
    body: 'Co-design the target-state workflow with the team who will run it.',
    duration: '2 weeks',
  },
  {
    title: 'Deliver',
    body: 'Ship the first production agent and the eval harness it runs against.',
    duration: '4 weeks',
  },
];

describe('StepStack', () => {
  it('renders the section title', () => {
    render(<StepStack sectionTitle="Our methodology" steps={SAMPLE_STEPS} />);
    expect(
      screen.getByRole('heading', { level: 2, name: /Our methodology/i }),
    ).toBeInTheDocument();
  });

  it('renders all step titles', () => {
    render(<StepStack steps={SAMPLE_STEPS} />);
    expect(screen.getByText('Discover')).toBeInTheDocument();
    expect(screen.getByText('Design')).toBeInTheDocument();
    expect(screen.getByText('Deliver')).toBeInTheDocument();
  });

  it('renders all step bodies', () => {
    render(<StepStack steps={SAMPLE_STEPS} />);
    expect(screen.getByText(/Map the current workflow/i)).toBeInTheDocument();
    expect(screen.getByText(/Co-design the target-state/i)).toBeInTheDocument();
    expect(screen.getByText(/Ship the first production agent/i)).toBeInTheDocument();
  });

  it('renders numbered labels 01, 02, 03', () => {
    render(<StepStack steps={SAMPLE_STEPS} />);
    expect(screen.getByText('01')).toBeInTheDocument();
    expect(screen.getByText('02')).toBeInTheDocument();
    expect(screen.getByText('03')).toBeInTheDocument();
  });

  it('renders duration when provided', () => {
    render(<StepStack steps={SAMPLE_STEPS} />);
    expect(screen.getByText('1 week')).toBeInTheDocument();
    expect(screen.getByText('2 weeks')).toBeInTheDocument();
    expect(screen.getByText('4 weeks')).toBeInTheDocument();
  });

  it('does not render duration when absent', () => {
    const stepsWithoutDuration = [
      { title: 'Solo', body: 'Just a title and body, no duration.' },
    ];
    const { container } = render(<StepStack steps={stepsWithoutDuration} />);
    // There should be no mono-badge rendered for duration.
    expect(container.querySelector('.mono-badge')).toBeNull();
  });

  it('renders step titles as h3 headings', () => {
    render(<StepStack steps={SAMPLE_STEPS} />);
    expect(
      screen.getByRole('heading', { level: 3, name: /Discover/i }),
    ).toBeInTheDocument();
  });

  it('renders eyebrow when provided', () => {
    render(<StepStack eyebrow="METHODOLOGY" steps={SAMPLE_STEPS} />);
    expect(screen.getByText('METHODOLOGY')).toBeInTheDocument();
  });

  it('renders lede when provided', () => {
    render(
      <StepStack
        lede="Four phases, one consultancy."
        steps={SAMPLE_STEPS}
      />,
    );
    expect(screen.getByText(/Four phases, one consultancy/i)).toBeInTheDocument();
  });

  it('passes through custom className', () => {
    const { container } = render(
      <StepStack className="custom-steps" steps={SAMPLE_STEPS} />,
    );
    expect(container.querySelector('.custom-steps')).toBeTruthy();
  });
});
