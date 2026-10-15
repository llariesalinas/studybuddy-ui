---
title: Subject category integrity
date: 2026-10-15
status: Done
spec: 2026-08-21-subject-category-storage.md
---

# Subject category integrity

## Status & Progress Summary

Implemented and tested locally on 2026-10-16. Imported from pr139-review-plans.patch and refined
before implementation. Changes are uncommitted and ready for review.

## Goal

Resolve the confirmed PR #139 review findings for subject category integrity.

## Approach

Apply the reviewed fixes with regression coverage and preserve established behavior outside the
reported problems. Record implementation refinements and known limitations below.

## Completed steps

1. System-category rename attempts return 400; display-order edits remain allowed. Fallback
   lookup and CBF exclusion use is_system rather than the category name.
2. Migration 0087 merges duplicate system categories and repoints subjects. Migration 0088
   enforces a single system category with a conditional unique constraint. The index is in a
   separate transaction because PostgreSQL rejects index creation with pending FK trigger events.
3. The authenticated read-only subject-categories endpoint returns all non-system category names
   in server order, including empty categories. Tutor proposals use this list and reject system
   categories on the backend.
4. Review-panel edit saves refresh unknown categories after updating local subjects.
5. Migration 0085 contains frozen taxonomy seed values while retaining the model field callables.
6. Admin category GET annotates subject counts in one query with explicit display ordering.
   Single-object serialization retains its count fallback.
7. Tests cover rename protection, reordering, force-renamed fallback lookup and CBF exclusion,
   empty categories, proposal rejection, constant query counts, and migration of duplicate rows.

## Risks

- Includes migrations 0087 and 0088. Both were exercised against fresh local PostgreSQL and
  the upgrade regression fixture. No remote application database was migrated.
- The category list is global, matching the existing SubjectCategory table and admin catalog.

## Verification

- npm run lint and npm run build pass.
- Focused frontend regression files: 29/29 pass.
- Focused backend classes plus migration regression: 95/95 pass on isolated local PostgreSQL.
- Full frontend: 249 pass, 1 skip, 9 existing failures. Original commit: 232 pass, 1 skip,
  the same 9 failures.
- Full backend: 555 pass, 1 existing chat grace-cutoff failure. Original commit: 540 pass,
  the same failure. No new failures.
- makemigrations --check --dry-run reports no changes.
- Manual two-browser review is left for the user; no production or remote database changes.

See [completion and manual checks](../session-summaries/2026-10-16-pr139-review-fixes.md).
