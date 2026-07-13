# Brief: Tutor onboarding & verification redesign

Follow this brief exactly. Standing rules are in AGENTS.md. Reference:
`docs/plans/2026-07-13-tutor-onboarding-verification-redesign.md` (full spec) and
`docs/mockups/2026-07-13-tutor-onboarding-verification-redesign.html` (approved visual design for
Step 2 and Step 3).

## Scope

In scope — the whole spec (no tickets file exists for this plan yet):

- Remove the tutor route-lockout; gate tutors only at `FindTutors` search visibility.
- New `UserProfile.tutor_onboarding_skipped_at` field + router-enforced onboarding sequence
  (Setup → Subjects → Verify) for tutors who haven't completed it.
- New `Subjects.status` / `proposed_by_tutor` / `proposed_application` fields, a tutor-facing
  propose-subject endpoint, and per-subject admin approve/reject endpoints.
- Frontend: Step 2 (Subjects, Direction B — inline picker, no modal) and Step 3 (Verification,
  Direction C — explainer strip + stacked Submit/Skip) built exactly per the mockup.
- Reuse `src/components/VerificationBanner.vue` for the new "skipped initial verification" case —
  do not build a new banner component.
- Admin UI: proposed-subjects list with per-subject approve/reject in
  `src/views/AdminTutorApplications.vue`.

Out of scope (do not touch):

- Any change to the tutee verification model (`TuteeApplication`, `tutee_verification_enforced()`)
  or the 90-day `TutorDocumentRenewalReview` cadence/UI — both stay exactly as they are.
- Server-side enforcement of the 8-subject cap for the *existing* catalog-pick path
  (`add_tutor_subject`) — it stays UI-only as today. Only the new propose endpoint gets a backend
  cap check.
- NLP, fuzzy search, or embeddings for subject matching — plain `icontains` search only.
- A separate admin queue/screen for proposed subjects outside the existing application review flow.
- The existing "Choose Subjects" modal in `TutorProfile.vue` — leave it completely untouched; the
  new onboarding picker is separate, inline UI.

## Execution checklist

### 1. Backend: search-visibility gate (replaces the route lockout)

- In `backend/studybuddy/views.py`, `get_recommendation_candidate_tutors()` (currently around line
  3732-3747): add `.filter(profile__tutor_application__application_status='approved')` to
  `base_candidates`. This is an inner join — tutors with no `TutorApplication` row at all (never
  submitted, or skipped) are excluded automatically along with `pending`/`rejected` ones. No
  separate null-check needed.
- Do not touch `can_create_new_booking()` (around line 291) — it needs no change; bookings are only
  ever created against tutors who already passed the search filter above.
- Do not touch anything related to `TutorDocumentRenewalReview` — renewal-due tutors must remain
  bookable, unaffected by this change.

**Acceptance criteria**
- [ ] A tutor with no `TutorApplication` row is excluded from `recommend_tutors_view` results.
- [ ] A tutor with a `pending` application is excluded.
- [ ] A tutor with a `rejected` application is excluded.
- [ ] A tutor with an `approved` application is included, regardless of renewal-due status.

### 2. Backend: onboarding-sequence state

- Add `tutor_onboarding_skipped_at` (nullable `DateTimeField`, default `null`) to `UserProfile` in
  `backend/studybuddy/models.py` (class starts around line 60). Generate and apply the migration
  (`python manage.py makemigrations studybuddy` then `migrate`) — no backfill needed, `null` for all
  existing rows.
- Add a small endpoint (e.g. `POST tutor/onboarding/skip-verification/`) that sets
  `tutor_onboarding_skipped_at = timezone.now()` on the authenticated tutor's profile. Wire it in
  `backend/studybuddy/urls.py` near the other `tutor/` endpoints.
- "Sequence complete" condition (used by both the router guard payload below and the reminder
  banner): `tutor_onboarding_skipped_at is not None OR a TutorApplication row exists (any status)`.
  Expose whatever the frontend needs to compute this — check what the tutor's profile/setup-status
  endpoint already returns (likely near where `application_status` is already surfaced) and add
  `tutor_onboarding_skipped_at` to that same payload rather than creating a new endpoint just for
  this field.

