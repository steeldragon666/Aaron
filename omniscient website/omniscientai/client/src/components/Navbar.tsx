// Navbar — OmniscientAI Luminous Depth
// Glass-morphism nav with dropdown menus, mobile hamburger
import { useState, useEffect } from "react";
import { Link, useLocation } from "wouter";
import { NAV_LINKS } from "@/lib/data";
import { Menu, X, ChevronDown } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Logo from "./Logo";

export default function Navbar() {
  const [location] = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    setMobileOpen(false);
    setOpenDropdown(null);
  }, [location]);

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${scrolled
          ? "py-3 bg-[#050505]/80 backdrop-blur-2xl border-b border-white/5 shadow-2xl shadow-black/40"
          : "py-6 bg-transparent"
        }`}
    >
      <nav className="container flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="hover:opacity-90 transition-opacity">
          <Logo variant="minimal" />
        </Link>

        {/* Desktop Nav */}
        <div className="hidden lg:flex items-center gap-1 bg-white/5 backdrop-blur-md rounded-full px-2 py-1.5 border border-white/5">
          {NAV_LINKS.map((link) => {
            const isActive = location === link.href || (link.href !== "/" && location.startsWith(link.href));

            return (
              <div
                key={link.label}
                className="relative"
                onMouseEnter={() => link.children && setOpenDropdown(link.label)}
                onMouseLeave={() => setOpenDropdown(null)}
              >
                <Link
                  href={link.href}
                  className={`relative px-4 py-2 text-sm font-medium rounded-full transition-all duration-300 flex items-center gap-1.5 ${isActive
                      ? "text-white"
                      : "text-white/60 hover:text-white"
                    }`}
                >
                  {isActive && (
                    <motion.div
                      layoutId="nav-active"
                      className="absolute inset-0 bg-[#12B5CB]/10 rounded-full border border-[#12B5CB]/20"
                      transition={{ type: "spring", bounce: 0.25, duration: 0.5 }}
                    />
                  )}
                  <span className="relative z-10">{link.label}</span>
                  {link.children && <ChevronDown className={`w-3.5 h-3.5 transition-transform duration-300 ${openDropdown === link.label ? "rotate-180" : ""}`} />}
                </Link>

                {/* Dropdown */}
                {link.children && (
                  <AnimatePresence>
                    {openDropdown === link.label && (
                      <motion.div
                        initial={{ opacity: 0, y: 10, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 10, scale: 0.95 }}
                        transition={{ duration: 0.2, ease: "easeOut" }}
                        className="absolute top-full left-0 mt-3 w-64 p-2 rounded-2xl bg-[#0F0F0F]/95 backdrop-blur-2xl border border-white/10 shadow-2xl ring-1 ring-black/50"
                      >
                        {link.children.map((child) => (
                          <Link
                            key={child.href}
                            href={child.href}
                            className="group flex flex-col px-4 py-2.5 rounded-xl hover:bg-white/5 transition-all"
                          >
                            <span className="text-sm font-medium text-white/80 group-hover:text-[#12B5CB]">
                              {child.label}
                            </span>
                          </Link>
                        ))}
                      </motion.div>
                    )}
                  </AnimatePresence>
                )}
              </div>
            );
          })}
        </div>

        {/* Desktop CTAs */}
        <div className="hidden lg:flex items-center gap-4">
          <Link
            href="/ai-readiness-quiz"
            className="text-sm font-semibold text-[#12B5CB] hover:text-[#12B5CB]/80 transition-colors"
          >
            AI Quiz
          </Link>
          <Link
            href="/book"
            className="px-6 py-2.5 text-sm font-bold text-[#052A30] bg-[#12B5CB] rounded-full hover:bg-[#12B5CB]/90 transition-all shadow-lg shadow-[#12B5CB]/20 hover:shadow-[#12B5CB]/40 active:scale-95 btn-premium"
          >
            Book Now
          </Link>
        </div>

        {/* Mobile toggle */}
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="lg:hidden p-2.5 rounded-xl bg-white/5 border border-white/10 text-white/80 hover:text-white"
          aria-label="Toggle menu"
        >
          {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </nav>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="lg:hidden bg-[#050505] border-t border-white/5 overflow-hidden"
          >
            <div className="container py-8 space-y-6">
              {NAV_LINKS.map((link) => (
                <div key={link.label} className="space-y-4">
                  <Link
                    href={link.href}
                    className="block text-2xl font-bold text-white hover:text-[#12B5CB] transition-colors"
                  >
                    {link.label}
                  </Link>
                  {link.children && (
                    <div className="flex flex-wrap gap-3 pl-2">
                      {link.children.map((child) => (
                        <Link
                          key={child.href}
                          href={child.href}
                          className="px-3 py-1.5 rounded-full bg-white/5 border border-white/5 text-sm text-white/50 hover:text-[#12B5CB] transition-all"
                        >
                          {child.label}
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              <div className="pt-8 flex flex-col gap-4 border-t border-white/5">
                <Link
                  href="/book"
                  className="w-full py-4 text-center text-lg font-bold text-[#052A30] bg-[#12B5CB] rounded-2xl shadow-xl shadow-[#12B5CB]/20"
                >
                  Book a Session
                </Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
