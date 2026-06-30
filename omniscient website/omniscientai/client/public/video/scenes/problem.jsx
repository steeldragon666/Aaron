// Scene 2 — The Problem (8–24s)
// SMEs buried in tools. Browser tabs stacking up, ticker of breakages,
// payoff: "The gap isn't intelligence. It's accountability."

function SceneProblem() {
  return (
    <Sprite start={8} end={24.5}>
      {/* Eyebrow label */}
      <Sprite start={8.2} end={24.4}>
        <ProblemEyebrow />
      </Sprite>

      {/* Stacking browser-tab / tool pill chaos */}
      <Sprite start={8.4} end={19}>
        <ToolClutter />
      </Sprite>

      {/* Ticker of breakages — overlays the chaos */}
      <Sprite start={10} end={19}>
        <BreakageTicker />
      </Sprite>

      {/* Payoff line — slams into frame as chaos clears */}
      <Sprite start={19.2} end={24.4}>
        <ProblemPayoff />
      </Sprite>
    </Sprite>
  );
}

function ProblemEyebrow() {
  const { localTime, duration } = useSprite();
  const intro = Easing.easeOutCubic(clamp(localTime / 0.4, 0, 1));
  const exit = clamp((localTime - (duration - 0.4)) / 0.4, 0, 1);
  const opacity = intro * (1 - exit);

  return (
    <div style={{
      position: 'absolute',
      left: 80, top: 72,
      display: 'flex', alignItems: 'center', gap: 16,
      opacity,
    }}>
      <div style={{
        width: 10, height: 10, borderRadius: 999, background: '#2F7BFF',
      }}/>
      <div style={{
        fontFamily: 'JetBrains Mono, monospace',
        fontSize: 16,
        color: '#0F1115',
        letterSpacing: '0.14em',
        textTransform: 'uppercase',
        fontWeight: 600,
      }}>
        01 / The problem
      </div>
    </div>
  );
}

const TOOLS = [
  'ChatGPT',         'Claude',           'Copilot',         'Gemini',
  'Zapier',          'Make',             'n8n',              'Notion AI',
  'Perplexity',      'Jasper',           'Midjourney',      'Runway',
  'Intercom Fin',    'HubSpot Breeze',   'Salesforce Einstein',
  'Gong',            'Otter.ai',         'Fathom',           'Grammarly',
  'Descript',        'Loom AI',          'Canva Magic',     'Adobe Firefly',
];

function ToolClutter() {
  const { localTime, duration } = useSprite();
  // Phase 1 (0–6s): stack pills in.
  // Phase 2 (6–9s): shake / dim as "broken" crosses appear.
  // Phase 3 (9–10.6s): all sweep off to bottom-right.

  const phase2Start = 6;
  const phase3Start = 9;
  const exitStart = duration - 1.2;

  return (
    <div style={{ position: 'absolute', inset: 0 }}>
      {TOOLS.map((name, i) => {
        // Deterministic pseudo-random per-tool position
        const seed = (i * 9301 + 49297) % 233280;
        const rand1 = (seed % 1000) / 1000;
        const rand2 = ((seed * 7) % 1000) / 1000;
        const rand3 = ((seed * 13) % 1000) / 1000;

        const appearAt = 0.15 + i * 0.22;
        if (localTime < appearAt) return null;

        const local = localTime - appearAt;
        const intro = Easing.easeOutBack(clamp(local / 0.3, 0, 1));

        // Scattered inside a loose band
        const baseX = 120 + rand1 * 1500;
        const baseY = 180 + rand2 * 640;

        // Phase 2 jitter / break — x in [−6, 6]
        let jitterX = 0, jitterY = 0, broken = false, rot = 0;
        if (localTime > phase2Start) {
          const jt = (localTime - phase2Start) * 8;
          jitterX = Math.sin(jt + i) * 4;
          jitterY = Math.cos(jt * 1.3 + i) * 4;
          broken = rand3 > 0.45; // most get marked broken
          rot = (rand3 - 0.5) * 8;
        }

        // Phase 3 — fly out to lower-right
        let exitDX = 0, exitDY = 0, exitOp = 1;
        if (localTime > phase3Start) {
          const t = Easing.easeInCubic(clamp((localTime - phase3Start) / 1.6, 0, 1));
          exitDX = t * (2200 - baseX + rand1 * 400);
          exitDY = t * (1400 - baseY + rand2 * 300);
          exitOp = 1 - t;
        }
        if (localTime > exitStart) {
          exitOp *= 1 - clamp((localTime - exitStart) / 1.2, 0, 1);
        }

        const x = baseX + jitterX + exitDX;
        const y = baseY + jitterY + exitDY;

        return (
          <div key={name} style={{
            position: 'absolute',
            left: x, top: y,
            transform: `scale(${intro}) rotate(${rot}deg)`,
            transformOrigin: 'center',
            opacity: exitOp * intro,
            padding: '10px 18px',
            background: broken ? '#FCE7E7' : '#FFFFFF',
            border: `1px solid ${broken ? '#D94B4B' : '#E4E7EC'}`,
            borderRadius: 999,
            fontFamily: 'Inter, sans-serif',
            fontSize: 16,
            fontWeight: 500,
            color: broken ? '#D94B4B' : '#2A2F37',
            boxShadow: '0 1px 2px rgb(15 17 21 / 0.06)',
            display: 'flex', alignItems: 'center', gap: 10,
            whiteSpace: 'nowrap',
            textDecoration: broken ? 'line-through' : 'none',
            textDecorationColor: '#D94B4B',
            willChange: 'transform, opacity',
          }}>
            <div style={{
              width: 8, height: 8, borderRadius: 2,
              background: broken ? '#D94B4B' : '#0F1115',
            }}/>
            {name}
          </div>
        );
      })}
    </div>
  );
}

