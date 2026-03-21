// Custom Workshop Enquiry — OmniscientAI
import { motion } from "framer-motion";
import { Link } from "wouter";
import { ArrowLeft, Send } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

export default function CustomWorkshop() {
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    toast.success("Enquiry submitted! We'll be in touch within 24 hours.");
  };

  return (
    <section className="pt-28 pb-20">
      <div className="container max-w-3xl">
        <Link href="/workshops" className="inline-flex items-center gap-1 text-sm text-white/60 hover:text-[#12B5CB] transition-colors mb-6 cursor-pointer">
          <ArrowLeft className="w-4 h-4" /> Back to workshops
        </Link>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <h1 className="text-4xl md:text-5xl font-bold text-[#E8E8E8] mb-4" style={{ fontFamily: "var(--font-heading)" }}>
            Custom <span className="text-[#12B5CB]">Workshop</span> Enquiry
          </h1>
          <p className="text-lg text-white/60 mb-10 leading-relaxed">
            Need something tailored to your specific industry, team, or learning objectives? Tell us what you're looking for and we'll design a bespoke workshop.
          </p>
        </motion.div>

        {submitted ? (
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="glass-card rounded-2xl p-8 text-center">
            <div className="w-16 h-16 rounded-full bg-[#12B5CB]/10 border border-[#12B5CB]/20 flex items-center justify-center mx-auto mb-4">
              <Send className="w-7 h-7 text-[#12B5CB]" />
            </div>
            <h2 className="text-2xl font-bold text-[#E8E8E8] mb-2" style={{ fontFamily: "var(--font-heading)" }}>Enquiry Received</h2>
            <p className="text-white/60 mb-6">Thank you for your interest. We'll review your requirements and get back to you within 24 hours with a tailored proposal.</p>
            <Link href="/" className="text-[#12B5CB] hover:underline cursor-pointer">Return to homepage</Link>
          </motion.div>
        ) : (
          <motion.form
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            onSubmit={handleSubmit}
            className="glass-card rounded-2xl p-6 md:p-8 space-y-6"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-[#E8E8E8] mb-2">Name *</label>
                <input required type="text" className="w-full px-4 py-3 rounded-lg bg-[#0A0A0A] border border-[#333333] text-[#E8E8E8] placeholder-white/40 focus:border-[#12B5CB] focus:outline-none transition-colors" placeholder="Your name" />
              </div>
              <div>
                <label className="block text-sm font-medium text-[#E8E8E8] mb-2">Email *</label>
                <input required type="email" className="w-full px-4 py-3 rounded-lg bg-[#0A0A0A] border border-[#333333] text-[#E8E8E8] placeholder-white/40 focus:border-[#12B5CB] focus:outline-none transition-colors" placeholder="you@company.com" />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-[#E8E8E8] mb-2">Company</label>
                <input type="text" className="w-full px-4 py-3 rounded-lg bg-[#0A0A0A] border border-[#333333] text-[#E8E8E8] placeholder-white/40 focus:border-[#12B5CB] focus:outline-none transition-colors" placeholder="Company name" />
              </div>
              <div>
                <label className="block text-sm font-medium text-[#E8E8E8] mb-2">Team Size</label>
                <input type="text" className="w-full px-4 py-3 rounded-lg bg-[#0A0A0A] border border-[#333333] text-[#E8E8E8] placeholder-white/40 focus:border-[#12B5CB] focus:outline-none transition-colors" placeholder="e.g. 10-15 people" />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-[#E8E8E8] mb-2">Industry</label>
              <input type="text" className="w-full px-4 py-3 rounded-lg bg-[#0A0A0A] border border-[#333333] text-[#E8E8E8] placeholder-white/40 focus:border-[#12B5CB] focus:outline-none transition-colors" placeholder="e.g. Legal, Healthcare, Manufacturing" />
            </div>
            <div>
              <label className="block text-sm font-medium text-[#E8E8E8] mb-2">What are your learning objectives? *</label>
              <textarea required rows={4} className="w-full px-4 py-3 rounded-lg bg-[#0A0A0A] border border-[#333333] text-[#E8E8E8] placeholder-white/40 focus:border-[#12B5CB] focus:outline-none transition-colors resize-none" placeholder="Tell us about your team's goals, current AI experience, and what you'd like to achieve..." />
            </div>
            <button
              type="submit"
              className="w-full px-6 py-3.5 text-sm font-semibold text-[#0A0A0A] bg-[#FA903E] rounded-lg hover:bg-[#FA903E]/90 transition-all"
            >
              Submit Enquiry
            </button>
          </motion.form>
        )}
      </div>
    </section>
  );
}
