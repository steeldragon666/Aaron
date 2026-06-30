import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { CheckboxCard } from './CheckboxCard';

describe('CheckboxCard', () => {
  it('renders label', () => {
    render(<CheckboxCard value="a" label="Option A" />);
    expect(screen.getByText('Option A')).toBeInTheDocument();
  });

  it('renders description when provided', () => {
    render(<CheckboxCard value="a" label="A" description="Extra" />);
    expect(screen.getByText('Extra')).toBeInTheDocument();
  });

  it('wraps a checkbox input with the right value', () => {
    render(<CheckboxCard value="alpha" label="A" />);
    const input = screen.getByRole('checkbox') as HTMLInputElement;
    expect(input.value).toBe('alpha');
  });

  it('is checked when checked prop is true', () => {
    render(<CheckboxCard value="a" label="A" checked onChange={() => {}} />);
    expect(screen.getByRole('checkbox')).toBeChecked();
  });

  it('calls onChange with (value, newChecked) when clicked', () => {
    const onChange = vi.fn();
    render(<CheckboxCard value="x" label="A" checked={false} onChange={onChange} />);
    fireEvent.click(screen.getByText('A'));
    expect(onChange).toHaveBeenCalledWith('x', true);
  });

  it('toggles from checked to unchecked', () => {
    const onChange = vi.fn();
    render(<CheckboxCard value="x" label="A" checked onChange={onChange} />);
    fireEvent.click(screen.getByText('A'));
    expect(onChange).toHaveBeenCalledWith('x', false);
  });

  it('is disabled when disabled prop is true', () => {
    render(<CheckboxCard value="a" label="A" disabled />);
    expect(screen.getByRole('checkbox')).toBeDisabled();
  });

  it('passes through className', () => {
    render(<CheckboxCard value="a" label="A" className="custom" />);
    const label = screen.getByText('A').closest('label');
    expect(label?.className).toMatch(/custom/);
  });

  it('applies selected-state border when checked', () => {
    const { container } = render(
      <CheckboxCard value="a" label="A" checked onChange={() => {}} />,
    );
    const label = container.querySelector('label');
    expect(label?.className).toMatch(/border-ink\b/);
  });
});
