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
import ServiceDetail from "./ServiceDetail";
import CompanionDetail from "./CompanionDetail";
import Industries from "./Industries";
import IndustryRedirect from "./IndustryRedirect";
import Workshops from "./Workshops";
import WorkshopDetail from "./WorkshopDetail";
import About from "./About";
import Approach from "./Approach";
import Contact from "./Contact";
import Book from "./Book";
import CustomWorkshop from "./CustomWorkshop";
import Insights from "./Insights";
import InsightArticle from "./InsightArticle";
import AIReadinessQuiz from "./AIReadinessQuiz";
import ROICalculator from "./ROICalculator";
import PrivacyPolicy from "./PrivacyPolicy";
import Terms from "./Terms";
import NotFound from "./NotFound";

const IS_DEV = import.meta.env.DEV;

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
        {/* Companion gets a bespoke detail page — must match before the
            generic /services/:slug route below. */}
        <Route path="/services/companion" component={CompanionDetail} />
        <Route path="/services/:slug" component={ServiceDetail} />
        <Route path="/industries" component={Industries} />
        {/* Legacy /industries/:slug deep links redirect to the matching
            /services/:slug product page (or the services overview if the
            slug doesn't map). The old IndustryDetail template is retired;
            industries are folded into Pillar 1 vertical SaaS. */}
        <Route path="/industries/:slug" component={IndustryRedirect} />
        <Route path="/workshops" component={Workshops} />
        {/* /workshops/custom must be matched before /workshops/:slug so
            the dynamic route doesn't swallow it. */}
        <Route path="/workshops/custom" component={CustomWorkshop} />
        <Route path="/workshops/:slug" component={WorkshopDetail} />
        <Route path="/about" component={About} />
        <Route path="/about/approach" component={Approach} />
        <Route path="/contact" component={Contact} />
        <Route path="/book" component={Book} />
        <Route path="/insights" component={Insights} />
        <Route path="/insights/:slug" component={InsightArticle} />
        <Route path="/ai-readiness-quiz" component={AIReadinessQuiz} />
        <Route path="/roi-calculator" component={ROICalculator} />
        <Route path="/privacy-policy" component={PrivacyPolicy} />
        <Route path="/terms" component={Terms} />
        {/* Catchall — NotFound replaces the prior V2Placeholder stand-in. */}
        <Route component={NotFound} />
      </Switch>
    </div>
  );
}
