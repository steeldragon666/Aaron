// Homepage — OmniscientAI Dramatic Visual Redesign
import { Link } from "wouter";
import { motion, useScroll, useTransform, useReducedMotion } from "framer-motion";
import { useRef } from "react";
import {
  ArrowRight,
  ChevronRight,
  Zap,
  Cpu,
  Shield,
  Globe,
  BarChart3,
  Users,
  FileCheck,
  Compass,
  BookOpen,
  Scale,
} from "lucide-react";
import { cn } from "@/lib/utils";
import TechPartners from "@/components/TechPartners";
import SEO from "@/components/SEO";

/* ─── Retro Grid Background ─── */
const RetroGrid = ({
  angle = 65,
  cellSize = 60,
  opacity = 0.3,
  lineColor = "#12B5CB",
}: {
  angle?: number;
  cellSize?: number;
  opacity?: number;
  lineColor?: string;
}) => {
  const gridStyles = {
    "--grid-angle": `${angle}deg`,
    "--cell-size": `${cellSize}px`,
    "--opacity": opacity,
    "--line-color": lineColor,
  } as React.CSSProperties;

  return (
    <div
      className="pointer-events-none absolute inset-0 overflow-hidden [perspective:200px]"
      style={{ ...gridStyles, opacity: "var(--opacity)" } as React.CSSProperties}
    >
      <div className="absolute inset-0 [transform:rotateX(var(--grid-angle))]">
        <div
          className="animate-grid [background-repeat:repeat] [height:300vh] [inset:0%_0px] [margin-left:-200%] [transform-origin:100%_0_0] [width:600vw]"
          style={{
            backgroundImage: `linear-gradient(to right, ${lineColor}22 1px, transparent 0), linear-gradient(to bottom, ${lineColor}22 1px, transparent 0)`,
            backgroundSize: `${cellSize}px ${cellSize}px`,
          }}
        />
      </div>
      <div className="absolute inset-0 bg-gradient-to-t from-black to-transparent to-90%" />
    </div>
  );
};

/* ─── Animated Dot Grid ─── */
const DotGrid = () => (
  <div
    className="absolute inset-0 pointer-events-none"
    style={{
      backgroundImage: `radial-gradient(circle, rgba(18, 181, 203, 0.15) 1px, transparent 1px)`,
      backgroundSize: "32px 32px",
      maskImage: "radial-gradient(ellipse 80% 60% at 50% 40%, black 40%, transparent 100%)",
      WebkitMaskImage: "radial-gradient(ellipse 80% 60% at 50% 40%, black 40%, transparent 100%)",
    }}
  />
);

/* ─── Radial Glow Accent ─── */
const RadialGlow = ({ className, color = "#12B5CB" }: { className?: string; color?: string }) => (
  <div
    className={cn("absolute rounded-full pointer-events-none blur-[120px]", className)}
    style={{ background: color, opacity: 0.15 }}
  />
);

const structuredData = {
  "@context": "https://schema.org",
  "@type": "ConsultingBusiness",
  name: "OmniscientAI",
  description: "Vendor-neutral AI training and consulting for Melbourne SMEs.",
  url: "https://omniscientai.io",
  address: {
    "@type": "PostalAddress",
    addressLocality: "Melbourne",
    addressRegion: "VIC",
    addressCountry: "AU",
  },
};

/* ─── Bento Item ─── */
interface BentoItemProps {
  title: string;
  value?: string;
  description: string;
  icon: React.ReactNode;
  colSpan?: number;
  rowSpan?: number;
  href?: string;
  accent?: string;
  className?: string;
}

