// Industries — OmniscientAI
import { Link } from "wouter";
import { motion } from "framer-motion";
import { ArrowRight, Briefcase, HeartPulse, Factory, ShoppingBag } from "lucide-react";
import SectionHeading from "@/components/SectionHeading";
import { INDUSTRIES } from "@/lib/data";

const icons = [Briefcase, HeartPulse, Factory, ShoppingBag];

export default function Industries() {
  return (
    <>
      <section className="relative pt-32 pb-16 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-[#12B5CB]/5 to-transparent pointer-events-none" />
        <div className="container relative">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <span className="inline-block text-xs font-semibold uppercase tracking-[0.2em] text-[#12B5CB] mb-3" style={{ fontFamily: "var(--font-mono)" }}>INDUSTRIES</span>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-[#E8E8E8] leading-tight mb-4" style={{ fontFamily: "var(--font-heading)" }}>
              AI solutions for <span className="text-[#12B5CB]">your industry</span>
            </h1>
            <p className="text-lg text-[#888888] max-w-2xl leading-relaxed">
              Every industry has unique AI opportunities and challenges. We tailor our workshops and consulting to your specific sector, regulations, and competitive landscape.
            </p>
          </motion.div>
        </div>
      </section>

      <section className="section-padding bg-[#0A0A0A]">
        <div className="container">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {INDUSTRIES.map((ind, i) => {
              const Icon = icons[i];
              return (
                <motion.div
                  key={ind.slug}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: i * 0.1 }}
                >
                  <Link href={`/industries/${ind.slug}`}>
                    <div className="glass-card rounded-2xl p-6 md:p-8 h-full group">
                      <div className="flex items-start gap-4 mb-4">
                        <div className="w-12 h-12 rounded-xl bg-[#12B5CB]/10 border border-[#12B5CB]/20 flex items-center justify-center shrink-0">
                          <Icon className="w-6 h-6 text-[#12B5CB]" />
                        </div>
                        <div>
                          <h2 className="text-xl font-bold text-[#E8E8E8]" style={{ fontFamily: "var(--font-heading)" }}>{ind.title}</h2>
                          <p className="text-sm text-[#888888]">{ind.subtitle}</p>
                        </div>
                      </div>
                      <p className="text-sm text-[#888888] leading-relaxed mb-4">{ind.description}</p>
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="text-2xl font-bold text-[#12B5CB]" style={{ fontFamily: "var(--font-mono)" }}>{ind.stat}</span>
                          <span className="text-xs text-[#888888] ml-2">{ind.statLabel}</span>
                        </div>
                        <div className="flex items-center gap-1 text-sm text-[#12B5CB] font-medium group-hover:gap-2 transition-all">
                          Learn more <ArrowRight className="w-4 h-4" />
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
    </>
  );
}
