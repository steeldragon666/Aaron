// Scenes 8–9 — Manifesto + CTA (108–120s)

function SceneManifesto() {
  return (
    <Sprite start={108} end={116}>
      {/* Paper background return */}
      <Sprite start={108} end={116}>
        <PaperFlip />
      </Sprite>

      <Sprite start={108.3} end={115.8}>
        <ManifestoText />
      </Sprite>
    </Sprite>
  );
}

function PaperFlip() {
  const { localTime, duration } = useSprite();
  const intro = Easing.easeOutCubic(clamp(localTime / 0.5, 0, 1));
  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      background: '#FFFFFF',
      opacity: intro,
    }}/>
  );
}

function ManifestoText() {
  const { localTime, duration } = useSprite();
  const exit = clamp((localTime - (duration - 0.6)) / 0.6, 0, 1);

  // Three words reveal sequentially, then the slashes pop
  const w1 = Easing.easeOutCubic(clamp(localTime / 0.5, 0, 1));
  const s1 = Easing.easeOutCubic(clamp((localTime - 0.6) / 0.3, 0, 1));
  const w2 = Easing.easeOutCubic(clamp((localTime - 0.9) / 0.5, 0, 1));
  const s2 = Easing.easeOutCubic(clamp((localTime - 1.5) / 0.3, 0, 1));
  const w3 = Easing.easeOutCubic(clamp((localTime - 1.8) / 0.5, 0, 1));

  // Hold all fully visible from ~2.4s to exit
  const holdOpacity = 1 - exit;

  const wordStyle = {
    fontFamily: 'Inter, sans-serif',
    fontWeight: 800,
    fontSize: 96,
    letterSpacing: '0.02em',
    color: '#0F1115',
    textTransform: 'uppercase',
  };
  const slashStyle = {
    fontFamily: 'Inter, sans-serif',
    fontWeight: 800,
    fontSize: 96,
    color: '#2F7BFF',
    margin: '0 28px',
  };

  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      gap: 36,
      opacity: holdOpacity,
    }}>
      {/* Top rule */}
      <div style={{
        width: 120, height: 2, background: '#0F1115',
        opacity: Easing.easeOutCubic(clamp((localTime - 0.2) / 0.4, 0, 1)),
      }}/>

      <div style={{ display: 'flex', alignItems: 'center' }}>
        <span style={{
          ...wordStyle,
          opacity: w1,
          transform: `translateY(${(1 - w1) * 20}px)`,
        }}>Intelligence</span>
        <span style={{
          ...slashStyle,
          opacity: s1,
          transform: `scale(${0.6 + 0.4 * s1})`,
        }}>//</span>
        <span style={{
          ...wordStyle,
          opacity: w2,
          transform: `translateY(${(1 - w2) * 20}px)`,
        }}>Connectivity</span>
        <span style={{
          ...slashStyle,
          opacity: s2,
          transform: `scale(${0.6 + 0.4 * s2})`,
        }}>//</span>
        <span style={{
          ...wordStyle,
          opacity: w3,
          transform: `translateY(${(1 - w3) * 20}px)`,
        }}>Innovation</span>
      </div>

      {/* Bottom rule */}
      <div style={{
        width: 120, height: 2, background: '#0F1115',
        opacity: Easing.easeOutCubic(clamp((localTime - 2.2) / 0.4, 0, 1)),
      }}/>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────
// Scene 9 — CTA

function SceneCTA({ variant }) {
  // variant: 'owners' or 'operators'
  const tagline = variant === 'operators'
    ? 'Stop prompting. Start reclaiming hours.'
    : 'Stop prompting. Start profiting.';
  const subline = variant === 'operators'
    ? 'Book a 20-minute call — we\'ll map the hours back to your team.'
    : 'Book a 20-minute call — we\'ll map the margin back to your P&L.';

  return (
    <Sprite start={116} end={120}>
      <CTACard tagline={tagline} subline={subline} />
    </Sprite>
  );
}

function CTACard({ tagline, subline }) {
  const { localTime, duration } = useSprite();
  const intro = Easing.easeOutCubic(clamp(localTime / 0.7, 0, 1));
  const exit = clamp((localTime - (duration - 0.4)) / 0.4, 0, 1);
  const opacity = (1 - exit);

  // Split tagline into two sentences for styling
  const parts = tagline.split('. ').map((p, i, arr) => p + (i < arr.length - 1 ? '.' : ''));
  const [firstHalf, secondHalf] = parts.length === 2 ? parts : [tagline, ''];

  // Reveal staging
  const first = Easing.easeOutCubic(clamp(localTime / 0.6, 0, 1));
  const second = Easing.easeOutCubic(clamp((localTime - 0.8) / 0.6, 0, 1));
  const logoIn = Easing.easeOutCubic(clamp((localTime - 1.6) / 0.6, 0, 1));

  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      background: '#0F1115',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      opacity,
    }}>
      {/* Brand graphic corner */}
      <div style={{
        position: 'absolute',
        right: -100, top: -100,
        width: 620, height: 620,
        opacity: intro * 0.55,
      }}>
        <img
          src="assets/brand-graphic-circles.png"
          alt=""
          style={{ width: '100%', height: '100%', objectFit: 'contain' }}
        />
      </div>
      <div style={{
        position: 'absolute',
        left: -80, bottom: -120,
        width: 480, height: 480,
        opacity: intro * 0.35,
        transform: 'rotate(180deg)',
      }}>
        <img
          src="assets/brand-graphic-circles.png"
          alt=""
          style={{ width: '100%', height: '100%', objectFit: 'contain' }}
        />
      </div>

      {/* Main tagline */}
      <div style={{
        position: 'relative',
        zIndex: 2,
        textAlign: 'center',
        fontFamily: 'Inter, sans-serif',
        maxWidth: 1400,
      }}>
        <div style={{
          fontSize: 96,
          fontWeight: 800,
          letterSpacing: '-0.035em',
          lineHeight: 1,
          color: '#FFFFFF',
          opacity: first,
          transform: `translateY(${(1 - first) * 16}px)`,
        }}>
          {firstHalf}
        </div>
        <div style={{
          fontSize: 96,
          fontWeight: 800,
          letterSpacing: '-0.035em',
          lineHeight: 1,
          color: '#2F7BFF',
          marginTop: 16,
          opacity: second,
          transform: `translateY(${(1 - second) * 24}px)`,
        }}>
          {secondHalf}
        </div>

        <div style={{
          fontSize: 22,
          fontWeight: 400,
          lineHeight: 1.4,
          color: '#BEC3CC',
          marginTop: 48,
          opacity: logoIn,
        }}>
          {subline}
        </div>

        {/* Logo row */}
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          gap: 14,
          marginTop: 48,
          opacity: logoIn,
          transform: `translateY(${(1 - logoIn) * 8}px)`,
        }}>
          <div style={{
            width: 36, height: 36, borderRadius: 999, background: '#FFFFFF',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <div style={{
              width: 14, height: 14, borderRadius: 999, background: '#0F1115',
            }}/>
          </div>
          <div style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 28,
            fontWeight: 700,
            color: '#FFFFFF',
            letterSpacing: '-0.02em',
          }}>
            Omniscient AI
          </div>
          <div style={{
            marginLeft: 20,
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: 14,
            color: '#7AA8FF',
            letterSpacing: '0.14em',
            textTransform: 'uppercase',
          }}>
            omniscientai.io →
          </div>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { SceneManifesto, SceneCTA });
