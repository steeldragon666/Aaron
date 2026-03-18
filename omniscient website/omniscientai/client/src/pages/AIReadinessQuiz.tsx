// AI Readiness Quiz — OmniscientAI
// 10-question assessment with radar chart results and email capture
import { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Link } from "wouter";
import { ArrowRight, ArrowLeft, CheckCircle, Lock, Download } from "lucide-react";
import { QUIZ_QUESTIONS, WORKSHOPS } from "@/lib/data";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from "recharts";

type Tier = "AI Beginner" | "AI Ready" | "AI Advanced";

function getTier(score: number): { tier: Tier; color: string; description: string } {
  if (score <= 15) return { tier: "AI Beginner", color: "#FA903E", description: "Your organisation is at the start of its AI journey. Focus on building data foundations and team awareness before investing in AI tools." };
  if (score <= 28) return { tier: "AI Ready", color: "#12B5CB", description: "Your organisation has solid foundations for AI adoption. Focus on identifying high-impact use cases and building internal capability." };
  return { tier: "AI Advanced", color: "#4ADE80", description: "Your organisation is well-positioned for advanced AI initiatives. Focus on scaling successful pilots and building governance frameworks." };
}

function getRecommendations(score: number) {
  if (score <= 15) return [WORKSHOPS[0], WORKSHOPS[2]];
  if (score <= 28) return [WORKSHOPS[0], WORKSHOPS[1]];
  return [WORKSHOPS[1], WORKSHOPS[2]];
}

