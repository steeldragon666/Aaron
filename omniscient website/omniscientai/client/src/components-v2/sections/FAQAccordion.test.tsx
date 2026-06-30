import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { FAQAccordion } from './FAQAccordion';

const ITEMS = [
  { q: 'What happens on day one?', a: 'We map your current workflow.' },
  { q: 'Is this vendor-neutral?', a: 'Yes — we have no vendor kickbacks.' },
];

describe('FAQAccordion', () => {
  it('renders the section title', () => {
    render(<FAQAccordion sectionTitle="Frequently asked" items={ITEMS} />);
    expect(
      screen.getByRole('heading', { level: 2, name: /Frequently asked/ }),
    ).toBeInTheDocument();
  });

  it('renders all question buttons', () => {
    render(<FAQAccordion items={ITEMS} />);
    expect(
      screen.getByRole('button', { name: /What happens on day one/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /vendor-neutral/i }),
    ).toBeInTheDocument();
  });

  it('all items closed by default', () => {
    render(<FAQAccordion items={ITEMS} />);
    const buttons = screen.getAllByRole('button');
    buttons.forEach((btn) => {
      expect(btn.getAttribute('aria-expanded')).toBe('false');
    });
  });

  it('opens an item when clicked', () => {
    render(<FAQAccordion items={ITEMS} />);
    fireEvent.click(screen.getByRole('button', { name: /day one/i }));
    expect(
      screen.getByRole('button', { name: /day one/i }).getAttribute('aria-expanded'),
    ).toBe('true');
    expect(screen.getByText('We map your current workflow.')).toBeInTheDocument();
  });

  it('closes the item on second click', () => {
    render(<FAQAccordion items={ITEMS} />);
    const btn = screen.getByRole('button', { name: /day one/i });
    fireEvent.click(btn);
    fireEvent.click(btn);
    expect(btn.getAttribute('aria-expanded')).toBe('false');
  });

  it('opening another item closes the first (single-open)', () => {
    render(<FAQAccordion items={ITEMS} />);
    const btn1 = screen.getByRole('button', { name: /day one/i });
    const btn2 = screen.getByRole('button', { name: /vendor-neutral/i });
    fireEvent.click(btn1);
    fireEvent.click(btn2);
    expect(btn1.getAttribute('aria-expanded')).toBe('false');
    expect(btn2.getAttribute('aria-expanded')).toBe('true');
  });

  it('renders eyebrow when provided', () => {
    render(<FAQAccordion eyebrow="SUPPORT" items={ITEMS} />);
    expect(screen.getByText('SUPPORT')).toBeInTheDocument();
  });

  it('passes through custom className', () => {
    const { container } = render(
      <FAQAccordion className="custom-faq" items={ITEMS} />,
    );
    expect(container.querySelector('.custom-faq')).toBeTruthy();
  });
});
