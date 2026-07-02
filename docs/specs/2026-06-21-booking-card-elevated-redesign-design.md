# Booking card "elevated avatar" redesign — Design Spec

Date: 2026-06-21
Status: Approved
Reference artifact: Option A from a 3-option visual-companion mockup session
(`.superpowers/brainstorm/277-1781978136/content/booking-card-options.html`)

---

## Overview

Restyle the shared `BookingCard` (the inline booking card rendered in
[`Chat.vue`](../../src/views/Chat.vue) for every booking status — Pending,
Confirmed, Rejected, Cancelled, Completed, Awaiting Payment Verification) from
the current flat card + thin left-accent stripe (shipped in
[2026-06-15-chat-banner-card-redesign.md](../plans/2026-06-15-chat-banner-card-redesign.md))
to the "elevated avatar" treatment picked from the mockup session: a soft
shadow, a colored icon-avatar circle carrying the status instead of a left
border line, a status pill in the header's top-right corner, and a divider
line separating the meta grid from the footer.

This is a **visual-only** restyle. No changes to props, emits, accept/reject/
edit-location logic, or the `ChatBanner.vue` sibling component (separate
plan/scope — not touched here).

---

## Goals

- Replace the "plain"-looking flat card (flagged by the user from a live
  screenshot of the Rejected state) with a more designed, less generic look.
- Keep the redesign consistent across **all** status variants the card
  renders — not just Rejected — since `BookingCard` is one shared component.
- Stay within the existing CSS variable system (`--sb-primary`,
  `--sb-card-border`, `--sb-warning-bg`, `--sb-info-bg`, `--sb-danger-bs`,
  etc.) — no new hardcoded hex values.

## Out of scope

- `ChatBanner.vue` (the accept/reject status bar above the thread) — visually
  distinct component, not part of this pass.
- Any change to what data is shown, when the card renders, or its
  interactive behavior (location edit, "View session details" link target).
- Dark mode tuning beyond reusing existing variables (no dedicated dark-mode
  pass — same risk profile as the prior compact-timeline redesign).

---

## Current structure (for reference)

`BookingCard` is a `defineComponent` render-function component inside
`Chat.vue` (around line 305), not a separate SFC. Structure today:

```
article.booking-card[.booking-card--{accent}][.compact]
  div.booking-card-header
    div
      span.booking-eyebrow.booking-card--{accent}   (status text)
      h4                                             (subject)
    span.mode-pill                                   (Online/F2F)
  div.booking-grid                                   (date / time / duration / location icons+text)
  div.booking-card-footer                            (location-editor and/or "View session details")
```

Status → accent map (`statusAccent`, line ~343): `Pending → warning`,
`Confirmed → primary`, `Completed → info`, `Awaiting Payment Verification →
info`, `Rejected → danger`, `Cancelled → danger`. This map is reused as-is —
only what the accent *renders as* changes.

---

## New structure

```
article.booking-card[.booking-card--{accent}][.compact]
  div.booking-card-header
    div.booking-card-headtext
      span.booking-avatar.booking-card--{accent}     (icon circle, status-colored)
      div
        h4                                            (subject)
        span.booking-card-mode                        (Online/F2F, moved under title)
    span.booking-pill.booking-card--{accent}          (status text, top-right corner)
  div.booking-grid                                    (unchanged: date / time / duration / location)
  div.booking-card-footer                             (unchanged content, new divider above it)
```

Key visual changes from current:

1. **Card surface**: drop `border-left: 3px solid <accent>`; add
   `box-shadow: 0 4px 14px rgba(20, 30, 40, 0.08)` and a faint all-around
   border (`1px solid rgba(20, 30, 40, 0.04)`) so the card reads as
   elevated rather than flat-bordered. Keep `border-radius: 14px`.
2. **Status avatar** (new `.booking-avatar`): 38px circle, status icon
   centered (reuse the icon-per-status mapping already used in
   `ChatBanner.vue`'s analogous templates: `bi-calendar-check-fill`
   confirmed, `bi-x-circle-fill` rejected, `bi-slash-circle-fill`
   cancelled, `bi-hourglass-split` pending, `bi-clock-history` awaiting
   payment, `bi-star-fill`/`bi-check2-circle` completed), background tint
   + icon color from the accent family (e.g. `rgba(220,53,69,0.1)` bg /
   `var(--sb-danger-bs)` icon for danger).
3. **Mode moves under the title** as a small muted line (`Online`/`F2F`)
   instead of a separate pill on the right — the right side is now owned by
   the status pill.
4. **Status pill** (renamed from `.booking-eyebrow` to `.booking-pill`,
   same accent-tinted-background pattern already defined for
   `.booking-eyebrow.booking-card--*`): moves to the header's top-right,
   replacing the former `.mode-pill` slot.
5. **Footer divider**: add `border-top: 1px solid var(--sb-card-border)` +
   `padding-top: 10px` above `.booking-card-footer` so it's visually
   separated from the meta grid, per the mockup.
6. **`.booking-grid` and footer contents unchanged** — same icons, same
   "View session details" link, same location-editor markup/logic.

No new CSS variables are introduced; accent backgrounds/icon colors reuse the
same `rgba(...)` values and `var(--sb-warning-bg|text)`, `var(--sb-primary)`,
`var(--sb-info-bg)`, `var(--sb-danger-bs)` already used for
`.booking-eyebrow.booking-card--*` and `ChatBanner.vue`'s icon-per-status
rules — just applied to a circle instead of a flat badge background.

---

## Icon mapping (new)

Today `BookingCard` has no per-status icon — only `ChatBanner.vue` does. This
redesign adds one to `BookingCard`'s render function, mirroring
`ChatBanner.vue`'s existing icon choices so the same status always shows the
same icon across both components:

| `booking.status` | Icon | Accent family |
|---|---|---|
| `Pending` | `bi-hourglass-split` | warning |
| `Confirmed` | `bi-calendar-check-fill` | primary |
| `Completed` | `bi-check2-circle` | info |
| `Awaiting Payment Verification` | `bi-clock-history` | info |
| `Rejected` | `bi-x-circle-fill` | danger |
| `Cancelled` | `bi-slash-circle-fill` | danger |
| *(fallback)* | `bi-calendar3` | neutral |

---

## Risks

- `BookingCard` is a render-function component (`h(...)` calls), not a
  template — the header/avatar/pill restructuring has to be done in
  JS-object form, which is more error-prone to hand-edit than SFC markup.
  Go slowly, diff the render tree before/after.
- The status pill's new top-right position must still wrap/stack sensibly on
  narrow chat widths (existing `@media (max-width: 700px)` rules on the
  sibling `ChatBanner.vue` stack to column — confirm `BookingCard` has or
  needs an equivalent mobile rule, since it currently has none beyond
  `.compact { margin-top: 10px }`).
- Confirm icon-color contrast on the new tinted circle backgrounds across
  all 6 status/accent combinations (reuse, don't recolor, the existing
  `rgba` tint values already validated in `.booking-eyebrow.booking-card--*`).

## Checks to run

- `npm run lint` — no new lint errors.
- `npm run build` — production build succeeds.
- Manual preview: render a Pending, Confirmed, Rejected, and Cancelled
  `BookingCard` inline in chat; confirm avatar icon/color, top-right pill,
  footer divider, and "View session details" link all render correctly, and
  the layout doesn't break under `@media (max-width: 700px)`.
