# Landing Page Redesign — "Studio Motion" Design Spec

Date: 2026-06-11
Status: Approved (design signed off in mockup form)
Reference artifact: `docs/artifacts/2026-06-11-landing-redesign-reference.html`
(open via `python -m http.server` or the `landing-mockups` entry in `.claude/launch.json`;
exploration mockups live in `docs/design/2026-06-11-landing-redesign-mockups/`)

## Overview

Replace the current `src/views/LandingPage.vue` with a premium "studio site" landing page:
oversized typography, lerped smooth scrolling, a reactive custom cursor, scroll-driven
character animations, and an aurora background — all built on the existing Studybuddy
design system (Inter, `--sb-*` tokens, white cards, dark CTA panel) with zero new
dependencies.

Key decisions made during design review:

- Copy is campus-agnostic. No mention of CPU anywhere; the platform is open to any campus.
- No fake social proof. The old stats strip (500+ tutors) and testimonials are dropped;
  a count strip of product facts (20s / 98% / 1 min) replaces them.
- The platform-tools section and FAQ ("Common questions") were re-added on 2026-06-11
  with new copy. After several layout iterations (flat 4-card grid, bento, pinned
  scrubbed assembly), the tools section's final form is a **pinned horizontal rail**
  (structure item 5). The multi-column footer stays dropped; footer is a single line.
- Illustrations are inline SVG "doodle" characters (hand-drawn hair, eyebrows, blush,
  glasses, hair bun) inside clean white cards — playful characters, clean chrome.

## Page structure (top to bottom)

1. **Nav** — fixed; brand mark + "Log in" (outline pill) + "Get started" (primary pill).
   Keep the existing theme toggle from the current landing nav.
2. **Hero** — full viewport. Kicker "PEER TUTORING — BY STUDENTS, FOR STUDENTS";
   H1 "Learn it from someone who *just aced it.*" (3 masked lines, staggered reveal;
   "just aced it." in `--sb-primary`); sub-paragraph; "Find my tutor" / "Become a tutor"
   CTAs; animated scroll cue (label + 44px bar with a sweeping fill).
3. **Marquee** — full-width strip, white bg, 1px borders:
   "Get matched · Study together · *Actually get it* · Tutors earn · Your campus, your
   buddies" with colored dot separators (yellow/pink/orange/green). Loops seamlessly.
4. **Panels (01–03)** — three rows, grid `90px 1fr 1fr` (index / copy / illustration card):
   - 01 "Share what you need." — "Choose a subject, topic, and goal so Studybuddy can
     surface the right peers." — subject-picker illustration (chips + time pill + arrow)
   - 02 "Match and book." — "Compare tutor fit, availability, and ratings, then reserve
     a time that works." — two doodle avatars, dashed connector, star check, "98% match"
   - 03 "Learn and track." — "Wrap each session with history, compensation, and progress
     details in place." — two figures at a table, lightbulb, "Got it!"
5. **Platform tools — pinned horizontal rail** — kicker "PLATFORM TOOLS"; H2 "Everything
   the tutoring loop needs." (masked line reveal); sub "Built for peer learning programs
   that need matching, scheduling, reporting, and fair tutor visibility." The page then
   anchors for ~2 viewport-heights (300vh stage) while a rail of four white slabs rides
   right-to-left through the frame. Each slab is a `60vw x >=30vh` banner laid out as
   `numeral | title + copy | illustration`:
   - numeral: italic serif watermark (Georgia stack, 90-140px, 700 italic) in the slab's
     accent color at 20% opacity — the only color on the otherwise standard white card
   - title 34-58px (900, -0.035em) / body 17-21px, max measure 560px
   - object doodle on the right (120-180px wide; objects only, NO characters/stick
     figures), ink-stroke style, split into 2-3 `.char` wiggle groups (amps 2.5-5):
     01 magnifier with a star in the lens + star/sparkle accents ·
     02 calendar with a circled checked date + floating clock ·
     03 rising bar trio (pink/yellow/green), dashed trend arrow, coin ·
     04 level balance scale with green and pink weights
   Copy per slab: Smart tutor matching "Rank peer tutors by subject fit, ratings,
   availability, and workload balance." · Flexible scheduling "Book around real tutor
   availability and keep upcoming sessions easy to scan." · Reports and earnings "Track
   completed sessions, tutor compensation, and program-level performance." · Balanced
   workloads "Protect session quality by keeping tutor demand visible before calendars
   fill up." Per-slab colored hover shadows (green/amber/coral/pink). On touch,
   <900px, or reduced motion: no pin — slabs stack as a normal vertical column.
