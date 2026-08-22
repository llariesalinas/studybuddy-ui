---
name: StudyBuddy
description: Peer-to-peer tutoring for Central Philippine University students.
colors:
  campus-green: "#00895A"
  campus-green-hover: "#00704A"
  campus-green-dark: "#0A7A51"
  campus-green-mid: "#18A36C"
  campus-green-light: "#edf6f1"
  campus-green-lighter: "#dff1e8"
  campus-green-contrast: "#ffffff"
  ink: "#0A1916"
  aurora-yellow: "#FFC94D"
  aurora-orange: "#FF8A5C"
  aurora-pink: "#FF8FA3"
  aurora-violet: "#8E7CF4"
  aurora-yellow-deep: "#DCA21B"
  aurora-orange-deep: "#E0683A"
  aurora-pink-deep: "#E26D86"
  deep-blue: "#006591"
  canvas: "#F8F9FA"
  surface: "#ffffff"
  hairline: "#EAEAEA"
  border-light: "#e0e7e3"
  text-main: "#163127"
  text-secondary: "#495057"
  text-muted: "#6B7280"
  text-subtle: "#a0acb8"
  text-muted-green: "#6b7d74"
  danger: "#ef4444"
  warning-bg: "#ffc107"
  warning-text: "#997404"
  info-bg: "#0dcaf0"
  link: "#0d6efd"
typography:
  display:
    fontFamily: "Plus Jakarta Sans, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "clamp(54px, 8.6vw, 132px)"
    fontWeight: 800
    lineHeight: 0.95
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Plus Jakarta Sans, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "30px"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "normal"
  title:
    fontFamily: "Plus Jakarta Sans, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "18px"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "normal"
  body:
    fontFamily: "Plus Jakarta Sans, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "normal"
  label:
    fontFamily: "Plus Jakarta Sans, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "13px"
    fontWeight: 700
    lineHeight: 1.4
    letterSpacing: "normal"
  eyebrow:
    fontFamily: "Plus Jakarta Sans, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "11px"
    fontWeight: 700
    lineHeight: 1.4
    letterSpacing: "0.08em"
  mono:
    fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "normal"
rounded:
  pill: "999px"
  xs: "10px"
  sm: "12px"
  md: "14px"
  lg: "18px"
  xl: "24px"
spacing:
  xs: "0.45rem"
  sm: "0.72rem"
  md: "1rem"
  lg: "1.5rem"
  xl: "3rem"
components:
  button-primary:
    backgroundColor: "{colors.campus-green}"
    textColor: "{colors.campus-green-contrast}"
    rounded: "{rounded.pill}"
    padding: "0.72rem 1rem"
    height: "42px"
    typography: "{typography.label}"
  button-primary-hover:
    backgroundColor: "{colors.campus-green-hover}"
    textColor: "{colors.campus-green-contrast}"
  button-on-brand:
    backgroundColor: "{colors.surface}"
    textColor: "#07543a"
    rounded: "{rounded.pill}"
    padding: "0.72rem 1rem"
    height: "42px"
  button-soft:
    textColor: "{colors.text-main}"
    rounded: "{rounded.pill}"
    padding: "0.72rem 1rem"
    height: "42px"
  button-danger-soft:
    textColor: "{colors.danger}"
    rounded: "{rounded.pill}"
    padding: "0.72rem 1rem"
    height: "42px"
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text-main}"
    rounded: "{rounded.lg}"
    padding: "28px"
  glass-segment:
    rounded: "{rounded.xl}"
    padding: "1.5rem"
  badge:
    backgroundColor: "{colors.campus-green-light}"
    textColor: "{colors.campus-green}"
    rounded: "{rounded.pill}"
    padding: "3px 10px"
  avatar:
    backgroundColor: "{colors.campus-green}"
    textColor: "{colors.campus-green-contrast}"
    rounded: "{rounded.pill}"
    size: "40px"
---

# Design System: StudyBuddy

## Overview

**Creative North Star: "The Bright Instrument"**

StudyBuddy is a precision tool that stayed warm. Its screens carry a lot of information at once —
schedules, wallets, session states, tutor rankings — and the type scale is unapologetic about it:
the working range is 11–14px, and it holds that density by leaning on weight rather than size.
Weight 700 and 800 appear over 300 times across the interface; weight 400 appears seven times.
Small and bold, not small and quiet.

