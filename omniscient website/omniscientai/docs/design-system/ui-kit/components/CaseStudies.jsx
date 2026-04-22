function CaseStudies() {
  const cs = [
    {sector:'Health', title:'Imaging triage for a radiology network', meta:'8-week pilot · 2025', featured:true},
    {sector:'Defense', title:'Edge-perception review for UAV partner', meta:'Spec + code audit'},
    {sector:'Agentic ops', title:'Outbound qualification agent for a Series A SaaS', meta:'Shipped Q1 2026'},
  ];
  return (
    <section id="work" style={{padding:'96px 40px', maxWidth:1240, margin:'0 auto'}}>
      <div style={{marginBottom:48}}>
        <div style={{fontFamily:'var(--font-text)', fontSize:12, fontWeight:600, letterSpacing:'0.14em', textTransform:'uppercase', color:'var(--ink-400)', marginBottom:16}}>Recent work</div>
        <h2 style={{fontSize:48, fontWeight:700, letterSpacing:'-0.025em', margin:0, color:'var(--ink)'}}>A representative sample. Not the portfolio.</h2>
      </div>
      <div style={{display:'grid', gridTemplateColumns:'1.5fr 1fr 1fr', gap:24}}>
        {cs.map((c, i) => (
          <article key={c.title} style={{
            border:'1px solid var(--line)', borderRadius:8, padding:24,
            background:'var(--paper)', minHeight: c.featured ? 380 : 280,
            display:'flex', flexDirection:'column', justifyContent:'space-between', gap:16,
            position:'relative', overflow:'hidden'
          }}>
            <div>
              <span style={{background:'var(--paper-100)', color:'var(--ink)', fontFamily:'var(--font-text)', fontSize:12, fontWeight:600, padding:'3px 10px', borderRadius:999, border:'1px solid var(--line)'}}>{c.sector}</span>
            </div>
            {c.featured && (
              <div style={{position:'absolute', top:-60, right:-60, width:260, height:260, backgroundImage:'url(../../assets/brand-graphic-circles.png)', backgroundSize:'cover', opacity:0.25}}/>
            )}
            <div style={{position:'relative'}}>
              <h3 style={{fontSize: c.featured ? 28 : 20, fontWeight:700, letterSpacing:'-0.02em', margin:'0 0 8px', color:'var(--ink)', lineHeight:1.15}}>{c.title}</h3>
              <div style={{fontFamily:'var(--font-mono)', fontSize:12, color:'var(--ink-400)'}}>{c.meta}</div>
              <a href="#" style={{display:'inline-block', marginTop:16, fontWeight:600, fontSize:14, color:'var(--ink)', borderBottom:0}}>Read the case study →</a>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
window.CaseStudies = CaseStudies;
