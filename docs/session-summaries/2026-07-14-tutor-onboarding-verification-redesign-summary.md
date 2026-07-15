# Tutor onboarding & verification redesign — session summary

Plan: `docs/plans/2026-07-13-tutor-onboarding-verification-redesign.md` · Brief:
`docs/briefs/2026-07-14-tutor-onboarding-verification-redesign.md`

## What shipped

Matches the spec, with one disclosed and justified deviation (below):

- **Backend gating**: `get_recommendation_candidate_tutors()` now filters candidates to
  `profile__tutor_application__application_status='approved'`, replacing the old route-wide
  lockout (`needsTutorApplicationLockout`) with a tutee-style search-visibility gate. Login no
  longer blocks pending tutors.
- **Onboarding-sequence state**: `UserProfile.tutor_onboarding_skipped_at` (migration `0076`),
  a skip endpoint, and `profile_status`/login payloads exposing `tutor_onboarding_complete` /
  `tutor_subjects_completed` for the frontend router guard.
- **Subject proposals**: `Subjects.status` / `proposed_by_tutor` / `proposed_application` fields;
  `POST tutor/subjects/propose/` (catalog-search-first, propose-new fallback, 8-subject cap across
  approved+pending, no recognition check on proposals, slugified `subject_code` generation with
  collision dedup); `PATCH admin/tutor-applications/<pk>/subjects/<code>/` for independent
  per-subject approve/reject.
- **Frontend onboarding sequence**: router guards force an incomplete tutor through
  Setup → Subjects → Verify; `TutorSubjectSetup.vue` (Direction B — inline picker, no modal) and
  `TutorVerificationSetup.vue` (Direction C — explainer strip + stacked submit/skip) built exactly
  per the chosen mockups (`docs/mockups/2026-07-13-tutor-onboarding-verification-redesign.html`),
  reusing the real Guided Rail shell/tokens from `PreferenceSetup.vue`.
- **Reminder banner**: reuses the existing `VerificationBanner.vue` as a third content variant
  (no new component), per the plan's finding during the `ui-preview` pass.
- **Admin review**: `AdminTutorApplications.vue` gained a "Proposed Subjects" list with per-subject
  approve/reject, independent of the application's own decision.

## Deviations from plan

1. **Tutor registration restructured to be account-only** (Codex, disclosed in the brief's
   Deviations section). The brief's Setup → Subjects → Verify sequence was unreachable under the
   old flow, where registration itself required documents and created a pending
   `TutorApplication` immediately. The smallest coherent fix: registration now matches tutees
   (account only), and the same document validation/compression/application-creation logic moves
   to the new, authenticated Step 3 (`tutor-application/submit/`). Rejected tutors still use the
   pre-existing `tutor-application/resubmit/` endpoint, untouched. Verified correct and
   well-tested (`TutorOnboardingStateTests`).
2. **Pre-application subject proposals** (Codex, disclosed). Step 2 happens before a
   `TutorApplication` exists, so a proposal made there links to the tutor directly
   (`proposed_application=null`) and gets atomically attached when Step 3 creates the application
   (`Subjects.objects.filter(proposed_by_tutor__profile=profile, proposed_application__isnull=True,
   status='pending').update(proposed_application=application)`). Both paths have targeted test
   coverage.
3. **No manual browser verification** (Codex, disclosed) — the Codex session had no available
   browser instance. Verified instead via full lint/build plus a line-by-line diff comparison
   against the mockup markup/CSS (confirmed matching classes, tokens, and structure).

## Fix rounds

None dispatched back to Codex — no substantive misses found. Two pieces of trivial dead code left
behind by deviation 1 were cleaned up directly (cheaper than a round trip):

1. `src/components/TutorScreeningModal.vue` — the tutor-specific registration screening modal,
   completely orphaned once `Register.vue` no longer shows it. Deleted.
2. `schoolIdFile` / `enrollmentProofFile` fields in `src/stores/registrationinfo.js` — only ever
   read by the now-deleted modal. Removed.

Rebuilt and reran the frontend test suite after both removals to confirm nothing broke.

## Checks run

- `python manage.py test studybuddy.tests.TutorOnboardingSearchVisibilityTests
  studybuddy.tests.TutorOnboardingStateTests studybuddy.tests.TutorSubjectProposalTests
  studybuddy.tests.AdminProposedSubjectReviewTests` — 17/17 pass, matches Codex's logged evidence.
- `python manage.py test` (full suite, fresh database, no `--keepdb`) — 315 tests, 28 failures + 5
  errors. **All pre-existing and unrelated**, confirmed by root-cause tracing (not assumption):
  - A large cluster (`RecommendTutorsViewTests`, `InstitutionScopedMatchingTests`,
    `AlgorithmDemoToolTests`, `DashboardRecommendationServiceTests`,
    `StudentDashboardRecommendationTests`) all fail with `400 != 200` on `recommend-tutors/`. Traced
    to `subject_is_recognized_for_profile()` (`backend/studybuddy/subject_recognition.py`, untouched
    by this diff) returning empty for any profile with no `course` set — several of these test
    fixtures never set one. Nothing to do with the new search-visibility gate; ruled that hypothesis
    out explicitly after checking a real traceback.
  - The remainder (`TutorCashOutTests`, `TutorProfileTests`/`TuteeProfileTests` avatar upload,
    `VerificationDevToolsTests`, `DevWalletFundsTests`, one `SuperAdminRedesignApiTests` seed-data
    unique-constraint error) are in files this diff never touches.
  - Exact same 28 failures + 5 errors count as yesterday's documented baseline
    (`docs/session-summaries/2026-07-13-superadmin-tutor-tutee-stats-summary.md`), and the fresh-vs-
    `--keepdb` reruns produced an identical failure list — reproducible, not flaky, not caused here.
- `npm run build` — green, no errors.
- `npm run test` (Vitest) — 67/67 pass, including `tutorApplicationState.test.js` (unaffected by
  the dead-code cleanup — the two now-dead exports there were left in place, not deleted, to avoid
  test-file surgery under review time pressure; flagged below as a minor follow-up).
- `npm run lint` — 4 pre-existing ESLint errors in `make_algo_pptx.cjs`/`.js`, neither touched by
  this change.

## Commits

1. `feat: gate tutors by search visibility, not a route lockout` (backend: gating, onboarding
   state, subject proposals, admin per-subject review, migration `0076`, all backend tests)
2. `feat: tutor onboarding sequence (setup, subjects, verify-or-skip)` (frontend: router guards,
   registration restructure, Step 2/3 screens, banner reuse, dead-code cleanup)
3. `feat: per-subject approve/reject for tutor-proposed subjects` (frontend: admin review UI)

## What's next

- Minor, non-blocking follow-up: `needsTutorApplicationLockout` and
  `needsTutorApplicationAttention` in `src/services/tutorApplicationState.js` are now dead exports
  (only referenced by their own test file) — a consequence of deviation 1. Left in place rather than
  risk hasty surgery on a well-annotated, plan-referenced test file during review; worth a clean
  removal pass later.
- Per the standard flow, a final whole-branch `/code-review` against the spec is the remaining gate
  before this is considered fully closed out — not skipped here, just not yet run.
