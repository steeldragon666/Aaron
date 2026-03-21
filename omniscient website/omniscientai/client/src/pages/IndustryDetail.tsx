// Industry Detail — OmniscientAI
import { useParams, Link } from "wouter";
import { motion } from "framer-motion";
import { ArrowLeft, ArrowRight, CheckCircle } from "lucide-react";
import { INDUSTRIES, WORKSHOPS } from "@/lib/data";

export default function IndustryDetail() {
  const { slug } = useParams<{ slug: string }>();
  const ind = INDUSTRIES.find((i) => i.slug === slug);

  if (!ind) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-[#E8E8E8] mb-4" style={{ fontFamily: "var(--font-heading)" }}>Industry not found</h1>
          <Link href="/industries" className="text-[#12B5CB] hover:underline">Back to industries</Link>
        </div>
      </div>
    );
  }

  return (
    <>
      <section className="relative pt-28 pb-16 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-[#12B5CB]/5 to-transparent pointer-events-none" />
        <div className="container relative">
          <Link href="/industries" className="inline-flex items-center gap-1 text-sm text-white/60 hover:text-[#12B5CB] transition-colors mb-6 cursor-pointer">
            <ArrowLeft className="w-4 h-4" /> Back to industries
          </Link>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <div className="flex items-center gap-3 mb-4">
              <span className="text-4xl font-bold text-[#12B5CB]" style={{ fontFamily: "var(--font-mono)" }}>{ind.stat}</span>
              <span className="text-sm text-white/60">{ind.statLabel}</span>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-[#E8E8E8] mb-3" style={{ fontFamily: "var(--font-heading)" }}>
              AI for {ind.title}
            </h1>
            <p className="text-lg text-white/60">{ind.subtitle}</p>
          </motion.div>
        </div>
      </section>

      <div className="container pb-20">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-12">
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.5 }}>
              <p className="text-lg text-[#E8E8E8]/90 leading-relaxed">{ind.description}</p>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.5 }}>
              <h2 className="text-2xl font-bold text-[#E8E8E8] mb-6" style={{ fontFamily: "var(--font-heading)" }}>Key AI Use Cases</h2>
              <div className="space-y-3">
                {ind.useCases.map((uc, i) => (
                  <div key={i} className="flex items-start gap-3 text-[#E8E8E8]/80">
                    <CheckCircle className="w-5 h-5 text-[#12B5CB] mt-0.5 shrink-0" />
                    <span>{uc}</span>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Recommended workshops */}
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.5 }}>
              <h2 className="text-2xl font-bold text-[#E8E8E8] mb-6" style={{ fontFamily: "var(--font-heading)" }}>Recommended Workshops</h2>
              <div className="space-y-4">
                {WORKSHOPS.map((ws) => (
                  <Link key={ws.slug} href={`/workshops/${ws.slug}`}>
                    <div className="glass-card rounded-xl p-5 group flex items-center justify-between cursor-pointer">
                      <div>
                        <h3 className="text-lg font-semibold text-[#E8E8E8]" style={{ fontFamily: "var(--font-heading)" }}>{ws.title}</h3>
                        <p className="text-sm text-white/60">{ws.duration} · {ws.priceRange}</p>
                      </div>
                      <ArrowRight className="w-5 h-5 text-[#12B5CB] group-hover:translate-x-1 transition-transform" />
                    </div>
                  </Link>
                ))}
              </div>
            </motion.div>
          </div>

          <div className="lg:col-span-1">
            <div className="lg:sticky lg:top-24">
              <div className="glass-card rounded-2xl p-6 glow-cyan">
                <h3 className="text-lg font-bold text-[#E8E8E8] mb-2" style={{ fontFamily: "var(--font-heading)" }}>Get Industry-Specific Advice</h3>
                <p className="text-sm text-white/60 mb-6">Book a free strategy session to discuss AI opportunities specific to {ind.title.toLowerCase()}.</p>
                <Link
                  href="/book"
                  className="block w-full text-center px-6 py-3.5 text-sm font-semibold text-[#0A0A0A] bg-[#FA903E] rounded-lg hover:bg-[#FA903E]/90 transition-all mb-3 cursor-pointer"
                >
                  Book a Strategy Session
                </Link>
                <Link
                  href="/ai-readiness-quiz"
                  className="block w-full text-center px-6 py-3 text-sm font-medium text-[#12B5CB] border border-[#12B5CB]/30 rounded-lg hover:bg-[#12B5CB]/10 transition-colors cursor-pointer"
                >
                  Take the AI Readiness Quiz
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
