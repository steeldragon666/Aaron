/**
 * v2 redesign scope helpers.
 *
 * Usage:
 *   - USE_V2: router flag. Production flips to true at cutover (Phase 12).
 *   - V2_SCOPE_CLASS: the class name applied to the v2 root element so
 *     scoped tokens in omniscient.css resolve correctly.
 *   - withV2Scope(): compose the scope class with additional classes.
 *
 * All v2 pages are wrapped by <Layout> in components-v2/layout/Layout.tsx,
 * which applies this class once at the v2 router root.
 */

export const USE_V2 = import.meta.env.VITE_USE_V2 === 'true';

export const V2_SCOPE_CLASS = 'v2';

export function withV2Scope(className?: string): string {
  return [V2_SCOPE_CLASS, className].filter(Boolean).join(' ');
}
