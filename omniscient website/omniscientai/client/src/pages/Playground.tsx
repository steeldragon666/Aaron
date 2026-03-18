import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Play,
  RotateCcw,
  Sparkles,
  ChevronDown,
  Copy,
  Check,
  Zap,
  BookOpen,
  FileText,
  Mail,
  BarChart3,
  Code,
  Briefcase,
  ArrowRight,
} from "lucide-react";
import { trpc } from "@/lib/trpc";
import { Streamdown } from "streamdown";
import { Link } from "wouter";

// ─── Prompt Templates ───
const TEMPLATE_CATEGORIES = [
  {
    name: "Business",
    icon: Briefcase,
    templates: [
      {
        title: "Meeting Summary",
        prompt: `Summarise the following meeting transcript into:
1. Key decisions made
2. Action items (with owners and deadlines)
3. Open questions requiring follow-up

Meeting transcript:
[Paste your meeting notes here]`,
      },
      {
        title: "Client Email Draft",
        prompt: `Draft a professional email to a client with the following context:
- Purpose: [e.g., project update, proposal follow-up]
- Tone: Professional but warm
- Key points to cover: [list 2-3 points]
- Call to action: [what you want them to do next]

Keep it under 200 words.`,
      },
      {
        title: "SWOT Analysis",
        prompt: `Conduct a SWOT analysis for the following business scenario:
- Company: [company name]
- Industry: [industry]
- Context: [brief description of current situation]

Format as a clear 2x2 matrix with 3-4 bullet points per quadrant. Include actionable insights for each section.`,
      },
    ],
  },
  {
    name: "Content",
    icon: FileText,
    templates: [
      {
        title: "Blog Post Outline",
        prompt: `Create a detailed blog post outline on the topic: [your topic]

Target audience: [describe your readers]
Desired length: ~1,500 words
Tone: [professional/conversational/technical]

Include:
- Compelling headline options (3 variants)
- Introduction hook
- 5-7 main sections with subheadings
- Key takeaways
- Call to action`,
      },
      {
        title: "Social Media Campaign",
        prompt: `Create a 5-post social media campaign for:
- Platform: LinkedIn
- Goal: [awareness/engagement/lead generation]
- Topic: [your topic]
- Brand voice: Professional, innovative, approachable

For each post include:
- Hook (first line)
- Body copy (under 150 words)
- Hashtags (3-5 relevant)
- Suggested image description`,
      },
    ],
  },
  {
    name: "Data & Analysis",
    icon: BarChart3,
    templates: [
      {
        title: "Data Interpretation",
        prompt: `Analyse the following data and provide insights:

[Paste your data here — CSV, table, or key metrics]

Please provide:
1. Summary of key trends
2. Notable anomalies or outliers
3. Possible explanations for the patterns observed
4. 3 actionable recommendations based on the data
5. Suggested visualisation types for presenting these findings`,
      },
      {
        title: "KPI Dashboard Brief",
        prompt: `Design a KPI dashboard for a [industry] company tracking:
- Revenue metrics
- Customer metrics
- Operational efficiency
- Team performance

For each KPI, specify:
- Metric name and formula
- Target/benchmark
- Update frequency
- Visualisation type
- Alert thresholds`,
      },
    ],
  },
  {
    name: "Technical",
    icon: Code,
    templates: [
      {
        title: "Code Review",
        prompt: `Review the following code for:
1. Bugs or logical errors
2. Performance improvements
3. Security vulnerabilities
4. Code style and readability
5. Best practice violations

Language: [language]
Context: [what the code does]

\`\`\`
[Paste your code here]
\`\`\`

Provide specific line-by-line feedback with suggested fixes.`,
      },
      {
        title: "Architecture Decision",
        prompt: `Help me make an architecture decision:

Context: [describe your system/project]
Decision needed: [what you need to choose between]
Options:
- Option A: [describe]
- Option B: [describe]

Evaluate each option against:
- Scalability
- Maintainability
- Cost
- Time to implement
- Risk

Recommend the best option with justification.`,
      },
    ],
  },
];

