# RAMA G7 Design System

**RAMA G7 Club** (ชมรมแพทย์นวัตกรรามา) is the Medical Innovation Club at Ramathibodi Hospital, Mahidol University. The club is run by medical students (5th–6th year and above) who build, evaluate, and write critically about medical technology — especially AI.

The site lives at **g7.prawees.com** and serves dual purposes: an editorial magazine for medical AI pieces, and a club presence (workshops, member content, join flow).

---

## Sources

| Source | Path / URL |
|---|---|
| Main codebase | `g7_site/` (mounted via File System Access API) |
| Live site | https://g7.prawees.com |
| Contact | rama.g7.club@gmail.com |

---

## Product Overview

One product surface: **the editorial website** (`g7.prawees.com`).

The site hosts two of three content streams from the RAMA G7 master plan:
- **Stream 2 — Editorial pieces.** Weekly, author-attributed, medical AI focus. Typically written by Smart (VP) or named club members.
- **Stream 3 — Member content.** Workshops, project journals, member spotlights. 2–4 per month.

Stream 1 (auto-curated news) lives on Facebook only — not on the website.

The stack is intentionally minimal: Python static site generator, Markdown posts, plain HTML/CSS, no JavaScript in production, deployed to Hostinger via FTP on every `git push`.

---

## CONTENT FUNDAMENTALS

### Tone and voice
- **Specific and questioning, never hype.** Numbers always beat adjectives.
- **Code-switch naturally.** English jargon (deep learning, ROC-AUC, etc.) is used as-is, not translated awkwardly.
- **First person singular** ("we" for the club as a body; "I" rarely appears; default voice is a measured editorial "the model performs…").
- **Sentence case** for titles (not Title Case). No colons in titles or body.
- **No em-dashes.** Commas or periods instead.
- **One emoji maximum**, never at the start of a sentence.
- **Always one limitation** stated per piece.

### Banned words (hype list)
ก้าวสำคัญ, breakthrough, revolutionize, น่าทึ่ง, เปลี่ยนวงการ, ปฏิวัติ, อนาคตของการแพทย์

### Citation style
Vancouver inline: `[1]` or `[1,2]`, rendered as superscript links. References block at end, heavy top rule, numbered list.

### Categories (fixed set)
`Paper Notes` · `Commentary` · `Tool Evaluation` · `Build Log` · `Member Spotlight`

### Language
Thai primary for headlines and intros. English for medical/technical terms as spoken in Thai medical culture. Some pieces entirely in English. Body mixes Thai prose with English jargon inline.

---

## VISUAL FOUNDATIONS

### Color system
| Token | Hex | Usage |
|---|---|---|
| `--ink` | `#030F27` | Primary text, masthead bg, footer bg |
| `--paper` | `#F4EFE6` | Page background (warm cream) |
| `--paper-warm` | `#EDE6D6` | Code bg, subtle surface |
| `--accent` | `#14B59D` | Teal — logo color, decorative borders, hover states |
| `--accent-deep` | `#0E8A78` | Teal on cream — text links, legible |
| `--rule` | `#DCD4C2` | Horizontal rules, card borders |
| `--muted` | `#5C6675` | Secondary text, metadata |
| `--muted-soft` | `#9AA0AB` | Tertiary text, footer text |

No gradients. No color fills on cards. Background is always cream or ink — never a mid-tone.

### Typography
**Final font stack:**
- **Wordmark:** Rajdhani 700 — geometric, techy, matches the club logo's character. "RAMA" white, "G7" in teal.
- **Display / Body:** DM Sans — clean, modern, no LLM-newspaper feel. Works well for both Thai and English via IBM Plex Sans Thai fallback.
- **Thai:** IBM Plex Sans Thai (loopless / ไม่มีหัวอักษร) — modern, sans, pairs perfectly with DM Sans.
- **UI / Meta:** DM Sans — same family, lighter weights for metadata and navigation.
- **Mono:** IBM Plex Mono — code, inline terms like ROC-AUC, 510(k).

