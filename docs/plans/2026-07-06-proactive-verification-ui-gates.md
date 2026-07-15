---
title: Proactive verification UI gates (booking & accept)
date: 2026-07-06
status: Approved
spec: docs/plans/2026-07-01-tutee-verification-overview.md
---

# Proactive verification UI gates (booking & accept)

<!-- LIVING SUMMARY: keep this section and the Changelog current on every edit -->
## Status & Progress Summary

**Status: Approved — design locked via `/grill-with-docs`, not yet implemented.**

Standalone plan (not filed as a phase of the tutee-verification overview, by explicit user choice),
but it directly builds on that initiative's Phase 2 (Reactive Gate, server-side, Done) and Phase 3
(tutee route guard, Done) — see `CONTEXT.md`'s new "Verification & booking gates" glossary section
for the Reactive Gate / Proactive UI Gate distinction this plan introduces.

## Goal

Today, an unverified Tutee or a Tutor with Renewal Required can click all the way through to a
booking attempt and only find out it's blocked from a generic toast after the server's Reactive
Gate returns a 403. Add a Proactive UI Gate at the two points that matter (TutorDetails' booking
button, Manage Sessions' accept button) so the control is visibly disabled before they try, plus a
persistent status banner and a small always-visible verified/unverified badge on both dashboards.

## Approach

**Reverse the existing Tutee route-guard redirect, narrow enforcement to the button.** Phase 3
redirects an unverified Tutee away from `/book`, `/find-tutors`, `/tutor/:id` entirely. The user
wants Tutees to be able to browse tutors freely and only be stopped at the actual booking action —
so `needsTuteeVerificationBlock` is no longer called from `router/index.js`'s guard for those three
routes (the pure function itself stays in `tutorApplicationState.js`, still used by the button gate
and the banner below). This is safe: the server-side Reactive Gate at `POST bookings/confirm/`
(Phase 2) is unaffected and remains the actual authority.

**Remove the header "Book Session" button's existing modal-based gate.** `App.vue` already has a
`isBookingGateModalOpen` modal that opens instead of navigating when an unverified Tutee clicks the
header button. Per user decision, this button is being reframed as pure flow-entry (browsing should
always be allowed), so the gate on it is redundant and is deleted along with the modal. Its
`goToVerificationStatus` helper is kept and reused as the banner's CTA.

**Single Proactive UI Gate per role, placed at the real transaction point:**
- Tutee: `TutorDetails.vue`'s "Confirm Booking" button (the only actual booking button in that
  view — there is no separate "Book a Session" button there). When `needsTuteeVerificationBlock`
  is true for the current Tutee, the button is disabled and its label changes to **"Verify to
  book"** (overriding the existing "Confirm Booking"/"Confirming..." states), plus a small link
  below it to `/application-status`.
- Tutor: `TutorRequestedSessions.vue`'s "Confirm Session" (accept) icon button. Gated on
  `tutorRenewalRequired` only — never-approved Tutors already can't reach this page at all (global
  lockout, `needsTutorApplicationLockout`), so Renewal Required is the only reachable "unverified"
  state here, and it's exactly what the server's Reactive Gate checks too. Button gets `:disabled`
  added and its `title`/`aria-label` changes to explain why.

**Persistent per-session banner, mirrors the same conditions.** A new small component rendered at
the top of `App.vue`'s `<main>`, above the route-specific page header, shown for:
- Tutee: same `needsTuteeVerificationBlock` condition as the TutorDetails gate.
- Tutor: `tutorRenewalRequired`.
Dismissible via a sessionStorage flag (reappears next login/session), each with role-specific copy
and a "Verify Now"/"Renew Now" link to `/application-status`. Deliberately does **not** show during
the Tutee grace period (`tuteeVerificationEnforced` false) — it only ever appears when the gate it's
warning about is actually live, so it can never contradict the button state on the same page.

**Small always-visible status badge, informational (not a gate).** Both dashboard "Welcome back"
headers actually live in `App.vue` itself (`route.path === '/dashboard'` and `'/tch-dashboard'`
blocks), not in `Dashboard.vue`/`TutorDashboard.vue` — so the badge is added once, in App.vue, next
to each. Unlike the banner, this reflects true status unconditionally (ignores
`tuteeVerificationEnforced`/grace period) since it's just information, not an enforcement warning:
green "Verified" (check icon) when `applicationStatus === 'approved'` and the role's own renewal
status is `'verified'`, grey "Unverified" otherwise. Clickable through to `/application-status`;
hovering shows a tooltip with more specific detail (e.g. "You are verified", "Renewal required",
"Application pending").

## Steps

