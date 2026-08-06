---
title: Subject Selection Onboarding + Commission Disclosure
date: 2026-08-07
status: In Progress
summary: Add subject descriptions and a Tutee onboarding subject picker; disclose the 10% commission to Tutors before they set their rate, with persisted acceptance.
spec: ../mockups/2026-08-07-tutee-subject-selection.html
---

# Subject Selection Onboarding + Commission Disclosure

## Status/Progress Summary

**2026-08-07:** In Progress. Discovered during implementation that `PreferenceSetup.vue` already
has a Tutee subject-selection card (Card 3, using `SubjectTaxonomyPicker`) that already persists
to `Preference` via `POST preferences/` → `save_preferences`. This was missed by the pre-grilling
exploration (stale relative to work already on `feat/subjects-reseed`). Steps 5 and 6 needed no
new code as a result — the `description` field/display work (steps 1-4) covers this screen for
free since it shares `SubjectTaxonomyPicker`. Commission disclosure (steps 6-8 in the numbered
list, i.e. the `Tutor` field/onboarding checkbox/router guard) still to implement.

## Changelog

- 2026-08-07: Plan created from grilling session. Status: Approved.
- 2026-08-07: Implementation started. `Subjects.description` field/migration, admin catalog form
  field, `SubjectTaxonomyPicker` description display, and seed description backfill (all 121
  seeded subjects) are done. Found Tutee subject-selection onboarding already exists — no new
  frontend/backend work needed there. Status: In Progress.

## Goal

1. Give both Tutees and Tutors a subject-selection experience during onboarding with per-subject
   descriptions, so users understand what a subject actually covers before picking it.
2. Inform Tutors of the platform's 10% commission before they set their hourly rate, with a
   persisted, auditable acceptance record — closing a gap where commission is currently disclosed
   only after the fact, in the wallet ledger.

## Approach

**Corrected scope:** the original request said "courses," but the actual target is `Subjects`
(what a Tutee needs tutoring in / what a Tutor teaches) — `Course` (degree program) is untouched.

**Subjects:**
- Tutee subject-selection is folded into the existing `PreferenceSetup.vue` onboarding step
  (alongside Course/Year Level), not a new dedicated step — see
  [chosen mockup](../mockups/2026-08-07-tutee-subject-selection.html) and rejected alternative
  (a standalone step mirroring the Tutor flow) captured there.
- Tutor subject-selection is unchanged structurally (`TutorSubjectSetup.vue` already exists) —
  it shares `SubjectTaxonomyPicker` with the new Tutee usage, so the description display is one
  component change that benefits both roles.
- `Subjects` gets a new `description` field, editable via the existing admin catalog screen
  (`AdminCourseCatalog.vue`), not seed-only — so subjects added after this ships aren't stuck
  without a description.
- Tutee subject picks are persisted via the existing `Preference` model (`user` OneToOne →
  `subjects` M2M, `backend/studybuddy/models.py:1041`), already used by the CBF recommender and
  currently populated at booking time — onboarding becomes a new write path into it via
  `get_or_create`, not a new table.

**Commission disclosure:** see [ADR-0010](../adr/0010-persisted-commission-disclosure-acceptance.md)
for the full decision record, including the deliberate deviation from ADR-0007's UI-only pattern.
Summary: new `commission_terms_accepted_at` field on `Tutor`, disclosed inline at the `hourly_rate`
field in `TutorPreferenceSetup.vue`, and enforced retroactively for already-onboarded tutors via
the router guard (same mechanism as the existing profile-completion/onboarding-step redirects).

## Steps

1. **Backend — `Subjects.description`**: add migration, add field to serializer(s) used by
   `AdminCourseCatalog` and subject-listing endpoints.
2. **Frontend — `AdminCourseCatalog.vue`**: add description form field (textarea), alongside
   existing `subject_name`/`department`/`category`/`keywords`.
3. **Frontend — `SubjectTaxonomyPicker.vue`**: render `subject.description` under the subject name
   in both the search-dropdown row and the category drill-pane chip/card view.
4. **Data — seed content**: write description text for all currently-seeded `Subjects` rows (via
   `seed_data.py` or a one-time data migration/fixture — decide format when implementing).
5. **Frontend — `PreferenceSetup.vue`**: embed `SubjectTaxonomyPicker` alongside the existing
   Course/Year Level fields; submit selected subject codes into `Preference` via
   `get_or_create(user=profile)`.
6. **Backend — `Tutor.commission_terms_accepted_at`**: add migration (nullable `DateTimeField`).
7. **Frontend — `TutorPreferenceSetup.vue`**: add disclosure line + checkbox next to `hourly_rate`;
   block "Continue" until checked; on submit, set `commission_terms_accepted_at` server-side.
8. **Frontend — `src/router/index.js`**: extend the guard so any Tutor-role route checks
   `commission_terms_accepted_at`; if null, force-redirect to a one-time acceptance screen (reusing
   the disclosure UI from step 7) before any other Tutor route loads. This retroactively forces
   acceptance for already-onboarded (including seeded) tutors — see ADR-0010.
9. Update `docs/adr/` cross-reference in ADR-0007 if useful (optional — ADR-0010 already links back).

## Risks

- `SubjectTaxonomyPicker.vue` is shared between two now-divergent contexts (Tutee preference
  picking vs Tutor "what I teach" picking) — verify the description copy reads sensibly in both
  ("subjects you need help in" vs "subjects you teach") without needing separate description text.
- Retroactive router-guard enforcement (step 8) is new gate surface — confirm it doesn't loop with
  the existing profile-completion/onboarding-step redirects for edge cases (e.g. a Tutor who is
  simultaneously mid-onboarding and missing the commission acceptance).
- Backfilling description text for all seeded subjects (step 4) is a content task with no
  authoritative source identified yet — needs an owner/process decided at implementation time.

## Checks to run

- `npm run lint`
- `npm run build`
- `python manage.py test` (add coverage for: `Preference` write on `PreferenceSetup` submit,
  router-guard redirect when `commission_terms_accepted_at` is null, migration safety on existing
  seeded `Tutor`/`Subjects` rows)
