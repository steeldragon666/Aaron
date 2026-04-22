function CTAStrip() {
  return (
    <section id="book" style={{padding:'0 40px 96px'}}>
      <div style={{maxWidth:1240, margin:'0 auto', border:'1.5px solid var(--ink)', borderRadius:8, padding:'48px 48px', display:'grid', gridTemplateColumns:'1.4fr 1fr', alignItems:'center', gap:40, background:'var(--paper)'}}>
        <div>
          <h2 style={{fontSize:40, fontWeight:700, letterSpacing:'-0.025em', margin:'0 0 12px', color:'var(--ink)', lineHeight:1.1}}>Got an idea and twenty minutes?</h2>
          <p style={{fontSize:16, color:'var(--ink-600)', margin:0, maxWidth:520}}>Book a short call. We'll tell you fast whether we're the right fit. If we're not, we'll point you to someone who is.</p>
        </div>
        <div style={{display:'flex', gap:12, justifyContent:'flex-end', flexWrap:'wrap'}}>
          <a href="#" style={{background:'var(--blue)', color:'var(--paper)', padding:'14px 22px', borderRadius:6, fontWeight:600, fontSize:15, borderBottom:0}}>Book a call →</a>
          <a href="mailto:hello@omniscientai.io" style={{background:'var(--paper)', color:'var(--ink)', border:'1.5px solid var(--ink)', padding:'13px 21px', borderRadius:6, fontWeight:600, fontSize:15, borderBottom:0}}>hello@omniscientai.io</a>
        </div>
      </div>
    </section>
  );
}
window.CTAStrip = CTAStrip;
