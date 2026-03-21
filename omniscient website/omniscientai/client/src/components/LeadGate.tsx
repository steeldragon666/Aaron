import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mail, User, Building2, ArrowRight, Sparkles, Shield } from "lucide-react";
import { trpc } from "@/lib/trpc";

type LeadGateProps = {
  toolName: string;
  toolDescription: string;
  icon: React.ReactNode;
  children: React.ReactNode;
};

const STORAGE_KEY = "omniscientai_lead";

function getStoredLead(): { email: string; name: string; company: string } | null {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return JSON.parse(stored);
  } catch {}
  return null;
}

export default function LeadGate({ toolName, toolDescription, icon, children }: LeadGateProps) {
  const storedLead = getStoredLead();
  const [unlocked, setUnlocked] = useState(!!storedLead);
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [company, setCompany] = useState("");
  const [error, setError] = useState("");

  const captureMutation = trpc.leads.capture.useMutation({
    onSuccess: () => {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ email, name, company }));
      setUnlocked(true);
    },
    onError: (err) => {
      setError(err.message || "Something went wrong. Please try again.");
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!email || !name || !company) {
      setError("All fields are required.");
      return;
    }
    captureMutation.mutate({ email, name, company, toolUsed: toolName });
  };

  if (unlocked) {
    return <>{children}</>;
  }

  return (
    <div className="min-h-[70vh] flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-lg"
      >
        {/* Glass card */}
        <div className="glass-card rounded-3xl p-8 md:p-10 relative overflow-hidden">
          {/* Glow */}
          <div className="absolute -top-20 -right-20 w-60 h-60 bg-[#12B5CB]/10 rounded-full blur-[80px] pointer-events-none" />

          {/* Icon */}
          <div className="flex items-center justify-center w-16 h-16 rounded-2xl bg-[#12B5CB]/10 border border-[#12B5CB]/20 mb-6 mx-auto">
            {icon}
          </div>

          <h2
            className="text-2xl md:text-3xl font-bold text-[#E8E8E8] text-center mb-2"
            style={{ fontFamily: "var(--font-heading)" }}
          >
            Unlock {toolName}
          </h2>
          <p className="text-sm text-white/60 text-center mb-8 max-w-sm mx-auto leading-relaxed">
            {toolDescription}
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Name */}
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/60" />
              <input
                type="text"
                placeholder="Your name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-[#1A1A1A] border border-[#333333] rounded-xl text-sm text-[#E8E8E8] placeholder-[#666666] focus:outline-none focus:border-[#12B5CB]/50 focus:ring-1 focus:ring-[#12B5CB]/20 transition-all"
              />
            </div>

            {/* Email */}
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/60" />
              <input
                type="email"
                placeholder="Work email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-[#1A1A1A] border border-[#333333] rounded-xl text-sm text-[#E8E8E8] placeholder-[#666666] focus:outline-none focus:border-[#12B5CB]/50 focus:ring-1 focus:ring-[#12B5CB]/20 transition-all"
              />
            </div>

            {/* Company */}
            <div className="relative">
              <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/60" />
              <input
                type="text"
                placeholder="Company name"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-[#1A1A1A] border border-[#333333] rounded-xl text-sm text-[#E8E8E8] placeholder-[#666666] focus:outline-none focus:border-[#12B5CB]/50 focus:ring-1 focus:ring-[#12B5CB]/20 transition-all"
              />
            </div>

            <AnimatePresence>
              {error && (
                <motion.p
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="text-xs text-red-400 text-center"
                >
                  {error}
                </motion.p>
              )}
            </AnimatePresence>

            <button
              type="submit"
              disabled={captureMutation.isPending}
              className="w-full flex items-center justify-center gap-2 px-6 py-3.5 text-sm font-semibold text-[#0A0A0A] bg-[#12B5CB] rounded-xl hover:bg-[#12B5CB]/90 transition-all hover:shadow-lg hover:shadow-[#12B5CB]/20 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {captureMutation.isPending ? (
                <>
                  <div className="w-4 h-4 border-2 border-[#0A0A0A]/30 border-t-[#0A0A0A] rounded-full animate-spin" />
                  Unlocking...
                </>
              ) : (
                <>
                  Get Free Access <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Trust signals */}
          <div className="flex items-center justify-center gap-4 mt-6 text-xs text-[#666666]">
            <span className="flex items-center gap-1">
              <Shield className="w-3 h-3" /> No spam, ever
            </span>
            <span className="flex items-center gap-1">
              <Sparkles className="w-3 h-3" /> Free to use
            </span>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
