# OmniscientAI Website Redesign Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Migrate `omniscientai.io` from the current dark-theme 22-page site to a complete new Bauhaus-geometric design system across 20 pages, with zero URL regression and a fast rollback path.

**Architecture:** Parallel scaffold approach. Build `pages-v2/`, `components-v2/`, and `styles/omniscient.css` alongside existing code; both coexist via a `VITE_USE_V2` env flag. Router flips at cutover; cleanup PR removes legacy 24h after flip stabilizes.

**Tech Stack:** React 18, Vite 5, TailwindCSS v4, Wouter (router), Framer Motion (sparingly, per design system motion rules), Lucide icons, Inter + JetBrains Mono (Google Fonts CDN for now), Vitest (existing).

**Design doc:** `docs/plans/2026-04-22-website-redesign-design.md` — read this first. All visual rules, token proportions, and voice guidelines live there.

**Design system source:** `C:\Users\Aaron\Downloads\Omniscient AI Design System.zip` — reference `colors_and_type.css`, `ui_kits/website/components/*.jsx`, and `assets/*.png` throughout.

---

## Execution notes

- **Working dir:** `C:\Users\Aaron\omniscient website\omniscientai\`
- **Git root:** `C:\Users\Aaron\` (user's home folder is a git repo — scope commits to `omniscient website/omniscientai/` paths only).
- **Branch:** Create `feat/v2-redesign` before starting Phase 0. All work lands on this branch until router flip.
- **Test runner:** `pnpm test` (Vitest). Tests go in `*.test.tsx` adjacent to source files.
- **Dev server:** `pnpm dev` → `localhost:3000`.
- **Build check:** `pnpm build` after every phase end to catch TS errors early.
- **Commit cadence:** commit after every task. Small, reviewable PRs per phase.

---

## Phase 0 — Project setup (5 tasks)

### Task 0.1: Create feature branch and capture baseline

**Files:** none (git operations)

**Step 1:** Create branch
```bash
cd "/c/Users/Aaron/omniscient website/omniscientai"
git checkout -b feat/v2-redesign
```

**Step 2:** Capture Lighthouse baseline for 4 key pages (Home, Services, Workshops, Book). Save as `docs/plans/baselines/lighthouse-pre-redesign.md` — a table of Performance / Accessibility / Best Practices / SEO scores per URL. Use Chrome DevTools Lighthouse tab or `lighthouse` CLI.

**Step 3:** Commit baseline
```bash
git add docs/plans/baselines/
git commit -m "docs: capture pre-redesign Lighthouse baseline"
```

### Task 0.2: Extract design system assets

**Files:**
- Create: `client/public/brand/logo-brain-stacked.png`
- Create: `client/public/brand/logo-horizontal-with-graphic.png`
- Create: `client/public/brand/logo-mark-circle.png`
- Create: `client/public/brand/brand-graphic-circles.png`
- Create: `client/public/brand/brand-graphic-horizontal.png`

**Step 1:** Extract design system zip to `/tmp/omniscient-ds/` (or reuse existing extraction).
**Step 2:** Copy 5 PNGs from `/tmp/omniscient-ds/assets/` to `client/public/brand/`.
**Step 3:** Verify files load at `http://localhost:3000/brand/logo-mark-circle.png` (start dev server if not running).
**Step 4:** Commit
```bash
git add client/public/brand/
git commit -m "assets: add Omniscient brand graphics and logos"
```

### Task 0.3: Install design system reference

**Files:**
- Create: `docs/design-system/README.md` (copy from design system zip)
- Create: `docs/design-system/colors_and_type.css` (copy — reference only; not imported)
- Create: `docs/design-system/ui-kit/` (copy of `ui_kits/website/` from zip — reference for porting)

**Step 1:** Copy design system docs into repo for offline reference
**Step 2:** Commit
```bash
git add docs/design-system/
git commit -m "docs: include Omniscient design system reference"
```

### Task 0.4: Add env flag to Vite config

**Files:**
- Modify: `client/.env.local` (create if missing)
- Modify: `client/.env.example`

**Step 1:** Add to `.env.example`:
```
VITE_USE_V2=false
```

**Step 2:** Add to `.env.local` (gitignored):
```
VITE_USE_V2=false
```

**Step 3:** Commit example only
```bash
git add client/.env.example
git commit -m "config: add VITE_USE_V2 env flag"
```

### Task 0.5: Create folder scaffolding

**Files:**
- Create: `client/src/styles/.gitkeep`
- Create: `client/src/pages-v2/.gitkeep`
- Create: `client/src/components-v2/brand/.gitkeep`
- Create: `client/src/components-v2/layout/.gitkeep`
- Create: `client/src/components-v2/ui/.gitkeep`
- Create: `client/src/components-v2/sections/.gitkeep`
- Create: `client/src/lib/.gitkeep` (if not present)

**Step 1:** Create empty directories via `.gitkeep` files.
**Step 2:** Commit
```bash
git add client/src/{styles,pages-v2,components-v2,lib}
git commit -m "scaffold: create v2 folder structure"
```

---

## Phase 1 — Design tokens & foundations (6 tasks)

### Task 1.1: Port colors_and_type.css to omniscient.css (scoped to .v2)

**Files:**
- Create: `client/src/styles/omniscient.css`

**Step 1:** Write the full token file. Start from `docs/design-system/colors_and_type.css` (already copied in Task 0.3). Modify the `:root` selector to `.v2` so tokens scope correctly.

