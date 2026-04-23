# Omniscient AI — Design System

Omniscient AI is a Melbourne-based, vendor-neutral AI consultancy. They sit at the intersection of **research and commercial practice**: running hands-on AI training workshops for SMEs, building agentic tooling for marketing & ops teams, and (per the founder's brief) extending into **health technologies** and **defense hardware & software**. The public posture is a boutique, heavy-hitter firm — small team, big shoulders, broad remit.

Core brand idea: **Intelligence // Connectivity // Innovation.** The visual signature is a dense, geometric "brain-as-network" graphic built from overlapping black, blue and white discs joined by thin blue wires with glowing nodes — the connectome rendered as Bauhaus.

## Surfaces represented

1. **Marketing website** (`omniscientai.io`) — the main surface covered in the UI kit. Currently reads as a training/consulting site and is up for a full overhaul.
2. **Social / pitch collateral** — square hero cards, wordmark lockups (see `assets/`).
3. **Future surfaces** — the health-tech, defense and agentic-ops product lines are described in the founder's brief but don't have finished UIs yet. The system is built so those products can all extend from the same visual core.

## Sources used to build this system

- `uploads/Screenshot 2026-02-05 234257.png` — stacked "brain" logomark + `Omniscient AI` wordmark
- `uploads/Screenshot 2026-02-05 234406.png` — square social hero: "UNLEASHING THE POWER OF INTELLIGENT CONNECTIONS" + tagline line + `INTELLIGENCE // CONNECTIVITY // INNOVATION`
- `uploads/Screenshot 2026-02-05 234507.png` — horizontal wordmark lockup with decorative graphic on the right
- `https://omniscientai.io/` — live site (currently a mostly-empty SPA; we could only pull the title `OmniscientAI — Melbourne's Vendor-Neutral AI Training for SMEs` and a handful of body copy fragments). **The marketing site is up for a full overhaul**, so this design system is deliberately more ambitious than the existing site.

## Caveats the reader should know

- No codebase or Figma was provided. The UI kit is an **original recreation rooted in the supplied brand assets** (logos, colors, type hierarchy, tone fragments). Treat screens as a direction for the overhaul, not a faithful rebuild.
- No custom webfont was provided. We've specified **Inter** (close geometric grotesque) as the display/text face until real files are supplied. See "Type" below — **please send font files if you have a purchased face.**
- The omniscientai.io SPA renders body copy client-side, so we have limited primary copy samples. Tone guidance is drawn from the social card, the project brief, and industry conventions for vendor-neutral AI consulting.

---

## Index — what's in this folder

```
README.md                    ← this file
SKILL.md                     ← agent-skill manifest (read this first if loaded as a skill)
colors_and_type.css          ← CSS custom properties: palette, type scale, semantic vars
fonts/                       ← webfont files (currently empty — Inter loaded from CDN)
assets/
  logo-brain-stacked.png       — primary logomark (brain graphic + wordmark, stacked)
  logo-horizontal-with-graphic ← horizontal lockup with decorative graphic
  logo-wordmark.png            — wordmark-only crop (circle dot + "Omniscient AI")
  logo-mark-circle.png         — standalone black-disc mark
  brand-graphic-circles.png    — decorative brain-network graphic (square)
  brand-graphic-horizontal.png — decorative brain-network graphic (horizontal band)
  hero-social-card.png         — reference: finished social hero card
preview/                     ← design-system cards surfaced in the Design System tab
ui_kits/
  website/                   ← marketing site UI kit (index.html + components)
```

---

## CONTENT FUNDAMENTALS

Omniscient AI's voice is **confident, plainspoken, slightly swaggering** — a boutique shop that has done serious research work and is now moving into commercial territory. It is *not* the breathless, emoji-heavy voice of a growth-stage SaaS startup, and it is *not* the dry, reference-grade tone of an enterprise vendor. It sits between them.

### Voice markers

- **Person.** Mostly **"we"** when describing Omniscient, and **"you / your team"** when addressing the reader. First-person singular "I" is reserved for founder bylines and quotes.
- **Sentences.** Short. Declarative. Cut the adverbs. Lead with the verb. Two- or three-word fragments are welcome as headlines (see `INTELLIGENCE // CONNECTIVITY // INNOVATION`).
- **Casing.**
  - `UPPERCASE` for hero and section labels — always tracked out (`letter-spacing: 0.06em` min). Used sparingly; one per view.
  - `Sentence case` for body copy, menu items, card titles. Avoid Title Case on buttons.
  - `Title Case` only for proper nouns and program names (e.g. `AI Readiness Assessment`).
- **Emoji.** No. The brand is geometric and serious — emoji break the silhouette. The exception is hashtags on social (`#OmniscientAI #Innovation #Connectivity #FutureTech`) because that's the platform convention.
- **Hashtag-as-signature.** On social cards, a short hashtag string ending in `#FutureTech` or `#AIReady` is a signature move. Don't use hashtags in product copy.
- **Acronyms.** `AI`, `ML`, `SME` — always uppercase, never `Ai` or `A.I.`. When spelling out, use "artificial intelligence" lowercase in running text.
- **Slashes as rhythm.** `//` between three equal words is a brand device (`INTELLIGENCE // CONNECTIVITY // INNOVATION`). Use once per page max.

### Example swaps

| Don't say | Say |
|---|---|
| "Leverage our AI-powered solutions to unlock synergies" | "We build AI that does one job well." |
| "Check out our amazing new training! 🚀" | "New this month: a two-day AI readiness workshop for ops teams." |
| "Our revolutionary platform" | "Our platform" (or name the thing) |
| "Reach out to learn more!" | "Book a 20-minute call." |

### Proof points that belong in copy

- **Vendor-neutral.** Bring up in the first paragraph of anything training-related.
- **Melbourne.** Physical presence matters for the SME audience — mention it.
- **Boutique / heavy-hitter.** Small team, named practitioners, no junior bait-and-switch.
- **Three practice areas.** Health, defense, agentic ops — mentioned together they establish breadth without getting specific.

---

## VISUAL FOUNDATIONS

### The big idea

**High-contrast geometric network.** Pure black, electric blue, and flat white, arranged as overlapping circles joined by thin blue wires with small glowing nodes. The logomark is literally a brain drawn this way. Apply the same grammar to illustrations, section dividers, and data visualisations. Keep things flat — no skeuomorphism, no soft 3D, no airbrush.

### Color

Built on a **tri-tone core** (ink / blue / paper) with a small set of neutrals and two semantic accents. See `colors_and_type.css` for the canonical tokens.

- `--ink` `#0F1115` — near-black, not pure black. Sampled from the logomark's discs which read as very-dark warm black on the card. Used for primary text, backgrounds in dark mode, and the black discs in illustrations.
- `--blue` `#2F7BFF` — the signature electric blue. Slightly bluer/cooler than the raw sample (`#3981F1`) to hold up at small sizes and against both light and dark backgrounds. Used for primary actions, key graphics, and the occasional pull-quote highlight.
- `--blue-deep` `#1C4FD6` — for pressed states and small-type blue text.
- `--blue-glow` `#7AA8FF` — the "node glow" blue, only inside illustrations and as a focus ring.
- `--paper` `#FFFFFF` — pure white. Primary canvas.
- `--paper-2` `#F4F6F9` — secondary surface / card on white.
- `--line` `#E4E7EC` — hairline dividers at 1px.
- `--ink-2` `#2A2F37` — secondary text on light.
- `--ink-3` `#5B6270` — tertiary / metadata.
- `--success` `#1EA97C`, `--warn` `#E8A23A`, `--danger` `#D94B4B` — semantic accents used only in product UI. Never in marketing material.

**Proportions.** On any given screen, roughly **70% paper, 20% ink, 8% blue, 2% glow/accent**. The blue is a scalpel, not a paint roller. Hero blocks and CTAs earn the blue; body type stays ink.

### Type

- **Display / UI face.** `Inter` (variable, 400–800). Geometric grotesque, wide aperture, reads cleanly at both 72pt hero size and 13px table cells. **This is a substitution** — if Omniscient AI has purchased Neue Haas Grotesk, GT America or Söhne, please send files and we'll swap.
- **Mono face.** `JetBrains Mono` for code, numeric tables, and the occasional hashtag string.
- **No serifs.** The brand is flat-geometric; a serif would fight the illustrations.

Scale (see `colors_and_type.css` for the full token set):

- Hero display `clamp(48px, 7vw, 96px)`, weight 700, tracking `-0.03em`, leading 0.95.
- H1 `56px` / 700 / `-0.025em` / leading 1.05.
- H2 `36px` / 700 / `-0.02em`.
- H3 `22px` / 600.
- Body `17px` / 400 / leading 1.55.
- Small `14px` / 400 / `--ink-3`.
- Eyebrow `12px` / 600 / `UPPERCASE` / tracking `0.14em`.

### Spacing

4-point base. Tokens: `4, 8, 12, 16, 24, 32, 48, 64, 96, 128`. Generous whitespace on marketing; denser 4/8 on product UI. Content max-width `1240px` centered.

### Backgrounds

- **Primary.** Pure white paper. Full-bleed. No gradients on body backgrounds.
- **Section break.** Swap to `--ink` (near-black) for a single section; invert everything inside. This is the primary way to pace a long page — not gradients, not images.
- **Illustration.** Brand graphic (`assets/brand-graphic-*`) as a corner element at 20–40% of viewport width. Never tiled, never faded, never behind text.
- **Gradients.** Avoid. A single exception: a 2-stop `--blue` → `--blue-deep` fill on very small marks (badges, button pressed states). **Never** purple/blue gradient washes.
- **Repeating patterns.** Use the 4px blue-dot grid (see `preview/card-pattern-dotgrid.html`) inside product empty states and loading skeletons. Not on marketing.

### Imagery

- **Cool, high-contrast, a little industrial.** Server rooms, optics labs, workshop scenes with real people. Black-and-white or slightly desaturated with a blue cast is fine. Never warm-toned or beige.
- **No stock-smiling-handshake photography.** If in doubt, use the brand graphic instead.
- **Grain.** Light film-grain acceptable on full-bleed photos to match the flat-illustration DNA. Don't add grain to UI.

### Animation

- **Short, decisive, geometric.** 160–220ms base duration. Easing `cubic-bezier(0.2, 0.9, 0.2, 1)` — a mild overshoot-free ease-out. No bouncy spring, no elastic.
- **Hover.** `translateY(-1px)` + slightly darker fill (`color-mix(in oklab, var(--blue) 92%, black)`). Never scale up.
- **Press.** `translateY(0)` + `filter: brightness(0.96)`. Never shrink.
- **Page transitions.** Fade + 8px upward translate, 200ms. Avoid slide-ins.
- **Brand graphic motion.** Individual nodes pulse (`--blue-glow`, 2s loop, `ease-in-out`) as the only ambient motion. Keep this rare; hero only.

### Borders, radii, shadows

- **Corner radius.** Tight. Cards `8px`, buttons `6px`, inputs `6px`, pills `999px`. Never `16px+` on product chrome — that reads as consumer-app and fights the geometric logo.
- **Hairline borders.** `1px solid var(--line)` for dividers; `1.5px solid var(--ink)` for emphasised card outlines.
- **Shadows.** Two tokens.
  - `--shadow-1` `0 1px 2px rgb(15 17 21 / 0.06), 0 1px 1px rgb(15 17 21 / 0.04)` — default card.
  - `--shadow-2` `0 10px 24px rgb(15 17 21 / 0.08), 0 2px 6px rgb(15 17 21 / 0.06)` — raised / menu / modal.
  - No inner shadows. No colored shadows.

### Hover, press, focus

- **Hover.** Primary button → darken blue by ~8%, 1px lift. Secondary → swap fill from paper to `--paper-2`. Link → underline appears on hover (default underline-off).
- **Press.** Drop the lift, darken another 4%.
- **Focus.** `2px` outline in `--blue-glow` with a `2px` offset. Visible, not tacky.
- **Disabled.** 40% opacity, no pointer.

### Transparency, blur, protection gradients

- **Transparency.** Used only on overlays (modal scrim `rgb(15 17 21 / 0.55)`). Not on surfaces.
- **Blur.** `backdrop-filter: saturate(1.2) blur(14px)` on the sticky top nav over white content. Do not use blur elsewhere.
- **Protection gradients over imagery.** `linear-gradient(to top, rgb(15 17 21 / 0.65), transparent 55%)` when placing paper-color text over a photo. Capsules/pills are *not* used for this — the brand prefers the gradient.

### Layout rules

- **Grid.** 12 columns, 72px gutter on desktop, 24px on mobile. `container` max-width 1240px.
- **Fixed elements.** Top nav is sticky translucent. No floating chat bubbles, no floating CTAs. A single anchored footer.
- **Asymmetry.** Hero blocks are split 55 / 45 (copy / graphic) not 50/50 — this is lifted from the social card composition.
- **Rhythm.** Dense headline → roomy body → dense proof-point row → roomy CTA. Alternating pressure is how the brand breathes.

### Cards

Flat. `1px solid --line`, `8px` radius, `--paper` fill (or `--paper-2` on white backgrounds for subtle separation), `--shadow-1` on hover only (not default). No gradient fills, no colored backgrounds except one "featured" variant that flips to `--ink` with `--paper` text.

### Iconography — see `ICONOGRAPHY` section below.

---

## ICONOGRAPHY

### Approach

Omniscient AI does **not** ship its own icon set. The brand leans into bold geometric illustrations rather than fussy UI glyphs — so line icons are supporting cast, used small and sparsely.

- **Chosen set:** [**Lucide**](https://lucide.dev) (MIT, CDN-available). Reasoning: consistent `1.75px` stroke reads as slightly heavier than Heroicons and matches the confident weight of Inter 600. 24px grid. We've linked it from CDN in the UI kit.
- **Flag / substitution notice.** Lucide is an **opinionated substitution** since no icon system was specified. If the user prefers Phosphor (more geometric), Heroicons (softer), or a custom set, we'll swap — all CDN-available.
- **Stroke weight.** 1.75px at 24px, scaled proportionally. Never fill unless the icon is a logo-adjacent mark (e.g. app tile).
- **Color.** `--ink` by default, `--blue` for the ONE icon in a component that is actively doing something (e.g. the chevron on an open menu). Never colorise a whole icon row.
- **Size.** 16px (inline), 20px (default UI), 24px (primary nav), 32px+ (illustration).
- **Pairing with labels.** Icons in nav and buttons always pair with a text label. Icon-only buttons are reserved for obvious actions (close, search) and get an `aria-label`.

### Emoji and unicode

- **Emoji:** no, as covered in CONTENT FUNDAMENTALS. The one exception is social media hashtags and in-room chat — not in product chrome or marketing.
- **Unicode as icon:** allowed for arrow marks (`→`, `↗`) in links and CTAs. The brand loves the `→` after a label: `Read the case study →`. That's the move.

### Brand marks and illustrations

- `logo-brain-stacked.png` — primary logomark for square contexts (app tile, LinkedIn avatar, lower-left of a pitch deck).
- `logo-horizontal-with-graphic.png` — horizontal lockup for wide contexts (email signature, deck header).
- `logo-wordmark.png` — wordmark-only for cramped contexts (favicon shoulder, footer row).
- `logo-mark-circle.png` — the standalone black-disc mark. The simplest form — use as a bullet or app favicon.
- `brand-graphic-circles.png`, `brand-graphic-horizontal.png` — decorative brain-network illustrations. Drop into hero corners. **Do not modify or recolor.** If you need a smaller piece, crop — don't recompose.

**Do not draw new brand illustrations.** If a design needs a brand graphic and the existing ones don't fit, **stop and ask the founder** — this is a signature element, not a thing to improvise. The brain/network motif is the core of the identity.

---

## Next steps for the reader

- Open the **Design System tab** to review every token and component visually.
- Open `ui_kits/website/index.html` for the proposed marketing-site recreation.
- See `SKILL.md` if invoking this as an Agent Skill.
