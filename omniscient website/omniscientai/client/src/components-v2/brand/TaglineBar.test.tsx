import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { TaglineBar } from './TaglineBar';

describe('TaglineBar', () => {
  it('renders the three-word tagline', () => {
    render(<TaglineBar data-testid="tb" />);
    const el = screen.getByTestId('tb');
    const text = el.textContent ?? '';
    expect(text).toMatch(/INTELLIGENCE/);
    expect(text).toMatch(/CONNECTIVITY/);
    expect(text).toMatch(/INNOVATION/);
    expect(text.match(/\/\//g)?.length).toBe(2);
  });

  it('uses eyebrow utility class', () => {
    render(<TaglineBar data-testid="tb" />);
    expect(screen.getByTestId('tb').className).toMatch(/eyebrow/);
  });

  it('aligns left by default', () => {
    render(<TaglineBar data-testid="tb" />);
    expect(screen.getByTestId('tb').className).toMatch(/text-left/);
  });

  it('aligns center when align="center"', () => {
    render(<TaglineBar align="center" data-testid="tb" />);
    expect(screen.getByTestId('tb').className).toMatch(/text-center/);
  });

  it('passes through className', () => {
    render(<TaglineBar className="custom" data-testid="tb" />);
    expect(screen.getByTestId('tb').className).toMatch(/custom/);
  });
});