export default function AIReadinessQuiz() {
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [currentQ, setCurrentQ] = useState(0);
  const [showResults, setShowResults] = useState(false);
  const [email, setEmail] = useState("");
  const [emailSubmitted, setEmailSubmitted] = useState(false);

  const totalScore = useMemo(() => Object.values(answers).reduce((a, b) => a + b, 0), [answers]);
  const maxScore = QUIZ_QUESTIONS.length * 4;
  const progress = (Object.keys(answers).length / QUIZ_QUESTIONS.length) * 100;

  const categoryScores = useMemo(() => {
    const cats: Record<string, { total: number; count: number }> = {};
    QUIZ_QUESTIONS.forEach((q) => {
      if (!cats[q.category]) cats[q.category] = { total: 0, count: 0 };
      cats[q.category].count++;
      if (answers[q.id] !== undefined) cats[q.category].total += answers[q.id];
    });
    return Object.entries(cats).map(([name, { total, count }]) => ({
      category: name,
      score: Math.round((total / (count * 4)) * 100),
      fullMark: 100,
    }));
  }, [answers]);

  const handleAnswer = (questionId: number, score: number) => {
    setAnswers((prev) => ({ ...prev, [questionId]: score }));
    if (currentQ < QUIZ_QUESTIONS.length - 1) {
      setTimeout(() => setCurrentQ(currentQ + 1), 300);
    }
  };

  const handleSubmitQuiz = () => {
    if (Object.keys(answers).length === QUIZ_QUESTIONS.length) {
      setShowResults(true);
    }
  };

  const tierInfo = getTier(totalScore);
  const recommendations = getRecommendations(totalScore);
  const q = QUIZ_QUESTIONS[currentQ];

  if (showResults) {
    return (
      <section className="pt-28 pb-20">
        <div className="container max-w-4xl">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <div className="text-center mb-10">
              <span className="inline-block text-xs font-semibold uppercase tracking-[0.2em] text-[#12B5CB] mb-3" style={{ fontFamily: "var(--font-mono)" }}>YOUR RESULTS</span>
              <h1 className="text-4xl md:text-5xl font-bold text-[#E8E8E8] mb-4" style={{ fontFamily: "var(--font-heading)" }}>
                AI Readiness Score
              </h1>
            </div>

            {/* Score display */}
            <div className="glass-card rounded-2xl p-8 mb-8">
              <div className="flex flex-col md:flex-row items-center gap-8">
                <div className="text-center md:text-left flex-1">
                  <div className="text-6xl font-bold mb-2" style={{ fontFamily: "var(--font-mono)", color: tierInfo.color }}>
                    {totalScore}/{maxScore}
                  </div>
                  <div className="text-2xl font-bold text-[#E8E8E8] mb-2" style={{ fontFamily: "var(--font-heading)" }}>{tierInfo.tier}</div>
                  <p className="text-[#888888] leading-relaxed">{tierInfo.description}</p>
                </div>
                <div className="w-full md:w-80 h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={categoryScores}>
                      <PolarGrid stroke="#333333" />
                      <PolarAngleAxis dataKey="category" tick={{ fill: "#888888", fontSize: 11 }} />
                      <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} axisLine={false} />
                      <Radar name="Score" dataKey="score" stroke="#12B5CB" fill="#12B5CB" fillOpacity={0.2} strokeWidth={2} />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Category breakdown */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
              {categoryScores.map((cat) => (
                <div key={cat.category} className="glass-card rounded-xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-[#E8E8E8]">{cat.category}</span>
                    <span className="text-sm font-bold text-[#12B5CB]" style={{ fontFamily: "var(--font-mono)" }}>{cat.score}%</span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-[#333333]">
                    <div className="h-full rounded-full bg-[#12B5CB] transition-all duration-500" style={{ width: `${cat.score}%` }} />
                  </div>
                </div>
              ))}
            </div>

            {/* Email gate for full report */}
            {!emailSubmitted ? (
              <div className="glass-card rounded-2xl p-8 mb-8 glow-cyan">
                <div className="flex items-start gap-4">
                  <Lock className="w-6 h-6 text-[#12B5CB] mt-1 shrink-0" />
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-[#E8E8E8] mb-2" style={{ fontFamily: "var(--font-heading)" }}>Get Your Full AI Readiness Report</h3>
                    <p className="text-sm text-[#888888] mb-4">Enter your email to receive a detailed PDF report with personalised recommendations, industry benchmarks, and a prioritised action plan.</p>
                    <form onSubmit={(e) => { e.preventDefault(); setEmailSubmitted(true); }} className="flex flex-col sm:flex-row gap-3">
                      <input
                        type="email"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="you@company.com"
                        className="flex-1 px-4 py-3 rounded-lg bg-[#0A0A0A] border border-[#333333] text-[#E8E8E8] placeholder-[#888888] focus:border-[#12B5CB] focus:outline-none transition-colors"
                      />
                      <button type="submit" className="px-6 py-3 text-sm font-semibold text-[#0A0A0A] bg-[#12B5CB] rounded-lg hover:bg-[#12B5CB]/90 transition-all whitespace-nowrap flex items-center gap-2">
                        <Download className="w-4 h-4" /> Get Report
                      </button>
                    </form>
                  </div>
                </div>
              </div>
            ) : (
              <div className="glass-card rounded-2xl p-6 mb-8 border-[#12B5CB]/20">
                <div className="flex items-center gap-3">
                  <CheckCircle className="w-6 h-6 text-[#12B5CB]" />
                  <p className="text-[#E8E8E8]">Your full report will be sent to <strong>{email}</strong> shortly.</p>
                </div>
              </div>
            )}

            {/* Recommended workshops */}
            <div className="mb-8">
              <h3 className="text-xl font-bold text-[#E8E8E8] mb-4" style={{ fontFamily: "var(--font-heading)" }}>Recommended Workshops</h3>
              <div className="space-y-3">
                {recommendations.map((ws) => (
                  <Link key={ws.slug} href={`/workshops/${ws.slug}`}>
                    <div className="glass-card rounded-xl p-5 group flex items-center justify-between">
                      <div>
                        <h4 className="text-lg font-semibold text-[#E8E8E8]" style={{ fontFamily: "var(--font-heading)" }}>{ws.title}</h4>
                        <p className="text-sm text-[#888888]">{ws.duration} · {ws.priceRange}</p>
                      </div>
                      <ArrowRight className="w-5 h-5 text-[#12B5CB] group-hover:translate-x-1 transition-transform" />
                    </div>
                  </Link>
                ))}
              </div>
            </div>

            <div className="text-center">
              <Link href="/book" className="inline-flex items-center gap-2 px-6 py-3.5 text-sm font-semibold text-[#0A0A0A] bg-[#FA903E] rounded-lg hover:bg-[#FA903E]/90 transition-all">
                Book a Free Strategy Session <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    );
  }

  return (
    <section className="pt-28 pb-20">
      <div className="container max-w-3xl">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <span className="inline-block text-xs font-semibold uppercase tracking-[0.2em] text-[#12B5CB] mb-3" style={{ fontFamily: "var(--font-mono)" }}>AI READINESS ASSESSMENT</span>
          <h1 className="text-3xl md:text-4xl font-bold text-[#E8E8E8] mb-2" style={{ fontFamily: "var(--font-heading)" }}>
            How AI-ready is your business?
          </h1>
          <p className="text-[#888888] mb-8">Answer 10 questions to get your personalised AI Readiness Score with tailored recommendations.</p>
        </motion.div>

        {/* Progress bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-[#888888]">Question {currentQ + 1} of {QUIZ_QUESTIONS.length}</span>
            <span className="text-[#12B5CB] font-medium" style={{ fontFamily: "var(--font-mono)" }}>{Math.round(progress)}%</span>
          </div>
          <div className="w-full h-2 rounded-full bg-[#333333]">
            <motion.div
              className="h-full rounded-full bg-[#12B5CB]"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>

        {/* Question */}
        <AnimatePresence mode="wait">
          <motion.div
            key={currentQ}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            <div className="glass-card rounded-2xl p-6 md:p-8 mb-6">
              <div className="flex items-center gap-2 mb-4">
                <span className="text-xs font-medium text-[#12B5CB] px-2 py-0.5 rounded-full bg-[#12B5CB]/10">{q.category}</span>
              </div>
              <h2 className="text-xl md:text-2xl font-bold text-[#E8E8E8] mb-6" style={{ fontFamily: "var(--font-heading)" }}>
                {q.question}
              </h2>
              <div className="space-y-3">
                {q.options.map((opt, i) => (
                  <button
                    key={i}
                    onClick={() => handleAnswer(q.id, opt.score)}
                    className={`w-full text-left p-4 rounded-xl border transition-all ${
                      answers[q.id] === opt.score
                        ? "border-[#12B5CB] bg-[#12B5CB]/10 text-[#E8E8E8]"
                        : "border-[#333333] text-[#888888] hover:border-[#12B5CB]/30 hover:text-[#E8E8E8] hover:bg-white/5"
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        </AnimatePresence>

        {/* Navigation */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => setCurrentQ(Math.max(0, currentQ - 1))}
            disabled={currentQ === 0}
            className="flex items-center gap-1 text-sm text-[#888888] hover:text-[#E8E8E8] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            <ArrowLeft className="w-4 h-4" /> Previous
          </button>

          {currentQ === QUIZ_QUESTIONS.length - 1 ? (
            <button
              onClick={handleSubmitQuiz}
              disabled={Object.keys(answers).length < QUIZ_QUESTIONS.length}
              className="px-6 py-3 text-sm font-semibold text-[#0A0A0A] bg-[#FA903E] rounded-lg hover:bg-[#FA903E]/90 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              See Results <ArrowRight className="w-4 h-4" />
            </button>
          ) : (
            <button
              onClick={() => setCurrentQ(Math.min(QUIZ_QUESTIONS.length - 1, currentQ + 1))}
              className="flex items-center gap-1 text-sm text-[#12B5CB] hover:text-[#12B5CB]/80 transition-colors"
            >
              Next <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </section>
  );
}
