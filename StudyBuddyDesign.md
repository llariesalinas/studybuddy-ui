---
version: alpha
name: StudyBuddy
description: >
  "Loud Background, Quiet Foreground" — highly vibrant Aurora Mesh backgrounds
  paired with Frosted Glass UI components for academic professionalism with modern gamification.
colors:
  primary: "#00895a"
  primary-hover: "#00704a"
  ink: "#0f172a"
  muted: "#475569"
  canvas: "#f8fafc"
  aurora-emerald: "rgba(16, 185, 129, 0.5)"
  aurora-sky: "rgba(14, 165, 233, 0.45)"
  aurora-violet: "rgba(139, 92, 246, 0.4)"
  glass-light: "rgba(255, 255, 255, 0.6)"
  glass-dark: "rgba(15, 23, 42, 0.7)"
typography: {}
rounded:
  sm: "6px"
  md: "12px"
  lg: "16px"
  full: "9999px"
spacing:
  section: "100px"
  gap-sm: "8px"
  gap-md: "16px"
  gap-lg: "24px"
motion:
  spring: "cubic-bezier(0.16, 1, 0.3, 1)"
  spring-fast: "cubic-bezier(0.34, 1.56, 0.64, 1)"
  t-quick: "120ms"
  t-normal: "250ms"
  t-slow: "400ms"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "#ffffff"
    padding: "10px 20px"
    rounded: "{rounded.md}"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
    textColor: "#ffffff"
  button-primary-active:
    backgroundColor: "{colors.primary}"
    textColor: "#ffffff"
  button-disabled:
    backgroundColor: "{colors.primary}"
    textColor: "#ffffff"
  card-glass-light:
    backgroundColor: "{colors.glass-light}"
    rounded: "{rounded.lg}"
  card-glass-dark:
    backgroundColor: "{colors.glass-dark}"
    rounded: "{rounded.lg}"
  card-interactive:
    backgroundColor: "{colors.glass-light}"
    rounded: "{rounded.lg}"
  card-interactive-hover:
    backgroundColor: "rgba(255, 255, 255, 0.92)"
  image-wrapper:
    backgroundColor: "{colors.glass-light}"
    rounded: "{rounded.lg}"
---

# StudyBuddy Design System (Pre-Finals)

## Overview

To balance academic professionalism with modern gamification, StudyBuddy uses a highly vibrant "Aurora Mesh" background paired with heavily blurred, stark white "Frosted Glass" UI components.

- **The Foreground:** Must remain clean, monochromatic (black/white/slate), and use the primary brand green sparingly for actions. No random colorful gradients on text or icons.
- **The Background:** Must provide all the visual energy.

## Colors

**Brand Colors:**
- `primary` (`#00895a`) — StudyBuddy Green. Used for buttons, links, and active states.
- `primary-hover` (`#00704a`) — Darkened green for hover states.
- `ink` (`#0f172a`) — Deep Slate. Used for all primary headings and text.
- `muted` (`#475569`) — Used for paragraphs and secondary text.
- `canvas` (`#f8fafc`) — Off-white base behind the aurora mesh.

**Aurora Mesh (The "Loud" Background):**
These colors are exclusively used as heavily blurred (`filter: blur(140px)`), large circular blobs (`mix-blend-mode: multiply`) in the absolute background.
- `aurora-emerald` (`rgba(16, 185, 129, 0.5)`)
- `aurora-sky` (`rgba(14, 165, 233, 0.45)`)
- `aurora-violet` (`rgba(139, 92, 246, 0.4)`)

**Glass Surface Colors:**
- `glass-light` (`rgba(255, 255, 255, 0.6)`) — Light frosted glass panels.
- `glass-dark` (`rgba(15, 23, 42, 0.7)`) — Dark frosted glass panels (footers, overlays).

## Typography

Typography tokens are not yet finalized. Fill in `fontFamily`, `fontSize`, `fontWeight`, and `lineHeight` here once the type scale is decided.

## Layout

- **Absolute Backgrounds:** Background meshes must use `position: absolute` with `width: 100%` and `height: 100%` relative to the document (NOT `100vh` or `fixed`) to prevent harsh cutoff lines when scrolling in Vue Router.
- **Split-Screen Layouts:** Use `.sb-split` (a 2-column CSS Grid) for hero sections and feature highlights. Left side for text, right side for SVG Clipart.
- **Anti-Density:** Ensure generous padding (e.g., `padding: 100px 0` for sections) to prevent the "Decision Fatigue" noted by the thesis panel.

