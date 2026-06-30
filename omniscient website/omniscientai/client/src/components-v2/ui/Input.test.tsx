import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Input } from './Input';

describe('Input', () => {
  it('renders input element', () => {
    render(<Input placeholder="Enter name" />);
    expect(screen.getByPlaceholderText('Enter name')).toBeInTheDocument();
  });

  it('renders label when provided and links via htmlFor', () => {
    render(<Input label="Email" id="email-field" />);
    const label = screen.getByText('Email');
    expect(label.tagName).toBe('LABEL');
    expect(label.getAttribute('for')).toBe('email-field');
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
  });

  it('auto-generates id when label provided but no id', () => {
    render(<Input label="Generated" />);
    const input = screen.getByLabelText('Generated');
    expect(input.id).toBeTruthy();
  });

  it('shows hint text when hint is provided and no error', () => {
    render(<Input label="X" hint="Your work email" />);
    expect(screen.getByText('Your work email')).toBeInTheDocument();
  });

  it('shows error message and applies aria-invalid when error is provided', () => {
    render(<Input label="X" error="Required" />);
    expect(screen.getByText('Required')).toBeInTheDocument();
    expect(screen.getByLabelText('X').getAttribute('aria-invalid')).toBe('true');
  });

  it('prefers error over hint when both provided', () => {
    render(<Input label="X" hint="H" error="E" />);
    expect(screen.getByText('E')).toBeInTheDocument();
    expect(screen.queryByText('H')).not.toBeInTheDocument();
  });

  it('calls onChange', () => {
    const onChange = vi.fn();
    render(<Input onChange={onChange} placeholder="x" />);
    fireEvent.change(screen.getByPlaceholderText('x'), { target: { value: 'a' } });
    expect(onChange).toHaveBeenCalled();
  });

  it('forwards ref to input element', () => {
    const ref = { current: null as HTMLInputElement | null };
    render(<Input ref={ref} placeholder="x" />);
    expect(ref.current).toBeInstanceOf(HTMLInputElement);
  });

  it('passes through className to the input element', () => {
    render(<Input className="custom" placeholder="x" />);
    expect(screen.getByPlaceholderText('x').className).toMatch(/custom/);
  });

  it('applies error border color when error prop present', () => {
    render(<Input placeholder="x" error="E" />);
    const input = screen.getByPlaceholderText('x');
    expect(input.className).toMatch(/border-/);
    expect(input.className).toMatch(/#D94B4B/);
  });
});
