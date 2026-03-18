/**
 * TechPartners — "We Train Across All Major AI Platforms" logo bar
 * Design: Luminous Depth — glass surface, infinite horizontal scroll, monochrome logos that colorize on hover
 */
import { motion } from "framer-motion";

interface Partner {
  name: string;
  logo: string;
  url: string;
  invert?: boolean; // true = logo is dark on transparent, needs invert for dark bg
  roundedFull?: boolean; // circular logos
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
      className="flex flex-col items-center justify-center gap-2 px-6 md:px-8 shrink-0 group"
      title={partner.name}
    >
      <div
        className={`
          w-14 h-14 md:w-16 md:h-16 flex items-center justify-center
          ${partner.roundedFull ? "rounded-full overflow-hidden" : ""}
          grayscale opacity-50 group-hover:grayscale-0 group-hover:opacity-100
          transition-all duration-500
        `}
      >
        <img
          src={partner.logo}
          alt={partner.name}
          className={`
            max-w-full max-h-full object-contain
            ${partner.invert ? "invert brightness-200" : ""}
            ${partner.roundedFull ? "w-full h-full object-cover" : ""}
          `}
          loading="lazy"
        />
      </div>
      <span className="text-[11px] md:text-xs font-mono tracking-wider text-muted-foreground/60 group-hover:text-cyan whitespace-nowrap transition-colors duration-300">
        {partner.name}
      </span>
    </a>
  );
}

export default function TechPartners() {
  // Duplicate for seamless infinite scroll
  const doubled = [...PARTNERS, ...PARTNERS];

  return (
    <section className="relative py-16 md:py-20 overflow-hidden">
      {/* Subtle top/bottom borders */}
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-cyan/20 to-transparent" />
      <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-cyan/20 to-transparent" />

      {/* Section header */}
      <div className="container mb-10 md:mb-14">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-60px" }}
          transition={{ duration: 0.6 }}
          className="text-center"
        >
          <span className="inline-block text-xs md:text-sm font-mono tracking-[0.2em] uppercase text-cyan/80 mb-3">
            Platform Expertise
          </span>
          <h2 className="text-2xl md:text-3xl lg:text-4xl font-heading font-bold text-foreground">
            We train across{" "}
            <span className="text-cyan text-glow-cyan">all major AI platforms</span>
          </h2>
          <p className="mt-3 text-sm md:text-base text-muted-foreground max-w-2xl mx-auto">
            Vendor-neutral means we know every platform inside out. Our workshops cover the tools that matter — so you get unbiased, practical guidance.
          </p>
        </motion.div>
      </div>

      {/* Infinite scroll marquee */}
      <div className="relative">
        {/* Fade edges */}
        <div className="absolute left-0 top-0 bottom-0 w-20 md:w-32 z-10 bg-gradient-to-r from-background to-transparent pointer-events-none" />
        <div className="absolute right-0 top-0 bottom-0 w-20 md:w-32 z-10 bg-gradient-to-l from-background to-transparent pointer-events-none" />

        {/* Scrolling track */}
        <div className="flex animate-marquee hover:[animation-play-state:paused]">
          {doubled.map((partner, i) => (
            <LogoItem key={`${partner.name}-${i}`} partner={partner} />
          ))}
        </div>
      </div>
    </section>
  );
}
