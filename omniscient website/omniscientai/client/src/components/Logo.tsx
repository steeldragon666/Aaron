import { motion } from "framer-motion";

interface LogoProps {
    className?: string;
    iconOnly?: boolean;
    variant?: "default" | "minimal";
}

export default function Logo({ className = "", iconOnly = false, variant = "default" }: LogoProps) {
    return (
        <div className={`flex items-center gap-3 select-none ${className}`}>
            {/* Dynamic Logo Mark */}
            <motion.div
                className="relative w-10 h-10 flex items-center justify-center"
                initial={false}
                whileHover="hover"
            >
                {/* Animated Background Glow */}
                <motion.div
                    className="absolute inset-0 bg-[#12B5CB] rounded-xl blur-lg opacity-20"
                    animate={{
                        scale: [1, 1.2, 1],
                        opacity: [0.2, 0.4, 0.2]
                    }}
                    transition={{
                        duration: 4,
                        repeat: Infinity,
                        ease: "easeInOut"
                    }}
                />

                {/* Main Logo Container */}
                <motion.div
                    className="relative w-full h-full rounded-xl bg-gradient-to-br from-[#12B5CB] to-[#0A8DA0] shadow-lg flex items-center justify-center overflow-hidden border border-white/10"
                    variants={{
                        hover: { scale: 1.05, rotate: -2 }
                    }}
                >
                    {/* Animated Mesh/Pulse inside logo */}
                    <motion.div
                        className="absolute inset-x-0 bottom-0 h-1/2 bg-white/10 blur-md"
                        animate={{
                            y: [-20, 20, -20],
                            opacity: [0.2, 0.5, 0.2]
                        }}
                        transition={{
                            duration: 3,
                            repeat: Infinity,
                            ease: "linear"
                        }}
                    />

                    <span className="text-[#052A30] font-black text-xl tracking-tighter" style={{ fontFamily: "var(--font-heading)" }}>
                        O
                    </span>
                </motion.div>

                {/* Active AI Indicator Dot */}
                <motion.div
                    className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-[#FA903E] rounded-full border-2 border-[#0A0A0A] shadow-sm"
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                />
            </motion.div>

            {/* Logo Text */}
            {!iconOnly && (
                <span
                    className={`text-xl font-bold tracking-tight ${variant === "minimal" ? "hidden md:block" : ""}`}
                    style={{ fontFamily: "var(--font-heading)" }}
                >
                    Omniscient<span className="text-[#12B5CB]">AI</span>
                </span>
            )}
        </div>
    );
}
