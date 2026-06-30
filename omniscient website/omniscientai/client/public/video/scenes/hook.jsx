// Scene 1 — Hook (0–8s)
// "AI promised 10× productivity." → "You got a chatbot that hallucinates."

function SceneHook() {
  return (
    <Sprite start={0} end={8.2}>
      {/* Line 1 — punch in */}
      <Sprite start={0.4} end={4.2}>
        <HookLine1 />
      </Sprite>

      {/* Line 2 — typed deadpan follow-up */}
      <Sprite start={4.2} end={8.2}>
        <HookLine2 />
      </Sprite>

      {/* Subtle ambient cursor caret blinking */}
      <Sprite start={0} end={8.2}>
        <HookCaret />
      </Sprite>
    </Sprite>
  );
}

function HookLine1() {
  const { localTime, duration } = useSprite();
  const exitStart = duration - 0.5;

  // Scale-in + very slight letter-spacing tighten
  const intro = Easing.easeOutCubic(clamp(localTime / 0.5, 0, 1));
  let opacity = intro;
  let scale = 0.96 + 0.04 * intro;

  if (localTime > exitStart) {
    const t = clamp((localTime - exitStart) / 0.5, 0, 1);
    opacity = 1 - t;
    scale = 1 - 0.02 * t;
  }

  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      opacity,
      transform: `scale(${scale})`,
      willChange: 'transform, opacity',
    }}>
      <div style={{
        fontFamily: 'Inter, sans-serif',
        fontWeight: 800,
        fontSize: 128,
        letterSpacing: '-0.035em',
        color: '#0F1115',
        lineHeight: 0.95,
        textAlign: 'center',
      }}>
        AI promised <span style={{ color: '#2F7BFF' }}>10×</span> productivity.
      </div>
    </div>
  );
}

function HookLine2() {
  const { localTime, duration } = useSprite();
  const exitStart = duration - 0.4;

  // Typewriter reveal of the follow-up
  const chars = 'You got a chatbot that hallucinates.';
  const revealDur = 1.4;
  const revealProgress = clamp(localTime / revealDur, 0, 1);
  const visibleCount = Math.floor(Easing.easeOutCubic(revealProgress) * chars.length);
  const shown = chars.slice(0, visibleCount);

  let opacity = 1;
  if (localTime > exitStart) {
    opacity = 1 - clamp((localTime - exitStart) / 0.4, 0, 1);
  }

  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      opacity,
    }}>
      <div style={{
        fontFamily: 'Inter, sans-serif',
        fontWeight: 700,
        fontSize: 84,
        letterSpacing: '-0.03em',
        color: '#0F1115',
        lineHeight: 1.05,
        textAlign: 'center',
        maxWidth: 1500,
      }}>
        <span>{shown}</span>
        {visibleCount < chars.length && (
          <span style={{
            display: 'inline-block',
            width: '0.05em',
            height: '0.9em',
            background: '#2F7BFF',
            verticalAlign: 'text-bottom',
            marginLeft: 6,
            opacity: Math.floor(localTime * 3) % 2 ? 0.2 : 1,
          }}/>
        )}
      </div>
    </div>
  );
}

function HookCaret() {
  // Small brand mark blinking in lower-left like a terminal prompt
  const { localTime } = useSprite();
  const blink = Math.floor(localTime * 2) % 2 ? 1 : 0.25;
  return (
    <div style={{
      position: 'absolute',
      left: 80, bottom: 80,
      display: 'flex', alignItems: 'center', gap: 14,
      fontFamily: 'JetBrains Mono, monospace',
      fontSize: 16,
      color: '#5B6270',
      letterSpacing: '0.14em',
      textTransform: 'uppercase',
    }}>
      <div style={{
        width: 10, height: 10, borderRadius: 999, background: '#2F7BFF', opacity: blink,
      }}/>
      OMNISCIENT AI — THE PROBLEM
    </div>
  );
}

Object.assign(window, { SceneHook });
