// Insight Article — OmniscientAI
import { useParams, Link } from "wouter";
import { motion } from "framer-motion";
import { ArrowLeft, Clock, Share2, Linkedin, Twitter } from "lucide-react";
import { INSIGHTS } from "@/lib/data";

export default function InsightArticle() {
  const { slug } = useParams<{ slug: string }>();
  const article = INSIGHTS.find((a) => a.slug === slug);

  if (!article) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-[#E8E8E8] mb-4" style={{ fontFamily: "var(--font-heading)" }}>Article not found</h1>
          <Link href="/insights" className="text-[#12B5CB] hover:underline">Back to insights</Link>
        </div>
      </div>
    );
  }

  const related = INSIGHTS.filter((a) => a.slug !== slug && a.category === article.category).slice(0, 2);

  return (
    <>
      <section className="pt-28 pb-8">
        <div className="container max-w-4xl">
          <Link href="/insights" className="inline-flex items-center gap-1 text-sm text-white/60 hover:text-[#12B5CB] transition-colors mb-6 cursor-pointer">
            <ArrowLeft className="w-4 h-4" /> Back to insights
          </Link>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <div className="flex items-center gap-3 mb-4">
              <span className="text-xs font-medium text-[#12B5CB] px-2 py-0.5 rounded-full bg-[#12B5CB]/10">{article.categoryLabel}</span>
              <span className="text-xs text-white/60 flex items-center gap-1" style={{ fontFamily: "var(--font-mono)" }}>
                <Clock className="w-3 h-3" /> {article.readTime}
              </span>
              <span className="text-xs text-white/60">{article.date}</span>
            </div>
            <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-[#E8E8E8] leading-tight mb-4" style={{ fontFamily: "var(--font-heading)" }}>
              {article.title}
            </h1>
            <div className="flex items-center gap-3 mb-8">
              <div className="w-10 h-10 rounded-full bg-[#12B5CB]/10 border border-[#12B5CB]/20 flex items-center justify-center">
                <span className="text-sm font-bold text-[#12B5CB]">O</span>
              </div>
              <div>
                <p className="text-sm font-medium text-[#E8E8E8]">{article.author}</p>
                <p className="text-xs text-white/60">AI Training & Consulting Specialists</p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      <div className="container max-w-4xl pb-20">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_200px] gap-8">
          <motion.article
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="prose prose-invert max-w-none"
          >
            <div className="text-[#E8E8E8]/90 leading-relaxed space-y-6">
              <p className="text-lg">{article.excerpt}</p>
              <p>This article is part of our ongoing series helping Australian SMEs navigate the AI landscape with practical, vendor-neutral advice. Our team brings real-world implementation experience across multiple industries.</p>
              <h2 className="text-2xl font-bold text-[#E8E8E8] mt-8 mb-4" style={{ fontFamily: "var(--font-heading)" }}>Key Takeaways</h2>
              <ul className="space-y-2 text-[#E8E8E8]/80">
                <li>Start with a clear business problem, not a technology solution</li>
                <li>Evaluate AI tools based on your specific use case, not marketing claims</li>
                <li>Build internal capability alongside external implementation</li>
                <li>Measure success with business metrics, not technical metrics</li>
              </ul>
              <p>For a deeper dive into any of these topics, explore our <Link href="/workshops" className="text-[#12B5CB] hover:underline">workshop offerings</Link> or <Link href="/book" className="text-[#12B5CB] hover:underline">book a free strategy session</Link>.</p>
            </div>

            {/* Email capture inline */}
            <div className="glass-card rounded-xl p-6 mt-10">
              <h3 className="text-lg font-bold text-[#E8E8E8] mb-2" style={{ fontFamily: "var(--font-heading)" }}>Get insights like this delivered weekly</h3>
              <p className="text-sm text-white/60 mb-4">Practical AI insights for Australian SMEs. No spam.</p>
              <form onSubmit={(e) => e.preventDefault()} className="flex flex-col sm:flex-row gap-3">
                <input type="email" placeholder="you@company.com" className="flex-1 px-4 py-2.5 rounded-lg bg-[#0A0A0A] border border-[#333333] text-[#E8E8E8] placeholder-white/40 focus:border-[#12B5CB] focus:outline-none transition-colors text-sm" />
                <button className="px-5 py-2.5 text-sm font-semibold text-[#0A0A0A] bg-[#12B5CB] rounded-lg hover:bg-[#12B5CB]/90 transition-all whitespace-nowrap cursor-pointer">Subscribe</button>
              </form>
            </div>
          </motion.article>

          {/* Sidebar */}
          <aside className="hidden lg:block">
            <div className="sticky top-24 space-y-6">
              {/* Share */}
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wider text-white/60 mb-3" style={{ fontFamily: "var(--font-mono)" }}>Share</h4>
                <div className="flex gap-2">
                  <button className="w-9 h-9 rounded-lg bg-white/5 border border-[#333333] flex items-center justify-center text-white/60 hover:text-[#12B5CB] hover:border-[#12B5CB]/30 transition-colors cursor-pointer">
                    <Linkedin className="w-4 h-4" />
                  </button>
                  <button className="w-9 h-9 rounded-lg bg-white/5 border border-[#333333] flex items-center justify-center text-white/60 hover:text-[#12B5CB] hover:border-[#12B5CB]/30 transition-colors cursor-pointer">
                    <Twitter className="w-4 h-4" />
                  </button>
                  <button className="w-9 h-9 rounded-lg bg-white/5 border border-[#333333] flex items-center justify-center text-white/60 hover:text-[#12B5CB] hover:border-[#12B5CB]/30 transition-colors cursor-pointer">
                    <Share2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Related */}
              {related.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-white/60 mb-3" style={{ fontFamily: "var(--font-mono)" }}>Related</h4>
                  <div className="space-y-3">
                    {related.map((r) => (
                      <Link key={r.slug} href={`/insights/${r.slug}`}>
                        <div className="text-sm text-[#E8E8E8]/80 hover:text-[#12B5CB] transition-colors leading-snug">
                          {r.title}
                        </div>
                      </Link>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </aside>
        </div>
      </div>
    </>
  );
}
