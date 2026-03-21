// AI ROI Calculator — OmniscientAI
import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import { Link } from "wouter";
import { ArrowRight, Calculator, DollarSign, Clock, TrendingUp } from "lucide-react";

const industries = [
  { value: "professional-services", label: "Professional Services", automationRate: 0.35 },
  { value: "healthcare", label: "Healthcare", automationRate: 0.30 },
  { value: "manufacturing", label: "Manufacturing", automationRate: 0.40 },
  { value: "retail", label: "Retail", automationRate: 0.32 },
  { value: "other", label: "Other", automationRate: 0.28 },
];

export default function ROICalculator() {
  const [employees, setEmployees] = useState(20);
  const [hoursManual, setHoursManual] = useState(10);
  const [hourlyRate, setHourlyRate] = useState(65);
  const [industry, setIndustry] = useState("professional-services");

  const results = useMemo(() => {
    const ind = industries.find((i) => i.value === industry) || industries[4];
    const weeklyManualCost = employees * hoursManual * hourlyRate;
    const annualManualCost = weeklyManualCost * 48;
    const timeSaved = hoursManual * ind.automationRate;
    const weeklySavings = employees * timeSaved * hourlyRate;
    const annualSavings = weeklySavings * 48;
    const implementationCost = employees * 500 + 5000;
    const roi = ((annualSavings - implementationCost) / implementationCost) * 100;
    return {
      timeSavedPerPerson: timeSaved.toFixed(1),
      totalTimeSavedWeekly: (employees * timeSaved).toFixed(0),
      weeklySavings: weeklySavings.toFixed(0),
      annualSavings: annualSavings.toFixed(0),
      estimatedCost: implementationCost.toFixed(0),
      roi: roi.toFixed(0),
      automationRate: (ind.automationRate * 100).toFixed(0),
    };
  }, [employees, hoursManual, hourlyRate, industry]);

  const fmt = (n: string) => "$" + Number(n).toLocaleString();

  return (
    <section className="pt-28 pb-20">
      <div className="container max-w-5xl">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="mb-10">
          <span className="inline-block text-xs font-semibold uppercase tracking-[0.2em] text-[#FA903E] mb-3" style={{ fontFamily: "var(--font-mono)" }}>ROI CALCULATOR</span>
          <h1 className="text-4xl md:text-5xl font-bold text-[#E8E8E8] mb-4" style={{ fontFamily: "var(--font-heading)" }}>
            Calculate your <span className="text-[#FA903E]">AI ROI</span>
          </h1>
          <p className="text-lg text-white/60 max-w-2xl leading-relaxed">
            Estimate the potential time and cost savings from AI adoption for your business. Adjust the inputs to match your organisation.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Inputs */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.1 }}>
            <div className="glass-card rounded-2xl p-6 md:p-8 space-y-6">
              <h2 className="text-xl font-bold text-[#E8E8E8]" style={{ fontFamily: "var(--font-heading)" }}>Your Business</h2>

              <div>
                <label className="flex items-center justify-between text-sm font-medium text-[#E8E8E8] mb-2">
                  <span>Number of employees</span>
                  <span className="text-[#12B5CB]" style={{ fontFamily: "var(--font-mono)" }}>{employees}</span>
                </label>
                <input
                  type="range"
                  min={1}
                  max={200}
                  value={employees}
                  onChange={(e) => setEmployees(Number(e.target.value))}
                  className="w-full h-2 rounded-full appearance-none bg-[#333333] accent-[#12B5CB]"
                />
                <div className="flex justify-between text-xs text-white/60 mt-1"><span>1</span><span>200</span></div>
              </div>

              <div>
                <label className="flex items-center justify-between text-sm font-medium text-[#E8E8E8] mb-2">
                  <span>Hours on manual tasks / person / week</span>
                  <span className="text-[#12B5CB]" style={{ fontFamily: "var(--font-mono)" }}>{hoursManual}h</span>
                </label>
                <input
                  type="range"
                  min={1}
                  max={40}
                  value={hoursManual}
                  onChange={(e) => setHoursManual(Number(e.target.value))}
                  className="w-full h-2 rounded-full appearance-none bg-[#333333] accent-[#12B5CB]"
                />
                <div className="flex justify-between text-xs text-white/60 mt-1"><span>1h</span><span>40h</span></div>
              </div>

              <div>
                <label className="flex items-center justify-between text-sm font-medium text-[#E8E8E8] mb-2">
                  <span>Average hourly rate (AUD)</span>
                  <span className="text-[#12B5CB]" style={{ fontFamily: "var(--font-mono)" }}>${hourlyRate}</span>
                </label>
                <input
                  type="range"
                  min={25}
                  max={250}
                  step={5}
                  value={hourlyRate}
                  onChange={(e) => setHourlyRate(Number(e.target.value))}
                  className="w-full h-2 rounded-full appearance-none bg-[#333333] accent-[#12B5CB]"
                />
                <div className="flex justify-between text-xs text-white/60 mt-1"><span>$25</span><span>$250</span></div>
              </div>

              <div>
                <label className="block text-sm font-medium text-[#E8E8E8] mb-2">Industry sector</label>
                <select
                  value={industry}
                  onChange={(e) => setIndustry(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg bg-[#0A0A0A] border border-[#333333] text-[#E8E8E8] focus:border-[#12B5CB] focus:outline-none transition-colors"
                >
                  {industries.map((ind) => (
                    <option key={ind.value} value={ind.value}>{ind.label}</option>
                  ))}
                </select>
              </div>
            </div>
          </motion.div>

          {/* Results */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.2 }}>
            <div className="glass-card rounded-2xl p-6 md:p-8 glow-cyan">
              <h2 className="text-xl font-bold text-[#E8E8E8] mb-6" style={{ fontFamily: "var(--font-heading)" }}>Estimated Results</h2>

              <div className="space-y-6">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-xl bg-[#12B5CB]/10 border border-[#12B5CB]/20 flex items-center justify-center shrink-0">
                    <Clock className="w-5 h-5 text-[#12B5CB]" />
                  </div>
                  <div>
                    <p className="text-sm text-white/60">Time saved per person per week</p>
                    <p className="text-2xl font-bold text-[#12B5CB]" style={{ fontFamily: "var(--font-mono)" }}>{results.timeSavedPerPerson} hours</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-xl bg-[#12B5CB]/10 border border-[#12B5CB]/20 flex items-center justify-center shrink-0">
                    <DollarSign className="w-5 h-5 text-[#12B5CB]" />
                  </div>
                  <div>
                    <p className="text-sm text-white/60">Estimated annual savings</p>
                    <p className="text-3xl font-bold text-[#12B5CB]" style={{ fontFamily: "var(--font-mono)" }}>{fmt(results.annualSavings)}</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-xl bg-[#FA903E]/10 border border-[#FA903E]/20 flex items-center justify-center shrink-0">
                    <TrendingUp className="w-5 h-5 text-[#FA903E]" />
                  </div>
                  <div>
                    <p className="text-sm text-white/60">Estimated ROI (first year)</p>
                    <p className="text-3xl font-bold text-[#FA903E]" style={{ fontFamily: "var(--font-mono)" }}>{results.roi}%</p>
                  </div>
                </div>

                <div className="border-t border-[#333333]/50 pt-4 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-white/60">Total hours saved / week</span>
                    <span className="text-[#E8E8E8]" style={{ fontFamily: "var(--font-mono)" }}>{results.totalTimeSavedWeekly}h</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-white/60">Weekly cost savings</span>
                    <span className="text-[#E8E8E8]" style={{ fontFamily: "var(--font-mono)" }}>{fmt(results.weeklySavings)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-white/60">Est. implementation cost</span>
                    <span className="text-[#E8E8E8]" style={{ fontFamily: "var(--font-mono)" }}>{fmt(results.estimatedCost)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-white/60">Industry automation rate</span>
                    <span className="text-[#E8E8E8]" style={{ fontFamily: "var(--font-mono)" }}>{results.automationRate}%</span>
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-6 border-t border-[#333333]/50">
                <p className="text-xs text-white/60 mb-4">These are estimates based on industry benchmarks. Actual results vary based on implementation quality and use case selection.</p>
                <Link
                  href="/book"
                  className="block w-full text-center px-6 py-3.5 text-sm font-semibold text-[#0A0A0A] bg-[#FA903E] rounded-lg hover:bg-[#FA903E]/90 transition-all cursor-pointer"
                >
                  Discuss Your AI Opportunity
                </Link>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
