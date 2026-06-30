import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Slider } from './Slider';

describe('Slider', () => {
  it('renders range input', () => {
    render(<Slider label="Team size" min={1} max={100} defaultValue={10} />);
    const input = screen.getByLabelText(/Team size/i) as HTMLInputElement;
    expect(input.type).toBe('range');
  });

  it('displays current value when label provided', () => {
    render(<Slider label="Hours" min={0} max={40} value={15} onChange={() => {}} />);
    // Expect the current value rendered as a MonoBadge or plain text near the label
    expect(screen.getByText('15')).toBeInTheDocument();
  });

  it('formats displayed value via valueDisplay', () => {
    render(
      <Slider
        label="Rate"
        min={0}
        max={200}
        value={150}
        onChange={() => {}}
        valueDisplay={(v) => `$${v}`}
      />,
    );
    expect(screen.getByText('$150')).toBeInTheDocument();
  });

  it('calls onChange when slider moves', () => {
    const onChange = vi.fn();
    render(<Slider label="x" min={0} max={10} value={5} onChange={onChange} />);
    const input = screen.getByLabelText(/x/i) as HTMLInputElement;
    fireEvent.change(input, { target: { value: '7' } });
    expect(onChange).toHaveBeenCalled();
  });

  it('respects min and max attributes', () => {
    render(<Slider label="x" min={10} max={50} defaultValue={30} />);
    const input = screen.getByLabelText(/x/i) as HTMLInputElement;
    expect(input.min).toBe('10');
    expect(input.max).toBe('50');
  });

  it('shows hint text', () => {
    render(<Slider label="x" min={0} max={10} defaultValue={5} hint="Drag to adjust" />);
    expect(screen.getByText('Drag to adjust')).toBeInTheDocument();
  });

  it('shows error and sets aria-invalid', () => {
    render(<Slider label="x" min={0} max={10} defaultValue={5} error="Required" />);
    expect(screen.getByText('Required')).toBeInTheDocument();
    expect(screen.getByLabelText(/x/i).getAttribute('aria-invalid')).toBe('true');
  });

  it('auto-generates id when not provided', () => {
    render(<Slider label="Auto" min={0} max={10} defaultValue={5} />);
    const input = screen.getByLabelText(/Auto/i) as HTMLInputElement;
    expect(input.id).toBeTruthy();
  });

  it('applies linear-gradient background reflecting the value', () => {
    render(<Slider label="x" min={0} max={100} value={25} onChange={() => {}} />);
    const input = screen.getByLabelText(/x/i) as HTMLInputElement;
    // 25/100 = 25%. Check inline style contains the percent.
    expect(input.style.background).toContain('25%');
  });

  it('forwards ref', () => {
    const ref = { current: null as HTMLInputElement | null };
    render(<Slider ref={ref} label="x" min={0} max={10} defaultValue={5} />);
    expect(ref.current).toBeInstanceOf(HTMLInputElement);
  });

  it('passes through className', () => {
    render(<Slider className="custom" label="x" min={0} max={10} defaultValue={5} />);
    expect(screen.getByLabelText(/x/i).className).toMatch(/custom/);
  });
});
