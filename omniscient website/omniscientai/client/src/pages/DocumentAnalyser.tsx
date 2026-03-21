import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  FileText,
  Upload,
  Sparkles,
  ArrowRight,
  BarChart3,
  Clock,
  Lightbulb,
  Target,
  Zap,
  BookOpen,
  Code,
  MessageCircle,
  CheckCircle2,
  AlertTriangle,
  X,
} from "lucide-react";
import { trpc } from "@/lib/trpc";
import { Link } from "wouter";
import LeadGate from "@/components/LeadGate";

type AnalysisResult = {
  summary: string;
  opportunities: string[];
  scores: {
    automationPotential: number;
    dataMaturity: number;
    processEfficiency: number;
    aiReadiness: number;
  };
  timeSavingsHoursPerWeek: number;
  recommendedWorkshops: string[];
  recommendations: string[];
};

const WORKSHOP_MAP: Record<string, { title: string; href: string; color: string }> = {
  "ai-for-business-leaders": {
    title: "AI for Business Leaders",
    href: "/workshops/ai-for-business-leaders",
    color: "#12B5CB",
  },
  "hands-on-prompt-engineering": {
    title: "Hands-On Prompt Engineering",
    href: "/workshops/hands-on-prompt-engineering",
    color: "#FA903E",
  },
  "ai-powered-workflows": {
    title: "AI-Powered Workflows",
    href: "/workshops/ai-powered-workflows",
    color: "#12B5CB",
  },
};

function ScoreBar({ label, value, delay }: { label: string; value: number; delay: number }) {
  const getColor = (v: number) => {
    if (v >= 70) return "#12B5CB";
    if (v >= 40) return "#FA903E";
    return "#ef4444";
  };

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <span className="text-xs text-white/60">{label}</span>
        <span className="text-xs font-semibold" style={{ color: getColor(value), fontFamily: "var(--font-mono)" }}>
          {value}%
        </span>
      </div>
      <div className="h-2 bg-[#1A1A1A] rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 1, delay, ease: "easeOut" }}
          className="h-full rounded-full"
          style={{ backgroundColor: getColor(value) }}
        />
      </div>
    </div>
  );
}

