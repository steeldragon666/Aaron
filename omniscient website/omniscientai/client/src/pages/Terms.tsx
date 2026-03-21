// Terms of Service — OmniscientAI
import { motion } from "framer-motion";

export default function Terms() {
  return (
    <section className="pt-28 pb-20">
      <div className="container max-w-3xl">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <h1 className="text-4xl font-bold text-[#E8E8E8] mb-2" style={{ fontFamily: "var(--font-heading)" }}>Terms of Service</h1>
          <p className="text-sm text-white/60 mb-10" style={{ fontFamily: "var(--font-mono)" }}>Last updated: March 2026</p>

          <div className="space-y-8 text-[#E8E8E8]/80 leading-relaxed">
            <div>
              <h2 className="text-xl font-bold text-[#E8E8E8] mb-3" style={{ fontFamily: "var(--font-heading)" }}>1. Services</h2>
              <p>OmniscientAI provides AI training workshops, consulting services, and related educational content for businesses. Our services are designed to help organisations understand, evaluate, and implement AI solutions in a vendor-neutral manner.</p>
            </div>

            <div>
              <h2 className="text-xl font-bold text-[#E8E8E8] mb-3" style={{ fontFamily: "var(--font-heading)" }}>2. Booking and Payment</h2>
              <p>Workshop bookings are confirmed upon receipt of payment or a signed agreement. Prices are quoted in Australian Dollars (AUD) and are exclusive of GST unless otherwise stated. We accept payment via bank transfer and major credit cards.</p>
            </div>

            <div>
              <h2 className="text-xl font-bold text-[#E8E8E8] mb-3" style={{ fontFamily: "var(--font-heading)" }}>3. Cancellation Policy</h2>
              <p>Cancellations made more than 14 days before the scheduled workshop will receive a full refund. Cancellations made 7–14 days before will receive a 50% refund. Cancellations made less than 7 days before are non-refundable. Rescheduling is available at no additional cost with at least 7 days' notice.</p>
            </div>

            <div>
              <h2 className="text-xl font-bold text-[#E8E8E8] mb-3" style={{ fontFamily: "var(--font-heading)" }}>4. Intellectual Property</h2>
              <p>All workshop materials, content, and resources provided by OmniscientAI remain our intellectual property. Participants may use materials for internal business purposes but may not redistribute, resell, or publish them without written permission.</p>
            </div>

            <div>
              <h2 className="text-xl font-bold text-[#E8E8E8] mb-3" style={{ fontFamily: "var(--font-heading)" }}>5. Limitation of Liability</h2>
              <p>Our workshops and consulting services provide general guidance and training. We do not guarantee specific business outcomes. Our liability is limited to the fees paid for the specific service in question. We are not liable for any indirect, consequential, or incidental damages.</p>
            </div>

            <div>
              <h2 className="text-xl font-bold text-[#E8E8E8] mb-3" style={{ fontFamily: "var(--font-heading)" }}>6. Vendor Neutrality</h2>
              <p>OmniscientAI maintains vendor neutrality in all our training and consulting engagements. We do not receive commissions or referral fees from AI tool vendors. Any tool recommendations are based solely on suitability for the client's needs.</p>
            </div>

            <div>
              <h2 className="text-xl font-bold text-[#E8E8E8] mb-3" style={{ fontFamily: "var(--font-heading)" }}>7. Governing Law</h2>
              <p>These terms are governed by the laws of the State of Victoria, Australia. Any disputes will be resolved in the courts of Victoria.</p>
            </div>

            <div>
              <h2 className="text-xl font-bold text-[#E8E8E8] mb-3" style={{ fontFamily: "var(--font-heading)" }}>8. Contact</h2>
              <p>For questions about these terms, contact us at hello@omniscientai.com.au.</p>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
