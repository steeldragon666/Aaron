/**
 * _TokenShowcase.tsx
 *
 * Dev-only visual reference that renders every v2 design token so we can
 * eyeball-verify the design system before building real components.
 *
 * Becomes the visual-regression surface for Phase 2+ — each UI primitive
 * (buttons, cards, inputs, etc.) will be added here as it's built.
 *
 * NOT linked from navigation. Task 1.6 will mount this at /_v2/_tokens
 * (dev-only). Never shipped to production.
 *
 * All tokens live in client/src/styles/omniscient.css scoped under `.v2`,
 * so this page MUST be wrapped with `withV2Scope()` at its root.
 */

import { useState } from "react";
import { withV2Scope } from "@/lib/theme-v2";
import {
  Button,
  Card,
  FeaturedCard,
  Eyebrow,
  Display,
  Lede,
  MonoBadge,
  CTALink,
  Input,
  Textarea,
  Select,
  Slider,
  RadioCard,
  CheckboxCard,
} from "@/components-v2/ui";
import {
  HeroSplit,
  HeroCentric,
  PillarGrid,
  CaseGrid,
  WorkshopCardGrid,
  StatsRow,
} from "@/components-v2/sections";
import { GraduationCap, Activity, Shield, Bot } from "lucide-react";

// =============================================================================
// Types — small shapes used to keep the data-driven sections tidy
// =============================================================================

interface ColorSwatch {
  token: string;
  hex: string;
  /** optional note e.g. alias relationships */
  note?: string;
}

interface ColorGroup {
  title: string;
  blurb: string;
  swatches: ColorSwatch[];
  /** render fg-colour of the swatch label swatch block (used for dark chips) */
  dark?: boolean;
}

interface TypeRow {
  token: string;
  sampleClass?: string;
  inlineStyle?: React.CSSProperties;
  sample: string;
  description: string;
}

interface SpaceRow {
  token: string;
  px: number;
}

interface RadiusRow {
  token: string;
  value: string;
}

// =============================================================================
// Data — every token from client/src/styles/omniscient.css
// =============================================================================

const coreTriTone: ColorSwatch[] = [
  { token: "--ink", hex: "#0F1115", note: "primary text, illustration disc" },
  { token: "--blue", hex: "#2F7BFF", note: "signature electric blue" },
  { token: "--paper", hex: "#FFFFFF", note: "canvas" },
];

const inkScale: ColorSwatch[] = [
  { token: "--ink-900", hex: "#0F1115", note: "= --ink" },
  { token: "--ink-800", hex: "#161A20" },
  { token: "--ink-700", hex: "#1E232B" },
  { token: "--ink-600", hex: "#2A2F37", note: "= --ink-2" },
  { token: "--ink-500", hex: "#3D434D" },
  { token: "--ink-400", hex: "#5B6270", note: "= --ink-3" },
  { token: "--ink-300", hex: "#8A909C" },
  { token: "--ink-200", hex: "#BEC3CC" },
  { token: "--ink-100", hex: "#E4E7EC", note: "= --line" },
];

const blueScale: ColorSwatch[] = [
  { token: "--blue-deep", hex: "#1C4FD6", note: "pressed / small type on light" },
  { token: "--blue-600", hex: "#2567E8" },
  { token: "--blue-500", hex: "#2F7BFF", note: "= --blue" },
  { token: "--blue-400", hex: "#5693FF" },
  { token: "--blue-300", hex: "#7AA8FF", note: "= --blue-glow" },
  { token: "--blue-200", hex: "#B8CFFF" },
  { token: "--blue-100", hex: "#E6EEFF", note: "subtle blue tint bg" },
];

const paperScale: ColorSwatch[] = [
  { token: "--paper", hex: "#FFFFFF", note: "canvas" },
  { token: "--paper-50", hex: "#FAFBFC" },
  { token: "--paper-100", hex: "#F4F6F9", note: "= --paper-2" },
];

const semantic: ColorSwatch[] = [
  { token: "--success", hex: "#1EA97C" },
  { token: "--success-bg", hex: "#E4F7EF" },
  { token: "--warn", hex: "#E8A23A" },
  { token: "--warn-bg", hex: "#FDF1DE" },
  { token: "--danger", hex: "#D94B4B" },
  { token: "--danger-bg", hex: "#FCE7E7" },
];

const semanticRoles: ColorSwatch[] = [
  { token: "--fg-1", hex: "#0F1115", note: "= --ink-900" },
  { token: "--fg-2", hex: "#2A2F37", note: "= --ink-600" },
  { token: "--fg-3", hex: "#5B6270", note: "= --ink-400" },
  { token: "--fg-inverse", hex: "#FFFFFF", note: "= --paper" },
  { token: "--bg-1", hex: "#FFFFFF", note: "= --paper" },
  { token: "--bg-2", hex: "#F4F6F9", note: "= --paper-100" },
  { token: "--bg-inverse", hex: "#0F1115", note: "= --ink-900" },
  { token: "--line", hex: "#E4E7EC", note: "= --ink-100" },
  { token: "--line-strong", hex: "#0F1115", note: "= --ink-900" },
  { token: "--accent", hex: "#2F7BFF", note: "= --blue" },
  { token: "--accent-fg", hex: "#FFFFFF", note: "= --paper" },
  { token: "--focus-ring", hex: "#7AA8FF", note: "= --blue-300" },
];

const colorGroups: ColorGroup[] = [
  { title: "Tri-tone core", blurb: "Three colors define the whole system.", swatches: coreTriTone },
  { title: "Ink scale", blurb: "Warm-neutral greys, near-black at top.", swatches: inkScale },
  { title: "Blue scale", blurb: "Built around --blue (=--blue-500).", swatches: blueScale },
  { title: "Paper scale", blurb: "Surface tints.", swatches: paperScale },
  { title: "Semantic", blurb: "Product UI only — never in marketing.", swatches: semantic },
  { title: "Semantic roles", blurb: "Aliases that map to the raw scales above.", swatches: semanticRoles },
];

