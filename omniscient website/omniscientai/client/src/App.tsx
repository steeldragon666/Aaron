import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Route } from "wouter";
import { HelmetProvider } from "react-helmet-async";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import { USE_V2 } from "@/lib/theme-v2";
import V2Routes from "@/pages-v2/V2Routes";
import LegacyRoutes from "@/pages-v2/LegacyRoutes";

const IS_DEV = import.meta.env.DEV;

function App() {
  return (
    <HelmetProvider>
      <ErrorBoundary>
        <ThemeProvider defaultTheme="dark">
          <TooltipProvider>
            <div className="relative">
              {USE_V2 ? (
                <V2Routes />
              ) : (
                <>
                  <LegacyRoutes />
                  {IS_DEV && (
                    // Dev-only preview: wouter's `nest` prop matches any
                    // path starting with /_v2 and strips that prefix from
                    // the inner routing context, so V2Routes' internal
                    // Switch matches /_v2/_tokens against `/_tokens`.
                    <Route path="/_v2" nest>
                      <V2Routes />
                    </Route>
                  )}
                </>
              )}
              <Toaster position="top-center" richColors />
            </div>
          </TooltipProvider>
        </ThemeProvider>
      </ErrorBoundary>
    </HelmetProvider>
  );
}

export default App;
