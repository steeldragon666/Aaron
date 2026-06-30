/**
 * Smoke tests for the v2 ROICalculator page. Verifies the inputs render,
 * that sliders drive the live computed outputs (hours saved + annual
 * savings), that the annual savings renders as formatted AUD ($X,XXX),
 * and that the closing CTA routes to /book.
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { HelmetProvider } from 'react-helmet-async';
import ROICalculator from './ROICalculator';

function renderPage() {
  return render(
    <HelmetProvider>
      <ROICalculator />
    </HelmetProvider>,
  );
}

// Sliders expose a range input per label — fetch by testid for stability
// (labels may share prefixes between Input and Slider primitives).
function getSlider(testid: string): HTMLInputElement {
  return screen.getByTestId(testid) as HTMLInputElement;
}

describe('ROICalculator page', () => {
  it('renders hero title', () => {
    renderPage();
    expect(
      screen.getByRole('heading', {
        level: 1,
        name: /What could AI save your team\?/i,
      }),
    ).toBeInTheDocument();
  });

  it('renders all four sliders and the industry Select', () => {
    renderPage();
    // Sliders — all four by testid
    expect(getSlider('team-size-slider').type).toBe('range');
    expect(getSlider('hours-slider').type).toBe('range');
    expect(getSlider('rate-slider').type).toBe('range');
    expect(getSlider('efficiency-slider').type).toBe('range');
    // Industry Select
    expect(screen.getByLabelText(/Industry/i)).toBeInTheDocument();
  });

  it('updating the team size slider updates the hours-saved calculation', () => {
    renderPage();
    // Defaults: team=20, hours=15, efficiency=30 → hoursSaved = 20*15*30/100 = 90
    expect(screen.getByTestId('hours-saved')).toHaveTextContent('90 hrs/week');
    // Change team size to 40 → 40*15*30/100 = 180
    fireEvent.change(getSlider('team-size-slider'), { target: { value: '40' } });
    expect(screen.getByTestId('hours-saved')).toHaveTextContent('180 hrs/week');
  });

  it('updating the efficiency gain updates the annual savings', () => {
    renderPage();
    // Defaults: team=20, hours=15, rate=150, eff=30 →
    //   hrs/wk = 90, annual hrs = 4680, annual$ = 702,000
    expect(screen.getByTestId('annual-savings')).toHaveTextContent('$702,000 AUD');
    // Raise efficiency to 60 → hrs/wk = 180, annual hrs = 9360, annual$ = 1,404,000
    fireEvent.change(getSlider('efficiency-slider'), { target: { value: '60' } });
    expect(screen.getByTestId('annual-savings')).toHaveTextContent(
      '$1,404,000 AUD',
    );
  });

  it('annual savings is formatted with dollar sign and comma separators', () => {
    renderPage();
    const annual = screen.getByTestId('annual-savings');
    // The default configuration yields a 6-digit number, so the formatting
    // must include at least one comma and a dollar sign.
    expect(annual.textContent).toMatch(/^\$[\d,]+ AUD$/);
    expect(annual.textContent).toContain(',');
  });

  it('renders the Book a scoping call CTA linking to /book', () => {
    renderPage();
    const bookLinks = screen.getAllByRole('link', {
      name: /Book a scoping call/i,
    });
    expect(
      bookLinks.some((link) => link.getAttribute('href') === '/book'),
    ).toBe(true);
  });
});