> **Font substitution note:** The deployed site still uses `Trirong` + `IBM Plex Sans Thai Looped`. The design system uses the above updated stack. To apply: swap the Google Fonts `<link>` in `templates/base.html` and update `--font-display`, `--font-body`, `--font-ui` in `static/css/style.css`.

Type scale: modular, using `clamp()` for headings. Body 18px / 1.65 leading. Generous paragraph spacing. Second paragraph indented (classic print indent). Small caps for metadata (category labels, dates, author lines).

### Spacing
8-point-ish modular scale via `--s-1` through `--s-9` (0.25rem → 6rem). Content width capped at `68ch`. Page max `1180px`.

### Backgrounds and texture
Subtle SVG fractal noise grain overlay fixed to the page at 35% opacity, `multiply` blend mode. Creates warmth against the cream background. No photography in the site structure — only editorial content may contain images.

### Animations
Single pattern: `fadeUp` — 8px translateY + opacity 0→1, 480ms, `cubic-bezier(0.2, 0.7, 0.2, 1)`. Staggered by child index (60ms increments). Respects `prefers-reduced-motion`.

### Hover states
- Links: color shifts from `--accent-deep` to `--ink`; bottom border darkens. 120ms ease.
- Post cards: very faint teal background tint (`rgba(20,181,157,0.04)`); title shifts to `--accent-deep`. 160ms ease.
- Nav links: opacity 0.85 → 1, color → `--accent`.

### Press / active states
No shrink or scale transforms. Color-only state changes.

### Borders and rules
1px solid `--rule` on card tops/bottoms. 2px solid `--ink` on the references block (heavy, typographic). 2px solid `--accent` for blockquote left border. No box shadows beyond a single subtle `0 1px 0 rgba(3,15,39,0.06)` token.

### Corner radii
Minimal: `2px` on inline code only. Everything else is sharp-cornered — true editorial.

### Cards
Post cards use a grid layout (number col + content col), top border only, no bg fill, no shadow, no rounding. Hover adds a trace tint.

### Imagery
No decorative illustrations on the site. Editorial pieces may contain referenced figures. Color vibe is neutral-warm (matching cream bg).

### Layout
Masthead: dark ink band, 3-column grid (logo | tagline | nav). Footer: 2-column dark ink grid. Content: centered, max 68ch. No sidebar. No sticky elements beyond what browser defaults provide.

---

## ICONOGRAPHY

No icon system used on the site. No icon font, no SVG icon set, no emoji in the UI chrome. Decorative punctuation (·, —) and typographic elements serve navigation/separation duties. The logo (`assets/logo.png`) is the only brand image asset in use.

If icons are needed for UI kit work or future club features (workshops, events), **Phosphor Icons** (https://phosphoricons.com/) is the recommended CDN-linked set — its stroke weight and editorial feel align with IBM Plex Sans. Use the `regular` weight.

---

## FILES IN THIS DESIGN SYSTEM

```
README.md                   This file
SKILL.md                    Agent skill entry point
colors_and_type.css         CSS custom properties — colors, type, spacing
assets/
  logo.png                  Club logo (masthead)
  favicon.png               Favicon
preview/
  colors-base.html          Base color palette swatches
  colors-semantic.html      Semantic color roles
  type-scale.html           Heading and body type specimens
  type-ui.html              UI / smallcaps / mono specimens
  spacing-tokens.html       Spacing scale tokens
  components-masthead.html  Masthead component
  components-postcard.html  Post card list
  components-article.html   Article header + body
  components-footer.html    Footer component
  components-buttons.html   Link styles and interactive states
ui_kits/
  website/
    README.md               UI kit notes
    index.html              Full interactive prototype
    Masthead.jsx            Header component
    PostCard.jsx            Index post card
    ArticleView.jsx         Article detail view
    Footer.jsx              Footer component
```
