// Services — OmniscientAI Dramatic Redesign
import { Link } from "wouter";
import { motion } from "framer-motion";
import { ArrowRight, Compass, BarChart3, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { SERVICES } from "@/lib/data";

const icons = [Compass, BarChart3];
const accents = ["#12B5CB", "#FA903E"];

export default function Services() {
  return (
    <>
      {/* Header */}
      <section className="relative pt-32 pb-16 overflow-hidden">
        {/* Background */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#FA903E]/5 via-transparent to-transparent pointer-events-none" />
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            backgroundImage: `radial-gradient(circle, rgba(250,144,62,0.06) 1px, transparent 1px)`,
            backgroundSize: "40px 40px",
            maskImage: "linear-gradient(to bottom, black, transparent 80%)",
            WebkitMaskImage: "linear-gradient(to bottom, black, transparent 80%)",
          }}
        />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-[radial-gradient(ellipse_at_center,rgba(250,144,62,0.1),transparent_70%)] pointer-events-none" />

        <div className="container relative">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="w-4 h-4 text-[#FA903E]" />
              <span className="inline-block text-xs font-semibold uppercase tracking-[0.2em] text-[#FA903E]" style={{ fontFamily: "var(--font-mono)" }}>
                SERVICES
              </span>
            </div>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-[#E8E8E8] leading-tight mb-4" style={{ fontFamily: "var(--font-heading)" }}>
              Strategic AI consulting for{" "}
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-[#FA903E] to-[#FA903E]/60">
                real outcomes
              </span>
            </h1>
            <p className="text-lg text-white/50 max-w-2xl leading-relaxed">
              Beyond workshops, we provide hands-on consulting to help your organisation develop and execute a practical AI strategy. Vendor-neutral. Budget-appropriate. Results-focused.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Service Cards Grid */}
      <section className="section-padding bg-[#0A0A0A] relative">
        {/* Subtle background pattern */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            backgroundImage: `radial-gradient(circle, rgba(255,255,255,0.02) 1px, transparent 1px)`,
            backgroundSize: "32px 32px",
          }}
        />

        <div className="container relative">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6 max-w-5xl mx-auto">
            {SERVICES.map((svc, i) => {
              const Icon = icons[i] || Compass;
              const accent = accents[i] || "#12B5CB";

              return (
                <motion.div
                  key={svc.slug}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: i * 0.1 }}
                >
                  <Link href={`/services/${svc.slug}`} className="cursor-pointer">
                    <div
                      className={cn(
                        "group relative rounded-2xl p-8 md:p-10 h-full overflow-hidden cursor-pointer",
                        "border border-white/[0.06] bg-white/[0.02]",
                        "hover:border-white/[0.12] hover:bg-white/[0.04]",
                        "transition-all duration-500 ease-out",
                        "hover:-translate-y-1",
                      )}
                    >
                      {/* Background icon watermark */}
                      <div className="absolute -right-6 -bottom-6 opacity-[0.03] group-hover:opacity-[0.06] transition-opacity duration-500">
                        <Icon className="w-48 h-48" style={{ color: accent }} />
                      </div>

                      {/* Top gradient line */}
                      <div
                        className="absolute top-0 left-0 right-0 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                        style={{ background: `linear-gradient(90deg, transparent, ${accent}, transparent)` }}
                      />

                      {/* Dot pattern on hover */}
                      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                        <div
                          className="absolute inset-0"
                          style={{
                            backgroundImage: `radial-gradient(circle, ${accent}10 1px, transparent 1px)`,
                            backgroundSize: "20px 20px",
                          }}
                        />
                      </div>

                      <div className="relative z-10">
                        {/* Icon */}
                        <div
                          className="w-14 h-14 rounded-2xl flex items-center justify-center mb-6 transition-all duration-300 group-hover:scale-110"
                          style={{ background: `${accent}12`, border: `1px solid ${accent}25` }}
                        >
                          <Icon className="w-7 h-7" style={{ color: accent }} />
                        </div>

                        {/* Content */}
                        <h2 className="text-2xl md:text-3xl font-bold text-[#E8E8E8] mb-2 tracking-tight" style={{ fontFamily: "var(--font-heading)" }}>
                          {svc.title}
                        </h2>
                        <p className="text-sm font-medium mb-4" style={{ color: accent }}>
                          {svc.subtitle}
                        </p>
                        <p className="text-white/50 leading-relaxed mb-6 text-sm md:text-base">
                          {svc.description}
                        </p>

                        {/* CTA */}
                        <div
                          className="inline-flex items-center gap-2 text-sm font-semibold group-hover:gap-3 transition-all duration-300"
                          style={{ color: accent }}
                        >
                          Explore this service
                          <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform duration-300" />
                        </div>
                      </div>

                      {/* Hover shadow */}
                      <div
                        className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
                        style={{ boxShadow: `0 12px 40px -12px ${accent}20` }}
                      />
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
