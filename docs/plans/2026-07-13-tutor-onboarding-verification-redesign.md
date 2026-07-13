---
title: Tutor onboarding & verification redesign
date: 2026-07-13
status: Done
summary: Removes the tutor route-lockout in favor of a tutee-style search-visibility gate, folds verification into one guided onboarding sequence with a skip option, and lets tutors propose subjects missing from the catalog for admin review alongside their application.
spec: ../mockups/2026-07-13-tutor-onboarding-verification-redesign.html
---

# Tutor onboarding & verification redesign

<!-- LIVING SUMMARY: keep this section and the Changelog current on every edit -->

## Status & Progress Summary

**Status (2026-07-14): Done — implemented, reviewed, and verified.** Grilled end-to-end (13
decisions) via `/grill-with-docs`, both onboarding screens mocked and chosen via `ui-preview`
(Step 2: Direction B, inline picker; Step 3: Direction C, explain-then-choose), compiled into
`docs/briefs/2026-07-14-tutor-onboarding-verification-redesign.md` and dispatched to Codex CLI on
`feat/tutor-onboarding-verification-redesign`. `/codex-review` verified independently: reran
Codex's 4 new test classes (17/17 pass) plus the full backend suite on a fresh database (315
tests, 28 failures + 5 errors, all confirmed pre-existing/unrelated by root-cause tracing — same
count as yesterday's documented baseline), `npm run build`/`npm run test` (67/67) green. One
disclosed, justified, well-tested deviation: tutor registration became account-only (matching
tutees) since the brief's Setup→Subjects→Verify sequence was unreachable under the old
documents-at-registration flow; document upload moved to the new Step 3. Cleaned up two pieces of
dead code the deviation left behind (`TutorScreeningModal.vue`, two unused store fields). No fix
round needed. Committed in three stops (backend, frontend onboarding, frontend admin review); full
report in `docs/session-summaries/2026-07-14-tutor-onboarding-verification-redesign-summary.md`.

## Problem Statement

Tutors currently cannot use the app at all until an admin approves their `TutorApplication` (school
ID + enrollment proof): the router redirects every route to `/application-status` until
`application_status == 'approved'`
(`src/router/index.js:317-335`, `needsTutorApplicationLockout` in
`src/services/tutorApplicationState.js:211-219`). Tutees have no equivalent lockout — they're only
blocked from *creating a booking* via `can_create_new_booking()`
(`backend/studybuddy/views.py:291-323`), and only when `tutee_verification_enforced()` is on (it
currently isn't). This mismatch means a tutor who just signed up can't even finish setting up their
profile, while document upload itself is a separate, disconnected step from preference setup
(`src/views/TutorPreferenceSetup.vue`) and subject/expertise selection
(`src/views/TutorProfile.vue`).

Separately, the subject catalog was just centralized (commit `f9dc843`, 2026-07-13) into one global,
admin-curated `Subjects` list. Tutors can only attach subjects that already exist in it
(`add_tutor_subject`, `backend/studybuddy/views.py:4102-4133`, 404s on any unknown
`subject_code`). Our faculty contact wants tutors to be able to teach subjects that aren't on that
list yet, which needs an escape hatch that doesn't undo the catalog curation work just finished.

## Solution

1. **Replace the tutor route-lockout with a search-visibility gate.** An unverified tutor gets full
   app access (no `/application-status` redirect anywhere). The only enforcement point: unverified
   tutors are excluded from `FindTutors` search/recommendation results, so no tutee can book them
   until their application is `approved`. This applies identically whether the tutor never
   submitted, is `pending`, or is `rejected` — and is unaffected by the existing 90-day
   `TutorDocumentRenewalReview` cadence, which keeps working exactly as it does today (renewal-due
   tutors stay bookable, no new restriction).

2. **Fold verification into one continuous onboarding sequence.** `TutorPreferenceSetup` (teaching
   level, mode, rate) → subject/expertise selection → verification upload, enforced in that order by
   router guards, ending in a real choice: submit documents, or **Skip**. Skipping drops the tutor
   onto their dashboard immediately (hidden from search per above) with a persistent reminder banner
   to finish verification later. Submitting creates the `TutorApplication` as `pending`, same as
   today.

3. **Subjects: catalog-first, propose-new as the fallback.** Tutors search/pick from the existing
   global `Subjects` catalog as today (instant, still runs `subject_is_recognized_for_profile`). If
   nothing matches, they can type a new subject name; this creates a `Subjects` row with
   `status='pending'`, tied to their `TutorApplication`, skipping the recognition check (nothing to
   check a brand-new name against). It counts toward the existing 8-subject UI cap
   (`TutorProfile.vue:207,886-889`) immediately. When an admin reviews that tutor's `TutorApplication`
   in `AdminTutorApplications.vue`, any pending subjects show alongside it with their own
   approve/reject action, independent of the application's own approve/reject decision. Approving
   promotes the subject to `status='approved'` (a normal, globally selectable catalog entry from
   then on); rejecting deletes the `Subjects` row and its `TutorSubjects` link outright.

Design references:
- `docs/mockups/2026-07-13-tutor-onboarding-verification-redesign.html` — both onboarding screens,
  chosen from 3 mocked directions each, built on the real Guided Rail shell/tokens from
  `PreferenceSetup.vue` extended to 3 tutor steps:
  - **Step 2 (Subjects) — Direction B**: inline picker, no modal. Search box and results render
    directly in the rail's `onboarding-main` panel (matching Step 3's single-screen style) rather
    than reusing the existing "Choose Subjects" modal from `TutorProfile.vue`; a `+ Propose new
    subject` button sits below the search results.
  - **Step 3 (Verification) — Direction C**: "explain, then choose." A one-line why-verify strip
    above the upload fields, then two stacked full-width actions.