function BentoCard({ title, value, description, icon, colSpan = 1, rowSpan = 1, href, accent = "#12B5CB", className }: BentoItemProps) {
  const content = (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
      className={cn(
        "group relative flex flex-col justify-between overflow-hidden rounded-2xl p-6 md:p-8 h-full",
        "border border-white/[0.08] bg-white/[0.02]",
        "hover:border-[#12B5CB]/30 hover:bg-white/[0.04]",
        "transition-all duration-500 ease-out",
        "hover:-translate-y-1",
        "shadow-[0_0_0_0_rgba(18,181,203,0)] hover:shadow-[0_8px_40px_-12px_rgba(18,181,203,0.15)]",
        colSpan === 2 ? "md:col-span-2" : "col-span-1",
        rowSpan === 2 ? "md:row-span-2" : "row-span-1",
        href && "cursor-pointer",
        className,
      )}
    >
      {/* Dot pattern on hover */}
      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: `radial-gradient(circle, ${accent}15 1px, transparent 1px)`,
            backgroundSize: "16px 16px",
          }}
        />
      </div>

      {/* Gradient accent line at top */}
      <div
        className="absolute top-0 left-0 right-0 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        style={{ background: `linear-gradient(90deg, transparent, ${accent}, transparent)` }}
      />

      <div className="relative z-10 flex flex-col h-full">
        <div className="flex items-center justify-between mb-4">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-300 group-hover:scale-110"
            style={{ background: `${accent}15`, border: `1px solid ${accent}20` }}
          >
            {icon}
          </div>
          {value && (
            <span
              className="text-3xl md:text-4xl font-black tracking-tight"
              style={{ color: accent }}
            >
              {value}
            </span>
          )}
        </div>
        <h3 className="text-base md:text-lg font-bold text-white mb-2 tracking-tight" style={{ fontFamily: "var(--font-heading)" }}>
          {title}
        </h3>
        <p className="text-sm text-white/50 leading-relaxed flex-1">{description}</p>
        {href && (
          <div className="flex items-center gap-1 mt-4 text-sm font-medium opacity-0 group-hover:opacity-100 transition-all duration-300" style={{ color: accent }}>
            Learn more <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
          </div>
        )}
      </div>
    </motion.div>
  );

  if (href) {
    return <Link href={href} className="cursor-pointer">{content}</Link>;
  }
  return content;
}

