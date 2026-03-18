// Workshops listing — OmniscientAI Bento Grid Edition
import { Link } from "wouter";
import { motion } from "framer-motion";
import { ArrowRight, Clock, Users, Cpu, Shield, Zap, Sparkles } from "lucide-react";
import SectionHeading from "@/components/SectionHeading";
import TechPartners from "@/components/TechPartners";
import SEO from "@/components/SEO";
import { WORKSHOPS } from "@/lib/data";

const structuredData = {
  "@context": "https://schema.org",
  "@type": "ItemList",
  "itemListElement": WORKSHOPS.map((ws, i) => ({
    "@type": "ListItem",
    "position": i + 1,
    "url": `https://omniscientai.io/workshops/${ws.slug}`,
    "name": ws.title
  }))
};

const ICONS = [Cpu, Shield, Zap];

export default function Workshops() {
  return (
    <>
      <SEO
        title="AI Training Workshops"
        description="Hands-on AI training workshops designed for Melbourne SMEs. From automation to strategic governance."
      />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }} />
      {/* Hero */}
      <section className="relative pt-32 pb-16 overflow-hidden">
        <div className="container relative">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center max-w-4xl mx-auto"
          >
            <div className="flex items-center justify-center gap-2 mb-6">
              <div className="h-[1px] w-12 bg-gradient-to-r from-transparent to-[#12B5CB]" />
              <span className="text-xs font-bold uppercase tracking-[0.3em] text-[#12B5CB]" style={{ fontFamily: "var(--font-mono)" }}>
                Knowledge Systems
              </span>
              <div className="h-[1px] w-12 bg-gradient-to-l from-transparent to-[#12B5CB]" />
            </div>
            <h1 className="text-4xl md:text-6xl font-bold text-white leading-tight mb-6" style={{ fontFamily: "var(--font-heading)" }}>
              Training the next generation of <span className="gradient-text-cyan">AI leaders</span>
            </h1>
            <p className="text-lg text-white/60 max-w-2xl mx-auto leading-relaxed">
              Our workshops are precision-engineered for Melbourne SMEs. We don't just teach theory; we implement operational AI workflows in real-time.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Tech Partners */}
      <TechPartners />

      {/* Advanced Bento Grid */}
      <section className="py-24 relative">
        <div className="container">
          <div className="grid grid-cols-1 md:grid-cols-6 lg:grid-cols-12 gap-6">
            {WORKSHOPS.map((ws, i) => {
              const Icon = ICONS[i % ICONS.length];
              const isLarge = i === 0;

              return (
                <motion.div
                  key={ws.slug}
                  initial={{ opacity: 0, scale: 0.95 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: i * 0.1 }}
                  className={`relative group ${isLarge ? "md:col-span-6 lg:col-span-8" : "md:col-span-3 lg:col-span-4"
                    }`}
                >
                  <Link href={`/workshops/${ws.slug}`}>
                    <div className="h-full glass-card rounded-3xl overflow-hidden border border-white/5 group-hover:border-[#12B5CB]/30 transition-all duration-500 relative flex flex-col">
                      {/* Interactive Glow */}
                      <div className="absolute inset-0 bg-gradient-to-br from-[#12B5CB]/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />

                      {/* Image Layer */}
                      <div className={`relative overflow-hidden ${isLarge ? "h-64 md:h-80" : "h-48"}`}>
                        <img
                          src={ws.heroImage}
                          alt={ws.title}
                          className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110 grayscale-[40%] group-hover:grayscale-0"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-[#0A0A0A] via-transparent to-transparent" />

                        {/* Status Badge */}
                        <div className="absolute top-4 left-4">
                          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-black/60 border border-white/10 backdrop-blur-md">
                            <Sparkles className="w-3 h-3 text-[#12B5CB]" />
                            <span className="text-[10px] font-bold text-white/80 uppercase tracking-widest" style={{ fontFamily: "var(--font-mono)" }}>
                              Featured System
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Content Layer */}
                      <div className="p-8 flex flex-col flex-1 relative z-10">
                        <div className="flex items-center gap-4 mb-4">
                          <Icon className="w-5 h-5 text-[#12B5CB]" />
                          <div className="h-[1px] flex-1 bg-white/10" />
                        </div>

                        <h2 className="text-2xl font-bold text-white mb-3 group-hover:text-[#12B5CB] transition-colors" style={{ fontFamily: "var(--font-heading)" }}>
                          {ws.title}
                        </h2>
                        <p className="text-sm text-white/50 leading-relaxed mb-6 line-clamp-2">
                          {ws.description}
                        </p>

                        <div className="mt-auto pt-6 border-t border-white/5 flex items-center justify-between">
                          <div className="flex gap-4">
                            <div className="flex items-center gap-1.5 text-white/40">
                              <Clock className="w-3.5 h-3.5" />
                              <span className="text-[10px] font-bold uppercase tracking-widest">{ws.duration}</span>
                            </div>
                            <div className="flex items-center gap-1.5 text-white/40">
                              <Users className="w-3.5 h-3.5" />
                              <span className="text-[10px] font-bold uppercase tracking-widest">{ws.format}</span>
                            </div>
                          </div>
                          <motion.div
                            whileHover={{ x: 5 }}
                            className="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center group-hover:bg-[#12B5CB] group-hover:text-black transition-all"
                          >
                            <ArrowRight className="w-5 h-5" />
                          </motion.div>
                        </div>
                      </div>
                    </div>
                  </Link>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Bespoke AI Core CTA */}
      <section className="pb-24">
        <div className="container">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="relative p-12 md:p-20 rounded-[40px] overflow-hidden group"
          >
            <div className="absolute inset-0 bg-[#0A0A0A] border border-white/10 group-hover:border-[#FA903E]/30 transition-all duration-700" />
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-[#FA903E]/10 via-transparent to-transparent opacity-40" />

            <div className="relative z-10 max-w-2xl">
              <span className="inline-block text-[#FA903E] text-[10px] font-bold uppercase tracking-[0.4em] mb-4">Proprietary Training</span>
              <h2 className="text-3xl md:text-5xl font-bold text-white mb-6 leading-tight" style={{ fontFamily: "var(--font-heading)" }}>
                Architect a custom <span className="text-[#FA903E]">AI strategy</span> for your team
              </h2>
              <p className="text-lg text-white/60 mb-10 leading-relaxed">
                We design exclusive frameworks tailored to your industry's specific data hierarchy and operational bottlenecks.
              </p>
              <Link
                href="/workshops/custom"
                className="inline-flex items-center gap-3 px-8 py-4 text-sm font-bold text-black bg-[#FA903E] rounded-2xl hover:bg-[#FA903E]/90 hover:scale-105 transition-all"
              >
                Request Systems Audit <Zap className="w-4 h-4" />
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </>
  );
}
