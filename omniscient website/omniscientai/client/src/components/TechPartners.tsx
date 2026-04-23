/**
 * TechPartners — Premium logo marquee with fade edges and smooth animation
 * Design: 21st.dev-inspired, polished with proper sizing and spacing
 */
import { motion, useReducedMotion } from "framer-motion";

interface Partner {
  name: string;
  logo: string;
  url: string;
  invert?: boolean;
  roundedFull?: boolean;
}

const PARTNERS: Partner[] = [
  {
    name: "OpenAI",
    logo: "https://d2xsxph8kpxj0f.cloudfront.net/310419663026972742/it6qHcTHLu2dmqyuKKnamM/openai_c072d2ec.png",
    url: "https://openai.com",
    invert: true,
  },
  {
    name: "Anthropic",
    logo: "https://d2xsxph8kpxj0f.cloudfront.net/310419663026972742/it6qHcTHLu2dmqyuKKnamM/anthropic_9a5f4b5b.jpg",
    url: "https://anthropic.com",
    roundedFull: true,
  },
  {
    name: "Google Gemini",
    logo: "https://d2xsxph8kpxj0f.cloudfront.net/310419663026972742/it6qHcTHLu2dmqyuKKnamM/gemini_0d825310.png",
    url: "https://gemini.google.com",
  },
  {
    name: "Grok (xAI)",
    logo: "https://d2xsxph8kpxj0f.cloudfront.net/310419663026972742/it6qHcTHLu2dmqyuKKnamM/grok_b546587f.png",
    url: "https://grok.x.ai",
    invert: true,
  },
  {
    name: "Microsoft Copilot",
    logo: "https://d2xsxph8kpxj0f.cloudfront.net/310419663026972742/it6qHcTHLu2dmqyuKKnamM/copilot_14c231e8.jpg",
    url: "https://copilot.microsoft.com",
    roundedFull: true,
  },
  {
    name: "Mistral AI",
    logo: "https://d2xsxph8kpxj0f.cloudfront.net/310419663026972742/it6qHcTHLu2dmqyuKKnamM/mistral_24823c81.png",
    url: "https://mistral.ai",
    invert: true,
  },
  {
    name: "Hugging Face",
    logo: "https://d2xsxph8kpxj0f.cloudfront.net/310419663026972742/it6qHcTHLu2dmqyuKKnamM/huggingface_32a8d242.png",
    url: "https://huggingface.co",
  },
  {
    name: "DeepSeek",
    logo: "https://d2xsxph8kpxj0f.cloudfront.net/310419663026972742/it6qHcTHLu2dmqyuKKnamM/deepseek_32175fe6.png",
    url: "https://deepseek.com",
  },
  {
    name: "Moonshot AI",
    logo: "https://d2xsxph8kpxj0f.cloudfront.net/310419663026972742/it6qHcTHLu2dmqyuKKnamM/moonshot_d92c369f.jpg",
    url: "https://moonshot.ai",
    roundedFull: true,
  },
  {
    name: "NVIDIA Inception",
    logo: "https://d2xsxph8kpxj0f.cloudfront.net/310419663026972742/it6qHcTHLu2dmqyuKKnamM/nvidia-inception_7a0ebf6c.png",
    url: "https://www.nvidia.com/en-us/startups/",
    roundedFull: true,
  },
  {
    name: "Perplexity",
    logo: "https://d2xsxph8kpxj0f.cloudfront.net/310419663026972742/it6qHcTHLu2dmqyuKKnamM/perplexity_034e6dcb.png",
    url: "https://perplexity.ai",
    invert: true,
  },
];

function LogoItem({ partner }: { partner: Partner }) {
  return (
    <a
      href={partner.url}
      target="_blank"
      rel="noopener noreferrer"
      className="flex flex-col items-center justify-center gap-3 px-8 md:px-10 shrink-0 group cursor-pointer"
      title={partner.name}
    >
      <div
        className={`
          w-12 h-12 md:w-14 md:h-14 flex items-center justify-center
          ${partner.roundedFull ? "rounded-full overflow-hidden" : ""}
          grayscale opacity-40 group-hover:grayscale-0 group-hover:opacity-90
          transition-all duration-500 ease-out
          group-hover:scale-110
        `}
      >
        <img
          src={partner.logo}
          alt={partner.name}
          width={56}
          height={56}
          loading="lazy"
          className={`
            max-w-full max-h-full object-contain
            ${partner.invert ? "invert brightness-200" : ""}
            ${partner.roundedFull ? "w-full h-full object-cover" : ""}
          `}
        />
      </div>
      <span className="text-[10px] md:text-[11px] font-mono tracking-wider text-white/30 group-hover:text-[#12B5CB] whitespace-nowrap transition-colors duration-300">
        {partner.name}
      </span>
    </a>
  );
}

export default function TechPartners() {
  const prefersReducedMotion = useReducedMotion();
  const doubled = [...PARTNERS, ...PARTNERS];

  return (
    <section className="relative py-16 md:py-24 overflow-hidden">
      {/* Subtle dividers */}
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-[#12B5CB]/15 to-transparent" />
      <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-[#12B5CB]/15 to-transparent" />

      {/* Section header */}
      <div className="container mb-12 md:mb-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-60px" }}
          transition={{ duration: 0.6 }}
          className="text-center"
        >
          <span className="inline-block text-[10px] md:text-xs font-mono tracking-[0.3em] uppercase text-[#12B5CB]/60 mb-3">
            Platform Expertise
          </span>
          <h2 className="text-2xl md:text-3xl lg:text-4xl font-bold text-white" style={{ fontFamily: "var(--font-heading)" }}>
            We train across{" "}
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-[#12B5CB] to-[#12B5CB]/60">
              all major AI platforms
            </span>
          </h2>
          <p className="mt-3 text-sm md:text-base text-white/40 max-w-xl mx-auto">
            Vendor-neutral means we know every platform inside out — so you get unbiased, practical guidance.
          </p>
        </motion.div>
      </div>

      {/* Logo marquee */}
      <div className="relative">
        {/* Fade edges — wider and smoother */}
        <div className="absolute left-0 top-0 bottom-0 w-24 md:w-48 z-10 bg-gradient-to-r from-background via-background/80 to-transparent pointer-events-none" />
        <div className="absolute right-0 top-0 bottom-0 w-24 md:w-48 z-10 bg-gradient-to-l from-background via-background/80 to-transparent pointer-events-none" />

        {prefersReducedMotion ? (
          <div className="flex flex-wrap justify-center gap-4 px-8">
            {PARTNERS.map((partner) => (
              <LogoItem key={partner.name} partner={partner} />
            ))}
          </div>
        ) : (
          <div
            className="flex animate-marquee hover:[animation-play-state:paused] focus-within:[animation-play-state:paused]"
            role="marquee"
            aria-label="AI platform partner logos"
          >
            {doubled.map((partner, i) => (
              <LogoItem key={`${partner.name}-${i}`} partner={partner} />
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