What keeps that density from reading as clinical is geometry and motion, not whitespace. Nearly
every interactive element is a pill — a 999px radius is used 169 times, more than every other
radius combined — and everything answers when touched: a 4–6px lift on hover, a scale to 0.97 on
press, a soft green halo on focus, all on one calibrated spring. A single deep green anchors the
whole product, and the playful part of the palette lives almost entirely in atmosphere: three-layer
radial gradient washes that sit behind content rather than inside it.

The system is honest about where it is unfinished. Dark mode is defined but partial, the landing
page deliberately sits outside the token system, and one stylesheet defines tokens that no page
loads. Those are recorded below rather than hidden, because the previous design document's silence
about exactly this kind of drift is what `src/assets/tokens.test.js` now exists to catch.

**Key Characteristics:**

- Dense by design — an 11–14px working scale carrying 700–800 weights
- Pill-first geometry; 999px is the default radius, not an accent
- One green anchors everything; colour play is confined to background washes
- Motion is calibrated, not decorative — one spring, two durations, two lift distances
- Depth appears on intent and is nearly absent at rest
- Tokens are centralised in `src/assets/main.css` and enforced by a test

## Colors

A single saturated green does all the work of identity and action, supported by a near-neutral
canvas and a four-colour accent set that appears almost exclusively inside gradient washes.

### Primary

- **Deep Campus Green** (`#00895A`): The one action colour. Primary buttons, active navigation,
  selected pills, focus rings, progress tracks, and every affirmative state. Also the anchor of
  `--sb-green-anchor`, which deliberately stays saturated in both themes so the live-session hero
  never loses its identity in dark mode.
- **Campus Green Hover** (`#00704A`): The pressed and hovered state of any primary surface. Never
  used at rest.
- **Campus Green Dark** (`#0A7A51`) and **Campus Green Mid** (`#18A36C`): Gradient stops for brand
  surfaces and the wash layers. Not intended as standalone fills.
- **Green Tint** (`#edf6f1`) and **Green Wash** (`#dff1e8`): Tinted backgrounds for badges,
  selected rows, and soft brand surfaces where a saturated green would overwhelm.

### Secondary

- **Deep Blue** (`#006591`): The one non-green identity colour, used for the collaborative half of
  paired data (the CBF/CF split on Algorithm Settings) and for informational contrast where green
  would imply an action.

### Tertiary — Aurora Pops

These four exist for atmosphere. They appear composited at 11–18% opacity inside
`--sb-wash-blob-1/2/3`, the layered radial gradients that give authenticated pages their tinted
depth. They are not a control palette.

- **Aurora Yellow** (`#FFC94D`), deep variant `#DCA21B`
- **Aurora Orange** (`#FF8A5C`), deep variant `#E0683A`
- **Aurora Pink** (`#FF8FA3`), deep variant `#E26D86`
- **Aurora Violet** (`#8E7CF4`)

### Neutral

- **Ink** (`#0A1916`): The near-black brand dark. Sidebar and high-contrast surfaces.
- **Canvas** (`#F8F9FA`): The page floor everything sits on.
- **Surface** (`#ffffff`): Cards, modals, panels.
- **Hairline** (`#EAEAEA`) and **Soft Border** (`#e0e7e3`): Dividers and card edges. Borders are
  hairlines, never structural weight.
- **Text Main** (`#163127`): Body and heading text — a green-shifted near-black, not pure grey.
- **Text Secondary** (`#495057`), **Text Muted** (`#6B7280`), **Text Subtle** (`#a0acb8`): The
  descending hierarchy for supporting copy, labels, and placeholder text.

### Status

Status colour is currently partial. What exists: **Danger** (`#ef4444`), **Warning** background
(`#ffc107`) with **Warning Text** (`#997404`), **Info** (`#0dcaf0`), and **Link** (`#0d6efd`).

There is no `--sb-success` token, and no `-fg` / `-surface` / `-border` slots for any status.
`tokens.test.js` asserts the full four-status ramp and currently fails on it: the ramp is the
intended design, not the implemented one. Success states borrow the primary green today.

### Named Rules

**The Atmosphere-Only Rule.** The Aurora Pops never colour a control, a label, or a piece of text.
They exist inside `--sb-wash-blob-*` and nowhere else. If an accent needs to carry meaning, it is
Deep Campus Green or Deep Blue.

**The One Green Rule.** There is exactly one action colour. A second saturated call-to-action
colour on the same screen means one of them is not actually a call to action.

## Typography