const typeRows: TypeRow[] = [
  {
    token: ".display (--type-hero)",
    sampleClass: "display",
    sample: "The quick brown fox",
    description: "clamp(48px, 7vw, 96px) / 700 / -0.03em / 0.95",
  },
  {
    token: "h1 (--type-h1)",
    inlineStyle: {
      fontSize: "var(--type-h1)",
      fontWeight: 700,
      letterSpacing: "-0.025em",
      lineHeight: 1.05,
      margin: 0,
    },
    sample: "The quick brown fox jumps",
    description: "56px / 700 / -0.025em / 1.05",
  },
  {
    token: "h2 (--type-h2)",
    inlineStyle: {
      fontSize: "var(--type-h2)",
      fontWeight: 700,
      letterSpacing: "var(--track-snug)",
      lineHeight: "var(--leading-heading)",
      margin: 0,
    },
    sample: "The quick brown fox jumps over the lazy dog",
    description: "36px / 700 / -0.02em / 1.1",
  },
  {
    token: "h3 (--type-h3)",
    inlineStyle: {
      fontSize: "var(--type-h3)",
      fontWeight: 600,
      letterSpacing: "var(--track-snug)",
      lineHeight: "var(--leading-heading)",
      margin: 0,
    },
    sample: "The quick brown fox jumps over the lazy dog",
    description: "22px / 600 / -0.02em / 1.1",
  },
  {
    token: "h4 (--type-h4)",
    inlineStyle: {
      fontSize: "var(--type-h4)",
      fontWeight: 600,
      letterSpacing: "var(--track-normal)",
      lineHeight: "var(--leading-heading)",
      margin: 0,
    },
    sample: "The quick brown fox jumps over the lazy dog",
    description: "18px / 600 / 0 / 1.1",
  },
  {
    token: ".lede",
    sampleClass: "lede",
    sample:
      "Operational intelligence for teams who need to move fast without breaking what matters.",
    description: "20px / 400 / 1.45 (lede supporting paragraph)",
  },
  {
    token: "body (--type-body)",
    inlineStyle: {
      fontSize: "var(--type-body)",
      lineHeight: "var(--leading-body)",
      margin: 0,
    },
    sample:
      "The quick brown fox jumps over the lazy dog. We design interfaces that disappear so the work can do the talking.",
    description: "17px / 400 / 1.55",
  },
  {
    token: "body-sm (--type-body-sm)",
    inlineStyle: {
      fontSize: "var(--type-body-sm)",
      lineHeight: "var(--leading-body)",
      margin: 0,
    },
    sample: "The quick brown fox jumps over the lazy dog.",
    description: "15px / 400 / 1.55",
  },
  {
    token: ".small (--type-small)",
    sampleClass: "small",
    sample: "The quick brown fox jumps over the lazy dog.",
    description: "14px / 400 (supporting meta text)",
  },
  {
    token: ".eyebrow (--type-micro)",
    sampleClass: "eyebrow",
    sample: "INTELLIGENCE // CONNECTIVITY // INNOVATION",
    description: "12px / 600 / 0.14em / UPPERCASE",
  },
];

const spaceRows: SpaceRow[] = [
  { token: "--space-0", px: 0 },
  { token: "--space-1", px: 4 },
  { token: "--space-2", px: 8 },
  { token: "--space-3", px: 12 },
  { token: "--space-4", px: 16 },
  { token: "--space-5", px: 24 },
  { token: "--space-6", px: 32 },
  { token: "--space-7", px: 48 },
  { token: "--space-8", px: 64 },
  { token: "--space-9", px: 96 },
  { token: "--space-10", px: 128 },
];

const radiusRows: RadiusRow[] = [
  { token: "--radius-xs", value: "2px" },
  { token: "--radius-sm", value: "4px" },
  { token: "--radius-md", value: "6px" },
  { token: "--radius-lg", value: "8px" },
  { token: "--radius-xl", value: "12px" },
  { token: "--radius-pill", value: "999px" },
];

const motionRows = [
  { token: "--dur-fast", value: "120ms", description: "Hover tint / icon swap" },
  { token: "--dur-base", value: "180ms", description: "Default UI transitions" },
  { token: "--dur-slow", value: "280ms", description: "Layout shifts / reveals" },
  { token: "--ease-brand", value: "cubic-bezier(0.2, 0.9, 0.2, 1)", description: "Brand easing curve" },
];

// =============================================================================
// Presentational helpers — tiny layout primitives local to this file.
// Kept deliberately vanilla (no shadcn imports) so this page isolates tokens.
// =============================================================================

interface SectionProps {
  eyebrow: string;
  title: string;
  blurb?: string;
  children: React.ReactNode;
  dark?: boolean;
}

function Section({ eyebrow, title, blurb, children, dark }: SectionProps) {
  return (
    <section
      className={dark ? "ink-section" : ""}
      style={{
        paddingTop: "var(--space-9)",
        paddingBottom: "var(--space-9)",
      }}
    >
      <Container>
        <div style={{ marginBottom: "var(--space-7)" }}>
          <div className="eyebrow" style={{ marginBottom: "var(--space-2)" }}>
            {eyebrow}
          </div>
          <h2 style={{ margin: 0 }}>{title}</h2>
          {blurb ? (
            <p
              className="lede"
              style={{ marginTop: "var(--space-3)", marginBottom: 0, maxWidth: 680 }}
            >
              {blurb}
            </p>
          ) : null}
        </div>
        {children}
      </Container>
    </section>
  );
}

interface ContainerProps {
  children: React.ReactNode;
}

function Container({ children }: ContainerProps) {
  return (
    <div
      style={{
        width: "100%",
        maxWidth: "var(--container)",
        marginInline: "auto",
        paddingInline: "var(--gutter-sm)",
      }}
      className="v2-container"
    >
      {children}
    </div>
  );
}

// Swatch block — reusable color chip
interface SwatchProps {
  swatch: ColorSwatch;
}

function Swatch({ swatch }: SwatchProps) {
  return (
    <div>
      <div
        aria-hidden
        style={{
          background: `var(${swatch.token})`,
          border: "1px solid var(--line)",
          borderRadius: "var(--radius-md)",
          aspectRatio: "1 / 1",
          width: "100%",
          minHeight: 120,
          boxShadow: "var(--shadow-1)",
        }}
      />
      <div style={{ marginTop: "var(--space-3)" }}>
        <span className="mono-badge">{swatch.token}</span>
      </div>
      <div
        style={{
          marginTop: "var(--space-2)",
          fontFamily: "var(--font-mono)",
          fontSize: 12,
          color: "var(--fg-2)",
        }}
      >
        {swatch.hex}
      </div>
      {swatch.note ? (
        <div className="small" style={{ marginTop: "var(--space-1)" }}>
          {swatch.note}
        </div>
      ) : null}
    </div>
  );
}

// =============================================================================
// Main component
// =============================================================================

