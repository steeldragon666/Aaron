import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { CTALink } from './CTALink';

describe('CTALink', () => {
  it('renders children as an anchor', () => {
    render(<CTALink href="/x">Read more</CTALink>);
    const el = screen.getByRole('link', { name: /read more/i });
    expect(el).toBeInTheDocument();
    expect(el.tagName).toBe('A');
    expect(el.getAttribute('href')).toBe('/x');
  });

  it('includes trailing arrow for internal link', () => {
    render(<CTALink href="/x">Read</CTALink>);
    expect(screen.getByRole('link').textContent).toContain('→');
  });

  it('uses diagonal arrow and opens new tab for external', () => {
    render(<CTALink href="https://example.com" external>Visit</CTALink>);
    const el = screen.getByRole('link');
    expect(el.textContent).toContain('↗');
    expect(el.getAttribute('target')).toBe('_blank');
    expect(el.getAttribute('rel')).toBe('noopener noreferrer');
  });

  it('passes through className', () => {
    render(<CTALink href="/x" className="custom">X</CTALink>);
    expect(screen.getByRole('link').className).toMatch(/custom/);
  });

  it('forwards ref to anchor', () => {
    const ref = { current: null as HTMLAnchorElement | null };
    render(<CTALink ref={ref} href="/x">X</CTALink>);
    expect(ref.current).toBeInstanceOf(HTMLAnchorElement);
  });
});
