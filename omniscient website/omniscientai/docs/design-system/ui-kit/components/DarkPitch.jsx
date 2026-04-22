function DarkPitch() {
  return (
    <section style={{background:'var(--ink)', padding:'96px 40px', position:'relative', overflow:'hidden'}}>
      <div style={{maxWidth:1240, margin:'0 auto', display:'grid', gridTemplateColumns:'1.4fr 1fr', gap:72, alignItems:'center', position:'relative', zIndex:1}}>
        <div>
          <div style={{fontFamily:'var(--font-text)', fontSize:12, fontWeight:600, letterSpacing:'0.14em', textTransform:'uppercase', color:'var(--blue-300)', marginBottom:24}}>Why vendor-neutral</div>
          <h2 style={{fontSize:56, fontWeight:700, letterSpacing:'-0.025em', color:'var(--paper)', margin:'0 0 24px', lineHeight:1.05}}>Model lock-in is a tax. We don't charge it.</h2>
          <p style={{fontSize:18, lineHeight:1.5, color:'var(--ink-200)', maxWidth:560, margin:'0 0 32px'}}>
            We test across providers, pick the right tool for your job, and teach your team to swap vendors as the frontier moves. The gains belong to you, not your LLM bill.
          </p>
          <div style={{display:'flex', gap:32, flexWrap:'wrap'}}>
            <div><div style={{fontFamily:'var(--font-display)', fontSize:44, fontWeight:700, color:'var(--paper)', letterSpacing:'-0.02em'}}>37</div><div style={{fontFamily:'var(--font-mono)', fontSize:12, color:'var(--ink-300)', marginTop:4}}>SMEs trained</div></div>
            <div><div style={{fontFamily:'var(--font-display)', fontSize:44, fontWeight:700, color:'var(--paper)', letterSpacing:'-0.02em'}}>12<span style={{color:'var(--blue)'}}>×</span></div><div style={{fontFamily:'var(--font-mono)', fontSize:12, color:'var(--ink-300)', marginTop:4}}>avg. ops throughput</div></div>
            <div><div style={{fontFamily:'var(--font-display)', fontSize:44, fontWeight:700, color:'var(--paper)', letterSpacing:'-0.02em'}}>0</div><div style={{fontFamily:'var(--font-mono)', fontSize:12, color:'var(--ink-300)', marginTop:4}}>junior bait-and-switch</div></div>
          </div>
        </div>
        <div style={{backgroundImage:'url(../../assets/brand-graphic-circles.png)', backgroundSize:'contain', backgroundRepeat:'no-repeat', backgroundPosition:'center right', minHeight:360, filter:'brightness(1.02)'}}/>
      </div>
    </section>
  );
}
window.DarkPitch = DarkPitch;
