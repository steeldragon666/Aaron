import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Route, useLocation } from "wouter";
import { HelmetProvider } from "react-helmet-async";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import { USE_V2 } from "@/lib/theme-v2";
import V2Routes from "@/pages-v2/V2Routes";
import LegacyRoutes from "@/pages-v2/LegacyRoutes";

const IS_DEV = import.meta.env.DEV;

function AppRouter() {
  const [location] = useLocation();

  // Production flip or dev preview routed to /_v2 → v2 surface only.
  // Otherwise legacy. Critical: we do NOT render LegacyRoutes alongside
  // the v2 preview — LegacyRoutes' catchall NotFound would double-render
  // on top of the v2 content.
  if (USE_V2) {
    return <V2Routes />;
  }

  if (IS_DEV && location.startsWith("/_v2")) {
    return (
      <Route path="/_v2" nest>
        <V2Routes />
      </Route>
    );
  }

  return <LegacyRoutes />;
}

function App() {
  return (
    <HelmetProvider>
      <ErrorBoundary>
        <ThemeProvider defaultTheme="dark">
          <TooltipProvider>
            <div className="relative">
              <AppRouter />
              <Toaster position="top-center" richColors />
            </div>
          </TooltipProvider>
        </ThemeProvider>
      </ErrorBoundary>
    </HelmetProvider>
  );
}

export default App;
