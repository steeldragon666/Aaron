// Privacy Policy — OmniscientAI
import { motion } from "framer-motion";

export default function PrivacyPolicy() {
  return (
    <section className="pt-28 pb-20">
      <div className="container max-w-3xl">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <h1 className="text-4xl font-bold text-[#E8E8E8] mb-2" style={{ fontFamily: "var(--font-heading)" }}>Privacy Policy</h1>
          <p className="text-sm text-white/60 mb-10" style={{ fontFamily: "var(--font-mono)" }}>Last updated: March 2026</p>

          <div className="space-y-8 text-[#E8E8E8]/80 leading-relaxed">
            <div>
              <h2 className="text-xl font-bold text-[#E8E8E8] mb-3" style={{ fontFamily: "var(--font-heading)" }}>1. Information We Collect</h2>
              <p>We collect information you provide directly to us, including your name, email address, company name, phone number, and any other information you choose to provide when filling out forms, booking sessions, or contacting us.</p>
              <p className="mt-3">We also automatically collect certain information when you visit our website, including your IP address, browser type, operating system, referring URLs, and information about how you interact with our website.</p>
            </div>

            <div>
              <h2 className="text-xl font-bold text-[#E8E8E8] mb-3" style={{ fontFamily: "var(--font-heading)" }}>2. How We Use Your Information</h2>
              <p>We use the information we collect to provide, maintain, and improve our services, to process bookings and enquiries, to send you relevant communications about our workshops and services, and to comply with legal obligations.</p>
            </div>

            <div>
              <h2 className="text-xl font-bold text-[#E8E8E8] mb-3" style={{ fontFamily: "var(--font-heading)" }}>3. Information Sharing</h2>
              <p>We do not sell, trade, or otherwise transfer your personal information to third parties. We may share information with trusted service providers who assist us in operating our website and conducting our business, provided they agree to keep this information confidential.</p>
            </div>

            <div>
              <h2 className="text-xl font-bold text-[#E8E8E8] mb-3" style={{ fontFamily: "var(--font-heading)" }}>4. Data Security</h2>
              <p>We implement appropriate technical and organisational measures to protect your personal information against unauthorised access, alteration, disclosure, or destruction. However, no method of transmission over the internet is 100% secure.</p>
            </div>

            <div>
              <h2 className="text-xl font-bold text-[#E8E8E8] mb-3" style={{ fontFamily: "var(--font-heading)" }}>5. Australian Privacy Principles</h2>
              <p>We comply with the Australian Privacy Principles (APPs) contained in the Privacy Act 1988 (Cth). You have the right to access and correct your personal information. To make a request, please contact us at hello@omniscientai.com.au.</p>
            </div>

            <div>
              <h2 className="text-xl font-bold text-[#E8E8E8] mb-3" style={{ fontFamily: "var(--font-heading)" }}>6. Cookies</h2>
              <p>Our website uses cookies and similar tracking technologies to enhance your browsing experience and analyse website traffic. You can control cookie settings through your browser preferences.</p>
            </div>

            <div>
              <h2 className="text-xl font-bold text-[#E8E8E8] mb-3" style={{ fontFamily: "var(--font-heading)" }}>7. Contact Us</h2>
              <p>If you have any questions about this Privacy Policy, please contact us at:</p>
              <p className="mt-2">
                <strong>OmniscientAI</strong><br />
                Email: hello@omniscientai.com.au<br />
                Location: Melbourne CBD, VIC 3000<br />
                ABN: 12 345 678 901
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