**Acceptance criteria**
- [ ] Migration adds the field, applies cleanly, existing rows read `null`.
- [ ] The skip endpoint sets the timestamp for the authenticated tutor only (403 for non-tutors).
- [ ] The tutor's profile/status payload includes `tutor_onboarding_skipped_at`.

### 3. Backend: subject proposals

- Add to `Subjects` (`backend/studybuddy/models.py`, class starts around line 656):
  - `status` — `CharField`, choices `('approved', 'Approved')` / `('pending', 'Pending')`, default
    `'approved'` (so the migration doesn't affect existing catalog rows' visibility).
  - `proposed_by_tutor` — nullable `ForeignKey('Tutor', on_delete=models.SET_NULL, null=True)`.
  - `proposed_application` — nullable `ForeignKey('TutorApplication', on_delete=models.CASCADE,
    null=True, related_name='proposed_subjects')`.
  - Generate and apply the migration.
- `subject_code` generation for proposals: `subject_code` is the primary key and today is supplied
  directly by the admin form (`SubjectSerializer` / `AdminCourseCatalog.vue`) — there is no
  generator to reuse. For proposals, derive it by slugifying `subject_name` (uppercase, spaces →
  hyphens), and on a collision with an existing `subject_code`, append `-2`, `-3`, etc. until unique.
- New endpoint, tutor-facing: `POST tutor/subjects/propose/` — body `{ subject_name, department,
  description }`.
  - Validate `department` against the existing set of catalog department values (query distinct
    `Subjects.department` values, or reuse whatever list `AdminCourseCatalog.vue`/`src/stores/catalog.js`
    already fetches on the frontend side — no free-text department accepted).
  - Create the `Subjects` row (`status='pending'`) and the `TutorSubjects` link in one transaction
    (`expertise_level` default `3`, matching `add_tutor_subject`'s existing default at
    `views.py:4102-4133`).
  - Do **not** call `subject_is_recognized_for_profile` for proposals — nothing to check a brand-new
    name against.
  - Enforce the 8-subject cap: count the tutor's `TutorSubjects` rows regardless of the linked
    subject's `status` (approved + pending together) and reject with a 400 if already at 8.
- Leave `add_tutor_subject` (`views.py:4102-4133`) unchanged — it's still the catalog-pick path,
  still requires an existing `subject_code`, still runs the recognition check.
- New admin endpoint(s), likely a method or sibling view near `AdminTutorApplicationDetailView`
  (`backend/studybuddy/admin_views.py`, around line 1336): `PATCH
  admin/tutor-applications/<pk>/subjects/<subject_code>/` with body `{ action: 'approve' |
  'reject' }`, gated by the existing `IsSuperAdminUser`/admin permission pattern used throughout
  `admin_views.py`.
  - `approve` → set `subject.status = 'approved'`; leave the `TutorSubjects` link in place.
  - `reject` → delete the `TutorSubjects` link, then delete the `Subjects` row.
  - Must work independently of the parent `TutorApplication`'s own approve/reject state (callable
    regardless of whether the application itself has been decided yet).
- `SubjectListView` (`views.py:1920`) must filter to `status='approved'` only, so pending proposals
  never appear as a selectable/searchable catalog entry to anyone but the proposing tutor.

**Acceptance criteria**
- [ ] `POST tutor/subjects/propose/` creates a `pending` `Subjects` row correctly linked to the
      tutor's `TutorApplication` (create the application row first in the test if one doesn't exist
      yet, matching however the real flow creates it).
- [ ] Proposing with a `department` not in the existing catalog list returns 400.
- [ ] Proposing when the tutor already has 8 subjects (any mix of approved + pending) returns 400.
- [ ] `subject_is_recognized_for_profile` is not called for the propose path (assert via mock/patch
      or by using a profile/subject combination that would fail recognition and confirming success
      anyway).
