// Scenes 5–7 — Three practice pillars (40–108s)
// Each pillar = hero title on the left + a distinct LIVE VISUALIZATION on the right.
// The right-side viz is the star of each scene; motion is continuous, not decorative.

// ─────────────────────────────────────────────────────────────────────
// Shared chrome (eyebrow, title, stat)
// ─────────────────────────────────────────────────────────────────────

function PillarChrome({ index, title, subtitle, stat, statStart, color = '#2F7BFF' }) {
  const { localTime, duration } = useSprite();
  const intro = Easing.easeOutCubic(clamp(localTime / 0.6, 0, 1));
  const exit = clamp((localTime - (duration - 0.5)) / 0.5, 0, 1);
  const opacity = intro * (1 - exit);

  const underline = Easing.easeOutCubic(clamp((localTime - 0.5) / 0.6, 0, 1));
  const subIn = Easing.easeOutCubic(clamp((localTime - 0.9) / 0.5, 0, 1));

  return (
    <>
      {/* Eyebrow */}
      <div style={{
        position: 'absolute', left: 80, top: 130,
        fontFamily: 'JetBrains Mono, monospace',
        fontSize: 14, letterSpacing: '0.16em', textTransform: 'uppercase',
        color: '#7AA8FF', fontWeight: 600,
        opacity,
      }}>Pillar {index} / 03</div>

      {/* Title */}
      <div style={{
        position: 'absolute', left: 80, top: 180, width: 820,
        opacity,
      }}>
        <div style={{
          fontFamily: 'Inter, sans-serif',
          fontWeight: 800, fontSize: 84, letterSpacing: '-0.035em',
          lineHeight: 0.95, color: '#FFFFFF',
          transform: `translateY(${(1 - intro) * 20}px)`,
        }}>{title}</div>
        <div style={{
          height: 6, width: 240, background: color, marginTop: 12,
          transform: `scaleX(${underline})`, transformOrigin: 'left',
        }}/>
        <div style={{
          fontFamily: 'Inter, sans-serif',
          fontSize: 22, lineHeight: 1.4, fontWeight: 400,
          color: '#BEC3CC', marginTop: 20, maxWidth: 640,
          opacity: subIn,
        }}>{subtitle}</div>
      </div>

      {/* Stat (appears later) */}
      {localTime > statStart && (
        <PillarStat stat={stat} color={color} localOffset={localTime - statStart} />
      )}
    </>
  );
}

