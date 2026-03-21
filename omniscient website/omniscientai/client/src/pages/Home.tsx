// Homepage — OmniscientAI Phase 5 High-End Refresh
import { Link } from "wouter";
import { motion, useScroll, useTransform, useReducedMotion } from "framer-motion";
import { useRef } from "react";
import { ArrowRight, ChevronRight, Zap, Cpu, Shield, Globe } from "lucide-react";
import TechPartners from "@/components/TechPartners";
import SEO from "@/components/SEO";

const AICore = () => {
  const prefersReducedMotion = useReducedMotion();

  if (prefersReducedMotion) {
    return (
      <div className="relative w-full h-full flex items-center justify-center">
        {[...Array(3)].map((_, i) => (
          <div
            key={i}
            className="absolute rounded-full border border-[#12B5CB]/20"
            style={{ width: `${300 + i * 150}px`, height: `${300 + i * 150}px` }}
          />
        ))}
        <div className="relative w-48 h-48 rounded-full bg-black border border-[#12B5CB]/40 flex items-center justify-center overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_#12B5CB44_0%,_transparent_70%)]" />
          <Cpu className="w-16 h-16 text-[#12B5CB] relative z-10" />
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full flex items-center justify-center">
      {[...Array(3)].map((_, i) => (
        <motion.div
          key={i}
          animate={{ rotate: 360, scale: [1, 1.05, 1] }}
          transition={{
            rotate: { duration: 20 + i * 5, repeat: Infinity, ease: "linear" },
            scale: { duration: 4, repeat: Infinity, ease: "easeInOut" },
          }}
          className="absolute rounded-full border border-[#12B5CB]/20"
          style={{ width: `${300 + i * 150}px`, height: `${300 + i * 150}px` }}
        />
      ))}

      <motion.div
        animate={{
          boxShadow: [
            "0 0 20px rgba(18, 181, 203, 0.2)",
            "0 0 60px rgba(18, 181, 203, 0.5)",
            "0 0 20px rgba(18, 181, 203, 0.2)",
          ],
        }}
        transition={{ duration: 4, repeat: Infinity }}
        className="relative w-48 h-48 rounded-full bg-black border border-[#12B5CB]/40 flex items-center justify-center overflow-hidden"
      >
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_#12B5CB44_0%,_transparent_70%)]" />
        <Cpu className="w-16 h-16 text-[#12B5CB] relative z-10" />
        <motion.div
          animate={{ opacity: [0.1, 0.3, 0.1] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="absolute inset-0 flex items-center justify-center"
        >
          <div className="w-32 h-32 rounded-full border-t-2 border-[#12B5CB] animate-spin" />
        </motion.div>
      </motion.div>

      {[...Array(8)].map((_, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0 }}
          animate={{
            opacity: [0, 1, 0],
            x: [0, Math.cos(i * 45 * (Math.PI / 180)) * 400],
            y: [0, Math.sin(i * 45 * (Math.PI / 180)) * 400],
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            repeat: Infinity,
            delay: i * 0.5,
          }}
          className="absolute w-1 h-1 bg-[#12B5CB] rounded-full blur-[1px]"
        />
      ))}
    </div>
  );
};

const DataStreamText = ({ text }: { text: string }) => {
  const prefersReducedMotion = useReducedMotion();
  const words = text.split(" ");

  if (prefersReducedMotion) {
    return <span>{text}</span>;
  }

  return (
    <span className="inline">
      {words.map((word, i) => (
        <motion.span
          key={i}
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            duration: 0.8,
            delay: 0.5 + i * 0.05,
            ease: [0.215, 0.61, 0.355, 1],
          }}
          className="inline-block mr-[0.5ch]"
        >
          {word}
        </motion.span>
      ))}
    </span>
  );
};

const structuredData = {
  "@context": "https://schema.org",
  "@type": "ConsultingBusiness",
  "name": "OmniscientAI",
  "description": "Vendor-neutral AI training and consulting for Melbourne SMEs.",
  "url": "https://omniscientai.io",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Melbourne",
    "addressRegion": "VIC",
    "addressCountry": "AU"
  }
};