- [ ] Admin approve sets `status='approved'` and leaves the `TutorSubjects` link intact.
- [ ] Admin reject deletes both the `Subjects` row and the `TutorSubjects` link.
- [ ] Both admin actions work regardless of the parent application's current status.
- [ ] `SubjectListView` never returns a `status='pending'` row.
- [ ] Generated `subject_code`s collide-and-dedupe correctly when two tutors propose the same
      subject name.

### 4. Frontend: onboarding router guards

- In `src/router/index.js`, remove the always-on tutor lockout redirect (currently driven by
  `needsTutorApplicationLockout`, `src/services/tutorApplicationState.js:215-222`, wired in around
  `router/index.js:317-335`).
- Replace with a guard that only applies to tutors who have **not** completed the onboarding
  sequence (per the backend condition in item 2): force navigation through Setup → Subjects →
  Verify in order (redirect to whichever of the three is next incomplete); once complete, tutors
  navigate freely with no lockout.
- `TutorPreferenceSetup.vue` (Step 1) stays as-is, no content changes.

**Acceptance criteria**
- [ ] A brand-new tutor (no preferences, no subjects, no application/skip) is redirected to Step 1
      on any route.
- [ ] A tutor who completed Step 1 but not Step 2 is redirected to Step 2.
- [ ] A tutor who completed Steps 1-2 but not Step 3 is redirected to Step 3.
- [ ] A tutor who submitted an application (any status) or skipped navigates freely, no redirects.
- [ ] No route redirects to `/application-status` anywhere anymore for this reason.

### 5. Frontend: Step 2 — Subjects (Direction B)

Build per the mockup exactly (`docs/mockups/2026-07-13-tutor-onboarding-verification-redesign.html`,
first screen block): inline picker inside the Guided Rail's `onboarding-main` panel, no modal.

- Reuse the Guided Rail shell/tokens/classes already established in `src/views/PreferenceSetup.vue`
  (`.onboarding-shell`, `.onboarding-rail`, `.rail-step`, `.rail-num`, `.onboarding-main`, and the
  `color-mix(in srgb, var(--sb-primary) N%, var(--sb-card-bg))` tinting pattern) — do not invent new
  shell classes.
- Selected subjects render as pills above the search box, in the existing `subject-pill`/`X/8`
  counter style from `TutorProfile.vue:207,211-232` — reuse that visual pattern, but this is
  separate markup local to the onboarding view (do not import/reuse `TutorProfile.vue`'s modal
  component).
- Approved subjects and pending proposals must be visually distinct pills (see the mockup: pending
  pills get a warm/amber border+background, approved pills get the standard primary-tinted style).
- Search input filters the catalog live (reuse `SubjectListView` for the query, `icontains` on
  `subject_name`/`subject_code`); results render as a dropdown list below the input.
- When the search yields no matches, show a `+ Propose new subject` button (per the mockup) that
  opens the propose form: subject name (pre-filled from the search text) + department (dropdown
  from existing catalog departments) + optional description. Submits to
  `POST tutor/subjects/propose/` from item 3.
- On successful propose, the new subject appears immediately as a pending pill; on successful
  catalog pick, it appears as an approved pill (calls `add_tutor_subject`, unchanged).
- Enforce the 8-subject cap client-side too (existing pattern at `TutorProfile.vue:886-889`), same
  message.

**Acceptance criteria**
- [ ] Screen matches the mockup's Step 2 block: rail shows "Subjects" as the active step, pills row,
      search input, dropdown results, propose button on empty search.
- [ ] Picking a catalog result adds an approved-style pill and calls the existing
      `add_tutor_subject` endpoint.
- [ ] Proposing a new subject adds a pending-style pill and calls the new propose endpoint.
- [ ] At 8 subjects (any mix), further add attempts are blocked with the existing cap message.
- [ ] Dark mode renders correctly (uses `[data-sb-theme="dark"]` tokens, no hardcoded hex).

### 6. Frontend: Step 3 — Verification (Direction C)

Build per the mockup exactly (second screen block): explainer strip, upload fields, stacked
Submit/Skip actions.