**Base Font:** Plus Jakarta Sans (with `system-ui`, `-apple-system`, `BlinkMacSystemFont`,
`Segoe UI`, sans-serif)
**Mono Font:** `ui-monospace`, SFMono-Regular, Menlo, Consolas, monospace

Both are centralised as `--sb-font-base` and `--sb-font-mono`. Plus Jakarta Sans is self-hosted as
a variable font (weights 200–800) via `@fontsource-variable/plus-jakarta-sans`, never a Google
Fonts link — see [ADR-0012](docs/adr/0012-typography-system.md).

**Character:** Geometric, slightly rounded, and legible at sizes most systems would consider too
small. The pairing carries the whole product; there is no display face. Personality comes from
weight and tightness, not from a second family.

### Hierarchy

- **Display** (800, `clamp(54px, 8.6vw, 132px)`, line-height 0.95): Landing page only. Hero
  statements that fill the viewport. Never appears in the authenticated app.
- **Headline** (700, 30px, 1.2): Page titles on app screens. The largest type most users ever see.
- **Title** (700–800, 18–24px, 1.3): Card and section headings.
- **Body** (400, 15px, 1.6): Paragraph copy. The global default set on `body`.
- **Label** (700–800, 11–14px, 1.4): The workhorse. Table cells, field labels, chips, buttons,
  metadata, list rows — most of the interface is here.
- **Eyebrow** (700, 11px, uppercase, 0.08em): The small green kicker above page titles.
- **Mono** (400, 13px): Export dialogs and developer panels only.

### Named Rules

**The Weight-Before-Size Rule.** Hierarchy is established by weight first and size second. Stepping
13px/700 up to 13px/800 is the system's normal move; jumping to 20px is not. Only seven rules in
the entire codebase use weight 400 outside body copy.

**The No Second Family Rule.** Two families, one for UI and one for code. A decorative third face
belongs nowhere in the app. The landing page's Georgia step-numbers are a documented exception, not
a licence.

## Layout

The authenticated app is a fixed sidebar shell with a scrolling content column; public routes render
a plain full-width view. A 60px top bar (`--sb-topbar-height`) and 3rem main padding
(`--sb-main-padding`) set the outer frame. Content columns cap at roughly 1180px and centre.

Bootstrap 5 supplies the grid and utility layer; the `--sb-*` tokens and `.sb-*` utilities extend it
rather than replace it. Custom utilities (`.sb-surface`, `.sb-text`, `.sb-muted`, `.sb-card-surface`,
`.text-sb-primary`) exist so components can reach tokens through Bootstrap-shaped class names.

Spacing rhythm runs on a small scale — `0.45rem` for inline gaps, `0.72rem` / `1rem` for control
padding, `1.5rem` for panel padding, `3rem` for page gutters. Cards and panels commonly use a
20–28px internal pad.

**Density mode.** The system ships a genuine compact mode: `[data-sb-density='compact']` sets
`--sb-density-scale: 0.8` and applies CSS `zoom` to `#app`. Because zoom breaks viewport units,
roughly twenty companion rules divide `100vh`/`100vw` back out via `--sb-vh-fix` / `--sb-vw-fix` for
every full-height shell and modal. Zoom is scoped to `#app` rather than `:root` so Bootstrap's
body-level backdrops still align to the true viewport.

Responsive behaviour breaks at 640px for dialogs and around 860px for two-column panel layouts,
collapsing to single column.

### Named Rules

**The vh Debt Rule.** Any new full-height shell or modal added under compact density must register a
`--sb-vh-fix` counterpart. A raw `100vh` inside `#app` renders 25% too tall at 0.8 zoom.

## Elevation & Depth

Depth is a response, not a decoration. Surfaces sit nearly flat at rest — the resting shadow is 6%
alpha — and lift only when the visitor reaches for them. `.sb-elevated` implements this precisely:
the rest shadow sits on the element, the hover shadow lives on a `::after` pseudo-element at
`opacity: 0`, and hover crossfades the opacity rather than animating the shadow itself.

Depth is reinforced by tone as much as shade. The aurora wash gradients tint whole regions, and
glass surfaces use `color-mix` to sit translucently over them.

### Shadow Vocabulary

- **Rest** (`0 6px 16px rgba(15, 23, 42, 0.06)`): The default resting state of an elevated surface.
  Barely visible by intent.
- **Hover** (`0 16px 36px rgba(15, 23, 42, 0.12)`): Crossfaded in on hover via `::after`.
- **Brand Rest** (`0 8px 18px rgba(0, 137, 90, 0.20)`): For primary buttons and brand surfaces, so
  the shadow carries the green rather than neutral grey.