- Interim interactive explainer (catalog-first + propose-new subject picker walkthrough, reviewed
  with the team) remains at
  `docs/mockups/sessions/1678-1783949194/content/explainer.html` — a session working file, not
  promoted, superseded for both screens by the mockup above.

## User Stories

1. As a new tutor, I want to use the app immediately after registering, so that I'm not blocked
   behind an admin approval before I can even look around.
2. As a new tutor, I want to be walked through preference setup, then subjects, then verification
   in one guided sequence, so that I don't have to hunt for a disconnected document-upload screen
   later.
3. As a new tutor, I want the option to skip verification at the end of onboarding, so that I can
   start using the app and submit my documents whenever I'm ready.
4. As a tutor who skipped verification, I want a persistent reminder banner, so that I don't forget
   I still need to submit documents to become bookable.
5. As a tutor, I want to search the existing subject catalog and pick a match instantly, so that
   adding a subject I already know is on the list is fast.
6. As a tutor, I want to propose a subject that isn't in the catalog by typing its name, so that I
   can list what I actually teach even if our admins haven't added it yet.
7. As a tutor, I want my proposed subject's department to still come from the existing catalog
   categories (not free text), so that department-based filtering keeps working even for my
   proposal.
8. As a tutor, I want to see my proposed subject marked "Pending" in my subject list, so that I know
   it isn't live yet and understand why.
9. As a tutee, I want search results to only ever show tutors whose application is approved, so
   that I can't end up trying to book someone who was never verified.
10. As an admin, I want to see any subjects a tutor proposed listed alongside their application when
    I review it, so that I don't have to go hunting for them separately.
11. As an admin, I want to approve or reject each proposed subject individually, independent of the
    application decision, so that I can approve a good tutor while rejecting one bad subject name
    (or vice versa).
12. As an admin, I want an approved proposed subject to become a normal catalog entry, so that other
    tutors can select it too from then on.
13. As an admin, I want a rejected proposed subject to disappear entirely (not linger in a rejected
    state), so that the tutor's subject list and the catalog both stay clean.

## Implementation Decisions

**Backend — gating (`backend/studybuddy/`)**
- `get_recommendation_candidate_tutors()` (`views.py:3732-3747`) — add
  `.filter(profile__tutor_application__application_status='approved')` to `base_candidates`. This
  is an inner join, so tutors with no `TutorApplication` row at all (never submitted, or skipped)
  are excluded automatically along with `pending`/`rejected` ones — no separate null-check needed.
- `can_create_new_booking()` (`views.py:291-323`) is unaffected — bookings are only ever created
  against tutors who already passed the search filter above, so no redundant tutor-side check is
  needed there.
