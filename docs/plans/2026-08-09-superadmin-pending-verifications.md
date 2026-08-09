---
title: Surface pending verifications in the SuperAdmin review queue
date: 2026-08-09
status: Done
spec:
---

# Surface pending verifications in the SuperAdmin review queue

## Status & Progress Summary

**Done** — all four steps implemented and checked.

| Step | State |
| --- | --- |
| 1. Backend aggregator | Done |
| 2. Dashboard item meta + routing | Done |
| 3. Applications screen query seeding | Done |
| 4. Tests | Done |

Deviation from the original approach: four item types (`tutor_application`, `tutor_renewal`,
`tutee_application`, `tutee_renewal`) instead of two. Application and renewal primary keys are
independent sequences, so sharing a type per role could produce duplicate `(type, id)` pairs and
therefore duplicate Vue list keys.

## Goal

A tutee whose application sits at `pending` shows "Pending Review" on their own status screen, but a
SuperAdmin sees no signal anywhere on the dashboard. Make pending tutee/tutor verifications appear in
the "Needs SuperAdmin review" panel, deep-linking to the Applications screen where they are actually
actioned.

## Approach

`AdminPendingActionsView` (`backend/studybuddy/admin_views.py`) builds its item list from exactly
three sources — institution requests, institution activations, and domain exemptions. Applications
were never included, so `/admin/pending-actions/` cannot report them regardless of status. The fix is
additive on the same aggregator rather than a new endpoint, so the dashboard count and list stay a
single source of truth.

Key decisions:

- **Include renewals, not just first-time applications.** A pending `TutorDocumentRenewalReview` /
  `TuteeDocumentRenewalReview` is the same unit of admin work and lives on the same screen; leaving
  them out would reproduce the exact gap being fixed. They share the item `type` per role and are
  distinguished in the `meta` string.
- **Two item types, not four** (`tutor_application`, `tutee_application`). The dashboard only needs to
  know which tab of the Applications screen to open.
- **No inline approve action.** Every existing pending item is approved with one click, but a
  verification requires reading uploaded documents. These items get a `Review` button that routes to
  `/admin/tutor-applications?role=<role>&status=pending` instead of calling a mutation.
- Deep-linking requires `AdminTutorApplications.vue` to seed its `filters` from the route query; it
  currently hardcodes `role: 'tutor', status: 'pending'`.

## Steps

1. `admin_views.py` — in `AdminPendingActionsView.get()`, append items for pending `TutorApplication`
   and `TuteeApplication` rows (`application_status='pending'`), and for pending
   `TutorDocumentRenewalReview` / `TuteeDocumentRenewalReview` rows (`status='pending'`), using
   `submitted_at` as `created_at`.
2. `SuperAdminDashboard.vue` — add the two types to `getPendingMeta()` with a `Review` action, and
   branch `handlePendingAction()` to `router.push()` for them.
3. `AdminTutorApplications.vue` — initialize `filters.role` / `filters.status` from `route.query`,
   falling back to today's defaults.
4. `tests.py` — extend the pending-actions test to cover a pending tutee application appearing in the
   payload.

## Risks

- The existing test asserts an exact `count` of 3 and an exact type set; it must be updated in the
  same change or it fails.
- `select_related('profile__user')` on the new queries to avoid an N+1 while building the `meta`
  string.
- The `domain_exemption` branch already iterates every completed profile; adding four more queries
  keeps this endpoint modest but it is now the heaviest part of the dashboard load.
- Institution-scoped Admins share the Applications route but not this dashboard, so no permission
  change is needed.

## Checks to run

- `python manage.py test studybuddy.tests.SuperAdminApiTests` — pending-actions tests pass.
- `npm run lint` — clean.
- `npm run build` — succeeds.

## Changelog

- **2026-08-09** — Plan created from the investigation into why a tutee's "Pending Review" status
  never reached the SuperAdmin dashboard. Root cause: `AdminPendingActionsView` aggregates only
  institution requests, institution activations, and domain exemptions.
- **2026-08-09** — Implemented all four steps. Split the item types four ways instead of two to keep
  `(type, id)` unique across applications and renewals. Checks: the two pending-actions tests pass
  (`--keepdb`; the shared test database sits behind a Supabase pooler whose session blocks a clean
  drop, and a separate `test_analytics_*` test errors on a leftover `PaymentMethod` row under
  `--keepdb` — pre-existing, unrelated). `npm run build` succeeds; `npm run lint` reports 4
  pre-existing `no-undef` errors in `make_algo_pptx.cjs`/`.js`, none in the files touched here.
