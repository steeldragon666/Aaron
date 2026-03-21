// Book a Strategy Session — OmniscientAI
import { useState } from "react";
import { motion } from "framer-motion";
import { Link } from "wouter";
import { ArrowRight, Calendar, Clock, Video, MapPin, CheckCircle, Phone } from "lucide-react";
import { toast } from "sonner";

const timeSlots = ["9:00 AM", "10:00 AM", "11:00 AM", "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM"];

function getNextBusinessDays(count: number): Date[] {
  const days: Date[] = [];
  const d = new Date();
  d.setDate(d.getDate() + 1);
  while (days.length < count) {
    if (d.getDay() !== 0 && d.getDay() !== 6) days.push(new Date(d));
    d.setDate(d.getDate() + 1);
  }
  return days;
}

export default function Book() {
  const [step, setStep] = useState(1);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [selectedTime, setSelectedTime] = useState("");
  const [format, setFormat] = useState<"video" | "phone">("video");
  const [submitted, setSubmitted] = useState(false);

  const businessDays = getNextBusinessDays(10);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    toast.success("Booking confirmed! Check your email for details.");
  };

  if (submitted) {
    return (
      <section className="pt-28 pb-20">
        <div className="container max-w-2xl text-center">
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}>
            <div className="glass-card rounded-2xl p-8 md:p-12">
              <div className="w-16 h-16 rounded-full bg-[#12B5CB]/10 border border-[#12B5CB]/20 flex items-center justify-center mx-auto mb-6">
                <CheckCircle className="w-8 h-8 text-[#12B5CB]" />
              </div>
              <h1 className="text-3xl font-bold text-[#E8E8E8] mb-3" style={{ fontFamily: "var(--font-heading)" }}>Booking Confirmed</h1>
              <p className="text-white/60 mb-2">
                Your free strategy session is booked for{" "}
                <span className="text-[#E8E8E8] font-medium">
                  {selectedDate?.toLocaleDateString("en-AU", { weekday: "long", day: "numeric", month: "long" })}
                </span>{" "}
                at <span className="text-[#12B5CB] font-medium">{selectedTime}</span> (AEST).
              </p>
              <p className="text-sm text-white/60 mb-6">We've sent a confirmation email with meeting details and a brief preparation guide.</p>
              <Link href="/" className="text-[#12B5CB] hover:underline cursor-pointer">Return to homepage</Link>
            </div>
          </motion.div>
        </div>
      </section>
    );
  }

  return (
    <section className="pt-28 pb-20">
      <div className="container max-w-4xl">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="mb-10">
          <span className="inline-block text-xs font-semibold uppercase tracking-[0.2em] text-[#FA903E] mb-3" style={{ fontFamily: "var(--font-mono)" }}>BOOK A SESSION</span>
          <h1 className="text-4xl md:text-5xl font-bold text-[#E8E8E8] mb-4" style={{ fontFamily: "var(--font-heading)" }}>
            Free 30-minute <span className="text-[#FA903E]">strategy session</span>
          </h1>
          <p className="text-lg text-white/60 max-w-2xl leading-relaxed">
            No sales pitch. We'll discuss your AI goals, assess your readiness, and recommend the best path forward for your business.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-8">
          <div>
            {/* Step indicators */}
            <div className="flex items-center gap-4 mb-8">
              {[1, 2, 3].map((s) => (
                <div key={s} className="flex items-center gap-2">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                    step >= s ? "bg-[#12B5CB] text-[#0A0A0A]" : "bg-[#333333] text-white/60"
                  }`} style={{ fontFamily: "var(--font-mono)" }}>
                    {s}
                  </div>
                  <span className={`text-sm ${step >= s ? "text-[#E8E8E8]" : "text-white/60"}`}>
                    {s === 1 ? "Date & Time" : s === 2 ? "Format" : "Details"}
                  </span>
                  {s < 3 && <div className={`w-8 h-px ${step > s ? "bg-[#12B5CB]" : "bg-[#333333]"}`} />}
                </div>
              ))}
            </div>

            {/* Step 1: Date & Time */}
            {step === 1 && (
              <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="glass-card rounded-2xl p-6 md:p-8">
                <h2 className="text-xl font-bold text-[#E8E8E8] mb-6" style={{ fontFamily: "var(--font-heading)" }}>Select a date</h2>
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mb-8">
                  {businessDays.map((d) => (
                    <button
                      key={d.toISOString()}
                      onClick={() => setSelectedDate(d)}
                      className={`p-3 rounded-xl border text-center transition-all ${
                        selectedDate?.toDateString() === d.toDateString()
                          ? "border-[#12B5CB] bg-[#12B5CB]/10"
                          : "border-[#333333] hover:border-[#12B5CB]/30"
                      }`}
                    >
                      <div className="text-xs text-white/60">{d.toLocaleDateString("en-AU", { weekday: "short" })}</div>
                      <div className="text-lg font-bold text-[#E8E8E8]">{d.getDate()}</div>
                      <div className="text-xs text-white/60">{d.toLocaleDateString("en-AU", { month: "short" })}</div>
                    </button>
                  ))}
                </div>

                {selectedDate && (
                  <>
                    <h2 className="text-xl font-bold text-[#E8E8E8] mb-4" style={{ fontFamily: "var(--font-heading)" }}>Select a time (AEST)</h2>
                    <div className="grid grid-cols-3 sm:grid-cols-4 gap-3 mb-6">
                      {timeSlots.map((t) => (
                        <button
                          key={t}
                          onClick={() => setSelectedTime(t)}
                          className={`px-4 py-3 rounded-xl border text-sm font-medium transition-all ${
                            selectedTime === t
                              ? "border-[#12B5CB] bg-[#12B5CB]/10 text-[#12B5CB]"
                              : "border-[#333333] text-white/60 hover:border-[#12B5CB]/30 hover:text-[#E8E8E8]"
                          }`}
                          style={{ fontFamily: "var(--font-mono)" }}
                        >
                          {t}
                        </button>
                      ))}
                    </div>
                  </>
                )}

                <button
                  onClick={() => selectedDate && selectedTime && setStep(2)}
                  disabled={!selectedDate || !selectedTime}
                  className="px-6 py-3 text-sm font-semibold text-[#0A0A0A] bg-[#FA903E] rounded-lg hover:bg-[#FA903E]/90 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  Continue <ArrowRight className="w-4 h-4" />
                </button>
              </motion.div>
            )}

            {/* Step 2: Format */}
            {step === 2 && (
              <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="glass-card rounded-2xl p-6 md:p-8">
                <h2 className="text-xl font-bold text-[#E8E8E8] mb-6" style={{ fontFamily: "var(--font-heading)" }}>Meeting format</h2>
                <div className="space-y-3 mb-6">
                  <button
                    onClick={() => setFormat("video")}
                    className={`w-full p-4 rounded-xl border flex items-center gap-4 transition-all ${
                      format === "video" ? "border-[#12B5CB] bg-[#12B5CB]/10" : "border-[#333333] hover:border-[#12B5CB]/30"
                    }`}
                  >
                    <Video className="w-6 h-6 text-[#12B5CB]" />
                    <div className="text-left">
                      <p className="text-[#E8E8E8] font-medium">Video Call</p>
                      <p className="text-sm text-white/60">Google Meet or Zoom — link provided after booking</p>
                    </div>
                  </button>
                  <button
                    onClick={() => setFormat("phone")}
                    className={`w-full p-4 rounded-xl border flex items-center gap-4 transition-all ${
                      format === "phone" ? "border-[#12B5CB] bg-[#12B5CB]/10" : "border-[#333333] hover:border-[#12B5CB]/30"
                    }`}
                  >
                    <Phone className="w-6 h-6 text-[#12B5CB]" />
                    <div className="text-left">
                      <p className="text-[#E8E8E8] font-medium">Phone Call</p>
                      <p className="text-sm text-white/60">We'll call you at your provided number</p>
                    </div>
                  </button>
                </div>
                <div className="flex gap-3">
                  <button onClick={() => setStep(1)} className="px-4 py-3 text-sm text-white/60 hover:text-[#E8E8E8] transition-colors cursor-pointer">Back</button>
                  <button
                    onClick={() => setStep(3)}
                    className="px-6 py-3 text-sm font-semibold text-[#0A0A0A] bg-[#FA903E] rounded-lg hover:bg-[#FA903E]/90 transition-all flex items-center gap-2"
                  >
                    Continue <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </motion.div>
            )}

            {/* Step 3: Details */}
            {step === 3 && (
              <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
                <form onSubmit={handleSubmit} className="glass-card rounded-2xl p-6 md:p-8 space-y-5">
                  <h2 className="text-xl font-bold text-[#E8E8E8] mb-2" style={{ fontFamily: "var(--font-heading)" }}>Your details</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div>
                      <label className="block text-sm font-medium text-[#E8E8E8] mb-2">Name *</label>
                      <input required type="text" className="w-full px-4 py-3 rounded-lg bg-[#0A0A0A] border border-[#333333] text-[#E8E8E8] placeholder-white/40 focus:border-[#12B5CB] focus:outline-none transition-colors" placeholder="Your name" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-[#E8E8E8] mb-2">Email *</label>
                      <input required type="email" className="w-full px-4 py-3 rounded-lg bg-[#0A0A0A] border border-[#333333] text-[#E8E8E8] placeholder-white/40 focus:border-[#12B5CB] focus:outline-none transition-colors" placeholder="you@company.com" />
                    </div>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div>
                      <label className="block text-sm font-medium text-[#E8E8E8] mb-2">Company</label>
                      <input type="text" className="w-full px-4 py-3 rounded-lg bg-[#0A0A0A] border border-[#333333] text-[#E8E8E8] placeholder-white/40 focus:border-[#12B5CB] focus:outline-none transition-colors" placeholder="Company name" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-[#E8E8E8] mb-2">Phone</label>
                      <input type="tel" className="w-full px-4 py-3 rounded-lg bg-[#0A0A0A] border border-[#333333] text-[#E8E8E8] placeholder-white/40 focus:border-[#12B5CB] focus:outline-none transition-colors" placeholder="04XX XXX XXX" />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-[#E8E8E8] mb-2">What would you like to discuss?</label>
                    <textarea rows={3} className="w-full px-4 py-3 rounded-lg bg-[#0A0A0A] border border-[#333333] text-[#E8E8E8] placeholder-white/40 focus:border-[#12B5CB] focus:outline-none transition-colors resize-none" placeholder="Tell us about your AI goals, challenges, or questions..." />
                  </div>
                  <div className="flex gap-3">
                    <button type="button" onClick={() => setStep(2)} className="px-4 py-3 text-sm text-white/60 hover:text-[#E8E8E8] transition-colors cursor-pointer">Back</button>
                    <button type="submit" className="px-6 py-3.5 text-sm font-semibold text-[#0A0A0A] bg-[#FA903E] rounded-lg hover:bg-[#FA903E]/90 transition-all flex items-center gap-2">
                      Confirm Booking <CheckCircle className="w-4 h-4" />
                    </button>
                  </div>
                </form>
              </motion.div>
            )}
          </div>

          {/* Sidebar summary */}
          <div>
            <div className="lg:sticky lg:top-24">
              <div className="glass-card rounded-2xl p-6">
                <h3 className="text-lg font-bold text-[#E8E8E8] mb-4" style={{ fontFamily: "var(--font-heading)" }}>Session Summary</h3>
                <div className="space-y-3 text-sm">
                  <div className="flex items-center gap-3">
                    <Calendar className="w-4 h-4 text-[#12B5CB]" />
                    <span className="text-[#E8E8E8]">
                      {selectedDate ? selectedDate.toLocaleDateString("en-AU", { weekday: "long", day: "numeric", month: "long" }) : "Select a date"}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Clock className="w-4 h-4 text-[#12B5CB]" />
                    <span className="text-[#E8E8E8]">{selectedTime || "Select a time"} (AEST)</span>
                  </div>
                  <div className="flex items-center gap-3">
                    {format === "video" ? <Video className="w-4 h-4 text-[#12B5CB]" /> : <Phone className="w-4 h-4 text-[#12B5CB]" />}
                    <span className="text-[#E8E8E8]">{format === "video" ? "Video Call" : "Phone Call"}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Clock className="w-4 h-4 text-[#12B5CB]" />
                    <span className="text-[#E8E8E8]">30 minutes</span>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-[#333333]/50">
                  <p className="text-xs text-white/60">This is a free, no-obligation strategy session. We'll discuss your goals and recommend the best path forward.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
