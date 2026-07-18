---
title: Tutor subject keyword search + onboarding back-navigation
date: 2026-07-18
status: Approved
summary: Add keyword-aware search to the subject picker and back buttons across tutor onboarding.
spec: ../mockups/2026-07-18-tutor-subject-search.html
---

# Tutor subject keyword search + onboarding back-navigation

<!-- LIVING SUMMARY: keep this section and the Changelog current on every edit -->
## Status & Progress Summary

**Status:** Approved — design fully settled via a `/grill-with-docs` session (domain-modeling +
two `ui-preview` rounds); implementation not started.

**Progress:** 0/8 steps done (see Steps below).

**Locked decisions:** dropdown-row search results with a "via keyword" badge (not flat chips or
grouped-by-category); Back + Continue side by side (not stacked or a text link); search is
client-side over the already-loaded `subjects` prop; `keywords` is a single comma-separated text
field seeded silently on the propose form and admin-editable from day one; capture of searched
text only happens if a proposal is actually submitted (no separate logging table); one-step-back
navigation only (rail steps stay non-interactive).

**Open items:** none — all open questions from the grilling session were resolved before this plan
was saved.

## Goal

Tutors currently browse the subject catalogue purely by clicking through category cards
(`SubjectTaxonomyPicker.vue`), with no way to search, and the catalogue itself has no concept of
synonyms/keywords, so a tutor searching "coding" won't find "Programming" and can't easily tell
whether their subject is simply missing. Add a keyword-aware search field to the shared subject
picker (used across tutor onboarding, FindTutors, InitialBooking, and PreferenceSetup), close the
loop back to the catalogue by seeding proposed-subject keywords from what tutors actually search
for, and fix the unrelated but blocking gap that the 3-step tutor onboarding flow currently has no
way to navigate backward at all.

## Approach

**Search & keywords**
- Add an admin-editable `keywords` field (single comma-separated text) to the `Subjects` model.
  Blank by default on all existing/newly-created subjects; nothing depends on it being filled in.
- Search runs client-side over the `subjects` prop already loaded into `SubjectTaxonomyPicker.vue`
  (no new network calls), matching `subject_name`, `category`, and `keywords` via case-insensitive
  substring, consistent with the existing admin-catalog search pattern.
- Results render as a dropdown row list — reusing the `.mini-input`/`.dropdown-row`/
  `.dropdown-preview` CSS classes already present but unused in `TutorSubjectSetup.vue` (leftover
  from an earlier attempt at this same feature). Keyword-only matches get a `via "search text"`
  badge; literal name/category matches don't. Selecting a row keeps the search text and results in
  place (existing `.selected` highlight), so a tutor can pick several matches from one search.
  Clearing the search box reverts to the existing category-card browsing UI, unchanged.
- Zero results: tutee-facing screens (FindTutors, InitialBooking, PreferenceSetup) show a plain
  "No matching subjects" — nothing is captured there, tutees aren't a source of catalogue truth.
  Tutor onboarding (`TutorSubjectSetup.vue`) additionally shows "Can't find it? Propose it →",
  which opens the existing propose-subject form pre-filled with the searched text as
  `subject_name`, and silently (no visible field) also seeds the new `keywords` value with it.
  Nothing is captured unless the tutor actually submits a proposal — no separate logging table.
- `AdminCourseCatalog.vue`'s own search filter is extended to also match `keywords`, for
  consistency with the tutor-facing search.
- `AdminTutorProposedSubjectDetailView` (currently read-only approve/reject on
  `Subjects(status='pending')`) gains an edit path so a superadmin can correct a pending proposal's
  `subject_name`, `category`, and `keywords` (all on `Subjects`) plus `description` (which lives on
  the `TutorSubjects` join row, not `Subjects`) before approving or rejecting. Scoped to that one
  pending proposal — not a duplicate of `AdminCourseCatalog`'s full CRUD.

**Back-navigation**
- All 3 onboarding screens (`TutorPreferenceSetup.vue`, `TutorSubjectSetup.vue`,
  `TutorVerificationSetup.vue`) are currently forward-only (`Continue` buttons only, no way back).
  Add a "← Back" outline pill next to `Continue` (side-by-side row) on Subjects (→ Preferences) and
  Verify (→ Subjects). One step back only — the rail-step indicators stay non-interactive.
- The router guard in `src/router/index.js` (~line 322-329) currently force-redirects any
  onboarding-route navigation to whichever step is "next incomplete," which would immediately
  bounce a Back click forward again. It needs to change from "always push to next incomplete step"
  to "allow navigating to any onboarding step at or behind the furthest completed step; only block
  skipping ahead." Each step already reloads its own data from the backend on mount, so revisiting
  a completed step is safe — no client-side state to lose.