```css
/* client/src/styles/omniscient.css */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

.v2 {
  /* Core tri-tone */
  --ink: #0F1115;
  --blue: #2F7BFF;
  --blue-deep: #1C4FD6;
  --blue-glow: #7AA8FF;
  --paper: #FFFFFF;
  --paper-2: #F4F6F9;
  --line: #E4E7EC;

  /* Full ink/blue/paper scales — copy from colors_and_type.css */
  --ink-900: #0F1115;
  --ink-800: #161A20;
  --ink-700: #1E232B;
  --ink-600: #2A2F37;
  --ink-500: #3D434D;
  --ink-400: #5B6270;
  --ink-300: #8A909C;
  --ink-200: #BEC3CC;
  --ink-100: #E4E7EC;

  --blue-600: #2567E8;
  --blue-500: #2F7BFF;
  --blue-400: #5693FF;
  --blue-300: #7AA8FF;
  --blue-200: #B8CFFF;
  --blue-100: #E6EEFF;

  --paper-50: #FAFBFC;
  --paper-100: #F4F6F9;

  /* Semantic (product UI only) */
  --success: #1EA97C;
  --warn: #E8A23A;
  --danger: #D94B4B;

  /* Semantic roles */
  --fg-1: var(--ink-900);
  --fg-2: var(--ink-600);
  --fg-3: var(--ink-400);
  --fg-inverse: var(--paper);
  --bg-1: var(--paper);
  --bg-2: var(--paper-100);
  --bg-inverse: var(--ink-900);
  --accent: var(--blue);
  --accent-fg: var(--paper);
  --focus-ring: var(--blue-300);

  /* Type */
  --font-display: 'Inter', 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif;
  --font-text:    'Inter', 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif;
  --font-mono:    'JetBrains Mono', ui-monospace, 'SF Mono', Menlo, monospace;

  --type-hero:       clamp(48px, 7vw, 96px);
  --type-h1:         56px;
  --type-h2:         36px;
  --type-h3:         22px;
  --type-h4:         18px;
  --type-body:       17px;
  --type-body-sm:    15px;
  --type-small:      14px;
  --type-micro:      12px;

  /* Spacing (4pt base) */
  --space-1: 4px;   --space-2: 8px;   --space-3: 12px;
  --space-4: 16px;  --space-5: 24px;  --space-6: 32px;
  --space-7: 48px;  --space-8: 64px;  --space-9: 96px;  --space-10: 128px;

  --container: 1240px;

  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
  --radius-xl: 12px;
  --radius-pill: 999px;

  --shadow-1: 0 1px 2px rgb(15 17 21 / 0.06), 0 1px 1px rgb(15 17 21 / 0.04);
  --shadow-2: 0 10px 24px rgb(15 17 21 / 0.08), 0 2px 6px rgb(15 17 21 / 0.06);

  --ease-brand: cubic-bezier(0.2, 0.9, 0.2, 1);
  --dur-fast: 120ms;
  --dur-base: 180ms;
  --dur-slow: 280ms;

  /* Set element defaults when .v2 is the canvas */
  background: var(--bg-1);
  color: var(--fg-1);
  font-family: var(--font-text);
  font-size: var(--type-body);
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
}

/* Base element styling under .v2 */
.v2 h1, .v2 h2, .v2 h3, .v2 h4, .v2 h5 {
  font-family: var(--font-display);
  color: var(--fg-1);
  margin: 0 0 var(--space-4);
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.1;
  text-wrap: pretty;
}
.v2 h1 { font-size: var(--type-h1); letter-spacing: -0.025em; line-height: 1.05; }
.v2 h2 { font-size: var(--type-h2); }
.v2 h3 { font-size: var(--type-h3); font-weight: 600; }
.v2 h4 { font-size: var(--type-h4); font-weight: 600; letter-spacing: 0; }

.v2 p { margin: 0 0 var(--space-4); color: var(--fg-2); }

.v2 code, .v2 pre, .v2 .mono { font-family: var(--font-mono); font-size: 0.92em; }

/* Utility classes */
.v2 .eyebrow {
  font-size: var(--type-micro);
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--fg-3);
}
.v2 .display {
  font-size: var(--type-hero);
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 0.95;
}
.v2 .lede {
  font-size: 20px;
  line-height: 1.45;
  color: var(--fg-2);
}
.v2 .mono-badge {
  font-family: var(--font-mono);
  font-size: 12px;
  padding: 2px 6px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  color: var(--fg-2);
  display: inline-block;
}

/* Ink section — flip canvas */
.v2 .ink-section {
  background: var(--bg-inverse);
  color: var(--fg-inverse);
}
.v2 .ink-section h1, .v2 .ink-section h2, .v2 .ink-section h3, .v2 .ink-section h4 { color: var(--paper); }
.v2 .ink-section p { color: color-mix(in oklab, var(--paper) 82%, transparent); }
.v2 .ink-section .eyebrow { color: color-mix(in oklab, var(--paper) 64%, transparent); }

/* Focus */
.v2 :focus-visible {
  outline: 2px solid var(--focus-ring);
  outline-offset: 2px;
  border-radius: 2px;
}

/* Selection */
.v2 ::selection {
  background: var(--blue);
  color: var(--paper);
}
```

**Step 2:** Import the file in `main.tsx` AFTER the existing `index.css`:

```tsx
import './index.css';
import './styles/omniscient.css';
```

**Step 3:** Verify no visual regression on current site. Open `localhost:3000` — old pages should look identical because `.v2` class is never applied yet.

**Step 4:** Commit
```bash
git add client/src/styles/omniscient.css client/src/main.tsx
git commit -m "tokens: add scoped Omniscient v2 design tokens"
```

### Task 1.2: Extend Tailwind @theme with v2 token aliases

**Files:**
- Modify: `client/src/index.css` (add to existing `@theme inline` block)

**Step 1:** Append to the existing `@theme inline { ... }` block:

```css
  /* Omniscient v2 — Tailwind utility aliases */
  --color-ink: var(--ink, #0F1115);
  --color-ink-2: var(--ink-600, #2A2F37);
  --color-ink-3: var(--ink-400, #5B6270);
  --color-blue: var(--blue, #2F7BFF);
  --color-blue-deep: var(--blue-deep, #1C4FD6);
  --color-blue-glow: var(--blue-glow, #7AA8FF);
  --color-paper: var(--paper, #FFFFFF);
  --color-paper-2: var(--paper-2, #F4F6F9);
  --color-line: var(--line, #E4E7EC);
```

The `var(--token, fallback)` pattern means Tailwind utilities like `bg-paper` default to white OUTSIDE `.v2` scope, but correctly resolve to the scoped value inside.

**Step 2:** Verify utilities resolve. Create a throwaway test:
```tsx
<div className="v2"><div className="bg-paper text-ink p-4">test</div></div>
```
Expected: white bg, near-black text.

**Step 3:** Commit
```bash
git add client/src/index.css
git commit -m "tokens: expose v2 tokens to Tailwind utilities"
```

### Task 1.3: Create theme scope helper

**Files:**
- Create: `client/src/lib/theme-v2.ts`

**Step 1:** Write helper
```ts
// client/src/lib/theme-v2.ts
export const USE_V2 = import.meta.env.VITE_USE_V2 === 'true';

export const V2_SCOPE_CLASS = 'v2';

export function withV2Scope(className?: string): string {
  return [V2_SCOPE_CLASS, className].filter(Boolean).join(' ');
}
```

**Step 2:** Commit
```bash
git add client/src/lib/theme-v2.ts
git commit -m "lib: add v2 scope helper"
```

### Task 1.4: Update favicon and manifest for new brand

**Files:**
- Modify: `client/public/favicon.ico` (or replace with generated multi-size)
- Modify: `client/public/manifest.json` (if exists)
- Modify: `client/index.html`

