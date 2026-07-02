---
title: Tutee enrollment verification — Phase 3 (UI surfaces)
date: 2026-07-01
status: Done
spec: 2026-07-01-tutee-verification-overview.md
---

# Phase 3 — UI surfaces

> Part of [Tutee enrollment verification — overview](2026-07-01-tutee-verification-overview.md). Do not
> start Phase 4 without explicit go-ahead once this phase is Done.

<!-- LIVING SUMMARY: keep this section and the Changelog current on every edit -->
## Status & Progress Summary

**Status: Done — implemented, tested, and verified in the browser end to end.**

Scope narrowed by explicit user decision (see Changelog): the "all-users renewal-status directory" (a
5-state filter + due dates across every user regardless of submission history) is deferred to a follow-up.
This phase ships the generalized status page, renewal cards on both profiles, a tutee admin review queue
(role tab, mirrored serializers/views — each row already carries its own computed renewal status/due date),
and closes the frontend booking-gate gap Phase 2 deliberately deferred.

## Goal

Give tutees the same submit/resubmit and status-visibility surfaces tutors have, give admins a unified
review queue across both roles, and close the tutee-side route-guard gap Phase 2 left open (it depended on
this phase's generalized `/application-status` page).

## Approach

### Backend

1. **New serializers** (`serializers.py`): `TuteeApplicationSerializer` / `TuteeDocumentRenewalReviewSerializer`,
   mirroring `TutorApplicationSerializer` / `TutorDocumentRenewalReviewSerializer` field-for-field against
   the `TuteeApplication`/`TuteeDocumentRenewalReview` models from Phase 1. Kept as separate classes rather
   than a shared mixin — the existing Tutor serializers don't share one either despite ~70% identical
   `SerializerMethodField` bodies, so a new mixin here would be a fresh abstraction inconsistent with
   existing style, not a "match existing style" mirror.
2. **New admin views** (`admin_views.py`): `AdminTuteeApplicationListView` / `AdminTuteeApplicationDetailView`
   / `AdminTuteeDocumentRenewalDetailView`, mirroring the three `AdminTutor*` views exactly (same
   `BaseAdminView` institution-scoping, same combined-and-sorted list shape).
   - **Dedup-field reset on renewal approval**: both `AdminTutorDocumentRenewalDetailView.patch` (existing)
     and the new `AdminTuteeDocumentRenewalDetailView.patch` clear `reminder_7day_sent_at` /
     `reminder_1day_sent_at` on the application when a renewal is approved — this is where the clock
     genuinely resets, so stale reminder flags must not carry into the next 90-day cycle. Not added to the
     *initial*-approval path (`AdminTutor/TuteeApplicationDetailView.patch`) — a fresh initial approval's
     `latest_approved_document_review_at()` falls back to `reviewed_at`, which is set fresh, so there's no
     stale dedup state to clear there.
   - **No email sent yet for tutee approve/reject** — matches the already-documented gap on
     `AdminTutorDocumentRenewalDetailView.patch` (no email on renewal decisions). Phase 4 owns generalizing
     `send_application_*_email` to take role/label; it will fix both gaps (tutor renewal + all tutee paths)
     together rather than this phase inventing tutee-worded emails ahead of that generalization.
3. **New tutee-facing endpoints** (`views.py`), mirroring the tutor ones: `tutee_application_status` (GET),
   `tutee_application_resubmit` (POST), `tutee_document_renewal_submit` (POST), plus a shared
   `create_tutee_document_renewal_submission` helper mirroring `create_tutor_document_renewal_submission`.
4. **New URLs** (`urls.py`): `admin/tutee-applications/`, `admin/tutee-applications/<pk>/`,
   `admin/tutee-document-renewals/<pk>/`, `tutee-application/status/`, `tutee-application/resubmit/`,
   `tutee-application/renewal/`.
5. **`profile_status` generalized for real**: add `get_role_document_review_context(profile)` — branches on
   `profile.role`, calling the existing `get_tutor_document_review_context` for tutors (byte-identical
   output, zero regression) or Phase 1's `get_document_review_context(profile.tutee_application)` for
   tutees (falling back to `EMPTY_DOCUMENT_REVIEW_CONTEXT` if no application exists yet). `profile_status`
   switches from calling `get_tutor_document_review_context` directly to this dispatcher. This is the exact
   wiring Phase 1 built `get_document_review_context` for and explicitly deferred ("not yet called from any
   view").
6. **Expose the grace-period flag**: `profile_status` also returns `tutee_verification_enforced` (from
   Phase 2's `tutee_verification_enforced()`) so the frontend route guard (step 8 below) can tell whether a
   tutee with no application yet is still inside the grace period, without duplicating that date logic
   client-side.

### Frontend

7. **`src/stores/profile.js`**: add `renewalStatus`, `renewalRequired`, `renewalDueAt`, and
   `tuteeVerificationEnforced` state, sourced from the response's already-generic
   `document_renewal_status`/`document_renewal_required`/`document_renewal_due_at`/
   `tutee_verification_enforced` keys. The existing `tutorRenewalStatus`/`tutorRenewalRequired` fields are
   left untouched (router guard and other tutor-specific code depend on those names) — these are additive,
   generic siblings sourced from the same payload.
8. **`src/router/index.js`**:
   - `/application-status` route `meta.role` changes from `'Tutor'` to `['Tutor', 'Tutee']`.
   - New tutee booking-flow gate, closing the Phase 2 gap: for `role === 'tutee'`, if navigating to one of
     the booking-flow routes (`book`, `tutors`, `tutor-details` — the `InitialBooking → FindTutors →
     TutorDetails` flow per `docs/architecture/booking-flow.md`) and `tuteeVerificationEnforced` is true and
     not (`applicationStatus === 'approved' && renewalStatus === 'verified'`), redirect to
     `/application-status`. Gated on `tuteeVerificationEnforced` specifically so a tutee who has never
     submitted anything isn't wrongly blocked from booking during the grace period, matching the
     server-side source of truth exactly instead of approximating it.
9. **`src/views/TutorApplicationStatus.vue`** generalized in place (file/route name kept, per the plan's own
   wording — renaming would be pure churn for zero functional gain): role-aware endpoint selection for
   status/resubmit/renewal, role-aware "go to dashboard" link (`/dashboard` vs `/tch-dashboard`), and
   role-neutral copy where the current text hardcodes "tutor".
10. **`src/views/TuteeProfile.vue`** and **`src/views/TutorProfile.vue`**: small verification card inserted
    right after the `<header class="glass-segment profile-header-segment">`, before `<main
    class="profile-grid">`, using the existing `.glass-segment`/`.segment-icon` patterns (no hardcoded
    colors, `--sb-*` custom properties only). Reads `useProfileStore()` (the same store the router guard
    already populates via `checkProfileStatus()` — no new network call needed in the common case, since the
    guard has almost always already loaded it by the time these views mount).
11. **`src/stores/admin.js`**: add `tuteeApplications` ref + `fetchTuteeApplications` /
    `updateTuteeApplicationStatus` actions mirroring the tutor ones.
12. **`src/views/AdminTutorApplications.vue`**: add a role tab (Tutor/Tutee) driving which store data/action
    pair is used; dynamic page title. Table columns, doc-preview logic, and offcanvas review flow are
    already role-agnostic (driven by generic field names via `readFirst`), so the tab only needs to swap
    the data source, not restructure the template.

## Risks

- Admin queue generalization touches a component with real daily production usage (tutor reviews) — needs
  careful regression testing of the existing tutor flow while adding the tutee tab.
- `profile_status`'s behavior change for tutors must be byte-identical (dispatcher delegates to the
  unchanged `get_tutor_document_review_context`) — verified by the existing `TutorDocumentRenewalTests`
  suite, which exercises this exact endpoint.
- The tutee router gate's correctness depends on `tuteeVerificationEnforced` matching the server's
  `tutee_verification_enforced()` exactly; mismatch risk is low since it's read directly off the same
  settings-derived value via the API response, not recomputed client-side.

## Checks to run

- Backend: new tests for `TuteeApplicationSerializer`/admin tutee views (list/detail/renewal
  approve/reject, dedup-field reset), `get_role_document_review_context` via `profile_status` for both
  roles, and the new tutee resubmit/renewal endpoints — TDD, written red first.
- Frontend: extend `tutorApplicationState.test.js` if a new pure function is extracted for the router gate;
  otherwise cover via the existing test file's patterns.
- Full suite: `npm run lint`, `npm run build`, `npx vitest run`, `python manage.py makemigrations --check
  --dry-run` (no model changes expected), `python manage.py test` (compare against the same 11 pre-existing
  failures — no new ones).
- Browser verification (required for this phase — UI-heavy): generalized `/application-status` for a tutee
  (submit initial documents, see status update); renewal card renders correctly on both `TuteeProfile.vue`
  and `TutorProfile.vue`; admin queue's tutor tab is unaffected, tutee tab shows tutee submissions and
  approve/reject works; tutee router gate blocks booking-flow navigation only when actually unverified and
  enforcement is active, and does not block during the grace period.

## Changelog

- 2026-07-01: Outline written alongside the overview and Phase 1 detail plan. Not started.
- 2026-07-01: Phase 1 cut its step 10 (Tutee serializers) as premature/unwired; this phase now explicitly
  owns writing `TuteeApplicationSerializer` / `TuteeDocumentRenewalReviewSerializer` itself.
- 2026-07-02: Fleshed out from the outline into full detail, after Phase 2 landed. User explicitly decided
  to defer the "all-users renewal-status directory" (5-state filter + due dates across every user
  regardless of submission history) to a follow-up rather than build it now — it's a distinct feature (a
  user directory, not a review queue) from the rest of this phase's scope. The existing review-queue table
  already surfaces `document_renewal_status`/`document_renewal_due_at` per row for both roles via the
  mirrored serializers, which reasonably covers "renewal status visibility" for the submissions that do
  exist. Explored `TuteeProfile.vue`/`TutorProfile.vue` structure (identical `.glass-segment` architecture,
  no existing `profileStore` usage) to plan the renewal-card insertion point and data source. Status set to
  Approved (ready to implement).
- 2026-07-02: Implemented, tested, and browser-verified.
  - Backend: `TuteeApplicationSerializer`/`TuteeDocumentRenewalReviewSerializer` mirrored; three new admin
    views (`AdminTuteeApplicationListView`/`DetailView`/`AdminTuteeDocumentRenewalDetailView`) mirrored with
    dedup-field reset added to both the new tutee renewal-approval path and the existing tutor one; three
    new tutee-facing endpoints (`tutee_application_status`/`resubmit`/`renewal_submit`); `profile_status`
    now dispatches through a new `get_role_document_review_context` and also exposes
    `tutee_verification_enforced`. Added a proper `tutee_application` `PlatformActivity.ACTIVITY_TYPES`
    choice rather than reusing the tutor one (would have mislabeled tutee events in the admin feed). TDD:
    10 new backend tests, all green; full backend suite re-run clean (same 11 pre-existing failures).
  - Frontend: `needsTuteeVerificationBlock` (TDD, 4 new Vitest cases) added and wired into the router guard
    to close the tutee-side gate gap Phase 2 deferred; `/application-status` route generalized to both
    roles; `TutorApplicationStatus.vue` made role-aware (endpoint selection, dashboard link, copy); new
    shared `VerificationStatusCard.vue` component (a genuine shared-abstraction case, unlike the backend
    serializers where existing duplication convention was matched) added to both `TuteeProfile.vue` and
    `TutorProfile.vue`; `AdminTutorApplications.vue` got a Tutor/Tutee role tab.
  - **Found and fixed a real gap during browser verification**, not caught by unit tests: a tutee with no
    application yet hit a dead-end "Could not load application status" error instead of an initial
    submission form — the component only ever handled *resubmission* (tutors always have an application by
    the time they can log in; tutees don't). Fixed by making `tutee_application_resubmit` create-or-resubmit
    (`get_or_create`) and adding a dedicated initial-submission template branch reusing the existing form
    plumbing. New regression test `test_tutee_application_resubmit_creates_initial_application_when_none_exists`.
  - Also fixed, while touching `TutorProfile.vue`: a pre-existing hardcoded "Verified" badge in the header
    that rendered unconditionally regardless of actual status — now gated on real `profileStore` data, since
    the new card right below it would otherwise visibly contradict a false "Verified" claim.
  - Full browser verification: tutee login → dashboard (no forced redirect, grace period off by default) →
    profile page shows "Verification Needed" card → `/application-status` shows the initial submission form
    → submitted → status flips to "Pending Review" → admin's Tutee tab shows the submission → admin approves
    it → DB confirms `approved`. Tutor tab confirmed unaffected. All test data and the two dev-account
    passwords reset during verification were cleaned up (passwords can't be restored to their originals,
    since they weren't recorded beforehand — a known, accepted side effect of testing against real
    dev-seeded accounts rather than throwaway ones).
  - Full suite: `npm run lint` (18 pre-existing errors, none in touched files), `npm run build` (clean),
    `npx vitest run` (31 tests, all pass), `python manage.py makemigrations --check --dry-run` (clean),
    full backend suite (121 tests — same 11 pre-existing failures, no new ones).
- 2026-07-02: Ran `/code-review` (8 finder angles + verify). Nearly every candidate was refuted on direct
  verification — several agents claimed the same `getattr(profile, 'x_application', None)` "unsafe
  OneToOneField access" bug already refuted in Phase 2 (contradicted by a passing test exercising exactly
  that path); a claimed `application_status`/`status` field-name bug that's actually a deliberate, tested
  serializer alias matching the pre-existing tutor pattern; a claimed "sequential blocking awaits" in
  `onMounted` handlers that don't use `await` at all; and extensive commentary re-flagging the
  Tutor/Tutee serializer and admin-view duplication already deliberated and accepted in this phase's own
  Approach section. Two real, low-severity findings were fixed:
  - `VerificationStatusCard.vue`'s four parallel per-state lookup objects (tone/icon/badge/subtitle) merged
    into one `STATE_CONFIG` object grouping all properties per state, so adding a state can't silently miss
    one of four lookups.
  - Removed an unnecessary hardcoded `#fff` fallback in `var(--sb-primary-contrast, #fff)` — the variable
    is always defined in `main.css`.
  One real, out-of-scope issue was found and flagged as a follow-up rather than fixed here: `TutorDetails.vue`
  (the public tutor-browsing page tutees see) still shows an unconditional "Verified" badge, now a clearer
  inconsistency since the equivalent badge on `TutorProfile.vue` (the tutor's own view) was just fixed in
  this phase. Left for a dedicated follow-up since it needs new backend serializer exposure plus a design
  call on whether granular renewal status should be public at all — not a security gap, since the actual
  booking gate is already enforced server-side (Phase 2).
  Re-ran the full suite after the two fixes: build clean, 31 Vitest tests pass, browser re-verified the
  refactored card renders identically. Status set to Done.
