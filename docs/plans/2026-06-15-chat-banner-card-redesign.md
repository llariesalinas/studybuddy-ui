---
title: Chat banner & booking card compact-timeline redesign
date: 2026-06-15
status: Approved
spec:
---

# Chat banner & booking card compact-timeline redesign

## Status & Progress Summary

Implemented (Steps 1-5 done; `npm run lint` and `npm run build` pass for both
`ChatBanner.vue` and `Chat.vue`). Follow-up fix applied: the `pending` banner's
"Respond to request" boxed action panel was removed in favor of an inline
Accept/Reject button group, per user screenshot feedback. Manual preview (Step 6)
still pending - port 5173 is occupied by the user's own dev server, same as the
slot-clarity plan.

## Goal

Restyle the chat `ChatBanner.vue` (the accept/reject / status bar above the chat thread)
and the inline `BookingCard` (in `Chat.vue`) to match the "Compact timeline" mockup: denser
cards, a left accent stripe that encodes status, smaller icons/badges/buttons. Purely
visual - no changes to accept/reject/edit/confirm logic.

## Approach

- Reuse existing CSS variables only (no new hardcoded hex), mapping status families to a
  left-accent color:
  - warning family (`pending`, `pending_location`, `payment_required`, raw status
    `Pending`) -> `var(--sb-warning-bg)`
  - primary/confirmed (`confirmed`, raw status `Confirmed`) -> `var(--sb-primary)`
  - info family (`ongoing`, `awaiting_payment`, `review_pending`, raw status `Completed` /
    `Awaiting Payment Verification`) -> `var(--sb-info-bg)`
  - danger family (`rejected`, `cancelled`, raw status `Rejected` / `Cancelled`) ->
    `var(--sb-danger-bs)`
- `ChatBanner.vue`:
  - Re-read the file fresh first - it was just modified by the concurrent
    chat-accept-reject session (now Done), so the decision-card/loc-chip/accept-reject
    markup must be preserved.
  - `.chat-banner`: drop the gradient backgrounds + heavy box-shadow for a flat
    `var(--sb-card-bg)` surface, `1px solid var(--sb-card-border)`, `border-radius: 14px`,
    tighter padding (`10px 14px`), and a `border-left: 3px solid <accent>` per status.
  - Remove the per-status gradient background overrides (`.chat-banner--pending`, etc.)
    and replace with per-status `border-left-color` overrides only.
  - Shrink `.chat-banner__icon` (36px -> 30px, font-size 16px -> 14px) and `.chat-banner__btn`
    (font-size 13px -> 12px, padding `7px 16px` -> `7px 14px`, min-height 34px -> 30px).
  - Keep `.chat-banner__decision-card` / `.chat-banner__action--online` translucent panels,
    tighten padding slightly to match the denser feel.
- `Chat.vue` `BookingCard`:
  - Add a small status -> accent mapping keyed off `props.booking.status` (raw string:
    `Pending`, `Confirmed`, `Rejected`, `Cancelled`, `Completed`,
    `Awaiting Payment Verification`), reusing the same variables as above.
  - `.booking-card`: border-radius 8px -> 14px, `border-left: 3px solid <accent>`,
    border color -> `var(--sb-card-border)`.
  - `.booking-eyebrow`: restyle from plain uppercase text into a small pill badge using the
    accent's light tint + dark text.
  - When both the location editor and "View session details" link are present, lay them
    out in one flex row (`justify-content: space-between`) instead of two stacked blocks,
    matching the compact mockup; keep single-item layout when only one is present.

## Steps

1. Re-read `ChatBanner.vue` to confirm the current (post accept/reject) markup/CSS.
2. Add the status-accent mapping and rework `.chat-banner` base styles + per-status
   `border-left-color` rules in `ChatBanner.vue`.
3. Shrink `.chat-banner__icon` and `.chat-banner__btn` (and dependent `:hover`/`:disabled`
   rules stay as-is).
4. In `Chat.vue`, add the `BookingCard` status-accent computed and update `.booking-card`,
   `.booking-eyebrow`, and the footer row layout.
5. Run `npm run lint` and `npm run build`.
6. Manual preview check (subject to the port-5173 conflict noted in the slot-clarity plan):
   confirm a pending/F2F banner, a pending-online banner, and a booking card each render
   with the new compact styling and correct accent colors.

## Risks

- `ChatBanner.vue` was modified very recently by a concurrent session for the
  accept/reject feature - must diff against the current file, not a stale read, before
  editing.
- 8+ `status_intent` branches share `.chat-banner__icon` / `.chat-banner__badge` color
  rules tied to the old gradient backgrounds; need to confirm contrast still works on a
  flat white card with only a left accent.
- Longer raw statuses (e.g. "Awaiting Payment Verification") may not fit the
  `.booking-eyebrow` pill without wrapping - may need `white-space: nowrap` with
  `overflow: hidden`/ellipsis or a shortened label.

## Checks to run

- `npm run lint` - no new lint errors.
- `npm run build` - production build succeeds.
- Manual preview: pending F2F banner, pending online banner, confirmed/rejected banners,
  and an inline booking card all render with the compact left-accent style and correct
  colors per status.

## Changelog

- 2026-06-15: Plan written and approved after picking "Option 3 - Compact timeline" from
  a 3-option chat mockup.
- 2026-06-15: Implemented the status-accent left border on `.chat-banner` and
  `.booking-card`, shrank `.chat-banner__icon`/`.chat-banner__btn`, restyled
  `.booking-eyebrow` as an accent pill, and combined the booking card's edit-location/
  view-details row into a single `.booking-card-footer`. `npm run lint` and
  `npm run build` both pass.
- 2026-06-15: Follow-up after user screenshot feedback ("it still looks like this") -
  the `pending` (online) banner still showed a separate bordered "Respond to request"
  panel around the Accept/Reject buttons, which doesn't match Option 3's box-free
  inline layout. Removed the `.chat-banner__action--online` wrapper and "Respond to
  request" field-label from the `pending` template, replacing the wrapper with a new
  lightweight `.chat-banner__quick-actions` class (no border/background/min-width) so
  the buttons sit inline within the flex `.chat-banner` row; added a matching mobile
  stretch rule. `npm run lint`/`eslint` and `npm run build` pass.