**Step 1:** Generate favicons from `logo-mark-circle.png`. Use [realfavicongenerator.net](https://realfavicongenerator.net/) or `sharp` CLI. Output at least:
- `favicon.ico` (16, 32, 48 multi-size)
- `apple-touch-icon.png` (180×180)
- `icon-512.png` (512×512)

Place all in `client/public/`.

**Step 2:** Update `client/index.html` `<head>`:
```html
<link rel="icon" type="image/x-icon" href="/favicon.ico" />
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
<meta name="theme-color" content="#0F1115" />
```

**Step 3:** If `manifest.json` exists, update `theme_color` to `#0F1115` and icons to new paths.

**Step 4:** Commit
```bash
git add client/public/ client/index.html
git commit -m "brand: update favicon and theme color for v2"
```

### Task 1.5: Create token showcase page (visual verification)

**Files:**
- Create: `client/src/pages-v2/_TokenShowcase.tsx`

**Step 1:** Build a page that renders every token visually. Not in router yet — will be accessed via ComponentShowcase later. Structure:
- Color swatches grid (ink / paper / blue scales with hex labels)
- Type scale (hero → micro, each labeled with size)
- Spacing scale (4px → 128px visual bars)
- Radius scale (4 → 12px boxes)
- Shadows (two shadow boxes labeled)

Reference `docs/design-system/ui-kit/index.html` for layout ideas.

**Step 2:** Commit
```bash
git add client/src/pages-v2/_TokenShowcase.tsx
git commit -m "v2: add token showcase page"
```

### Task 1.6: Router scaffolding (no routes yet)

**Files:**
- Modify: `client/src/App.tsx`
- Create: `client/src/pages-v2/V2Routes.tsx`
- Create: `client/src/pages-v2/LegacyRoutes.tsx`

**Step 1:** Extract existing route configuration from `App.tsx` into `LegacyRoutes.tsx` (copy all existing `<Route>` entries).

**Step 2:** Create empty `V2Routes.tsx`:
```tsx
import { Route } from 'wouter';
import { withV2Scope } from '@/lib/theme-v2';
import TokenShowcase from './_TokenShowcase';

export default function V2Routes() {
  return (
    <div className={withV2Scope()}>
      <Route path="/_tokens" component={TokenShowcase} />
      {/* Real routes added in later phases */}
    </div>
  );
}
```

**Step 3:** Modify `App.tsx`:
```tsx
import { USE_V2 } from '@/lib/theme-v2';
import V2Routes from '@/pages-v2/V2Routes';
import LegacyRoutes from '@/pages-v2/LegacyRoutes';

// In dev, always mount v2 at /v2/* for side-by-side preview
const IS_DEV = import.meta.env.DEV;

export default function App() {
  return USE_V2 ? <V2Routes /> : (
    <>
      <LegacyRoutes />
      {IS_DEV && <Route path="/_v2/:rest*" component={V2Routes} />}
    </>
  );
}
```

**Step 4:** Run dev server. Verify:
- `localhost:3000/` renders old Home
- `localhost:3000/_v2/_tokens` renders the token showcase

**Step 5:** Commit
```bash
git add client/src/App.tsx client/src/pages-v2/
git commit -m "router: scaffold v2 routes alongside legacy"
```

**Phase 1 gate:** Run `pnpm build`. Must succeed with zero TypeScript errors. Open `localhost:3000/_v2/_tokens` and eyeball the token showcase — compare every color, size, and spacing to `docs/design-system/colors_and_type.css`.

---

## Phase 2 — UI primitives (14 tasks)

Every primitive follows the same pattern: **component file + test file + export from barrel**. Tests use Vitest + React Testing Library (already set up in the project).

Common barrel file:
```tsx
// client/src/components-v2/ui/index.ts
export { Button } from './Button';
export { Card, FeaturedCard } from './Card';
/* ... append as components are built ... */
```

### Task 2.1: Button

**Files:**
- Create: `client/src/components-v2/ui/Button.tsx`
- Create: `client/src/components-v2/ui/Button.test.tsx`
- Modify: `client/src/components-v2/ui/index.ts`

**Step 1:** Write failing test
```tsx
// Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Button } from './Button';

describe('Button', () => {
  it('renders children', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Click</Button>);
    fireEvent.click(screen.getByRole('button'));
    expect(onClick).toHaveBeenCalledOnce();
  });

  it('applies primary variant classes by default', () => {
    render(<Button>Primary</Button>);
    expect(screen.getByRole('button').className).toMatch(/bg-blue/);
  });

  it('applies secondary variant classes', () => {
    render(<Button variant="secondary">Secondary</Button>);
    expect(screen.getByRole('button').className).toMatch(/border/);
  });

  it('renders arrow suffix when arrow prop is true', () => {
    render(<Button arrow>Go</Button>);
    expect(screen.getByRole('button').textContent).toContain('→');
  });

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
```

**Step 2:** Run test — expect fail (component doesn't exist)
```bash
cd client && pnpm test Button --run
```
Expected: `Cannot find module './Button'`

**Step 3:** Implement
```tsx
// Button.tsx
import { ButtonHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

type Variant = 'primary' | 'secondary' | 'ghost';
type Size = 'md' | 'lg';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  arrow?: boolean;
}

const base =
  'inline-flex items-center gap-2 font-semibold rounded-md ' +
  'transition-[transform,background-color,filter] duration-[var(--dur-base)] ease-[cubic-bezier(0.2,0.9,0.2,1)] ' +
  'hover:-translate-y-px active:translate-y-0 active:brightness-[.96] ' +
  'disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:translate-y-0 ' +
  'focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2 ' +
  'cursor-pointer';

const variants: Record<Variant, string> = {
  primary: 'bg-blue text-paper border-0 hover:bg-blue-deep',
  secondary: 'bg-paper text-ink border-[1.5px] border-ink hover:bg-paper-2',
  ghost: 'bg-transparent text-ink border-0 hover:bg-paper-2',
};

const sizes: Record<Size, string> = {
  md: 'px-4 py-2 text-[14px]',
  lg: 'px-[22px] py-[14px] text-[15px]',
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'lg', arrow, className, children, ...rest }, ref) => (
    <button
      ref={ref}
      className={cn(base, variants[variant], sizes[size], className)}
      {...rest}
    >
      {children}
      {arrow && <span aria-hidden>→</span>}
    </button>
  )
);
Button.displayName = 'Button';
```

**Step 4:** Run test — expect all pass
```bash
cd client && pnpm test Button --run
```
Expected: 6 passing.

**Step 5:** Add export to barrel
```ts
// index.ts
export { Button } from './Button';
```

**Step 6:** Commit
```bash
git add client/src/components-v2/ui/Button.{tsx,test.tsx} client/src/components-v2/ui/index.ts
git commit -m "ui: add Button primitive with variants"
```

### Task 2.2: Card and FeaturedCard

**Files:**
- Create: `client/src/components-v2/ui/Card.tsx`
- Create: `client/src/components-v2/ui/Card.test.tsx`
- Modify: `client/src/components-v2/ui/index.ts`

**Spec:**
- `Card`: flat, 1px `--line` border, 8px radius, `--paper` fill, `--shadow-1` on hover only (not default). Paper-2 background variant optional.
- `FeaturedCard`: ink background, paper text. Single variant used once per grid for emphasis.
- Both accept a `as` prop to render as `<a>` for linked cards; default `<div>`.

**Step 1:** Write test covering: default render, paper-2 variant, hover shadow class present, FeaturedCard inverts colors, `as="a"` renders anchor.
**Step 2:** Implement both components (`Card` and `FeaturedCard` in the same file).
**Step 3:** Run tests, export, commit
```bash
git commit -m "ui: add Card and FeaturedCard primitives"
```

### Task 2.3: Typography primitives (Eyebrow, Display, Lede, MonoBadge)

**Files:**
- Create: `client/src/components-v2/ui/Typography.tsx`
- Create: `client/src/components-v2/ui/Typography.test.tsx`
- Modify: `client/src/components-v2/ui/index.ts`

**Spec:** All four are thin wrappers over the utility classes in `omniscient.css`. Each accepts `className` and `as` (polymorphic component). Full implementations, not 4 separate files — one shared file because they're all tiny.

**Key test:** each component applies its utility class and passes through `className`.

**Step 1-6:** Standard TDD loop. Commit with message `ui: add typography primitives`.

### Task 2.4: CTALink

**Files:**
- Create: `client/src/components-v2/ui/CTALink.tsx`
- Create: `client/src/components-v2/ui/CTALink.test.tsx`

**Spec:** Anchor with underline-on-hover + `→` suffix. Used as the standard "Read the case study →" link pattern.

Props: `href`, `children`, optional `external` (if true, opens in new tab with proper rel).

**Step 1-6:** TDD loop. Commit with `ui: add CTALink`.

### Task 2.5: Input

**Files:**
- Create: `client/src/components-v2/ui/Input.tsx`
- Create: `client/src/components-v2/ui/Input.test.tsx`

**Spec:** `<input>` wrapper with label support. 6px radius. 1px `--line` border. Focus ring in `--blue-glow` (2px outline, 2px offset). Error state (red border + inline error message).

Props: standard input attrs, plus `label`, `error`, `hint`.

**Key tests:** renders label linked via htmlFor; shows error message when `error` prop present; wraps `aria-invalid` when error; focus ring visible class present.

**Step 1-6:** TDD loop. Commit with `ui: add Input primitive`.

### Task 2.6: Textarea

**Files:**
- Create: `client/src/components-v2/ui/Textarea.tsx`
- Create: `client/src/components-v2/ui/Textarea.test.tsx`

**Spec:** Same pattern as Input but `<textarea>`. Minimum 4 rows.

**Step 1-6:** TDD loop. Commit with `ui: add Textarea primitive`.

### Task 2.7: Select

**Files:**
- Create: `client/src/components-v2/ui/Select.tsx`
- Create: `client/src/components-v2/ui/Select.test.tsx`

**Spec:** Native `<select>` wrapper (not a custom listbox — we're prioritizing simplicity and a11y). Same visual treatment as Input: 6px radius, `--line` border, chevron icon on right. If we need a custom listbox later, it's a follow-up.

**Step 1-6:** TDD loop. Commit with `ui: add Select primitive`.

### Task 2.8: Slider

**Files:**
- Create: `client/src/components-v2/ui/Slider.tsx`
- Create: `client/src/components-v2/ui/Slider.test.tsx`

**Spec:** Native `<input type="range">` styled via cross-browser CSS. 6px track, `--ink-100` bg, `--blue` fill (via `background-image: linear-gradient`), 16px circular thumb with `--shadow-1`. Used in ROI Calculator.

Props: `min`, `max`, `step`, `value`, `onChange`, `label`, `valueDisplay` (controls how current value renders — e.g. `$1,000,000`).

**Key tests:** value clamped to min/max; onChange fires with correct value; keyboard arrows work (native); label+value render correctly.

**Step 1-6:** TDD loop. Commit with `ui: add Slider primitive`.

### Task 2.9: RadioCard

**Files:**
- Create: `client/src/components-v2/ui/RadioCard.tsx`
- Create: `client/src/components-v2/ui/RadioCard.test.tsx`

**Spec:** A Card-styled radio option for Quiz questions. Large tap target. Radio dot (native `<input type="radio">` visually hidden; custom disc indicator). Selected state: ink border instead of line, small blue dot.

Props: `name`, `value`, `label`, `description?`, `checked`, `onChange`.

**Step 1-6:** TDD loop. Commit with `ui: add RadioCard`.

### Task 2.10: CheckboxCard

**Files:**
- Create: `client/src/components-v2/ui/CheckboxCard.tsx`
- Create: `client/src/components-v2/ui/CheckboxCard.test.tsx`

**Spec:** Same as RadioCard but checkbox. Supports multi-select. Selected state: ink border, blue checkmark icon (Lucide `Check`).

**Step 1-6:** TDD loop. Commit with `ui: add CheckboxCard`.

### Task 2.11: Eyebrow, Display, Lede, MonoBadge exports sanity pass

**Note:** these are covered by Task 2.3. This placeholder task exists to remind the executor to verify the barrel export list is complete after Phase 2 and matches the design doc's Section 5.3.

**Action:** Open `client/src/components-v2/ui/index.ts`. Verify exports:
- Button
- Card, FeaturedCard
- Eyebrow, Display, Lede, MonoBadge
- CTALink
- Input, Textarea, Select
- Slider, RadioCard, CheckboxCard

If anything missing, add. No commit needed unless changes.

### Task 2.12: Phase 2 gate — visual sanity test via _TokenShowcase

**Step 1:** Extend `_TokenShowcase.tsx` to render one instance of every primitive built in Phase 2. Import from the barrel.

**Step 2:** Run dev server. Visit `localhost:3000/_v2/_tokens`. Eyeball check:
- Buttons: primary blue / secondary ink outline / ghost; hover lifts 1px; arrow displays
- Cards: flat 8px border; FeaturedCard ink-dark
- Typography classes render at spec sizes
- Inputs: focus ring shows in `--blue-glow`
- Slider: blue fill bar, circular thumb
- RadioCard/CheckboxCard: selected state visibly distinct

**Step 3:** Run full test suite
```bash
cd client && pnpm test --run
```
Expected: all passing.

**Step 4:** Run build
```bash
cd client && pnpm build
```
Expected: success, zero TS errors.

**Step 5:** Commit
```bash
git add client/src/pages-v2/_TokenShowcase.tsx
git commit -m "showcase: render all Phase 2 primitives"
```

---

## Phase 3 — Layout layer (6 tasks)

### Task 3.1: Container

**Files:** `client/src/components-v2/layout/Container.tsx` (+ test)

**Spec:** Max-width 1240px, centered, horizontal padding 24px mobile / 72px desktop. Polymorphic `as` prop (default `<div>`). Replaces all inline `max-w-*` usages in v2.

**Step 1-6:** TDD loop. Commit `layout: add Container`.

### Task 3.2: Section

**Files:** `client/src/components-v2/layout/Section.tsx` (+ test)

**Spec:** Default paper section with vertical rhythm — 96px top/bottom desktop, 48px mobile. Wraps a `Container` unless `fluid` prop is true. Semantic `<section>` by default.

Props: `eyebrow?`, `title?`, `lede?`, `children`, `fluid?`, `tone` (`paper` | `paper-2` default `paper`).

**Step 1-6:** TDD loop. Commit `layout: add Section`.

### Task 3.3: InkSection

**Files:** `client/src/components-v2/layout/InkSection.tsx` (+ test)

**Spec:** Flip-to-ink variant. Applies `.ink-section` class (defined in `omniscient.css`). Inverts token appearance. Used at most once per long page for pacing.

**Design rule check:** Add a runtime dev-only warning if more than one `InkSection` renders on the same page (via a context or counter). Optional — flag to executor if implementing this check feels like premature optimization, skip it.

**Step 1-6:** TDD loop. Commit `layout: add InkSection`.

### Task 3.4: Nav

**Files:** `client/src/components-v2/layout/Nav.tsx` (+ test)
**Reference:** `docs/design-system/ui-kit/components/Nav.jsx` (starting-point template)

**Spec:**
- Sticky top-0, `z-index: 50`
- Background: `rgba(255,255,255,0.72)`, `backdrop-filter: saturate(1.2) blur(14px)`
- Bottom: `1px solid var(--line)`
- Left: Logo (`mark-circle.png` + "Omniscient AI" wordmark, 18px/700)
- Center: 4 links — Workshops / Services / Case studies / About
- Right: Primary Button "Book a call →"
- Mobile (<768px): collapse to hamburger. Open state is a full-screen `.ink-section` overlay with the same 4 links + CTA stacked vertically, text-2xl.

**Step 1:** Write tests covering desktop layout, mobile hamburger toggle, open/close.
**Step 2-5:** Implement. Use Lucide `Menu` / `X` icons.
**Step 6:** Commit `layout: add Nav with mobile drawer`.

### Task 3.5: Footer

**Files:** `client/src/components-v2/layout/Footer.tsx` (+ test)
**Reference:** `docs/design-system/ui-kit/components/Footer.jsx`

**Spec:** 3-column grid on desktop, stacked on mobile.
- Col 1: `logo-horizontal-with-graphic.png` (200px wide) + short company tagline
- Col 2: Nav links repeated + legal (Privacy, Terms)
- Col 3: Contact — email, Melbourne address, socials (LinkedIn + X, Lucide icons, ink color)
- Bottom row: copyright + `TaglineBar` component rendered micro-size

**Step 1-6:** TDD loop. Commit `layout: add Footer`.

### Task 3.6: Layout wrapper

**Files:** `client/src/components-v2/layout/Layout.tsx` (+ test)

**Spec:** Wraps all v2 pages. Injects `Nav` at top, `Footer` at bottom, `main` in middle. Accepts `children`. Adds a skip-to-content link above Nav for a11y.

Special case: Book page uses `Layout hideFooter` prop because the booking wizard uses the full viewport.

**Step 1-6:** TDD loop. Commit `layout: add Layout wrapper`.

**Phase 3 gate:** Extend `_TokenShowcase` to render inside a `Layout` wrapper. Verify Nav renders sticky, Footer anchors at bottom, sticky blur works over content that scrolls.

---

## Phase 4 — Brand layer (3 tasks)

### Task 4.1: Logo

**Files:** `client/src/components-v2/brand/Logo.tsx` (+ test)

**Spec:** Renders one of 3 PNG variants based on `variant` prop:
- `stacked` → `logo-brain-stacked.png`
- `horizontal` → `logo-horizontal-with-graphic.png`
- `mark` → `logo-mark-circle.png`

Props: `variant`, `width` (auto-scales height), `alt` (default "Omniscient AI").

**Step 1-6:** TDD loop. Commit `brand: add Logo component`.

### Task 4.2: BrainGraphic

**Files:** `client/src/components-v2/brand/BrainGraphic.tsx` (+ test)

**Spec:** Decorative illustration placer.
- Props: `variant` (`circles` | `horizontal`), `size` (`hero` | `section` | `corner`), `position` (`left` | `right`).
- Rendered as `<img>` with appropriate sizing. `aria-hidden="true"` because it's decorative (semantic meaning is in the adjacent copy).

| Size | Width |
|------|-------|
| hero | 40vw max 540px |
| section | 25vw max 320px |
| corner | 15vw max 200px |

**Step 1-6:** TDD loop. Commit `brand: add BrainGraphic component`.

### Task 4.3: TaglineBar

**Files:** `client/src/components-v2/brand/TaglineBar.tsx` (+ test)

**Spec:** Renders the `INTELLIGENCE // CONNECTIVITY // INNOVATION` tagline as an eyebrow-styled row. Max 1 per page.
- Three UPPERCASE words separated by ` // ` (with spaces)
- Tracked 0.14em
- 12px / 600 / `--ink-3`
- Centered or left-aligned via `align` prop

**Step 1-6:** TDD loop. Commit `brand: add TaglineBar`.

**Phase 4 gate:** Render all 3 brand components in `_TokenShowcase`. Verify Logo variants load, BrainGraphic appears at 3 sizes, Tagline tracked correctly.

---

## Phase 5 — Section patterns (14 tasks)

Each section is a composable block. Pages pick 4-7. Each task follows the same shape: build section + minimal smoke test + add to showcase.

### Task 5.1: HeroSplit

**Files:** `client/src/components-v2/sections/HeroSplit.tsx` (+ test)
**Reference:** `docs/design-system/ui-kit/components/Hero.jsx`

**Spec:** 55/45 grid — copy left, BrainGraphic right. On mobile, stacks graphic above copy.

Props:
- `eyebrow?: string` — typically the Tagline or a page eyebrow
- `title: ReactNode` — Display-sized headline
- `lede?: string`
- `primaryCta?: { label: string; href: string }`
- `secondaryCta?: { label: string; href: string }`
- `graphic?: 'circles' | 'horizontal'` (default `circles`)

**Step 1:** Smoke test (renders title, CTAs work).
**Step 2-5:** Implement.
**Step 6:** Commit `sections: add HeroSplit`.

### Task 5.2: HeroCentric

**Files:** `client/src/components-v2/sections/HeroCentric.tsx` (+ test)

**Spec:** Stacked, center-aligned. Eyebrow → Display title → Lede → CTAs. Optional narrow BrainGraphic below CTAs at `section` size.

Same props as HeroSplit minus the `graphic` placement.

**Step 1-6:** Commit `sections: add HeroCentric`.

### Task 5.3: PillarGrid

**Files:** `client/src/components-v2/sections/PillarGrid.tsx` (+ test)

**Spec:** 4-up responsive card grid. Each pillar: icon (Lucide) + H3 title + 2-3 sentence description + `CTALink` "Learn more →".

Props: `pillars: Array<{ icon: LucideIcon; title: string; description: string; href: string }>`, `eyebrow?`, `sectionTitle?`.

Default content seed for Home page (4 pillars):
1. **AI Training** (`GraduationCap`) — hands-on workshops for Melbourne SMEs, vendor-neutral.
2. **Health Technologies** (`Activity`) — [NEW copy needed]
3. **Defense Hardware & Software** (`Shield`) — [NEW copy needed]
4. **Agentic Ops** (`Bot`) — [NEW copy needed]

**Step 1-6:** Commit `sections: add PillarGrid`.

### Task 5.4: CaseGrid

**Files:** `client/src/components-v2/sections/CaseGrid.tsx` (+ test)

**Spec:** 3-up grid. First tile is `FeaturedCard` (ink), other two are `Card`. Each: eyebrow (industry), H3 title, 1-sentence result, `CTALink` "Read the case study →".

Props: `cases: Array<{ industry: string; title: string; outcome: string; href: string }>`, `eyebrow?`, `sectionTitle?`.

**Note:** If no real case studies exist at launch, Home calls this with 3 anonymized engagement summaries. Flag to executor.

**Step 1-6:** Commit `sections: add CaseGrid`.

### Task 5.5: WorkshopCardGrid

**Files:** `client/src/components-v2/sections/WorkshopCardGrid.tsx` (+ test)

**Spec:** 3-up (or grid of N). Each workshop card: image (from CMS/data), MonoBadge row (duration + format + price), H3 title, 2-sentence description, `Button` "Book this workshop →".

Data source: existing workshops data in the project (likely `client/src/data/workshops.ts` or similar — locate during Phase 5, adapt types if needed).

**Step 1-6:** Commit `sections: add WorkshopCardGrid`.

### Task 5.6: StepStack

**Files:** `client/src/components-v2/sections/StepStack.tsx` (+ test)

**Spec:** Numbered vertical list. Each step: large `01` mono numeral (left) + ink-line divider, then H3 title + body text. Used in Approach page (4-phase methodology) and Workshop Detail (module agenda).

Props: `steps: Array<{ title: string; body: string; duration?: string }>`, `eyebrow?`, `sectionTitle?`.

**Step 1-6:** Commit `sections: add StepStack`.

### Task 5.7: FAQAccordion

**Files:** `client/src/components-v2/sections/FAQAccordion.tsx` (+ test)

**Spec:** Vertical list. Each item: hairline `--line` top border, 24px padding, H4 title + `+`/`−` toggle icon right. Open state reveals body. Keyboard accessible (Enter/Space toggles).

Props: `items: Array<{ q: string; a: ReactNode }>`, `eyebrow?`, `sectionTitle?`.

Use `useState` for open item(s). Decide single-open vs multi-open: **single-open** (matches boutique feel).

**Step 1-6:** Commit `sections: add FAQAccordion`.

### Task 5.8: TestimonialStrip

**Files:** `client/src/components-v2/sections/TestimonialStrip.tsx` (+ test)

**Spec:** 3 horizontal quotes. Each: big `"` mark (decorative), quote body (20px/1.45), attribution (name, role, company) in MonoBadge style.

**Design rule check:** No star ratings (design doc explicitly forbids — "too consumer"). Tests should NOT include stars.

**Step 1-6:** Commit `sections: add TestimonialStrip`.

### Task 5.9: StatsRow

**Files:** `client/src/components-v2/sections/StatsRow.tsx` (+ test)

**Spec:** 4-column responsive row. Each stat: Display-sized numeral (use `Display` primitive, or custom 72px mono) + small label underneath. Can be on paper or ink background.

Props: `stats: Array<{ value: string; label: string }>`, `tone?: 'paper' | 'ink'`.

Current site stats: `50+` workshops, `12` industries, `4.9/5` satisfaction, `8hrs` saved per week. Port these.

**Step 1-6:** Commit `sections: add StatsRow`.

### Task 5.10: CTAStrip

**Files:** `client/src/components-v2/sections/CTAStrip.tsx` (+ test)

**Spec:** Book-a-call prompt. Two variants via `tone` prop:
- `paper`: centered headline + lede + primary `Button`
- `ink`: same but ink background, inverted

Used on nearly every page as the footer-preceding CTA.

**Step 1-6:** Commit `sections: add CTAStrip`.

### Task 5.11: BookingForm (multi-step wizard)

**Files:**
- Create: `client/src/components-v2/sections/BookingForm.tsx`
- Create: `client/src/components-v2/sections/BookingForm.test.tsx`
- Create: `client/src/components-v2/sections/BookingForm.types.ts`

**Spec:** 3-step wizard:
1. Service select (RadioCard per option)
2. Date + time picker (simple month grid + time slots; OR embed Calendly if that's the current mechanism — CHECK existing `Book.tsx`)
3. Contact form (name, email, company, notes)

Sticky summary sidebar (desktop): shows selections so far in a `Card` on `--paper-2`.

Submit → POST to the existing booking endpoint (check `client/src/pages/Book.tsx` for the current API).

**Step 1:** Write tests: step navigation (next / back), submit payload, validation errors on required fields, submit button disabled until current step valid.
**Step 2-5:** Implement.
**Step 6:** Commit `sections: add BookingForm wizard`.

### Task 5.12: ContactForm

**Files:** `client/src/components-v2/sections/ContactForm.tsx` (+ test)

**Spec:** Single-page form in a Card on `--paper-2` bg. Fields: name, email, company, enquiry type (Select), message (Textarea). Submits to existing contact endpoint.

**Step 1-6:** Commit `sections: add ContactForm`.

### Task 5.13: ArticleHeader

**Files:** `client/src/components-v2/sections/ArticleHeader.tsx` (+ test)

**Spec:** Long-form article top. Eyebrow (category) → Display title → Lede → MonoBadge row (byline name + read time + date).

Props: `category`, `title`, `lede?`, `author`, `readTime`, `publishDate`.

**Step 1-6:** Commit `sections: add ArticleHeader`.

### Task 5.14: ArticleBody

**Files:** `client/src/components-v2/sections/ArticleBody.tsx` (+ test)

**Spec:** Article content wrapper. Applies `max-w-[65ch]` for readable line length (65-75 char rule). Styles for nested h2, h3, p, ul, ol, blockquote, code, pre, img.

Props: `children` (rendered Markdown or raw JSX).

**Step 1-6:** Commit `sections: add ArticleBody`.

**Phase 5 gate:** Extend `_TokenShowcase` to render one example of every section pattern. Visual eyeball check. Run full test suite. Run build. Commit showcase update.

---

## Phase 6 — Component showcase consolidation (1 task)

### Task 6.1: Finalize ComponentShowcase page

**Files:**
- Rename: `client/src/pages-v2/_TokenShowcase.tsx` → `client/src/pages-v2/ComponentShowcase.tsx`
- Add route: `/_showcase` in `V2Routes.tsx` (dev-only — not in Nav)

**Spec:** The canonical visual-regression surface. Each section has a heading anchor. Structure:
1. Tokens (colors, type, spacing, radius, shadows)
2. UI primitives (every component from Phase 2)
3. Layout components (Container, Section, InkSection in situ)
4. Brand components (Logo, BrainGraphic, TaglineBar)
5. Section patterns (every section from Phase 5, one real-data example each)

**Action:** This page is already being built throughout Phases 2-5 via the "extend showcase" gate steps. Task 6.1 is consolidation — rename, add route, ensure all examples present, add anchors.

Commit: `showcase: finalize ComponentShowcase page`.

---

## Phase 7 — Marketing pages (10 tasks)

Each page task follows the pattern: compose sections from Phase 5, port copy from legacy page, write a smoke test (renders, key elements present, CTAs link correctly), add to `V2Routes`.

**Copy porting discipline for every page:**
1. Open legacy `client/src/pages/<Page>.tsx`
2. Extract copy strings (headlines, body, CTAs)
3. Fix casing (Title Case → sentence case for body/buttons)
4. Shorten where voice demands it (cut adverbs, lead with verb)
5. Reuse legacy copy wholesale unless it violates voice rules (see design doc §3.3)

### Task 7.1: Home

**Files:**
- Create: `client/src/pages-v2/Home.tsx`
- Create: `client/src/pages-v2/Home.test.tsx`
- Modify: `client/src/pages-v2/V2Routes.tsx` (add route)

**Composition (from design doc §6.1):**
```tsx
<Layout>
  <HeroSplit {...} />
  <TaglineBar />
  <PillarGrid {...} /> {/* 4 pillars — training + health + defense + agentic ops */}
  <InkSection> {/* "Why vendor-neutral" manifesto — NEW COPY NEEDED */} </InkSection>
  <WorkshopCardGrid workshops={flagshipWorkshops} />
  <CaseGrid cases={featuredCases} />
  <StatsRow stats={currentStats} />
  <TestimonialStrip testimonials={featuredTestimonials} />
  <CTAStrip tone="paper" />
</Layout>
```

**Step 1:** Port copy from legacy `Home.tsx`. Draft the 4 pillar descriptions and the InkSection manifesto. Flag to user any copy that's entirely new and needs approval before ship.
**Step 2:** Write smoke test: renders `<main>`, contains "Unleashing the power of intelligent connections" (or similar), primary CTA links to `/book`.
**Step 3:** Implement.
**Step 4:** Add route to `V2Routes.tsx` at path `/`.
**Step 5:** Run test + visit `localhost:3000/_v2/` to eyeball.
**Step 6:** Commit `pages: add v2 Home`.

### Task 7.2: Services (overview)

**Files:** `client/src/pages-v2/Services.tsx` (+ test); add route.

**Composition:**
- HeroCentric
- Services card grid (3-up) — each service: icon, H3, 2-line blurb, CTALink to detail
- PillarGrid (breadth signal)
- InkSection (approach overview)
- CTAStrip

Data source: existing `client/src/data/services.ts` (locate and adapt).

**Step 1-6:** Commit `pages: add v2 Services overview`.

### Task 7.3: Service Detail

**Files:** `client/src/pages-v2/ServiceDetail.tsx` (+ test); add route `/services/:slug`.

**Composition:**
- HeroSplit with BrainGraphic horizontal
- "What you'll get" checklist (2-column)
- StepStack (engagement phases)
- Pricing block — MonoBadges for rates + "from" pricing
- FAQAccordion
- CTAStrip ink variant

**Step 1-6:** Commit `pages: add v2 Service Detail`.

### Task 7.4: Industries (overview)

**Files:** `client/src/pages-v2/Industries.tsx` (+ test); add route.

**Composition:**
- HeroCentric
- 4-up industry card grid (each: icon, H3, stat, blurb, CTALink)
- CaseGrid (industry-tagged cases)
- CTAStrip

**Step 1-6:** Commit `pages: add v2 Industries`.

### Task 7.5: Industry Detail

**Files:** `client/src/pages-v2/IndustryDetail.tsx` (+ test); add route `/industries/:slug`.

**Composition:**
- HeroSplit
- Use-case list (3-up Cards)
- FeaturedCard (flagship case study)
- WorkshopCardGrid (filtered by industry)
- CTAStrip

**Step 1-6:** Commit `pages: add v2 Industry Detail`.

### Task 7.6: Workshops (overview)

**Files:** `client/src/pages-v2/Workshops.tsx` (+ test); add route.

**Composition:**
- HeroCentric
- WorkshopCardGrid (all workshops)
- Custom Workshop CTA Card (inline)
- TestimonialStrip
- CTAStrip

**Step 1-6:** Commit `pages: add v2 Workshops overview`.

### Task 7.7: Workshop Detail

**Files:** `client/src/pages-v2/WorkshopDetail.tsx` (+ test); add route `/workshops/:slug`.

**Composition:** (per design doc — heaviest page)
- HeroSplit — pricing, duration, format as MonoBadges; main CTA "Book this workshop →"
- "Who it's for" checklist (2-column, Card)
- 4-module agenda via StepStack (with durations)
- Outcomes (numbered list with Lucide icons)
- FAQAccordion
- **Sticky sidebar:** BookingForm wizard on desktop (column 4); on mobile, a fixed bottom bar "Book now" button that opens BookingForm as full-screen wizard

**Step 1:** Study legacy `client/src/pages/WorkshopDetail.tsx` thoroughly — this page has the most dynamic data.
**Step 2-6:** Commit `pages: add v2 Workshop Detail`.

### Task 7.8: About

**Files:** `client/src/pages-v2/About.tsx` (+ test); add route.

**Composition:**
- HeroCentric
- Story block (long-form paragraph on paper)
- FeaturedCard grid (4 values)
- Named-practitioner bios (3-up Cards) — **NEW copy needed**
- InkSection (manifesto snippet)
- CTAStrip

**Flag to user:** About page needs named-practitioner data. Block at bio step until provided.

**Step 1-6:** Commit `pages: add v2 About`.

### Task 7.9: Approach

**Files:** `client/src/pages-v2/Approach.tsx` (+ test); add route.

**Composition:**
- HeroCentric
- StepStack (4-phase methodology — Discover / Design / Deliver / Embed)
- Principles grid (6-up mini Cards)
- CTAStrip

**Step 1-6:** Commit `pages: add v2 Approach`.

### Task 7.10: Contact

**Files:** `client/src/pages-v2/Contact.tsx` (+ test); add route.

**Composition:**
- HeroCentric narrow
- 2-column: ContactForm left, contact details sidebar right (email, Melbourne address, business hours MonoBadge, socials)

**Step 1-6:** Commit `pages: add v2 Contact`.

**Phase 7 gate:** Visit every new page at `localhost:3000/_v2/<path>`. Full QA checklist per design doc §8.1 for each. Commit any fixes.

---

## Phase 8 — Conversion pages (2 tasks)

### Task 8.1: Book

**Files:** `client/src/pages-v2/Book.tsx` (+ test); add route `/book`.

**Composition:**
- `<Layout hideFooter>` — minimal chrome
- BookingForm wizard centered (full-width on mobile, constrained on desktop with sticky summary sidebar)

Reuse BookingForm from Task 5.11. Book page is a thin wrapper.

**Step 1-6:** Commit `pages: add v2 Book`.

### Task 8.2: Custom Workshop

**Files:** `client/src/pages-v2/CustomWorkshop.tsx` (+ test); add route.

**Composition:**
- HeroCentric
- Requirements form (Card on paper-2) — fields: org size, industry, goals, preferred format, budget range
- "How we scope" StepStack
- CTAStrip

**Step 1-6:** Commit `pages: add v2 Custom Workshop`.

---

## Phase 9 — Content pages (2 tasks)

### Task 9.1: Insights (index)

**Files:** `client/src/pages-v2/Insights.tsx` (+ test); add route.

**Composition:**
- HeroCentric
- Category filter pills (horizontal row, pill-style buttons)
- Featured article FeaturedCard (most recent)
- Article grid (3-up Cards — each: image, category eyebrow, title, read-time MonoBadge, CTALink)

**Step 1-6:** Commit `pages: add v2 Insights`.

### Task 9.2: Insight Article

**Files:** `client/src/pages-v2/InsightArticle.tsx` (+ test); add route `/insights/:slug`.

**Composition:**
- ArticleHeader
- ArticleBody
- Author bio Card at bottom
- Related articles grid (3-up)
- CTAStrip

**Step 1-6:** Commit `pages: add v2 Insight Article`.

---

## Phase 10 — Tool pages (2 tasks)

These are classified as "product UI" — semantic accents and blue-dot grid backgrounds permitted.

### Task 10.1: AI Readiness Quiz

**Files:** `client/src/pages-v2/AIReadinessQuiz.tsx` (+ test); add route `/quiz`.

**Composition:**
- `<Layout>`
- HeroCentric intro — eyebrow, Display title, lede, Button "Start assessment →"
- Wizard: progress bar (thin, `--blue` fill on `--line` track) + current step MonoBadge + RadioCard/CheckboxCard grid per question
- Result screen: Display-sized score + category breakdown (StatsRow style) + recommendations + Button "Book a diagnostic call →"

Data source: existing quiz questions from `client/src/pages/AIReadinessQuiz.tsx`. Port as-is; adjust UI to new aesthetic.

**Step 1:** Port quiz question data unchanged.
**Step 2-5:** Build new UI on top of existing logic.
**Step 6:** Commit `pages: add v2 AI Readiness Quiz`.

### Task 10.2: ROI Calculator

**Files:** `client/src/pages-v2/ROICalculator.tsx` (+ test); add route `/roi-calculator`.

**Composition:**
- `<Layout>`
- HeroCentric narrow intro
- 2-column: inputs (Card) left, results (Card) right
  - Inputs: Select (industry), Slider (team size), Slider (hours/week on tasks), Slider (hourly rate)
  - Results: live-computed savings in Display size, MonoBadge breakdown (hours saved / annual cost / payback period)
- Below results: CTAStrip "Book a scoping call →"

Port computation logic from legacy `ROICalculator.tsx` unchanged.

**Step 1-6:** Commit `pages: add v2 ROI Calculator`.

**Phase 10 gate:** End-to-end test both tools. Quiz: complete full flow, verify score calculation matches legacy. ROI: verify computation outputs match legacy for same inputs.

---

## Phase 11 — Legal & utility (3 tasks)

### Task 11.1: Privacy Policy + Terms (shared template)

**Files:**
- Create: `client/src/pages-v2/PrivacyPolicy.tsx` (+ test)
- Create: `client/src/pages-v2/Terms.tsx` (+ test)
- Add routes `/privacy` and `/terms` to V2Routes

**Spec:** Both pages use the same template — HeroCentric narrow + ArticleBody with the legal content as nested h2/h3 sections + last-updated MonoBadge.

Port content verbatim from legacy `PrivacyPolicy.tsx` / `Terms.tsx`. Legal text is not rewritten — it's ported exactly.

**Step 1-6:** Commit `pages: add v2 Privacy and Terms`.

### Task 11.2: NotFound

**Files:** `client/src/pages-v2/NotFound.tsx` (+ test); add fallback route.

**Spec:** Centered layout. Display-sized "404" + lede "Page not found. The page you're looking for doesn't exist or has moved." + two Buttons — "Back to home →" and "Browse workshops →". Corner BrainGraphic circles variant.

**Step 1-6:** Commit `pages: add v2 NotFound`.

### Task 11.3: ComponentShowcase (dev-only route)

**Files:** already built in Phase 6. Add route at `/_showcase` in V2Routes, guarded by `import.meta.env.DEV`.

**Step 1:** Add conditional route.
**Step 2:** Commit `pages: expose ComponentShowcase at /_showcase in dev`.

---

## Phase 12 — Router flip & cleanup (6 tasks)

### Task 12.1: Add platform-level redirects for removed tools

**Files:**
- Modify: `render.yaml` and/or `app.yaml` (whichever is the active deploy config — check `C:\Users\Aaron\omniscient website\omniscientai\` root)

**Step 1:** Add 301 redirects:
- `/document-analyser` → `/services`
- `/voice-consultant` → `/services`
- `/playground` → `/`

**Step 2:** If using Render: add `redirects` block in `render.yaml`. If using Cloud Run: add rewrites via the static-site config.

**Step 3:** Deploy to staging, verify `curl -I https://staging-url/document-analyser` returns 301 with `Location: /services`.

**Step 4:** Commit `deploy: add 301 redirects for removed tool URLs`.

### Task 12.2: Regenerate sitemap

**Files:**
- Modify: `client/public/sitemap.xml` (or sitemap generator script)

**Step 1:** Regenerate for the 20 v2 URLs only. Remove `/document-analyser`, `/voice-consultant`, `/playground`.

**Step 2:** Commit `seo: regenerate sitemap for v2 URLs`.

### Task 12.3: Full QA pass on staging

**Step 1:** Deploy current branch to staging with `VITE_USE_V2=true`.
**Step 2:** For each of 20 pages, run the Phase 8.1-style checklist from design doc §8.1. Record pass/fail in `docs/plans/qa-log.md`.
**Step 3:** Fix any failures.
**Step 4:** Lighthouse pass on Home, Services, Workshops, Book — each ≥ 90.
**Step 5:** Cross-browser smoke (Chrome, Safari, Firefox, Edge; iOS Safari). Document any regressions.
**Step 6:** Forms end-to-end: submit Contact, Book (3 steps), Custom Workshop, Quiz, ROI Calculator — verify data arrives.

**Step 7:** Commit QA log
```bash
git add docs/plans/qa-log.md
git commit -m "docs: record v2 pre-flip QA pass"
```

### Task 12.4: Production flip

**Step 1:** Rehearse rollback: flip `VITE_USE_V2=false` on staging, redeploy, verify old site renders, flip back.

**Step 2:** Pre-flip announcement (if applicable — internal Slack, team notification).

**Step 3:** Set `VITE_USE_V2=true` in production environment. Deploy.

**Step 4:** Smoke-test production for 30 minutes:
- Home loads, Book flow completes, Contact form submits
- Sentry dashboard — error rate baseline
- GA live view — traffic unaffected

**Step 5:** If all clear: announce flip complete. If regressions: flip env flag back, investigate.

**Step 6:** Commit any production-specific config
```bash
git commit --allow-empty -m "release: flip production to v2 redesign"
```

### Task 12.5: 24h stability watch

**Step 1:** Monitor for 24h:
- Sentry error rate vs 7-day median (alarm: +50%)
- 404 rate (alarm: +20%)
- Form submission volume (alarm: -25%)
- GA bounce rate (alarm: +15%)

**Step 2:** If any alarm fires, diagnose. If structural, rollback via env flag.
**Step 3:** After 24h clean: proceed to cleanup.

### Task 12.6: Legacy code cleanup (PR)

**Files (large delete):**
- Delete: `client/src/pages/*` (all files)
- Rename: `client/src/pages-v2/*` → `client/src/pages/*`
- Delete: dead `client/src/components/*` (keep only: `ui/` (shadcn base primitives if still used), `SEO.tsx`, `ErrorBoundary.tsx`, `Map.tsx` — audit during this task)
- Rename: `client/src/components-v2/*` → `client/src/components/*`
- Delete: dark-theme tokens from `client/src/index.css` (the `@theme inline` v2 aliases become the canonical tokens)
- Rename: `.v2` class wrapper — remove the class from `Layout`, remove the scoping from `omniscient.css` so tokens apply at `:root`
- Delete: `client/src/lib/theme-v2.ts` (no longer needed post-unification)
- Delete: `VITE_USE_V2` from `.env` files and `App.tsx` branching

**Step 1:** Create a separate branch `feat/v2-cleanup` off main (post-flip main).
**Step 2:** Execute the deletes and renames.
**Step 3:** Fix imports (rename `components-v2` → `components` everywhere).
**Step 4:** Run build + all tests — expect zero regressions (visually identical).
**Step 5:** Open PR. Expect a LOT of `-` lines. Reviewer checks for zero visual diff on sampled pages.
**Step 6:** Merge after review. Commit message: `refactor: consolidate v2 → v1, remove dark theme legacy`.

---

## Phase 13 — Ship gate & post-launch (5 tasks)

### Task 13.1: OG image + social preview

**Files:** `client/public/og-default.png` (1200×630)

**Step 1:** Compose OG image — ink background + `brand-graphic-horizontal.png` on right + paper-colored text "Vendor-neutral AI for Melbourne SMEs" + small wordmark.
**Step 2:** Verify `<meta property="og:image">` in `SEO.tsx` points to `/og-default.png`.
**Step 3:** Test on [metatags.io](https://metatags.io/) and Twitter Card validator.
**Step 4:** Commit `brand: add OG share image`.

### Task 13.2: Search Console update

**Step 1:** Submit new sitemap to Google Search Console.
**Step 2:** Request re-index of 20 primary URLs.
**Step 3:** Verify no URL errors in the next 48h.

### Task 13.3: Performance polish

Only if Lighthouse <90 anywhere:

**Step 1:** Convert brand PNGs to WebP (keep PNG as fallback via `<picture>`). Use `sharp` or `imagemin`.
**Step 2:** Preload Home BrainGraphic in `<head>`.
**Step 3:** Self-host Inter + JetBrains Mono if Font Observer shows > 100ms FOUT.
**Step 4:** Verify Lighthouse ≥ 90. Commit `perf: WebP assets and font self-host`.

### Task 13.4: Monitoring dashboard

**Files:** `docs/runbook/v2-monitoring.md`

**Step 1:** Document the post-launch monitoring plan (from design doc §8.3).
**Step 2:** Link dashboards (Sentry, GA, Search Console).
**Step 3:** Commit `docs: add v2 monitoring runbook`.

### Task 13.5: Retrospective

**Files:** `docs/plans/2026-xx-xx-v2-redesign-retro.md`

**Step 1:** Two weeks post-flip, capture:
- Metrics — booking rate before/after, bounce, time-on-page
- Feedback — customer/prospect reactions
- Learnings — what went smoother than expected, what didn't
- Follow-ups — carryover tickets (Storybook? Self-host fonts? Real case studies? Named bios?)
**Step 2:** Commit `docs: v2 redesign retrospective`.

---

## Dependencies & open items

- **Pillar copy** (Health / Defense / Agentic Ops × 3 paragraphs) — flag to Aaron at Task 7.1.
- **InkSection manifesto** (Home "Why vendor-neutral") — draft in Task 7.1, Aaron approves before ship.
- **Named-practitioner bios** (About) — blocker at Task 7.8; needed before flip.
- **Real case studies** vs. anonymized engagement summaries — decide before Task 5.4.
- **Purchased display font** — if delivered before Phase 1 complete, swap Inter `@import` for `@font-face`.
- **Lighthouse 90 target** — negotiable to 85 if brand PNG weight makes it unreachable and WebP doesn't close the gap.

---

## Quick reference — file paths

| Thing | Path |
|-------|------|
| Design doc | `docs/plans/2026-04-22-website-redesign-design.md` |
| This plan | `docs/plans/2026-04-22-website-redesign.md` |
| Design system source (read-only) | `docs/design-system/` |
| v2 tokens | `client/src/styles/omniscient.css` |
| v2 Tailwind aliases | `client/src/index.css` (`@theme inline` block) |
| v2 scope helper | `client/src/lib/theme-v2.ts` |
| v2 routes | `client/src/pages-v2/V2Routes.tsx` |
| v2 UI primitives | `client/src/components-v2/ui/` |
| v2 layout | `client/src/components-v2/layout/` |
| v2 brand | `client/src/components-v2/brand/` |
| v2 sections | `client/src/components-v2/sections/` |
| v2 pages | `client/src/pages-v2/` |
| Brand assets | `client/public/brand/` |
| Component showcase | `/_showcase` route (dev-only) |

---

## Phase summary

| Phase | Tasks | Est. | Shipping criterion |
|-------|-------|------|---------------------|
| 0 — Setup | 5 | 1 day | Branch + assets + env flag in place |
| 1 — Tokens | 6 | 1 day | Token showcase renders per design system |
| 2 — UI primitives | 14 | 3 days | All 14 primitives tested, in showcase |
| 3 — Layout | 6 | 2 days | Nav + Footer + Layout wrap showcase |
| 4 — Brand | 3 | 0.5 day | Logo, BrainGraphic, Tagline in showcase |
| 5 — Sections | 14 | 4 days | All 14 sections in showcase |
| 6 — Showcase | 1 | 0.5 day | `/_showcase` is canonical visual reference |
| 7 — Marketing | 10 | 5 days | 10 pages on `/_v2/*` preview |
| 8 — Conversion | 2 | 1 day | Book + Custom Workshop pages |
| 9 — Content | 2 | 1 day | Insights + Article pages |
| 10 — Tools | 2 | 2 days | Quiz + ROI Calculator |
| 11 — Legal/utility | 3 | 0.5 day | Privacy/Terms/404 pages |
| 12 — Flip & cleanup | 6 | 1.5 days | Production on v2; legacy deleted |
| 13 — Ship gate | 5 | 1 day + 2-wk retro | OG image, SEO updates, monitoring, retro |

**Total:** ~24 days of focused work + the 2-week monitoring tail. 75 tasks.
