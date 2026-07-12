# Admin Role Consolidation & SuperAdmin User Analytics — Design Spec

## Problem Statement

Panel review feedback on the platform identified two problems in the admin area:

1. The institution-scoped `Admin` role and the platform-wide `SuperAdmin` role overlap almost
   entirely — `Admin` is a strict subset of what `SuperAdmin` can already do (the same screens,
   just filtered to one institution), plus a request-only workflow to promote someone to `Admin`.
   Maintaining two parallel role tiers, two parallel sets of frontend views, and institution-scoping
   branches throughout the backend for a role that adds no real capability is unnecessary
   complexity with no corresponding benefit.
2. SuperAdmins have no way to inspect a single tutor's or tutee's activity. Existing admin
   analytics (platform KPIs, per-institution rollups, top-N tutor lists) are all aggregate views —
   there's no way to click on one specific user and see their full session/rating/earning history.

## Solution

Remove the institution-scoped `Admin` role entirely, consolidating all admin capability into the
single `SuperAdmin` tier. Existing `Admin` accounts are converted to `SuperAdmin` via a data
migration so nobody loses access. Institution scoping is dropped from everything that only existed
to support the `Admin` tier (admin permission checks, the admin-account-request workflow, and the
per-institution course/subject catalog, which becomes one global subject pool); `PartnerInstitution`
itself is untouched and remains available as a registration-domain gate and a reporting filter.
Frontend admin views are consolidated into the existing `/superadmin/*` area, and the demo-data
reset tooling is updated to match. Separately, a new per-user analytics drill-down is added to the
SuperAdmin user list: clicking a tutor or tutee opens a slide-over panel showing that user's
session history and stats, addressing the panel's second piece of feedback.

## User Stories

1. As a SuperAdmin, I want existing institutional Admin accounts automatically converted to
   SuperAdmin by a data migration, so that no one loses access when the role is removed.
2. As a SuperAdmin, I want the `Admin` role removed from the system entirely, so there is one clear
   admin tier instead of two overlapping ones.
3. As a SuperAdmin, I want every endpoint and view that used to accept either `Admin` or
   `SuperAdmin` to now require `SuperAdmin` only, so access control stays consistent after the role
   is removed.
4. As a developer, I want the institution-scoping logic in admin views and permission checks
   removed (not left as dead, unreachable branches), so the codebase doesn't carry logic for a role
   that no longer exists.
5. As a developer, I want the parallel institution-scoped admin frontend views deleted and their
   functionality consolidated into the existing SuperAdmin view set, so there's no duplicate UI to
   maintain.
6. As a SuperAdmin, I want the old institution-scoped admin routes to redirect to their SuperAdmin
   equivalents, so any bookmarked or shared links don't break.
7. As a SuperAdmin, I want subjects and courses to be available platform-wide instead of curated
   per institution, so tutors and tutees aren't restricted by a per-institution catalog that no
   longer has an owning role to curate it.
8. As a SuperAdmin, I want to manage one global list of subjects and courses (add/edit/remove),
   without an institution picker, so subject management is simpler.
9. As a developer, I want the per-institution course-catalog join table and the per-institution
   subject-ownership field removed via migration, so the schema matches the new global model.
10. As a developer, I want the existing "request to become Admin for my institution" workflow
    removed, since there is no institutional Admin role left to request.
11. As a SuperAdmin, I want the "request a new partner institution" workflow to keep working
    unchanged, since institutions are still used for registration and reporting.
12. As a SuperAdmin, I want `PartnerInstitution` to remain available as a filter on relevant
    lists/reports, so I can still narrow data down by school when more than one institution exists.
13. As a developer, I want the demo-data reset tooling updated to stop seeding a per-institution
    Admin account, so dev/demo environments match the new role model.
14. As a SuperAdmin, I want to click a tutor or tutee row in the user list and see a slide-over
    panel with their stats, so I don't have to leave the list to investigate a specific user.
15. As a SuperAdmin, I want the tutor drill-down to show session counts broken down by status
    (total/completed/cancelled/pending), so I can gauge their activity and reliability.
