import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Container } from './Container';

describe('Container', () => {
  it('renders children', () => {
    render(<Container>Inside</Container>);
    expect(screen.getByText('Inside')).toBeInTheDocument();
  });

  it('renders as div by default', () => {
    render(<Container data-testid="c">Content</Container>);
    expect(screen.getByTestId('c').tagName).toBe('DIV');
  });

  it('renders as main when as="main"', () => {
    render(<Container as="main" data-testid="c">Content</Container>);
    expect(screen.getByTestId('c').tagName).toBe('MAIN');
  });

  it('renders as section when as="section"', () => {
    render(<Container as="section" data-testid="c">Content</Container>);
    expect(screen.getByTestId('c').tagName).toBe('SECTION');
  });

  it('renders as article when as="article"', () => {
    render(<Container as="article" data-testid="c">Content</Container>);
    expect(screen.getByTestId('c').tagName).toBe('ARTICLE');
  });

  it('applies max-w-[1240px] and mx-auto classes', () => {
    render(<Container data-testid="c">Content</Container>);
    const cls = screen.getByTestId('c').className;
    expect(cls).toMatch(/max-w-\[1240px\]/);
    expect(cls).toMatch(/mx-auto/);
  });

  it('applies responsive horizontal padding (24px mobile, 72px desktop)', () => {
    render(<Container data-testid="c">Content</Container>);
    const cls = screen.getByTestId('c').className;
    expect(cls).toMatch(/\bpx-6\b/);
    expect(cls).toMatch(/lg:px-\[72px\]/);
  });

  it('passes through custom className via cn()', () => {
    render(<Container className="custom-class" data-testid="c">Content</Container>);
    expect(screen.getByTestId('c').className).toMatch(/custom-class/);
  });
});