- **Brand Hover** (`0 14px 30px rgba(0, 137, 90, 0.28)`).
- **Glass** (`0 24px 70px rgba(15, 23, 42, 0.1)`): Wide, soft, and diffuse — used only on
  `.glass-segment` panels.
- **Halo** (`0 0 0 4px rgba(0, 137, 90, 0.12)`): The focus ring, not a shadow in spirit.

### Named Rules

**The Intent Rule.** A shadow answers an intent. If a surface is not hoverable, focusable, or
floating above the page, it gets no shadow — it gets a hairline border instead.

## Shapes

The form language is overwhelmingly round. A 999px pill is the default for anything interactive:
buttons, chips, badges, filter toggles, avatars, and tags. Rectangular radii are reserved for
containers, and they step in a tight range — 10px and 12px for small surfaces and skeletons, 14px
for compact cards, 18px for the standard card, and 24px for the large glass panels.

Borders are hairlines (1px) in near-neutral tones, frequently softened further with `color-mix` to
sit at 82–90% opacity against a tinted background. There are no heavy rules, no double borders, and
no square corners anywhere in the authenticated app.

### Named Rules

**The Pill-Or-Card Rule.** If it is interactive and inline, it is a pill (999px). If it is a
container, it is a card (14–24px). There is no third shape.

## Components

The character across the set is tactile and responsive: everything answers when touched. The shared
motion contract lives on three classes — `.sb-btn` and `.sb-pill` lift 4px, `.sb-interactive` lifts
6px, and all three scale to 0.97 on press over 70ms. All of it is suppressed under
`prefers-reduced-motion`.

### Buttons

- **Shape:** Full pill (`999px`), minimum height 42px, padding `0.72rem 1rem`, weight 850.
- **Primary:** Deep Campus Green on white text with a brand-tinted shadow
  (`0 16px 32px rgba(0, 137, 90, 0.2)`). Hover shifts to Campus Green Hover.
- **On-Brand:** White fill with dark green text (`#07543a`). Exists for CTAs sitting on a saturated
  green hero, where a green button would disappear.
- **Soft:** An 8% ink tint with a hairline border, deepening to 14% on hover. The default secondary.
- **Danger Soft:** A 12% danger tint with a 30% danger border, deepening to 18% on hover. Destructive
  actions are never solid red.
- **Link:** Text in Deep Campus Green with a 1px underline border.
- **Hover / Press:** Lift 4px on hover; scale 0.97 on press. Disabled drops to 0.4 opacity and
  `pointer-events: none`.

### Chips & Pills

- **Style:** Pill geometry, small heavy label (11–13px, 600–700).
- **Selected:** A 2px Deep Campus Green outline at 2px offset — applied via `.sb-pill` on `.active`,
  `[aria-pressed="true"]`, `[aria-selected="true"]`, `[aria-checked="true"]`, and `[aria-current]`.
  Selection is an outline, never a fill swap, so the label never has to change colour to stay legible.

### Badges

- **Style:** Green Tint background, Deep Campus Green text, a soft green border, 999px, 11px/500,
  `3px 10px` padding. Used for subject tags and status markers.

### Cards / Containers

- **Corner Style:** 18px standard; 14px compact; 24px for glass panels.
- **Background:** Surface white on the Canvas floor.
- **Shadow Strategy:** None at rest beyond a hairline border. Lift 6px on hover, and only when the
  card is genuinely interactive — `.sb-card-static` opts out.
- **Border:** 1px Hairline.
- **Internal Padding:** 20–28px.

### Glass Segment

A distinctive shared surface (`.glass-segment` / `.sb-glass-segment`): 24px radius, 1.5rem padding,
and a translucent fill built with `color-mix` — 84% card background, 82% border — over a wide soft
shadow. It is how profile and session-detail pages sit on top of the aurora wash without blocking it.

### Inputs / Fields

- **Style:** Bootstrap form controls with the `.sb-field` behaviour layer.
- **Focus:** Border shifts to Deep Campus Green and a 4px green halo appears
  (`0 0 0 4px rgba(0, 137, 90, 0.12)`). Transition is explicitly disabled on fields so focus is
  instant.
- **Global focus-visible:** Every link, button, input, select, textarea and `[tabindex]` gets a 4px
  green outline at 2px offset. This is set once with `:where()` so components never restate it.