export default function Home() {
  const heroRef = useRef(null);
  const prefersReducedMotion = useReducedMotion();
  const { scrollYProgress } = useScroll({
    target: heroRef,
    offset: ["start start", "end start"],
  });

  const contentY = useTransform(scrollYProgress, [0, 1], [0, prefersReducedMotion ? 0 : -50]);
  const contentOpacity = useTransform(scrollYProgress, [0, 0.5], [1, prefersReducedMotion ? 1 : 0]);

  return (
    <>
      <SEO
        title="Melbourne's Vendor-Neutral AI Training for SMEs"
        description="Transform your team with practical AI skills. Vendor-neutral workshops and strategic consulting for Melbourne SMEs."
      />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }} />

      {/* Hero */}
      <section ref={heroRef} className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20">
        <div className="absolute inset-0 z-0">
          <AICore />
        </div>

        <div className="container relative z-10">
          <motion.div
            style={{ y: contentY, opacity: contentOpacity }}
            className="max-w-4xl mx-auto text-center"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 1, ease: "easeOut" }}
              className="mb-10 flex justify-center"
            >
              <div className="px-5 py-2 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-2xl flex items-center gap-3">
                <div className="flex -space-x-2">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="w-6 h-6 rounded-full bg-[#12B5CB] border-2 border-black flex items-center justify-center">
                      <Zap className="w-3 h-3 text-black" />
                    </div>
                  ))}
                </div>
                <span className="text-[11px] font-bold text-white/70 uppercase tracking-[0.2em]" style={{ fontFamily: "var(--font-mono)" }}>
                  Strategic AI Orchestration
                </span>
              </div>
            </motion.div>

            <h1 className="text-5xl md:text-8xl font-black text-white leading-[0.9] tracking-tighter mb-10 overflow-hidden" style={{ fontFamily: "var(--font-heading)" }}>
              <DataStreamText text="Intelligence that transforms." />
            </h1>

            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 1.5, delay: 1.2 }}
              className="text-xl md:text-2xl text-white/70 leading-relaxed mb-14 max-w-2xl mx-auto font-medium"
            >
              We don't just teach AI; we architect <span className="text-[#12B5CB]">cognitive operations</span> for Melbourne's most ambitious SMEs.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 1.5 }}
              className="flex flex-wrap items-center justify-center gap-6"
            >
              <Link
                href="/book"
                className="group relative px-10 py-5 bg-[#12B5CB] text-black font-black rounded-3xl overflow-hidden hover:scale-105 transition-all shadow-2xl shadow-[#12B5CB]/30 cursor-pointer"
              >
                <span className="relative z-10 flex items-center gap-2">
                  Initiate Audit <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                </span>
                <div className="absolute inset-0 bg-white translate-x-[-100%] group-hover:translate-x-0 transition-transform duration-500 opacity-20" />
              </Link>
              <Link
                href="/workshops"
                className="px-10 py-5 bg-white/5 border border-white/10 text-white font-bold rounded-3xl hover:bg-white/10 backdrop-blur-md transition-all flex items-center gap-2 cursor-pointer"
              >
                Explore Systems <ChevronRight className="w-5 h-5 text-[#12B5CB]" />
              </Link>
            </motion.div>
          </motion.div>
        </div>

        {/* Floating Data Nodes — only render on desktop */}
        <div className="absolute bottom-20 left-10 hidden lg:block">
          <motion.div
            animate={prefersReducedMotion ? {} : { y: [-10, 10, -10] }}
            transition={{ duration: 4, repeat: Infinity }}
            className="glass-card p-4 rounded-2xl border border-white/5 flex items-center gap-4"
          >
            <div className="w-10 h-10 rounded-xl bg-[#12B5CB]/10 flex items-center justify-center">
              <Shield className="w-5 h-5 text-[#12B5CB]" />
            </div>
            <div>
              <p className="text-[10px] font-bold text-[#12B5CB] uppercase">Governance</p>
              <p className="text-xs text-white/60">Secure by design.</p>
            </div>
          </motion.div>
        </div>

        <div className="absolute top-40 right-10 hidden lg:block">
          <motion.div
            animate={prefersReducedMotion ? {} : { y: [10, -10, 10] }}
            transition={{ duration: 5, repeat: Infinity }}
            className="glass-card p-4 rounded-2xl border border-white/5 flex items-center gap-4"
          >
            <div className="w-10 h-10 rounded-xl bg-purple-500/10 flex items-center justify-center">
              <Globe className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <p className="text-[10px] font-bold text-purple-400 uppercase">Scale</p>
              <p className="text-xs text-white/60">Global patterns.</p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Tech Partners */}
      <TechPartners />

      {/* Stats & Metrics */}
      <section className="section-padding bg-black relative">
        <div className="container">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-24 items-center">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <span className="text-[#12B5CB] text-[10px] font-bold uppercase tracking-[0.4em] mb-6 block">The Benchmarks</span>
              <h2 className="text-4xl md:text-6xl font-bold text-white mb-8" style={{ fontFamily: "var(--font-heading)" }}>
                Quantifying <span className="text-[#12B5CB]">Impact.</span>
              </h2>
              <div className="space-y-12">
                {[
                  { label: "Internal Efficiency", value: "+42%", desc: "Average increase in task automation for SMEs." },
                  { label: "Skill Maturity", value: "3.5x", desc: "Growth in team AI confidence post-workshop." },
                  { label: "Strategic Clarity", value: "100%", desc: "Clients leave with a documented AI roadmap." },
                ].map((stat, i) => (
                  <div key={i} className="relative pl-8">
                    <div className="absolute left-0 top-0 bottom-0 w-[2px] bg-gradient-to-b from-[#12B5CB] to-transparent" />
                    <div className="flex items-baseline gap-4 mb-2">
                      <span className="text-4xl font-black text-white">{stat.value}</span>
                      <span className="text-xs font-bold uppercase text-[#12B5CB] tracking-widest">{stat.label}</span>
                    </div>
                    <p className="text-white/60 text-sm leading-relaxed">{stat.desc}</p>
                  </div>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              className="relative aspect-square"
            >
              <div className="absolute inset-0 bg-[#12B5CB]/10 blur-[100px] rounded-full" />
              <div className="relative h-full w-full glass-card rounded-[3rem] overflow-hidden border border-white/5">
                <img
                  src="https://d2xsxph8kpxj0f.cloudfront.net/310419663026972742/it6qHcTHLu2dmqyuKKnamM/ai-brain-dmFjeh4UoufhTZyDTgkXjM.webp"
                  alt="AI brain visualization representing strategic AI consulting"
                  width={800}
                  height={800}
                  loading="lazy"
                  className="w-full h-full object-cover opacity-50 grayscale hover:grayscale-0 transition-all duration-1000"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent" />
                <div className="absolute bottom-10 left-10 p-10">
                  <Cpu className="w-12 h-12 text-[#12B5CB] mb-6" />
                  <p className="text-2xl font-bold text-white mb-2">Real-world Application</p>
                  <p className="text-white/60">Bridging the gap between theory and execution.</p>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Final Call to Action */}
      <section className="py-32 relative text-center">
        <div className="container relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="max-w-4xl mx-auto"
          >
            <h2 className="text-5xl md:text-7xl font-bold text-white mb-10 leading-[0.9]">
              The future belongs to the <span className="text-[#FA903E]">Prepared.</span>
            </h2>
            <p className="text-xl text-white/70 mb-14 max-w-2xl mx-auto leading-relaxed">
              Join the elite group of Melbourne SMEs defining the new AI economy.
            </p>
            <div className="flex flex-wrap justify-center gap-8">
              <Link
                href="/book"
                className="px-12 py-6 bg-[#12B5CB] text-black font-black rounded-3xl hover:scale-105 active:scale-95 transition-all cursor-pointer"
              >
                Secure Your Strategic Audit
              </Link>
              <Link
                href="/contact"
                className="px-12 py-6 glass-card border border-white/10 text-white font-bold rounded-3xl hover:bg-white/10 transition-all cursor-pointer"
              >
                Connect with Experts
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </>
  );
}