function PillarStat({ stat, color, localOffset }) {
  const intro = Easing.easeOutCubic(clamp(localOffset / 0.8, 0, 1));
  const count = Math.round(stat.value * Easing.easeOutCubic(clamp(localOffset / 1.4, 0, 1)));

  return (
    <div style={{
      position: 'absolute', left: 80, bottom: 90,
      display: 'flex', alignItems: 'baseline', gap: 18,
      opacity: intro,
      transform: `translateY(${(1 - intro) * 12}px)`,
    }}>
      <div style={{
        fontFamily: 'Inter, sans-serif',
        fontSize: 80, fontWeight: 800, letterSpacing: '-0.03em',
        lineHeight: 1, color, fontVariantNumeric: 'tabular-nums',
      }}>{count}{stat.suffix || ''}</div>
      <div style={{
        fontFamily: 'Inter, sans-serif',
        fontSize: 18, fontWeight: 500, color: '#BEC3CC',
        maxWidth: 380, lineHeight: 1.3,
      }}>{stat.label}</div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// PILLAR 01 — ADMIN & OPS
// Right side: a live "agent fleet" dashboard — parallel agent lanes
// processing emails / calendar / docs / meetings with progress bars,
// real-time activity ticker, and an animated hours-reclaimed dial.
// ─────────────────────────────────────────────────────────────────────

function ScenePillarAdmin() {
  const start = 40.2, end = 64;
  return (
    <Sprite start={start} end={end}>
      <PillarChrome
        index="01"
        title="Admin & Operations"
        subtitle="The 30+ hours a week your team loses before lunch on Monday."
        stat={{ value: 30, suffix: '+ hrs', label: 'reclaimed per team, per week' }}
        statStart={16}
        color="#2F7BFF"
      />
      <AdminDashboard />
    </Sprite>
  );
}

const ADMIN_AGENTS = [
  { name: 'Inbox triage',       tasks: ['Draft reply: Jamie (RFP)', 'Flag: Contract renewal', 'Archive: 14 newsletters', 'Reply: Scheduling request', 'Reply: Vendor invoice', 'Flag: Client escalation'] },
  { name: 'Calendar',            tasks: ['Reschedule: Tues standup', 'Brief: 3pm pitch (Acme)', 'Hold: Fri 2hr focus block', 'Reply: Booking — Monday OK', 'Prep notes: 4pm review'] },
  { name: 'Documents',           tasks: ['File: Q3 contracts/', 'Rename: proposal_v4_FINAL', 'Version: SOW-Acme-0421', 'Archive: 2024/Deprecated', 'Merge: 3 duplicate PDFs'] },
  { name: 'Meeting notes',       tasks: ['Summarise: Board sync', 'Actions → Asana (4)', 'Distribute: Weekly ops', 'Summarise: Vendor call', 'Actions → Linear (2)'] },
  { name: 'Data entry',          tasks: ['CRM: 12 new leads', 'Timesheets: pay period 8', 'Sync: Pipedrive ↔ Sheets', 'Enrich: 24 contacts', 'Tag: inbound/outbound'] },
  { name: 'Internal reporting',  tasks: ['Compile: Ops digest W17', 'Chart: 7-day throughput', 'Send: Monday brief', 'Flag: 2 SLA near-miss'] },
];

function AdminDashboard() {
  const { localTime } = useSprite();
  const introAll = Easing.easeOutCubic(clamp((localTime - 0.6) / 0.8, 0, 1));

  return (
    <div style={{
      position: 'absolute',
      right: 60, top: 130,
      width: 920, height: 820,
      opacity: introAll,
      transform: `translateY(${(1 - introAll) * 16}px)`,
    }}>
      {/* Dashboard window chrome */}
      <div style={{
        background: 'rgba(255,255,255,0.03)',
        border: '1px solid rgba(255,255,255,0.12)',
        borderRadius: 10,
        padding: 18,
        height: '100%',
        display: 'flex', flexDirection: 'column',
        backdropFilter: 'blur(2px)',
      }}>
        {/* Header bar */}
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          marginBottom: 16,
          paddingBottom: 14,
          borderBottom: '1px solid rgba(255,255,255,0.08)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <StatusDot />
            <div style={{
              fontFamily: 'Inter, sans-serif', fontSize: 14, fontWeight: 600,
              color: '#FFFFFF', letterSpacing: '-0.01em',
            }}>Agent Fleet · Live</div>
          </div>
          <div style={{
            fontFamily: 'JetBrains Mono, monospace', fontSize: 12,
            color: '#7AA8FF', letterSpacing: '0.1em',
          }}>
            {ADMIN_AGENTS.length} AGENTS · {Math.floor(localTime * 3 + 142)} TASKS TODAY
          </div>
        </div>

        {/* Agent lanes */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 10 }}>
          {ADMIN_AGENTS.map((agent, i) => (
            <AgentLane key={agent.name} agent={agent} index={i} appearAt={0.2 + i * 0.25} />
          ))}
        </div>
      </div>
    </div>
  );
}

function StatusDot() {
  const { time } = useTimeline();
  const phase = (time * 2) % 2;
  const opacity = phase < 1 ? 1 : 0.3;
  return (
    <div style={{
      width: 10, height: 10, borderRadius: 999, background: '#1EA97C',
      boxShadow: `0 0 ${8 * opacity}px #1EA97C`,
      opacity,
    }}/>
  );
}

function AgentLane({ agent, index, appearAt }) {
  const { localTime } = useSprite();
  if (localTime < appearAt) return null;

  const local = localTime - appearAt;
  const appear = Easing.easeOutCubic(clamp(local / 0.35, 0, 1));

  // Cycle through this agent's tasks
  const taskDur = 2.4;
  const jitter = (index * 0.13) % taskDur;
  const cycleT = (local + jitter) % taskDur;
  const taskIdx = Math.floor((local + jitter) / taskDur) % agent.tasks.length;
  const prevIdx = (taskIdx - 1 + agent.tasks.length) % agent.tasks.length;

  const progress = cycleT / taskDur; // 0..1 progress bar
  const swapT = Math.min(1, cycleT / 0.4); // transition between tasks

  const currentTask = agent.tasks[taskIdx];
  const prevTask = agent.tasks[prevIdx];

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: '160px 1fr 80px',
      alignItems: 'center',
      gap: 14,
      padding: '10px 14px',
      background: 'rgba(47, 123, 255, 0.05)',
      border: '1px solid rgba(47, 123, 255, 0.18)',
      borderRadius: 6,
      opacity: appear,
      transform: `translateX(${(1 - appear) * 12}px)`,
    }}>
      {/* Agent name */}
      <div style={{
        fontFamily: 'Inter, sans-serif', fontSize: 13, fontWeight: 600,
        color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: 8,
      }}>
        <SpinnerRing />
        {agent.name}
      </div>

      {/* Current task + progress */}
      <div style={{ position: 'relative' }}>
        <div style={{
          fontFamily: 'JetBrains Mono, monospace', fontSize: 12,
          color: '#BEC3CC', marginBottom: 6,
          height: 14, overflow: 'hidden', position: 'relative',
        }}>
          {/* Previous task sliding out up */}
          <div style={{
            position: 'absolute', left: 0, top: 0, right: 0,
            opacity: 1 - swapT,
            transform: `translateY(${-swapT * 14}px)`,
          }}>{prevTask}</div>
          {/* Current task sliding in up */}
          <div style={{
            position: 'absolute', left: 0, top: 0, right: 0,
            opacity: swapT,
            transform: `translateY(${(1 - swapT) * 14}px)`,
            color: '#FFFFFF',
          }}>{currentTask}</div>
        </div>
        {/* Progress bar */}
        <div style={{
          height: 4, background: 'rgba(255,255,255,0.08)', borderRadius: 2,
          position: 'relative', overflow: 'hidden',
        }}>
          <div style={{
            position: 'absolute', left: 0, top: 0, bottom: 0,
            width: `${progress * 100}%`,
            background: '#2F7BFF',
            transition: progress < 0.05 ? 'none' : 'width 40ms linear',
          }}/>
          {/* Shimmer */}
          <div style={{
            position: 'absolute', left: `${progress * 100 - 10}%`, top: 0, bottom: 0,
            width: 40,
            background: 'linear-gradient(90deg, transparent, rgba(122,168,255,0.9), transparent)',
            filter: 'blur(2px)',
          }}/>
        </div>
      </div>

      {/* Status chip */}
      <div style={{
        fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
        letterSpacing: '0.1em', textTransform: 'uppercase',
        color: '#7AA8FF', textAlign: 'right',
        fontVariantNumeric: 'tabular-nums',
      }}>
        {Math.round(progress * 100)}%
      </div>
    </div>
  );
}

