// Workshop Detail — OmniscientAI
import { useParams, Link } from "wouter";
import { motion } from "framer-motion";
import { ArrowRight, ArrowLeft, Clock, Users, MapPin, CheckCircle, ChevronDown } from "lucide-react";
import { WORKSHOPS } from "@/lib/data";
import { useState } from "react";

export default function WorkshopDetail() {
  const { slug } = useParams<{ slug: string }>();
  const ws = WORKSHOPS.find((w) => w.slug === slug);
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  if (!ws) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-[#E8E8E8] mb-4" style={{ fontFamily: "var(--font-heading)" }}>Workshop not found</h1>
          <Link href="/workshops" className="text-[#12B5CB] hover:underline">Back to workshops</Link>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Hero */}
      <section className="relative pt-28 pb-16 overflow-hidden">
        <div className="absolute inset-0">
          <img src={ws.heroImage} alt="" className="w-full h-full object-cover opacity-30" />
          <div className="absolute inset-0 bg-gradient-to-b from-[#0A0A0A]/80 via-[#0A0A0A]/90 to-[#0A0A0A]" />
        </div>
        <div className="container relative">
          <Link href="/workshops" className="inline-flex items-center gap-1 text-sm text-white/60 hover:text-[#12B5CB] transition-colors mb-6 cursor-pointer">
            <ArrowLeft className="w-4 h-4" /> Back to workshops
          </Link>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <div className="flex flex-wrap gap-2 mb-4">
              <span className="text-xs font-medium text-[#12B5CB] px-3 py-1 rounded-full bg-[#12B5CB]/10 border border-[#12B5CB]/20 flex items-center gap-1" style={{ fontFamily: "var(--font-mono)" }}>
                <Clock className="w-3 h-3" /> {ws.duration}
              </span>
              <span className="text-xs font-medium text-white/60 px-3 py-1 rounded-full bg-white/5 border border-[#333333] flex items-center gap-1" style={{ fontFamily: "var(--font-mono)" }}>
                <Users className="w-3 h-3" /> {ws.format}
              </span>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-[#E8E8E8] mb-3" style={{ fontFamily: "var(--font-heading)" }}>{ws.title}</h1>
            <p className="text-xl text-white/60 mb-4">{ws.subtitle}</p>
            <div className="flex items-center gap-4">
              <span className="text-2xl font-bold text-[#FA903E]" style={{ fontFamily: "var(--font-mono)" }}>{ws.priceRange}</span>
              <span className="text-sm text-white/60">{ws.priceNote}</span>
            </div>
          </motion.div>
        </div>
      </section>

      <div className="container pb-20">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main content */}
          <div className="lg:col-span-2 space-y-12">
            {/* Description */}
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.5 }}>
              <p className="text-lg text-[#E8E8E8]/90 leading-relaxed">{ws.description}</p>
            </motion.div>

            {/* Who is it for */}
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.5 }}>
              <h2 className="text-2xl font-bold text-[#E8E8E8] mb-6" style={{ fontFamily: "var(--font-heading)" }}>Who This Is For</h2>
              <div className="space-y-3">
                {ws.whoIsItFor.map((item, i) => (
                  <div key={i} className="flex items-start gap-3 text-[#E8E8E8]/80">
                    <CheckCircle className="w-5 h-5 text-[#12B5CB] mt-0.5 shrink-0" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Modules */}
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.5 }}>
              <h2 className="text-2xl font-bold text-[#E8E8E8] mb-6" style={{ fontFamily: "var(--font-heading)" }}>Workshop Agenda</h2>
              <div className="space-y-4">
                {ws.modules.map((mod, i) => (
                  <div key={i} className="glass-card rounded-xl p-5">
                    <div className="flex items-start justify-between gap-4 mb-2">
                      <h3 className="text-lg font-semibold text-[#E8E8E8]" style={{ fontFamily: "var(--font-heading)" }}>
                        <span className="text-[#12B5CB] mr-2" style={{ fontFamily: "var(--font-mono)" }}>0{i + 1}</span>
                        {mod.title}
                      </h3>
                      <span className="text-xs text-white/60 shrink-0 px-2 py-0.5 rounded-full bg-white/5" style={{ fontFamily: "var(--font-mono)" }}>{mod.duration}</span>
                    </div>
                    <p className="text-sm text-white/60 leading-relaxed">{mod.description}</p>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Outcomes */}
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.5 }}>
              <h2 className="text-2xl font-bold text-[#E8E8E8] mb-6" style={{ fontFamily: "var(--font-heading)" }}>What You'll Walk Away With</h2>
              <div className="space-y-3">
                {ws.outcomes.map((item, i) => (
                  <div key={i} className="flex items-start gap-3 text-[#E8E8E8]/80">
                    <div className="w-6 h-6 rounded-full bg-[#12B5CB]/10 border border-[#12B5CB]/20 flex items-center justify-center shrink-0 mt-0.5">
                      <span className="text-xs text-[#12B5CB] font-bold" style={{ fontFamily: "var(--font-mono)" }}>{i + 1}</span>
                    </div>
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* FAQs */}
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.5 }}>
              <h2 className="text-2xl font-bold text-[#E8E8E8] mb-6" style={{ fontFamily: "var(--font-heading)" }}>Frequently Asked Questions</h2>
              <div className="space-y-3">
                {ws.faqs.map((faq, i) => (
                  <div key={i} className="glass-card rounded-xl overflow-hidden">
                    <button
                      onClick={() => setOpenFaq(openFaq === i ? null : i)}
                      className="w-full flex items-center justify-between p-5 text-left cursor-pointer"
                    >
                      <span className="text-[#E8E8E8] font-medium pr-4">{faq.q}</span>
                      <ChevronDown className={`w-5 h-5 text-white/60 shrink-0 transition-transform ${openFaq === i ? "rotate-180" : ""}`} />
                    </button>
                    {openFaq === i && (
                      <div className="px-5 pb-5 -mt-1">
                        <p className="text-sm text-white/60 leading-relaxed">{faq.a}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Testimonials */}
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.5 }}>
              <h2 className="text-2xl font-bold text-[#E8E8E8] mb-6" style={{ fontFamily: "var(--font-heading)" }}>What Attendees Say</h2>
              <div className="space-y-4">
                {ws.testimonials.map((t, i) => (
                  <div key={i} className="glass-card rounded-xl p-6">
                    <p className="text-[#E8E8E8]/90 leading-relaxed mb-4 italic">"{t.quote}"</p>
                    <div>
                      <p className="text-sm font-semibold text-[#E8E8E8]">{t.name}</p>
                      <p className="text-xs text-white/60">{t.role}</p>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>

          {/* Sticky sidebar CTA */}
          <div className="lg:col-span-1">
            <div className="lg:sticky lg:top-24">
              <div className="glass-card rounded-2xl p-6 glow-cyan">
                <h3 className="text-lg font-bold text-[#E8E8E8] mb-2" style={{ fontFamily: "var(--font-heading)" }}>Book This Workshop</h3>
                <p className="text-sm text-white/60 mb-4">Secure your team's spot. We'll customise the content to your industry.</p>
                <div className="space-y-3 mb-6">
                  <div className="flex justify-between text-sm">
                    <span className="text-white/60">Duration</span>
                    <span className="text-[#E8E8E8] font-medium">{ws.duration}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-white/60">Format</span>
                    <span className="text-[#E8E8E8] font-medium">{ws.format}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-white/60">Investment</span>
                    <span className="text-[#FA903E] font-bold" style={{ fontFamily: "var(--font-mono)" }}>{ws.priceRange}</span>
                  </div>
                  <div className="text-xs text-white/60">{ws.priceNote}</div>
                </div>
                <Link
                  href="/book"
                  className="block w-full text-center px-6 py-3.5 text-sm font-semibold text-[#0A0A0A] bg-[#FA903E] rounded-lg hover:bg-[#FA903E]/90 transition-all mb-3 cursor-pointer"
                >
                  Book Now
                </Link>
                <Link
                  href="/contact"
                  className="block w-full text-center px-6 py-3 text-sm font-medium text-[#12B5CB] border border-[#12B5CB]/30 rounded-lg hover:bg-[#12B5CB]/10 transition-colors cursor-pointer"
                >
                  Ask a Question
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
