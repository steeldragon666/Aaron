import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Eyebrow, Display, Lede, MonoBadge } from './Typography';

describe('Eyebrow', () => {
  it('renders children in a span by default', () => {
    render(<Eyebrow>Featured</Eyebrow>);
    const el = screen.getByText('Featured');
    expect(el.tagName).toBe('SPAN');
    expect(el.className).toMatch(/eyebrow/);
  });

  it('renders as div when as="div"', () => {
    render(<Eyebrow as="div">X</Eyebrow>);
    expect(screen.getByText('X').tagName).toBe('DIV');
  });

  it('passes through className', () => {
    render(<Eyebrow className="custom" data-testid="e">X</Eyebrow>);
    expect(screen.getByTestId('e').className).toMatch(/custom/);
  });
});

describe('Display', () => {
  it('renders children in h1 by default', () => {
    render(<Display>Big headline</Display>);
    const el = screen.getByText('Big headline');
    expect(el.tagName).toBe('H1');
    expect(el.className).toMatch(/display/);
  });

  it('renders as h2 when as="h2"', () => {
    render(<Display as="h2">Second</Display>);
    expect(screen.getByText('Second').tagName).toBe('H2');
  });

  it('passes through className', () => {
    render(<Display className="extra" data-testid="d">X</Display>);
    expect(screen.getByTestId('d').className).toMatch(/extra/);
  });
});

describe('Lede', () => {
  it('renders children in a p by default', () => {
    render(<Lede>Lead paragraph</Lede>);
    const el = screen.getByText('Lead paragraph');
    expect(el.tagName).toBe('P');
    expect(el.className).toMatch(/lede/);
  });

  it('renders as div when as="div"', () => {
    render(<Lede as="div">X</Lede>);
    expect(screen.getByText('X').tagName).toBe('DIV');
  });
});

describe('MonoBadge', () => {
  it('renders children in a span by default', () => {
    render(<MonoBadge>$4,995</MonoBadge>);
    const el = screen.getByText('$4,995');
    expect(el.tagName).toBe('SPAN');
    expect(el.className).toMatch(/mono-badge/);
  });

  it('renders as div when as="div"', () => {
    render(<MonoBadge as="div">X</MonoBadge>);
    expect(screen.getByText('X').tagName).toBe('DIV');
  });

  it('passes through className', () => {
    render(<MonoBadge className="extra" data-testid="m">X</MonoBadge>);
    expect(screen.getByTestId('m').className).toMatch(/extra/);
  });
});
