---
title: Session Details "alive" redesign (tutee + tutor)
date: 2026-06-15
status: Done
spec: ../artifacts/2026-06-15-session-details-alive-redesign-preview.html
---

# Session Details "alive" redesign (tutee + tutor)

## Status & Progress Summary

Implemented on 2026-06-15. The shared alive-session components now back both
`TuteeSessionDetailsFlow.vue` and `TutorBookingDetailsFlow.vue`, with the reference
artifact retained as the visual source of truth.

Completion summary:
[2026-06-15-session-details-alive-redesign-summary.md](../session-summaries/2026-06-15-session-details-alive-redesign-summary.md).

## Goal

Redesign the Session Details page for both roles so it feels "alive" when a session is
Ongoing — animated aurora background, pop-color accents, a live elapsed timer, a progress
timeline, a pulsing live badge, quick actions, and haptics — borrowing the landing page's
visual language (`LandingPage.vue` + `src/assets/main.css` aurora/pop tokens). One unified
layout serves all statuses; the live elements only switch on when status = Ongoing.

## Approach

Decisions locked with the user (all from the approved preview):

- **One unified layout for every status.** Same redesigned skeleton (hero → session info
  grid → progress timeline → action rail → support) renders for
  Pending / Upcoming / Ongoing / Awaiting verification / Completed / Rejected / Cancelled.
- **Liveliness scope: aurora always, studio only when live.** The animated aurora
  background + pop-color accents show on every status. The lighter green-tinted "live"
  hero treatment, the live elapsed timer, the shimmer-free progress bar, the quick-actions
  dock, and the timeline's "in session now" emphasis activate **only** when Ongoing.
- **Lighter hero (not dark ink).** Per user feedback, the Ongoing hero uses the soft
  green→cream gradient (`#f3fbf7 → #e3f3ea → #fef6e6`), brand-green timer text, white live
  badge with a green ring. (Earlier dark `--sb-dark` studio version was rejected.)
- **No "rail" animations.** The scrolling LIVE ticker marquee and the traveling progress
  shimmer were both removed; the progress bar is a clean static fill.
- **Timeline on all statuses.** Requested → Confirmed → Session day → Completed, with the
  current node emphasized (pulsing ring) when Ongoing.
- **Quick actions wired to existing flows — no new backend.** Message → `chat` route;
  tutee "I've arrived" / tutor "Confirm venue" + "Mid check-in" → existing check-in
  endpoints already surfaced via `DevSessionQaPanel` / `tutorBookingDetails` store;
  tutor "End session" → the existing complete/ready-for-payment action.
- **Live timer derived from `date` + `start_time`** (Manila tz), no schema change. Ticker
  runs on a 1s interval gated behind an `isOngoing` computed and cleared in
  `onBeforeUnmount` so it never leaks when the user leaves an Ongoing session.
- **Respect `prefers-reduced-motion`.** Aurora, blobs, badge pulse, timeline ring,
  reveals, and confetti all freeze to static when the OS requests reduced motion — same
  pattern `LandingPage.vue` already follows. Haptics still fire (they are not visual
  motion).
- **Hide the floating dock on these pages.** `OngoingBookingBar.vue` renders globally in
  `App.vue:360` and has no route awareness today. Add a `useRoute()` guard so it is hidden
  when `route.name` is `tuteeSessionDetails` or `booking-details` (redundant once you're
  already viewing the session). The dock stays as-is everywhere else.
