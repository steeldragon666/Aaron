function Footer() {
  return (
    <footer style={{borderTop:'1px solid var(--line)', padding:'48px 40px', background:'var(--paper)'}}>
      <div style={{maxWidth:1240, margin:'0 auto', display:'grid', gridTemplateColumns:'1.3fr 1fr 1fr 1fr', gap:48}}>
        <div>
          <div style={{display:'flex', alignItems:'center', gap:10, marginBottom:16}}>
            <div style={{width:24, height:24, background:'var(--ink)', borderRadius:999}}/>
            <span style={{fontFamily:'var(--font-display)', fontWeight:700, fontSize:16, color:'var(--ink)'}}>Omniscient AI</span>
          </div>
          <p style={{fontSize:14, color:'var(--ink-400)', maxWidth:320, margin:0}}>Vendor-neutral AI training and consulting. Melbourne, Australia.</p>
        </div>
        <FooterCol title="Work" items={['Workshops','Consulting','Advisory','Case studies']} />
        <FooterCol title="Company" items={['About','Practitioners','Writing','Careers']} />
        <FooterCol title="Contact" items={['hello@omniscientai.io','LinkedIn','GitHub','+61 3 xxxx xxxx']} />
      </div>
      <div style={{maxWidth:1240, margin:'32px auto 0', paddingTop:24, borderTop:'1px solid var(--line)', display:'flex', justifyContent:'space-between', alignItems:'center', fontFamily:'var(--font-mono)', fontSize:12, color:'var(--ink-400)'}}>
        <span>© 2026 Omniscient AI Pty Ltd</span>
        <span>INTELLIGENCE // CONNECTIVITY // INNOVATION</span>
      </div>
    </footer>
  );
}
function FooterCol({title, items}) {
  return (
    <div>
      <div style={{fontFamily:'var(--font-text)', fontSize:12, fontWeight:600, letterSpacing:'0.14em', textTransform:'uppercase', color:'var(--ink-400)', marginBottom:16}}>{title}</div>
      <ul style={{listStyle:'none', padding:0, margin:0, display:'flex', flexDirection:'column', gap:10}}>
        {items.map(i => <li key={i} style={{fontSize:14, color:'var(--ink)'}}>{i}</li>)}
      </ul>
    </div>
  );
}
window.Footer = Footer;
