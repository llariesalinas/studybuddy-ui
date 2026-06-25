---
title: Booking card "glow avatar" redesign
date: 2026-06-22
status: Done
spec: this document
---

# Booking Card "Glow Avatar" Redesign

> **Implemented:** 2026-06-22. See the
> [implementation plan](../plans/2026-06-22-booking-card-glow-avatar-redesign.md) and
> [completion summary](../session-summaries/2026-06-22-booking-card-glow-avatar-redesign-summary.md).

> **Visual reference:** Option C ("Glow avatar + pill") from a 3-option visual-companion
> mockup session held during brainstorming
> (`.superpowers/brainstorm/1738-1782119429/content/card-styles.html`).

---

## Overview

Restyle the shared `BookingCard` (the inline card rendered inside the chat
thread's system-event bubble in [`Chat.vue`](../../src/views/Chat.vue), for
every booking status — Pending, Confirmed, Rejected, Cancelled, Completed,
Awaiting Payment Verification) from the current flat icon-avatar + pill card
(shipped after [2026-06-21's elevated-avatar
spec](2026-06-21-booking-card-elevated-redesign-design.md)) to a more
polished "glow avatar" treatment: a soft accent-tinted shadow, a
rounded-square icon avatar with a tinted gradient background, and a tinted
panel behind the date/time/duration/location row.

The user flagged the current card as "all of the above" — flat, weak
hierarchy, cramped/awkward spacing, and generically undesigned — from a live
screenshot of a Confirmed booking card. Three directions (banner header,
timeline rail, glow avatar) were mocked up with real data; the user picked
the glow-avatar direction (Option C).

This is a **visual-only** restyle. No changes to props, emits, accept/reject/
edit-location logic, or any sibling component.

---

## Goals

- Replace the current flat-shadow card with a more designed, depth-forward
  look: tinted shadow, rounded-square gradient-tint avatar, tinted meta
  panel.
- Keep the redesign consistent across **all** status variants the card
  renders (Pending, Confirmed, Rejected, Cancelled, Completed, Awaiting
  Payment Verification) — `BookingCard` is one shared component.
- Keep the accent swap **per status**, reusing the existing `statusAccent`
  map (`warning` / `primary` / `info` / `danger`) — shadow tint, avatar tint,
  and pill all recolor together, same behavior as today.
- Stay within the existing CSS variable system (`--sb-primary`,
  `--sb-card-border`, `--sb-warning-bg`, `--sb-info-bg`, `--sb-danger-bs`,
  etc.) — no new hardcoded hex values.
- The avatar square is **always a status icon** (calendar-check, hourglass,
  x-circle, etc., from the existing `statusIcon` map) — never a tutor/tutee
  photo. This was a point of explicit confirmation during design, not a
  behavior change.

## Out of scope

- `ChatBanner.vue` and the surrounding `system-event` wrapper / label
  ("Booking request approved.", etc.) above the card — untouched, separate
  component.
- Any change to what data is shown, when the card renders, or its
  interactive behavior (location edit, "View session details" link target).
- A separate full-size (non-`compact`) variant. `BookingCard` is only ever
  rendered with the `compact` prop (one call site, `Chat.vue:106`) — this
  redesign **is** the compact style; there is no other rendering mode to
  preserve or maintain.
- Dark mode tuning beyond reusing existing variables (no dedicated dark-mode
  pass — same risk profile as prior booking-card redesigns).

---

## Current structure (for reference)

`BookingCard` is a `defineComponent` render-function component inside
`Chat.vue` (around line 305), not a separate SFC. Structure today (post
2026-06-21 elevated-avatar spec):

```
article.booking-card[.booking-card--{accent}][.compact]
  div.booking-card-header
    div.booking-card-headtext
      span.booking-avatar.booking-card--{accent}   (icon circle, status-colored)
      div
        h4                                          (subject)
        span.booking-card-mode                      (Online/F2F)
    span.booking-pill.booking-card--{accent}        (status text, top-right)
  div.booking-grid                                  (date / time / duration / location icons+text)
  div.booking-card-footer                           (location-editor and/or "View session details")
```

Status → accent map (`statusAccent`, line ~343): `Pending → warning`,
`Confirmed → primary`, `Completed → info`, `Awaiting Payment Verification →
info`, `Rejected → danger`, `Cancelled → danger`. Status → icon map
(`statusIcon`, line ~355): `Pending → bi-hourglass-split`, `Confirmed →
bi-calendar-check-fill`, `Completed → bi-check2-circle`, `Awaiting Payment
Verification → bi-clock-history`, `Rejected → bi-x-circle-fill`, `Cancelled →
bi-slash-circle-fill`, fallback `bi-calendar3`. Both maps are reused as-is —
only what the accent/icon *render as* changes.

---

## New structure

```
article.booking-card[.booking-card--{accent}]
  div.booking-card-head
    div.booking-card-avatar.booking-card--{accent}   (rounded-square, gradient tint bg, icon)
    div.booking-card-headtext
      h4                                              (subject)
      span.booking-card-mode                          (Online/F2F, unchanged position)
    span.booking-card-pill.booking-card--{accent}     (status text, top-right, unchanged position)
  div.booking-card-grid.booking-card--{accent}         (date / time / duration / location, on tinted panel)
  div.booking-card-footer                              (unchanged content, right-aligned link + arrow icon)
```

Key visual changes from current:

