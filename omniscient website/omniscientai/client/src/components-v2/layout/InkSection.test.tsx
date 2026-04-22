import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { InkSection } from './InkSection';

describe('InkSection', () => {
  it('renders children', () => {
    render(<InkSection>Body</InkSection>);
    expect(screen.getByText('Body')).toBeInTheDocument();
  });

  it('renders as a semantic <section> element', () => {
    render(<InkSection data-testid="s">Body</InkSection>);
    expect(screen.getByTestId('s').tagName).toBe('SECTION');
  });

  it('applies the ink-section class', () => {
    render(<InkSection data-testid="s">Body</InkSection>);
    expect(screen.getByTestId('s').className).toMatch(/\bink-section\b/);
  });

  it('applies standard vertical rhythm (py-12 lg:py-24)', () => {
    render(<InkSection data-testid="s">Body</InkSection>);
    const cls = screen.getByTestId('s').className;
    expect(cls).toMatch(/\bpy-12\b/);
    expect(cls).toMatch(/lg:py-24/);
  });

  it('renders eyebrow, title and lede when provided', () => {
    render(
      <InkSection
        eyebrow="Eyebrow label"
        title="Ink title"
        lede="Lead paragraph text"
        data-testid="s"
      >
        Body
      </InkSection>,
    );
    expect(screen.getByText('Eyebrow label')).toBeInTheDocument();
    const h2 = screen.getByText('Ink title');
    expect(h2.tagName).toBe('H2');
    expect(screen.getByText('Lead paragraph text')).toBeInTheDocument();
  });

  it('wraps children in Container by default', () => {
    render(<InkSection data-testid="s">Body</InkSection>);
    const section = screen.getByTestId('s');
    const container = section.querySelector('.max-w-\\[1240px\\]');
    expect(container).not.toBeNull();
  });

  it('does NOT wrap children in Container when fluid=true', () => {
    render(<InkSection fluid data-testid="s">Body</InkSection>);
    const section = screen.getByTestId('s');
    expect(section.querySelector('.max-w-\\[1240px\\]')).toBeNull();
  });

  it('passes through custom className via cn()', () => {
    render(<InkSection className="custom-class" data-testid="s">Body</InkSection>);
    expect(screen.getByTestId('s').className).toMatch(/custom-class/);
  });
});
