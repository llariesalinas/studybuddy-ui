---
title: Session countdown (Orbit Strip)
date: 2026-07-03
status: Done
spec:
---

# Session Countdown Implementation Plan

## Status/Progress Summary

Design settled via a grilling session on 2026-07-03 (13 decisions below, all confirmed).
Domain terms (`Display Status`, `Handoff`, `Queue Item`, `Orbit Zone`) recorded in
[CONTEXT.md](../../CONTEXT.md). Implementation shipped on this branch as commit `df994ca`
("feat: add session orbit countdown"). All 13 Resolved Decisions were verified against real data
(`npm run lint`, `npm run build`, the new test suites, and live browser checks against a real
tutee account) — see
[docs/session-summaries/2026-07-03-session-countdown-summary.md](../session-summaries/2026-07-03-session-countdown-summary.md)
for the full verification record. Verification surfaced one real bug in Decision 8 (the detail
page's own countdown bar was silently inheriting the global queue's state instead of computing
its own), fixed in `useOrbitStrip.js`. A second, pre-existing bug (an oversized blank block on the
detail page, from `SessionHero.vue`'s `min-height: 100%`) was caught by the user via a screenshot
after this session's own verification pass missed it, and was also fixed. Plan is Done.

## Goal

Implement the new session countdown surfaces in the Vue app using the selected `Orbit Strip` direction.

## Decision

- Locked concept: `B - Orbit Strip`
- Visual treatment: aurora glow lane, moving orbit bead, compact dark dock, full-width detail bar
- The four orbit zones are presentation rhythm only, not literal backend states or tracked workflow steps.
- Preview reference: [session-countdown-concepts-preview.html](../artifacts/2026-07-03-session-countdown-concepts-preview.html)

## MVP Rules

- The official timer is based on the Scheduled Session Window.
- The countdown appears 15 minutes before the session starts.
- The current live session or unresolved post-session handoff has priority over the next upcoming session.
- The session detail page gets a full-width status bar.
- The rest of the app gets a compact bottom dock.
- The compact dock hides when the user is already on the matching session detail page.
- Readiness or arrival is supporting state, not the thing that starts the official timer.

## Real Product States

- `upcoming`: next session is within 15 minutes of scheduled start
- `live`: current time is inside the Scheduled Session Window
- `handoff`: scheduled session ended, but post-session payment or verification is still unresolved
  (see [CONTEXT.md](../../CONTEXT.md) — this maps 1:1 to Display Status `Payment Required` /
  `Awaiting Verification`, no extra time math needed)

## Surfaces

1. Full session detail bar
The session detail screens for tutee and tutor get the large Orbit Strip treatment directly under the hero area.

2. Global bottom dock
All other authenticated pages get the compact Orbit Strip dock when there is a relevant queue item.

3. Shared language
Both surfaces should use the same state labels, countdown logic, and aurora motion language.

## Resolved Decisions (grilling session, 2026-07-03)

1. **Queue logic location** — extend `src/stores/activeSession.js` in place with new computeds
   (`queueState`, `queueItem`) rather than a separate store. It's already the polling singleton;
   a second store would duplicate the timer.
2. **Handoff detection** — purely status-based: `session.status` (the backend's Display Status,
   `get_display_status` in `backend/studybuddy/views.py:851`) is `'Payment Required'` or
   `'Awaiting Verification'`. No client-side time recomputation — the backend already recalculates
   this on every fetch.
3. **Timezone fix** — `activeSession.js`'s own `parseDateTime` (`activeSession.js:33`, no timezone,
   parses in the browser's local zone) is replaced with `useSessionClock.js`'s
   `parseSessionDateTime` (explicit `+08:00` / Asia-Manila offset). Users are all PH institutions,
   so all session-window math should be Manila-anchored regardless of the visitor's device
   timezone. This also fixes a latent bug in the existing live/check-in logic, not just new code.
4. **Tie-break for multiple candidates** — `handoff`: oldest unresolved session wins (longest
   overdue). `upcoming`: soonest-starting session wins (same sort `activeBooking` already uses at
   `activeSession.js:67`).
5. **Component split** — one shared composable (e.g. `useOrbitStrip()`) turning the store's queue
   state into presentation-ready values (label, countdown string, orbit-zone progress, "up next"
   hint) — pure data, no markup. Two separate presentational components consume it: refactored
   `OngoingBookingBar.vue` (compact dock) and new `SessionCountdownBar.vue` (full-width bar). Not
   one component branching on a `variant` prop — the layouts differ enough to make that branchy.
6. **Orbit zone semantics** — time-driven, not decorative: the bead's position reflects real
   elapsed/remaining time, but the 4 zones are a generic 0–25/25–50/50–75/75–100% progress scale
   for whichever phase is active (countdown-to-start / elapsed-live / time-since-ended). They are
   **not** tied to session-specific milestones like "venue" or "midpoint" — that literal 4-step
   mapping is what today's `OngoingBookingBar.vue:71-82` stepper does, and it does not carry over.
7. **Handoff progress cap** — since handoff has no natural end, progress is measured against a
   24-hour cap (time since session end / 24h, clamped to 100%). Past the cap, zone 4 holds steady
   (not looping) as an urgency cue.
8. **Detail-page bar scope** — the full-width bar on `TuteeSessionDetailsFlow.vue` /
   `TutorBookingDetailsFlow.vue` always reflects **that page's own session**, not the global
   front-of-queue item. Avoids a confusing "wrong session" bar when viewing an unrelated booking.
9. **Dock hide rule** — exact match only: hide the compact dock when the current route's
   `params.id` equals the front-of-queue item's id (role-aware route name, same as
   `OngoingBookingBar.vue:91-97` already resolves). Viewing a *different* session's detail page
   does not hide the dock for a more urgent item elsewhere.
