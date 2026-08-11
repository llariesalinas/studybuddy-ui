---
title: Removing or modifying UI components
date: 2026-08-10
status: Done
spec:
---

# Removing or modifying UI components

## Goal

Three unrelated UI cleanups: make `/register` fit a laptop viewport without scrolling, narrow the
SuperAdmin Support Desk to strike tickets by dropping the Escalated queue, and hide the sidebar Help
button for SuperAdmin.

## Approach

**Registration.** Layout restructure, not density trickery. The existing `data-sb-density='compact'`
system is role-driven and `userRole` is `null` on public auth routes, so it is inert on `/register`
by design (see [2026-08-04](2026-08-04-tutee-ui-80-percent-density.md)); triggering it by route
would have shrunk `/login`, `/forgot-password` and `/reset-password` as a side effect. Only the
three name fields share a row; Email, Institution, Password and "I want to" keep their original
full-width positions and order. The rest of the height comes out of the masthead and the gaps
between fields, never the controls themselves.

The card and page paddings live in `AuthShell.vue`'s **scoped** styles, which `Register.vue` cannot
reach — the card is not inside Register's template scope, so `:deep()` does not apply. Hence two
opt-in boolean props (`wide`, `dense`) rather than an override, keeping every other auth page on the
440px comfortable treatment.

**Escalated tickets.** `/superadmin/support`, its route and its sidebar entry stay — the desk is
still where system-opened Late Cancellation tickets are judged. Only the escalation queue goes.

**Help.** The whole `Support` section is hidden for SuperAdmin, label included, so no stray heading
is left behind. `SupportModal` and the `open-support` wiring are untouched — the modal is also
opened from the Tutee and Tutor session flows.

## Steps

1. `src/components/AuthShell.vue` — added `wide` / `dense` props bound to `.sb-auth-card--wide`
   (560px) and `.sb-auth-page--dense` (tighter page/card padding, brand margin, icon badge,
   subtitle). Restated the dense card padding inside the existing `@media (max-width: 768px)` block,
   which it outranks on specificity, and added a `@media (max-height: 880px)` tier last in source
   order that further shrinks the masthead (32px icon badge, 18px title, tighter subtitle) and the
   vertical page/card padding. That tier's padding rules are vertical-only so a landscape phone
   keeps its narrower gutters.
2. `src/views/Register.vue` — `<AuthShell wide dense>`; First/Middle/Last share a
   `.sb-auth-row--3` grid that collapses to one column under 768px, with `align-items: start` so a
   field error cannot stretch its neighbours. Every other field keeps its original full-width
   position and order. Field margin 16px → 14px (8px under 880px tall, where label margin also
   drops to 4px); alert padding/margin trimmed. No change to bindings or logic.
3. `src/views/AdminSupport.vue` — SuperAdmin `statusTabs` `['Open','Escalated','Resolved']` →
   `['Open','Resolved']`; `filters.status` defaults to `'Open'` on both desks; the
   `watch(isSuperAdminDesk)` reset follows; `canClaim` keys the SuperAdmin branch on `Open &&
   !assigned_agent_id`; `canChat` loses its escalated clause; `canResolve` loses its `Escalated`
   branch and keeps the strike branch. Admin's desk, Escalate button, modal and `handleEscalate`
   are untouched.
4. `src/App.vue` — SuperAdmin support header subtitle reworded off "escalated support tickets".
5. `src/components/AppSidebar.vue` — `showHelp` computed (`role !== 'superadmin'`) wrapping the
   `Support` label and nav in a `<template v-if>`; new test case in `AppSidebar.test.js` asserting
   the button is gone and the section label is not among `.sb-section-label` (the "Support Desk"
   nav item legitimately still contains the word).

## Follow-up: campus location modal under compact density

Reported after the main pass: picking **Face-to-face** on `/book` opened `CampusLocationModal`
off-centre with a backdrop that did not cover the page. Both are the density system's root `zoom`
(Tutee is in `COMPACT_ROLES`), and neither is specific to that modal's own CSS. Measured in-browser
by toggling `data-sb-density` and probing:

| | comfortable | compact, before | compact, after |
|---|---|---|---|
| Dialog drift from its anchor's centre | (0, 0) | **(-136, -170)** | (0, 0) |
| Backdrop coverage at a 1366×660 viewport | 1366×660 | **1093×528** (80%) | 1366×660 |

1. **Position.** `CampusLocationModal` is the only modal in the app that positions from
   `getBoundingClientRect()` (every other one centres with flexbox) — which is why it alone was
   off. The rect is reported in post-zoom coordinates, but the `left`/`top` written back onto the
   fixed dialog are scaled by the root `zoom` again, applying 0.8 twice. `updateDialogPosition()`
   now divides by a `readDensityScale()` helper reading `--sb-density-scale`.