6. **Count band** — full-width band (`--sb-primary` at ~4.5% alpha, hairline top/bottom
   borders) holding three left-bordered numbers that count up on reveal (54-96px,
   3px accent bar, 130px vertical padding):
   `20s` to tell us what's hurting · `98%` match scores, out in the open ·
   `1 min` to join with your student email.
7. **Common questions (FAQ)** — kicker "COMMON QUESTIONS"; H2 "Asked a lot, answered
   straight." (masked line reveal); 4 accordion items (38px row padding, ~170px section
   padding), staggered reveal:
   - 01 Who can become a tutor?
   - 02 How much does it cost?
   - 03 Can I use it on my campus?
   - 04 What happens if a session falls through?
   (answers in the reference artifact)
8. **CTA panel** — `--sb-dark` rounded panel, radial green glow, H2 "Your study buddy is
   *already on campus.*" (em in `--sb-pop-yellow`), magnetic "Get started" button.
9. **Footer** — single line: "Studybuddy — built by students, for students. Bring it to
   your campus."

All "Get started"/"Find my tutor" CTAs route to `/register`; "Log in" routes to `/login`
(`router.push`, same as the current page).

## Design tokens

Existing tokens are used throughout (`--sb-primary`, `--sb-bg`, `--sb-card-bg`,
`--sb-card-border`, `--sb-text-main`, `--sb-text-muted`, `--sb-dark`, `--sb-spring`).

New accent tokens to add to `src/assets/main.css` (light mode values; pick dimmed
equivalents for `[data-sb-theme="dark"]`):

| Token | Value | Used for |
|---|---|---|
| `--sb-pop-yellow` | `#FFC94D` | hero underline, marquee dots, star checks, CTA em |
| `--sb-pop-orange` | `#FF8A5C` | lightbulb rays, card-3 shadow hue, aurora band |
| `--sb-pop-pink` | `#FF8FA3` | character blush, marquee dot, aurora band |
| `--sb-aurora-violet` | `#8E7CF4` | aurora band 2 only (new hue; aurora needs it) |
| `--sb-pop-yellow-deep` | `#DCA21B` | rail numeral 02 (text-safe dark variant of pop-yellow) |
| `--sb-pop-orange-deep` | `#E0683A` | rail numeral 03 (text-safe dark variant of pop-orange) |
| `--sb-pop-pink-deep` | `#E26D86` | rail numeral 04 (text-safe dark variant of pop-pink) |

No hardcoded hex in the component — SVG fills/strokes use classes bound to these vars.
The rail numerals use a serif stack (`Georgia, 'Times New Roman', serif`, italic 700) —
the page's single intentional departure from Inter; no webfont is loaded for it.

## Aurora background

Fixed full-viewport layer behind everything (`z-index: 0`, content above), composed of:

- Base: vertical gradient `#F1FAF6 0% → --sb-bg 40% → #FDF9F1 100%` (tokenize these too).
- Three ribbon `<i>` elements, each ~135–150vw wide, 50–58vh tall, soft radial-gradient
  blends, rotated diagonally, animated `transform`-only on slow alternating loops:
  - b1 (top, rotate -14°): green `.18` + teal `.15` + yellow `.13`, 36s
  - b2 (middle right, rotate 10°): violet `.11` + pink `.13`, 44s
  - b3 (bottom, rotate -6°): orange `.11` + green `.14`, 40s
- Keyframes drift/rotate/scaleY slightly (see artifact `@keyframes sway1/2/3`).
- Note: the app already has a global aurora on `body > #app::before`
  (see `docs/plans/2026-06-07-aurora-hue-restoration.md`). The landing page must not
  double-stack: suppress the global one on the landing route or scope the ribbons to
  replace it there. Decide in implementation; do not render both.

## Motion inventory (exact parameters in the reference artifact)

