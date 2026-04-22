function Pillars() {
  const pillars = [
    {tag:'01', name:'Health technology', body:'We build ML tooling for clinicians and researchers — diagnostic aids, imaging pipelines, and decision support.'},
    {tag:'02', name:'Defense hardware & software', body:'Ruggedised perception stacks and dual-use ML systems for partners in national defense.'},
    {tag:'03', name:'Agentic marketing & ops', body:'Agents that reduce toil in go-to-market and operations — scoped to one measurable outcome.'}
  ];
  return (
    <section id="consulting" style={{padding:'64px 40px', maxWidth:1240, margin:'0 auto'}}>
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'flex-end', marginBottom:40, gap:40, flexWrap:'wrap'}}>
        <h2 style={{fontSize:48, fontWeight:700, letterSpacing:'-0.025em', margin:0, color:'var(--ink)', maxWidth:560, lineHeight:1.05}}>Three practice areas. One research-grade bar.</h2>
        <p style={{fontSize:16, color:'var(--ink-600)', maxWidth:360, margin:0}}>The work spans industries but the standard doesn't. Every engagement ships evaluatable output.</p>
      </div>
      <div style={{display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:24}}>
        {pillars.map(p => (
          <div key={p.tag} style={{border:'1px solid var(--line)', borderRadius:8, padding:28, background:'var(--paper)'}}>
            <div style={{fontFamily:'var(--font-mono)', fontSize:13, color:'var(--blue-deep)', marginBottom:20}}>{p.tag}</div>
            <h3 style={{fontSize:22, fontWeight:700, margin:'0 0 10px', color:'var(--ink)'}}>{p.name}</h3>
            <p style={{fontSize:15, lineHeight:1.55, color:'var(--ink-600)', margin:0}}>{p.body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
window.Pillars = Pillars;
