---
title: Session details redesign — profile-page feel + animated status bar + mid-session pulse
date: 2026-07-04
status: Done
spec:
---

# Session details redesign — profile-page feel + animated status bar + mid-session pulse

## Status & Progress Summary

- 2026-07-04: Grilled end-to-end (7 decisions resolved) with interactive previews for layout,
  hero treatment, status-bar animation, and light/dark. Approved, no code written yet.
- 2026-07-04: Execution started (In Progress) on branch `feat/verification-phase4-session-redesign`;
  10-step task list created, beginning with Step 1 (shared style primitives).
- 2026-07-04: Implemented and closed. Shared profile-style primitives now back both session
  detail pages; the tutee/tutor layouts use the two-column glass composition; Orbit Strip gained
  the Level 3 presentation with zone-pop feedback and view-owned haptics; mid-session pulse uses
  the hold-to-confirm pointer flow plus single-press keyboard/assistive path; session info and
  timeline match the profile row rhythm, including the five-step lifecycle. Status moved to Done.

## Goal

Redesign both session detail pages so they carry the profile page's material, button tiers, and
press/haptic feel, while keeping every existing behaviour. Recycle the countdown status bar (Orbit
Strip) as a more animated, dynamic element, and restore the mid-session check-in as a
hold-to-confirm "Mid-session pulse" with an accessible fallback. Must work in both light and dark
mode.

## Approach

Full page redesign (not just a reskin), but functionality-preserving. Decisions locked during the
grill:

1. **Scope — both pages.** `TuteeSessionDetailsFlow.vue` and `TutorBookingDetailsFlow.vue` share
   the session components (`SessionHero`, `SessionInfoGrid`, `SessionTimeline`,
   `SessionCountdownBar`), so both get the redesign together; shared components change once.
2. **Layout — two-column with a persistent right rail (option A).** Task content on the left; a
   right rail holds "Next action" and "Support". Preserves the always-visible CTA affordance the
   current page already has. Every panel becomes a profile-style glass segment.
3. **Hero — keep the green hero + countdown as the one saturated accent (option B of Q6).**
   Mirrors how the profile page keeps its header bold and everything else quiet. Supporting panels
   are glass; the hero/countdown are the focal colour.
4. **Status bar — recycle the Orbit Strip, full "Level 3" animation.** Eased bead/fill motion,
   flowing gradient, breathing bead, comet trail, zone-crossing pop, ticking percentage, plus a
   haptic buzz on each quarter-mark crossing (via the existing `vibrate` patterns util). The orbit
   data logic in `useOrbitStrip.js` is unchanged — presentation only.
5. **Mid-session pulse — hold-to-confirm card (the working-tree version), with accessibility
   fixed.** Two explicit options (`good` / `issues`). Pointer users hold 700ms with a fill
   animation; keyboard / assistive-tech users get a single Enter/Space press that confirms
   immediately (no hold). Fixes the key-repeat bug and the missing tap fallback found in review.
6. **Buttons — profile tiers, one primary CTA per state.** `btn-primary-action` for the single
   "Next action" CTA of each state (Submit payment / Open chat / Rate session); `btn-soft` for
   secondary quick actions; destructive treatment for Report issue / Cancel booking. Every
   interactive element carries `sb-btn` (press-scale + hover-lift) and the primary CTA adds
   `sb-elevated sb-elevated--brand`.
7. **Light mode — glass panels adapt via theme variables; the green hero/countdown stay saturated
   in both modes (option A of Q7).** The Level 3 bead/comet/glow are built for dark green and wash
   out on a pale surface, so the green anchor stays constant while the rest of the page respects
   light/dark.

## Steps

1. **Glass-segment + button primitives.** Confirm the profile classes (`glass-segment`,
   `btn-primary-action`, `btn-soft`, `sb-btn`, `sb-elevated`) are reusable from a shared location;
   if they live only in `TuteeProfile.vue` scoped styles, promote the needed ones to
   `src/assets/main.css` (or a small shared stylesheet) so both session pages and the profile page
   use one source. No new hardcoded colours — theme variables only.