function ResultsDashboard({ result }: { result: AnalysisResult }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="space-y-6"
    >
      {/* Summary */}
      <div className="glass-card rounded-2xl p-6">
        <div className="flex items-center gap-2 mb-3">
          <FileText className="w-5 h-5 text-[#12B5CB]" />
          <h3 className="text-sm font-semibold text-[#E8E8E8]" style={{ fontFamily: "var(--font-heading)" }}>
            Document Summary
          </h3>
        </div>
        <p className="text-sm text-white/60 leading-relaxed">{result.summary}</p>
      </div>

      {/* Scores Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Score bars */}
        <div className="glass-card rounded-2xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="w-5 h-5 text-[#12B5CB]" />
            <h3 className="text-sm font-semibold text-[#E8E8E8]" style={{ fontFamily: "var(--font-heading)" }}>
              AI Readiness Scores
            </h3>
          </div>
          <div className="space-y-4">
            <ScoreBar label="Automation Potential" value={result.scores.automationPotential} delay={0.2} />
            <ScoreBar label="Data Maturity" value={result.scores.dataMaturity} delay={0.4} />
            <ScoreBar label="Process Efficiency" value={result.scores.processEfficiency} delay={0.6} />
            <ScoreBar label="AI Readiness" value={result.scores.aiReadiness} delay={0.8} />
          </div>
        </div>

        {/* Time savings + opportunities */}
        <div className="space-y-4">
          {/* Time savings */}
          <div className="glass-card rounded-2xl p-6">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="w-5 h-5 text-[#FA903E]" />
              <h3 className="text-sm font-semibold text-[#E8E8E8]" style={{ fontFamily: "var(--font-heading)" }}>
                Estimated Time Savings
              </h3>
            </div>
            <div className="flex items-baseline gap-1">
              <motion.span
                initial={{ opacity: 0, scale: 0.5 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.5 }}
                className="text-4xl font-bold text-[#FA903E]"
                style={{ fontFamily: "var(--font-heading)" }}
              >
                {result.timeSavingsHoursPerWeek}
              </motion.span>
              <span className="text-sm text-white/60">hours/week</span>
            </div>
            <p className="text-xs text-[#666666] mt-1">
              That's ~{Math.round(result.timeSavingsHoursPerWeek * 52)} hours per year your team could save with AI automation.
            </p>
          </div>

          {/* Opportunities */}
          <div className="glass-card rounded-2xl p-6">
            <div className="flex items-center gap-2 mb-3">
              <Lightbulb className="w-5 h-5 text-[#12B5CB]" />
              <h3 className="text-sm font-semibold text-[#E8E8E8]" style={{ fontFamily: "var(--font-heading)" }}>
                AI Opportunities
              </h3>
            </div>
            <div className="space-y-2">
              {result.opportunities.map((opp, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + i * 0.1 }}
                  className="flex items-start gap-2"
                >
                  <CheckCircle2 className="w-3.5 h-3.5 text-[#12B5CB] shrink-0 mt-0.5" />
                  <span className="text-xs text-white/60 leading-relaxed">{opp}</span>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="glass-card rounded-2xl p-6">
        <div className="flex items-center gap-2 mb-4">
          <Target className="w-5 h-5 text-[#FA903E]" />
          <h3 className="text-sm font-semibold text-[#E8E8E8]" style={{ fontFamily: "var(--font-heading)" }}>
            Key Recommendations
          </h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {result.recommendations.map((rec, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 + i * 0.1 }}
              className="flex items-start gap-3 p-3 rounded-xl bg-[#1A1A1A]/50 border border-[#333333]/30"
            >
              <span className="text-xs font-bold text-[#12B5CB] shrink-0 mt-0.5" style={{ fontFamily: "var(--font-mono)" }}>
                {String(i + 1).padStart(2, "0")}
              </span>
              <span className="text-xs text-white/60 leading-relaxed">{rec}</span>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Recommended Workshops */}
      {result.recommendedWorkshops.length > 0 && (
        <div className="glass-card rounded-2xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <BookOpen className="w-5 h-5 text-[#12B5CB]" />
            <h3 className="text-sm font-semibold text-[#E8E8E8]" style={{ fontFamily: "var(--font-heading)" }}>
              Recommended Workshops
            </h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {result.recommendedWorkshops.map((ws) => {
              const info = WORKSHOP_MAP[ws];
              if (!info) return null;
              return (
                <Link key={ws} href={info.href}>
                  <div className="p-4 rounded-xl bg-[#1A1A1A]/50 border border-[#333333]/30 hover:border-[#12B5CB]/30 transition-all group cursor-pointer">
                    <p className="text-sm font-medium text-[#E8E8E8] group-hover:text-[#12B5CB] transition-colors mb-1">
                      {info.title}
                    </p>
                    <span className="inline-flex items-center gap-1 text-xs text-[#12B5CB]">
                      Learn more <ArrowRight className="w-3 h-3" />
                    </span>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      )}

      {/* CTA */}
      <div className="glass-card rounded-2xl p-6 border-[#FA903E]/20 text-center">
        <h3 className="text-lg font-semibold text-[#E8E8E8] mb-2" style={{ fontFamily: "var(--font-heading)" }}>
          Ready to act on these insights?
        </h3>
        <p className="text-sm text-white/60 mb-4 max-w-lg mx-auto">
          Book a free strategy session to discuss your analysis results and create a tailored AI implementation roadmap.
        </p>
        <Link
          href="/book"
          className="inline-flex items-center gap-2 px-6 py-3 text-sm font-semibold text-[#0A0A0A] bg-[#FA903E] rounded-xl hover:bg-[#FA903E]/90 transition-all"
        >
          Book a Free Strategy Session <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </motion.div>
  );
}

function AnalyserContent() {
  const [file, setFile] = useState<File | null>(null);
  const [textContent, setTextContent] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState("");
  const [inputMode, setInputMode] = useState<"file" | "text">("file");

  const analyseMutation = trpc.documentAnalyser.analyse.useMutation({
    onSuccess: (data) => {
      setResult(data as AnalysisResult);
    },
    onError: (err) => {
      setError(err.message || "Analysis failed. Please try again.");
    },
  });

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      setFile(droppedFile);
      setError("");
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError("");
    }
  };

  const handleAnalyse = async () => {
    setError("");

    if (inputMode === "text") {
      if (!textContent.trim()) {
        setError("Please paste some document text to analyse.");
        return;
      }
      analyseMutation.mutate({ documentText: textContent, fileName: "pasted-text" });
      return;
    }

    if (!file) {
      setError("Please upload a file first.");
      return;
    }

    try {
      const text = await file.text();
      if (text.length < 10) {
        setError("The file appears to be empty or too short to analyse.");
        return;
      }
      // Truncate very long documents
      const truncated = text.length > 15000 ? text.slice(0, 15000) + "\n\n[Document truncated for analysis — first 15,000 characters shown]" : text;
      analyseMutation.mutate({ documentText: truncated, fileName: file.name });
    } catch {
      setError("Could not read the file. Please try a text-based file (.txt, .csv, .md) or paste the content directly.");
    }
  };

  const handleReset = () => {
    setFile(null);
    setTextContent("");
    setResult(null);
    setError("");
    analyseMutation.reset();
  };

  if (result) {
    return (
      <div>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-[#E8E8E8]" style={{ fontFamily: "var(--font-heading)" }}>
            Analysis Results
          </h2>
          <button
            onClick={handleReset}
            className="text-xs text-white/60 hover:text-[#12B5CB] transition-colors flex items-center gap-1 cursor-pointer"
          >
            Analyse another document
          </button>
        </div>
        <ResultsDashboard result={result} />
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Upload area */}
      <div className="lg:col-span-2 space-y-4">
        {/* Mode toggle */}
        <div className="flex gap-2">
          <button
            onClick={() => setInputMode("file")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-medium transition-all ${
              inputMode === "file"
                ? "bg-[#12B5CB]/10 text-[#12B5CB] border border-[#12B5CB]/20"
                : "text-white/60 border border-[#333333] hover:border-[#12B5CB]/20"
            }`}
          >
            <Upload className="w-3.5 h-3.5" /> Upload File
          </button>
          <button
            onClick={() => setInputMode("text")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-medium transition-all ${
              inputMode === "text"
                ? "bg-[#12B5CB]/10 text-[#12B5CB] border border-[#12B5CB]/20"
                : "text-white/60 border border-[#333333] hover:border-[#12B5CB]/20"
            }`}
          >
            <FileText className="w-3.5 h-3.5" /> Paste Text
          </button>
        </div>

        {inputMode === "file" ? (
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`glass-card rounded-2xl p-8 md:p-12 text-center transition-all cursor-pointer ${
              isDragging ? "border-[#12B5CB]/50 bg-[#12B5CB]/5" : ""
            }`}
            onClick={() => document.getElementById("file-input")?.click()}
          >
            <input
              id="file-input"
              type="file"
              onChange={handleFileChange}
              accept=".txt,.csv,.md,.json,.xml,.html,.log,.doc,.docx"
              className="hidden"
            />

            {file ? (
              <div className="space-y-3">
                <div className="w-16 h-16 rounded-2xl bg-[#12B5CB]/10 border border-[#12B5CB]/20 flex items-center justify-center mx-auto">
                  <FileText className="w-7 h-7 text-[#12B5CB]" />
                </div>
                <div>
                  <p className="text-sm font-medium text-[#E8E8E8]">{file.name}</p>
                  <p className="text-xs text-white/60">{(file.size / 1024).toFixed(1)} KB</p>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setFile(null);
                  }}
                  className="inline-flex items-center gap-1 text-xs text-white/60 hover:text-red-400 transition-colors cursor-pointer"
                >
                  <X className="w-3 h-3" /> Remove
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="w-16 h-16 rounded-2xl bg-[#1A1A1A] border border-[#333333] border-dashed flex items-center justify-center mx-auto">
                  <Upload className="w-7 h-7 text-white/60" />
                </div>
                <div>
                  <p className="text-sm text-[#E8E8E8]">
                    Drop your file here or <span className="text-[#12B5CB]">click to browse</span>
                  </p>
                  <p className="text-xs text-[#666666] mt-1">
                    Supports .txt, .csv, .md, .json, .xml, .html, .log files
                  </p>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="glass-card rounded-2xl p-5">
            <textarea
              value={textContent}
              onChange={(e) => setTextContent(e.target.value)}
              placeholder="Paste your business document, process description, meeting notes, or any text you'd like analysed for AI opportunities..."
              className="w-full min-h-[300px] bg-transparent text-sm text-[#E8E8E8] placeholder-[#555555] resize-none focus:outline-none leading-relaxed"
              style={{ fontFamily: "var(--font-mono)" }}
            />
            <div className="text-right mt-2">
              <span className="text-[10px] text-[#666666]" style={{ fontFamily: "var(--font-mono)" }}>
                {textContent.length} chars
              </span>
            </div>
          </div>
        )}

        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="flex items-center gap-2 p-3 rounded-xl bg-red-500/10 border border-red-500/20"
            >
              <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />
              <p className="text-xs text-red-400">{error}</p>
            </motion.div>
          )}
        </AnimatePresence>

        <button
          onClick={handleAnalyse}
          disabled={analyseMutation.isPending || (inputMode === "file" ? !file : !textContent.trim())}
          className="w-full flex items-center justify-center gap-2 px-6 py-3.5 text-sm font-semibold text-[#0A0A0A] bg-[#12B5CB] rounded-xl hover:bg-[#12B5CB]/90 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {analyseMutation.isPending ? (
            <>
              <div className="w-4 h-4 border-2 border-[#0A0A0A]/30 border-t-[#0A0A0A] rounded-full animate-spin" />
              Analysing document... This may take 15-30 seconds
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" /> Analyse Document
            </>
          )}
        </button>
      </div>

      {/* Sidebar */}
      <div className="space-y-4">
        {/* What we analyse */}
        <div className="glass-card rounded-2xl p-5">
          <h3 className="text-sm font-semibold text-[#E8E8E8] mb-3" style={{ fontFamily: "var(--font-heading)" }}>
            What We Analyse
          </h3>
          <div className="space-y-3">
            {[
              { icon: Target, label: "Automation opportunities", desc: "Processes that AI can streamline" },
              { icon: BarChart3, label: "Data maturity", desc: "Quality of your data practices" },
              { icon: Clock, label: "Time savings", desc: "Hours your team could save weekly" },
              { icon: BookOpen, label: "Training needs", desc: "Personalised workshop recommendations" },
            ].map((item) => (
              <div key={item.label} className="flex items-start gap-3">
                <div className="w-7 h-7 rounded-lg bg-[#12B5CB]/10 flex items-center justify-center shrink-0">
                  <item.icon className="w-3.5 h-3.5 text-[#12B5CB]" />
                </div>
                <div>
                  <p className="text-xs font-medium text-[#E8E8E8]">{item.label}</p>
                  <p className="text-[10px] text-[#666666]">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Other tools */}
        <div className="glass-card rounded-2xl p-5">
          <h3 className="text-sm font-semibold text-[#E8E8E8] mb-3" style={{ fontFamily: "var(--font-heading)" }}>
            Try Our Other Tools
          </h3>
          <div className="space-y-2">
            <Link href="/playground">
              <div className="flex items-center gap-3 p-3 rounded-xl hover:bg-[#12B5CB]/5 border border-transparent hover:border-[#12B5CB]/20 transition-all group cursor-pointer">
                <Code className="w-4 h-4 text-[#12B5CB]" />
                <div>
                  <p className="text-xs font-medium text-[#E8E8E8] group-hover:text-[#12B5CB] transition-colors">Prompt Playground</p>
                  <p className="text-[10px] text-[#666666]">Free — no sign-up</p>
                </div>
              </div>
            </Link>
            <Link href="/voice-consultant">
              <div className="flex items-center gap-3 p-3 rounded-xl hover:bg-[#12B5CB]/5 border border-transparent hover:border-[#12B5CB]/20 transition-all group cursor-pointer">
                <MessageCircle className="w-4 h-4 text-[#12B5CB]" />
                <div>
                  <p className="text-xs font-medium text-[#E8E8E8] group-hover:text-[#12B5CB] transition-colors">AI Consultant</p>
                  <p className="text-[10px] text-[#666666]">Chat with our AI advisor</p>
                </div>
              </div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function DocumentAnalyser() {
  return (
    <>
      {/* Hero */}
      <section className="relative pt-32 pb-8 overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-[#FA903E]/6 rounded-full blur-[120px] pointer-events-none" />
        <div className="container relative">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center max-w-3xl mx-auto"
          >
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-[#FA903E]/20 bg-[#FA903E]/5 mb-4">
              <FileText className="w-3.5 h-3.5 text-[#FA903E]" />
              <span className="text-xs font-medium text-[#FA903E] tracking-wide" style={{ fontFamily: "var(--font-mono)" }}>
                AI-POWERED ANALYSIS
              </span>
            </div>
            <h1
              className="text-3xl md:text-4xl lg:text-5xl font-bold text-[#E8E8E8] mb-4 leading-tight"
              style={{ fontFamily: "var(--font-heading)" }}
            >
              AI Business{" "}
              <span className="text-[#FA903E]">Document Analyser</span>
            </h1>
            <p className="text-base md:text-lg text-white/60 leading-relaxed max-w-2xl mx-auto">
              Upload any business document and get an instant AI analysis identifying automation opportunities,
              time savings, and personalised workshop recommendations.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Main content */}
      <section className="pb-20">
        <div className="container">
          <LeadGate
            toolName="Document Analyser"
            toolDescription="Enter your details to unlock the AI Document Analyser. Get a comprehensive analysis of your business documents with actionable AI recommendations."
            icon={<FileText className="w-7 h-7 text-[#FA903E]" />}
          >
            <AnalyserContent />
          </LeadGate>
        </div>
      </section>
    </>
  );
}