- Reuse the existing document-upload UI/flow that currently creates the `TutorApplication` (school
  ID + enrollment proof) for the `Submit & Finish Onboarding` action — do not rebuild upload logic
  from scratch, wire the existing fields/submit handler into this screen's layout.
- Add the why-strip copy exactly as mocked: "**Verified tutors appear in tutee search.** Until an
  admin approves your documents, tutees can't find or book you — but you can still use the rest of
  the app."
- `Skip for Now` (outline button, second in the stack) calls the new skip endpoint from item 2, then
  navigates to the tutor dashboard.
- `Submit & Finish Onboarding` (filled primary button, first in the stack) submits documents as
  today, then navigates to the tutor dashboard.

**Acceptance criteria**
- [ ] Screen matches the mockup's Step 3 block exactly: rail shows "Verify" active, why-strip, two
      upload rows, two stacked full-width buttons (primary then outline).
- [ ] Submit creates the `TutorApplication` as `pending` (existing behavior) and lands on dashboard.
- [ ] Skip calls the skip endpoint, sets `tutor_onboarding_skipped_at`, and lands on dashboard
      without creating an application.
- [ ] Dark mode renders correctly.

### 7. Frontend: reminder banner (reuse `VerificationBanner.vue`)

- Do **not** create a new component. Add a third case to `src/components/VerificationBanner.vue`'s
  existing `bannerContent` computed (alongside the current `tutee` and `tutor`-renewal cases,
  currently around lines 76-100): a `tutor`-initial-verification case, shown when
  `tutor_onboarding_skipped_at` is set and either no `TutorApplication` exists yet or the existing
  one is `rejected`. Hidden once a `pending` or `approved` application exists.
- Reuse the existing `tutor` tone (purple, `bi-arrow-repeat` icon) rather than introducing a 4th
  tone/color, unless doing so makes the renewal and initial-verification cases indistinguishable in
  a way that's clearly confusing when reading the component's own existing copy side by side — if
  so, note the deviation and what you changed instead.
- Suggested copy (adjust only if needed for clarity against the existing tone's established
  wording style): eyebrow `Verification required`, title `Verify your account to appear in tutee
  search.`, text `Your dashboard stays available, but tutees can't find or book you until your
  documents are approved.`, cta `Verify Now`.
- The `showTutorBanner`/renewal-required computed already checks
  `profileStore.tutorRenewalRequired` — add the new case as its own computed
  (`showTutorInitialVerificationBanner` or similar) checked before or after it in `bannerContent`,
  keeping the existing renewal case's priority/logic completely untouched.

**Acceptance criteria**
- [ ] A tutor who skipped verification (no application, or a rejected one) sees the banner.
- [ ] A tutor with a `pending` or `approved` application does not see this banner case.
- [ ] The existing tutee-verification and tutor-renewal banner cases are unaffected — verify by
      reading the diff shows no behavior change to those two branches.
- [ ] Dismiss behavior (session-storage-based, existing `dismissBanner`/`syncDismissedState` logic)
      works unchanged for the new case.

### 8. Frontend: admin per-subject review

- In `src/views/AdminTutorApplications.vue` (application detail view/panel), add a "Proposed
  subjects" section listing any `Subjects` rows with `status='pending'` linked to the application
  being reviewed (via the new `proposed_application` FK — expose this list from the existing
  application-detail fetch, or a small addition to it).
- Each proposed subject gets its own Approve/Reject buttons, calling the new per-subject endpoint
  from item 3. These controls are independent of the application's own existing Approve/Reject
  controls — both remain fully functional regardless of the other's state.
- On approve/reject, remove that subject from the pending list (optimistic update or refetch,
  whichever pattern this file already uses elsewhere for similar list mutations).

**Acceptance criteria**
- [ ] An application with proposed subjects shows them listed, each with its own approve/reject
      action.
- [ ] Approving one subject doesn't affect the application's own status or other pending subjects.
- [ ] An application with no proposed subjects shows no "Proposed subjects" section (or an
      appropriately empty state — match whatever this file's existing convention is for empty
      optional sections).

## Context