function SpinnerRing() {
  const { time } = useTimeline();
  const rot = (time * 240) % 360;
  return (
    <svg width="12" height="12" viewBox="0 0 12 12" style={{ transform: `rotate(${rot}deg)` }}>
      <circle cx="6" cy="6" r="4.5" fill="none" stroke="rgba(47,123,255,0.25)" strokeWidth="1.5"/>
      <path d="M 6 1.5 A 4.5 4.5 0 0 1 10.5 6" fill="none" stroke="#2F7BFF" strokeWidth="1.5" strokeLinecap="round"/>
    </svg>
  );
}

// ─────────────────────────────────────────────────────────────────────
// PILLAR 02 — MARKETING & SALES
// Right side: a live CRM pipeline — cards flow through New → Qualified
// → Replied → Meeting. Plus an active "draft post" panel with typing.
// ─────────────────────────────────────────────────────────────────────

function ScenePillarMarketing() {
  const start = 64, end = 88;
  return (
    <Sprite start={start} end={end}>
      <PillarChrome
        index="02"
        title="Marketing & Sales"
        subtitle="Consistent outbound without hiring a marketing coordinator."
        stat={{ value: 1, suffix: '', label: 'fleet replaces a full marketing coordinator' }}
        statStart={16}
        color="#2F7BFF"
      />
      <CRMPipeline />
    </Sprite>
  );
}

