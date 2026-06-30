function Nav() {
  return (
    <nav style={{
      position: 'sticky', top: 0, zIndex: 10,
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '16px 40px',
      background: 'rgba(255,255,255,0.72)',
      backdropFilter: 'saturate(1.2) blur(14px)',
      WebkitBackdropFilter: 'saturate(1.2) blur(14px)',
      borderBottom: '1px solid var(--line)'
    }}>
      <a href="#" style={{display:'flex', alignItems:'center', gap:10, borderBottom:0}}>
        <div style={{width:32, height:32, background:'var(--ink)', borderRadius:999}}/>
        <span style={{fontFamily:'var(--font-display)', fontWeight:700, fontSize:18, letterSpacing:'-0.01em', color:'var(--ink)'}}>Omniscient AI</span>
      </a>
      <div style={{display:'flex', gap:28, fontFamily:'var(--font-text)', fontSize:14, fontWeight:500, color:'var(--ink-600)'}}>
        <a href="#workshops" style={{color:'inherit'}}>Workshops</a>
        <a href="#consulting" style={{color:'inherit'}}>Consulting</a>
        <a href="#work" style={{color:'inherit'}}>Case studies</a>
        <a href="#about" style={{color:'inherit'}}>About</a>
      </div>
      <a href="#book" style={{
        background:'var(--blue)', color:'var(--paper)', border:0,
        padding:'9px 16px', borderRadius:6,
        fontFamily:'var(--font-text)', fontWeight:600, fontSize:14, borderBottom:0
      }}>Book a call →</a>
    </nav>
  );
}
window.Nav = Nav;