- No change to `TutorDocumentRenewalReview` handling — renewal-due tutors are not additionally
  filtered out of search.

**Backend — onboarding-sequence state**
- Add `UserProfile.tutor_onboarding_skipped_at` (nullable `DateTimeField`). Set when a tutor clicks
  Skip on the verification step; left `null` if they submit documents instead or haven't reached
  that step yet.
- A tutor is considered to have completed the guided sequence once **either**
  `tutor_onboarding_skipped_at` is set **or** a `TutorApplication` row exists (any status). Until
  then, router guards force them through Setup → Subjects → Verify in order; afterward they navigate
  freely.
- Reminder banner condition (frontend, wherever the tutor's authenticated shell renders — likely
  `App.vue` or a tutor dashboard component): show when `tutor_onboarding_skipped_at` is set **and**
  no `TutorApplication` exists yet, or an existing one is `rejected`. Hide once a `pending` or
  `approved` application exists.
- Migration: one new nullable field, no backfill needed (defaults to `null` for all existing
  tutors, meaning nothing about their current state changes on migrate).

**Backend — subject proposals**
- Add to `Subjects` (`models.py:656-663`):
  - `status` — `CharField` with choices `('approved', 'Approved')`, `('pending', 'Pending')`,
    default `'approved'` (so the migration doesn't touch existing catalog rows' visibility).
  - `proposed_by_tutor` — nullable `ForeignKey(Tutor, on_delete=models.SET_NULL, null=True)`.
  - `proposed_application` — nullable `ForeignKey(TutorApplication, on_delete=models.CASCADE,
    null=True, related_name='proposed_subjects')`, so `AdminTutorApplicationDetailView` can pull
    `Subjects.objects.filter(proposed_application=application, status='pending')` directly.
  - `subject_code` generation for proposals: since `subject_code` is the primary key and is
    currently supplied by the admin form when adding a catalog entry
    (`SubjectSerializer`/`AdminCourseCatalog.vue`), proposals need a generated one — slugify
    `subject_name`, uppercase, dedupe with a numeric suffix on collision (e.g.
    `EDUCATIONAL-DATA-VISUALIZATION`, or `-2` if taken). Confirm this scheme still reads sensibly
    next to admin-authored codes before finalizing; flag if it doesn't.
- New endpoint, tutor-facing: `POST /tutor/subjects/propose/` — body `{ subject_name, department,
  description }`. Validates `department` against the existing set of catalog department values
  (reuse whatever list `AdminCourseCatalog.vue`/`catalog.js` already exposes — no free-text
  department). Creates the `Subjects` row (`status='pending'`) and the `TutorSubjects` link in one
  transaction. No `subject_is_recognized_for_profile` check (nothing to check a new name against).
  Enforces the existing 8-subject cap counting pending + approved subjects together.
- `add_tutor_subject` (`views.py:4102-4133`) is unchanged — it still only accepts existing
  `subject_code`s and still runs the recognition check; that's the catalog-pick path.
- New admin endpoints on `AdminTutorApplicationDetailView` (or a sibling view) —
  `PATCH /admin/tutor-applications/<pk>/subjects/<subject_code>/` with `{ action: 'approve' |
  'reject' }`:
  - `approve` → `subject.status = 'approved'`; leave the `TutorSubjects` link in place.
  - `reject` → delete the `TutorSubjects` link, then delete the `Subjects` row.
  - Independent of and callable regardless of the application's own approve/reject state.
- `SubjectListView` (`views.py:1920`, used for the tutee-facing/tutor-facing catalog search) must
  filter to `status='approved'` only — pending proposals must never appear as a selectable/searchable
  catalog entry to anyone but the proposing tutor (who sees it via their own `TutorSubjects` list,
  not this endpoint).

**Frontend — onboarding sequence (`src/views/`, `src/router/index.js`)**
- Router guards enforce Setup → Subjects → Verify order for tutors who haven't completed the
  sequence (per the backend condition above), replacing the current always-on
  `needsTutorApplicationLockout` redirect in `tutorApplicationState.js:211-219` and
  `router/index.js:317-335`.
