// About — OmniscientAI
import { Link } from "wouter";
import { motion } from "framer-motion";
import { ArrowRight, Award, Shield, Users, Lightbulb } from "lucide-react";

export default function About() {
  return (
    <>
      <section className="relative pt-32 pb-16 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-[#12B5CB]/5 to-transparent pointer-events-none" />
        <div className="container relative">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <span className="inline-block text-xs font-semibold uppercase tracking-[0.2em] text-[#12B5CB] mb-3" style={{ fontFamily: "var(--font-mono)" }}>ABOUT</span>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-[#E8E8E8] leading-tight mb-4" style={{ fontFamily: "var(--font-heading)" }}>
              Vendor-neutral AI expertise for <span className="text-[#12B5CB]">Melbourne SMEs</span>
            </h1>
            <p className="text-lg text-[#888888] max-w-2xl leading-relaxed">
              We exist because most AI training is either too theoretical, too vendor-biased, or too expensive for small and medium businesses. We're changing that.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Founder story */}
      <section className="section-padding bg-[#0A0A0A]">
        <div className="container">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.5 }}>
              <div className="glass-card rounded-2xl p-8 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-[#12B5CB]/5 rounded-full blur-[60px]" />
                <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-[#12B5CB] to-[#12B5CB]/60 flex items-center justify-center mb-6">
                  <span className="text-3xl font-bold text-[#0A0A0A]" style={{ fontFamily: "var(--font-heading)" }}>O</span>
                </div>
                <h2 className="text-2xl font-bold text-[#E8E8E8] mb-4" style={{ fontFamily: "var(--font-heading)" }}>Our Story</h2>
                <div className="space-y-4 text-[#E8E8E8]/80 leading-relaxed">
                  <p>OmniscientAI was founded with a simple observation: Melbourne's SMEs were being left behind in the AI revolution. Enterprise companies had dedicated AI teams and seven-figure budgets. Small businesses had ChatGPT and confusion.</p>
                  <p>We saw an opportunity to bridge that gap — not by selling AI tools, but by teaching businesses how to evaluate, implement, and govern AI on their own terms. Vendor-neutral means we recommend what's best for you, not what pays us the highest commission.</p>
                  <p>Based in Melbourne's CBD, we work exclusively with Australian SMEs. We understand the local regulatory landscape, the specific challenges of the Australian market, and the practical constraints of running a small business.</p>
                </div>
              </div>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.5, delay: 0.1 }}>
              <img
                src="https://d2xsxph8kpxj0f.cloudfront.net/310419663026972742/it6qHcTHLu2dmqyuKKnamM/melbourne-skyline-PTJNo5KjCBwBdy5Wy2WHDt.webp"
                alt="Melbourne skyline"
                className="w-full rounded-2xl"
              />
            </motion.div>
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="section-padding bg-[#0A0A0A]">
        <div className="container">
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.5 }} className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-[#E8E8E8]" style={{ fontFamily: "var(--font-heading)" }}>What We Stand For</h2>
          </motion.div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: Shield, title: "Vendor Neutral", desc: "We don't sell AI tools. We recommend what's genuinely best for your business, not what pays us commission." },
              { icon: Lightbulb, title: "Practical Focus", desc: "Every workshop ends with implemented workflows. We measure success by what your team does differently on Monday." },
              { icon: Users, title: "SME Specialist", desc: "We understand the constraints of small business — limited budgets, small teams, and the need for quick wins." },
              { icon: Award, title: "Australian Context", desc: "We know the local regulatory landscape, privacy requirements, and market dynamics that matter for Australian businesses." },
            ].map((v, i) => (
              <motion.div
                key={v.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
              >
                <div className="glass-card rounded-2xl p-6 h-full">
                  <div className="w-10 h-10 rounded-xl bg-[#12B5CB]/10 border border-[#12B5CB]/20 flex items-center justify-center mb-4">
                    <v.icon className="w-5 h-5 text-[#12B5CB]" />
                  </div>
                  <h3 className="text-lg font-semibold text-[#E8E8E8] mb-2" style={{ fontFamily: "var(--font-heading)" }}>{v.title}</h3>
                  <p className="text-sm text-[#888888] leading-relaxed">{v.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="section-padding bg-[#0A0A0A]">
        <div className="container text-center">
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.5 }}>
            <h2 className="text-3xl md:text-4xl font-bold text-[#E8E8E8] mb-4" style={{ fontFamily: "var(--font-heading)" }}>
              Want to learn more about our approach?
            </h2>
            <div className="flex flex-wrap justify-center gap-4 mt-6">
              <Link href="/about/approach" className="inline-flex items-center gap-2 px-6 py-3 text-sm font-semibold text-[#12B5CB] border border-[#12B5CB]/30 rounded-lg hover:bg-[#12B5CB]/10 transition-colors">
                Our Methodology <ArrowRight className="w-4 h-4" />
              </Link>
              <Link href="/book" className="inline-flex items-center gap-2 px-6 py-3 text-sm font-semibold text-[#0A0A0A] bg-[#FA903E] rounded-lg hover:bg-[#FA903E]/90 transition-all">
                Book a Strategy Session <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </>
  );
}
