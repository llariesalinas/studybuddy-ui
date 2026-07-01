---
title: tutor-document-renewal-review
date: 2026-07-01
status: Done
spec:
---

# Tutor document renewal review

> Retro-documented. This plan was written *after* the code shipped (commit `66c1441`, "Add tutor document
> renewal review flow"), which landed on `fix/tutor-application-bugfixes` between sessions without a saved
> plan file, in violation of the "document the plan before writing code" convention. This file exists to bring
> the docs into compliance with what's actually in the branch — the code was not reverted or restructured.
> See [`docs/plans/2026-07-01-tutor-application-bugfixes.md`](2026-07-01-tutor-application-bugfixes.md) for how
> this intersects with that session's bugfix work.

## Status & Progress Summary

**Status: Done.** Shipped in commit `66c1441` (2026-07-01), on top of `f23b423` on
`fix/tutor-application-bugfixes`. This is the first slice of the deferred "3-month tutor enrollment
re-verification" feature (GitHub issue #96) — the tutor half only; the tutee-side extension discussed in the
2026-07-01 handoff session is still undesigned.

## Goal

Let an **approved** tutor's enrollment documents be periodically re-verified (every
`TutorApplication.DOCUMENT_RENEWAL_INTERVAL_DAYS` = 90 days from the last approved review) without reusing the
original pending/rejected application lifecycle, and give admins a review queue for renewal submissions
separate from the initial-application queue.

## Approach

New model `TutorDocumentRenewalReview` (FK to `TutorApplication` and `UserProfile`), one row per renewal
submission, with its own `pending`/`approved`/`rejected` status independent of `TutorApplication.application_status`.

`TutorApplication` gained renewal-tracking methods:
- `latest_approved_document_review_at()` — most recent approved renewal's `reviewed_at`, falling back to the
  original application's `reviewed_at` if no renewal has ever been approved.
- `document_renewal_due_at()` — `latest_approved_document_review_at() + 90 days`, `None` if not approved.
- `latest_document_renewal_review()` — most recent renewal submission of any status.
- `document_renewal_status()` — `None` (not approved), `'pending'`/`'rejected'` (latest renewal in that state),
  `'due'` (past the 90-day window, no open renewal), or `'verified'`.
- `can_submit_document_renewal()` — `True` only when status is `'due'` or `'rejected'`.

`tutor_application_resubmit` (`backend/studybuddy/views.py:4436`) now branches on `application_status`: if
`'approved'`, it delegates to `create_tutor_document_renewal_submission(...)`, which creates a
`TutorDocumentRenewalReview` row instead of mutating the approved `TutorApplication` — this is what stops an
approved tutor from being silently reverted to `pending` on resubmit (previously a bug; see bugfix plan step 1).

New surfaces:
- `POST tutor-application/renewal/` (`views.tutor_document_renewal_submit`) — tutee-side renewal submission.
- `AdminTutorDocumentRenewalDetailView` at `admin/tutor-document-renewals/<int:pk>/` — admin review endpoint.
- `AdminTutorApplications.vue` extended to surface renewal reviews alongside initial applications.
- `TutorApplicationStatus.vue` extended (204 lines changed) to show renewal due/pending/rejected state.
- `src/services/tutorApplicationState.js` (new, 205 lines + 78-line test file) — centralizes the
  frontend-side status/label logic for application + renewal state combinations.
- `src/stores/auth.js`, `src/stores/profile.js`, `src/router/index.js`, `Login.vue` — wire renewal-due state
  into login/routing so a tutor with a lapsed renewal is routed appropriately.
- Frontend upload-size constant `MAX_DOCUMENT_UPLOAD_SIZE_BYTES` added to `src/config.js` and used by both
  `TutorScreeningModal.vue` and `TutorApplicationStatus.vue` — this is the frontend half of the
  `MAX_UPLOAD_SIZE` centralization also tracked in the bugfix plan (step 3); the backend half was not done by
  this commit.

Migrations: `0056_tutordocumentrenewalreview.py` (new model), plus an index-merge migration for recommendation
+ document-renewal indexes.

## What this explicitly does not handle

- Tutee-side enrollment verification — tutees have no document-based verification at all today; this commit
  is tutor-only.
- A scheduled job to proactively flag/notify lapsed tutors — `document_renewal_status()` is computed on read
  (login-time / status-check time), not pushed via a background task.
- A dev-mode override to shorten the 90-day interval for testing — not present; still an open question from
  the 2026-07-01 handoff doc.

## Risks

- `document_renewal_status()`/`can_submit_document_renewal()` are computed properties, not stored state — any
  future query needing to filter tutors by renewal status at scale would need to either denormalize or accept
  a Python-side filter after fetch.

## Checks run

Backend test suite gained 207 new lines in `backend/studybuddy/tests.py` covering this flow (per commit diff
stat) — not independently re-run as part of this retro-documentation pass. See the bugfix plan's "Checks to
run" section for the test run covering this session's combined work.

## Changelog

- 2026-07-01: Retro-documented after discovering commit `66c1441` on `fix/tutor-application-bugfixes` had no
  corresponding plan file. Code was not modified as part of writing this doc.
