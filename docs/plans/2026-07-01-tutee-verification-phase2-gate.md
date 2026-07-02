---
title: Tutee enrollment verification — Phase 2 (booking gate & forward-only)
date: 2026-07-01
status: Done
spec: 2026-07-01-tutee-verification-overview.md
---

# Phase 2 — Booking gate & forward-only enforcement

> Part of [Tutee enrollment verification — overview](2026-07-01-tutee-verification-overview.md). Do not
> start Phase 3 without explicit go-ahead once this phase is Done.

<!-- LIVING SUMMARY: keep this section and the Changelog current on every edit -->
## Status & Progress Summary

**Status: Done — implemented, tested, and verified in the browser.**

Scope narrowed from the original outline after tracing the actual code (see Changelog): the tutee-side
**route guard** is deferred to Phase 3, since its only sensible redirect target (`/application-status`) is
tutor-only until Phase 3 generalizes it. Redirecting a tutee there today would immediately hit the
existing role guard and dead-end. Phase 2 ships the full **server-side** gate (the actual source of truth)
plus the **tutor-side router loosening**, which has no such dependency.

## Goal

Enforce document verification at the point of new work (booking creation for tutees, accepting a booking
request for tutors) instead of a global lockout, for both roles, with an existing-tutee grace period —
without yet depending on Phase 3's generalized `/application-status` page.

## Approach

**Endpoints identified (not assumed):**
- Tutee booking creation: `POST bookings/confirm/` → `confirm_payment_and_book` (`views.py`).
- Tutor accepting a pending booking request: `POST bookings/<id>/approve/` → `approve_booking`
  (`views.py`, right below the `#accept booking` comment). `tutor_confirm_booking` (a different function,
  despite the similar name) is unrelated — it marks an already-confirmed, paid session **Completed**, not
  a new-request accept.

**Shared source-of-truth check** (`views.py`, near the Phase 1 `get_document_review_context` helpers):
- `get_verification_application(profile)` — returns `profile.tutor_application` /
  `profile.tutee_application` (via `getattr(profile, name, None)`, safe because Django's reverse-OneToOne
  `DoesNotExist` also subclasses `AttributeError` — same pattern `login_view` already uses via `hasattr`),
  or `None` for any other role.
- `can_create_new_booking(profile)` — `True` only if an application exists, `application_status ==
  'approved'`, and `document_renewal_status() == 'verified'`. Any other state (no application yet, initial
  pending/rejected, renewal due/pending/rejected) returns `False`. For tutees only, this is bypassed
  (`True`) while the grace period hasn't ended yet (see below). Existing bookings, wallet, and dashboard
  access are never touched by this check — it only gates the two endpoints above.

**Grace-period cutover — resolves the outline's open decision.** Settings constant, not a DB field: a new
model/table for a single boolean flag would be heavier than the need, and this repo has no existing
generic "platform settings" table to extend.
- `TUTEE_VERIFICATION_GRACE_PERIOD_DAYS = 30` (documentation constant; the actual gate uses the date
  below, not a live "N days from install" calculation, so it can't be a moving target across server
  restarts).
- `TUTEE_VERIFICATION_ENFORCEMENT_START_DATE = os.getenv('TUTEE_VERIFICATION_ENFORCEMENT_START_DATE')` —
  an ISO date string, **unset by default**. Unset means "not yet enforced" (the safe default — a fresh
  clone/CI run must never start gating tutees just because wall-clock time passed some hardcoded date).
  Whoever actually ships this feature sets the env var once, to (rollout date + 30 days).
- `tutee_verification_enforced()` returns `False` if unset, else compares `timezone.now().date()` against
  the parsed cutover.

**Wiring:**
- `confirm_payment_and_book`: if `role == 'Tutee'` and not `can_create_new_booking`, return
  `403 {"error": "...", "code": "verification_required"}` before any booking/payment work happens.
- `approve_booking`: same check for the authenticated tutor, placed right after the existing "Unauthorized"
  ownership check, before the wallet-balance check.