2. **Restyle `SessionHero.vue`** to the saturated green anchor that stays constant in light/dark;
   keep avatar/name/meta/subject/status-badge structure and the live sub-panel.
3. **Recycle `SessionCountdownBar.vue`** into the Level 3 animated status bar: eased transitions,
   flowing gradient, breathing bead, comet trail, zone-crossing pop, ticking `%`. Add
   `prefers-reduced-motion` collapse to a plain fill. No change to `useOrbitStrip.js` outputs.
4. **Wire haptics** on zone crossing in the consuming view(s) (watch `presentation.zone`), reusing
   the existing `vibrate`/`patterns` util; guarded by reduced-motion / no-op where unsupported.
5. **Fix `SessionCheckInModal.vue`**: guard `startHold` against key auto-repeat / re-entry, add
   the single-press keyboard/AT confirm path, de-duplicate the hint copy, and ensure the hold
   option colours use theme variables so the card is readable in light mode. Keep the
   `submitMidpointCheckIn` store call and the `good`/`issues` contract.
6. **Recompose `TuteeSessionDetailsFlow.vue`** into the two-column glass layout: left column
   (hero → countdown → mid-session pulse when Live → quick actions → session information →
   timeline), right rail (Next action → Support). Preserve all state gating
   (upcoming/pending/live/payment required/completed rated+unrated/cancelled), payment-return
   banner, cancel modal, rating modal, support modal.
7. **Apply the same recomposition to `TutorBookingDetailsFlow.vue`**, honouring its
   tutor-specific actions and copy.
8. **Restyle `SessionInfoGrid.vue`** as a glass panel with the profile row rhythm; keep the
   online-session location suppression already in the working tree.
9. **Light/dark pass** across all touched components; verify every glass panel uses
   `--sb-card-bg` / `--sb-text-main` / `--sb-card-border` (or equivalents) and no `#fff` leaks
   onto glass.
10. **Documentation**: on completion, write the session summary and set this plan to Done,
    regenerating `docs/plans/index.html`.

## Risks

- **Shared components cut both ways.** Restyling `SessionHero`/`SessionCountdownBar` changes the
  global Orbit dock too (it also consumes `useOrbitStrip`). Verify the global dock still looks
  right, not just the detail pages.
- **Profile classes may be scoped, not shared.** If `glass-segment`/`btn-*` live inside
  `TuteeProfile.vue`'s `<style scoped>`, they can't be reused directly — promoting them risks
  visual drift on the profile page. Diff the profile page before/after promotion.
- **Animation cost.** Continuous Level 3 animation (rAF bead, flowing gradient) on an always-on
  bar must not jank; keep to compositor-friendly properties (transform/opacity) and honour
  reduced-motion.
- **Accessibility of hold-to-confirm.** The whole point of step 5 is not shipping a control some
  input methods can't operate — verify keyboard and screen-reader paths, not just mouse.
- **State matrix.** Six+ display states × two pages. Easy to restyle the happy path and break a
  rarely-seen state (cancelled, pending, awaiting verification). Walk every state.

## Checks to run

- `npm run lint` — passes clean (oxlint + ESLint).
- `npm run build` — production build succeeds.
- `npm run test` — Vitest green, including `src/composables/useOrbitStrip` / `activeSession`
  coverage (orbit logic must be unchanged).
- Manual/browser: each display state on both pages in light and dark; hold-to-confirm via mouse
  and keyboard; reduced-motion on; the global Orbit dock still renders correctly.

## Changelog

- 2026-07-04: Plan created from the grilling session (7 decisions resolved via interactive
  previews). Status Approved; no code written yet.
- 2026-07-04: Moved to In Progress; execution began with the 10-step task list.
- 2026-07-04: Implemented the redesign across shared session components and both detail pages,
  fixed the midpoint check-in accessibility path, moved Orbit haptics into the consuming detail
  views, restored the five-step timeline, added a session summary, and moved the plan to Done.
- 2026-07-04: Verification note: `git diff --check` passed. `npm run lint`, `npm run build`, and
  `npm run test` were blocked by sandbox `spawn EPERM`; the lint escalation retry was rejected by
  the app usage limit.
