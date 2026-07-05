---
title: Institution course catalog
date: 2026-07-05
status: Done
spec: ../specs/2026-07-05-institution-course-catalog-design.md
---

# Institution course catalog

## Status & Progress Summary

**Status:** Done - implemented and verified with focused backend tests, frontend lint, and frontend
build. Full backend suite still reports the existing broader baseline failures; the new catalog
test class passes.

## Goal

Let each Partner Institution curate its own course-subject catalog in Studybuddy, including
institution-private Custom Subjects, without changing the global catalog used by other
institutions.

## Approach

Model the feature in two layers: keep `Subjects` as the global master list with an optional
`owning_institution` for Custom Subjects, then add an `InstitutionCourseCatalog` join that records
which Course/Subject pairings a given institution recognizes. Ship the work in thin end-to-end
slices so privacy rules land first, then catalog curation, then SuperAdmin visibility, then demo
data and glossary cleanup.

## Steps

1. Add institution ownership to `Subjects`, expose admin creation of Custom Subjects, and fix
   subject-list visibility so private subjects only appear to their owning institution.
2. Add `InstitutionCourseCatalog` plus admin list/create/delete APIs and tests for institution
   scoping, duplicate prevention, and private-subject ownership guards.
3. Build the Admin Course Catalog screen, route, sidebar entry, and store wiring so institution
   admins can curate subjects under a selected course end-to-end.
4. Extend the same flow for SuperAdmin with an `institution_id` selector/filter while preserving
   normal Admin scoping.
5. Update seed/reset demo data so CPU and North University have visibly different Institution
   Course Catalogs, including one seeded Custom Subject, and refine glossary entries to match the
   final model.

## Risks

- `SubjectListView` is used platform-wide today, so the privacy fix must not accidentally hide all
  subjects for users with missing or unexpected institution data.
- The repo currently treats `Subjects.category` as a loose course hint in some places; the new
  curation model must not silently depend on or overwrite that legacy meaning.
- Admin and SuperAdmin scoping needs careful coverage so one institution cannot curate another
  institution's Custom Subjects or catalog entries.
- Seed/demo data can make the feature look broken if the two institutions end up with nearly
  identical catalogs after reset.

## Checks to run

- `cd backend && python manage.py test studybuddy.tests`
  Passing result: the institution catalog and subject-visibility tests pass with no new regressions.
- `npm run lint`
  Passing result: frontend/admin screen and store changes lint cleanly.
- `npm run build`
  Passing result: the Admin Course Catalog route builds successfully in production mode.
- Manual verification in local dev:
  Passing result: an Admin can add/remove catalog entries only for their own institution, create a
  Custom Subject, and a user from another institution never sees that Custom Subject in subject
  dropdowns.

## Changelog

- **2026-07-05** - Implemented institution-owned Custom Subjects, Institution Course Catalog
  model/API, Admin Course Catalog UI, SuperAdmin institution selector, demo-data seeding, and
  glossary updates.