2. **Backdrop.** Bootstrap sizes `.modal-backdrop` with `100vw`/`100vh`, and root `zoom` does not
   rescale viewport units. Compensated globally in `main.css` with a new `--sb-vw-fix` beside the
   existing `--sb-vh-fix`, following that file's established pattern. This also repairs the
   backdrops in `CashInModal` and `TutorWallet`, which are Tutor-reachable and had the same defect.

`.modal` itself was measured and deliberately left alone: its `100%` resolves against the initial
containing block, which is already in unzoomed pixels, so it was never short. An earlier attempt to
"fix" it with `--sb-vw-fix` over-corrected it to 1708px wide.

Covered by `src/components/CampusLocationModal.test.js` (3 cases: comfortable, compact, and a
missing-variable fallback). Note the position watcher is not `immediate`, so the modal only measures
on the `false -> true` transition — mounting it already open would not position it. That matches how
`InitialBooking` drives it, and the test does the same.

## Risks

- **Escalated tickets are now orphaned.** The backend list endpoint
  (`backend/studybuddy/views.py:5838-5860`) still returns `Escalated | escalated_at NOT NULL |
  Late_Cancellation` to SuperAdmin, and Admin's "Escalate to SuperAdmin" button still works. With no
  Escalated tab, a newly escalated ticket is fetched but unreachable and never reaches `Resolved` —
  escalation is a one-way trip. Accepted for this pass; the follow-up is to gate `canEscalate`
  (`AdminSupport.vue`) to `false`.
- The `ESCALATION REASON` block and the `case 'Escalated'` badge style were left in place. They are
  inert while no Escalated row renders, and still correct if one ever does.
- The short-viewport threshold has to sit **above** the form's height at the roomier tier, not at a
  round device number. An earlier `max-height: 700px` left a dead band: at a 720px viewport the
  roomier tier applied but needed ~818px, overflowing by 98px — worse than at 660px. 880px clears
  the ~747px the roomier tier needs. Any future field added to this form must be re-measured
  against that threshold.
- The short-viewport query is last in source order, so on a landscape phone it beats the mobile
  block. That is the intended precedence (short viewport wins), and its padding rules are
  vertical-only so the mobile gutters survive.

## Checks to run

- `npm run test` — 167/167. Earlier runs on this branch showed 163/164; the one failure,
  `useOrbitStripComposable.test.js`, was a midnight-boundary flake, not a regression. The test builds
  `endTime` as `now + 15min`, which wraps to `00:00` on the same date key when run just before
  midnight, so the session reads as already ended. Confirmed twice: it failed on a stashed (clean)
  tree at the same commit, and it passes unchanged once the clock is past midnight. Worth fixing
  independently — it will fail again in that window.
- `npm run build` and `npm run lint:eslint` — both clean.
- Measured in-browser on `/register` with the dev server, no console errors. Intrinsic content
  height (page `min-height` neutralised), so it compares against any viewport:

  | Tier | State | Height needed |
  |---|---|---|
  | tight (≤880px tall) | clean | 616px |
  | tight | institution selected (helper line) | 639px |
  | tight | + domain-mismatch field error | 661px |
  | tight | + server general alert | 710px |
  | roomy (>880px tall) | institution selected | 747px |

  The form therefore loads without scrolling on any viewport from ~620px up. On a 768p laptop
  (~660px) the loaded state has ~21px of headroom; the post-submit states that stack a server alert
  on top of a field error still scroll there, though the submit button stays visible until the alert
  appears. Spot-checked at 620, 660, 720, 890 and 375×812 — the phone width collapses the name row
  to one column, keeps its 20px card gutters, and has no horizontal overflow.

  `/login` verified unchanged at a 660px viewport: 440px card, `36px 32px` padding, 48px badge, no
  modifier classes — every short-viewport rule is scoped to `.sb-auth-page--dense`.
- Still to do manually (needs a logged-in session): SuperAdmin `/superadmin/support` shows only
  `Open` / `Resolved` and the verdict modal still works; Admin `/admin/support` is unchanged; the
  SuperAdmin sidebar has no Support section while Tutee/Tutor/Admin still open `SupportModal`; and
  as a Tutee on `/book`, picking Face-to-face opens the campus modal centred on the booking card
  with a backdrop covering the whole page. The modal fixes were verified by measurement against a
  toggled `data-sb-density` rather than on `/book` itself, which needs a Tutee login.
