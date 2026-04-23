// Scene 3 — Turn (24–32s)
// "You don't need another tool to prompt."
// "You need someone to take the work off your plate."

function SceneTurn() {
  return (
    <Sprite start={24.5} end={32.5}>
      <Sprite start={24.7} end={28.6}>
        <TurnLineA />
      </Sprite>
      <Sprite start={28.6} end={32.4}>
        <TurnLineB />
      </Sprite>
    </Sprite>
  );
}

function TurnLineA() {
  const { localTime, duration } = useSprite();
  const intro = Easing.easeOutCubic(clamp(localTime / 0.5, 0, 1));
  const exit = clamp((localTime - (duration - 0.5)) / 0.5, 0, 1);
  const opacity = intro * (1 - exit);

  // Strike-through on "another tool to prompt"
  const strikeT = Easing.easeOutCubic(clamp((localTime - 1.4) / 0.6, 0, 1));

  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      opacity,
    }}>
      <div style={{
        fontFamily: 'Inter, sans-serif',
        fontWeight: 700,
        fontSize: 88,
        letterSpacing: '-0.03em',
        lineHeight: 1.05,
        color: '#0F1115',
        textAlign: 'center',
        maxWidth: 1600,
        transform: `translateY(${(1 - intro) * 16}px)`,
      }}>
        You don't need{' '}
        <span style={{ position: 'relative', display: 'inline-block' }}>
          another tool to prompt.
          <span style={{
            position: 'absolute',
            left: 0, right: 0, top: '52%',
            height: 6,
            background: '#D94B4B',
            transform: `scaleX(${strikeT})`,
            transformOrigin: 'left',
          }}/>
        </span>
      </div>
    </div>
  );
}

function TurnLineB() {
  const { localTime, duration } = useSprite();
  const intro = Easing.easeOutCubic(clamp(localTime / 0.5, 0, 1));
  const exit = clamp((localTime - (duration - 0.5)) / 0.5, 0, 1);
  const opacity = intro * (1 - exit);

  // Second phrase reveal
  const part2 = Easing.easeOutCubic(clamp((localTime - 1.1) / 0.6, 0, 1));

  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      gap: 18,
      opacity,
    }}>
      <div style={{
        fontFamily: 'Inter, sans-serif',
        fontWeight: 700,
        fontSize: 88,
        letterSpacing: '-0.03em',
        lineHeight: 1.05,
        color: '#0F1115',
        textAlign: 'center',
        transform: `translateY(${(1 - intro) * 16}px)`,
      }}>
        You need someone to
      </div>
      <div style={{
        fontFamily: 'Inter, sans-serif',
        fontWeight: 800,
        fontSize: 124,
        letterSpacing: '-0.035em',
        lineHeight: 1,
        color: '#2F7BFF',
        textAlign: 'center',
        opacity: part2,
        transform: `translateY(${(1 - part2) * 24}px)`,
      }}>
        deliver the outcome.
      </div>
    </div>
  );
}

Object.assign(window, { SceneTurn });