- `TutorPreferenceSetup.vue` stays as Step 1, unchanged in content.
- Step 2 (subjects/expertise) — build per the chosen mockup
  (`docs/mockups/2026-07-13-tutor-onboarding-verification-redesign.html`, Direction B): an inline
  picker in the rail's `onboarding-main` panel — no modal. Search input filters the catalog live
  (dropdown of matches below it); when nothing matches, a `+ Propose new subject` button appears,
  opening the name + department fields described in the Solution section. Selected subjects render
  as pills above the search box (approved subjects styled normally, pending proposals styled
  distinctly), with the existing `X/8` counter
  (`TutorProfile.vue:207,886-889`) reused as-is. This is a **separate, onboarding-only** picker UI —
  it does not touch or replace the existing "Choose Subjects" modal in `TutorProfile.vue`, which
  stays exactly as it is today for post-onboarding subject editing.
- Step 3 (verification) — build per the chosen mockup
  (`docs/mockups/2026-07-13-tutor-onboarding-verification-redesign.html`, Direction C): a one-line
  "why verify matters" explainer strip above the existing School ID + enrollment proof upload
  fields, then two stacked full-width actions — `Submit & Finish Onboarding` (filled primary) and
  `Skip for Now` (outline secondary). Submit reuses the existing document-upload flow that creates
  the `TutorApplication`; Skip calls a new small endpoint (or a field on the existing tutor-setup
  completion call) that sets `tutor_onboarding_skipped_at`.
- Reminder banner: **reuse the existing `src/components/VerificationBanner.vue`** — it already
  handles exactly this pattern (dismissible per session via `sessionStorage`, tone-based content) for
  a `tutee` verification-required case and a `tutor` renewal-required case. Add a third case —
  `showTutorInitialVerificationBanner` — shown when `tutor_onboarding_skipped_at` is set and no
  `TutorApplication` exists yet or the existing one is `rejected`; hidden once a `pending` or
  `approved` application exists. No new component needed. Copy/tone (icon, color) for this new case
  still needs picking — reuse the existing `tutor` tone (purple, `bi-arrow-repeat` currently used for
  renewal) or introduce a 4th tone; a small decision to make during implementation, not a mockup-pass
  item.

**Frontend — admin review (`src/views/AdminTutorApplications.vue`, `src/stores/`)**
- Application detail view gains a "Proposed subjects" list alongside the existing document review,
  each row with its own Approve/Reject buttons calling the new per-subject admin endpoint. Existing
  application-level Approve/Reject controls are unchanged and act independently.

## Testing Decisions

- Backend tests (Django `APITestCase`, matching existing patterns in `backend/studybuddy/tests.py`):
  - Search/recommendation: `recommend_tutors_view` / `get_recommendation_candidate_tutors` excludes
    tutors with no application, a `pending` application, and a `rejected` application; includes
    tutors with an `approved` application regardless of renewal-due status.
  - Onboarding-sequence state: `tutor_onboarding_skipped_at` is set correctly by the skip action and
    left `null` on submit; the "sequence complete" condition (skipped OR application exists) is
    covered for all four combinations.
  - Subject proposals: `POST /tutor/subjects/propose/` creates a `pending` `Subjects` row linked to
    the correct `TutorApplication`; rejects a department not in the existing catalog list; enforces
    the 8-subject cap across approved + pending; does not run `subject_is_recognized_for_profile`.
  - Admin per-subject review: approve flips `status` to `approved` and leaves the tutor's
    `TutorSubjects` link intact; reject deletes both the `Subjects` row and the link; both actions
    work regardless of the parent application's own status.
  - `SubjectListView` never returns `status='pending'` rows.
