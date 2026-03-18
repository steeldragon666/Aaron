// Approach — OmniscientAI Methodology
import { Link } from "wouter";
import { motion } from "framer-motion";
import { ArrowRight, ArrowLeft, Target, Search, Lightbulb, Rocket, BarChart3 } from "lucide-react";

const steps = [
  { icon: Search, title: "Discover", desc: "We start by understanding your business — operations, pain points, strategic goals, and current technology landscape. No assumptions." },
  { icon: Target, title: "Assess", desc: "Using our AI Readiness Framework, we evaluate your organisation across five dimensions: Data, People, Process, Technology, and Strategy." },
  { icon: Lightbulb, title: "Design", desc: "We design a tailored engagement — whether that's a workshop, consulting engagement, or blended approach — based on your specific needs and budget." },
  { icon: Rocket, title: "Deliver", desc: "Hands-on, interactive delivery focused on practical outcomes. Your team leaves with implemented workflows, not just slides." },
  { icon: BarChart3, title: "Measure", desc: "We help you track the business impact of AI adoption with clear metrics and 30 days of post-engagement support." },
];

export default function Approach() {
  return (
    <>
      <section className="relative pt-28 pb-16 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-[#12B5CB]/5 to-transparent pointer-events-none" />
        <div className="container relative">
          <Link href="/about" className="inline-flex items-center gap-1 text-sm text-[#888888] hover:text-[#12B5CB] transition-colors mb-6">
            <ArrowLeft className="w-4 h-4" /> Back to about
          </Link>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <span className="inline-block text-xs font-semibold uppercase tracking-[0.2em] text-[#12B5CB] mb-3" style={{ fontFamily: "var(--font-mono)" }}>OUR APPROACH</span>
            <h1 className="text-4xl md:text-5xl font-bold text-[#E8E8E8] leading-tight mb-4" style={{ fontFamily: "var(--font-heading)" }}>
              A methodology built for <span className="text-[#12B5CB]">real results</span>
            </h1>
            <p className="text-lg text-[#888888] max-w-2xl leading-relaxed">
              Our five-step methodology ensures every engagement delivers measurable business outcomes, not just AI awareness.
            </p>
          </motion.div>
        </div>
      </section>

      <section className="section-padding bg-[#0A0A0A]">
        <div className="container max-w-4xl">
          <div className="space-y-6">
            {steps.map((step, i) => (
              <motion.div
                key={step.title}
                initial={{ opacity: 0, x: i % 2 === 0 ? -30 : 30 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
              >
                <div className="glass-card rounded-2xl p-6 md:p-8 flex items-start gap-6">
                  <div className="w-14 h-14 rounded-2xl bg-[#12B5CB]/10 border border-[#12B5CB]/20 flex items-center justify-center shrink-0">
                    <step.icon className="w-7 h-7 text-[#12B5CB]" />
                  </div>
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-sm font-bold text-[#12B5CB]" style={{ fontFamily: "var(--font-mono)" }}>0{i + 1}</span>
                      <h2 className="text-xl font-bold text-[#E8E8E8]" style={{ fontFamily: "var(--font-heading)" }}>{step.title}</h2>
                    </div>
                    <p className="text-[#888888] leading-relaxed">{step.desc}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="mt-16 text-center"
          >
            <h2 className="text-2xl font-bold text-[#E8E8E8] mb-4" style={{ fontFamily: "var(--font-heading)" }}>Ready to get started?</h2>
            <Link href="/book" className="inline-flex items-center gap-2 px-6 py-3.5 text-sm font-semibold text-[#0A0A0A] bg-[#FA903E] rounded-lg hover:bg-[#FA903E]/90 transition-all">
              Book a Free Strategy Session <ArrowRight className="w-4 h-4" />
            </Link>
          </motion.div>
        </div>
      </section>
    </>
  );
}
