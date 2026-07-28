---
title: SuperAdmin role + per-institution admin scoping
date: 2026-06-08
status: Done
spec:
---

# SuperAdmin role + per-institution admin scoping

## Status & Progress Summary

**Status (2026-07-17): Done.** This plan predates the living-plan convention and never had a
tracked summary. Verified against the codebase during a plan-vs-code implementation audit:
`SuperAdmin` is a live role in `ROLE_CHOICES` (`models.py`), `IsSuperAdminUser` permission class
and `SuperAdminInstitutionPerformanceView` endpoint both exist, `login_view()` has the
domain-exemption check for `SuperAdmin`, and `src/router/index.js` guards SuperAdmin routes with
`role: ['Admin', 'SuperAdmin']`. Frontmatter status was never flipped from Approved.

## Goal

Split the current single global `Admin` role into (a) admins scoped to their own
institution and (b) a new `SuperAdmin` role that adds/removes institutions and views
cross-institution performance, with cross-institution login blocked.

## Approach

Current state: `UserProfile.ROLE_CHOICES` has only `Tutee`/`Tutor`/`Admin`
(`backend/studybuddy/models.py` ~line 88); `PartnerInstitution` already exists
(~line 36) with a `UserProfile.institution` FK; `permissions.py` has a single
`IsAdminUser` checking `role == 'Admin' or is_staff or is_superuser` with **no**
institution scoping; `admin_views.py` mixes institution-CRUD with general admin
endpoints under that one permission class; `login_view()` (`views.py` ~line 904)
matches users to institutions by email domain and exempts `role == 'Admin'` from that
check via `is_domain_exempt`.

Decision: `SuperAdmin` is a brand-new distinct role value (not a flag/tier on `Admin`)
— this matches the existing role-based pattern and keeps permission checks to a single
axis (`role ==`) instead of adding a second one to get wrong.

## Steps

1. Backend: add `'SuperAdmin'` to `ROLE_CHOICES` + migration.
2. Backend: add an `IsSuperAdminUser` permission class in `permissions.py`, parallel to
   the existing `IsAdminUser` pattern (also honoring `is_superuser`).
3. Backend: audit `admin_views.py` endpoint by endpoint — split into "institution admin"
   (must filter querysets by `request.user.userprofile.institution`) vs.
   "superadmin-only" (institution add/remove, cross-institution analytics).
4. Backend: add per-institution performance endpoint(s) — aggregate counts (tutors,
   tutees, sessions, revenue, ratings) grouped by `PartnerInstitution`, gated to
   `SuperAdmin`.
5. Frontend: add a SuperAdmin route group with `meta: { role: 'SuperAdmin' }` guards in
   `src/router/index.js`, mirroring the existing Admin route pattern.
6. Frontend: build the SuperAdmin dashboard — institution list/add/remove (moved out of
   the existing admin dashboard) + per-institution performance views.
7. Frontend: remove the institution add/drop UI from the current institutional-admin
   dashboard.
8. Verify the cross-login guarantee end to end: decide whether `SuperAdmin` stays
   domain-exempt (yes, like current `Admin`s) and whether per-institution `Admin`s
   should now be domain-bound to their own institution — this is the actual mechanism
   that prevents "logging into a different institution".

## Risks

- Migration path for existing `Admin` accounts — decide whether any become `SuperAdmin`,
  or SuperAdmin accounts are created fresh.
- Scoping every `admin_views.py` query by institution is the highest-effort and most
  error-prone part; each endpoint needs individual review, not a blanket filter.
- The domain-exemption logic in `login_view()` is the actual cross-login safeguard —
  changing who is exempt has direct security implications and needs care.

## Checks to run

- Create one `SuperAdmin` and two institution-scoped `Admin`s; confirm each `Admin`
  sees only their institution's data.
- Confirm the `SuperAdmin` sees all institutions and can add/remove them.
- Confirm a Tutor/Tutee registered under institution A's email domain cannot
  authenticate as a member of institution B.
- `npm run lint` and `npm run build` pass; backend test run
  (`backend/studybuddy/tests.py`) passes.

## Changelog

- 2026-06-08: Plan written and approved.
- 2026-07-17: Verified implemented during a plan-vs-code implementation audit; frontmatter
  status corrected from Approved to Done. Added this Status & Progress Summary/Changelog
  retroactively per the living-plan convention.