| Behavior | Parameters | Gating |
|---|---|---|
| Lerped smooth scroll | content `position:fixed` + spacer div sets body height; `current += (target-current)*0.085`; rAF loop | fine pointer + no reduced motion; otherwise native scroll |
| Custom cursor | 14px `--sb-primary` dot, lerp 0.2, grows to 56px yellow over links/cards; `mix-blend-mode: multiply` | fine pointer only |
| Hero H1 reveal | 3 lines in `overflow:hidden` rows, `translateY(112%) → 0`, 1s `--sb-spring`, 80ms stagger | reduced motion: static |
| Marquee | two identical halves, each with self-contained 56px gap + trailing padding; track `translateX(-50%)` 26s linear infinite. Halves MUST measure exactly 50% of track or the loop jumps | reduced motion: paused |
| Panel reveal | `clip-path: inset(12% 6% round 26px) → inset(0)`, 0.9s spring, on IntersectionObserver (threshold 0.25) | reduced motion: none |
| Illustration parallax | `data-depth` 0.06/0.09/0.07; translateY = -(element center − viewport center) × depth, in the rAF loop | reduced motion: off |
| Character wiggle | `.char` SVG groups (`transform-box: fill-box; transform-origin: center`); per group `rotate(sin(scroll/55 + i*1.7) * amp)` + `translateY(cos(scroll/48 + i*1.7) * amp*0.7)`; amps 2.5–6 via `data-amp`. Driven by smoothed scroll value, so they settle when scrolling stops | reduced motion: off |
| Card tilt (haptic) | per-card config — card1 `{max:7°, dir:+1, twist:0}`, card2 `{max:12°, dir:−1, twist:+1.4°}`, card3 `{max:9°, dir:+1, twist:−1.8°}`; `perspective(900px) rotateX/rotateY` from cursor position + `scale(1.025)`; springs back on leave (0.6s) | fine pointer + no reduced motion |
| Hover shadows | per-card colored: green `rgba(0,137,90,.22)` / amber `rgba(255,176,46,.30)` / coral `rgba(255,120,70,.28)` + neutral layer | — |
| Count-up numbers | 0 → target over 1100ms, cubic ease-out, triggered once on reveal | reduced motion: show final |
| Section-head reveals | tools + FAQ H2s use the hero's masked-row reveal (`translateY(112%) → 0`, 0.9s spring, 80ms stagger), triggered by IO on the section | reduced motion: static |
| Tools pinned rail | manual pin — 300vh stage; pin content counter-translated `translateY(y)` inside the shared rAF loop (CSS `position: sticky` CANNOT work inside the fixed+translated smooth wrapper); rail progress `rp = clamp((p - .05) / .85)` maps to `translateX(-rp * travel)` with a hold at both ends; `travel = track.scrollWidth - (innerWidth - 80)`, cached and re-measured only on init/resize — never per frame | fine pointer + no reduced motion; touch/<900px/reduced: static stacked column (`.nopin` class / media query) |
| Rail slab content | white card chrome (card bg/border/shadow); object-doodle illustrations ride the global `.char` wiggle loop (2-3 groups per slab, amps 2.5-5); hover: per-slab colored shadow only (no transform, so the scrub owns the geometry) | reduced motion: wiggle off |
| FAQ accordion | answer wrapper `grid-template-rows: 0fr → 1fr`, 0.5s spring; plus icon rotates 135° into a filled `--sb-primary` circle; question slides +10px and tints primary on hover; items stagger in (70ms) | reduced motion: no transitions, rows still toggle |
| Magnetic CTA | wrapper translates `(cursor − center) × 0.35`, springs back on leave | fine pointer only |
| Button hover fill | dark layer slides up inside pill, 0.35s spring | — |

## Responsiveness, themes, accessibility

- Breakpoint ~900px: panels stack to one column; smooth scroll, cursor, tilt, and
  parallax are disabled on touch (`pointer: fine` check) — phones get a normal page.
- `prefers-reduced-motion: reduce`: every animation above has a static fallback
  (final state shown, no loops, native scrolling).
- Dark mode: page must work under `[data-sb-theme="dark"]` using the dark token set;
  aurora ribbon opacities roughly halved; marquee strip uses `--sb-card-bg`.
- Semantics: one `h1`, sections with `h2`, nav/footer landmarks, focus styles on pills,
  `aria-hidden="true"` on the cursor dot, bgwash, and decorative SVGs.
- Lifecycle: ALL rAF loops, listeners (`scroll`, `resize`, `mousemove` — including the
  rail's resize re-measure), and the ResizeObserver must be torn down in `onUnmounted`
  so nothing runs after navigating to `/login` or `/register`.

## Performance budget

Zero new dependencies. All animation is `transform`/`opacity` (compositor-only).
Continuous rAF loops only while mounted and only on fine-pointer devices.
No raster images; all illustrations are inline SVG. Target: no long tasks > 50ms from
this page's scripts on a mid-range laptop, Lighthouse performance unaffected vs current.