- **No frontend error-handling changes needed** — traced both call sites: `TutorDetails.vue:confirmBooking`
  already surfaces any `error.response.data.error` via a toast, and `TutorRequestedSessions.vue:
  confirmSession` already surfaces it via `actionError`. The new 403 message displays through existing,
  unmodified code.

**Router loosening (tutor side only this phase):** `needsTutorApplicationAttention` (used by `Login.vue`
for the post-login landing suggestion, kept as-is — not a lockout) stays untouched. A new, narrower
`needsTutorApplicationLockout` is added to `tutorApplicationState.js`, true only for
`kind === 'initial' && ['pending','rejected'].includes(status)` — i.e. never-approved tutors. The router
guard (`router/index.js` ~line 296) swaps its global-redirect check from `needsTutorApplicationAttention`
to this new function, so a renewal-due/pending/rejected tutor (previously locked out of the whole app) can
navigate freely again; only never-approved tutors keep the full lockout.

**Deferred to Phase 3 (documented, not silently dropped):**
- The tutee-side route guard mirroring the tutor one (needs `/application-status` generalized first).
- Resetting `reminder_7day_sent_at`/`reminder_1day_sent_at` on renewal approval (needs the generalized
  admin approval endpoints Phase 3 adds).

## Risks

- This *loosens* current tutor behavior for existing users. Mitigated by keeping `needsTutorApplicationAttention`
  (and Login.vue's use of it) untouched, and by only removing the lockout for the renewal-lapse case, not
  the never-approved case.
- Shipping only the server-side gate without a tutee route guard means a tutee who tries to book without
  verification gets a toast error at submit time rather than being redirected earlier — acceptable and
  temporary; Phase 3 closes this gap.
- `can_create_new_booking` is the single source of truth used by both endpoints — if its logic is wrong,
  both are wrong the same way. Covered by direct unit-style API tests below, independent of the grace-period
  default so the suite never depends on wall-clock date.

## Checks to run

- New backend tests (`ApplicationVerificationSharedBaseTests`-adjacent or a new test class) covering
  `can_create_new_booking` for both roles across every state: no application, initial pending/rejected,
  approved+verified, approved+due, approved+renewal-pending, approved+renewal-rejected — using
  `@override_settings(TUTEE_VERIFICATION_ENFORCEMENT_START_DATE=...)` to force enforcement on/off
  deterministically rather than relying on the real clock.
- New tests hitting `POST bookings/confirm/` and `POST bookings/<id>/approve/` directly, asserting the 403
  + `verification_required` code in the blocked cases and success in the allowed cases.
- `tutorApplicationState.test.js`: new cases for `needsTutorApplicationLockout` (true only for the initial
  kind) alongside the existing `needsTutorApplicationAttention` cases (unchanged).
- Existing tutor-lockout-adjacent tests re-run to confirm nothing else broke.
- `python manage.py makemigrations --check --dry-run` (no model changes expected this phase — confirm).
- `npm run lint`, `npm run build`, `python manage.py test` (full suite, compare against the same
  pre-existing 11 failures/errors from Phase 1 — no new ones).
- Manual browser check: log in as a renewal-due tutor, confirm free navigation across the app (no more
  forced redirect); attempt to accept a pending booking request, confirm the 403 message surfaces.

## Changelog

- 2026-07-01: Outline written alongside the overview and Phase 1 detail plan. Not started.
- 2026-07-01: Phase 1 cut its step 10 (Tutee serializers) as premature/unwired; this phase now explicitly
  owns writing `TuteeApplicationSerializer` / `TuteeDocumentRenewalReviewSerializer` itself.
- 2026-07-02: Fleshed out from the outline into full detail. Two scope findings from tracing the actual
  code, both documented rather than silently absorbed:
  1. **Tutee route guard deferred to Phase 3.** The outline assumed mirroring the tutor route guard for
     tutees now, but its redirect target (`/application-status`) is `role: 'Tutor'`-gated until Phase 3
     generalizes it — wiring it now would dead-end tutees behind the existing role guard. Server-side
     enforcement (the actual source of truth per the original design) ships this phase regardless; the
     route guard is a UX nicety that can land with Phase 3's page.
  2. **Grace-period cutover resolved as an env-driven settings constant, default unset/inactive** — not a
     literal hardcoded date, so the test suite and any fresh environment never starts gating tutees based
     on wall-clock time alone.
  Status set to Approved (ready to implement).
- 2026-07-02: Implemented and verified.
  - Backend: `TUTEE_VERIFICATION_ENFORCEMENT_START_DATE` added to settings;
    `tutee_verification_enforced()`, `get_verification_application()`, `can_create_new_booking()`
    added to `views.py`; wired into `confirm_payment_and_book` and `approve_booking`. TDD: 7 new tests in
    `BookingVerificationGateTests` covering every state for both roles, written red first, all green after
    implementation. Confirmed both call sites' existing generic error handling (`TutorDetails.vue`,
    `TutorRequestedSessions.vue`) already surfaces the new 403 message with no frontend changes needed.
  - Frontend: `needsTutorApplicationLockout` added to `tutorApplicationState.js` (narrower than the
    unchanged `needsTutorApplicationAttention`), router guard swapped to it. TDD: 4 new Vitest cases written
    red first, all green after implementation.
  - Discovered the dev database had never had the Phase 1 migration applied (only the test DB had it via
    `--keepdb`) — applied `python manage.py migrate` to the dev DB as part of this phase's verification.
  - Browser-verified end to end: backdated a seeded tutor's `reviewed_at` 91 days to simulate a due renewal,
    logged in, confirmed free navigation to `/tch-dashboard` with no forced redirect (previously would have
    bounced back to `/application-status` on every navigation), then restored the original timestamp exactly.
  - Full suite: `npm run lint` (18 pre-existing errors, none in touched files), `npm run build` (clean),
    `npx vitest run` (27 tests, all pass), `python manage.py makemigrations --check --dry-run` (no changes
    expected or found), `python manage.py test` (110 tests — 7 more than Phase 1's 103 — same 11
    pre-existing failures/errors, no new ones).