1. **Card surface**: keep `border-radius: 14px`-ish (bump to 16px to read
   softer), drop the flat `box-shadow` for a **two-layer tinted** one —
   `box-shadow: 0 10px 26px <accent-rgba-~8%>, 0 2px 6px <neutral-rgba-~5%>`
   (colored glow + neutral ambient depth, matching the picked Option C
   mockup's layered shadow, not a single flat tint) — plus a faint
   accent-tinted border (`1px solid <accent-rgba-at-~12%-opacity>`) instead
   of the current flat `var(--sb-card-border)`. Each accent family gets its
   own shadow/border tint (warning/primary/info/danger/neutral), not one
   fixed color. Card padding bumps from `14px` to `16px` to match the
   mockup's slightly airier feel.
2. **Avatar** (rename `.booking-avatar` → `.booking-card-avatar`): change
   from a 38px **circle** to a 38–40px **rounded-square** (`border-radius:
   12-14px`), background becomes a soft two-stop gradient of the accent
   tint (e.g. `linear-gradient(135deg, <accent-rgba-16%>, <accent-rgba-6%>)`)
   instead of a flat tint, icon color unchanged (`var(--sb-*)` per accent).
   Icon mapping (`statusIcon`) is unchanged — still purely an icon.
3. **Status pill**: keep `.booking-pill` → rename to `.booking-card-pill`
   for naming consistency with the new `.booking-card-*` prefix; same
   accent-tinted-background visual pattern and top-right position as today,
   but soften the typography to match the mockup's pill (not the old
   "eyebrow" badge look): drop `text-transform: uppercase` and
   `letter-spacing`, bump `font-size` 10px → 11.5px, `font-weight` 800 →
   700, `padding` 3px 9px → 4px 11px.
4. **Meta grid becomes a tinted panel**: wrap the existing `.booking-grid`
   content in a panel with a light neutral background (e.g.
   `rgba(15, 23, 42, 0.03)` light / appropriate dark-mode equivalent token
   if one exists) and `border-radius: 12px`, internal padding `~10px 12px`,
   to separate it visually from the header and footer and improve
   scannability. Same icons/text/order as today (date, time, duration,
   location-when-F2F).
5. **Footer**: keep existing content (location editor and/or "View session
   details" link) and the divider above it (`border-top`), but right-align
   the "View session details" link and add a trailing arrow icon
   (`bi-arrow-right`) for affordance. Location-editor markup/logic
   unchanged.
6. **Class naming**: this pass also normalizes the `.booking-*` prefix to
   `.booking-card-*` for the elements introduced/touched here
   (`.booking-card-avatar`, `.booking-card-pill`, `.booking-card-grid`,
   `.booking-card-head`) for consistency with `.booking-card-footer` /
   `.booking-card-mode`, which already use that prefix. `.booking-card`
   itself and the `statusAccent`/`statusIcon` computed maps are unchanged.

No new CSS variables are introduced; accent shadow/border/avatar-gradient
tints are derived from the same `rgba(...)` base values already validated
for `.booking-pill.booking-card--*` per accent family, just at different
opacity stops for shadow (~8-10%), border (~12%), and avatar gradient
(~6-16%).

---

## Accent reference (per status, for shadow/border/avatar gradient stops)

| Accent family | Statuses | Base color source |
|---|---|---|
| `warning` | Pending | `var(--sb-warning-bg)` / its paired text/icon color |
| `primary` | Confirmed | `var(--sb-primary)` |
| `info` | Completed, Awaiting Payment Verification | `var(--sb-info-bg)` |
| `danger` | Rejected, Cancelled | `var(--sb-danger-bs)` |
| `neutral` (fallback) | any unmapped status | existing neutral fallback already used by `statusAccent` |

---

## Risks

- `BookingCard` is a render-function component (`h(...)` calls), not a
  template — the header/avatar/grid/footer restructuring and class renames
  have to be done in JS-object form, which is more error-prone to hand-edit
  than SFC markup. Go slowly, diff the render tree before/after.
- Renaming `.booking-avatar` → `.booking-card-avatar` and `.booking-pill` →
  `.booking-card-pill` means the corresponding CSS selectors in `Chat.vue`'s
  `<style>` block must be renamed in lockstep with the render function, or
  the new markup will render unstyled. Grep for both old class names after
  the edit to confirm no stale references remain.
- Confirm shadow/border/avatar-gradient contrast and legibility across all 5
  accent families (warning/primary/info/danger/neutral) — especially that
  the new tinted shadow doesn't look muddy against the chat thread's
  background, and that the avatar gradient still has enough icon contrast
  at the lighter gradient stop.
- The new tinted meta-grid panel needs a value that holds up in dark mode if
  this component renders there — confirm whether an existing dark-mode
  token covers a "light neutral panel" use case, or whether a `prefers-color-scheme`/
  dark-mode override is needed (out of scope to design new dark-mode tokens
  here; reuse what exists or flag if nothing fits).
- Card only ever renders `compact` — confirm no other code path expects
  `.booking-card:not(.compact)` styling that this redesign might silently
  break if such a rule still exists from before this card had only one call
  site.

## Checks to run

- `npm run lint` — no new lint errors.
- `npm run build` — production build succeeds.
- Manual preview: render a Pending, Confirmed, Rejected, Cancelled,
  Completed, and Awaiting Payment Verification `BookingCard` inline in a
  chat thread; confirm avatar gradient/icon, tinted shadow/border, top-right
  pill, tinted meta panel, and right-aligned "View session details" link
  (with arrow icon) all render correctly per accent family, and the layout
  doesn't break at narrow chat widths (existing `@media (max-width: 700px)`
  rules on `Chat.vue`).
