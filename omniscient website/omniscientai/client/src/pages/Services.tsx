// Services — OmniscientAI
import { Link } from "wouter";
import { motion } from "framer-motion";
import { ArrowRight, Compass, BarChart3 } from "lucide-react";
import { SERVICES } from "@/lib/data";

const icons = [Compass, BarChart3];

export default function Services() {
  return (
    <>
      <section className="relative pt-32 pb-16 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-[#FA903E]/5 to-transparent pointer-events-none" />
        <div className="container relative">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <span className="inline-block text-xs font-semibold uppercase tracking-[0.2em] text-[#FA903E] mb-3" style={{ fontFamily: "var(--font-mono)" }}>SERVICES</span>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-[#E8E8E8] leading-tight mb-4" style={{ fontFamily: "var(--font-heading)" }}>
              Strategic AI consulting for <span className="text-[#FA903E]">real outcomes</span>
            </h1>
            <p className="text-lg text-white/60 max-w-2xl leading-relaxed">
              Beyond workshops, we provide hands-on consulting to help your organisation develop and execute a practical AI strategy. Vendor-neutral. Budget-appropriate. Results-focused.
            </p>
          </motion.div>
        </div>
      </section>

      <section className="section-padding bg-[#0A0A0A]">
        <div className="container">
          <div className="space-y-8">
            {SERVICES.map((svc, i) => {
              const Icon = icons[i];
              return (
                <motion.div
                  key={svc.slug}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: i * 0.1 }}
                >
                  <Link href={`/services/${svc.slug}`} className="cursor-pointer">
                    <div className="glass-card rounded-2xl p-8 group cursor-pointer">
                      <div className="flex items-start gap-6">
                        <div className="w-12 h-12 rounded-xl bg-[#FA903E]/10 border border-[#FA903E]/20 flex items-center justify-center shrink-0">
                          <Icon className="w-6 h-6 text-[#FA903E]" />
                        </div>
                        <div className="flex-1">
                          <h2 className="text-2xl font-bold text-[#E8E8E8] mb-2" style={{ fontFamily: "var(--font-heading)" }}>{svc.title}</h2>
                          <p className="text-sm text-[#12B5CB] mb-3">{svc.subtitle}</p>
                          <p className="text-white/60 leading-relaxed mb-4">{svc.description}</p>
                          <div className="flex items-center gap-1 text-sm text-[#12B5CB] font-medium group-hover:gap-2 transition-all">
                            Learn more <ArrowRight className="w-4 h-4" />
                          </div>
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