**Design decisions locked in this session** (see linked mockup for the visual result):
- Dropdown-row search results, not flat chips or grouped-by-category.
- Back + Continue side by side, not stacked or a plain text link.

## Steps

1. **Backend — data model**
   - Migration: add `Subjects.keywords` (`CharField`/`TextField`, blank, default `''`).
   - `SubjectSerializer`: expose `keywords`.
   - `propose_tutor_subject`: accept optional `keywords` in the request body, store it on the
     created `Subjects` row.
   - `AdminTutorProposedSubjectDetailView.patch`: add an `action=update` path (or equivalent) that
     lets a superadmin edit `subject_name`/`category`/`keywords` on the `Subjects` row and
     `description` on the related `TutorSubjects` row, only while `status='pending'`.
2. **Backend — admin catalog**
   - `AdminCourseCatalog` create/update endpoints: accept `keywords`.
3. **Frontend — picker component**
   - `SubjectTaxonomyPicker.vue`: add search input above the category grid; client-side filter over
     `subject_name`/`category`/`keywords`; render matches as dropdown rows with the keyword-match
     badge; wire selection to existing `toggle()`/`modelValue` logic; empty-search reverts to
     category-card view.
   - Expose an optional slot/prop so only `TutorSubjectSetup.vue` renders the "propose it" zero-
     result CTA; the other 3 screens get the plain empty state.
4. **Frontend — propose flow**
   - `TutorSubjectSetup.vue`: wire the zero-result CTA to `openProposalForm`, pre-filling
     `proposal.subject_name` (and silently `proposal.keywords`, not rendered as a form field) from
     the search text; extend the `proposeTutorSubject` service call to send `keywords`.
5. **Frontend — admin catalog UI**
   - `AdminCourseCatalog.vue`: add a `keywords` input to the add/edit form; extend
     `filteredSubjects` to also match `keywords`.
6. **Frontend — admin proposal review UI**
   - `AdminTutorApplications.vue`: make each `proposed_subjects` row editable inline
     (subject_name, category, keywords, description) before approve/reject; call the new update
     endpoint.
7. **Frontend — back navigation**
   - `src/router/index.js`: relax the onboarding guard to permit revisiting completed steps while
     still blocking skip-ahead.
   - `TutorSubjectSetup.vue` and `TutorVerificationSetup.vue`: add the "← Back" outline pill beside
     `Continue`, matching the merged mockup layout.
8. **Docs**
   - Update `docs/architecture/booking-flow.md`-equivalent tutor-onboarding docs if any reference
     the picker's UI, since the CLAUDE.md convention is to keep architecture docs in sync with flow
     changes.

## Risks

- The router-guard relaxation is the riskiest single change — it's central auth/navigation logic
  touched by every tutor onboarding session. Must be verified to still block skipping ahead (e.g.
  a tutor with incomplete Preferences manually navigating to `/tutor-setup/verification`).
- `description` living on `TutorSubjects` while `subject_name`/`category`/`keywords` live on
  `Subjects` means the admin-review edit endpoint touches two models in one request — needs care
  to keep atomic (existing view already wraps in `@transaction.atomic`).
- Client-side substring search across `subject_name` + `category` + `keywords` on ~121+ subjects is
  cheap now, but if the catalogue grows substantially this may need revisiting (out of scope here).
- `SubjectTaxonomyPicker.vue` is shared across 4 screens — a regression here has a wide blast
  radius; each of the 4 call sites should be manually re-verified after the change, not just
  onboarding.

## Checks to run

- `npm run lint`
- `npm run build`
- `python manage.py test` (particularly any existing tests touching `SubjectListView`,
  `propose_tutor_subject`, `AdminTutorProposedSubjectDetailView`, and `GlobalSubjectCatalogTests`
  per recent commit history)
- Manual verification in-browser: search + select on all 4 `SubjectTaxonomyPicker` call sites;
  zero-result propose flow end-to-end (search → propose → admin review/edit → approve → subject
  appears in catalogue with seeded keywords); Back navigation on Subjects and Verify steps,
  including confirming the guard still blocks skipping ahead when preferences/subjects are
  incomplete.

## Changelog

- 2026-07-18 — Plan created and approved after a `/grill-with-docs` session covering the search
  feature, keyword data model, propose-flow integration, admin review scope, and (added mid-session)
  onboarding back-navigation. Two `ui-preview` rounds settled the search-results layout (dropdown
  rows) and the Back/Continue button placement (side by side); merged mockup saved to
  `docs/mockups/2026-07-18-tutor-subject-search.html`.
