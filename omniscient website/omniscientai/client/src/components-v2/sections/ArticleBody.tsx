import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';
import { Section } from '@/components-v2/layout';

/**
 * ArticleBody — long-form content wrapper for Insights articles.
 *
 * Constrains the reading measure to 65ch for ideal line-length, and
 * applies the `.article-body` scoped typography utility defined in
 * omniscient.css. That utility styles nested h2/h3/p/ul/ol/blockquote
 * /code/pre/a/img/hr elements so downstream authors can write plain
 * JSX or markdown output without having to style each element.
 */

interface ArticleBodyProps {
  children: ReactNode;
  className?: string;
}

export function ArticleBody({ children, className }: ArticleBodyProps) {
  return (
    <Section tone="paper">
      <article className={cn('article-body mx-auto max-w-[65ch]', className)}>
        {children}
      </article>
    </Section>
  );
}
