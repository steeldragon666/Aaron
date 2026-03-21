// Footer — OmniscientAI Luminous Depth
// Melbourne-specific footer with ABN, address, map, and links
import { Link } from "wouter";
import { BRAND } from "@/lib/data";
import { Mail, Phone, MapPin } from "lucide-react";
import Logo from "./Logo";

export default function Footer() {
  return (
    <footer className="bg-[#050505] border-t border-white/5">
      <div className="container section-padding">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-16">
          {/* Brand */}
          <div className="lg:col-span-1">
            <Link href="/" className="inline-block hover:opacity-90 transition-opacity mb-6 cursor-pointer">
              <Logo iconOnly={false} />
            </Link>
            <p className="text-base text-white/60 leading-relaxed mb-8 max-w-sm">
              Melbourne's leading vendor-neutral AI training and consulting for SMEs. Practical skills, not vendor hype.
            </p>
            <div className="space-y-4 text-sm font-medium">
              <a href={`mailto:${BRAND.email}`} className="flex items-center gap-3 text-white/60 hover:text-[#12B5CB] transition-colors cursor-pointer">
                <div className="w-8 h-8 rounded-full bg-white/5 border border-white/10 flex items-center justify-center">
                  <Mail className="w-4 h-4" />
                </div>
                {BRAND.email}
              </a>
              <a href={`tel:${BRAND.phone}`} className="flex items-center gap-3 text-white/60 hover:text-[#12B5CB] transition-colors cursor-pointer">
                <div className="w-8 h-8 rounded-full bg-white/5 border border-white/10 flex items-center justify-center">
                  <Phone className="w-4 h-4" />
                </div>
                {BRAND.phone}
              </a>
              <div className="flex items-start gap-3 text-white/60">
                <div className="w-8 h-8 rounded-full bg-white/5 border border-white/10 flex items-center justify-center shrink-0">
                  <MapPin className="w-4 h-4" />
                </div>
                <span className="leading-relaxed">{BRAND.address}</span>
              </div>
            </div>
          </div>

          {/* Workshops */}
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-[0.2em] mb-8">Workshops</h4>
            <ul className="space-y-4">
              <li><Link href="/workshops/ai-for-business-leaders" className="text-sm text-white/60 hover:text-[#12B5CB] transition-colors cursor-pointer">AI for Business Leaders</Link></li>
              <li><Link href="/workshops/microsoft-copilot-masterclass" className="text-sm text-white/60 hover:text-[#12B5CB] transition-colors cursor-pointer">Copilot Masterclass</Link></li>
              <li><Link href="/workshops/ai-governance-essentials" className="text-sm text-white/60 hover:text-[#12B5CB] transition-colors cursor-pointer">Governance Essentials</Link></li>
              <li><Link href="/workshops/custom" className="text-sm text-white/60 hover:text-[#12B5CB] transition-colors cursor-pointer">Custom Workshop</Link></li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-[0.2em] mb-8">Company</h4>
            <ul className="space-y-4">
              <li><Link href="/about" className="text-sm text-white/60 hover:text-[#12B5CB] transition-colors cursor-pointer">About Us</Link></li>
              <li><Link href="/about/approach" className="text-sm text-white/60 hover:text-[#12B5CB] transition-colors cursor-pointer">Our Approach</Link></li>
              <li><Link href="/insights" className="text-sm text-white/60 hover:text-[#12B5CB] transition-colors cursor-pointer">Insights</Link></li>
              <li><Link href="/contact" className="text-sm text-white/60 hover:text-[#12B5CB] transition-colors cursor-pointer">Contact</Link></li>
              <li><Link href="/book" className="text-sm text-white/60 hover:text-[#12B5CB] transition-colors cursor-pointer">Book a Session</Link></li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-[0.2em] mb-8">Resources</h4>
            <ul className="space-y-4">
              <li><Link href="/ai-readiness-quiz" className="text-sm text-white/60 hover:text-[#12B5CB] transition-colors cursor-pointer">AI Readiness Quiz</Link></li>
              <li><Link href="/roi-calculator" className="text-sm text-white/60 hover:text-[#12B5CB] transition-colors cursor-pointer">AI ROI Calculator</Link></li>
              <li><Link href="/services/ai-strategy-consulting" className="text-sm text-white/60 hover:text-[#12B5CB] transition-colors cursor-pointer">Strategy Consulting</Link></li>
              <li><Link href="/services/ai-readiness-assessment" className="text-sm text-white/60 hover:text-[#12B5CB] transition-colors cursor-pointer">Readiness Assessment</Link></li>
            </ul>
          </div>
        </div>

        {/* Google Maps Embed */}
        <div className="mt-20 rounded-[2rem] overflow-hidden border border-white/5 group">
          <iframe
            src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3151.835434509374!2d144.9559283!3d-37.8172099!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x6ad65d4c2b349649%3A0xb6899234e561db11!2s440%20Collins%20St%2C%20Melbourne%20VIC%203000!5e0!3m2!1sen!2sau!4v1700000000000!5m2!1sen!2sau"
            width="100%"
            height="300"
            style={{ border: 0, filter: "invert(95%) hue-rotate(180deg) brightness(0.7) contrast(1.2)" }}
            allowFullScreen
            loading="lazy"
            referrerPolicy="no-referrer-when-downgrade"
            title="OmniscientAI Office Location"
            className="group-hover:scale-[1.01] transition-transform duration-700"
          />
        </div>

        {/* Bottom bar */}
        <div className="mt-20 pt-8 border-t border-white/5 flex flex-col md:flex-row items-center justify-between gap-6">
          <p className="text-xs font-bold uppercase tracking-widest text-white/30">
            &copy; {new Date().getFullYear()} OmniscientAI &middot; ABN {BRAND.abn}
          </p>
          <div className="flex items-center gap-8">
            <Link href="/privacy-policy" className="text-xs font-bold uppercase tracking-widest text-white/30 hover:text-[#12B5CB] transition-colors cursor-pointer">Privacy</Link>
            <Link href="/terms" className="text-xs font-bold uppercase tracking-widest text-white/30 hover:text-[#12B5CB] transition-colors cursor-pointer">Terms</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
