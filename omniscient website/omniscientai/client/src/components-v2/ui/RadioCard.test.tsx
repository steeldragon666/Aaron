import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { RadioCard } from './RadioCard';

describe('RadioCard', () => {
  it('renders label', () => {
    render(<RadioCard name="q1" value="a" label="Option A" />);
    expect(screen.getByText('Option A')).toBeInTheDocument();
  });

  it('renders description when provided', () => {
    render(
      <RadioCard name="q1" value="a" label="A" description="Extra detail" />,
    );
    expect(screen.getByText('Extra detail')).toBeInTheDocument();
  });

  it('wraps a radio input with the right name and value', () => {
    render(<RadioCard name="q1" value="alpha" label="A" />);
    const input = screen.getByRole('radio') as HTMLInputElement;
    expect(input.name).toBe('q1');
    expect(input.value).toBe('alpha');
  });

  it('is checked when checked prop is true', () => {
    render(<RadioCard name="q" value="a" label="A" checked onChange={() => {}} />);
    expect(screen.getByRole('radio')).toBeChecked();
  });

  it('calls onChange with the value when clicked', () => {
    const onChange = vi.fn();
    render(<RadioCard name="q" value="x" label="A" checked={false} onChange={onChange} />);
    fireEvent.click(screen.getByText('A'));
    expect(onChange).toHaveBeenCalledWith('x');
  });

  it('is disabled when disabled prop is true', () => {
    render(<RadioCard name="q" value="a" label="A" disabled />);
    expect(screen.getByRole('radio')).toBeDisabled();
  });

  it('passes through className to the label wrapper', () => {
    render(<RadioCard name="q" value="a" label="A" className="custom" />);
    const label = screen.getByText('A').closest('label');
    expect(label?.className).toMatch(/custom/);
  });

  it('applies selected-state border when checked', () => {
    const { container } = render(
      <RadioCard name="q" value="a" label="A" checked onChange={() => {}} />,
    );
    // Look for the label wrapper class list — selected adds border-ink
    const label = container.querySelector('label');
    expect(label?.className).toMatch(/border-ink\b/);
  });
});
