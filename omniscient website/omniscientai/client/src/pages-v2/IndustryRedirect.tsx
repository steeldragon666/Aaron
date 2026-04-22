/**
 * IndustryRedirect.tsx — redirect /industries/:slug → matching /services/:slug.
 *
 * The v2 pivot (2026-04-22 / -23) folded the standalone "industries" taxonomy
 * into the three Pillar 1 vertical-SaaS services. The Industries overview
 * page now links to /services/:slug (bioenergy, defence, mental-health), so
 * the legacy /industries/:slug deep links are orphaned.
 *
 * Rather than silently 404, this redirect preserves inbound links (search
 * engines, bookmarks, marketing assets) by mapping each legacy INDUSTRIES
 * slug to its closest current SERVICES slug, or falling through to the
 * services overview if there's no clean match.
 *
 * INDUSTRIES slugs (from lib/data.ts): professional-services, healthcare,
 * manufacturing, retail.
 *
 * Mapping choices:
 *   - healthcare       → /services/mental-health
 *     (Mental health is the first health-adjacent SaaS we ship.)
 *   - professional-services, manufacturing, retail → /services
 *     (No direct replacement yet. Overview is the least-surprising fallback
 *     and leaves room to expand the map if/when those verticals get a
 *     dedicated product line.)
 *
 * TODO: when new vertical SaaS products ship (e.g. a manufacturing-ops
 * product), extend SLUG_MAP so the deep link lands on the right service.
 */

import { useEffect } from 'react';
import { useLocation, useParams } from 'wouter';

// Legacy-slug → new-slug map. Keys are the original INDUSTRIES slugs in
// lib/data.ts; values are absolute paths under /services. Any slug not in
// this map falls through to the services overview. Kept narrow on purpose
// — we'd rather drop someone at the overview than send them to an unrelated
// product page.
const SLUG_MAP: Record<string, string> = {
  healthcare: '/services/mental-health',
  // health is a reasonable alias for the same verticals — not a current
  // INDUSTRIES slug, but defensive for any ad/marketing asset that linked
  // to /industries/health historically.
  health: '/services/mental-health',
  // TODO: add mappings for professional-services, manufacturing, and
  // retail once those verticals have dedicated services.
};

export default function IndustryRedirect() {
  const params = useParams<{ slug?: string }>();
  const [, navigate] = useLocation();

  useEffect(() => {
    const target =
      (params.slug && SLUG_MAP[params.slug]) ?? '/services';
    navigate(target, { replace: true });
  }, [params.slug, navigate]);

  // Render nothing while the navigate call runs. The redirect happens in a
  // useEffect (after mount) so this is intentionally a blank frame — the
  // next render cycle flips the location and the target page takes over.
  return null;
}
