// Layout — OmniscientAI Luminous Depth design
// Wraps all pages with Navbar + Footer + Background Visuals
import { ReactNode } from "react";
import Navbar from "./Navbar";
import Footer from "./Footer";
import GenerativeNeuralMesh from "./GenerativeNeuralMesh";

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col bg-[#050505] text-[#E8E8E8]">
      <a href="#main-content" className="skip-to-content">
        Skip to main content
      </a>
      <GenerativeNeuralMesh />
      <Navbar />
      <main id="main-content" className="flex-1 relative z-10">{children}</main>
      <Footer />
    </div>
  );
}
