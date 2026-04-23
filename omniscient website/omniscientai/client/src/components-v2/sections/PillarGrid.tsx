import type { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import { CTALink } from '@/components-v2/ui';
import { Card } from '@/components-v2/ui';
import { Section } from '@/components-v2/layout';

/**
 * PillarGrid — 4-up grid of practice areas / capabilities.
 *
 * Each pillar is a Card containing an icon, a heading, a short description,
 * and an optional "Learn more →" CTALink when an `href` is supplied. Used on
 * Home for the practice areas (Training / Health / Defense / Agentic Ops)
 * and reusable on Services for the full capability matrix.
 *
 * Layout: single column on mobile, 2-up at md, 4-up at lg.
 */

interface Pillar {
  icon: LucideIcon;
  title: string;
  description: string;
  /** If provided, renders a "Learn more" CTALink. */
  href?: string;
}

interface PillarGridProps {
  eyebrow?: string;
  sectionTitle?: string;
  lede?: string;
  pillars: Pillar[];
  className?: string;
}

export function PillarGrid({
  eyebrow,
  sectionTitle,
  lede,
  pillars,
  className,
}: PillarGridProps) {
  return (
    <Section
      eyebrow={eyebrow}
      title={sectionTitle}
      lede={lede}
      className={cn(className)}
    >
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        {pillars.map((pillar) => {
          const Icon = pillar.icon;
          return (
            <Card key={pillar.title} className="flex flex-col">
              {/* Blue pillar icons — 2026-04-23 style pass. Ink title/body
                  unchanged, only the icon mark shifts to --blue to give the
                  cards a bit more colour pop without breaking the design
                  system's ~10% blue proportion rule. */}
              <Icon className="h-8 w-8 text-blue" aria-hidden />
              <h3 className="mt-5 font-semibold text-[22px] leading-tight text-ink">
                {pillar.title}
              </h3>
              <p className="mt-3 text-ink-2">{pillar.description}</p>
              {pillar.href && (
                <CTALink href={pillar.href} className="mt-5 text-blue">
                  Learn more
                </CTALink>
              )}
            </Card>
          );
        })}
      </div>
    </Section>
  );
}
