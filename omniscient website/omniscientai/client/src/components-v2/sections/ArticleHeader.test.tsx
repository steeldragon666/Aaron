import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ArticleHeader } from './ArticleHeader';

describe('ArticleHeader', () => {
  const baseProps = {
    category: 'Field notes',
    title: 'Why we don’t recommend starting with a chatbot',
    author: 'Aaron',
    publishDate: '22 April 2026',
    readTime: '7 min read',
  };

  it('renders the category as an eyebrow', () => {
    render(<ArticleHeader {...baseProps} />);
    expect(screen.getByText('Field notes')).toBeInTheDocument();
  });

  it('renders the title as an h1', () => {
    render(<ArticleHeader {...baseProps} />);
    expect(
      screen.getByRole('heading', { level: 1, name: /starting with a chatbot/i }),
    ).toBeInTheDocument();
  });

  it('renders the lede when provided', () => {
    render(<ArticleHeader {...baseProps} lede="A short summary paragraph." />);
    expect(screen.getByText('A short summary paragraph.')).toBeInTheDocument();
  });

  it('does not render a lede element when no lede prop is provided', () => {
    const { container } = render(<ArticleHeader {...baseProps} />);
    expect(container.querySelector('.lede')).toBeNull();
  });

  it('renders author, publishDate, and readTime metadata', () => {
    render(<ArticleHeader {...baseProps} />);
    expect(screen.getByText('Aaron')).toBeInTheDocument();
    expect(screen.getByText('22 April 2026')).toBeInTheDocument();
    expect(screen.getByText('7 min read')).toBeInTheDocument();
  });

  it('passes className through to the wrapping section', () => {
    const { container } = render(
      <ArticleHeader {...baseProps} className="custom-header" />,
    );
    expect(container.querySelector('section.custom-header')).not.toBeNull();
  });

  it('renders ReactNode titles (e.g. with inline emphasis)', () => {
    render(
      <ArticleHeader
        {...baseProps}
        title={
          <>
            Why we <em>don’t</em> recommend chatbots
          </>
        }
      />,
    );
    const h1 = screen.getByRole('heading', { level: 1 });
    expect(h1.textContent).toContain('don’t');
    expect(h1.querySelector('em')).not.toBeNull();
  });
});