16. As a SuperAdmin, I want the tutor drill-down to show their average rating, so I can gauge
    tutoring quality.
17. As a SuperAdmin, I want the tutor drill-down to show their total earnings, so I can see their
    revenue impact on the platform.
18. As a SuperAdmin, I want the tutor drill-down to show which subjects they teach and which
    students they've had sessions with, so I understand their scope of activity.
19. As a SuperAdmin, I want the tutee drill-down to show session counts broken down by status, so I
    can gauge their engagement.
20. As a SuperAdmin, I want the tutee drill-down to show their total amount spent, so I can see
    their revenue impact on the platform.
21. As a SuperAdmin, I want the tutee drill-down to show which subjects they've booked and which
    tutors they've booked, so I understand their usage pattern.
22. As a SuperAdmin, I want the tutee drill-down to show the ratings they've given, so I can review
    their feedback history.
23. As a SuperAdmin, I want the drill-down panel to show all-time totals with no period toggle or
    export, so the first version stays simple.
24. As a SuperAdmin, I want the drill-down panel to open and close without navigating away from the
    user list, so I can quickly check multiple users in sequence.
25. As a developer, I want a proper Django data migration (not a one-off management command) for the
    `Admin` → `SuperAdmin` role conversion, so the real shared database is migrated safely and
    repeatably.
26. As a developer, I want backend admin API URL paths to remain unchanged even though the frontend
    routes move, so the API surface doesn't need a disruptive rename for no functional benefit.
27. As a SuperAdmin, I want tutor-tutee institution matching (a tutee only ever sees tutors from
    their own institution) to keep working exactly as it does today, so removing the Admin role and
    globalizing the subject catalog doesn't accidentally loosen who can book whom.

## Implementation Decisions

**Role model.** Remove the institution-scoped admin role from the user role field's set of valid
choices, leaving tutee, tutor, and the single platform-wide admin role (`SuperAdmin`, unchanged in
name). A data migration converts every existing user with the removed role to `SuperAdmin` before
the choice is dropped. `PartnerInstitution`'s domain-based registration matching is untouched.

**Permissions.** Every existing endpoint/view that currently accepts either the institution-scoped
admin role or `SuperAdmin` becomes `SuperAdmin`-only. Institution-scoping helpers (the queryset/
target-institution filtering used throughout the admin view layer) are removed rather than left
unreachable, since `SuperAdmin` was already unscoped.

**Request workflows.** The admin-account-request workflow (request/approve promotion to
institutional Admin) is deleted, including its model and endpoints. The institution-request
workflow (request a new partner institution) is unchanged.

**Global subject pool.** The per-institution subject-ownership field on the subjects model is
removed; any subject previously private to one institution becomes globally visible. The
per-institution course-catalog curation table is dropped entirely. The admin views that previously
managed per-institution catalog curation are reworked into a single global subject/course CRUD
surface — list, add, edit, remove — with no institution selector. This directly supersedes the
institution-scoped course catalog feature (`docs/specs/2026-07-05-institution-course-catalog-design.md`).
Making the subject/course catalog global does **not** change tutor-tutee institution matching —
that remains a hard filter based on `UserProfile.institution` (`docs/specs/2026-06-26-institution-scoped-matching-design.md`),
completely independent of which subjects exist.

**Frontend.** The institution-scoped admin views (dashboard, reports, withdrawals, users, support,
course catalog, tutor/tutee applications) are deleted; their functionality is consolidated into the
existing SuperAdmin view set, which already exists in parallel and was already being visually
aligned with the institution-scoped views in prior work
(`docs/specs/2026-06-21-admin-dashboard-redesign-design.md`, now superseded by this consolidation).
Old institution-scoped admin routes redirect to their SuperAdmin equivalents.

**Backend URL surface.** Existing `/api/admin/...` endpoint paths are unchanged — only their
permission gating tightens to `SuperAdmin`-only. No corresponding rename to `/api/superadmin/...`.

