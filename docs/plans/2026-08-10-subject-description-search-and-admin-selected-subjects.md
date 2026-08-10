---
title: Subject description search and admin selected subjects
date: 2026-08-10
status: Done
summary: Make subject descriptions searchable in both pickers with two-tier ordering, show a tutor's catalog picks alongside their proposals in the admin review drawer, and repoint the admin Description field at the catalog so approved proposals become searchable.
spec: ../mockups/2026-08-10-subject-description-search.html
---

# Subject description search and admin selected subjects

Mockups: [subject description search](../mockups/2026-08-10-subject-description-search.html) ·
[admin selected subjects](../mockups/2026-08-10-admin-selected-subjects.html)

## Status & Progress Summary

**2026-08-10 — Done.** Grilled through eight decisions with `ui-preview` (four mockup rounds), then
implemented in a single pass. Two independent halves. The grill turned up a defect neither half was
originally about: `Subjects.description` is never populated for tutor proposals, so the search being
built here would have been permanently blind to every tutor-originated subject. Fixed as step 6.

All nine steps shipped as planned, with no deviation from the approved design. The API-shape risk
was real: step 7 splits the overloaded `description` key on `proposed_subjects` into
`catalog_description` and `tutor_note`, and `AdminTutorApplications.vue` was the only consumer, so
both sides landed together. The pre-existing backend test asserting the old wrong-field write was
rewritten rather than extended, as the plan anticipated. `npm run test` 139/139 (was 136, +3 net
from the new search cases), 9/9 in `AdminProposedSubjectReviewTests`, `npm run build` succeeds.
`npm run lint` reports 4 pre-existing `no-undef` errors in `make_algo_pptx.cjs`/`.js`, untouched by
this work. The manual checks in "Checks to run" have not been performed — see the summary.
[Summary](../session-summaries/2026-08-10-subject-description-search-and-admin-selected-subjects-summary.md).

## Goal

Subject descriptions are written, stored, and displayed, but they do not participate in search — a
tutor searching "derivatives" gets no results even though Calculus's description contains the word,
and is nudged toward proposing a duplicate. Separately, an admin reviewing a tutor's proposed
subjects cannot see which catalog subjects that tutor already selected, which is the context the
proposal decision depends on.

## Approach

Two halves, no dependency between them.

**Search.** `searchSubjects()` in `src/components/subjectPicker.shared.js` is a pure function shared
by `SubjectTaxonomyPicker` (tutor registration) and `SubjectPickerModal` (tutee Find Tutors /
Initial Booking). Adding `description` to its matched fields covers both surfaces in one edit. No API
work: the pickers load the whole catalog once via `/subjects/?catalog_scope=all` and filter
client-side, and `description` is already in `SubjectSerializer`. `useSubjectCatalog.js` (a third,
separate filter used by `TuteeProfile.vue`) is deliberately left alone — different component,
different UI, no description row to justify a match badge.

Broadening the match without ranking would make search worse: searching "data" would bury the
subjects literally named "Data …" beneath rows that merely mention the word. So results are
partitioned into two tiers — direct name/category matches first, keyword/description-only matches
after, catalog order preserved within each. A partition, not a scoring system; there is nothing to
tune. The existing `via "…"` badge already marks the second tier, so no labelled break is drawn, and
`matchedViaKeyword` is renamed `matchedViaHint` to stop the flag lying about why a row matched.

`SubjectPickerModal` rows currently render name + category only. A description-only match there
would show a badge asserting a reason the row never displays, so those rows gain one clamped
description line. Term highlighting inside the description was considered and deferred: it needs a
split-into-spans helper plus its own edge cases (casing, repeats, and the clamp cutting off the very
word that matched, which silently returns you to an unexplained badge).

**Admin.** Every subject a tutor holds is a `TutorSubjects` row; catalog picks have
`subject.status = 'approved'` and proposals have `'pending'`. The drawer's existing block renders the
pending ones, so the selected ones are exactly the complement — a new `selected_subjects` field on
`TutorApplicationSerializer`, rendered read-only below the proposal queue behind the same visibility
gate (tutor role, initial review), with an explicit empty state rather than a hidden section.

The third piece is a naming collision the grill exposed. Two fields are both called "description":
`Subjects.description` is the global catalog copy and the field this plan's search reads;
`TutorSubjects.description` is one tutor's note about their own expertise. `propose_tutor_subject`
(`views.py:4307`) creates the `Subjects` row without a description, and the admin edit form labelled
"Description" writes the *tutor's* note (`admin_views.py:1547`). Seeded subjects all carry catalog
descriptions (`subject_descriptions.py` → `seed_data.py`); approved proposals never do. Left alone,
the catalog splits into a searchable half and an unsearchable half, and the split grows with every
approval. The form is therefore repointed at `Subjects.description`, with the tutor's note shown
read-only above it as the evidence being judged and prefilling the field when the catalog copy is
blank.

Copying the note into the catalog field automatically on approve was rejected: notes are
first-person and about the tutor, and would surface as shared catalog copy under a subject every
user sees.

## Steps

1. `src/components/subjectPicker.shared.js` — `searchSubjects()` matches `description`; rename
   `matchedViaKeyword` → `matchedViaHint` (set when the query hit only keywords or description);
   partition results into direct matches then hint matches, stable within each tier.
2. `src/components/subjectPicker.shared.test.js` — update the existing assertions to the renamed
   flag (this file asserts the old name; it changes, it does not merely gain cases) and add coverage
   for description-only matching and tier ordering.
