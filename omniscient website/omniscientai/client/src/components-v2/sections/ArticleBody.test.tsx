import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ArticleBody } from './ArticleBody';

describe('ArticleBody', () => {
  it('renders children inside an <article> element', () => {
    const { container } = render(
      <ArticleBody>
        <p>Hello world</p>
      </ArticleBody>,
    );
    const article = container.querySelector('article');
    expect(article).not.toBeNull();
    expect(article?.textContent).toContain('Hello world');
  });

  it('applies the article-body class for scoped typography styles', () => {
    const { container } = render(
      <ArticleBody>
        <p>content</p>
      </ArticleBody>,
    );
    expect(container.querySelector('article.article-body')).not.toBeNull();
  });

  it('applies a max-width constraint for ideal reading line-length', () => {
    const { container } = render(
      <ArticleBody>
        <p>content</p>
      </ArticleBody>,
    );
    const article = container.querySelector('article');
    expect(article?.className).toMatch(/max-w-\[65ch\]/);
  });

  it('passes className through to the <article> element', () => {
    const { container } = render(
      <ArticleBody className="custom-body">
        <p>content</p>
      </ArticleBody>,
    );
    expect(container.querySelector('article.custom-body')).not.toBeNull();
  });

  it('renders nested headings and paragraphs without issue', () => {
    render(
      <ArticleBody>
        <h2>Section heading</h2>
        <p>Paragraph body</p>
        <h3>Subheading</h3>
      </ArticleBody>,
    );
    expect(
      screen.getByRole('heading', { level: 2, name: /Section heading/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: /Subheading/i }),
    ).toBeInTheDocument();
    expect(screen.getByText('Paragraph body')).toBeInTheDocument();
  });

  it('wraps the article in a paper-toned Section', () => {
    const { container } = render(
      <ArticleBody>
        <p>content</p>
      </ArticleBody>,
    );
    const section = container.querySelector('section');
    expect(section).not.toBeNull();
    expect(section?.className).toMatch(/bg-paper/);
  });
});
