import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';
import { Section } from '@/components-v2/layout';
import { Display, Eyebrow, Lede, MonoBadge } from '@/components-v2/ui';

/**
 * ArticleHeader — top-of-article block for long-form Insights pages.
 *
 * Narrower than the standard Section (max-w-[800px]) to keep the Display
 * heading at a readable measure. Left-aligned, which reads more editorial
 * than centered. Metadata (author · date · read time) renders as individual
 * MonoBadge chips joined by middot separators.
 */

interface ArticleHeaderProps {
  category: string;
  title: ReactNode;
  lede?: ReactNode;
  author: string;
  publishDate: string;
  readTime: string;
  className?: string;
}

export function ArticleHeader({
  category,
  title,
  lede,
  author,
  publishDate,
  readTime,
  className,
}: ArticleHeaderProps) {
  return (
    <Section className={cn(className)}>
      <div className="max-w-[800px]">
        <Eyebrow className="mb-4 block">{category}</Eyebrow>
        <Display as="h1">{title}</Display>
        {lede && <Lede className="mt-6">{lede}</Lede>}
        <div className="mt-8 flex flex-wrap items-center gap-x-3 gap-y-2">
          <MonoBadge>{author}</MonoBadge>
          <span aria-hidden className="text-ink-3">
            ·
          </span>
          <MonoBadge>{publishDate}</MonoBadge>
          <span aria-hidden className="text-ink-3">
            ·
          </span>
          <MonoBadge>{readTime}</MonoBadge>
        </div>
      </div>
    </Section>
  );
}
