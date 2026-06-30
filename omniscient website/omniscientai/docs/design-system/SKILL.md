---
name: omniscient-ai-design
description: Use this skill to generate well-branded interfaces and assets for Omniscient AI, either for production or throwaway prototypes/mocks/decks. Contains essential design guidelines, colors, type, fonts, assets, and UI kit components for prototyping.
user-invocable: true
---

Read the `README.md` file within this skill, and explore the other available files.

If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy assets out and create static HTML files for the user to view. Always `@import` `colors_and_type.css` at the top of any HTML file so the tokens resolve.

If working on production code, you can copy assets and read the rules here to become an expert in designing with this brand.

If the user invokes this skill without any other guidance, ask them what they want to build or design, ask some questions, and act as an expert designer who outputs HTML artifacts _or_ production code, depending on the need.

Key reminders for Omniscient AI specifically:
- Tri-tone palette: near-black `#0F1115`, electric blue `#2F7BFF`, pure white. Proportions on a page: ~70% paper / 20% ink / 8% blue / 2% glow.
- Flat geometric DNA. No gradient washes, no skeuomorphism, no emoji in product or marketing surfaces.
- Pace long pages by flipping one section to ink (`#0F1115`) — not gradients, not photos.
- The brain-network brand graphic (`assets/brand-graphic-*`) is a signature element. Drop it in hero corners, 20–40% of viewport width. Don't recolor or recompose it.
- Sentence case for copy. `UPPERCASE` only for eyebrows and the signature `INTELLIGENCE // CONNECTIVITY // INNOVATION` tagline. Prefer `→` at the end of CTAs.
- Inter is a substitution for the display face until a purchased font is supplied.
