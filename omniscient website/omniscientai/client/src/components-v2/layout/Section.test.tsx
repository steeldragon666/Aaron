import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Section } from './Section';

describe('Section', () => {
  it('renders children', () => {
    render(<Section>Body</Section>);
    expect(screen.getByText('Body')).toBeInTheDocument();
  });

  it('renders as a semantic <section> element', () => {
    render(<Section data-testid="s">Body</Section>);
    expect(screen.getByTestId('s').tagName).toBe('SECTION');
  });

  it('applies paper tone by default', () => {
    render(<Section data-testid="s">Body</Section>);
    expect(screen.getByTestId('s').className).toMatch(/bg-paper\b/);
  });

  it('applies paper-2 tone when tone="paper-2"', () => {
    render(<Section tone="paper-2" data-testid="s">Body</Section>);
    expect(screen.getByTestId('s').className).toMatch(/bg-paper-2/);
  });

  it('applies standard vertical rhythm (py-12 lg:py-24)', () => {
    render(<Section data-testid="s">Body</Section>);
    const cls = screen.getByTestId('s').className;
    expect(cls).toMatch(/\bpy-12\b/);
    expect(cls).toMatch(/lg:py-24/);
  });

  it('renders eyebrow, title and lede when provided', () => {
    render(
      <Section
        eyebrow="Eyebrow label"
        title="The title"
        lede="Lead paragraph text"
        data-testid="s"
      >
        Body
      </Section>,
    );
    expect(screen.getByText('Eyebrow label')).toBeInTheDocument();
    const h2 = screen.getByText('The title');
    expect(h2.tagName).toBe('H2');
    expect(screen.getByText('Lead paragraph text')).toBeInTheDocument();
    expect(screen.getByText('Body')).toBeInTheDocument();
  });

  it('does not render header block when no eyebrow/title/lede are given', () => {
    render(<Section data-testid="s">Body only</Section>);
    const section = screen.getByTestId('s');
    // No <h2> should be emitted when there is no title.
    expect(section.querySelector('h2')).toBeNull();
  });

  it('wraps children in Container by default', () => {
    render(<Section data-testid="s">Body</Section>);
    const section = screen.getByTestId('s');
    // The container adds the shared 1240px max-width / mx-auto classes.
    const container = section.querySelector('.max-w-\\[1240px\\]');
    expect(container).not.toBeNull();
    expect(container?.className).toMatch(/mx-auto/);
  });

  it('does NOT wrap children in Container when fluid=true', () => {
    render(<Section fluid data-testid="s">Body</Section>);
    const section = screen.getByTestId('s');
    // No inner container element should be present.
    expect(section.querySelector('.max-w-\\[1240px\\]')).toBeNull();
  });

  it('passes through custom className via cn()', () => {
    render(<Section className="custom-class" data-testid="s">Body</Section>);
    expect(screen.getByTestId('s').className).toMatch(/custom-class/);
  });
});
