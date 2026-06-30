/**
 * LegacyRoutes.tsx
 *
 * The existing (pre-v2) 22 dark-theme routes, extracted verbatim from
 * App.tsx so the router can flag-switch between legacy and v2 surfaces.
 *
 * CustomCursor and AIOssistant live here — they are legacy-only decorations
 * that violate the v2 design system (no floating chat, no custom cursors)
 * and must NOT render inside the .v2 scope.
 *
 * Dropped entirely in the cleanup PR after the Phase 12 production flip
 * is stable.
 */

import { Route, Switch } from "wouter";
import Layout from "@/components/Layout";
import CustomCursor from "@/components/CustomCursor";
import AIOssistant from "@/components/AIOssistant";
import NotFound from "@/pages/NotFound";
import Home from "@/pages/Home";
import Workshops from "@/pages/Workshops";
import WorkshopDetail from "@/pages/WorkshopDetail";
import CustomWorkshop from "@/pages/CustomWorkshop";
import Services from "@/pages/Services";
import ServiceDetail from "@/pages/ServiceDetail";
import Industries from "@/pages/Industries";
import IndustryDetail from "@/pages/IndustryDetail";
import Insights from "@/pages/Insights";
import InsightArticle from "@/pages/InsightArticle";
import About from "@/pages/About";
import Approach from "@/pages/Approach";
import AIReadinessQuiz from "@/pages/AIReadinessQuiz";
import ROICalculator from "@/pages/ROICalculator";
import Book from "@/pages/Book";
import Contact from "@/pages/Contact";
import PrivacyPolicy from "@/pages/PrivacyPolicy";
import Terms from "@/pages/Terms";
import Playground from "@/pages/Playground";
import VoiceConsultant from "@/pages/VoiceConsultant";
import DocumentAnalyser from "@/pages/DocumentAnalyser";

export default function LegacyRoutes() {
  return (
    <>
      <CustomCursor />
      <Layout>
        <Switch>
          <Route path="/" component={Home} />
          <Route path="/workshops" component={Workshops} />
          <Route path="/workshops/custom" component={CustomWorkshop} />
          <Route path="/workshops/:slug" component={WorkshopDetail} />
          <Route path="/services" component={Services} />
          <Route path="/services/:slug" component={ServiceDetail} />
          <Route path="/industries" component={Industries} />
          <Route path="/industries/:slug" component={IndustryDetail} />
          <Route path="/insights" component={Insights} />
          <Route path="/insights/:slug" component={InsightArticle} />
          <Route path="/about" component={About} />
          <Route path="/about/approach" component={Approach} />
          <Route path="/ai-readiness-quiz" component={AIReadinessQuiz} />
          <Route path="/roi-calculator" component={ROICalculator} />
          <Route path="/playground" component={Playground} />
          <Route path="/voice-consultant" component={VoiceConsultant} />
          <Route path="/document-analyser" component={DocumentAnalyser} />
          <Route path="/book" component={Book} />
          <Route path="/contact" component={Contact} />
          <Route path="/privacy-policy" component={PrivacyPolicy} />
          <Route path="/terms" component={Terms} />
          <Route path="/404" component={NotFound} />
          <Route component={NotFound} />
        </Switch>
      </Layout>
      <AIOssistant />
    </>
  );
}
