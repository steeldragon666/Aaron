import { useState, type ReactNode } from 'react';
import { Plus, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Section } from '@/components-v2/layout';

/**
 * FAQAccordion — vertical accordion of Q&A rows.
 *
 * Single-open behaviour: only one item is expanded at a time. Used on
 * Workshop Detail, Service Detail, and selectively on Home.
 *
 * Each row is a native `<button>` toggling an adjacent answer panel so
 * Enter/Space keyboard activation is free. Hairline borders top+bottom on
 * the item list, with an additional top-border between items. `+`/`−`
 * icons on the right reflect the open/closed state.
 */

interface FAQItem {
  q: string;
  a: ReactNode;
}

interface FAQAccordionProps {
  eyebrow?: string;
  sectionTitle?: string;
  items: FAQItem[];
  className?: string;
}

export function FAQAccordion({
  eyebrow,
  sectionTitle,
  items,
  className,
}: FAQAccordionProps) {
  const [open, setOpen] = useState<number | null>(null);

  return (
    <Section
      eyebrow={eyebrow}
      title={sectionTitle}
      className={cn(className)}
    >
      <div className="border-b border-line">
        {items.map((item, i) => {
          const isOpen = open === i;
          const panelId = `faq-panel-${i}`;
          const buttonId = `faq-button-${i}`;
          const Icon = isOpen ? Minus : Plus;

          return (
            <div key={i} className="border-t border-line">
              <button
                id={buttonId}
                type="button"
                aria-expanded={isOpen}
                aria-controls={panelId}
                onClick={() => setOpen(isOpen ? null : i)}
                className={cn(
                  'flex w-full items-center justify-between gap-6 py-6 text-left',
                  'transition-colors duration-[120ms] ease-[cubic-bezier(0.2,0.9,0.2,1)]',
                  'hover:text-blue',
                  'focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2',
                  'cursor-pointer',
                )}
              >
                <span className="font-semibold text-[18px] leading-tight text-ink">
                  {item.q}
                </span>
                <Icon className="h-5 w-5 shrink-0 text-ink" aria-hidden />
              </button>
              {isOpen && (
                <div
                  id={panelId}
                  role="region"
                  aria-labelledby={buttonId}
                  className="pb-6 text-ink-2 text-[17px] leading-relaxed"
                >
                  {item.a}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </Section>
  );
}
