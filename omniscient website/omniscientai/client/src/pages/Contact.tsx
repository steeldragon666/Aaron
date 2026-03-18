// Contact — OmniscientAI
import { useState } from "react";
import { motion } from "framer-motion";
import { Mail, Phone, MapPin, Clock, Send, CheckCircle, Linkedin } from "lucide-react";
import { toast } from "sonner";

export default function Contact() {
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    toast.success("Message sent! We'll respond within 24 hours.");
  };

  return (
    <section className="pt-28 pb-20">
      <div className="container max-w-5xl">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="mb-10">
          <span className="inline-block text-xs font-semibold uppercase tracking-[0.2em] text-[#12B5CB] mb-3" style={{ fontFamily: "var(--font-mono)" }}>CONTACT</span>
          <h1 className="text-4xl md:text-5xl font-bold text-[#E8E8E8] mb-4" style={{ fontFamily: "var(--font-heading)" }}>
            Get in <span className="text-[#12B5CB]">touch</span>
          </h1>
          <p className="text-lg text-[#888888] max-w-2xl leading-relaxed">
            Have a question about our workshops or services? Want to discuss a custom engagement? We'd love to hear from you.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_360px] gap-8">
          {/* Form */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.1 }}>
            {submitted ? (
              <div className="glass-card rounded-2xl p-8 text-center">
                <div className="w-16 h-16 rounded-full bg-[#12B5CB]/10 border border-[#12B5CB]/20 flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="w-8 h-8 text-[#12B5CB]" />
                </div>
                <h2 className="text-2xl font-bold text-[#E8E8E8] mb-2" style={{ fontFamily: "var(--font-heading)" }}>Message Sent</h2>
                <p className="text-[#888888]">Thank you for reaching out. We'll respond within 24 hours during business days.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="glass-card rounded-2xl p-6 md:p-8 space-y-5">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div>
                    <label className="block text-sm font-medium text-[#E8E8E8] mb-2">Name *</label>
                    <input required type="text" className="w-full px-4 py-3 rounded-lg bg-[#0A0A0A] border border-[#333333] text-[#E8E8E8] placeholder-[#888888] focus:border-[#12B5CB] focus:outline-none transition-colors" placeholder="Your name" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-[#E8E8E8] mb-2">Email *</label>
                    <input required type="email" className="w-full px-4 py-3 rounded-lg bg-[#0A0A0A] border border-[#333333] text-[#E8E8E8] placeholder-[#888888] focus:border-[#12B5CB] focus:outline-none transition-colors" placeholder="you@company.com" />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div>
                    <label className="block text-sm font-medium text-[#E8E8E8] mb-2">Company</label>
                    <input type="text" className="w-full px-4 py-3 rounded-lg bg-[#0A0A0A] border border-[#333333] text-[#E8E8E8] placeholder-[#888888] focus:border-[#12B5CB] focus:outline-none transition-colors" placeholder="Company name" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-[#E8E8E8] mb-2">Subject</label>
                    <select className="w-full px-4 py-3 rounded-lg bg-[#0A0A0A] border border-[#333333] text-[#E8E8E8] focus:border-[#12B5CB] focus:outline-none transition-colors">
                      <option value="general">General Enquiry</option>
                      <option value="workshop">Workshop Enquiry</option>
                      <option value="consulting">Consulting Enquiry</option>
                      <option value="custom">Custom Workshop</option>
                      <option value="partnership">Partnership</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#E8E8E8] mb-2">Message *</label>
                  <textarea required rows={5} className="w-full px-4 py-3 rounded-lg bg-[#0A0A0A] border border-[#333333] text-[#E8E8E8] placeholder-[#888888] focus:border-[#12B5CB] focus:outline-none transition-colors resize-none" placeholder="Tell us how we can help..." />
                </div>
                <button type="submit" className="w-full px-6 py-3.5 text-sm font-semibold text-[#0A0A0A] bg-[#FA903E] rounded-lg hover:bg-[#FA903E]/90 transition-all flex items-center justify-center gap-2">
                  <Send className="w-4 h-4" /> Send Message
                </button>
              </form>
            )}
          </motion.div>

          {/* Contact info sidebar */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.2 }}>
            <div className="space-y-4">
              <div className="glass-card rounded-2xl p-6">
                <h3 className="text-lg font-bold text-[#E8E8E8] mb-4" style={{ fontFamily: "var(--font-heading)" }}>Contact Details</h3>
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <Mail className="w-5 h-5 text-[#12B5CB] mt-0.5" />
                    <div>
                      <p className="text-sm text-[#888888]">Email</p>
                      <a href="mailto:hello@omniscientai.com.au" className="text-[#E8E8E8] hover:text-[#12B5CB] transition-colors">hello@omniscientai.com.au</a>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Phone className="w-5 h-5 text-[#12B5CB] mt-0.5" />
                    <div>
                      <p className="text-sm text-[#888888]">Phone</p>
                      <a href="tel:+61412345678" className="text-[#E8E8E8] hover:text-[#12B5CB] transition-colors">+61 4 1234 5678</a>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <MapPin className="w-5 h-5 text-[#12B5CB] mt-0.5" />
                    <div>
                      <p className="text-sm text-[#888888]">Location</p>
                      <p className="text-[#E8E8E8]">Melbourne CBD, VIC 3000</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Clock className="w-5 h-5 text-[#12B5CB] mt-0.5" />
                    <div>
                      <p className="text-sm text-[#888888]">Business Hours</p>
                      <p className="text-[#E8E8E8]">Mon–Fri: 9am–5pm AEST</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="glass-card rounded-2xl p-6">
                <h3 className="text-lg font-bold text-[#E8E8E8] mb-3" style={{ fontFamily: "var(--font-heading)" }}>Follow Us</h3>
                <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 text-[#888888] hover:text-[#12B5CB] transition-colors">
                  <Linkedin className="w-5 h-5" />
                  <span className="text-sm">LinkedIn</span>
                </a>
              </div>

              <div className="glass-card rounded-2xl p-6 glow-tangerine">
                <h3 className="text-lg font-bold text-[#E8E8E8] mb-2" style={{ fontFamily: "var(--font-heading)" }}>Prefer to talk?</h3>
                <p className="text-sm text-[#888888] mb-4">Book a free 30-minute strategy session instead.</p>
                <a href="/book" className="block w-full text-center px-4 py-3 text-sm font-semibold text-[#0A0A0A] bg-[#FA903E] rounded-lg hover:bg-[#FA903E]/90 transition-all">
                  Book a Session
                </a>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