3. `src/components/SubjectTaxonomyPicker.vue` — consume the renamed flag. No visual change.
4. `src/components/SubjectPickerModal.vue` — consume the renamed flag and add a single clamped
   description line to result rows.
5. `backend/studybuddy/serializers.py` — add `selected_subjects` to `TutorApplicationSerializer`
   (the applicant's `TutorSubjects` rows whose subject status is `approved`), returning subject code,
   name, and category.
6. `backend/studybuddy/admin_views.py` — in `AdminTutorProposedSubjectDetailView.patch`, the
   `update` action writes `description` to `Subjects.description` instead of
   `TutorSubjects.description`, and returns the tutor's note alongside so the form can render it.
7. `backend/studybuddy/serializers.py` — `get_proposed_subjects` returns both fields under distinct
   names (catalog description and tutor note) rather than one overloaded `description` key.
8. `src/views/AdminTutorApplications.vue` — render the read-only "Selected from catalog" section
   below the proposal block with the "No catalog subjects selected" empty state, gated identically to
   `proposedSubjects`; update the edit form to show the tutor's note read-only above an editable
   catalog description that prefills from the note when blank.
9. `backend/studybuddy/tests.py` — cover `selected_subjects` (including the empty case) and the
   repointed patch action.

## Risks

- **Renaming `matchedViaKeyword` is a cross-file rename.** Both picker components and the shared
  test file reference it. A missed reference fails silently as a badge that never renders, not as an
  error — grep for the old name before calling step 4 done.
- **Step 6 removes a capability.** Admins can no longer edit a tutor's own note through this form.
  Intended, but it is a removal, not a relabel, and worth confirming visually once it ships.
- **Steps 6 and 7 change the shape of an existing API response.** `AdminTutorApplications.vue` reads
  `description` from `proposed_subjects` today; splitting the key breaks that read unless both sides
  land together.
- **Search quality is unmeasured.** Descriptions are prose, so common words ("data", "analysis") will
  pull long tails. The two-tier ordering contains this, but if a query returns dozens of hint
  matches the tier is only as useful as the badge is visible — worth a look with real seeded data.
- **The clamp and the match can disagree.** A description-only match whose word sits past the
  single-line clamp shows a badge with the reason cut off. Accepted for now; it is the same failure
  the deferred highlighting would have had.

## Checks to run

- `npx vitest run src/components/subjectPicker.shared.test.js` — the renamed flag and new
  description/ordering cases pass.
- `npm run test` — full frontend suite green (baseline is 136/136).
- `npm run lint` — oxlint + ESLint clean.
- `npm run build` — production build succeeds.
- `python manage.py test studybuddy` — backend suite; note the remote test DB has historically needed
  chunked runs and carries pre-existing failures, so compare against a stashed tree before blaming
  this change.
- Manual: search "derivatives" in tutor registration and in the tutee picker; open an admin review
  drawer for a tutor with both catalog picks and proposals, and one with proposals only.

## Changelog

- **2026-08-10** — Plan created at status Approved after an eight-decision `ui-preview` grill.
  Decisions locked: description joins the matched fields (not a tutor-supplied keywords field, not a
  display-only change); applied to both pickers via the shared function, `useSubjectCatalog.js`
  untouched; one renamed badge plus a description line on the tutee rows, highlighting deferred;
  two-tier ordering without a labelled break; admin selected subjects as a read-only section below
  the proposal queue; the admin Description field repointed at `Subjects.description` with the tutor
  note read-only and prefilling; same visibility gate as proposed subjects with an explicit empty
  state; single-pass execution rather than phased. Mockups promoted to
  `docs/mockups/2026-08-10-subject-description-search.html` and
  `docs/mockups/2026-08-10-admin-selected-subjects.html`. No code written.
- **2026-08-10** — Implemented all nine steps in one pass; status Approved -> Done. No design
  deviations. `searchSubjects()` now matches `description` and returns direct matches ahead of hint
  matches (a two-array partition, catalog order preserved within each tier);
  `matchedViaKeyword` -> `matchedViaHint` across both picker components with no stale references
  left. `SubjectPickerModal` rows gained a `-webkit-line-clamp: 1` description line;
  `SubjectTaxonomyPicker` already rendered one, so it took only the flag rename. Backend:
  `selected_subjects` added to `TutorApplicationSerializer` (approved-status `TutorSubjects` rows,
  `select_related`), the overloaded `description` key on `proposed_subjects` split into
  `catalog_description` + `tutor_note`, and the admin `update` action repointed at
  `Subjects.description` with `update_fields` extended conditionally so an omitted key leaves
  existing catalog copy intact — covered by its own test. The admin form now shows the tutor's note
  read-only above an editable catalog description that prefills from the note when blank, and a
  read-only "Selected from catalog" chip list sits below the proposal queue behind a new shared
  `isInitialTutorReview` computed (extracted so both sections cannot drift apart), with a
  "No catalog subjects selected." empty state. Tests: one rewritten (it asserted the old wrong-field
  write), five added. Verified with `npx vitest run src/components/subjectPicker.shared.test.js`
  (13 passing), `npm run test` (139/139), `python manage.py test
  studybuddy.tests.AdminProposedSubjectReviewTests --keepdb` (9/9), and `npm run build`. The remote
  test DB needed `--keepdb` because a stale `test_postgres` was held open by another session. Manual
  verification of both pickers and the admin drawer is still outstanding.
