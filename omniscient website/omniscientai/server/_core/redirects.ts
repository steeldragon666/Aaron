/**
 * 301 redirects for URLs removed during the v2 redesign.
 *
 * Cut from the v2 site:
 *   - /document-analyser  (novelty tool, low conversion)
 *   - /voice-consultant   (novelty tool, low conversion)
 *   - /playground         (dev/demo surface, not a conversion asset)
 *
 * 301 redirects preserve SEO equity for any organic traffic still
 * landing on these URLs. Must be registered BEFORE the Vite/static
 * middleware in index.ts so the SPA doesn't swallow them.
 */

import type { Express } from "express";

const REDIRECTS: Record<string, string> = {
  "/document-analyser": "/services",
  "/voice-consultant": "/services",
  "/playground": "/",
};

export function registerRedirects(app: Express): void {
  for (const [from, to] of Object.entries(REDIRECTS)) {
    app.get(from, (_req, res) => {
      res.redirect(301, to);
    });
  }
}