const BREAKAGES = [
  'Zapier flow broke again',
  '3 ChatGPT tabs open',
  'Copilot subscription — who owns this?',
  'Prompt library v4_FINAL_final.docx',
  'Someone paid for Jasper?',
  'Claude Project — where did the PDFs go',
  'Agent built 6 months ago, nobody touched since',
  'Marketing ops spent Friday debugging Make',
];

function BreakageTicker() {
  const { localTime } = useSprite();
  // Only the 3 most recent breakages visible, sliding up
  const perRow = 2.1;
  const rows = BREAKAGES.slice(0, Math.floor(localTime / perRow) + 1);
  const recent = rows.slice(-3);

  return (
    <div style={{
      position: 'absolute',
      left: 80, bottom: 120,
      width: 560,
      display: 'flex', flexDirection: 'column-reverse', gap: 8,
    }}>
      {recent.map((msg, idx) => {
        const age = localTime - (rows.length - recent.length + idx) * perRow;
        const introT = Easing.easeOutCubic(clamp(age / 0.4, 0, 1));
        const opacity = Math.max(0, 1 - (recent.length - 1 - idx) * 0.35) * introT;
        return (
          <div key={msg + idx} style={{
            background: '#0F1115',
            color: '#FFFFFF',
            padding: '10px 14px',
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: 14,
            borderRadius: 6,
            display: 'flex', alignItems: 'center', gap: 10,
            opacity,
            transform: `translateY(${(1 - introT) * 12}px)`,
          }}>
            <span style={{ color: '#D94B4B' }}>✕</span>
            {msg}
          </div>
        );
      })}
    </div>
  );
}

function ProblemPayoff() {
  const { localTime, duration } = useSprite();
  const intro = Easing.easeOutCubic(clamp(localTime / 0.6, 0, 1));
  const exit = clamp((localTime - (duration - 0.5)) / 0.5, 0, 1);
  const opacity = intro * (1 - exit);

  // Reveal second half with short delay
  const secondReveal = Easing.easeOutCubic(clamp((localTime - 1.6) / 0.6, 0, 1));

  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      gap: 20,
      opacity,
    }}>
      <div style={{
        fontFamily: 'Inter, sans-serif',
        fontWeight: 700,
        fontSize: 96,
        letterSpacing: '-0.03em',
        lineHeight: 1,
        color: '#0F1115',
        textAlign: 'center',
        transform: `translateY(${(1 - intro) * 20}px)`,
      }}>
        The gap isn't intelligence.
      </div>
      <div style={{
        fontFamily: 'Inter, sans-serif',
        fontWeight: 800,
        fontSize: 120,
        letterSpacing: '-0.035em',
        lineHeight: 1,
        color: '#2F7BFF',
        textAlign: 'center',
        opacity: secondReveal,
        transform: `translateY(${(1 - secondReveal) * 24}px)`,
      }}>
        It's accountability.
      </div>
    </div>
  );
}

Object.assign(window, { SceneProblem });
