function Hero() {
  return (
    <section style={{padding:'72px 40px 96px', maxWidth:1240, margin:'0 auto'}}>
      <div style={{display:'grid', gridTemplateColumns:'1.3fr 1fr', gap:64, alignItems:'center'}}>
        <div>
          <div style={{fontFamily:'var(--font-text)', fontSize:12, fontWeight:600, letterSpacing:'0.14em', textTransform:'uppercase', color:'var(--ink-400)', marginBottom:24}}>
            Intelligence // Connectivity // Innovation
          </div>
          <h1 style={{fontSize:'clamp(48px, 6.2vw, 88px)', fontWeight:800, letterSpacing:'-0.03em', lineHeight:0.95, color:'var(--ink)', margin:'0 0 24px'}}>
            Unleashing the power of intelligent connections.
          </h1>
          <p style={{fontSize:20, lineHeight:1.45, color:'var(--ink-600)', maxWidth:560, margin:'0 0 32px'}}>
            Vendor-neutral AI training and consulting for Melbourne SMEs. We work in short engagements with named practitioners — every workshop leaves your team with a shippable artefact.
          </p>
          <div style={{display:'flex', gap:12, flexWrap:'wrap'}}>
            <a href="#book" style={{background:'var(--blue)', color:'var(--paper)', padding:'14px 22px', borderRadius:6, fontWeight:600, fontSize:15, borderBottom:0}}>Book a 20-minute call →</a>
            <a href="#work" style={{background:'var(--paper)', color:'var(--ink)', border:'1.5px solid var(--ink)', padding:'13px 21px', borderRadius:6, fontWeight:600, fontSize:15, borderBottom:0}}>See our work</a>
          </div>
        </div>
        <div style={{
          backgroundImage:'url(../../assets/brand-graphic-circles.png)',
          backgroundSize:'contain',
          backgroundRepeat:'no-repeat',
          backgroundPosition:'right center',
          minHeight:440
        }}/>
      </div>
    </section>
  );
}
window.Hero = Hero;
