import { cn } from '@/lib/utils';
import { Section, InkSection } from '@/components-v2/layout';

/**
 * StatsRow — 4-column row of big numbers + short labels.
 *
 * Used on Home for the "50+ workshops / 12 industries / 4.9/5 satisfaction /
 * 8hrs saved per week" summary. Renders inside a regular <Section> for
 * paper / paper-2 tones, or inside <InkSection> when tone="ink" to
 * provide a dramatic full-bleed pacing moment.
 *
 * Layout: 2 columns on mobile, 4 at md+.
 */

interface Stat {
  /** e.g. "50+", "12", "4.9/5", "8hrs" */
  value: string;
  /** e.g. "Workshops delivered" */
  label: string;
}

interface StatsRowProps {
  eyebrow?: string;
  sectionTitle?: string;
  /** Typically 3-4 stats. */
  stats: Stat[];
  /** Surface tone. Defaults to `paper`. */
  tone?: 'paper' | 'paper-2' | 'ink';
  className?: string;
}

const valueClass =
  'text-[56px] lg:text-[72px] font-bold tracking-[-0.02em] leading-none';

export function StatsRow({
  eyebrow,
  sectionTitle,
  stats,
  tone = 'paper',
  className,
}: StatsRowProps) {
  const grid = (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-8 items-start">
      {stats.map((stat) => (
        <div key={stat.label}>
          <div className={valueClass}>{stat.value}</div>
          <div
            className={cn(
              'mt-3 text-[14px] font-medium',
              tone === 'ink' ? 'text-paper/60' : 'text-ink-3',
            )}
          >
            {stat.label}
          </div>
        </div>
      ))}
    </div>
  );

  if (tone === 'ink') {
    return (
      <InkSection
        eyebrow={eyebrow}
        title={sectionTitle}
        className={cn(className)}
      >
        {grid}
      </InkSection>
    );
  }

  return (
    <Section
      tone={tone}
      eyebrow={eyebrow}
      title={sectionTitle}
      className={cn(className)}
    >
      {grid}
    </Section>
  );
}