- 2026-07-02: Ran `/code-review` (8 finder angles + verify). Most candidates were false positives caught by
  direct verification (a claimed "tutor bypasses the grace period" that's contradicted by the exact
  `if profile.role == 'Tutee' and ...` guard and by the passing `test_tutor_without_application_blocked_
  from_approving` test; a claimed null-deref that's already guarded by `if application is None: return
  False`; claims that the frontend shows only a generic error that are contradicted by reading the exact
  `error.response?.data?.error` fallback chain against the specific message this diff's 403 responses
  supply). Three real, low-severity findings were fixed:
  - `tutee_verification_enforced()` now wraps `date.fromisoformat()` in try/except, logs an error, and
    fails safe (treats a malformed `TUTEE_VERIFICATION_ENFORCEMENT_START_DATE` as not-yet-enforced) instead
    of letting every booking request 500. New regression test
    `test_malformed_enforcement_date_fails_safe_as_not_enforced` added.
  - Removed the unused `TUTEE_VERIFICATION_GRACE_PERIOD_DAYS` settings constant (nothing read it — folded
    the "30 days" reasoning into the comment above `TUTEE_VERIFICATION_ENFORCEMENT_START_DATE` instead).
  - Reworded `approve_booking`'s 403 message from "renew your enrollment verification" to "complete your
    enrollment verification", since a never-approved-but-rejected tutor (reachable — `login_view` only
    hard-blocks `pending`, not `rejected`) has nothing to "renew".
  Re-ran the full suite after fixes: 8 booking-gate tests, 27 Vitest tests, `makemigrations --check`, and
  the full backend suite (same 11 pre-existing failures, no new ones) all still pass. Status set to Done.
