---
title: Tutor verification relocation
date: 2026-07-08
status: Approved
spec: ../specs/2026-07-08-tutor-verification-relocation-design.md
---

# Tutor verification relocation

## Status & Progress Summary

**Status:** Approved — design confirmed (action-specific gate, delete superseded onboarding UI,
drop the rejected-tutor re-registration path); not yet implemented.

## Goal

Move tutor enrollment verification (School ID + proof of enrollment) off registration/onboarding so
tutors register free and verify later, gated only at accepting a booking — mirroring how tutee
verification already works.

## Approach

`approve_booking` already calls `can_create_new_booking`, the same gate `confirm_payment_and_book`
uses for tutees, so the action-specific gate for tutors already works once a tutor can reach it
without an application. The change is mostly subtraction: stop requiring documents at registration,
stop the router's full-app lockout for never-approved tutors, and let the existing
`/application-status` page (already built to serve first-time tutee submissions) also serve
first-time tutor submissions. The one real gap is `tutor_application_resubmit`, which 404s when no
`TutorApplication` exists yet — it needs the same `get_or_create` treatment
`tutee_application_resubmit` already has. Ship backend first (register_user + resubmit endpoint),
then the frontend pieces that depend on it, then delete the superseded onboarding UI last.

## Steps

1. **Backend: stop requiring documents at registration.** In `register_user`
   (`backend/studybuddy/views.py`), remove the `school_id`/`enrollment_proof` 400 check and the
   `TutorApplication.objects.update_or_create(...)` block (plus its confirmation-email call) from
   the `role == "Tutor"` branch. Keep `Tutor.objects.get_or_create(profile=profile)` and the
   `PlatformActivity` registration log. Remove the `is_rejected_tutor` recovery branch in the
   `existing_user` check so re-registering with an existing email always returns "User already
   exists" for both roles.
2. **Backend: make `tutor_application_resubmit` create-on-first-submit.** Change the
   `TutorApplication.objects.select_for_update().get(...)` lookup (404 if missing) to
   `get_or_create`, mirroring `tutee_application_resubmit` exactly — `created=True` sends the
   "application received" email and logs `PlatformActivity`, then returns the "submitted
   successfully" response; the existing pending/approved/rejected branches run unchanged when
   `created=False`.
3. **Backend tests.** In `backend/studybuddy/tests.py`: update tests that assert Tutor registration
   requires/accepts `school_id`/`enrollment_proof` (should now succeed without them, and no
   `TutorApplication` should exist after registration); add a test that `tutor_application_resubmit`
   creates a `TutorApplication` on first call for a tutor with none (parallel to the existing
   `tutee_application_resubmit` first-submission test); remove/update any test relying on the
   `is_rejected_tutor` re-registration recovery path.
4. **Frontend: generalize the verification-gate helper.** In
   `src/services/tutorApplicationState.js`, delete `needsTutorApplicationLockout` and add
   `needsTutorVerificationBlock(snapshot)`, mirroring `needsTuteeVerificationBlock` minus the
   enforcement-flag check (tutors have never had a grace period).
5. **Frontend: remove the router's full-app lockout for tutors.** In `src/router/index.js`, remove
   the `needsTutorApplicationLockout` import and the `hasTutorApplicationLockout` block. Tutors are
   now governed by the same rules as tutees: authentication, profile-completion (`/tutor-setup`),
   role protection — nothing auto-redirects to `/application-status`.
6. **Frontend: generalize the banner.** In `src/components/VerificationBanner.vue`, replace
   `showTutorBanner`'s renewal-only condition with `needsTutorVerificationBlock`, and branch the
   copy on whether `profileStore.applicationStatus === 'approved'` (renewal wording) vs. not
   (first-time "verify your enrollment" wording), matching the design spec's copy exactly.
7. **Frontend: generalize the initial-submission page.** In `src/views/TutorApplicationStatus.vue`,
   rename `showInitialTuteeSubmission` to `showInitialSubmission` and drop the `isTutee.value &&`
   restriction. Adjust the copy that currently hardcodes "before booking your first session" to be
   role-neutral.
8. **Frontend: simplify registration.** In `src/views/Register.vue`, remove the
   `TutorScreeningModal` import/usage and the `showScreeningModal` branch in `handleRegister` —
   `submitRegistration()` runs directly for both roles. In `buildRegistrationPayload`, drop the
   `FormData`/file-upload branch for `role === 'Tutor'`; both roles now send the same JSON payload.
   The post-submit redirect drops the tutor-specific branch — both roles go to
   `{ name: 'login', query: { registered: 'success', email } }`.
9. **Delete superseded files.** Remove `src/components/TutorScreeningModal.vue`,
   `src/views/TutorApplicationSubmitted.vue`, and the `/tutor-application-submitted` route in
   `src/router/index.js`.
10. **Update architecture docs.** Note the change in `docs/architecture/booking-flow.md` if it
    references the old tutor-registration-time verification step.

## Risks

- **Test coverage gap on `approve_booking`.** `BookingVerificationGateTests` already exercises the
  gate; confirm it still passes once tutors can genuinely have no `TutorApplication` at all (not
  just a pending/rejected one) — the "no application" case may not have been reachable before.
- **Stale sessions mid-rollout.** A tutor who registered before this change already has a
  `TutorApplication`; nothing in this plan touches existing rows, so their experience is unaffected
  (they may still see the renewal-style banner if applicable).
- **Copy drift.** The banner and `/application-status` page now serve both an "initial" and
  "renewal" tutor state with shared components — double check no leftover string says "book" when
  the tutor-facing action is "accept".

## Checks to run

- `python manage.py test studybuddy.tests.BookingVerificationGateTests` and any updated
  registration/resubmit test classes — all passing.
- `python manage.py test` (full suite) — no new failures beyond the pre-existing baseline.
- `npm run lint` and `npm run build` — passing.
- Manual verification in the browser: register a new Tutor account with no file upload, log in,
  confirm dashboard/profile/schedule are all reachable, confirm the `VerificationStatusCard` and
  dashboard banner both prompt for verification, submit documents via `/application-status`, and
  confirm `approve_booking` still 403s with `verification_required` before approval.

## Changelog

- 2026-07-08: Plan created and Approved after design confirmation (spec at
  `docs/specs/2026-07-08-tutor-verification-relocation-design.md`). Not yet implemented.