const PIPELINE_COLUMNS = [
  { id: 'new',       title: 'New',       accent: '#5B6270' },
  { id: 'qualified', title: 'Qualified', accent: '#7AA8FF' },
  { id: 'replied',   title: 'Replied',   accent: '#2F7BFF' },
  { id: 'meeting',   title: 'Meeting',   accent: '#1EA97C' },
];

const LEADS = [
  { name: 'Jamie C.',   company: 'Northwind Logistics', avatar: 'JC', seed: 0,  offset: 0.0  },
  { name: 'Priya S.',   company: 'Acme Industrial',     avatar: 'PS', seed: 3,  offset: 1.0  },
  { name: 'Tom W.',     company: 'Loomis & Co.',        avatar: 'TW', seed: 6,  offset: 2.2  },
  { name: 'Aisha K.',   company: 'Blue Ridge Health',   avatar: 'AK', seed: 9,  offset: 3.4  },
  { name: 'Marco R.',   company: 'Pacific Freight',     avatar: 'MR', seed: 12, offset: 4.6  },
  { name: 'Lena V.',    company: 'Vale & Daughter',     avatar: 'LV', seed: 15, offset: 5.8  },
  { name: 'Sam O.',     company: 'Orbit Manufacturing', avatar: 'SO', seed: 18, offset: 7.0  },
  { name: 'Kira M.',    company: 'Hinterland Grocers',  avatar: 'KM', seed: 21, offset: 8.2  },
  { name: 'Ben H.',     company: 'Relay Couriers',      avatar: 'BH', seed: 24, offset: 9.4  },
  { name: 'Nadia P.',   company: 'South Dock Studios',  avatar: 'NP', seed: 27, offset: 10.6 },
];

function CRMPipeline() {
  const { localTime } = useSprite();
  const introAll = Easing.easeOutCubic(clamp((localTime - 0.6) / 0.8, 0, 1));

  return (
    <div style={{
      position: 'absolute',
      right: 60, top: 130,
      width: 920, height: 820,
      opacity: introAll,
      display: 'flex', flexDirection: 'column', gap: 14,
    }}>
      {/* Pipeline board */}
      <div style={{
        background: 'rgba(255,255,255,0.03)',
        border: '1px solid rgba(255,255,255,0.12)',
        borderRadius: 10,
        padding: 16,
        flex: '0 0 auto',
      }}>
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          marginBottom: 14,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <StatusDot />
            <div style={{
              fontFamily: 'Inter, sans-serif', fontSize: 14, fontWeight: 600,
              color: '#FFFFFF',
            }}>Pipeline · Outbound</div>
          </div>
          <div style={{
            fontFamily: 'JetBrains Mono, monospace', fontSize: 12,
            color: '#7AA8FF', letterSpacing: '0.1em',
          }}>
            {Math.floor(localTime * 0.8 + 34)} ACTIVE
          </div>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: 10,
          height: 360,
        }}>
          {PIPELINE_COLUMNS.map((col, ci) => (
            <PipelineColumn key={col.id} col={col} ci={ci} localTime={localTime} />
          ))}
        </div>
      </div>

      {/* Live draft post */}
      <DraftPostPanel />
    </div>
  );
}

