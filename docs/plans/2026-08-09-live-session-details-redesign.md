---
title: Live session details view redesign
date: 2026-08-09
status: Done
summary: Replaced the stacked-card ongoing-session layout with a universal SessionActionRail across all booking statuses.
spec: ../mockups/2026-08-09-live-session-universal-rail.html
---

# Live session details view redesign

**Status & Progress Summary** (2026-08-09): Done — all steps implemented on
`feat/superadmin-reports-csv-export`. `SessionActionRail.vue` created
(`src/components/session/`) and wired into `TuteeSessionDetailsFlow.vue`, replacing the old
`session-progress-card` / `session-action-card` (quick actions, next-action, support) template
blocks with a single rail component; the midpoint check-in status now swaps in place inside the
rail's "Progress check" slot instead of a separate card. All now-dead CSS (progress card, quick
actions, action-head, live pill, cta, and related keyframes/media-query rules) removed from the
view. `npm run lint` and `npm run build` both pass. Mobile stacking remains explicitly deferred to
a future pass (see Risks).

## Goal

`TuteeSessionDetailsFlow.vue`'s "ongoing" state stacked five separate cards in the left column
and two more in the rail (hero, progress-check card, quick-actions grid, info grid, timeline,
next-action card, support card), with nothing establishing visual priority. Redesign it around a
single ranked action rail that works the same way across every booking status, so the page reads
as one consistent structure instead of a pile of competing cards.

## Approach

Grilled via `/grilling` (7 decisions, see Changelog). Landed on:

- **Universal rail** — one ranked action list in the right rail for every status (upcoming,
  ongoing, payment required, awaiting verification, completed), always ending with a pinned
  "Report an issue" link. Only the rail's contents change per status; the shape stays fixed. Left
  column becomes read-only: hero + info + timeline.
- **Mid-session progress check folds into the rail** as a status-swap slot — before answered it's
  a "Progress check" button, after answered it swaps in place to a compact status line — instead
  of its own card.
- **`SessionInfoGrid` and `SessionTimeline` stay as two separate cards** (not merged into one) —
  confirmed via mockup comparison, no code change needed since this matches current behavior.
- **Extract `SessionActionRail.vue`** (`src/components/session/`) to hold the per-status branching
  that currently lives inline in the view's template, matching the existing
  `SessionHero`/`SessionInfoGrid`/`SessionTimeline` componentization pattern. Props in
  (status/session data), events out (`@open-chat`, `@open-progress`, `@cancel`, `@venue-arrived`,
  `@report`, etc.) back to the view, which keeps owning the actual API calls.
- **Cancel-session modal restyled** to match `SessionCheckInModal`'s glass-card language
  (radial-gradient wash, rounded-24 card, eyebrow label, pill buttons) instead of a plain Bootstrap
  modal — landed directly during the grill, see Changelog.
- **`SessionTimeline` hover jiggle removed** — the dotted progress steps are pure display, not
  interactive, so the `translateX(3px)` hover nudge was misleading. Landed directly.
- **`DevSessionQaPanel` placement unchanged** — it's `v-if="isDev"`-gated and never ships to real
  users, so it's out of scope for this pass.
- **Mobile stacking/reflow is explicitly deferred** — needs its own pass (see Risks).

## Steps

1. ~~Restyle the inline cancel-session modal in `TuteeSessionDetailsFlow.vue` to the glass-card
   language.~~ Done.
2. ~~Remove the hover-nudge transform from `SessionTimeline.vue`'s steps and the now-dead
   reduced-motion rules referencing it.~~ Done.
3. ~~Create `src/components/session/SessionActionRail.vue`: props for status/session/check-in
   data, emits action events; internally branches per status (upcoming / ongoing / payment
   required / awaiting verification / completed / no-action fallback) to render the ranked button
   list plus the pinned "Report an issue" link.~~ Done.
4. ~~Update `TuteeSessionDetailsFlow.vue`: replace the `session-alive-grid` left/right split so the
   left column holds only the hero + `SessionInfoGrid` + `SessionTimeline` (read-only), and the
   right column renders `SessionActionRail`. Remove the now-redundant `session-progress-card` and
   `session-action-card`/`session-next-action` template blocks, wiring their existing handlers
   (`openMidpointModal`, `handleVenueQuickAction`, `goToChat`, `goToPayment`, cancel modal open,
   `openSupport`) through to the rail's emitted events.~~ Done.
5. ~~Fold the midpoint check-in status display into the rail's "Progress check" slot (button when
   unanswered, status line when `midpointCheckIn` is set) instead of the separate
   `session-progress-card`.~~ Done.
6. Update this file's `docs/plans/README.md` row and write the session summary once shipped.

## Risks

- Removing `session-progress-card`/`session-action-card` template blocks touches a lot of existing
  event wiring (`handleVenueQuickAction`, `handleMidpointQuickAction`, cancel modal, support modal)
  — verify every action still fires correctly per status after the extraction, not just visually.
- `SessionActionRail` needs to reproduce the exact same disabled/loading states
  (`isQuickSubmitting`, `isCancelling`, `canCancelSession`) that today live directly in the view's
  template — a missed prop here could let a user double-submit an action.
- Mobile behavior is explicitly out of scope for this pass; the rail's current CSS
  (`.session-alive-grid` breakpoint at 900px) will need a real follow-up pass once the new
  structure lands, since simply collapsing to `1fr` would bury the rail below read-only info on
  small screens.

## Checks to run

- `npm run lint`
- `npm run build`
- Manually verify (or add tests for) each status renders the correct rail contents: upcoming,
  ongoing, payment required, awaiting verification, completed (rated and unrated), and the cancel
  flow from both upcoming and pending.

## Changelog

- **2026-08-09** — Plan created from the `/ui-preview` + `/grill-with-docs` session on
  `TuteeSessionDetailsFlow.vue`. Decisions locked: universal rail, folded progress check, separate
  info/timeline cards, `SessionActionRail` extraction, deferred mobile pass. Landed directly:
  cancel-session modal restyled to the glass-card language; `SessionTimeline` hover-nudge removed
  along with its now-dead reduced-motion rules. Both verified with `npm run build`.
- **2026-08-09** — Implemented Steps 3-5: added `src/components/session/SessionActionRail.vue`
  and wired it into `TuteeSessionDetailsFlow.vue` in place of the old
  `session-progress-card`/`session-action-card` blocks; midpoint check-in status now folds into
  the rail's "Progress check" slot. Removed all now-dead CSS from the view (progress card, quick
  actions grid, action-head, live pill, cta, and orphaned keyframes/media-query rules). Verified
  with `npm run lint` and `npm run build` — both clean. Plan marked Done; mobile stacking remains
  the one deliberately deferred item for a future pass.