### Navigation

- **Style:** Fixed sidebar, Ink surface, icon-plus-label rows using Bootstrap Icons.
- **States:** Active rows carry the green tint; hover lifts per the shared control contract.
- **Mobile:** Collapses to an offcanvas panel.

### Motion

One spring — `cubic-bezier(0.16, 1, 0.3, 1)` — and two durations: 130ms quick and 180ms normal.
Route changes fade and rise 8px on enter, fade on leave. Named keyframes cover the recurring
moments: `sb-bubble-in`, `sb-pop`, `sb-shake`, `sb-stagger-in`, `sb-scale-in`, `sb-toast-in`, and
`sb-success-border`. Modals scale in; lists stagger.

### Named Rules

**The One Spring Rule.** Every transition uses `--sb-spring` at `--sb-t-quick` or `--sb-t-normal`.
A bespoke cubic-bezier or a 300ms duration is drift, not expression.

## Do's and Don'ts

### Do

- **Do** reach for tokens from `src/assets/main.css` (`var(--sb-primary)`, `var(--sb-card-border)`,
  `var(--sb-text-muted)`) rather than typing a hex value. `tokens.test.js` enforces this.
- **Do** use 999px for anything interactive and inline; 14–24px for containers.
- **Do** establish hierarchy with weight before size — 13px/800 over 20px/600.
- **Do** put new components on the shared motion contract by adding `.sb-btn`, `.sb-pill`, or
  `.sb-interactive` instead of writing a new transition.
- **Do** use `color-mix` against a token for tinted fills and softened borders, the way `.sb-btn-soft`
  and `.glass-segment` do.
- **Do** declare a private token inside the component when it is genuinely component-scoped — the
  test allows this, and it is preferable to a raw literal.
- **Do** register a `--sb-vh-fix` rule when adding a full-height shell or modal, or it will break at
  compact density.

### Don't

- **Don't** read a `--sb-*` token that is not declared in `main.css` or the component itself. In
  particular, **`src/assets/admin.css` is never imported** — its `--sb-surface-container-*`,
  `--sb-primary-deep`, `--sb-warning`, `--sb-ink` and `--sb-outline` tokens resolve to `unset`.
  This is the exact bug the previous design document caused.
- **Don't** redefine a core token (`--sb-primary`, `--sb-primary-hover`, `--sb-card-bg`,
  `--sb-card-border`, `--sb-text-main`, `--sb-green-tint`) to a literal colour inside a component.
  It makes the whole subtree immune to theming, and the test fails on it.
- **Don't** colour a control with an Aurora Pop. They belong in `--sb-wash-blob-*` only.
- **Don't** assume a success token exists. There is no `--sb-success`; the four-status ramp is
  asserted by a currently-failing test and is intended, not implemented.
- **Don't** introduce a new radius. The scale is 10/12/14/18/24 and 999.
- **Don't** add a resting shadow to a non-interactive surface — use a hairline border.
- **Don't** write a new `font-family` stack. Use `var(--sb-font-base)` or `var(--sb-font-mono)`.
- **Don't** apply these rules to `src/views/LandingPage.vue`. It sits outside the token system by
  product decision (ADR-0012) and keeps its own system-ui body font and Georgia step-numbers.
  Extending the tokens into it is a separate decision, not a cleanup.
- **Don't** treat dark mode as finished. `[data-sb-theme="dark"]` defines a partial override set,
  and the test asserting a dark counterpart for every colour token is skipped. Adding a light-mode
  colour token without a dark counterpart deepens that debt.

## Known drift

Recorded deliberately, because a design document that hides drift is how the previous one caused a
bug.

1. **`admin.css` is dead.** 131 lines of Material-style surface tokens that no entry point imports.
   UI written against it silently renders with `unset` values.
2. **Dark mode is partial.** The override block covers colour and shadow tokens but not the full
   `:root` set; its enforcing test is skipped.
3. **The status ramp is aspirational.** `tokens.test.js` demands success/warning/danger/info across
   four slots each; five status tokens exist.
4. **`--sb-green-tint` has no global home.** It is redeclared in five components
   (`AppSidebar`, `AuthShell`, `Dashboard`, `TuteeProfile`, `TutorProfile`) rather than defined once
   in `main.css`, and one of those redefinitions is explicitly allow-listed in the test.
5. **The landing page is a sanctioned exception**, not drift — but it is a divergence, and new work
   should not use it as a reference for the app's typography.