// ─── Prompt Score Display ───
function ScoreDisplay({ scores, overall, suggestions }: {
  scores: Record<string, number>;
  overall: number;
  suggestions: string[];
}) {
  const getColor = (score: number) => {
    if (score >= 8) return "#12B5CB";
    if (score >= 6) return "#FA903E";
    return "#ef4444";
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card rounded-2xl p-6 space-y-4"
    >
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-[#E8E8E8]" style={{ fontFamily: "var(--font-heading)" }}>
          Prompt Score
        </h3>
        <div className="flex items-center gap-2">
          <span
            className="text-2xl font-bold"
            style={{ color: getColor(overall), fontFamily: "var(--font-heading)" }}
          >
            {overall}
          </span>
          <span className="text-xs text-[#888888]">/10</span>
        </div>
      </div>

      <div className="grid grid-cols-5 gap-2">
        {Object.entries(scores).map(([key, value]) => (
          <div key={key} className="text-center">
            <div className="relative w-full h-1.5 bg-[#1A1A1A] rounded-full overflow-hidden mb-1">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${(value as number) * 10}%` }}
                transition={{ duration: 0.8, delay: 0.2 }}
                className="absolute left-0 top-0 h-full rounded-full"
                style={{ backgroundColor: getColor(value as number) }}
              />
            </div>
            <span className="text-[10px] text-[#888888] capitalize">{key}</span>
          </div>
        ))}
      </div>

      {suggestions.length > 0 && (
        <div className="space-y-1.5">
          <p className="text-xs font-medium text-[#FA903E]">Suggestions:</p>
          {suggestions.map((s, i) => (
            <p key={i} className="text-xs text-[#888888] leading-relaxed pl-3 border-l border-[#333333]">
              {s}
            </p>
          ))}
        </div>
      )}
    </motion.div>
  );
}

export default function Playground() {
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");
  const [activeCategory, setActiveCategory] = useState(0);
  const [copied, setCopied] = useState(false);
  const [showTemplates, setShowTemplates] = useState(true);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const chatMutation = trpc.playground.chat.useMutation({
    onSuccess: (data) => {
      setResponse(data.content);
    },
  });

  const scoreMutation = trpc.playground.scorePrompt.useMutation();

  const handleRun = () => {
    if (!prompt.trim()) return;
    setResponse("");
    chatMutation.mutate({
      messages: [
        { role: "system", content: "You are a helpful, knowledgeable AI assistant. Provide clear, well-structured responses." },
        { role: "user", content: prompt },
      ],
    });
  };

  const handleScore = () => {
    if (!prompt.trim()) return;
    scoreMutation.mutate({ prompt });
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(response);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleReset = () => {
    setPrompt("");
    setResponse("");
    scoreMutation.reset();
  };

  const handleTemplateClick = (templatePrompt: string) => {
    setPrompt(templatePrompt);
    setShowTemplates(false);
    textareaRef.current?.focus();
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 400) + "px";
    }
  }, [prompt]);

  return (
    <>
      {/* Hero */}
      <section className="relative pt-32 pb-12 overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-[#12B5CB]/6 rounded-full blur-[120px] pointer-events-none" />
        <div className="container relative">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center max-w-3xl mx-auto"
          >
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-[#12B5CB]/20 bg-[#12B5CB]/5 mb-4">
              <Zap className="w-3.5 h-3.5 text-[#12B5CB]" />
              <span className="text-xs font-medium text-[#12B5CB] tracking-wide" style={{ fontFamily: "var(--font-mono)" }}>
                FREE TOOL — NO SIGN-UP REQUIRED
              </span>
            </div>
            <h1
              className="text-3xl md:text-4xl lg:text-5xl font-bold text-[#E8E8E8] mb-4 leading-tight"
              style={{ fontFamily: "var(--font-heading)" }}
            >
              Prompt Engineering{" "}
              <span className="text-[#12B5CB]">Playground</span>
            </h1>
            <p className="text-base md:text-lg text-[#888888] leading-relaxed max-w-2xl mx-auto">
              Experiment with AI prompts, learn best practices, and score your prompt quality.
              This is exactly what you'll master in our{" "}
              <Link href="/workshops/hands-on-prompt-engineering" className="text-[#12B5CB] hover:underline">
                Hands-On Prompt Engineering
              </Link>{" "}
              workshop.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Main Playground */}
      <section className="pb-20">
        <div className="container">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* LEFT: Prompt Editor */}
            <div className="space-y-4">
              {/* Template selector */}
              <div className="glass-card rounded-2xl overflow-hidden">
                <button
                  onClick={() => setShowTemplates(!showTemplates)}
                  className="w-full flex items-center justify-between px-5 py-3 text-sm font-medium text-[#E8E8E8] hover:bg-[#1A1A1A]/50 transition-colors"
                >
                  <span className="flex items-center gap-2">
                    <BookOpen className="w-4 h-4 text-[#12B5CB]" />
                    Prompt Templates
                  </span>
                  <ChevronDown className={`w-4 h-4 text-[#888888] transition-transform ${showTemplates ? "rotate-180" : ""}`} />
                </button>

                <AnimatePresence>
                  {showTemplates && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3 }}
                      className="overflow-hidden"
                    >
                      <div className="px-5 pb-4 border-t border-[#333333]/30">
                        {/* Category tabs */}
                        <div className="flex gap-1 mt-3 mb-3 overflow-x-auto">
                          {TEMPLATE_CATEGORIES.map((cat, i) => (
                            <button
                              key={cat.name}
                              onClick={() => setActiveCategory(i)}
                              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all ${
                                activeCategory === i
                                  ? "bg-[#12B5CB]/10 text-[#12B5CB] border border-[#12B5CB]/20"
                                  : "text-[#888888] hover:text-[#E8E8E8] border border-transparent"
                              }`}
                            >
                              <cat.icon className="w-3 h-3" />
                              {cat.name}
                            </button>
                          ))}
                        </div>

                        {/* Templates */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          {TEMPLATE_CATEGORIES[activeCategory].templates.map((t) => (
                            <button
                              key={t.title}
                              onClick={() => handleTemplateClick(t.prompt)}
                              className="text-left p-3 rounded-xl bg-[#1A1A1A]/50 border border-[#333333]/30 hover:border-[#12B5CB]/30 hover:bg-[#12B5CB]/5 transition-all group"
                            >
                              <span className="text-xs font-medium text-[#E8E8E8] group-hover:text-[#12B5CB] transition-colors">
                                {t.title}
                              </span>
                              <p className="text-[10px] text-[#666666] mt-0.5 line-clamp-2">
                                {t.prompt.slice(0, 80)}...
                              </p>
                            </button>
                          ))}
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* Prompt input */}
              <div className="glass-card rounded-2xl p-5">
                <div className="flex items-center justify-between mb-3">
                  <label className="text-xs font-semibold text-[#888888] uppercase tracking-wider" style={{ fontFamily: "var(--font-mono)" }}>
                    Your Prompt
                  </label>
                  <span className="text-[10px] text-[#666666]" style={{ fontFamily: "var(--font-mono)" }}>
                    {prompt.length} chars
                  </span>
                </div>
                <textarea
                  ref={textareaRef}
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                      handleRun();
                    }
                  }}
                  placeholder="Type your prompt here, or select a template above..."
                  className="w-full min-h-[200px] bg-transparent text-sm text-[#E8E8E8] placeholder-[#555555] resize-none focus:outline-none leading-relaxed"
                  style={{ fontFamily: "var(--font-mono)" }}
                />

                {/* Actions */}
                <div className="flex items-center gap-2 mt-4 pt-4 border-t border-[#333333]/30">
                  <button
                    onClick={handleRun}
                    disabled={!prompt.trim() || chatMutation.isPending}
                    className="flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-[#0A0A0A] bg-[#12B5CB] rounded-xl hover:bg-[#12B5CB]/90 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    {chatMutation.isPending ? (
                      <>
                        <div className="w-3.5 h-3.5 border-2 border-[#0A0A0A]/30 border-t-[#0A0A0A] rounded-full animate-spin" />
                        Running...
                      </>
                    ) : (
                      <>
                        <Play className="w-3.5 h-3.5" /> Run Prompt
                      </>
                    )}
                  </button>

                  <button
                    onClick={handleScore}
                    disabled={!prompt.trim() || scoreMutation.isPending}
                    className="flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-[#FA903E] border border-[#FA903E]/30 rounded-xl hover:bg-[#FA903E]/5 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    {scoreMutation.isPending ? (
                      <>
                        <div className="w-3.5 h-3.5 border-2 border-[#FA903E]/30 border-t-[#FA903E] rounded-full animate-spin" />
                        Scoring...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-3.5 h-3.5" /> Score Prompt
                      </>
                    )}
                  </button>

                  <button
                    onClick={handleReset}
                    className="ml-auto p-2.5 text-[#888888] hover:text-[#E8E8E8] transition-colors rounded-xl hover:bg-[#1A1A1A]/50"
                    title="Reset"
                  >
                    <RotateCcw className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Prompt Score */}
              <AnimatePresence>
                {scoreMutation.data && (
                  <ScoreDisplay
                    scores={scoreMutation.data.scores}
                    overall={scoreMutation.data.overall}
                    suggestions={scoreMutation.data.suggestions}
                  />
                )}
              </AnimatePresence>
            </div>

            {/* RIGHT: Response */}
            <div className="space-y-4">
              <div className="glass-card rounded-2xl p-5 min-h-[500px] flex flex-col">
                <div className="flex items-center justify-between mb-3">
                  <label className="text-xs font-semibold text-[#888888] uppercase tracking-wider" style={{ fontFamily: "var(--font-mono)" }}>
                    AI Response
                  </label>
                  {response && (
                    <button
                      onClick={handleCopy}
                      className="flex items-center gap-1 text-xs text-[#888888] hover:text-[#12B5CB] transition-colors"
                    >
                      {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                      {copied ? "Copied" : "Copy"}
                    </button>
                  )}
                </div>

                <div className="flex-1">
                  {chatMutation.isPending ? (
                    <div className="flex items-center gap-3 text-sm text-[#888888]">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 rounded-full bg-[#12B5CB] animate-bounce" style={{ animationDelay: "0ms" }} />
                        <div className="w-2 h-2 rounded-full bg-[#12B5CB] animate-bounce" style={{ animationDelay: "150ms" }} />
                        <div className="w-2 h-2 rounded-full bg-[#12B5CB] animate-bounce" style={{ animationDelay: "300ms" }} />
                      </div>
                      Generating response...
                    </div>
                  ) : response ? (
                    <div className="prose prose-sm prose-invert max-w-none text-[#E8E8E8]/90">
                      <Streamdown>{response}</Streamdown>
                    </div>
                  ) : chatMutation.isError ? (
                    <div className="text-sm text-red-400">
                      Error: {chatMutation.error?.message || "Failed to generate response. Please try again."}
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center h-full text-center py-16">
                      <div className="w-16 h-16 rounded-2xl bg-[#12B5CB]/5 border border-[#12B5CB]/10 flex items-center justify-center mb-4">
                        <Sparkles className="w-7 h-7 text-[#12B5CB]/30" />
                      </div>
                      <p className="text-sm text-[#888888] mb-1">AI response will appear here</p>
                      <p className="text-xs text-[#666666]">
                        Write a prompt and click <strong className="text-[#12B5CB]">Run Prompt</strong> or press{" "}
                        <kbd className="px-1.5 py-0.5 rounded bg-[#1A1A1A] border border-[#333333] text-[10px]">Cmd+Enter</kbd>
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* CTA card */}
              <div className="glass-card rounded-2xl p-5">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-xl bg-[#FA903E]/10 border border-[#FA903E]/20 flex items-center justify-center shrink-0">
                    <BookOpen className="w-5 h-5 text-[#FA903E]" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-sm font-semibold text-[#E8E8E8] mb-1" style={{ fontFamily: "var(--font-heading)" }}>
                      Want to master prompt engineering?
                    </h3>
                    <p className="text-xs text-[#888888] leading-relaxed mb-3">
                      Our full-day Hands-On Prompt Engineering workshop covers advanced techniques, chain-of-thought prompting, and multi-model strategies your team can use immediately.
                    </p>
                    <Link
                      href="/workshops/hands-on-prompt-engineering"
                      className="inline-flex items-center gap-1 text-xs font-medium text-[#FA903E] hover:text-[#FA903E]/80 transition-colors"
                    >
                      Learn more <ArrowRight className="w-3 h-3" />
                    </Link>
                  </div>
                </div>
              </div>

              {/* Cross-promote other tools */}
              <div className="grid grid-cols-2 gap-3">
                <Link href="/voice-consultant">
                  <div className="glass-card rounded-xl p-4 hover:border-[#12B5CB]/30 transition-all group cursor-pointer">
                    <Mail className="w-5 h-5 text-[#12B5CB] mb-2" />
                    <p className="text-xs font-medium text-[#E8E8E8] group-hover:text-[#12B5CB] transition-colors">AI Consultant</p>
                    <p className="text-[10px] text-[#666666] mt-0.5">Chat with our AI advisor</p>
                  </div>
                </Link>
                <Link href="/document-analyser">
                  <div className="glass-card rounded-xl p-4 hover:border-[#FA903E]/30 transition-all group cursor-pointer">
                    <FileText className="w-5 h-5 text-[#FA903E] mb-2" />
                    <p className="text-xs font-medium text-[#E8E8E8] group-hover:text-[#FA903E] transition-colors">Document Analyser</p>
                    <p className="text-[10px] text-[#666666] mt-0.5">Upload & analyse docs</p>
                  </div>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
