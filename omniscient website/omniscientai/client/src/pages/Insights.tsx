// Insights Hub — OmniscientAI
import { Link } from "wouter";
import { motion } from "framer-motion";
import { ArrowRight, Clock, Tag } from "lucide-react";
import { INSIGHTS } from "@/lib/data";
import { useState } from "react";

const categories = [
  { value: "all", label: "All" },
  { value: "ai-for-business", label: "AI for Business" },
  { value: "ai-governance", label: "AI Governance" },
  { value: "ai-tools", label: "AI Tools" },
  { value: "melbourne-ai", label: "Melbourne AI" },
];

export default function Insights() {
  const [filter, setFilter] = useState("all");
  const filtered = filter === "all" ? INSIGHTS : INSIGHTS.filter((a) => a.category === filter);
  const featured = INSIGHTS.filter((a) => a.featured);

  return (
    <>
      <section className="relative pt-32 pb-16 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-[#12B5CB]/5 to-transparent pointer-events-none" />
        <div className="container relative">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <span className="inline-block text-xs font-semibold uppercase tracking-[0.2em] text-[#12B5CB] mb-3" style={{ fontFamily: "var(--font-mono)" }}>INSIGHTS</span>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-[#E8E8E8] leading-tight mb-4" style={{ fontFamily: "var(--font-heading)" }}>
              Practical AI knowledge for <span className="text-[#12B5CB]">Australian SMEs</span>
            </h1>
            <p className="text-lg text-[#888888] max-w-2xl leading-relaxed">
              Vendor-neutral insights, guides, and analysis to help your business navigate the AI landscape with confidence.
            </p>
          </motion.div>
        </div>
      </section>

      <section className="section-padding bg-[#0A0A0A]">
        <div className="container">
          {/* Category filters */}
          <div className="flex flex-wrap gap-2 mb-10">
            {categories.map((cat) => (
              <button
                key={cat.value}
                onClick={() => setFilter(cat.value)}
                className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
                  filter === cat.value
                    ? "bg-[#12B5CB]/10 text-[#12B5CB] border border-[#12B5CB]/30"
                    : "text-[#888888] border border-[#333333] hover:text-[#E8E8E8] hover:border-[#12B5CB]/20"
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>

          {/* Featured articles */}
          {filter === "all" && featured.length > 0 && (
            <div className="mb-12">
              <h2 className="text-sm font-semibold uppercase tracking-[0.15em] text-[#888888] mb-6" style={{ fontFamily: "var(--font-mono)" }}>Featured</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {featured.map((article, i) => (
                  <motion.div
                    key={article.slug}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5, delay: i * 0.1 }}
                  >
                    <Link href={`/insights/${article.slug}`}>
                      <div className="glass-card rounded-2xl p-6 h-full group border-[#12B5CB]/10">
                        <div className="flex items-center gap-2 mb-3">
                          <span className="text-xs font-medium text-[#12B5CB] px-2 py-0.5 rounded-full bg-[#12B5CB]/10">{article.categoryLabel}</span>
                          <span className="text-xs text-[#888888] flex items-center gap-1" style={{ fontFamily: "var(--font-mono)" }}>
                            <Clock className="w-3 h-3" /> {article.readTime}
                          </span>
                        </div>
                        <h3 className="text-xl font-bold text-[#E8E8E8] mb-2 group-hover:text-[#12B5CB] transition-colors" style={{ fontFamily: "var(--font-heading)" }}>
                          {article.title}
                        </h3>
                        <p className="text-sm text-[#888888] leading-relaxed mb-4">{article.excerpt}</p>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-[#888888]">{article.date}</span>
                          <div className="flex items-center gap-1 text-sm text-[#12B5CB] font-medium group-hover:gap-2 transition-all">
                            Read <ArrowRight className="w-4 h-4" />
                          </div>
                        </div>
                      </div>
                    </Link>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {/* All articles grid */}
          <div>
            {filter === "all" && <h2 className="text-sm font-semibold uppercase tracking-[0.15em] text-[#888888] mb-6" style={{ fontFamily: "var(--font-mono)" }}>All Articles</h2>}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filtered.map((article, i) => (
                <motion.div
                  key={article.slug}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: i * 0.05 }}
                >
                  <Link href={`/insights/${article.slug}`}>
                    <div className="glass-card rounded-xl p-5 h-full group">
                      <div className="flex items-center gap-2 mb-3">
                        <span className="text-xs font-medium text-[#12B5CB] px-2 py-0.5 rounded-full bg-[#12B5CB]/10">{article.categoryLabel}</span>
                        <span className="text-xs text-[#888888]" style={{ fontFamily: "var(--font-mono)" }}>{article.readTime}</span>
                      </div>
                      <h3 className="text-lg font-semibold text-[#E8E8E8] mb-2 group-hover:text-[#12B5CB] transition-colors leading-snug" style={{ fontFamily: "var(--font-heading)" }}>
                        {article.title}
                      </h3>
                      <p className="text-sm text-[#888888] leading-relaxed mb-3 line-clamp-3">{article.excerpt}</p>
                      <span className="text-xs text-[#888888]">{article.date}</span>
                    </div>
                  </Link>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Email capture */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="mt-16"
          >
            <div className="glass-card rounded-2xl p-8 md:p-12 text-center max-w-2xl mx-auto">
              <h3 className="text-2xl font-bold text-[#E8E8E8] mb-3" style={{ fontFamily: "var(--font-heading)" }}>
                Get insights like this delivered weekly
              </h3>
              <p className="text-[#888888] mb-6">Practical AI insights for Australian SMEs. No spam. Unsubscribe anytime.</p>
              <form onSubmit={(e) => { e.preventDefault(); }} className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
                <input
                  type="email"
                  placeholder="you@company.com"
                  className="flex-1 px-4 py-3 rounded-lg bg-[#0A0A0A] border border-[#333333] text-[#E8E8E8] placeholder-[#888888] focus:border-[#12B5CB] focus:outline-none transition-colors"
                />
                <button className="px-6 py-3 text-sm font-semibold text-[#0A0A0A] bg-[#12B5CB] rounded-lg hover:bg-[#12B5CB]/90 transition-all whitespace-nowrap">
                  Subscribe
                </button>
              </form>
            </div>
          </motion.div>
        </div>
      </section>
    </>
  );
}
