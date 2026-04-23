import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Select } from './Select';

describe('Select', () => {
  it('renders select element with options', () => {
    render(
      <Select aria-label="Country">
        <option value="us">United States</option>
        <option value="au">Australia</option>
      </Select>,
    );
    expect(screen.getByRole('combobox', { name: /country/i })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'United States' })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'Australia' })).toBeInTheDocument();
  });

  it('renders a select DOM node', () => {
    render(
      <Select aria-label="x">
        <option value="a">A</option>
      </Select>,
    );
    expect(screen.getByRole('combobox').tagName).toBe('SELECT');
  });

  it('renders label when provided and links via htmlFor', () => {
    render(
      <Select label="Country" id="country-field">
        <option value="us">US</option>
      </Select>,
    );
    const label = screen.getByText('Country');
    expect(label.tagName).toBe('LABEL');
    expect(label.getAttribute('for')).toBe('country-field');
    expect(screen.getByLabelText('Country')).toBeInTheDocument();
  });

  it('auto-generates id when label provided but no id', () => {
    render(
      <Select label="Generated">
        <option value="a">A</option>
      </Select>,
    );
    const select = screen.getByLabelText('Generated');
    expect(select.id).toBeTruthy();
  });

  it('shows hint text when hint is provided and no error', () => {
    render(
      <Select label="X" hint="Pick your region">
        <option value="a">A</option>
      </Select>,
    );
    expect(screen.getByText('Pick your region')).toBeInTheDocument();
  });

  it('shows error message and applies aria-invalid when error is provided', () => {
    render(
      <Select label="X" error="Required">
        <option value="a">A</option>
      </Select>,
    );
    expect(screen.getByText('Required')).toBeInTheDocument();
    expect(screen.getByLabelText('X').getAttribute('aria-invalid')).toBe('true');
  });

  it('prefers error over hint when both provided', () => {
    render(
      <Select label="X" hint="H" error="E">
        <option value="a">A</option>
      </Select>,
    );
    expect(screen.getByText('E')).toBeInTheDocument();
    expect(screen.queryByText('H')).not.toBeInTheDocument();
  });

  it('calls onChange', () => {
    const onChange = vi.fn();
    render(
      <Select aria-label="x" onChange={onChange}>
        <option value="a">A</option>
        <option value="b">B</option>
      </Select>,
    );
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'b' } });
    expect(onChange).toHaveBeenCalled();
  });

  it('forwards ref to select element', () => {
    const ref = { current: null as HTMLSelectElement | null };
    render(
      <Select ref={ref} aria-label="x">
        <option value="a">A</option>
      </Select>,
    );
    expect(ref.current).toBeInstanceOf(HTMLSelectElement);
  });

  it('passes through className to the select element', () => {
    render(
      <Select aria-label="x" className="custom">
        <option value="a">A</option>
      </Select>,
    );
    expect(screen.getByRole('combobox').className).toMatch(/custom/);
  });

  it('applies error border color when error prop present', () => {
    render(
      <Select aria-label="x" error="E">
        <option value="a">A</option>
      </Select>,
    );
    const select = screen.getByRole('combobox');
    expect(select.className).toMatch(/border-/);
    expect(select.className).toMatch(/#D94B4B/);
  });

  it('renders a chevron icon', () => {
    const { container } = render(
      <Select aria-label="x">
        <option value="a">A</option>
      </Select>,
    );
    // Lucide icons render as inline SVG
    const svg = container.querySelector('svg');
    expect(svg).toBeTruthy();
  });
});
