---
title: Admin role consolidation & SuperAdmin user analytics
date: 2026-07-12
status: In Progress
summary: Remove the institution-scoped Admin role (merge into SuperAdmin), make the subject/course catalog global, and add a per-tutor/per-tutee stats drill-down for SuperAdmin.
spec: ../specs/2026-07-12-admin-role-consolidation-design.md
---

# Admin role consolidation & SuperAdmin user analytics

## Status & Progress Summary

**Status:** In Progress — ticket 1 (Admin-to-SuperAdmin conversion, migration 0072, permission
tightening) shipped and committed on `feat/admin-role-consolidation`; tickets 2-8 hand off to the
Codex CLI per user direction. Frontier: tickets 2, 3, 4, 7. Run summary:
`docs/session-summaries/2026-07-13-admin-role-consolidation-run-summary.md`.

## Goal

Remove the institution-scoped `Admin` role in favor of a single `SuperAdmin` tier (panel feedback),
collapse the per-institution subject/course catalog into one global pool, and add a per-tutor/
per-tutee analytics drill-down to the SuperAdmin user list — addressing the panel's admin-analytics
feedback.

## Approach

This is a real-shared-database migration plus a UI/permissions consolidation plus one new read
endpoint. Order matters: land the backend role/permission/schema changes and their data migration
first (with tests), then the frontend consolidation that depends on permissions being final, then
the new analytics endpoint + slide-over panel last, since it's additive and independent of the
removal work. Full rationale and every decision are recorded in the spec
(`docs/specs/2026-07-12-admin-role-consolidation-design.md`); this file tracks execution status only.

## Steps

1. **Data migration: convert `Admin` → `SuperAdmin`.** Write a Django migration that converts every
   `UserProfile` with the institution-scoped admin role to `SuperAdmin`, then removes that role from
   the field's valid choices.
2. **Backend: tighten permissions.** Update the admin permission classes and every view that
   currently accepts either the institution-scoped role or `SuperAdmin` to require `SuperAdmin`
   only. Remove the institution-scoping helpers/branches in the admin view layer (queryset/target
   filtering) since they're now dead code.
3. **Backend: delete the admin-account-request workflow.** Remove its model, endpoints, and any
   frontend surface that references it. Leave the institution-request workflow untouched.
4. **Backend: globalize the subject/course catalog.** Migration to drop the per-institution
   subject-ownership field and the per-institution course-catalog table entirely. Rework the
   catalog-management views into a single global subject/course CRUD surface with no institution
   selector.
5. **Backend tests.** Cover permission tightening, the role-conversion migration, and the
   globalized catalog endpoint per the spec's Testing Decisions — one `APITestCase` class per seam.
6. **Frontend: consolidate admin views.** Delete the institution-scoped admin views; move any
   functionality they had that SuperAdmin's equivalents don't yet cover. Add redirects from the old
   institution-scoped routes to their SuperAdmin equivalents.
7. **Demo data: update `reset_demo_data.py`.** Stop seeding a per-institution Admin account; only
   the SuperAdmin login is seeded/preserved across resets.
8. **Backend: new per-user analytics endpoint.** Add the read-only endpoint returning the tutor or
   tutee all-time stats payload defined in the spec, plus its `APITestCase` coverage.
9. **Frontend: slide-over drill-down panel.** Build the panel component per
   `docs/mockups/2026-07-12-superadmin-user-drilldown.html`, wired to open from a row click in the
   SuperAdmin user list and call the new endpoint.

## Risks

- **Real shared database.** The role-conversion migration runs against production data — verify it
  on a copy/backup before applying, and confirm no code path outside the admin views still checks
  for the institution-scoped role by string comparison (would silently break instead of erroring).
- **Institution matching regression.** Globalizing the subject catalog must not touch
  `UserProfile.institution`-based tutor/tutee matching (`docs/specs/2026-06-26-institution-scoped-matching-design.md`)
  — that filter is unrelated and must keep working exactly as today.
- **Frontend consolidation gaps.** The institution-scoped admin views may have small feature deltas
  from their SuperAdmin counterparts beyond institution-scoping (they were being aligned in
  `docs/specs/2026-06-21-admin-dashboard-redesign-design.md`, not necessarily finished) — diff them
  carefully before deleting, not just assume parity.
- **Stats endpoint performance.** The per-user drill-down aggregates across Bookings/Payments/
  ratings on every open; fine for v1 given no period filter, but watch for slow queries on users
  with very large session counts.

## Checks to run

- `python manage.py test` (full suite, focused first on the new/updated test classes) — all
  passing, no regressions beyond the pre-existing baseline.
- `npm run lint` and `npm run build` — passing.
- Manual verification in the browser: confirm a former Admin account now lands in the SuperAdmin
  area post-migration; confirm the old institution-scoped admin routes redirect; confirm the global
  subject/course CRUD screen has no institution picker; confirm `reset_demo_data.py` no longer seeds
  an Admin login; open the drill-down panel for a tutor and a tutee and compare against the mockup.

## Changelog

- 2026-07-12: Plan created and Approved after a grilling session + confirmed `ui-preview` mockup
  (spec at `docs/specs/2026-07-12-admin-role-consolidation-design.md`). Not yet implemented.
- 2026-07-13: Status moved to In Progress — tickets split into `docs/tickets.md` (mirrored as
  GitHub Issues #1-8 on the fork) and an `/orchestrate` run started on branch
  `feat/admin-role-consolidation`.
- 2026-07-13 (later): Ticket 1 shipped — migration 0072 converts Admin rows to SuperAdmin,
  `IsAdminUser` deleted, 17 admin views re-gated, role checks tightened; full suite verified
  against the pre-existing baseline (289 tests, no new failures). Orchestrate run ended early by
  user direction; tickets 2-8 hand off to Codex. Run summary:
  `docs/session-summaries/2026-07-13-admin-role-consolidation-run-summary.md`.
