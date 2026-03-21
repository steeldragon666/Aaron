// Demo AI Chatbot Widget — OmniscientAI
// Floating chat bubble with pre-scripted responses to demonstrate AI capability
import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageCircle, X, Send, Bot, User } from "lucide-react";

interface Message {
  id: number;
  role: "bot" | "user";
  text: string;
}

const INITIAL_MESSAGE: Message = {
  id: 0,
  role: "bot",
  text: "Hi! I'm OmniscientAI's demo assistant. I can answer questions about our workshops, services, and AI readiness. What would you like to know?",
};

const QUICK_REPLIES = [
  "What workshops do you offer?",
  "How much do workshops cost?",
  "What is the AI Readiness Quiz?",
  "Do you offer custom training?",
];

const RESPONSES: Record<string, string> = {
  "workshop": "We offer three core workshops:\n\n1. **AI Foundations for Business** (Half-day, $2,000–$3,500) — Perfect for teams new to AI\n2. **Copilot Mastery** (Full-day, $3,000–$5,000) — Hands-on Microsoft 365 Copilot training\n3. **AI Strategy & Governance** (2-day, $5,000–$8,000) — For leadership teams building AI roadmaps\n\nAll workshops are vendor-neutral and customised to your industry. Would you like to know more about any of these?",
  "cost": "Our workshop pricing is based on team size and customisation level:\n\n• AI Foundations: $2,000–$3,500\n• Copilot Mastery: $3,000–$5,000\n• AI Strategy & Governance: $5,000–$8,000\n\nAll prices are ex-GST. We also offer custom workshops — pricing depends on scope. Book a free strategy session to get a tailored quote.",
  "quiz": "Our AI Readiness Quiz is a free 5-minute assessment that scores your business across five dimensions: Data Maturity, Team Skills, Process Automation, Strategic Alignment, and Governance. You'll get a personalised score, tier rating, and tailored workshop recommendations. You can take it right now at /ai-readiness-quiz!",
  "custom": "Absolutely! We design custom workshops tailored to your specific industry, team size, and learning objectives. Common customisations include industry-specific case studies, tool-specific deep dives, and multi-session programs. Visit /workshops/custom to submit an enquiry, or book a free strategy session to discuss your needs.",
  "default": "Great question! For detailed information, I'd recommend booking a free 30-minute strategy session where we can discuss your specific needs. You can also explore our workshops at /workshops or take our AI Readiness Quiz at /ai-readiness-quiz. Is there anything else I can help with?",
};

function getResponse(input: string): string {
  const lower = input.toLowerCase();
  if (lower.includes("workshop") || lower.includes("training") || lower.includes("offer")) return RESPONSES["workshop"];
  if (lower.includes("cost") || lower.includes("price") || lower.includes("much")) return RESPONSES["cost"];
  if (lower.includes("quiz") || lower.includes("readiness") || lower.includes("assessment")) return RESPONSES["quiz"];
  if (lower.includes("custom") || lower.includes("bespoke") || lower.includes("tailored")) return RESPONSES["custom"];
  return RESPONSES["default"];
}

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([INITIAL_MESSAGE]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  let nextId = useRef(1);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, typing]);

  const sendMessage = (text: string) => {
    if (!text.trim()) return;
    const userMsg: Message = { id: nextId.current++, role: "user", text: text.trim() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setTyping(true);

    setTimeout(() => {
      const botMsg: Message = { id: nextId.current++, role: "bot", text: getResponse(text) };
      setMessages((prev) => [...prev, botMsg]);
      setTyping(false);
    }, 800 + Math.random() * 600);
  };

  return (
    <>
      {/* Chat bubble */}
      <AnimatePresence>
        {!open && (
          <motion.button
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            onClick={() => setOpen(true)}
            className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-[#12B5CB] text-[#0A0A0A] shadow-lg shadow-[#12B5CB]/20 flex items-center justify-center hover:bg-[#12B5CB]/90 transition-colors"
          >
            <MessageCircle className="w-6 h-6" />
          </motion.button>
        )}
      </AnimatePresence>

      {/* Chat panel */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="fixed bottom-6 right-6 z-50 w-[380px] max-w-[calc(100vw-2rem)] h-[520px] max-h-[calc(100vh-6rem)] rounded-2xl overflow-hidden flex flex-col border border-[#333333] bg-[#1A1A1A] shadow-2xl"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 bg-[#0A0A0A] border-b border-[#333333]">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-[#12B5CB]/10 border border-[#12B5CB]/20 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-[#12B5CB]" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-[#E8E8E8]" style={{ fontFamily: "var(--font-heading)" }}>OmniscientAI</p>
                  <p className="text-xs text-white/60">Demo Assistant</p>
                </div>
              </div>
              <button onClick={() => setOpen(false)} className="text-white/60 hover:text-[#E8E8E8] transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Messages */}
            <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((msg) => (
                <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                    msg.role === "user"
                      ? "bg-[#12B5CB] text-[#0A0A0A] rounded-br-md"
                      : "bg-[#0A0A0A] text-[#E8E8E8] border border-[#333333] rounded-bl-md"
                  }`}>
                    <div className="whitespace-pre-line">{msg.text}</div>
                  </div>
                </div>
              ))}
              {typing && (
                <div className="flex justify-start">
                  <div className="bg-[#0A0A0A] border border-[#333333] rounded-2xl rounded-bl-md px-4 py-3">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 rounded-full bg-white/60 animate-bounce" style={{ animationDelay: "0ms" }} />
                      <div className="w-2 h-2 rounded-full bg-white/60 animate-bounce" style={{ animationDelay: "150ms" }} />
                      <div className="w-2 h-2 rounded-full bg-white/60 animate-bounce" style={{ animationDelay: "300ms" }} />
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Quick replies */}
            {messages.length <= 1 && (
              <div className="px-4 pb-2 flex flex-wrap gap-2">
                {QUICK_REPLIES.map((qr) => (
                  <button
                    key={qr}
                    onClick={() => sendMessage(qr)}
                    className="text-xs px-3 py-1.5 rounded-full border border-[#12B5CB]/30 text-[#12B5CB] hover:bg-[#12B5CB]/10 transition-colors"
                  >
                    {qr}
                  </button>
                ))}
              </div>
            )}

            {/* Input */}
            <div className="px-4 py-3 border-t border-[#333333] bg-[#0A0A0A]">
              <form
                onSubmit={(e) => { e.preventDefault(); sendMessage(input); }}
                className="flex items-center gap-2"
              >
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask about our workshops..."
                  className="flex-1 px-3 py-2 rounded-lg bg-[#1A1A1A] border border-[#333333] text-[#E8E8E8] placeholder-white/40 text-sm focus:border-[#12B5CB] focus:outline-none transition-colors"
                />
                <button
                  type="submit"
                  disabled={!input.trim()}
                  className="w-9 h-9 rounded-lg bg-[#12B5CB] text-[#0A0A0A] flex items-center justify-center hover:bg-[#12B5CB]/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send className="w-4 h-4" />
                </button>
              </form>
              <p className="text-[10px] text-white/60 mt-1.5 text-center">This is a demo chatbot with pre-scripted responses.</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