1. `src/router/index.js`: remove the `needsTuteeVerificationBlock` redirect for `book`/`tutors`/
   `tutor-details` routes (~lines 341-353). Leave the Tutor global lockout guard untouched.
2. `src/App.vue`:
   - Delete the `isBookingGateModalOpen` modal markup (~lines 65-101), the `isBookingGateModalOpen`
     ref, `closeBookingGateModal`, and the verification-check body of `handleBookSessionClick` —
     collapse it to an unconditional `router.push('/book')`. Keep `goToVerificationStatus`.
   - Add the verified/unverified badge next to both "Welcome back" header blocks (`/dashboard` and
     `/tch-dashboard`), role-aware, using `profileStore` fields already loaded
     (`applicationStatus`, `renewalStatus` for Tutee; `tutorRenewalStatus` for Tutor).
   - Mount the new banner component at the top of `<main>`, before the existing
     `app-page-header` block, passed `userRole` (or let it read the stores itself).
3. New component `src/components/VerificationBanner.vue`: reads `useProfileStore()` +
   `useAuthStore()` (or equivalent role source), computes the tutee/tutor condition above, renders
   role-specific copy + CTA, handles sessionStorage dismissal.
4. `src/views/TutorDetails.vue`: extend the "Confirm Booking" button's `:disabled` and label logic
   to include the unverified-Tutee case (new highest-priority branch: unverified > submitting >
   no-slots-selected), add the small "Verify your account to book" link to `/application-status`
   directly under the button when in that state.
5. `src/views/TutorRequestedSessions.vue`: add `tutorRenewalRequired` (from `profileStore`) to the
   "Confirm Session" button's `:disabled` condition; update `title`/`aria-label` when disabled for
   this reason.
6. `src/services/tutorApplicationState.js`: no functional change — `needsTuteeVerificationBlock`
   is retained as-is, just gains new call sites (TutorDetails button, banner) alongside its existing
   Vitest coverage.
7. Update `CONTEXT.md` — already done as part of this plan's `/domain-modeling` pass (new
   "Verification & booking gates" glossary section).

## Risks

- Reversing the Phase 3 route-guard redirect is a real behavior change for existing unverified
  Tutees (they can now browse where before they were bounced) — mitigated by the server-side
  Reactive Gate being completely unaffected, so no new booking can actually succeed unverified.
- Two independent client-side mirrors of the same server condition (TutorDetails button + banner
  for Tutee; accept button + banner for Tutor) must stay in sync with `can_create_new_booking`'s
  server logic — drift risk if the backend condition ever changes without updating
  `needsTuteeVerificationBlock` / the new `tutorRenewalRequired` check accordingly.
- Removing the header button's modal changes an existing, working UX pattern — low risk since it's
  purely being replaced by "always navigate," not by a new failure mode.

## Checks to run

- `npm run lint`, `npm run build`.
- `npx vitest run` — existing `tutorApplicationState.test.js` cases must still pass unchanged
  (no functional change to `needsTuteeVerificationBlock`); add coverage for the new
  `tutorRenewalRequired`-based helper if one is extracted.
- Browser verification (required — UI-heavy):
  - Unverified Tutee: can navigate freely to `/book` → `/find-tutors` → `/tutor/:id`; sees the
    persistent banner (dismiss it, refresh, confirm it stays dismissed for the session, reappears
    on a fresh login); "Confirm Booking" button shows "Verify to book" and is disabled; dashboard
    badge shows grey "Unverified" with an informative tooltip.
  - Verified Tutee: no banner, "Confirm Booking" behaves exactly as before, dashboard badge shows
    green "Verified".
  - Tutor with Renewal Required: sees the persistent banner; "Confirm Session" accept button is
    disabled with an explanatory tooltip; dashboard badge shows grey "Unverified".
  - Verified Tutor: no banner, accept button works as before, badge shows green "Verified".
  - Header "Book Session" button always navigates to `/book` regardless of verification state, for
    both roles.

## Changelog

- 2026-07-06: Plan written and approved via `/grill-with-docs` (domain-modeling + grilling). Key
  decisions locked: reverse the Phase 3 tutee route-guard redirect in favor of a single Proactive
  UI Gate at TutorDetails' booking button; remove the header button's modal-based gate entirely;
  gate Tutor accept only on Renewal Required (never-approved Tutors already can't reach the page);
  persistent per-session-dismissible banner for both roles, suppressed during the Tutee grace
  period; informational (non-gating) verified/unverified badge added to both dashboard headers in
  `App.vue` (where those headers actually live, not in `Dashboard.vue`/`TutorDashboard.vue`).
