import { cn } from '@/lib/utils';
import { Section } from '@/components-v2/layout';

/**
 * TestimonialStrip — horizontal row of 3 quotes.
 *
 * No star ratings by design — the v2 system rejects them as "too consumer".
 * Each testimonial is a decorative opening quote glyph, the quote body
 * (lede-like: 20px / 1.45), and an attribution block (name bold, role +
 * company in muted small type).
 *
 * Layout: single column on mobile, 3-up at md+.
 */

interface Testimonial {
  quote: string;
  name: string;
  /** e.g. "COO" */
  role: string;
  /** e.g. "Acme Health" */
  company: string;
}

interface TestimonialStripProps {
  eyebrow?: string;
  sectionTitle?: string;
  testimonials: Testimonial[];
  /** Surface tone. Defaults to `paper`. */
  tone?: 'paper' | 'paper-2';
  className?: string;
}

export function TestimonialStrip({
  eyebrow,
  sectionTitle,
  testimonials,
  tone = 'paper',
  className,
}: TestimonialStripProps) {
  return (
    <Section
      tone={tone}
      eyebrow={eyebrow}
      title={sectionTitle}
      className={cn(className)}
    >
      <div className="grid md:grid-cols-3 gap-8 lg:gap-12">
        {testimonials.map((t, idx) => (
          <figure key={idx} className="flex flex-col">
            <span
              aria-hidden
              className="block text-[48px] leading-none text-ink-300 mb-4 font-serif"
            >
              &ldquo;
            </span>
            <blockquote className="text-[20px] leading-[1.45] text-ink-2">
              {t.quote}
            </blockquote>
            <figcaption className="mt-6 text-[14px] leading-snug">
              <div className="font-semibold text-ink">{t.name}</div>
              <div className="mt-1 text-ink-3">
                {t.role}, {t.company}
              </div>
            </figcaption>
          </figure>
        ))}
      </div>
    </Section>
  );
}