## Elevation & Depth

Instead of solid white backgrounds, use heavily blurred translucency so the Aurora Mesh subtly bleeds through.

- **Light Panels** (`card-glass-light`): `background: rgba(255, 255, 255, 0.6)` with `backdrop-filter: blur(24px)` and a crisp `border: 1px solid rgba(255, 255, 255, 0.9)`.
- **Dark Panels** (`card-glass-dark`): `background: rgba(15, 23, 42, 0.7)` with `backdrop-filter: blur(24px)` and `border-top: 1px solid rgba(255,255,255,0.1)`.

## Components

**Buttons (`.sb-btn`) — apply to every `<button>`:**
- Base: `background: {colors.primary}`, `color: #fff`, `padding: 10px 20px`, `border-radius: {rounded.md}`, `box-shadow: 0 4px 15px rgba(0,137,90,0.3)`
- Hover: `transform: translateY(-3px)`, shadow deepens — transition on `{motion.t-quick}` with `{motion.spring-fast}`
- Active/press: `transform: scale(0.96) translateY(0)` — snaps down, springs back on release
- Disabled: `opacity: 0.4`, `pointer-events: none`, no shadow

**Interactive Surfaces (`.sb-interactive`) — apply to cards, list rows, pressable panels:**
- Hover: `transform: translateY(-6px)`, glass opacity increases to `rgba(255,255,255,0.92)`, `border-bottom: 3px solid {colors.primary}`
- Active: `transform: scale(0.98) translateY(0)`
- Transition: `{motion.t-normal}` with `{motion.spring}`

**Image Wrapper (`.sb-image-wrapper`):**
- Wrap SVGs in a `card-glass-light` container (max-width ~380px). Hover: `transform: scale(1.1) translateY(-10px)`.

**Accordion Toggles:**
- The "+" icon rotates 45° (`transform: rotate(45deg)`) and fills with `{colors.primary}` when opened.

## Motion & Interaction

**Timing & Easing Tokens** (defined as CSS custom properties on `:root`):

| Token | Value | Use |
|---|---|---|
| `--sb-spring` | `cubic-bezier(0.16, 1, 0.3, 1)` | Cards, panels, entrance animations — smooth deceleration |
| `--sb-spring-fast` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Buttons — slight overshoot for tactile feel |
| `--sb-t-quick` | `120ms` | Button press, hover transitions |
| `--sb-t-normal` | `250ms` | Card hover, bubble entrance, room transitions |
| `--sb-t-slow` | `400ms` | Error shake, page-level transitions |

**Keyframe Animations** (defined globally, applied by class or inline):

| Animation | Trigger | Behaviour |
|---|---|---|
| `sb-bubble-in` | New message appended | Fade in + slide up 12px + scale 0.94→1, 250ms `--sb-spring` |
| `sb-pulse-dot` | Pending send / unread badge | Green glow ring pulses outward on repeat |
| `sb-pop` | Read receipt flips `is_read=true` | Icon scales 0.6→1.3→1 with opacity, fires once |
| `sb-shake` | Send failure / empty submit | Element translates ±5px × 2 cycles, 400ms, then removed |

**Rules:**
- Only newly appended elements animate — never replay animations on existing content.
- Use `<TransitionGroup>` (Vue) for list items so only entering nodes get `sb-bubble-in`.
- Shake class must be added and removed via `setTimeout` (420ms) — never leave it permanently applied.
- All interactive elements must have `cursor: pointer` and `user-select: none`.

## Do's and Don'ts

**Iconography & Graphics:**
- **No Stock Photos:** Avoid generic stock images of real people.
- **SVG Clipart:** Use dependency-free, inline SVG illustrations.

**Interaction Rules:**
- **Always use `.sb-btn`** on `<button>` elements — never write one-off hover/active CSS for buttons.
- **Always use `.sb-interactive`** on pressable cards and list rows — do not override with custom transforms.
- **Never hardcode easing curves** — always reference `--sb-spring` or `--sb-spring-fast`.
- **Never animate history** — entrance animations apply only to newly rendered nodes.

**Thesis Panel Logic Proofs:**
Every design element must reflect actual backend capability:
- **OTP/Verification:** Visually represented by the "CPU Verified Only" badges.
- **Hybrid Recommender:** Visually represented by the "Step 02: Match and Book" flow.
- **Wallet/Ledger:** Visually represented by the "Tutor Earnings/Reports" feature cards.