**Demo data.** The demo-data reset command is updated to seed and preserve only the SuperAdmin
login across resets, dropping the per-institution Admin account(s) it currently seeds.

**Per-user analytics drill-down.** A new read-only endpoint, reachable from the existing admin API
surface, returns an all-time stats payload for one user given their id and role:

- **Tutor payload:** session counts by status (total/completed/cancelled/pending), average rating,
  total earnings, list of subjects taught, list of students they've had sessions with (each with
  a session count).
- **Tutee payload:** session counts by status, total amount spent, list of subjects booked, list of
  tutors they've booked (each with a session count), list of ratings they've given.

No period filter and no export in this version — the endpoint always returns all-time totals.

On the frontend, a new slide-over panel is triggered by clicking a row in the SuperAdmin user list.
The panel stays anchored to the right of the list (the list remains visible/scrollable underneath)
and renders one of the two payload shapes above depending on the clicked user's role, sharing a
common header (avatar, name, role, institution) and section layout between the two variants. The
confirmed visual design is saved at `docs/mockups/2026-07-12-superadmin-user-drilldown.html`.

## Testing Decisions

Tests target real behavior through the same seam this codebase already uses for admin-area
coverage — Django REST Framework `APITestCase` classes hitting the actual endpoints, not internal
helper functions (matching `SuperAdminRedesignApiTests` and `AdminDashboardMetricsTests` in
`backend/studybuddy/tests.py`). One seam per concern, one test class per seam:

1. **Role removal & permission tightening** — an `APITestCase` class exercising the existing admin
   endpoints (withdrawals, users, applications, etc.) confirming they now reject anything but
   `SuperAdmin`, since the institution-scoped admin role no longer exists.
2. **Data migration** — a focused test that runs the role-conversion migration and asserts no user
   retains the removed role afterward, and that previously-Admin accounts became `SuperAdmin`.
3. **Global subject pool** — an `APITestCase` class against the reworked subject/course CRUD
   endpoint, confirming no institution scoping applies and the per-institution catalog table is
   gone.
4. **Per-user analytics endpoint** — an `APITestCase` class seeding Bookings, Payments, and ratings
   for a tutor and a tutee, asserting the endpoint's returned aggregates match the seeded data for
   both roles.
5. **Frontend** — no dedicated test runner beyond the existing baseline (`npm run lint`,
   `npm run build`); manual browser verification of the slide-over panel against the confirmed
   mockup, covering both the tutor and tutee payload shapes.

## Out of Scope

- Renaming the `SuperAdmin` role or any of its existing `/superadmin/*` frontend routes.
- Renaming backend `/api/admin/...` URL paths.
- A period toggle or CSV export on the new per-user drill-down panel (may be added later if
  needed).
- Any change to the institution-request (new partner institution) workflow.
- Any change to tutor-tutee institution-scoped matching — tutees must continue to see only tutors
  from their own institution; this is unrelated to the subject catalog becoming global and must not
  regress.
- Any change to booking, payment, verification, or recommender logic.
- Historical/point-in-time reporting on the new per-user drill-down — it always reflects current
  all-time totals, not a snapshot.

## Further Notes

- Originated from a panel defense review (no fixed resubmission deadline).
- Confirmed via a grilling session in this conversation; the slide-over panel design was confirmed
  interactively via `ui-preview` and saved to `docs/mockups/2026-07-12-superadmin-user-drilldown.html`.
- Supersedes/reverses `docs/specs/2026-07-05-institution-course-catalog-design.md` (per-institution
  catalog curation) and simplifies past the parallel-alignment work in
  `docs/specs/2026-06-21-admin-dashboard-redesign-design.md`.
- Builds on top of, and simplifies, the role split introduced in
  `docs/plans/2026-06-08-superadmin-institution-hierarchy.md` and
  `docs/specs/2026-06-17-superadmin-redesign-design.md`.
- Does not touch `docs/specs/2026-06-26-institution-scoped-matching-design.md` — see Out of Scope.
- This spec spans a real shared database, so the role-conversion migration is production-safe by
  requirement, not just a dev/demo convenience.
