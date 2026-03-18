// Service Detail — OmniscientAI
import { useParams, Link } from "wouter";
import { motion } from "framer-motion";
import { ArrowLeft, ArrowRight, CheckCircle } from "lucide-react";
import { SERVICES } from "@/lib/data";

export default function ServiceDetail() {
  const { slug } = useParams<{ slug: string }>();
  const svc = SERVICES.find((s) => s.slug === slug);

  if (!svc) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-[#E8E8E8] mb-4" style={{ fontFamily: "var(--font-heading)" }}>Service not found</h1>
          <Link href="/services" className="text-[#12B5CB] hover:underline">Back to services</Link>
        </div>
      </div>
    );
  }

  return (
    <>
      <section className="relative pt-28 pb-16 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-[#FA903E]/5 to-transparent pointer-events-none" />
        <div className="container relative">
          <Link href="/services" className="inline-flex items-center gap-1 text-sm text-[#888888] hover:text-[#12B5CB] transition-colors mb-6">
            <ArrowLeft className="w-4 h-4" /> Back to services
          </Link>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <h1 className="text-4xl md:text-5xl font-bold text-[#E8E8E8] mb-3" style={{ fontFamily: "var(--font-heading)" }}>{svc.title}</h1>
            <p className="text-xl text-[#FA903E]">{svc.subtitle}</p>
          </motion.div>
        </div>
      </section>

      <div className="container pb-20">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-12">
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.5 }}>
              <p className="text-lg text-[#E8E8E8]/90 leading-relaxed">{svc.description}</p>
            </motion.div>

            {/* What's included */}
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.5 }}>
              <h2 className="text-2xl font-bold text-[#E8E8E8] mb-6" style={{ fontFamily: "var(--font-heading)" }}>What's Included</h2>
              <div className="space-y-3">
                {svc.features.map((f, i) => (
                  <div key={i} className="flex items-start gap-3 text-[#E8E8E8]/80">
                    <CheckCircle className="w-5 h-5 text-[#12B5CB] mt-0.5 shrink-0" />
                    <span>{f}</span>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Process */}
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.5 }}>
              <h2 className="text-2xl font-bold text-[#E8E8E8] mb-6" style={{ fontFamily: "var(--font-heading)" }}>Our Process</h2>
              <div className="space-y-4">
                {svc.process.map((p, i) => (
                  <div key={i} className="glass-card rounded-xl p-5 flex items-start gap-4">
                    <div className="w-10 h-10 rounded-xl bg-[#FA903E]/10 border border-[#FA903E]/20 flex items-center justify-center shrink-0">
                      <span className="text-sm font-bold text-[#FA903E]" style={{ fontFamily: "var(--font-mono)" }}>{i + 1}</span>
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-[#E8E8E8] mb-1" style={{ fontFamily: "var(--font-heading)" }}>{p.step}</h3>
                      <p className="text-sm text-[#888888] leading-relaxed">{p.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>

          {/* Sidebar CTA */}
          <div className="lg:col-span-1">
            <div className="lg:sticky lg:top-24">
              <div className="glass-card rounded-2xl p-6 glow-tangerine">
                <h3 className="text-lg font-bold text-[#E8E8E8] mb-2" style={{ fontFamily: "var(--font-heading)" }}>Get Started</h3>
                <p className="text-sm text-[#888888] mb-6">Book a free 30-minute strategy session to discuss how this service can help your business.</p>
                <Link
                  href="/book"
                  className="block w-full text-center px-6 py-3.5 text-sm font-semibold text-[#0A0A0A] bg-[#FA903E] rounded-lg hover:bg-[#FA903E]/90 transition-all mb-3"
                >
                  Book a Strategy Session
                </Link>
                <Link
                  href="/contact"
                  className="block w-full text-center px-6 py-3 text-sm font-medium text-[#12B5CB] border border-[#12B5CB]/30 rounded-lg hover:bg-[#12B5CB]/10 transition-colors"
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
