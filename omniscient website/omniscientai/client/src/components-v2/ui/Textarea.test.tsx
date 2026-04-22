import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Textarea } from './Textarea';

describe('Textarea', () => {
  it('renders textarea element', () => {
    render(<Textarea placeholder="Enter message" />);
    expect(screen.getByPlaceholderText('Enter message')).toBeInTheDocument();
  });

  it('renders a textarea DOM node', () => {
    render(<Textarea placeholder="x" />);
    expect(screen.getByPlaceholderText('x').tagName).toBe('TEXTAREA');
  });

  it('defaults to 4 rows', () => {
    render(<Textarea placeholder="x" />);
    expect(screen.getByPlaceholderText('x').getAttribute('rows')).toBe('4');
  });

  it('allows overriding rows', () => {
    render(<Textarea placeholder="x" rows={8} />);
    expect(screen.getByPlaceholderText('x').getAttribute('rows')).toBe('8');
  });

  it('renders label when provided and links via htmlFor', () => {
    render(<Textarea label="Message" id="msg-field" />);
    const label = screen.getByText('Message');
    expect(label.tagName).toBe('LABEL');
    expect(label.getAttribute('for')).toBe('msg-field');
    expect(screen.getByLabelText('Message')).toBeInTheDocument();
  });

  it('auto-generates id when label provided but no id', () => {
    render(<Textarea label="Generated" />);
    const textarea = screen.getByLabelText('Generated');
    expect(textarea.id).toBeTruthy();
  });

  it('shows hint text when hint is provided and no error', () => {
    render(<Textarea label="X" hint="Share your thoughts" />);
    expect(screen.getByText('Share your thoughts')).toBeInTheDocument();
  });

  it('shows error message and applies aria-invalid when error is provided', () => {
    render(<Textarea label="X" error="Required" />);
    expect(screen.getByText('Required')).toBeInTheDocument();
    expect(screen.getByLabelText('X').getAttribute('aria-invalid')).toBe('true');
  });

  it('prefers error over hint when both provided', () => {
    render(<Textarea label="X" hint="H" error="E" />);
    expect(screen.getByText('E')).toBeInTheDocument();
    expect(screen.queryByText('H')).not.toBeInTheDocument();
  });

  it('calls onChange', () => {
    const onChange = vi.fn();
    render(<Textarea onChange={onChange} placeholder="x" />);
    fireEvent.change(screen.getByPlaceholderText('x'), { target: { value: 'a' } });
    expect(onChange).toHaveBeenCalled();
  });

  it('forwards ref to textarea element', () => {
    const ref = { current: null as HTMLTextAreaElement | null };
    render(<Textarea ref={ref} placeholder="x" />);
    expect(ref.current).toBeInstanceOf(HTMLTextAreaElement);
  });

  it('passes through className to the textarea element', () => {
    render(<Textarea className="custom" placeholder="x" />);
    expect(screen.getByPlaceholderText('x').className).toMatch(/custom/);
  });

  it('applies error border color when error prop present', () => {
    render(<Textarea placeholder="x" error="E" />);
    const textarea = screen.getByPlaceholderText('x');
    expect(textarea.className).toMatch(/border-/);
    expect(textarea.className).toMatch(/#D94B4B/);
  });
});