function PipelineColumn({ col, ci, localTime }) {
  // Compute which leads are in this column at this time.
  // Each lead's column index = Math.floor((t - offset) / STEP) clamped [0, 3]
  const STEP = 2.0;

  return (
    <div style={{
      background: 'rgba(15, 17, 21, 0.4)',
      border: '1px solid rgba(255,255,255,0.06)',
      borderRadius: 6,
      padding: 10,
      display: 'flex', flexDirection: 'column', gap: 8,
      overflow: 'hidden',
      position: 'relative',
    }}>
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        marginBottom: 4,
      }}>
        <div style={{
          fontFamily: 'Inter, sans-serif', fontSize: 11, fontWeight: 700,
          letterSpacing: '0.12em', textTransform: 'uppercase',
          color: col.accent,
        }}>{col.title}</div>
        <ColumnCount columnIndex={ci} localTime={localTime} step={STEP} />
      </div>

      <div style={{ position: 'relative', flex: 1 }}>
        {LEADS.map((lead, li) => {
          const t = localTime - lead.offset;
          if (t < 0) return null;
          const rawCol = Math.floor(t / STEP);
          const currentCol = Math.min(3, rawCol);
          const transT = Math.min(1, (t % STEP) / 0.5);

          // Only render if in THIS column or transitioning INTO it
          const prevCol = Math.max(0, currentCol - 1);
          const isIncoming = currentCol === ci && rawCol > 0 && transT < 1 && prevCol !== currentCol;
          const isHere = currentCol === ci && !isIncoming;
          const isLeaving = false; // handled by next column's incoming

          if (!isHere && !isIncoming) return null;

          // Stacking order within column — use lead index mod some offset
          const stackIndex = (li * 7) % 4;
          const yBase = stackIndex * 58;

          let slideX = 0, opacity = 1;
          if (isIncoming) {
            // Slide in from left
            const e = Easing.easeOutCubic(transT);
            slideX = (1 - e) * -120;
            opacity = e;
          }

          return (
            <LeadCard
              key={lead.name}
              lead={lead}
              y={yBase}
              slideX={slideX}
              opacity={opacity}
              accent={col.accent}
              status={col.id}
            />
          );
        })}
      </div>
    </div>
  );
}

function ColumnCount({ columnIndex, localTime, step }) {
  // Count leads currently in this column
  let count = 0;
  LEADS.forEach(lead => {
    const t = localTime - lead.offset;
    if (t < 0) return;
    const rawCol = Math.floor(t / step);
    const currentCol = Math.min(3, rawCol);
    if (currentCol === columnIndex) count++;
  });

  return (
    <div style={{
      fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
      color: '#8A909C', fontVariantNumeric: 'tabular-nums',
    }}>{count}</div>
  );
}

function LeadCard({ lead, y, slideX, opacity, accent, status }) {
  const statusLabels = {
    new: 'Imported',
    qualified: 'Scored 8/10',
    replied: 'Drafted reply',
    meeting: 'Booked Tue',
  };
  return (
    <div style={{
      position: 'absolute',
      left: slideX, top: y,
      right: 0,
      opacity,
      padding: 8,
      background: '#161A20',
      border: `1px solid ${accent}33`,
      borderLeft: `3px solid ${accent}`,
      borderRadius: 4,
      display: 'flex', alignItems: 'center', gap: 8,
      transition: 'left 300ms cubic-bezier(0.2,0.9,0.2,1), opacity 300ms',
    }}>
      <div style={{
        width: 24, height: 24, borderRadius: 999,
        background: accent, color: '#FFFFFF',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontFamily: 'Inter, sans-serif', fontSize: 10, fontWeight: 700,
        flexShrink: 0,
      }}>{lead.avatar}</div>
      <div style={{ minWidth: 0, flex: 1 }}>
        <div style={{
          fontFamily: 'Inter, sans-serif', fontSize: 11, fontWeight: 600,
          color: '#FFFFFF', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
        }}>{lead.name}</div>
        <div style={{
          fontFamily: 'JetBrains Mono, monospace', fontSize: 9,
          color: '#8A909C', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
        }}>{statusLabels[status]}</div>
      </div>
    </div>
  );
}