export default function Home() {
  const heroRef = useRef(null);
  const prefersReducedMotion = useReducedMotion();
  const { scrollYProgress } = useScroll({
    target: heroRef,
    offset: ["start start", "end start"],
  });

  const contentY = useTransform(scrollYProgress, [0, 1], [0, prefersReducedMotion ? 0 : -80]);
  const contentOpacity = useTransform(scrollYProgress, [0, 0.6], [1, prefersReducedMotion ? 1 : 0]);

  return (
    <>
      <SEO
        title="Melbourne's Vendor-Neutral AI Training for SMEs"
        description="Transform your team with practical AI skills. Vendor-neutral workshops and strategic consulting for Melbourne SMEs."
      />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }} />

      {/* ═══ HERO ═══ */}
      <section ref={heroRef} className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20">
        {/* Background layers */}
        <div className="absolute inset-0 z-0">
          <div className="absolute inset-0 bg-black" />
          <RetroGrid angle={65} cellSize={50} opacity={0.4} lineColor="#12B5CB" />
          <DotGrid />
          <RadialGlow className="w-[600px] h-[600px] -top-40 left-1/2 -translate-x-1/2" color="#12B5CB" />
          <RadialGlow className="w-[400px] h-[400px] bottom-0 right-0" color="#FA903E" />
          {/* Top radial accent */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-screen h-[600px] bg-[radial-gradient(ellipse_50%_80%_at_50%_-20%,rgba(18,181,203,0.15),transparent)]" />
        </div>

        <div className="container relative z-10">
          <motion.div
            style={{ y: contentY, opacity: contentOpacity }}
            className="max-w-5xl mx-auto text-center"
          >
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              transition={{ duration: 0.8, ease: "easeOut" }}
              className="mb-8 flex justify-center"
            >
              <div className="px-5 py-2.5 rounded-full bg-white/[0.03] border border-white/[0.08] backdrop-blur-2xl flex items-center gap-3 hover:border-[#12B5CB]/30 transition-colors">
                <div className="flex -space-x-1.5">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="w-5 h-5 rounded-full bg-gradient-to-br from-[#12B5CB] to-[#12B5CB]/60 border-2 border-black flex items-center justify-center">
                      <Zap className="w-2.5 h-2.5 text-black" />
                    </div>
                  ))}
                </div>
                <span className="text-[11px] font-semibold text-white/60 uppercase tracking-[0.2em]" style={{ fontFamily: "var(--font-mono)" }}>
                  Strategic AI Orchestration
                </span>
                <ChevronRight className="w-3.5 h-3.5 text-white/30" />
              </div>
            </motion.div>

            {/* Heading with gradient text */}
            <motion.h1
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, delay: 0.2, ease: [0.215, 0.61, 0.355, 1] }}
              className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl xl:text-[6.5rem] font-black leading-[0.9] tracking-tighter mb-8"
              style={{ fontFamily: "var(--font-heading)" }}
            >
              <span className="bg-clip-text text-transparent bg-[linear-gradient(180deg,_#FFF_0%,_rgba(255,255,255,0.4)_100%)]">
                Intelligence{" "}
              </span>
              <br className="hidden sm:block" />
              <span className="bg-clip-text text-transparent bg-[linear-gradient(180deg,_#FFF_0%,_rgba(255,255,255,0.4)_100%)]">
                that{" "}
              </span>
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-[#12B5CB] via-[#12B5CB] to-[#FA903E]">
                transforms.
              </span>
            </motion.h1>

            {/* Subtext */}
            <motion.p
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, delay: 0.5 }}
              className="text-lg md:text-xl lg:text-2xl text-white/50 leading-relaxed mb-12 max-w-2xl mx-auto font-medium"
            >
              We don't just teach AI; we architect{" "}
              <span className="text-[#12B5CB] font-semibold">cognitive operations</span> for
              Melbourne's most ambitious SMEs.
            </motion.p>

            {/* CTAs */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.8 }}
              className="flex flex-wrap items-center justify-center gap-4 md:gap-6"
            >
              <Link href="/book" className="cursor-pointer">
                <span className="group relative inline-flex items-center gap-2 px-8 md:px-10 py-4 md:py-5 bg-[#12B5CB] text-black font-black rounded-full overflow-hidden hover:scale-[1.03] active:scale-[0.98] transition-all duration-300 shadow-[0_0_30px_rgba(18,181,203,0.3)] hover:shadow-[0_0_50px_rgba(18,181,203,0.5)]">
                  <span className="relative z-10">Initiate Audit</span>
                  <ArrowRight className="w-5 h-5 relative z-10 group-hover:translate-x-1 transition-transform" />
                  <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/25 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
                </span>
              </Link>
              <Link href="/workshops" className="cursor-pointer">
                <span className="group inline-flex items-center gap-2 px-8 md:px-10 py-4 md:py-5 rounded-full border border-white/10 bg-white/[0.03] text-white font-bold backdrop-blur-xl hover:bg-white/[0.08] hover:border-white/20 transition-all duration-300">
                  Explore Systems
                  <ChevronRight className="w-5 h-5 text-[#12B5CB] group-hover:translate-x-0.5 transition-transform" />
                </span>
              </Link>
            </motion.div>
          </motion.div>
        </div>

        {/* Floating cards — desktop only */}
        <div className="absolute bottom-20 left-8 hidden lg:block">
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 1, delay: 1.2 }}
          >
            <motion.div
              animate={prefersReducedMotion ? {} : { y: [-8, 8, -8] }}
              transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
              className="p-4 rounded-2xl border border-white/[0.06] bg-white/[0.03] backdrop-blur-2xl flex items-center gap-4"
            >
              <div className="w-10 h-10 rounded-xl bg-[#12B5CB]/10 border border-[#12B5CB]/20 flex items-center justify-center">
                <Shield className="w-5 h-5 text-[#12B5CB]" />
              </div>
              <div>
                <p className="text-[10px] font-bold text-[#12B5CB] uppercase tracking-wider">Governance</p>
                <p className="text-xs text-white/50">Secure by design.</p>
              </div>
            </motion.div>
          </motion.div>
        </div>

        <div className="absolute top-40 right-8 hidden lg:block">
          <motion.div
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 1, delay: 1.4 }}
          >
            <motion.div
              animate={prefersReducedMotion ? {} : { y: [8, -8, 8] }}
              transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
              className="p-4 rounded-2xl border border-white/[0.06] bg-white/[0.03] backdrop-blur-2xl flex items-center gap-4"
            >
              <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center">
                <Globe className="w-5 h-5 text-purple-400" />
              </div>
              <div>
                <p className="text-[10px] font-bold text-purple-400 uppercase tracking-wider">Scale</p>
                <p className="text-xs text-white/50">Global patterns.</p>
              </div>
            </motion.div>
          </motion.div>
        </div>

        {/* Bottom fade */}
        <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-black to-transparent pointer-events-none z-10" />
      </section>

      {/* ═══ TECH PARTNERS ═══ */}
      <TechPartners />

      {/* ═══ BENTO GRID — Stats & Services ═══ */}
      <section className="section-padding bg-black relative overflow-hidden">
        {/* Background accents */}
        <RadialGlow className="w-[500px] h-[500px] top-20 -left-40" color="#12B5CB" />
        <RadialGlow className="w-[400px] h-[400px] bottom-20 -right-20" color="#FA903E" />

        <div className="container relative z-10">
          {/* Section header */}
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16 md:mb-20"
          >
            <span className="inline-block text-[10px] md:text-xs font-semibold uppercase tracking-[0.3em] text-[#12B5CB]/70 mb-4" style={{ fontFamily: "var(--font-mono)" }}>
              The Benchmarks
            </span>
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-4" style={{ fontFamily: "var(--font-heading)" }}>
              Quantifying{" "}
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-[#12B5CB] to-[#12B5CB]/60">
                Impact.
              </span>
            </h2>
            <p className="text-white/40 max-w-xl mx-auto text-sm md:text-base">
              Real metrics from real engagements. No vanity numbers.
            </p>
          </motion.div>

          {/* Bento Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-4 max-w-6xl mx-auto">
            {/* Stats row - 3 columns */}
            <BentoCard
              title="Internal Efficiency"
              value="+42%"
              description="Average increase in task automation for SMEs after our strategic engagement."
              icon={<BarChart3 className="w-5 h-5 text-[#12B5CB]" />}
              accent="#12B5CB"
            />
            <BentoCard
              title="Skill Maturity"
              value="3.5x"
              description="Growth in team AI confidence post-workshop, measured via our proprietary assessment."
              icon={<Users className="w-5 h-5 text-[#FA903E]" />}
              accent="#FA903E"
            />
            <BentoCard
              title="Strategic Clarity"
              value="100%"
              description="Clients leave with a documented AI roadmap — zero exceptions."
              icon={<FileCheck className="w-5 h-5 text-emerald-400" />}
              accent="#34D399"
            />

            {/* Service preview cards - bottom row */}
            <BentoCard
              title="AI Workshops"
              description="Hands-on, vendor-neutral training for business leaders and teams. From Copilot to governance."
              icon={<BookOpen className="w-5 h-5 text-[#12B5CB]" />}
              href="/workshops"
              colSpan={2}
              accent="#12B5CB"
            />
            <BentoCard
              title="Strategy Consulting"
              description="We work alongside your leadership team to build a practical AI strategy aligned with your goals."
              icon={<Compass className="w-5 h-5 text-[#FA903E]" />}
              href="/services"
              accent="#FA903E"
            />
          </div>
        </div>
      </section>

      {/* ═══ CTA BANNER ═══ */}
      <section className="relative py-24 md:py-32 overflow-hidden">
        {/* Gradient background */}
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-br from-[#12B5CB]/10 via-black to-[#FA903E]/10" />
          <div
            className="absolute inset-0"
            style={{
              backgroundImage: `radial-gradient(circle, rgba(255,255,255,0.03) 1px, transparent 1px)`,
              backgroundSize: "24px 24px",
            }}
          />
          {/* Animated border glow - top */}
          <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#12B5CB]/40 to-transparent" />
          {/* Animated border glow - bottom */}
          <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#FA903E]/40 to-transparent" />
        </div>

        {/* Radial glows */}
        <RadialGlow className="w-[600px] h-[400px] top-0 left-1/4" color="#12B5CB" />
        <RadialGlow className="w-[600px] h-[400px] bottom-0 right-1/4" color="#FA903E" />

        <div className="container relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="max-w-4xl mx-auto text-center"
          >
            <h2
              className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-white mb-6 leading-[0.95] tracking-tight"
              style={{ fontFamily: "var(--font-heading)" }}
            >
              The future belongs to the{" "}
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-[#FA903E] to-[#FA903E]/60">
                Prepared.
              </span>
            </h2>
            <p className="text-lg md:text-xl text-white/50 mb-12 max-w-2xl mx-auto leading-relaxed">
              Join the elite group of Melbourne SMEs defining the new AI economy.
            </p>
            <div className="flex flex-wrap justify-center gap-4 md:gap-6">
              <Link href="/book" className="cursor-pointer">
                <motion.span
                  whileHover={{ scale: 1.03 }}
                  whileTap={{ scale: 0.98 }}
                  className="group relative inline-flex items-center gap-2 px-10 md:px-12 py-5 md:py-6 rounded-full font-black text-black overflow-hidden"
                  style={{
                    background: "linear-gradient(135deg, #12B5CB 0%, #12B5CB 50%, #0EA5B7 100%)",
                    boxShadow: "0 0 40px rgba(18,181,203,0.3), inset 0 1px 0 rgba(255,255,255,0.2)",
                  }}
                >
                  <span className="relative z-10">Secure Your Strategic Audit</span>
                  <ArrowRight className="w-5 h-5 relative z-10 group-hover:translate-x-1 transition-transform" />
                  <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
                </motion.span>
              </Link>
              <Link href="/contact" className="cursor-pointer">
                <motion.span
                  whileHover={{ scale: 1.03 }}
                  whileTap={{ scale: 0.98 }}
                  className="inline-flex items-center gap-2 px-10 md:px-12 py-5 md:py-6 rounded-full border border-white/10 bg-white/[0.03] text-white font-bold backdrop-blur-xl hover:bg-white/[0.08] hover:border-white/20 transition-all duration-300"
                >
                  Connect with Experts
                </motion.span>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </>
  );
}