- **No hardcoded hex in shipped code.** Map the artifact's literal colors to the existing
  `--sb-*` tokens (`--sb-primary` #00895a, `--sb-primary-mid` #18A36C, `--sb-pop-yellow`
  #FFC94D, `--sb-pop-orange` #FF8A5C, `--sb-pop-pink` #FF8FA3, `--sb-aurora-violet`
  #8E7CF4, `--sb-dark` #0A1916, `--sb-spring`). Add new tokens only if a needed value is
  genuinely missing.

Shared-code strategy (the two views are ~90% identical markup): extract the common pieces
so the redesign lives in one place rather than being copy-pasted twice:

- `src/components/session/SessionHero.vue` — avatar + name + subject + status badge +
  (when Ongoing) the live timer/progress strip. Props: counterpart profile, subject,
  status, schedule (date/start/end), `isOngoing`.
- `src/components/session/SessionTimeline.vue` — the 4-step progress rail, driven by a
  normalized status.
- `src/components/session/SessionInfoGrid.vue` — the pop-accent info tiles.
- `src/components/session/SessionAurora.vue` — the animated aurora background layer
  (reduced-motion aware), reused by both views.
- `src/composables/useSessionClock.js` — derives elapsed/total/`minutesLeft`/`progress`
  from `date` + `start_time` + `end_time` in Manila tz; owns the 1s interval + cleanup.
- `src/composables/useHaptics.js` — a thin `vibrate(pattern)` wrapper (guards
  `navigator.vibrate`, swallows errors, no-ops where unsupported). There is no existing
  haptics helper in `src/`; centralize here rather than scattering `navigator.vibrate`
  calls. Patterns: light tick (12ms) for nav/taps, medium (30ms) for End session,
  celebratory (`[18,40,18,40,60]`) for Mark complete / rating.

The per-role **action rail** and **quick actions** stay inside each view (their
CTAs/handlers differ — tutee submits payment/rates; tutor verifies payment/ends session),
but both consume the shared components above.

## Steps

1. Add design tokens check: confirm every artifact color maps to an existing `--sb-*`
   token in `src/assets/main.css`; add any missing token there (no inline hex in SFCs).
2. Build `useHaptics.js` and `useSessionClock.js` composables (+ a Vitest unit test for
   the clock math: elapsed/progress/minutesLeft, Manila tz, pre-start and post-end edge
   cases).
3. Build the shared components: `SessionAurora.vue`, `SessionHero.vue`,
   `SessionTimeline.vue`, `SessionInfoGrid.vue` — markup/CSS ported from the artifact,
   using `--sb-*` tokens and a `prefers-reduced-motion` block.
4. Refactor `TuteeSessionDetailsFlow.vue` to compose the shared components; keep its
   existing action rail (payment / rating / cancel) and support card; add the Ongoing
   quick-actions dock wired to the existing chat/check-in handlers.
5. Refactor `TutorBookingDetailsFlow.vue` the same way; keep its payment-summary /
   verify / end-session / check-ins rail; add the Ongoing quick-actions dock.
6. Add the `useRoute()` visibility guard to `OngoingBookingBar.vue` (hide on
   `tuteeSessionDetails` and `booking-details`).
7. Add the confetti burst on transition into Completed (reduced-motion aware; one-shot,
   cleaned up).
8. Run `npm run lint` and `npm run build`; fix issues.
9. Manual preview of both views across all statuses (see Checks). Note: port 5173 is
   often occupied by the user's own dev server — coordinate before assuming a free port.
10. On completion, write `docs/session-summaries/2026-06-15-session-details-alive-redesign-summary.md`,
    link it from the index row, and flip status to Done.

## Risks

- **Status sources differ between views.** Tutee uses `completedSessions` store
  (`session.status`); tutor uses `tutorBookingDetails` store (`sessionInfo.status` +
  `raw_status`). The shared timeline/hero must take a *normalized* status prop so both map
  cleanly — don't assume identical field names.
- **No real Ongoing status may exist in data yet.** Confirm the API/stores actually emit
  an `ongoing` status; if "ongoing" is only a derived/time-window concept, the
  `isOngoing` computed may need to combine status with the clock (now within
  start/end). Verify before wiring the live gate. Related: the
  [Ongoing-booking live status surface](2026-06-14-ongoing-booking-live-status.md) plan
  (In Progress) — reuse its definition of "ongoing" rather than inventing a second one.
- **Timer leak / battery.** The 1s interval must be gated on `isOngoing` and torn down in
  `onBeforeUnmount`; also pause when `document.visibilityState === 'hidden'` to match the
  landing page's discipline.
- **Aurora performance.** The repo has prior aurora performance plans
  (2026-06-07 aurora fixes). Keep blob count low (≤4), use transform/opacity-only
  animations, and gate on reduced-motion + coarse-pointer if needed — don't reintroduce
  the perf regression those plans fixed.
- **Hiding the dock could mask a regression** if the route guard is wrong — verify the
  dock still shows on dashboard/other routes after the change.
- **Scope creep.** Extracting shared components touches two large views; keep behavior
  (handlers, computed gates) byte-for-byte and change only structure/markup/styles.

## Checks to run

- `npm run lint` — no new lint errors.
- `npm run build` — production build succeeds.
- `npx vitest run` — the new `useSessionClock` test passes; existing store tests still
  pass.
- Manual preview, both roles × statuses: Ongoing shows aurora + lighter live hero + ticking
  timer + progress + timeline "in session now" + quick actions; non-Ongoing shows the same
  skeleton with live bits off but aurora/accents on; Completed fires confetti once;
  `OngoingBookingBar` is hidden on both detail routes and visible elsewhere; reduced-motion
  freezes animation.

## Changelog

- 2026-06-15: Explored both views + `LandingPage.vue`; produced three iterations of an
  interactive preview (base alive → landing-energy colored + haptics → lighter hero,
  ticker/rail removed). User approved the third. Saved the approved mockup as a
  self-contained reference artifact and wrote this plan. Status: Approved, pending
  implementation.
- 2026-06-15: Implemented the shared component/composable redesign, wired tutee and tutor
  details pages, hid the global ongoing dock on detail routes, added clock tests, and ran
  lint/build verification. Status: Done.
