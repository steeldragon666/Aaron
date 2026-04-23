import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Button } from './Button';

describe('Button', () => {
  it('renders children', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Click</Button>);
    fireEvent.click(screen.getByRole('button'));
    expect(onClick).toHaveBeenCalledOnce();
  });

  it('applies primary variant classes by default', () => {
    render(<Button>Primary</Button>);
    expect(screen.getByRole('button').className).toMatch(/bg-blue/);
  });

  it('applies secondary variant classes', () => {
    render(<Button variant="secondary">Secondary</Button>);
    const btn = screen.getByRole('button');
    expect(btn.className).toMatch(/border/);
    expect(btn.className).toMatch(/text-ink/);
  });

  it('applies ghost variant classes', () => {
    render(<Button variant="ghost">Ghost</Button>);
    expect(screen.getByRole('button').className).toMatch(/bg-transparent/);
  });

  it('renders arrow suffix when arrow prop is true', () => {
    render(<Button arrow>Go</Button>);
    expect(screen.getByRole('button').textContent).toContain('→');
  });

  it('omits arrow when arrow prop is not set', () => {
    render(<Button>No arrow</Button>);
    expect(screen.getByRole('button').textContent).not.toContain('→');
  });

  it('is disabled when disabled prop is true', () => {
    const onClick = vi.fn();
    render(<Button disabled onClick={onClick}>Disabled</Button>);
    const btn = screen.getByRole('button');
    expect(btn).toBeDisabled();
    fireEvent.click(btn);
    expect(onClick).not.toHaveBeenCalled();
  });

  it('applies md size classes', () => {
    render(<Button size="md">Medium</Button>);
    expect(screen.getByRole('button').className).toMatch(/text-\[14px\]|text-sm/);
  });

  it('applies lg size classes (default)', () => {
    render(<Button>Large default</Button>);
    expect(screen.getByRole('button').className).toMatch(/text-\[15px\]/);
  });

  it('forwards ref to the button element', () => {
    const ref = { current: null as HTMLButtonElement | null };
    render(<Button ref={ref}>Ref test</Button>);
    expect(ref.current).toBeInstanceOf(HTMLButtonElement);
  });

  it('passes through custom className via cn()', () => {
    render(<Button className="custom-class">Custom</Button>);
    expect(screen.getByRole('button').className).toMatch(/custom-class/);
  });
});
