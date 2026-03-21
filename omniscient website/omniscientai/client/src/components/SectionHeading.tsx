// SectionHeading — reusable section title block
import { motion } from "framer-motion";

interface Props {
  label?: string;
  title: string;
  description?: string;
  align?: "left" | "center";
}

export default function SectionHeading({ label, title, description, align = "center" }: Props) {
  const alignClass = align === "center" ? "text-center mx-auto" : "text-left";
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-100px" }}
      transition={{ duration: 0.8, ease: [0.21, 0.47, 0.32, 0.98] }}
      className={`max-w-3xl mb-16 md:mb-24 ${alignClass}`}
    >
      {label && (
        <motion.span
          initial={{ opacity: 0, x: -10 }}
          whileInView={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="inline-block px-3 py-1 rounded-full border border-[#12B5CB]/20 bg-[#12B5CB]/5 text-[10px] font-bold uppercase tracking-[0.3em] text-[#12B5CB] mb-5"
          style={{ fontFamily: "var(--font-mono)" }}
        >
          {label}
        </motion.span>
      )}
      <h2 className="text-balance leading-[1.1] tracking-tight mb-6 transition-colors">
        {title}
      </h2>
      {description && (
        <p className="text-lg md:text-xl text-white/70 leading-relaxed font-medium">
          {description}
        </p>
      )}
    </motion.div>
  );
}