10. **"Up next" hint** — shown whenever a second queue candidate exists behind the front item.
    Content: state label + relative time for that #2 item only (e.g. "Up next: Calculus with
    Maria in 8 min"). Never peeks more than one item ahead.
11. **Tick rate** — data poll stays at 60s (`SESSION_POLL_INTERVAL_MS`, unchanged, no extra API
    load). A separate 1-second UI-only ticker (mirroring `useSessionClock.js`'s pattern, paused on
    `document.hidden`) drives the displayed countdown text and bead motion so it doesn't stutter.
12. **Relationship to `SessionTimeline.vue`** — the existing 5-step lifecycle stepper
    (`session/SessionTimeline.vue`) is hidden and replaced by the Orbit Strip bar while a session
    is the page's active countdown target (upcoming/live/handoff). `SessionTimeline` continues to
    own every other state (pending, far-future confirmed, completed) — the two surfaces are never
    shown at once for the same session.
13. **Dev QA tooling** — add two buttons to `DevSessionQaPanel.vue` ("Force upcoming (T-12min)",
    "Force handoff (payment required)"), reusing the existing dev-override mechanism
    (`apply_dev_live_override` in `views.py`), so the plan's own Verification step (checking all
    three states) doesn't require waiting on real time or hand-editing data.

## Implementation Steps

1. Build shared queue state
   - Add `queueState` / `queueItem` computeds to `activeSession.js` per Decision 1, using the
     tie-break rules in Decision 4 and the status-based handoff check in Decision 2.
   - Swap `activeSession.js`'s local date parsing for `useSessionClock.js`'s
     `parseSessionDateTime` (Decision 3).

2. Reuse the scheduled session clock
   - Use `useSessionClock.js` (or its exported pure `getSessionClockState`) as the timer source for
     time-until-start, time-remaining, and time-since-ended.
   - Add the 1-second UI-only ticker per Decision 11, decoupled from the 60s data poll.

3. Build the shared composable
   - `useOrbitStrip()` (or similar) wraps `activeSession.js`'s queue state into label, countdown
     string, orbit-zone progress (Decision 6, with the 24h handoff cap from Decision 7), and the
     "up next" hint (Decision 10).

4. Replace the current global dock
   - Refactor `OngoingBookingBar.vue` to consume `useOrbitStrip()`: dark aurora surface, moving
     orbit bead, primary message + timer, "up next" hint.
   - Apply the exact-match hide rule (Decision 9).

5. Add the full Orbit Strip bar to session details
   - New `src/components/session/SessionCountdownBar.vue`, scoped to the page's own session
     (Decision 8), inserted into `TuteeSessionDetailsFlow.vue` and `TutorBookingDetailsFlow.vue`
     directly under the hero area.
   - Conditionally hide `SessionTimeline.vue` while the Orbit Strip is active for that session
     (Decision 12).

6. Dev QA tooling
   - Add the two new force-state buttons to `DevSessionQaPanel.vue` (Decision 13).

7. Preserve existing workflow behavior
   Do not change the underlying payment, venue confirmation, midpoint check-in, or completion workflow in this pass. The countdown surfaces should reflect state, not redefine it.

8. Keep readiness separate
   Do not implement hold-to-ready in this pass. That should come later with persistent backend state and should layer onto the bar without controlling the official timer.

## File Targets

- `src/components/OngoingBookingBar.vue`
- `src/stores/activeSession.js`
- `src/composables/useSessionClock.js`
- `src/views/TuteeSessionDetailsFlow.vue`
- `src/views/TutorBookingDetailsFlow.vue`
- `src/components/session/SessionTimeline.vue` (conditional visibility only, no logic changes)
- `src/components/DevSessionQaPanel.vue`
- new: `src/components/session/SessionCountdownBar.vue`
- new: shared composable, e.g. `src/composables/useOrbitStrip.js`

