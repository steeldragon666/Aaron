function Services() {
  const items = [
    {kind:'Workshop', title:'AI readiness, in two days', price:'From AU$14,000', body:'On-site intensive for ops and product teams. We audit your stack, pick two wins, and leave you with working prototypes.', featured:false},
    {kind:'Engagement', title:'Agentic ops pilot', price:'6-week sprint', body:'One named practitioner embeds with your team to ship an agent against one measurable outcome.', featured:true},
    {kind:'Advisory', title:'Fractional AI lead', price:'Monthly retainer', body:'For teams without a senior AI hire: strategy, evals, vendor selection, and hands-on when it counts.', featured:false},
  ];
  return (
    <section id="workshops" style={{padding:'40px 40px 96px', maxWidth:1240, margin:'0 auto'}}>
      <div style={{display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:24}}>
        {items.map((it) => {
          const fg = it.featured ? 'var(--paper)' : 'var(--ink)';
          const sub = it.featured ? 'var(--ink-100)' : 'var(--ink-600)';
          const eyebrow = it.featured ? 'var(--blue-300)' : 'var(--ink-400)';
          return (
            <div key={it.title} style={{
              borderRadius:8,
              padding:28,
              background: it.featured ? 'var(--ink)' : 'var(--paper)',
              border: it.featured ? '1px solid var(--ink)' : '1px solid var(--line)',
              display:'flex', flexDirection:'column', gap:16, minHeight:240
            }}>
              <div style={{display:'flex', justifyContent:'space-between'}}>
                <div style={{fontFamily:'var(--font-text)', fontSize:12, fontWeight:600, letterSpacing:'0.14em', textTransform:'uppercase', color:eyebrow}}>{it.kind}</div>
                <div style={{fontFamily:'var(--font-mono)', fontSize:12, color:sub}}>{it.price}</div>
              </div>
              <h3 style={{fontSize:26, fontWeight:700, letterSpacing:'-0.02em', color:fg, margin:0, lineHeight:1.1}}>{it.title}</h3>
              <p style={{fontSize:15, lineHeight:1.55, color:sub, margin:0, flex:1}}>{it.body}</p>
              <a href="#" style={{color:fg, fontWeight:600, fontSize:14, borderBottom:0}}>Learn more →</a>
            </div>
          );
        })}
      </div>
    </section>
  );
}
window.Services = Services;
