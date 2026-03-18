import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Send, Cpu, Terminal, Shield, Zap, Info } from "lucide-react";

interface Message {
    id: number;
    role: "bot" | "user";
    text: string;
}

const INITIAL_STATUS = [
    "Synchronizing with Melbourne data nodes...",
    "Analyzing SME business patterns...",
    "Calibrating vendor-neutral training modules...",
    "Optimizing for 100% human-AI synergy...",
];

export default function AIOssistant() {
    const [open, setOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([
        { id: 0, role: "bot", text: "Systems online. I am your strategic AI assistant. How can I help you transform your team today?" }
    ]);
    const [input, setInput] = useState("");
    const [isTyping, setIsTyping] = useState(false);
    const [statusIdx, setStatusIdx] = useState(0);
    const [isScanning, setIsScanning] = useState(false);

    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const interval = setInterval(() => {
            setStatusIdx((prev) => (prev + 1) % INITIAL_STATUS.length);
        }, 4000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, isTyping]);

    const handleSend = (text: string) => {
        if (!text.trim()) return;
        setMessages(prev => [...prev, { id: Date.now(), role: "user", text }]);
        setInput("");
        setIsTyping(true);
        setIsScanning(true);

        // Simulated AI Processing
        setTimeout(() => {
            setIsScanning(false);
            setIsTyping(false);
            setMessages(prev => [...prev, {
                id: Date.now() + 1,
                role: "bot",
                text: "Analyzing your request... Our Melbourne-based workshops provide hands-on training tailored for SMEs. Would you like to view our current $workshops schedule?"
            }]);
        }, 2000);
    };

    return (
        <>
            <AnimatePresence>
                {!open && (
                    <motion.button
                        initial={{ opacity: 0, scale: 0.5, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.5, y: 20 }}
                        onClick={() => setOpen(true)}
                        className="fixed bottom-8 right-8 z-[100] group"
                    >
                        <div className="relative">
                            <div className="absolute inset-0 bg-[#12B5CB] blur-xl opacity-20 group-hover:opacity-40 transition-opacity" />
                            <div className="relative w-16 h-16 rounded-2xl bg-black border border-white/10 flex items-center justify-center overflow-hidden">
                                <div className="absolute inset-0 bg-gradient-to-br from-[#12B5CB]/10 to-transparent" />
                                <Cpu className="w-8 h-8 text-[#12B5CB] animate-pulse" />
                                {/* Active Scanning Line */}
                                <motion.div
                                    animate={{ y: [-64, 64] }}
                                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                                    className="absolute left-0 right-0 h-[1px] bg-[#12B5CB]/50 z-10"
                                />
                            </div>
                        </div>
                    </motion.button>
                )}
            </AnimatePresence>

            <AnimatePresence>
                {open && (
                    <motion.div
                        initial={{ opacity: 0, x: 100, scale: 0.9 }}
                        animate={{ opacity: 1, x: 0, scale: 1 }}
                        exit={{ opacity: 0, x: 100, scale: 0.9 }}
                        className="fixed bottom-8 right-8 z-[101] w-[420px] max-w-[calc(100vw-4rem)] h-[600px] max-h-[calc(100vh-8rem)] rounded-3xl overflow-hidden glass-card border border-white/10 flex flex-col shadow-2xl"
                    >
                        {/* AI Assistant Header */}
                        <div className="p-6 bg-black/40 border-b border-white/5 backdrop-blur-3xl relative overflow-hidden">
                            <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-[#12B5CB]/50 to-transparent" />

                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 rounded-xl bg-black border border-[#12B5CB]/20 flex items-center justify-center relative">
                                        <Cpu className="w-6 h-6 text-[#12B5CB]" />
                                        <div className="absolute -top-1 -right-1 w-3 h-3 bg-[#12B5CB] rounded-full border-2 border-black animate-pulse" />
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-bold text-white leading-none mb-1.5">OmniSystem 01</h3>
                                        <div className="flex items-center gap-2">
                                            <div className="w-1.5 h-1.5 rounded-full bg-[#12B5CB] animate-pulse" />
                                            <AnimatePresence mode="wait">
                                                <motion.span
                                                    key={statusIdx}
                                                    initial={{ opacity: 0, y: 5 }}
                                                    animate={{ opacity: 1, y: 0 }}
                                                    exit={{ opacity: 0, y: -5 }}
                                                    className="text-[10px] font-bold uppercase tracking-widest text-white/40"
                                                >
                                                    {INITIAL_STATUS[statusIdx]}
                                                </motion.span>
                                            </AnimatePresence>
                                        </div>
                                    </div>
                                </div>
                                <button
                                    onClick={() => setOpen(false)}
                                    className="p-2 hover:bg-white/5 rounded-lg transition-colors"
                                >
                                    <X className="w-5 h-5 text-white/40 hover:text-white" />
                                </button>
                            </div>
                        </div>

                        {/* Scanning Overlay (Active) */}
                        <AnimatePresence>
                            {isScanning && (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    exit={{ opacity: 0 }}
                                    className="absolute inset-0 pointer-events-none z-20 overflow-hidden"
                                >
                                    <motion.div
                                        animate={{ y: [-10, 600] }}
                                        transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                                        className="w-full h-[100px] bg-gradient-to-b from-transparent via-[#12B5CB]/10 to-transparent border-t border-[#12B5CB]/30"
                                    />
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {/* Log / Messages Area */}
                        <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-6 relative">
                            {messages.map((m) => (
                                <div key={m.id} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                                    <div className={`max-w-[85%] group ${m.role === "user" ? "text-right" : ""}`}>
                                        {m.role === "bot" && (
                                            <div className="flex items-center gap-2 mb-2">
                                                <Terminal className="w-3 h-3 text-[#12B5CB]" />
                                                <span className="text-[10px] font-bold text-[#12B5CB] uppercase tracking-tighter">System Output</span>
                                            </div>
                                        )}
                                        <div className={`px-5 py-3.5 rounded-2xl text-sm leading-relaxed ${m.role === "user"
                                                ? "bg-[#12B5CB] text-[#050505] font-bold rounded-tr-none"
                                                : "bg-white/5 border border-white/5 text-white/80 rounded-tl-none backdrop-blur-md"
                                            }`}>
                                            {m.text}
                                        </div>
                                    </div>
                                </div>
                            ))}

                            {isTyping && (
                                <div className="flex justify-start">
                                    <div className="bg-white/5 border border-white/5 rounded-2xl rounded-tl-none px-5 py-4 backdrop-blur-md">
                                        <div className="flex gap-1.5">
                                            {[0, 1, 2].map((i) => (
                                                <motion.div
                                                    key={i}
                                                    animate={{ scale: [1, 1.5, 1], opacity: [0.3, 1, 0.3] }}
                                                    transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
                                                    className="w-1.5 h-1.5 rounded-full bg-[#12B5CB]"
                                                />
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Diagnostic Footer */}
                        <div className="p-6 bg-black/60 border-t border-white/5 relative">
                            <div className="flex items-center gap-4 mb-4">
                                <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-[#12B5CB]/10 border border-[#12B5CB]/20">
                                    <Shield className="w-3 h-3 text-[#12B5CB]" />
                                    <span className="text-[9px] font-bold text-[#12B5CB] uppercase tracking-tighter">Secure Link</span>
                                </div>
                                <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-[#FA903E]/10 border border-[#FA903E]/20">
                                    <Zap className="w-3 h-3 text-[#FA903E]" />
                                    <span className="text-[9px] font-bold text-[#FA903E] uppercase tracking-tighter">Low Latency</span>
                                </div>
                            </div>

                            <form
                                onSubmit={(e) => { e.preventDefault(); handleSend(input); }}
                                className="relative"
                            >
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    placeholder="Transmit query..."
                                    className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-4 text-sm text-white focus:outline-none focus:border-[#12B5CB] focus:bg-white/[0.08] transition-all pr-14"
                                />
                                <button
                                    disabled={!input.trim() || isTyping}
                                    className="absolute right-2 top-2 w-10 h-10 rounded-xl bg-[#12B5CB] text-[#050505] flex items-center justify-center hover:scale-105 active:scale-95 transition-all disabled:opacity-50 disabled:grayscale"
                                >
                                    <Send className="w-5 h-5" />
                                </button>
                            </form>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}