const DRAFT_CONTENT = [
  { type: 'header', text: 'Drafting · LinkedIn post' },
  { type: 'body',   text: 'Most SMEs aren\'t short on AI tools — they\'re buried in them. Three things we see every week…' },
  { type: 'header', text: 'Drafting · Proposal reply' },
  { type: 'body',   text: 'Hi Jamie — appreciate the brief. Based on your Q2 goals, here\'s a 90-day agent deployment plan…' },
  { type: 'header', text: 'Drafting · Review response' },
  { type: 'body',   text: 'Thank you for the review, Priya. We\'re so glad the onboarding workshop landed — let\'s find a time…' },
  { type: 'header', text: 'Drafting · Weekly newsletter' },
  { type: 'body',   text: 'This week in agent-land: three new workflows live, two big customer wins, one Zapier flow finally retired…' },
];

function DraftPostPanel() {
  const { localTime } = useSprite();
  const cycleDur = 4;
  const idx = Math.floor(localTime / cycleDur) % (DRAFT_CONTENT.length / 2);
  const header = DRAFT_CONTENT[idx * 2];
  const body = DRAFT_CONTENT[idx * 2 + 1];

  const cycleT = localTime % cycleDur;
  const typeDur = 2.5;
  const typeProgress = Easing.easeOutCubic(clamp(cycleT / typeDur, 0, 1));
  const visChars = Math.floor(typeProgress * body.text.length);
  const shown = body.text.slice(0, visChars);
  const blink = Math.floor(localTime * 3) % 2 ? 1 : 0.2;

  return (
    <div style={{
      background: 'rgba(255,255,255,0.03)',
      border: '1px solid rgba(255,255,255,0.12)',
      borderRadius: 10,
      padding: 18,
      flex: '1 1 0',
      display: 'flex', flexDirection: 'column', gap: 10,
    }}>
      <div style={{
        display: 'flex', alignItems: 'center', gap: 10,
      }}>
        <SpinnerRing/>
        <div style={{
          fontFamily: 'Inter, sans-serif', fontSize: 13, fontWeight: 600,
          color: '#FFFFFF',
        }}>{header.text}</div>
      </div>
      <div style={{
        fontFamily: 'Inter, sans-serif', fontSize: 16, lineHeight: 1.45,
        color: '#DCE3EE', fontWeight: 400,
      }}>
        {shown}
        {visChars < body.text.length && (
          <span style={{
            display: 'inline-block', width: 3, height: 16,
            background: '#2F7BFF', verticalAlign: 'text-bottom',
            marginLeft: 2, opacity: blink,
          }}/>
        )}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// PILLAR 03 — FINANCE & COMPLIANCE
// Right side: document flow (invoice → capture → code → reconcile → BAS)
// plus a live ledger and a drawing-in BAS chart.
// ─────────────────────────────────────────────────────────────────────

function ScenePillarFinance() {
  const start = 88, end = 108;
  return (
    <Sprite start={start} end={end}>
      <PillarChrome
        index="03"
        title="Finance & Compliance"
        subtitle="Your bookkeeper's volume at a fraction of the cost. Audit trail included."
        stat={{ value: 100, suffix: '%', label: 'audit trail — every action, every agent, every time' }}
        statStart={13}
        color="#2F7BFF"
      />
      <FinanceDashboard />
    </Sprite>
  );
}

const INVOICES = [
  { id: 'INV-8421', vendor: 'Northwind Logistics',  amount: 3420.55, code: '6-1200 · Freight' },
  { id: 'INV-8422', vendor: 'Telstra',              amount: 189.00,  code: '6-4400 · Telephony' },
  { id: 'INV-8423', vendor: 'AWS',                  amount: 1240.18, code: '6-2600 · Cloud' },
  { id: 'INV-8424', vendor: 'Officeworks',          amount: 87.45,   code: '6-3100 · Office' },
  { id: 'INV-8425', vendor: 'Canva',                amount: 29.99,   code: '6-4200 · Software' },
  { id: 'INV-8426', vendor: 'Linktree',             amount: 24.00,   code: '6-4200 · Software' },
  { id: 'INV-8427', vendor: 'Adobe',                amount: 89.99,   code: '6-4200 · Software' },
  { id: 'INV-8428', vendor: 'Deliveroo',            amount: 142.30,  code: '6-5100 · Staff meals' },
  { id: 'INV-8429', vendor: 'Melbourne Water',      amount: 312.80,  code: '6-3400 · Utilities' },
];

function FinanceDashboard() {
  const { localTime } = useSprite();
  const introAll = Easing.easeOutCubic(clamp((localTime - 0.6) / 0.8, 0, 1));

  return (
    <div style={{
      position: 'absolute',
      right: 60, top: 130,
      width: 920, height: 820,
      opacity: introAll,
      display: 'flex', flexDirection: 'column', gap: 14,
    }}>
      <InvoiceFeed />
      <BASChart />
    </div>
  );
}

function InvoiceFeed() {
  const { localTime } = useSprite();
  const perInvoice = 1.35;

  return (
    <div style={{
      background: 'rgba(255,255,255,0.03)',
      border: '1px solid rgba(255,255,255,0.12)',
      borderRadius: 10,
      padding: 18,
      flex: '0 0 auto',
      height: 430,
      display: 'flex', flexDirection: 'column',
    }}>
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        marginBottom: 14,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <StatusDot />
          <div style={{
            fontFamily: 'Inter, sans-serif', fontSize: 14, fontWeight: 600,
            color: '#FFFFFF',
          }}>Invoice capture · Xero sync</div>
        </div>
        <div style={{
          fontFamily: 'JetBrains Mono, monospace', fontSize: 12,
          color: '#7AA8FF', letterSpacing: '0.1em',
        }}>
          AUD · {Math.floor(localTime / perInvoice) + 12} TODAY
        </div>
      </div>

      <div style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
        {INVOICES.map((inv, i) => {
          const appearAt = i * perInvoice;
          if (localTime < appearAt) return null;
          const local = localTime - appearAt;
          const appear = Easing.easeOutCubic(clamp(local / 0.3, 0, 1));

          // Stage progression: 0 captured, 1 coded, 2 reconciled
          let stage = 0;
          if (local > 0.6) stage = 1;
          if (local > 1.2) stage = 2;

          // Stack newest at top, older slides down
          const idxFromNewest = Math.floor(localTime / perInvoice) - i;
          const y = idxFromNewest * 52;
          const fadeOut = idxFromNewest > 4 ? Math.max(0, 1 - (idxFromNewest - 4) * 0.3) : 1;

          return (
            <InvoiceRow
              key={inv.id}
              inv={inv}
              y={y}
              opacity={appear * fadeOut}
              stage={stage}
            />
          );
        })}
      </div>
    </div>
  );
}

function InvoiceRow({ inv, y, opacity, stage }) {
  const stageLabels = [
    { label: 'Captured',    color: '#7AA8FF' },
    { label: 'Coded',       color: '#2F7BFF' },
    { label: 'Reconciled',  color: '#1EA97C' },
  ];
  const s = stageLabels[stage];

  return (
    <div style={{
      position: 'absolute', left: 0, right: 0, top: y,
      display: 'grid',
      gridTemplateColumns: '90px 1fr 110px 140px 100px',
      alignItems: 'center',
      gap: 12,
      padding: '10px 14px',
      background: '#161A20',
      border: '1px solid rgba(255,255,255,0.06)',
      borderRadius: 6,
      opacity,
      transition: 'top 400ms cubic-bezier(0.2,0.9,0.2,1)',
    }}>
      <div style={{
        fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
        color: '#8A909C', letterSpacing: '0.05em',
      }}>{inv.id}</div>
      <div style={{
        fontFamily: 'Inter, sans-serif', fontSize: 13, fontWeight: 500,
        color: '#FFFFFF', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
      }}>{inv.vendor}</div>
      <div style={{
        fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
        color: '#BEC3CC', letterSpacing: '0.04em',
      }}>{inv.code}</div>
      <div style={{
        display: 'flex', alignItems: 'center', gap: 6,
        fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
        color: s.color, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase',
      }}>
        <div style={{ width: 6, height: 6, borderRadius: 999, background: s.color }}/>
        {s.label}
      </div>
      <div style={{
        fontFamily: 'JetBrains Mono, monospace', fontSize: 13,
        color: '#FFFFFF', fontWeight: 600, textAlign: 'right',
        fontVariantNumeric: 'tabular-nums',
      }}>
        ${inv.amount.toLocaleString('en-AU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
      </div>
    </div>
  );
}

function BASChart() {
  const { localTime } = useSprite();
  const chartStart = 3;
  if (localTime < chartStart) {
    return (
      <div style={{
        background: 'rgba(255,255,255,0.03)',
        border: '1px solid rgba(255,255,255,0.12)',
        borderRadius: 10,
        padding: 18,
        flex: '1 1 0',
      }}/>
    );
  }

  const local = localTime - chartStart;
  const drawT = Easing.easeOutCubic(clamp(local / 4, 0, 1));

  // Fake time-series: monthly GST collected and credits
  const W = 860, H = 200;
  const points = 12;
  const data = [];
  for (let i = 0; i < points; i++) {
    const x = (i / (points - 1)) * W;
    const base = 80 + Math.sin(i * 0.7) * 40 + (i * 4);
    const y = H - (base - 40);
    data.push({ x, y, value: Math.round(base * 100) });
  }

  const visiblePoints = Math.ceil(drawT * points);
  const pathD = data.slice(0, visiblePoints).map((p, i) =>
    `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`
  ).join(' ');

  const fillD = pathD + ` L ${data[visiblePoints - 1]?.x || 0} ${H} L 0 ${H} Z`;

  const totalValue = Math.floor(
    data.slice(0, visiblePoints).reduce((s, p) => s + p.value, 0)
  );

  return (
    <div style={{
      background: 'rgba(255,255,255,0.03)',
      border: '1px solid rgba(255,255,255,0.12)',
      borderRadius: 10,
      padding: 18,
      flex: '1 1 0',
      display: 'flex', flexDirection: 'column',
    }}>
      <div style={{
        display: 'flex', alignItems: 'baseline', justifyContent: 'space-between',
        marginBottom: 8,
      }}>
        <div style={{
          fontFamily: 'Inter, sans-serif', fontSize: 13, fontWeight: 600,
          color: '#FFFFFF',
        }}>BAS-ready · GST collected, rolling</div>
        <div style={{
          fontFamily: 'JetBrains Mono, monospace', fontSize: 20, fontWeight: 700,
          color: '#2F7BFF', fontVariantNumeric: 'tabular-nums',
        }}>${totalValue.toLocaleString('en-AU')}</div>
      </div>

      <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" style={{
        width: '100%', flex: 1,
      }}>
        {/* Grid */}
        <g stroke="rgba(255,255,255,0.06)" strokeWidth="1">
          {[0, 1, 2, 3].map(i => (
            <line key={i} x1="0" y1={H * i / 3} x2={W} y2={H * i / 3}/>
          ))}
        </g>
        {/* Fill */}
        {visiblePoints > 1 && (
          <path d={fillD} fill="#2F7BFF" fillOpacity="0.15"/>
        )}
        {/* Stroke */}
        <path d={pathD} fill="none" stroke="#2F7BFF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        {/* Dots */}
        {data.slice(0, visiblePoints).map((p, i) => (
          <circle key={i} cx={p.x} cy={p.y} r="3" fill="#FFFFFF" stroke="#2F7BFF" strokeWidth="1.5"/>
        ))}
        {/* Leading dot glow */}
        {visiblePoints > 0 && visiblePoints <= points && (
          <circle cx={data[visiblePoints - 1].x} cy={data[visiblePoints - 1].y} r="8"
                  fill="none" stroke="#7AA8FF" strokeWidth="1.5" opacity="0.6"/>
        )}
      </svg>
    </div>
  );
}

Object.assign(window, {
  PillarChrome, PillarStat,
  ScenePillarAdmin, ScenePillarMarketing, ScenePillarFinance,
});
