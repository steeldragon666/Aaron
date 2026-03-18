import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  MessageCircle,
  Send,
  Sparkles,
  User,
  ArrowRight,
  Zap,
  FileText,
  Code,
  BookOpen,
  ExternalLink,
} from "lucide-react";
import { trpc } from "@/lib/trpc";
import { Streamdown } from "streamdown";
import { Link } from "wouter";
import LeadGate from "@/components/LeadGate";

type ChatMessage = {
  role: "system" | "user" | "assistant";
  content: string;
};

const SYSTEM_PROMPT = `You are the OmniscientAI Virtual Consultant — a knowledgeable, friendly AI assistant for OmniscientAI, Melbourne's leading vendor-neutral AI training and consulting company.

YOUR KNOWLEDGE:
- OmniscientAI offers three core workshops:
  1. "AI for Business Leaders" (half-day, $2,500-4,500) — strategic AI literacy for executives and decision-makers
  2. "Hands-On Prompt Engineering" (full-day, $3,000-5,500) — practical prompt crafting across ChatGPT, Claude, Gemini, Copilot
  3. "AI-Powered Workflows" (full-day, $3,500-6,000) — building automated workflows with AI tools
- Custom workshops available, tailored to any industry
- Services: AI Strategy Consulting, AI Implementation Support
- Industries served: Legal, Healthcare, Manufacturing, Professional Services, Retail, Construction
- Based in Melbourne, Australia. Serves SMEs (5-200 employees)
- Vendor-neutral approach — we teach ALL major AI platforms, not just one
- Founded by an experienced AI practitioner with deep technical and business expertise

YOUR BEHAVIOUR:
- Be warm, professional, and concise
- Ask qualifying questions: team size, industry, current AI usage, goals
- Recommend specific workshops based on their needs
- Mention the AI Readiness Quiz at /ai-readiness-quiz for self-assessment
- IMPORTANT: Actively cross-promote the other tools on the website:
  * "Have you tried our Prompt Engineering Playground? It's a free tool at /playground where you can experiment with different AI models."
  * "Our Document Analyser at /document-analyser can scan your business documents and identify AI automation opportunities."
  * "Take our AI Readiness Quiz at /ai-readiness-quiz to get a personalised score."
- Always offer to help them book a free strategy session at /book
- Keep responses under 150 words for conversational flow`;

const SUGGESTED_PROMPTS = [
  "What workshops do you offer?",
  "How can AI help my small business?",
  "I want to train my team on prompt engineering",
  "What industries do you work with?",
];

function ConsultantChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: "system", content: SYSTEM_PROMPT },
    {
      role: "assistant",
      content:
        "G'day! 👋 I'm the OmniscientAI Virtual Consultant. I can help you find the right AI training and consulting solutions for your business.\n\nWhether you're looking to upskill your team, automate workflows, or develop an AI strategy — I'm here to help. What brings you here today?",
    },
  ]);
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  const chatMutation = trpc.voiceConsultant.chat.useMutation({
    onSuccess: (data) => {
      setMessages((prev) => [...prev, { role: "assistant", content: data.content }]);
    },
    onError: () => {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "I'm sorry, I encountered an issue. Please try again or contact us directly at hello@omniscientai.com.au" },
      ]);
    },
  });

  const handleSend = (content: string) => {
    if (!content.trim() || chatMutation.isPending) return;
    const newMessages: ChatMessage[] = [...messages, { role: "user", content }];
    setMessages(newMessages);
    setInput("");
    chatMutation.mutate({ messages: newMessages });
  };

  // Auto-scroll
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
    }
  }, [messages, chatMutation.isPending]);

  const displayMessages = messages.filter((m) => m.role !== "system");

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4">
        {displayMessages.map((msg, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            {msg.role === "assistant" && (
              <div className="w-8 h-8 rounded-full bg-[#12B5CB]/10 border border-[#12B5CB]/20 flex items-center justify-center shrink-0 mt-1">
                <Sparkles className="w-4 h-4 text-[#12B5CB]" />
              </div>
            )}
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                msg.role === "user"
                  ? "bg-[#12B5CB] text-[#0A0A0A]"
                  : "bg-[#1A1A1A] border border-[#333333]/50 text-[#E8E8E8]"
              }`}
            >
              {msg.role === "assistant" ? (
                <div className="prose prose-sm prose-invert max-w-none text-[#E8E8E8]/90 text-sm leading-relaxed">
                  <Streamdown>{msg.content}</Streamdown>
                </div>
              ) : (
                <p className="text-sm">{msg.content}</p>
              )}
            </div>
            {msg.role === "user" && (
              <div className="w-8 h-8 rounded-full bg-[#FA903E]/10 border border-[#FA903E]/20 flex items-center justify-center shrink-0 mt-1">
                <User className="w-4 h-4 text-[#FA903E]" />
              </div>
            )}
          </motion.div>
        ))}

        {chatMutation.isPending && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex gap-3"
          >
            <div className="w-8 h-8 rounded-full bg-[#12B5CB]/10 border border-[#12B5CB]/20 flex items-center justify-center shrink-0">
              <Sparkles className="w-4 h-4 text-[#12B5CB]" />
            </div>
            <div className="bg-[#1A1A1A] border border-[#333333]/50 rounded-2xl px-4 py-3">
              <div className="flex gap-1.5">
                <div className="w-2 h-2 rounded-full bg-[#12B5CB] animate-bounce" style={{ animationDelay: "0ms" }} />
                <div className="w-2 h-2 rounded-full bg-[#12B5CB] animate-bounce" style={{ animationDelay: "150ms" }} />
                <div className="w-2 h-2 rounded-full bg-[#12B5CB] animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </motion.div>
        )}

        {/* Suggested prompts (only show if just the welcome message) */}
        {displayMessages.length === 1 && (
          <div className="flex flex-wrap gap-2 pt-2">
            {SUGGESTED_PROMPTS.map((prompt) => (
              <button
                key={prompt}
                onClick={() => handleSend(prompt)}
                className="px-3 py-1.5 text-xs font-medium text-[#12B5CB] border border-[#12B5CB]/20 rounded-full bg-[#12B5CB]/5 hover:bg-[#12B5CB]/10 transition-all"
              >
                {prompt}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-[#333333]/30 p-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend(input);
          }}
          className="flex gap-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about workshops, AI strategy, or how AI can help your business..."
            className="flex-1 px-4 py-3 bg-[#1A1A1A] border border-[#333333] rounded-xl text-sm text-[#E8E8E8] placeholder-[#666666] focus:outline-none focus:border-[#12B5CB]/50 transition-all"
          />
          <button
            type="submit"
            disabled={!input.trim() || chatMutation.isPending}
            className="px-4 py-3 bg-[#12B5CB] text-[#0A0A0A] rounded-xl hover:bg-[#12B5CB]/90 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}

export default function VoiceConsultant() {
  return (
    <>
      {/* Hero */}
      <section className="relative pt-32 pb-8 overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-[#12B5CB]/6 rounded-full blur-[120px] pointer-events-none" />
        <div className="container relative">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center max-w-3xl mx-auto"
          >
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-[#12B5CB]/20 bg-[#12B5CB]/5 mb-4">
              <MessageCircle className="w-3.5 h-3.5 text-[#12B5CB]" />
              <span className="text-xs font-medium text-[#12B5CB] tracking-wide" style={{ fontFamily: "var(--font-mono)" }}>
                AI-POWERED CONSULTANT
              </span>
            </div>
            <h1
              className="text-3xl md:text-4xl lg:text-5xl font-bold text-[#E8E8E8] mb-4 leading-tight"
              style={{ fontFamily: "var(--font-heading)" }}
            >
              Chat with Our{" "}
              <span className="text-[#12B5CB]">AI Consultant</span>
            </h1>
            <p className="text-base md:text-lg text-[#888888] leading-relaxed max-w-2xl mx-auto">
              Get instant, personalised advice on AI training and strategy for your business.
              Our AI consultant knows everything about our workshops, services, and how AI can transform your operations.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Main content */}
      <section className="pb-20">
        <div className="container">
          <LeadGate
            toolName="AI Consultant"
            toolDescription="Enter your details to start chatting with our AI consultant. Get personalised workshop recommendations and AI strategy advice for your business."
            icon={<MessageCircle className="w-7 h-7 text-[#12B5CB]" />}
          >
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Chat area */}
              <div className="lg:col-span-3">
                <div className="glass-card rounded-2xl overflow-hidden" style={{ height: "600px" }}>
                  <ConsultantChat />
                </div>
              </div>

              {/* Sidebar */}
              <div className="space-y-4">
                {/* Quick links */}
                <div className="glass-card rounded-2xl p-5">
                  <h3 className="text-sm font-semibold text-[#E8E8E8] mb-3" style={{ fontFamily: "var(--font-heading)" }}>
                    Explore More Tools
                  </h3>
                  <div className="space-y-2">
                    <Link href="/playground">
                      <div className="flex items-center gap-3 p-3 rounded-xl hover:bg-[#12B5CB]/5 border border-transparent hover:border-[#12B5CB]/20 transition-all group cursor-pointer">
                        <div className="w-8 h-8 rounded-lg bg-[#12B5CB]/10 flex items-center justify-center shrink-0">
                          <Code className="w-4 h-4 text-[#12B5CB]" />
                        </div>
                        <div>
                          <p className="text-xs font-medium text-[#E8E8E8] group-hover:text-[#12B5CB] transition-colors">Prompt Playground</p>
                          <p className="text-[10px] text-[#666666]">Free — no sign-up</p>
                        </div>
                      </div>
                    </Link>
                    <Link href="/document-analyser">
                      <div className="flex items-center gap-3 p-3 rounded-xl hover:bg-[#FA903E]/5 border border-transparent hover:border-[#FA903E]/20 transition-all group cursor-pointer">
                        <div className="w-8 h-8 rounded-lg bg-[#FA903E]/10 flex items-center justify-center shrink-0">
                          <FileText className="w-4 h-4 text-[#FA903E]" />
                        </div>
                        <div>
                          <p className="text-xs font-medium text-[#E8E8E8] group-hover:text-[#FA903E] transition-colors">Document Analyser</p>
                          <p className="text-[10px] text-[#666666]">Upload & analyse docs</p>
                        </div>
                      </div>
                    </Link>
                    <Link href="/ai-readiness-quiz">
                      <div className="flex items-center gap-3 p-3 rounded-xl hover:bg-[#12B5CB]/5 border border-transparent hover:border-[#12B5CB]/20 transition-all group cursor-pointer">
                        <div className="w-8 h-8 rounded-lg bg-[#12B5CB]/10 flex items-center justify-center shrink-0">
                          <Zap className="w-4 h-4 text-[#12B5CB]" />
                        </div>
                        <div>
                          <p className="text-xs font-medium text-[#E8E8E8] group-hover:text-[#12B5CB] transition-colors">AI Readiness Quiz</p>
                          <p className="text-[10px] text-[#666666]">5-min assessment</p>
                        </div>
                      </div>
                    </Link>
                  </div>
                </div>

                {/* Book CTA */}
                <div className="glass-card rounded-2xl p-5 border-[#FA903E]/20">
                  <BookOpen className="w-6 h-6 text-[#FA903E] mb-3" />
                  <h3 className="text-sm font-semibold text-[#E8E8E8] mb-2" style={{ fontFamily: "var(--font-heading)" }}>
                    Ready for the real thing?
                  </h3>
                  <p className="text-xs text-[#888888] leading-relaxed mb-3">
                    Book a free 30-minute strategy session with a human consultant to discuss your AI training needs.
                  </p>
                  <Link
                    href="/book"
                    className="inline-flex items-center gap-1 text-xs font-semibold text-[#FA903E] hover:text-[#FA903E]/80 transition-colors"
                  >
                    Book a Session <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              </div>
            </div>
          </LeadGate>
        </div>
      </section>
    </>
  );
}