- **Guided Rail tokens/classes**: `--sb-primary`, `--sb-primary-hover`, `--sb-card-bg`,
  `--sb-card-border`, `--sb-text-main`, `--sb-text-muted` are defined in
  `src/assets/main.css:1-71` (light) and `src/assets/main.css:73-` (dark, under
  `[data-sb-theme="dark"]`). Never hardcode hex values for these — use the variables, and
  `color-mix(in srgb, var(--sb-primary) N%, var(--sb-card-bg))` for tinted backgrounds, exactly as
  `PreferenceSetup.vue` already does.
- **`VerificationBanner.vue`** already handles two cases (`tutee`, `tutor`-renewal) with
  session-storage-scoped dismissal keyed by `role:userId`. Read the whole file before editing —
  the new case must slot into the existing `bannerContent` computed's `if` chain without disturbing
  the other two.
- **`Tutor.profile`** is a `OneToOneField(UserProfile, primary_key=True)` (`models.py:225-229`) —
  the join path for the search-gate filter is `profile__tutor_application__application_status`.
- This plan does not touch `tutee_verification_enforced()`/`TuteeApplication` at all — if any code
  path looks like it should but doesn't visibly need to, that's expected; don't "fix" it as part of
  this brief.

## Contract

- Work ONLY this brief — no scope creep, no drive-by refactors.
- TDD: failing test first, then the minimal implementation, matching existing style.
- Run typecheck (frontend: none configured beyond lint/build) and only the **new/targeted** test
  file(s) or test class(es) you add for each backend item — e.g. `python manage.py test
  studybuddy.tests.<NewTestClassName>` — to confirm your own new code is green.
- **Do NOT run the full backend test suite** (`python manage.py test` with no target) — it is
  long-running and will be run separately during review. Do not run it, do not report its output,
  do not use it to decide whether your work is done.
- Frontend: run `npm run lint` and `npm run build` — both are fast and required to be clean.
- NEVER commit, push, branch, or run any git write. Leave the tree dirty.
- Record anything done differently, and why, under Deviations.

## Test evidence

- `python manage.py makemigrations studybuddy`
  - Created `studybuddy/migrations/0076_subjects_proposed_application_and_more.py`.
- `python manage.py migrate`
  - Applied `studybuddy.0076_subjects_proposed_application_and_more` successfully.
- `python manage.py test --keepdb --noinput studybuddy.tests.TutorOnboardingSearchVisibilityTests studybuddy.tests.TutorOnboardingStateTests studybuddy.tests.TutorSubjectProposalTests studybuddy.tests.AdminProposedSubjectReviewTests`
  - Found 17 tests; all passed (`OK`) in 47.066s. The existing `test_postgres` database was
    preserved because the first non-interactive run found it already present.
- `python manage.py makemigrations --check --dry-run`
  - No model changes were missing from migrations.
- `python manage.py check`
  - System check identified no issues.
- `npm run lint`
  - Oxlint: 0 warnings, 0 errors. ESLint completed successfully.
- `npm run build`
  - Vite transformed 324 modules and completed the production build successfully in 2.88s.
- `graphify update .`
  - Rebuilt the local code graph with 5,197 nodes and 10,120 edges.
- The full backend suite was not run, per this brief.

## Deviations

- Tutor registration previously required documents and created a pending `TutorApplication`, which
  made the specified Setup → Subjects → Verify sequence unreachable for a brand-new tutor. The
  smallest coherent change was to make tutor registration account-only, move the same initial
  document validation/compression/application creation to authenticated Step 3, and allow pending
  tutors to log back in. Rejected applications still use the existing resubmit endpoint.
- Step 2 occurs before a `TutorApplication` exists, while the proposal FK is nullable and admin
  review is application-scoped. Proposals therefore link to an existing application immediately
  when one exists; otherwise they remain tutor-linked and are attached atomically when Step 3
  creates the application. Both paths have targeted API coverage.
- Manual in-app browser verification could not run because this session exposed no browser instance
  (`available browsers: []`). The browser-control instructions prohibited switching to an unrelated
  automation backend. The new views were still checked through the required lint/build commands and
  a source-level review of token usage and responsive rules; no browser-render claim is made.