- No frontend component tests are added, per this repo's convention — `npm run lint` and `npm run
  build` are the baseline frontend checks; manual browser verification of the onboarding sequence
  and admin review screen once the visual design is chosen.

## Out of Scope

- **Reminder banner copy/tone.** Reuses the existing `VerificationBanner.vue` component (no new
  component or mockup needed), but the exact copy and whether it gets its own tone or reuses the
  existing `tutor` (renewal) tone is still an open small decision — see the banner note under
  Implementation Decisions.
- Server-side enforcement of the 8-subject cap for catalog picks (`add_tutor_subject`) — that cap is
  currently UI-only (`TutorProfile.vue`) with no backend check; this plan adds a backend check only
  for the new propose endpoint, not retroactively for existing catalog-pick additions. Flagged
  separately, not bundled into this change.
- Any change to the tutee verification model (`TuteeApplication`,
  `tutee_verification_enforced()`) — this plan only brings tutor gating in line with the *existing*
  tutee behavior, it doesn't touch how tutee enforcement itself works.
- Any change to the 90-day `TutorDocumentRenewalReview` cadence or its review UI.
- NLP, fuzzy search, or embeddings for subject-name matching — catalog search stays simple
  substring/icontains matching; proposals are plain typed text with no automated similarity check
  against existing entries.
- A separate admin queue/screen for proposed subjects outside the existing application review flow.

## Further Notes

- This plan resolves a naming overlap worth flagging: the ask used "reverification," but nothing
  here changes the 90-day *renewal* flow — the change is entirely to *initial* verification gating
  and onboarding. Renewal-due tutors were never route-locked-out and remain unaffected.
- `subject_code` generation for proposals (slugified name + numeric-suffix dedupe) is a reasonable
  default but not battle-tested against the admin-authored code conventions already in the catalog
  — worth a quick sanity check against real catalog entries during implementation before treating it
  as final.

## Changelog

- 2026-07-13: Spec created from `/grill-with-docs` interview (13 decisions) + interactive HTML
  explainer reviewed with the team, including a follow-up subject-picker storyboard section added
  on request. Status: Approved. Onboarding screen visuals explicitly deferred to a `ui-preview`
  mockup pass before frontend implementation starts.
- 2026-07-13: Ran `ui-preview` for the Step 3 (Verification) screen — 3 directions mocked on the
  real Guided Rail shell/tokens from `PreferenceSetup.vue`; Direction C ("explain, then choose")
  picked and promoted to `docs/mockups/2026-07-13-tutor-onboarding-verification-redesign.html`,
  linked from this plan's `spec:` frontmatter. Found that the reminder banner can reuse the existing
  `VerificationBanner.vue` component as a third content variant instead of needing new UI. Step 2's
  subject-picker screen and the banner's exact copy/tone remain open, moved to Out of Scope as
  follow-up mockup/decision items.
- 2026-07-13: Ran `ui-preview` for the Step 2 (Subjects) screen — 3 directions mocked (extend the
  existing `TutorProfile.vue` modal, inline picker with no modal, or modal-plus-quiet-propose-link);
  Direction B (inline, no modal) picked and added to the same promoted mockup file alongside Step 3.
  Onboarding screen visual design is now fully decided — only the reminder banner's exact copy/tone
  remains open.
- 2026-07-14: Created dedicated branch `feat/tutor-onboarding-verification-redesign` (previous work
  was sitting uncommitted on the unrelated `feat/admin-role-consolidation` branch) and committed the
  plan/mockup docs there. Compiled the full spec into
  `docs/briefs/2026-07-14-tutor-onboarding-verification-redesign.md` via `/codex-brief` for Codex
  CLI dispatch, per user instruction explicitly telling Codex to skip the long-running full backend
  test suite and only run its own new/targeted tests — full-suite verification deferred to
  `/codex-review`. Status: In Progress.
- 2026-07-14: `/codex-review` verified independently — reran Codex's 4 new test classes (17/17
  pass) plus the full backend suite on a genuinely fresh database (315 tests, 28 failures + 5
  errors), root-cause-traced every failure cluster to confirm all are pre-existing and unrelated
  (a `subject_is_recognized_for_profile` course-requirement issue in untouched code, plus
  payment/avatar/dev-tools tests in untouched files) rather than assuming from the failure count
  alone. `npm run build` and `npm run test` (67/67) green. Reviewed the full diff against every
  checklist item; found Codex's one disclosed deviation (account-only tutor registration, moving
  document upload to Step 3) justified and well-tested. Cleaned up two pieces of dead code the
  deviation left behind (`TutorScreeningModal.vue`, two unused store fields) directly rather than
  a Codex fix round. Committed in three logical stops (backend; frontend onboarding sequence;
  frontend admin review UI). Session summary at
  `docs/session-summaries/2026-07-14-tutor-onboarding-verification-redesign-summary.md`. Status:
  Done. Remaining, not yet run: the final whole-branch `/code-review` against the spec.
