/**
 * Smoke tests for the v2 ServiceDetail page. Exercises the dynamic-slug
 * route by wrapping the page in a wouter Router configured with an
 * in-memory location pointing at /services/{slug}. Asserts composition —
 * hero title, checklist, engagement stepstack, pricing block, FAQ — plus
 * the 404-style fallback when the slug doesn't match.
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { HelmetProvider } from 'react-helmet-async';
import { Route, Router, Switch } from 'wouter';
import { memoryLocation } from 'wouter/memory-location';
import ServiceDetail from './ServiceDetail';
import { SERVICES } from '@/lib/data';

function renderAt(path: string) {
  const { hook } = memoryLocation({ path, static: true });
  return render(
    <HelmetProvider>
      <Router hook={hook}>
        <Switch>
          <Route path="/services/:slug" component={ServiceDetail} />
          <Route component={ServiceDetail} />
        </Switch>
      </Router>
    </HelmetProvider>,
  );
}

const VALID_SLUG = SERVICES[0].slug; // 'ai-strategy-consulting'
const VALID_SERVICE = SERVICES[0];

describe('ServiceDetail page', () => {
  it('renders the service title as the hero h1 when the slug is valid', () => {
    renderAt(`/services/${VALID_SLUG}`);
    expect(
      screen.getByRole('heading', { level: 1, name: VALID_SERVICE.title }),
    ).toBeInTheDocument();
  });

  it("renders the 'What you'll get' checklist from service features", () => {
    renderAt(`/services/${VALID_SLUG}`);
    expect(
      screen.getByRole('heading', { level: 2, name: /Outcomes, not deliverables/i }),
    ).toBeInTheDocument();
    // Every feature in the service data lands on screen.
    for (const feature of VALID_SERVICE.features) {
      expect(screen.getByText(feature)).toBeInTheDocument();
    }
  });

  it('renders the engagement StepStack', () => {
    renderAt(`/services/${VALID_SLUG}`);
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: /Four phases\. Three weeks\. One artefact\./i,
      }),
    ).toBeInTheDocument();
    // At least one phase title lands as an h3.
    expect(
      screen.getByRole('heading', { level: 3, name: /Scoping call/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: /The work/i }),
    ).toBeInTheDocument();
  });

  it('renders the pricing block with Investment eyebrow and from-price', () => {
    renderAt(`/services/${VALID_SLUG}`);
    // Investment eyebrow
    expect(screen.getByText(/Investment/i)).toBeInTheDocument();
    // From-price heading for ai-strategy-consulting
    expect(
      screen.getByRole('heading', { level: 2, name: /From \$12,500 AUD/i }),
    ).toBeInTheDocument();
    // Custom quote note
    expect(screen.getByText(/Custom quote on scope/i)).toBeInTheDocument();
  });

  it('renders the FAQAccordion with service FAQs', () => {
    renderAt(`/services/${VALID_SLUG}`);
    // FAQ section heading
    expect(
      screen.getByRole('heading', {
        level: 2,
        name: /The questions we hear most/i,
      }),
    ).toBeInTheDocument();
    // Each FAQ question is rendered as a button label (accordion trigger).
    expect(screen.getByRole('button', { name: /Who is this for\?/i })).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /How long does it take\?/i }),
    ).toBeInTheDocument();
  });

  it('renders the back-link to /services', () => {
    renderAt(`/services/${VALID_SLUG}`);
    const backLink = screen.getByTestId('back-to-services');
    expect(backLink.getAttribute('href')).toBe('/services');
  });

  it('renders a 404-style fallback when the slug does not match', () => {
    renderAt('/services/this-service-does-not-exist');
    expect(
      screen.getByRole('heading', { level: 1, name: /Service not found/i }),
    ).toBeInTheDocument();
    // Link back to overview is present.
    const backLinks = screen.getAllByRole('link', { name: /Back to services/i });
    expect(
      backLinks.some((link) => link.getAttribute('href') === '/services'),
    ).toBe(true);
  });
});