## Risks

- **Payment-block gap (known, out of scope here):** nothing currently stops a tutee from booking
  a new session while an existing one is in `handoff` (Payment Required / Awaiting Verification).
  This plan does not change that; tracked separately as a future booking-flow change, not part of
  the Orbit Strip work.
- **Timezone fix has a wider blast radius than it looks:** swapping `activeSession.js`'s date
  parsing (Decision 3) also changes behavior for the existing venue/midpoint check-in due-logic,
  not just the new countdown code. Needs regression-checking against the check-in modal flow, not
  only the new surfaces.
- **`SessionTimeline` visibility toggle:** hiding it conditionally (Decision 12) needs to degrade
  cleanly for statuses the Orbit Strip doesn't cover (`pending`, `rejected`, `cancelled`) — those
  must keep showing `SessionTimeline` untouched.

## Verification

- Preview on the existing local Vite server
- Verify `upcoming`, `live`, and `handoff` states in both tutor and tutee flows, using the new
  `DevSessionQaPanel.vue` force buttons (Decision 13)
- Confirm the compact dock hides on the matching session detail route (exact `params.id` match
  only, per Decision 9), and stays visible when viewing an unrelated session's detail page with a
  more urgent queue item elsewhere
- Confirm venue/midpoint check-in modals still fire correctly after the timezone fix (Decision 3)
- Run `npm run lint`
- Run `npm run build`

## Out of Scope

- Backend persistence for readiness
- New session start logic
- Reworking payment rules
- Blocking new bookings while a payment/verification handoff is unresolved (tracked separately)
- Replacing the existing modal flow for ongoing session prompts

## Changelog

- 2026-07-03: Initial draft locked to the `Orbit Strip` concept.
- 2026-07-03: Grilled the plan end-to-end via `/grill-with-docs`; resolved 13 open decisions
  (queue-logic location, handoff detection, timezone fix, tie-breaks, component split, orbit-zone
  semantics, handoff progress cap, detail-bar scope, dock hide rule, "up next" hint, tick rate,
  `SessionTimeline` relationship, dev QA tooling). Added frontmatter, Status/Progress Summary, a
  Resolved Decisions section, a Risks section, and updated File Targets/Verification to match.
  Recorded new domain terms (`Display Status`, `Handoff`, `Queue Item`, `Orbit Zone`) in
  `CONTEXT.md`.
- 2026-07-03: Moved the preview reference from the untracked repo-root file
  `session-countdown-concepts.html` into `docs/artifacts/2026-07-03-session-countdown-concepts-preview.html`
  (repo convention for design previews) and removed the duplicate links that had been added to
  `docs/plans/README.md` and `docs/plans/index.html` — this plan file stays the single canonical
  place linking to it.
- 2026-07-03: Discovered commit `df994ca` ("feat: add session orbit countdown") already implements
  this plan, committed outside this session. Moved status `Approved` -> `In Progress` to reflect
  reality. Full decision-by-decision audit + `npm run lint` / `npm run build` / test verification
  still outstanding — see
  [docs/session-summaries/2026-07-03-session-countdown-handoff.md](../session-summaries/2026-07-03-session-countdown-handoff.md).
- 2026-07-03: Ran the outstanding verification (lint/build/tests clean; all 13 decisions confirmed
  against real data via a live tutee account, `reg@cpu.edu.ph`). Found a real Decision 8 violation:
  `useOrbitStrip({ session })` fell back to the *global* queue's `state` whenever the caller didn't
  also pass `state` explicitly, so both `TuteeSessionDetailsFlow.vue` and
  `TutorBookingDetailsFlow.vue` showed the wrong phase (their own session's subject/times, but the
  global queue's handoff/live/upcoming state) whenever the two didn't match. Fixed in
  `src/composables/useOrbitStrip.js` — an explicit `session` now forces a fresh
  per-session phase unless `state` is also explicitly supplied. Re-ran the unit tests (10/10 pass)
  and re-verified the corrected logic against the shipped module in the browser. Moved status
  `In Progress` -> `Done`. Full record in
  [docs/session-summaries/2026-07-03-session-countdown-summary.md](../session-summaries/2026-07-03-session-countdown-summary.md).
- 2026-07-03: User caught a second bug via a screenshot of the detail page (a large empty green
  block) that this session's own verification pass had missed. Root cause: `SessionHero.vue`'s
  `min-height: 100%` resolved against its whole stretched grid-column height (~1155px) rather than
  its own ~230px of content — pre-existing from the June 15 "Session Details alive redesign" plan,
  not introduced by the Orbit Strip diff. Removed the rule, verified live (screenshots + bounding
  box measurements before/after), re-ran `npm run build`. See the summary doc for details.
