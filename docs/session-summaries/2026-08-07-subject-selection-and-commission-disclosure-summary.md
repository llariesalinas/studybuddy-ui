# Subject Selection Onboarding + Commission Disclosure — Session Summary

**Date:** 2026-08-07
**Plan:** [2026-08-07-subject-selection-and-commission-disclosure.md](../plans/2026-08-07-subject-selection-and-commission-disclosure.md)
**ADR:** [0010-persisted-commission-disclosure-acceptance.md](../adr/0010-persisted-commission-disclosure-acceptance.md)
**Branch:** `feat/subject-descriptions-commission-disclosure` (off `feat/subjects-reseed`)

## What shipped

**Subject descriptions**
- `Subjects.description` field (migration `0080_subjects_description_and_more`).
- Editable via the existing admin catalog form (`AdminCourseCatalog.vue`), same pattern as
  `subject_name`/`category`/`keywords`.
- Displayed in `SubjectTaxonomyPicker.vue` — under the subject name in search-dropdown rows, and
  as a `title` tooltip on category-drilldown chips (adapted from the planned mockup's card layout
  to fit the picker's actual compact-chip UI).
- All 121 seeded subjects backfilled with real one-line descriptions
  (`backend/studybuddy/subject_descriptions.py`), wired into `seed_data.py`.

**Tutee subject-selection onboarding**
- Discovered mid-implementation that `PreferenceSetup.vue` already has a subject-selection card
  (Card 3) using `SubjectTaxonomyPicker`, persisting to `Preference` via `POST preferences/`. This
  predated the grilling session (already on `feat/subjects-reseed`) and made plan steps 5-6 no-ops
  — the description work above covers this screen automatically since it shares the same picker.

**Commission disclosure**
- `Tutor.commission_terms_accepted_at` field (same migration).
- Inline disclosure checkbox next to `hourly_rate` in `TutorPreferenceSetup.vue` (Proactive Gate —
  disables "Complete Profile" until checked).
- Backend `tutor_setup` view rejects (400) submission without acknowledgement (Reactive Gate,
  authoritative per the codebase's established gate pattern).
- New `accept-commission-terms` endpoint + `TutorCommissionTermsAcceptance.vue` screen, gated in
  by a new router-guard branch: any already-onboarded Tutor route load with
  `commission_terms_accepted_at IS NULL` force-redirects there. This retroactively forces
  acceptance on existing/seeded tutors, per ADR-0010's deliberate deviation from ADR-0007's
  UI-only pattern.
- `PLATFORM_COMMISSION_RATE_PERCENT` added to `src/config.js` rather than hardcoding "10%".

## Deviations from the plan

None in substance. Steps 5 and 6 turned out to be already implemented (see above) rather than
needing new code — noted in the plan's Changelog rather than silently dropped.

## Checks run

- `python manage.py test studybuddy.tests.CommissionTermsDisclosureTests studybuddy.tests.GlobalSubjectCatalogTests` — 12/12 new tests pass.
- `python manage.py test` (full suite, 378 tests) — 7 failures, all confirmed pre-existing and
  unrelated (dev-tools flags, avatar upload, PayMongo cash-out amounts) by reproducing them
  identically via `git stash` against the unmodified branch.
- `npm run lint` — clean (2 pre-existing, unrelated errors in `make_algo_pptx.cjs/js`).
- `npm run build` — clean.
- `npm run test` (vitest) — 93/93 pass.
- Two-axis `/code-review` (Standards + Spec, parallel sub-agents) against fixed point `7b2d8e2`:
  - **Standards:** 1 hard violation (stray emoji in a new router-guard comment) — fixed. A few
    judgement-call smells noted (commission-rate constant duplicated frontend/backend behind a
    "keep in sync" comment; near-duplicate disclosure copy in two Vue files) — left as-is, both
    low-risk and consistent with existing patterns in the codebase.
  - **Spec:** clean. All plan/ADR requirements verified implemented as specified, including the
    Proactive+Reactive gate pair, retroactive (not grandfathered) enforcement for existing tutors,
    full 121/121 subject description coverage, and the admin-catalog-to-picker wiring end to end.
    One gap noted: no frontend test for the router-guard branch — consistent with the rest of
    `src/router/index.js`, which has zero pre-existing test coverage of any guard branch.

## Commits

- `0a6e3d3` — feat: subject descriptions and tutor commission disclosure
- follow-up — fix: drop emoji from router guard comment per no-emoji rule
