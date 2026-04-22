import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Card, FeaturedCard } from './Card';

describe('Card', () => {
  it('renders children', () => {
    render(<Card>Hello</Card>);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });

  it('renders as div by default', () => {
    render(<Card data-testid="card">Content</Card>);
    expect(screen.getByTestId('card').tagName).toBe('DIV');
  });

  it('renders as anchor when as="a"', () => {
    render(<Card as="a" href="/x" data-testid="card">Link</Card>);
    const el = screen.getByTestId('card');
    expect(el.tagName).toBe('A');
    expect(el.getAttribute('href')).toBe('/x');
  });

  it('applies paper tone classes by default', () => {
    render(<Card data-testid="card">Content</Card>);
    expect(screen.getByTestId('card').className).toMatch(/bg-paper\b/);
  });

  it('applies paper-2 tone classes', () => {
    render(<Card tone="paper-2" data-testid="card">Content</Card>);
    expect(screen.getByTestId('card').className).toMatch(/bg-paper-2/);
  });

  it('applies border and radius classes', () => {
    render(<Card data-testid="card">Content</Card>);
    const cls = screen.getByTestId('card').className;
    expect(cls).toMatch(/border/);
    expect(cls).toMatch(/border-line/);
    expect(cls).toMatch(/rounded-lg/);
  });

  it('includes cursor-pointer only when as="a"', () => {
    const { rerender } = render(<Card data-testid="card">Content</Card>);
    expect(screen.getByTestId('card').className).not.toMatch(/cursor-pointer/);

    rerender(<Card as="a" href="/x" data-testid="card">Link</Card>);
    expect(screen.getByTestId('card').className).toMatch(/cursor-pointer/);
  });

  it('passes through custom className via cn()', () => {
    render(<Card className="custom-class" data-testid="card">Content</Card>);
    expect(screen.getByTestId('card').className).toMatch(/custom-class/);
  });
});

describe('FeaturedCard', () => {
  it('renders children', () => {
    render(<FeaturedCard>Featured</FeaturedCard>);
    expect(screen.getByText('Featured')).toBeInTheDocument();
  });

  it('applies ink background and paper text', () => {
    render(<FeaturedCard data-testid="fc">Featured</FeaturedCard>);
    const cls = screen.getByTestId('fc').className;
    expect(cls).toMatch(/bg-ink\b/);
    expect(cls).toMatch(/text-paper/);
  });

  it('renders as anchor when as="a"', () => {
    render(<FeaturedCard as="a" href="/x" data-testid="fc">Link</FeaturedCard>);
    expect(screen.getByTestId('fc').tagName).toBe('A');
  });

  it('passes through custom className', () => {
    render(<FeaturedCard className="custom" data-testid="fc">X</FeaturedCard>);
    expect(screen.getByTestId('fc').className).toMatch(/custom/);
  });
});
