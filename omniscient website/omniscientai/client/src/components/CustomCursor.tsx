import { useEffect, useState } from "react";
import { motion, useSpring, useMotionValue, useReducedMotion } from "framer-motion";

export default function CustomCursor() {
    const [isVisible, setIsVisible] = useState(false);
    const [isHovering, setIsHovering] = useState(false);
    const prefersReducedMotion = useReducedMotion();

    const mouseX = useMotionValue(0);
    const mouseY = useMotionValue(0);

    const springConfig = { damping: 25, stiffness: 250 };
    const cursorX = useSpring(mouseX, springConfig);
    const cursorY = useSpring(mouseY, springConfig);

    useEffect(() => {
        if (prefersReducedMotion) return;

        const handleMouseMove = (e: MouseEvent) => {
            mouseX.set(e.clientX);
            mouseY.set(e.clientY);
            if (!isVisible) setIsVisible(true);
        };

        const handleMouseOver = (e: MouseEvent) => {
            const target = e.target as HTMLElement;
            const isClickable =
                target.closest("button") ||
                target.closest("a") ||
                target.getAttribute("role") === "button" ||
                window.getComputedStyle(target).cursor === "pointer";

            setIsHovering(!!isClickable);
        };

        window.addEventListener("mousemove", handleMouseMove);
        window.addEventListener("mouseover", handleMouseOver);

        return () => {
            window.removeEventListener("mousemove", handleMouseMove);
            window.removeEventListener("mouseover", handleMouseOver);
        };
    }, [isVisible, mouseX, mouseY, prefersReducedMotion]);

    if (prefersReducedMotion || !isVisible) return null;

    return (
        <div className="fixed inset-0 pointer-events-none z-50 hidden md:block">
            {/* Outer Ring */}
            <motion.div
                className="absolute w-8 h-8 border border-[#12B5CB]/40 rounded-full -translate-x-1/2 -translate-y-1/2"
                style={{
                    x: cursorX,
                    y: cursorY,
                    scale: isHovering ? 2.5 : 1,
                    opacity: isHovering ? 0.3 : 0.6,
                }}
                transition={{ type: "spring", damping: 30, stiffness: 200 }}
            />

            {/* Inner Dot */}
            <motion.div
                className="absolute w-1.5 h-1.5 bg-[#12B5CB] rounded-full -translate-x-1/2 -translate-y-1/2"
                style={{
                    x: cursorX,
                    y: cursorY,
                    scale: isHovering ? 0 : 1,
                }}
            />

            {/* Glow Effect */}
            <motion.div
                className="absolute w-24 h-24 bg-[#12B5CB]/5 rounded-full blur-2xl -translate-x-1/2 -translate-y-1/2"
                style={{
                    x: cursorX,
                    y: cursorY,
                }}
            />
        </div>
    );
}
