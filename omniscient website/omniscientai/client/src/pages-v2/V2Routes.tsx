/**
 * V2Routes.tsx
 *
 * Router for the v2 redesign surface. Wrapped in the `.v2` scope class
 * (via `withV2Scope()`) so scoped tokens in omniscient.css resolve.
 *
 * CustomCursor and AIOssistant are intentionally absent — the v2 design
 * system forbids floating chat widgets and custom cursors.
 *
 * Real page routes land in Phase 7+. `/_showcase` is a dev-only visual
 * regression surface for the whole design system. `/_tokens` is kept as
 * a legacy alias pointing at the same page.
 *
 * Mounted two ways:
 *   1. Production (Phase 12): App.tsx renders <V2Routes /> at the app root
 *      when USE_V2 is true — routes match against the absolute URL.
 *   2. Dev preview: App.tsx nests <V2Routes /> under <Route path="/_v2" nest>
 *      so developers can browse the v2 surface at /_v2/* while legacy is
 *      still the default. Wouter's `nest` prop strips the /_v2 prefix before
 *      the inner Switch sees the location, so the SAME Switch below works
 *      in both modes.
 */

import { Route, Switch } from "wouter";
import { withV2Scope } from "@/lib/theme-v2";
import ComponentShowcase from "./ComponentShowcase";
import Home from "./Home";
import Services from "./Services";
import Industries from "./Industries";
import Workshops from "./Workshops";

const IS_DEV = import.meta.env.DEV;

function V2Placeholder() {
  return (
    <main className="min-h-screen grid place-items-center bg-paper text-ink">
      <div className="max-w-md text-center px-6">
        <div className="eyebrow mb-4">v2 redesign</div>
        <h1 className="display mb-4">Coming soon</h1>
        <p className="lede">
          This route hasn&apos;t been built in the v2 design yet. Real pages
          land in Phase 7. Visit{" "}
          <a href="/_v2/_showcase" className="underline">
            /_v2/_showcase
          </a>{" "}
          to see the design system.
        </p>
      </div>
    </main>
  );
}

export default function V2Routes() {
  return (
    <div className={withV2Scope("min-h-screen")}>
      <Switch>
        {IS_DEV && (
          <Route path="/_showcase" component={ComponentShowcase} />
        )}
        {IS_DEV && (
          // Legacy alias — early links pointed at /_tokens
          <Route path="/_tokens" component={ComponentShowcase} />
        )}
        {/* Phase 7+ routes land here */}
        <Route path="/" component={Home} />
        <Route path="/services" component={Services} />
        <Route path="/industries" component={Industries} />
        <Route path="/workshops" component={Workshops} />
        <Route component={V2Placeholder} />
      </Switch>
    </div>
  );
}