export default function TokenShowcase() {
  // Local state for interactive primitives. Keeping these uncontrolled would
  // freeze the visuals (e.g. Slider fill-bar wouldn't track the thumb).
  const [teamSize, setTeamSize] = useState(50);
  const [hourlyRate, setHourlyRate] = useState(180);
  const [aiMaturity, setAiMaturity] = useState("pilot");
  const [useCases, setUseCases] = useState<string[]>(["ops"]);

  const toggleUseCase = (value: string, checked: boolean) => {
    setUseCases((prev) =>
      checked ? [...prev, value] : prev.filter((v) => v !== value),
    );
  };

  return (
    <div
      className={withV2Scope("min-h-screen bg-paper text-ink")}
      style={{ fontFamily: "var(--font-text)" }}
    >
      {/* ---------------------------------------------------------------
          Desktop gutter override — design system calls for 72px horizontal
          padding on wide screens (vs 24px mobile). Tailwind has no match
          for the --gutter-lg token so we inline the media query.
          --------------------------------------------------------------- */}
      <style>{`
        @media (min-width: 1024px) {
          .v2-container { padding-inline: var(--gutter-lg); }
        }
      `}</style>

      {/* ===============================================================
          Header
          =============================================================== */}
      <header
        style={{
          paddingTop: "var(--space-9)",
          paddingBottom: "var(--space-8)",
          borderBottom: "1px solid var(--line)",
        }}
      >
        <Container>
          <div className="eyebrow" style={{ marginBottom: "var(--space-3)" }}>
            Token Showcase
          </div>
          <h1 className="display" style={{ margin: 0 }}>
            OmniscientAI v2 Design System
          </h1>
          <p className="lede" style={{ marginTop: "var(--space-5)", maxWidth: 780 }}>
            Every design token rendered visually. This page is the visual-regression
            surface for the v2 redesign — if a component looks wrong, the token
            sample here will show the bug first. Dev-only; not linked from the
            public site.
          </p>
          <div
            style={{
              marginTop: "var(--space-5)",
              display: "flex",
              gap: "var(--space-2)",
              flexWrap: "wrap",
            }}
          >
            <span className="mono-badge">Phase 1.5</span>
            <span className="mono-badge">omniscient.css</span>
            <span className="mono-badge">.v2 scope</span>
          </div>
        </Container>
      </header>

      {/* ===============================================================
          1. Color swatches
          =============================================================== */}
      <Section
        eyebrow="01 / Color"
        title="Color swatches"
        blurb="Six groups: three tri-tone cores, the ink and blue scales, paper tints, product-only semantic colors, and the semantic-role aliases."
      >
        {colorGroups.map((group) => (
          <div key={group.title} style={{ marginBottom: "var(--space-8)" }}>
            <h3 style={{ margin: 0, marginBottom: "var(--space-2)" }}>{group.title}</h3>
            <p style={{ margin: 0, marginBottom: "var(--space-5)", color: "var(--fg-2)" }}>
              {group.blurb}
            </p>
            <div
              className="swatch-grid"
              style={{
                display: "grid",
                gap: "var(--space-5)",
                gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
              }}
            >
              {group.swatches.map((sw) => (
                <Swatch key={sw.token} swatch={sw} />
              ))}
            </div>
          </div>
        ))}
        <style>{`
          @media (min-width: 768px) {
            .swatch-grid { grid-template-columns: repeat(4, minmax(0, 1fr)) !important; }
          }
        `}</style>
      </Section>

      {/* ===============================================================
          2. Typography scale
          =============================================================== */}
      <Section
        eyebrow="02 / Type"
        title="Typography scale"
        blurb="Inter for display and text. Sizes px-anchored except hero, which is fluid clamp(48px, 7vw, 96px)."
      >
        <div
          style={{
            display: "grid",
            rowGap: "var(--space-7)",
            borderTop: "1px solid var(--line)",
          }}
        >
          {typeRows.map((row) => (
            <div
              key={row.token}
              style={{
                display: "grid",
                gridTemplateColumns: "minmax(0, 1fr)",
                gap: "var(--space-4)",
                paddingTop: "var(--space-5)",
                borderBottom: "1px solid var(--line)",
                paddingBottom: "var(--space-5)",
              }}
              className="type-row"
            >
              {/* Token label + description */}
              <div>
                <div style={{ marginBottom: "var(--space-1)" }}>
                  <span className="mono-badge">{row.token}</span>
                </div>
                <div className="small">{row.description}</div>
              </div>
              {/* Live sample */}
              <div>
                {row.sampleClass ? (
                  <div className={row.sampleClass}>{row.sample}</div>
                ) : (
                  <div style={row.inlineStyle}>{row.sample}</div>
                )}
              </div>
            </div>
          ))}
        </div>
        <style>{`
          @media (min-width: 900px) {
            .type-row {
              grid-template-columns: 260px 1fr !important;
              align-items: baseline;
            }
          }
        `}</style>
      </Section>

      {/* ===============================================================
          3. Spacing scale
          =============================================================== */}
      <Section
        eyebrow="03 / Spacing"
        title="Spacing scale"
        blurb="4pt base. Use these instead of ad-hoc pixel values."
      >
        <div
          style={{
            display: "grid",
            rowGap: "var(--space-4)",
          }}
        >
          {spaceRows.map((s) => (
            <div
              key={s.token}
              style={{
                display: "grid",
                gridTemplateColumns: "200px 64px 1fr",
                alignItems: "center",
                gap: "var(--space-4)",
                padding: "var(--space-3) 0",
                borderBottom: "1px solid var(--line)",
              }}
            >
              <span className="mono-badge">{s.token}</span>
              <span
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: 12,
                  color: "var(--fg-2)",
                }}
              >
                {s.px}px
              </span>
              <div
                aria-hidden
                style={{
                  background: "var(--blue)",
                  height: 12,
                  width: Math.max(s.px, 1),
                  borderRadius: "var(--radius-xs)",
                }}
              />
            </div>
          ))}
        </div>
      </Section>

      {/* ===============================================================
          4. Radius scale
          =============================================================== */}
      <Section
        eyebrow="04 / Radius"
        title="Radius scale"
        blurb="6 corner-radius values from hairline to pill."
      >
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
            gap: "var(--space-5)",
          }}
          className="radius-grid"
        >
          {radiusRows.map((r) => (
            <div key={r.token}>
              <div
                aria-hidden
                style={{
                  width: "100%",
                  aspectRatio: "1 / 1",
                  minHeight: 120,
                  background: "var(--paper-100)",
                  border: "1px solid var(--line)",
                  borderRadius: `var(${r.token})`,
                }}
              />
              <div style={{ marginTop: "var(--space-3)" }}>
                <span className="mono-badge">{r.token}</span>
              </div>
              <div
                style={{
                  marginTop: "var(--space-1)",
                  fontFamily: "var(--font-mono)",
                  fontSize: 12,
                  color: "var(--fg-2)",
                }}
              >
                {r.value}
              </div>
            </div>
          ))}
        </div>
        <style>{`
          @media (min-width: 768px) {
            .radius-grid { grid-template-columns: repeat(6, minmax(0, 1fr)) !important; }
          }
        `}</style>
      </Section>

      {/* ===============================================================
          5. Shadows
          =============================================================== */}
      <Section
        eyebrow="05 / Shadow"
        title="Shadow scale"
        blurb="Two production shadows. Rendered on paper-100 so the drop is visible."
      >
        <div
          style={{
            background: "var(--paper-100)",
            padding: "var(--space-8)",
            borderRadius: "var(--radius-lg)",
            display: "grid",
            gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
            gap: "var(--space-7)",
          }}
        >
          {[
            { token: "--shadow-1", label: "Shadow 1", desc: "Subtle — cards, buttons at rest" },
            { token: "--shadow-2", label: "Shadow 2", desc: "Lifted — dropdowns, hover states" },
          ].map((s) => (
            <div key={s.token}>
              <div
                aria-hidden
                style={{
                  background: "var(--paper)",
                  borderRadius: "var(--radius-lg)",
                  aspectRatio: "3 / 2",
                  boxShadow: `var(${s.token})`,
                }}
              />
              <div style={{ marginTop: "var(--space-3)" }}>
                <span className="mono-badge">{s.token}</span>
              </div>
              <div className="small" style={{ marginTop: "var(--space-1)" }}>
                {s.desc}
              </div>
            </div>
          ))}
        </div>
        <div
          style={{ marginTop: "var(--space-4)", color: "var(--fg-2)" }}
          className="small"
        >
          <span className="mono-badge">--shadow-focus</span>
          &nbsp; 0 0 0 2px var(--paper), 0 0 0 4px var(--focus-ring) — used for
          :focus-visible outlines.
        </div>
      </Section>

      {/* ===============================================================
          6. Motion
          =============================================================== */}
      <Section
        eyebrow="06 / Motion"
        title="Motion tokens"
        blurb="Three durations and one brand easing curve. No demo animation — these are referenced by components."
      >
        <div style={{ display: "grid", rowGap: "var(--space-4)" }}>
          {motionRows.map((m) => (
            <div
              key={m.token}
              style={{
                display: "grid",
                gridTemplateColumns: "220px 180px 1fr",
                alignItems: "center",
                gap: "var(--space-4)",
                padding: "var(--space-4) 0",
                borderBottom: "1px solid var(--line)",
              }}
            >
              <span className="mono-badge">{m.token}</span>
              <span
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: 12,
                  color: "var(--fg-2)",
                }}
              >
                {m.value}
              </span>
              <span style={{ color: "var(--fg-2)" }}>{m.description}</span>
            </div>
          ))}
        </div>
      </Section>

      {/* ===============================================================
          7. Utility classes
          =============================================================== */}
      <Section
        eyebrow="07 / Utilities"
        title="Utility classes"
        blurb="Shortcuts for the patterns used most often."
      >
        <div
          style={{
            display: "grid",
            rowGap: "var(--space-6)",
          }}
        >
          {/* .eyebrow */}
          <div style={{ padding: "var(--space-5) 0", borderBottom: "1px solid var(--line)" }}>
            <div style={{ marginBottom: "var(--space-3)" }}>
              <span className="mono-badge">.eyebrow</span>
            </div>
            <div className="eyebrow">INTELLIGENCE // CONNECTIVITY // INNOVATION</div>
          </div>

          {/* .lede */}
          <div style={{ padding: "var(--space-5) 0", borderBottom: "1px solid var(--line)" }}>
            <div style={{ marginBottom: "var(--space-3)" }}>
              <span className="mono-badge">.lede</span>
            </div>
            <p className="lede" style={{ margin: 0 }}>
              Operational intelligence for teams that need to move fast without
              breaking what matters. Built for the people who live on the operations
              floor, not the ones who sell the software.
            </p>
          </div>

          {/* .mono-badge */}
          <div style={{ padding: "var(--space-5) 0", borderBottom: "1px solid var(--line)" }}>
            <div style={{ marginBottom: "var(--space-3)" }}>
              <span className="mono-badge">.mono-badge</span>
            </div>
            <div style={{ display: "flex", gap: "var(--space-2)", flexWrap: "wrap" }}>
              <span className="mono-badge">v2.0.0</span>
              <span className="mono-badge">feat/v2-redesign</span>
              <span className="mono-badge">/api/v2/health</span>
              <span className="mono-badge">AUTHENTICATED</span>
            </div>
          </div>

          {/* .display inline */}
          <div style={{ padding: "var(--space-5) 0", borderBottom: "1px solid var(--line)" }}>
            <div style={{ marginBottom: "var(--space-3)" }}>
              <span className="mono-badge">.display</span>
            </div>
            <div className="display" style={{ margin: 0 }}>
              Intelligence, wired.
            </div>
          </div>

          {/* .small */}
          <div style={{ padding: "var(--space-5) 0", borderBottom: "1px solid var(--line)" }}>
            <div style={{ marginBottom: "var(--space-3)" }}>
              <span className="mono-badge">.small</span>
            </div>
            <div className="small">
              Build meta, captions, footnotes — the quiet text that frames the
              main content.
            </div>
          </div>
        </div>
      </Section>

      {/* ===============================================================
          8. Section-flip pattern (.ink-section)
          =============================================================== */}
      <div className="ink-section">
        <Section
          eyebrow="08 / Flip"
          title=".ink-section flip"
          blurb="The primary way to pace a long page. Swap a section to near-black and invert its content. Everything inside — headings, paragraphs, eyebrows — inherits inverse colors automatically."
          dark
        >
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
              gap: "var(--space-5)",
            }}
            className="flip-card-grid"
          >
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                style={{
                  border: "1px solid color-mix(in oklab, var(--paper) 18%, transparent)",
                  borderRadius: "var(--radius-lg)",
                  padding: "var(--space-6)",
                }}
              >
                <div className="eyebrow">Pattern {String(i).padStart(2, "0")}</div>
                <h4 style={{ marginTop: "var(--space-3)", marginBottom: "var(--space-2)" }}>
                  Content flows without extra styles
                </h4>
                <p style={{ margin: 0 }}>
                  Heading colors, paragraph tone, and eyebrow tint are all handled
                  by the .ink-section cascade in omniscient.css.
                </p>
              </div>
            ))}
          </div>
          <style>{`
            @media (min-width: 768px) {
              .flip-card-grid { grid-template-columns: repeat(4, minmax(0, 1fr)) !important; }
            }
          `}</style>
        </Section>
      </div>

      {/* ===============================================================
          UI Primitives — every component shipped in Phase 2
          This is the canonical visual-regression surface for the redesign.
          Phase 3+ components will append further subsections here.
          =============================================================== */}
      <Section
        eyebrow="UI / Primitives"
        title="UI Primitives"
        blurb="Every component shipped in Phase 2. Each category renders its full variant matrix so visual regressions show up here first. All imports from @/components-v2/ui."
      >
        {/* -----------------------------------------------------------------
            Buttons — 3 variants × 2 sizes, plus arrow + disabled examples
            ----------------------------------------------------------------- */}
        <div style={{ marginBottom: "var(--space-8)" }}>
          <Eyebrow style={{ marginBottom: "var(--space-2)", display: "block" }}>
            Buttons
          </Eyebrow>
          <h3 style={{ margin: 0, marginBottom: "var(--space-2)" }}>Button</h3>
          <p style={{ margin: 0, marginBottom: "var(--space-5)", color: "var(--fg-2)" }}>
            Three variants (primary, secondary, ghost) at two sizes (md, lg), plus
            the arrow affordance and disabled state.
          </p>
          <div
            style={{
              background: "var(--paper-100)",
              padding: "var(--space-6)",
              borderRadius: "var(--radius-lg)",
              display: "flex",
              flexWrap: "wrap",
              gap: "var(--space-4)",
              alignItems: "center",
            }}
          >
            <Button variant="primary" size="md">Primary md</Button>
            <Button variant="primary" size="lg">Primary lg</Button>
            <Button variant="secondary" size="md">Secondary md</Button>
            <Button variant="secondary" size="lg">Secondary lg</Button>
            <Button variant="ghost" size="md">Ghost md</Button>
            <Button variant="ghost" size="lg">Ghost lg</Button>
            <Button variant="primary" size="lg" arrow>
              With arrow
            </Button>
            <Button variant="primary" size="lg" disabled>
              Disabled
            </Button>
          </div>
        </div>

        {/* -----------------------------------------------------------------
            Cards — paper, paper-2, linked, featured
            ----------------------------------------------------------------- */}
        <div style={{ marginBottom: "var(--space-8)" }}>
          <Eyebrow style={{ marginBottom: "var(--space-2)", display: "block" }}>
            Cards
          </Eyebrow>
          <h3 style={{ margin: 0, marginBottom: "var(--space-2)" }}>Card &amp; FeaturedCard</h3>
          <p style={{ margin: 0, marginBottom: "var(--space-5)", color: "var(--fg-2)" }}>
            Two tones plus an ink-flipped featured variant. Cards can also render
            as an anchor tag via <code style={{ fontFamily: "var(--font-mono)" }}>as=&quot;a&quot;</code>.
          </p>
          <div
            style={{
              background: "var(--paper-100)",
              padding: "var(--space-6)",
              borderRadius: "var(--radius-lg)",
              display: "grid",
              gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
              gap: "var(--space-5)",
            }}
            className="card-grid"
          >
            <Card tone="paper">
              <Eyebrow>Paper tone</Eyebrow>
              <h4 style={{ margin: "var(--space-2) 0 var(--space-2)" }}>
                Default card surface
              </h4>
              <p style={{ margin: 0, color: "var(--fg-2)" }}>
                Lives on --paper-100 to show its own --paper background.
                Elevates on hover via --shadow-1.
              </p>
            </Card>
            <Card tone="paper-2">
              <Eyebrow>Paper-2 tone</Eyebrow>
              <h4 style={{ margin: "var(--space-2) 0 var(--space-2)" }}>
                Alt card surface
              </h4>
              <p style={{ margin: 0, color: "var(--fg-2)" }}>
                Uses --paper-2 for a subtly tinted variant when paper tone would
                vanish against the parent surface.
              </p>
            </Card>
            <Card as="a" href="#primitives-cards" tone="paper">
              <Eyebrow>Linked card</Eyebrow>
              <h4 style={{ margin: "var(--space-2) 0 var(--space-2)" }}>
                Rendered as &lt;a&gt;
              </h4>
              <p style={{ margin: 0, color: "var(--fg-2)" }}>
                Cursor changes to pointer and focus-visible gets the blue-glow
                outline. Anchor props pass through unchanged.
              </p>
            </Card>
            <FeaturedCard>
              <Eyebrow>Featured card</Eyebrow>
              <h4 style={{ margin: "var(--space-2) 0 var(--space-2)" }}>
                Ink-flipped emphasis
              </h4>
              <p style={{ margin: 0 }}>
                Uses --ink background with --paper text. Stronger hover shadow
                for headline placement in a grid.
              </p>
            </FeaturedCard>
          </div>
          <style>{`
            @media (max-width: 767px) {
              .card-grid { grid-template-columns: 1fr !important; }
            }
          `}</style>
        </div>

        {/* -----------------------------------------------------------------
            Typography primitives — Eyebrow, Display, Lede, MonoBadge
            ----------------------------------------------------------------- */}
        <div style={{ marginBottom: "var(--space-8)" }}>
          <Eyebrow style={{ marginBottom: "var(--space-2)", display: "block" }}>
            Typography
          </Eyebrow>
          <h3 style={{ margin: 0, marginBottom: "var(--space-2)" }}>
            Eyebrow, Display, Lede, MonoBadge
          </h3>
          <p style={{ margin: 0, marginBottom: "var(--space-5)", color: "var(--fg-2)" }}>
            Typed wrappers over the utility classes in omniscient.css. Each has a
            small constrained <code style={{ fontFamily: "var(--font-mono)" }}>as</code> prop
            for semantic flexibility.
          </p>
          <div
            style={{
              background: "var(--paper-100)",
              padding: "var(--space-6)",
              borderRadius: "var(--radius-lg)",
              display: "grid",
              rowGap: "var(--space-6)",
            }}
          >
            <div>
              <div style={{ marginBottom: "var(--space-2)" }}>
                <MonoBadge>&lt;Eyebrow&gt;</MonoBadge>
              </div>
              <Eyebrow>Featured</Eyebrow>
            </div>
            <div>
              <div style={{ marginBottom: "var(--space-2)" }}>
                <MonoBadge>&lt;Display&gt;</MonoBadge>
              </div>
              <Display as="div">Unleashing intelligent connections</Display>
            </div>
            <div>
              <div style={{ marginBottom: "var(--space-2)" }}>
                <MonoBadge>&lt;Lede&gt;</MonoBadge>
              </div>
              <Lede>
                Vendor-neutral AI training and consulting for Melbourne SMEs.
              </Lede>
            </div>
            <div>
              <div style={{ marginBottom: "var(--space-2)" }}>
                <MonoBadge>&lt;MonoBadge&gt;</MonoBadge>
              </div>
              <div style={{ display: "flex", gap: "var(--space-2)", flexWrap: "wrap" }}>
                <MonoBadge>$4,995 AUD</MonoBadge>
                <MonoBadge>2 hours</MonoBadge>
                <MonoBadge>Intermediate</MonoBadge>
              </div>
            </div>
          </div>
        </div>

        {/* -----------------------------------------------------------------
            Links — CTALink (internal + external)
            ----------------------------------------------------------------- */}
        <div style={{ marginBottom: "var(--space-8)" }}>
          <Eyebrow style={{ marginBottom: "var(--space-2)", display: "block" }}>
            Links
          </Eyebrow>
          <h3 style={{ margin: 0, marginBottom: "var(--space-2)" }}>CTALink</h3>
          <p style={{ margin: 0, marginBottom: "var(--space-5)", color: "var(--fg-2)" }}>
            Inline call-to-action anchor with arrow glyph. <code style={{ fontFamily: "var(--font-mono)" }}>external</code>
            swaps the glyph to ↗ and sets target/rel attributes.
          </p>
          <div
            style={{
              background: "var(--paper-100)",
              padding: "var(--space-6)",
              borderRadius: "var(--radius-lg)",
              display: "flex",
              flexWrap: "wrap",
              gap: "var(--space-6)",
              alignItems: "center",
            }}
          >
            <CTALink href="#primitives-links">Read the case study</CTALink>
            <CTALink href="https://example.com" external>
              Visit Anthropic
            </CTALink>
          </div>
        </div>

        {/* -----------------------------------------------------------------
            Form fields — Input, Textarea, Select
            Wrapped in a paper-2 card so --paper backgrounds show.
            ----------------------------------------------------------------- */}
        <div style={{ marginBottom: "var(--space-8)" }}>
          <Eyebrow style={{ marginBottom: "var(--space-2)", display: "block" }}>
            Forms
          </Eyebrow>
          <h3 style={{ margin: 0, marginBottom: "var(--space-2)" }}>
            Input, Textarea, Select
          </h3>
          <p style={{ margin: 0, marginBottom: "var(--space-5)", color: "var(--fg-2)" }}>
            Shared API: optional label, hint, and error. Error state swaps the
            hint for a red message and flips the border token. Rendered on
            paper-2 to expose the field&rsquo;s --paper background.
          </p>
          <div
            style={{
              background: "var(--paper-100)",
              padding: "var(--space-6)",
              borderRadius: "var(--radius-lg)",
              display: "grid",
              gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
              gap: "var(--space-5)",
            }}
            className="form-grid"
          >
            <Input label="Work email" placeholder="name@company.com" />
            <Input label="Role" hint="Your position, if applicable" />
            <Input
              label="Password"
              type="password"
              error="Must be at least 8 characters"
            />
            <Select label="Industry" defaultValue="">
              <option value="" disabled>
                Select an industry
              </option>
              <option value="healthcare">Healthcare</option>
              <option value="finance">Finance</option>
              <option value="retail">Retail</option>
              <option value="logistics">Logistics</option>
              <option value="government">Government</option>
            </Select>
            <div style={{ gridColumn: "1 / -1" }}>
              <Textarea
                label="Project goals"
                placeholder="Describe what success looks like in six months..."
                rows={4}
              />
            </div>
          </div>
          <style>{`
            @media (max-width: 767px) {
              .form-grid { grid-template-columns: 1fr !important; }
            }
          `}</style>
        </div>

        {/* -----------------------------------------------------------------
            Slider — with live state so fill-bar tracks the thumb
            ----------------------------------------------------------------- */}
        <div style={{ marginBottom: "var(--space-8)" }}>
          <Eyebrow style={{ marginBottom: "var(--space-2)", display: "block" }}>
            Slider
          </Eyebrow>
          <h3 style={{ margin: 0, marginBottom: "var(--space-2)" }}>Slider</h3>
          <p style={{ margin: 0, marginBottom: "var(--space-5)", color: "var(--fg-2)" }}>
            Range input with a linear-gradient fill that tracks the value. The
            second example supplies a <code style={{ fontFamily: "var(--font-mono)" }}>valueDisplay</code>
            formatter for currency.
          </p>
          <div
            style={{
              background: "var(--paper-100)",
              padding: "var(--space-6)",
              borderRadius: "var(--radius-lg)",
              display: "grid",
              rowGap: "var(--space-6)",
            }}
          >
            <Slider
              label="Team size"
              min={1}
              max={200}
              value={teamSize}
              onChange={(e) =>
                setTeamSize(Number((e.target as HTMLInputElement).value))
              }
            />
            <Slider
              label="Hourly rate"
              min={50}
              max={500}
              value={hourlyRate}
              onChange={(e) =>
                setHourlyRate(Number((e.target as HTMLInputElement).value))
              }
              valueDisplay={(v) => `$${v}`}
            />
          </div>
        </div>

        {/* -----------------------------------------------------------------
            RadioCard — single-select group with state
            ----------------------------------------------------------------- */}
        <div style={{ marginBottom: "var(--space-8)" }}>
          <Eyebrow style={{ marginBottom: "var(--space-2)", display: "block" }}>
            Selection — single
          </Eyebrow>
          <h3 style={{ margin: 0, marginBottom: "var(--space-2)" }}>RadioCard group</h3>
          <p style={{ margin: 0, marginBottom: "var(--space-5)", color: "var(--fg-2)" }}>
            Radio-card selection surface used throughout the AI-readiness quiz.
            Click any card to select; the other two deselect automatically.
          </p>
          <div
            style={{
              background: "var(--paper-100)",
              padding: "var(--space-6)",
              borderRadius: "var(--radius-lg)",
              display: "grid",
              rowGap: "var(--space-3)",
            }}
            role="radiogroup"
            aria-label="AI maturity"
          >
            <RadioCard
              name="ai-maturity"
              value="exploring"
              label="Our team is exploring AI for the first time"
              description="Curiosity-driven — no production models yet."
              checked={aiMaturity === "exploring"}
              onChange={setAiMaturity}
            />
            <RadioCard
              name="ai-maturity"
              value="pilot"
              label="We've done a pilot or two"
              description="Early traction; scoping the next step."
              checked={aiMaturity === "pilot"}
              onChange={setAiMaturity}
            />
            <RadioCard
              name="ai-maturity"
              value="core"
              label="AI is part of our core product"
              description="Models in production, iterating on evaluation."
              checked={aiMaturity === "core"}
              onChange={setAiMaturity}
            />
          </div>
        </div>

        {/* -----------------------------------------------------------------
            CheckboxCard — multi-select group with array state
            ----------------------------------------------------------------- */}
        <div style={{ marginBottom: 0 }}>
          <Eyebrow style={{ marginBottom: "var(--space-2)", display: "block" }}>
            Selection — multi
          </Eyebrow>
          <h3 style={{ margin: 0, marginBottom: "var(--space-2)" }}>CheckboxCard group</h3>
          <p style={{ margin: 0, marginBottom: "var(--space-5)", color: "var(--fg-2)" }}>
            Multi-select sibling of RadioCard. Each card toggles independently;
            selected state is tracked as a string array.
          </p>
          <div
            style={{
              background: "var(--paper-100)",
              padding: "var(--space-6)",
              borderRadius: "var(--radius-lg)",
              display: "grid",
              rowGap: "var(--space-3)",
            }}
            role="group"
            aria-label="AI use cases"
          >
            <CheckboxCard
              name="use-cases"
              value="ops"
              label="Internal operations"
              description="Back-office automation, knowledge retrieval, ticket triage."
              checked={useCases.includes("ops")}
              onChange={toggleUseCase}
            />
            <CheckboxCard
              name="use-cases"
              value="product"
              label="Customer-facing products"
              description="Assistants, copilots, generative features in the product."
              checked={useCases.includes("product")}
              onChange={toggleUseCase}
            />
            <CheckboxCard
              name="use-cases"
              value="risk"
              label="Compliance and risk"
              description="Policy review, audit trails, red-teaming."
              checked={useCases.includes("risk")}
              onChange={toggleUseCase}
            />
          </div>
        </div>
      </Section>

      {/* ===============================================================
          UI / Sections — hero section patterns composed from primitives
          Gives a direct eyeball of how real marketing pages will feel
          once Phase 7 wires up the actual routes.
          =============================================================== */}
      <Section
        eyebrow="UI / Sections"
        title="Hero section patterns"
        blurb="HeroSplit (asymmetric 55/45) and HeroCentric (centered single column), rendered with realistic home + about copy. Each preview is wrapped in a bordered container so the section's own edges read cleanly."
      >
        {/* ------------------------------------------------------------
            HeroSplit preview
            ------------------------------------------------------------ */}
        <div style={{ marginBottom: "var(--space-8)" }}>
          <div style={{ marginBottom: "var(--space-3)" }}>
            <MonoBadge>&lt;HeroSplit&gt;</MonoBadge>
          </div>
          <p style={{ margin: 0, marginBottom: "var(--space-5)", color: "var(--fg-2)" }}>
            Asymmetric home hero — copy left, BrainGraphic right. Stacks on mobile.
          </p>
          <div className="border border-line rounded-lg overflow-hidden">
            <HeroSplit
              eyebrow="INTELLIGENCE // CONNECTIVITY // INNOVATION"
              title="Unleashing the power of intelligent connections."
              lede="Vendor-neutral AI training and consulting for Melbourne SMEs. We work in short engagements with named practitioners — every workshop leaves your team with a shippable artefact."
              primaryCta={{ label: "Book a 20-minute call", href: "/book" }}
              secondaryCta={{ label: "See our work", href: "/work" }}
            />
          </div>
        </div>

        {/* ------------------------------------------------------------
            HeroCentric preview
            ------------------------------------------------------------ */}
        <div style={{ marginBottom: 0 }}>
          <div style={{ marginBottom: "var(--space-3)" }}>
            <MonoBadge>&lt;HeroCentric&gt;</MonoBadge>
          </div>
          <p style={{ margin: 0, marginBottom: "var(--space-5)", color: "var(--fg-2)" }}>
            Centered single-column hero for About / Approach / Contact pages. Optional
            graphic below CTAs via <code style={{ fontFamily: "var(--font-mono)" }}>showGraphic</code>.
          </p>
          <div className="border border-line rounded-lg overflow-hidden">
            <HeroCentric
              eyebrow="About us"
              title="A boutique AI consultancy, built for the real world."
              lede="Named practitioners. Short engagements. Every workshop ends with a shippable artefact, not a 40-slide deck."
              primaryCta={{ label: "Meet the team", href: "/about" }}
              showGraphic
            />
          </div>
        </div>

        {/* ------------------------------------------------------------
            PillarGrid preview
            ------------------------------------------------------------ */}
        <div style={{ marginTop: "var(--space-8)", marginBottom: "var(--space-8)" }}>
          <div style={{ marginBottom: "var(--space-3)" }}>
            <MonoBadge>&lt;PillarGrid&gt;</MonoBadge>
          </div>
          <p style={{ margin: 0, marginBottom: "var(--space-5)", color: "var(--fg-2)" }}>
            4-up practice area grid. Each pillar has a Lucide icon, title,
            description, and an optional "Learn more" CTA when an href is
            supplied.
          </p>
          <div className="border border-line rounded-lg overflow-hidden">
            <PillarGrid
              eyebrow="WHAT WE DO"
              sectionTitle="Four practice areas, one consultancy."
              lede="Every engagement draws on the same vendor-neutral playbook — scoped tight, run by named practitioners, and closed with a shippable artefact."
              pillars={[
                {
                  icon: GraduationCap,
                  title: "AI Training",
                  description:
                    "Hands-on workshops that leave your team with a working prototype, not a slide deck.",
                  href: "/services/training",
                },
                {
                  icon: Activity,
                  title: "Health Technologies",
                  description:
                    "Clinical AI adoption patterns for regulated healthcare and aged-care settings.",
                  href: "/services/health",
                },
                {
                  icon: Shield,
                  title: "Defense Systems",
                  description:
                    "Hardened agentic systems for defence primes and sovereign-data workloads.",
                  href: "/services/defense",
                },
                {
                  icon: Bot,
                  title: "Agentic Ops",
                  description:
                    "Production-grade marketing and ops agents that actually ship and observe themselves.",
                  href: "/services/agentic-ops",
                },
              ]}
            />
          </div>
        </div>

        {/* ------------------------------------------------------------
            CaseGrid preview
            ------------------------------------------------------------ */}
        <div style={{ marginBottom: "var(--space-8)" }}>
          <div style={{ marginBottom: "var(--space-3)" }}>
            <MonoBadge>&lt;CaseGrid&gt;</MonoBadge>
          </div>
          <p style={{ margin: 0, marginBottom: "var(--space-5)", color: "var(--fg-2)" }}>
            3-up case study grid. First tile is a FeaturedCard on ink; the
            remaining two are standard paper Cards.
          </p>
          <div className="border border-line rounded-lg overflow-hidden">
            <CaseGrid
              eyebrow="SELECTED WORK"
              sectionTitle="Where we've shipped."
              cases={[
                {
                  industry: "Healthcare provider",
                  title: "Radiology triage agent",
                  outcome:
                    "40% faster first-read on priority scans across three Melbourne hospitals.",
                  href: "/work/radiology",
                },
                {
                  industry: "Financial services",
                  title: "KYC onboarding pipeline",
                  outcome:
                    "Cut manual review from 45 minutes to 8 minutes per applicant with a human-in-the-loop.",
                  href: "/work/kyc",
                },
                {
                  industry: "Industrial automation",
                  title: "Predictive maintenance co-pilot",
                  outcome:
                    "Reduced unplanned downtime by 27% across 14 processing sites in six months.",
                  href: "/work/maintenance",
                },
              ]}
            />
          </div>
        </div>

        {/* ------------------------------------------------------------
            WorkshopCardGrid preview
            ------------------------------------------------------------ */}
        <div style={{ marginBottom: "var(--space-8)" }}>
          <div style={{ marginBottom: "var(--space-3)" }}>
            <MonoBadge>&lt;WorkshopCardGrid&gt;</MonoBadge>
          </div>
          <p style={{ margin: 0, marginBottom: "var(--space-5)", color: "var(--fg-2)" }}>
            3-up workshop catalog grid. Meta row (duration · format · price),
            title, description, and a full-width "Book this workshop" CTA per
            card.
          </p>
          <div className="border border-line rounded-lg overflow-hidden">
            <WorkshopCardGrid
              eyebrow="UPCOMING WORKSHOPS"
              sectionTitle="Hands-on training for Melbourne SMEs."
              workshops={[
                {
                  slug: "ai-fundamentals-sme",
                  title: "AI Fundamentals for SMEs",
                  description:
                    "A two-day foundation covering LLMs, RAG, and agentic patterns with a prototype you'll take home.",
                  duration: "2 days",
                  format: "In-person, Melbourne",
                  price: "$4,995 AUD",
                },
                {
                  slug: "clinical-ai-primer",
                  title: "Clinical AI Primer",
                  description:
                    "Safe adoption patterns and governance scaffolding for regulated healthcare environments.",
                  duration: "1 day",
                  format: "Hybrid",
                  price: "From $2,495",
                },
                {
                  slug: "agentic-ops-lab",
                  title: "Agentic Ops Lab",
                  description:
                    "Build an internal agent that actually ships — observability, guardrails, and evals included.",
                  duration: "3 days",
                  format: "In-person, Sydney",
                  price: "$6,995 AUD",
                },
              ]}
            />
          </div>
        </div>

        {/* ------------------------------------------------------------
            StatsRow preview (paper + ink variants)
            ------------------------------------------------------------ */}
        <div style={{ marginBottom: "var(--space-5)" }}>
          <div style={{ marginBottom: "var(--space-3)" }}>
            <MonoBadge>&lt;StatsRow&gt;</MonoBadge>
          </div>
          <p style={{ margin: 0, marginBottom: "var(--space-5)", color: "var(--fg-2)" }}>
            4-column row of big numbers + short labels. Paper tone (default)
            and ink tone shown so the dramatic pacing variant is visible.
          </p>
          <div className="border border-line rounded-lg overflow-hidden">
            <StatsRow
              eyebrow="IMPACT"
              sectionTitle="By the numbers."
              stats={[
                { value: "50+", label: "Workshops delivered" },
                { value: "12", label: "Industries" },
                { value: "4.9/5", label: "Satisfaction" },
                { value: "8hrs", label: "Saved per week" },
              ]}
            />
          </div>
        </div>
        <div style={{ marginBottom: 0 }}>
          <div style={{ marginBottom: "var(--space-3)" }}>
            <MonoBadge>&lt;StatsRow tone="ink"&gt;</MonoBadge>
          </div>
          <p style={{ margin: 0, marginBottom: "var(--space-5)", color: "var(--fg-2)" }}>
            Ink-toned pacing variant — rendered via InkSection for full-bleed
            drama in the middle of a long page.
          </p>
          <div className="border border-line rounded-lg overflow-hidden">
            <StatsRow
              tone="ink"
              stats={[
                { value: "50+", label: "Workshops delivered" },
                { value: "12", label: "Industries" },
                { value: "4.9/5", label: "Satisfaction" },
                { value: "8hrs", label: "Saved per week" },
              ]}
            />
          </div>
        </div>
      </Section>

      {/* ===============================================================
          9. Font families
          =============================================================== */}
      <Section
        eyebrow="09 / Typefaces"
        title="Font families"
        blurb="Inter drives display and text. JetBrains Mono is the code/label face. Webfonts imported at the top of omniscient.css."
      >
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
            gap: "var(--space-6)",
          }}
          className="font-grid"
        >
          {[
            {
              label: "--font-display / --font-text",
              family:
                "'Inter', 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif",
              sample: "Inter — quick brown fox",
              tokenValue: "'Inter', 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif",
            },
            {
              label: "--font-mono",
              family: "'JetBrains Mono', ui-monospace, 'SF Mono', Menlo, monospace",
              sample: "JetBrains Mono — 0O1lI{}",
              tokenValue: "'JetBrains Mono', ui-monospace, 'SF Mono', Menlo, monospace",
            },
          ].map((f) => (
            <div
              key={f.label}
              style={{
                border: "1px solid var(--line)",
                borderRadius: "var(--radius-lg)",
                padding: "var(--space-6)",
                background: "var(--paper)",
              }}
            >
              <div style={{ marginBottom: "var(--space-3)" }}>
                <span className="mono-badge">{f.label}</span>
              </div>
              <div
                style={{
                  fontFamily: f.family,
                  fontSize: 24,
                  fontWeight: 600,
                  lineHeight: 1.2,
                  marginBottom: "var(--space-4)",
                }}
              >
                {f.sample}
              </div>
              <div
                style={{
                  fontFamily: f.family,
                  fontSize: 18,
                  lineHeight: 1.45,
                  color: "var(--fg-2)",
                  marginBottom: "var(--space-4)",
                }}
              >
                The quick brown fox jumps over the lazy dog. 0123456789
              </div>
              <div
                className="small"
                style={{
                  fontFamily: "var(--font-mono)",
                  whiteSpace: "normal",
                  wordBreak: "break-word",
                }}
              >
                {f.tokenValue}
              </div>
            </div>
          ))}
        </div>
        <style>{`
          @media (min-width: 768px) {
            .font-grid { grid-template-columns: repeat(2, minmax(0, 1fr)) !important; }
          }
          @media (max-width: 767px) {
            .font-grid { grid-template-columns: 1fr !important; }
          }
        `}</style>
      </Section>

      {/* ===============================================================
          Footer — meta
          =============================================================== */}
      <footer
        style={{
          paddingTop: "var(--space-7)",
          paddingBottom: "var(--space-9)",
          borderTop: "1px solid var(--line)",
        }}
      >
        <Container>
          <div className="eyebrow" style={{ marginBottom: "var(--space-2)" }}>
            End of file
          </div>
          <p style={{ margin: 0, color: "var(--fg-2)" }}>
            Source of truth: <span className="mono-badge">client/src/styles/omniscient.css</span>.
            Every new UI primitive built in Phase 2+ should appear here.
          </p>
        </Container>
      </footer>
    </div>
  );
}
