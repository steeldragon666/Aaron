// Scene 4 — Thesis "What We Do" (32–40s)
// Brand graphic assembles on the right. Thesis line on the left.
// "We deploy and manage a fleet of AI agents."

function SceneThesis() {
  return (
    <Sprite start={32.5} end={40.2}>
      {/* Background flips to ink */}
      <Sprite start={32.5} end={108}>
        <InkBackground />
      </Sprite>

      {/* Section eyebrow */}
      <Sprite start={32.7} end={40.1}>
        <SectionEyebrow label="02 / What we do" />
      </Sprite>

      {/* Thesis text */}
      <Sprite start={33.2} end={40.1}>
        <ThesisText />
      </Sprite>

      {/* Brand graphic assembles in right half — persists through pillars */}
      <Sprite start={33.0} end={108}>
        <BrandGraphicAmbient />
      </Sprite>
    </Sprite>
  );
}

// Shared: flip canvas to ink during pillars block
function InkBackground() {
  const { localTime, duration } = useSprite();
  const intro = Easing.easeOutCubic(clamp(localTime / 0.5, 0, 1));
  const exit = clamp((localTime - (duration - 0.8)) / 0.8, 0, 1);
  const opacity = intro * (1 - exit);
  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      background: '#0F1115',
      opacity,
    }}/>
  );
}

function SectionEyebrow({ label }) {
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
        color: '#FFFFFF',
        letterSpacing: '0.14em',
        textTransform: 'uppercase',
        fontWeight: 600,
      }}>
        {label}
      </div>
    </div>
  );
}

function ThesisText() {
  const { localTime, duration } = useSprite();
  const intro = Easing.easeOutCubic(clamp(localTime / 0.6, 0, 1));
  const exit = clamp((localTime - (duration - 0.5)) / 0.5, 0, 1);
  const opacity = intro * (1 - exit);

  const secondLine = Easing.easeOutCubic(clamp((localTime - 1.0) / 0.6, 0, 1));
  const thirdLine = Easing.easeOutCubic(clamp((localTime - 2.0) / 0.6, 0, 1));

  return (
    <div style={{
      position: 'absolute',
      left: 80, top: 360,
      width: 880,
      opacity,
    }}>
      <div style={{
        fontFamily: 'Inter, sans-serif',
        fontWeight: 500,
        fontSize: 26,
        color: '#7AA8FF',
        letterSpacing: '-0.01em',
        marginBottom: 16,
        transform: `translateY(${(1 - intro) * 12}px)`,
      }}>
        We don't sell you software.
      </div>
      <div style={{
        fontFamily: 'Inter, sans-serif',
        fontWeight: 800,
        fontSize: 84,
        letterSpacing: '-0.03em',
        lineHeight: 1,
        color: '#FFFFFF',
      }}>
        <div style={{
          opacity: intro,
          transform: `translateY(${(1 - intro) * 20}px)`,
        }}>
          We deploy and manage
        </div>
        <div style={{
          opacity: secondLine,
          transform: `translateY(${(1 - secondLine) * 20}px)`,
          marginTop: 8,
        }}>
          a <span style={{ color: '#2F7BFF' }}>fleet of AI agents</span>
        </div>
        <div style={{
          opacity: thirdLine,
          transform: `translateY(${(1 - thirdLine) * 20}px)`,
          marginTop: 8,
          fontSize: 64,
          fontWeight: 700,
          color: '#BEC3CC',
          letterSpacing: '-0.02em',
        }}>
          that run your business.
        </div>
      </div>
    </div>
  );
}

// Brand graphic sits in the right half of frame during pillars.
// Assembles on thesis, then persists, repositions subtly for each pillar.
function BrandGraphicAmbient() {
  const { time } = useTimeline();
  const { localTime } = useSprite();

  // Entry animation (first ~1.5s)
  const intro = Easing.easeOutCubic(clamp(localTime / 1.5, 0, 1));
  // Gentle breathing scale
  const breath = 1 + Math.sin(time * 0.6) * 0.008;

  // Slow drift based on which pillar is active (time-based)
  // Thesis 32.5-40.2, Admin 40-64, MarketSales 64-88, Finance 88-108
  let targetX = 1020, targetY = 140;
  if (time > 40) { targetX = 1080; targetY = 160; }
  if (time > 64) { targetX = 1060; targetY = 180; }
  if (time > 88) { targetX = 1100; targetY = 140; }

  return (
    <div style={{
      position: 'absolute',
      left: targetX, top: targetY,
      width: 820, height: 820,
      opacity: intro,
      transform: `scale(${0.88 + 0.12 * intro}) scale(${breath})`,
      transformOrigin: 'center',
      transition: 'left 1.5s cubic-bezier(0.2,0.9,0.2,1), top 1.5s cubic-bezier(0.2,0.9,0.2,1)',
      willChange: 'transform, opacity',
    }}>
      <img
        src="assets/brand-graphic-circles.png"
        alt=""
        style={{
          width: '100%', height: '100%', objectFit: 'contain',
          filter: 'drop-shadow(0 40px 80px rgba(47, 123, 255, 0.18))',
        }}
      />
      {/* Pulse nodes overlay */}
      <PulseNodes />
    </div>
  );
}

function PulseNodes() {
  const { time } = useTimeline();
  // A few blue pulse nodes placed around the graphic
  const nodes = [
    { x: 12, y: 28, delay: 0 },
    { x: 72, y: 18, delay: 0.7 },
    { x: 86, y: 62, delay: 1.3 },
    { x: 38, y: 78, delay: 2.0 },
    { x: 58, y: 44, delay: 2.7 },
  ];
  return (
    <>
      {nodes.map((n, i) => {
        const phase = ((time + n.delay) % 2.4) / 2.4;
        const opacity = Math.max(0, 1 - phase);
        const scale = 1 + phase * 3.5;
        return (
          <div key={i} style={{
            position: 'absolute',
            left: `${n.x}%`, top: `${n.y}%`,
            width: 18, height: 18,
            marginLeft: -9, marginTop: -9,
            borderRadius: 999,
            background: 'radial-gradient(circle, rgba(122,168,255,0.7) 0%, rgba(47,123,255,0) 70%)',
            transform: `scale(${scale})`,
            opacity,
            pointerEvents: 'none',
          }}/>
        );
      })}
    </>
  );
}

Object.assign(window, { SceneThesis, InkBackground, SectionEyebrow, BrandGraphicAmbient });
