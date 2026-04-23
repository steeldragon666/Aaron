import { render, screen, within } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Layout } from './Layout';

describe('Layout', () => {
  it('renders children inside main landmark', () => {
    render(
      <Layout>
        <div data-testid="child">Hello</div>
      </Layout>,
    );
    const main = screen.getByRole('main');
    expect(main).toBeInTheDocument();
    expect(within(main).getByTestId('child')).toBeInTheDocument();
  });

  it('renders nav by default', () => {
    render(<Layout>content</Layout>);
    // Nav's wordmark (also present in Footer, so presence is enough here).
    expect(screen.getAllByText('Omniscient AI').length).toBeGreaterThanOrEqual(1);
  });

  it('renders footer by default', () => {
    render(<Layout>content</Layout>);
    expect(screen.getByText(/© 2026 Omniscient AI/i)).toBeInTheDocument();
  });

  it('hides nav when hideNav is true', () => {
    render(<Layout hideNav>content</Layout>);
    // Wordmark still appears in Footer, but the Nav hamburger button should not.
    expect(screen.queryByRole('button', { name: /open menu/i })).not.toBeInTheDocument();
  });

  it('hides footer when hideFooter is true', () => {
    render(<Layout hideFooter>content</Layout>);
    expect(screen.queryByText(/© 2026 Omniscient AI/i)).not.toBeInTheDocument();
  });

  it('includes skip-to-content link', () => {
    render(<Layout>content</Layout>);
    expect(screen.getByRole('link', { name: /Skip to content/i })).toBeInTheDocument();
  });
});
