# Tickets: Admin role consolidation & SuperAdmin user analytics

Removes the institution-scoped Admin role in favor of a single SuperAdmin tier, globalizes the
subject/course catalog, and adds a per-tutor/per-tutee analytics drill-down to the SuperAdmin user
list. Source spec: [`docs/specs/2026-07-12-admin-role-consolidation-design.md`](specs/2026-07-12-admin-role-consolidation-design.md).
Also mirrored to GitHub Issues on the fork repo.

Work the **frontier**: any ticket whose blockers are all done. Tickets 1, 2, 3, and 4 are done; the
frontier is now tickets 5, 6 (both unblocked), and 7 (was already open).

Mirrored to GitHub Issues on [RayDomD/studybuddy-ui](https://github.com/RayDomD/studybuddy-ui),
labeled `ready-for-agent`, issue numbers noted per ticket below.

## Convert institutional Admins to SuperAdmin

GitHub: [#1](https://github.com/RayDomD/studybuddy-ui/issues/1)

**What to build:** Existing `Admin` accounts become `SuperAdmin` via a real-database-safe data
migration; `Admin` is removed from the role choices; admin permission checks tighten to
`SuperAdmin`-only everywhere. A former Admin logs in and lands with full SuperAdmin access.

**Blocked by:** None — can start immediately.

**Model:** mid

- [x] Data migration converts every `UserProfile` with role `Admin` to `SuperAdmin`, then removes
      `Admin` from the role field's valid choices. (migration 0072)
- [x] Every endpoint/view that previously accepted either `Admin` or `SuperAdmin` now requires
      `SuperAdmin` only. (`IsAdminUser` deleted; 17 views re-gated; role checks tightened)
- [x] `APITestCase` coverage: existing admin endpoints reject anything but `SuperAdmin`.
      (`AdminEndpointsRequireSuperAdminTests`)
- [x] Migration test: no `UserProfile` retains role `Admin` after migration; previously-Admin rows
      are `SuperAdmin`. (`AdminToSuperAdminMigrationTests`)

## Remove dead institution-scoping code from admin views

GitHub: [#2](https://github.com/RayDomD/studybuddy-ui/issues/2)

**What to build:** The institution-filtering branches across the admin view layer, now unreachable
since only `SuperAdmin` exists, are deleted. Excludes the catalog views — the global-catalog ticket
rebuilds those directly. Pure cleanup; no behavior change (`SuperAdmin` was already unscoped).

**Blocked by:** Convert institutional Admins to SuperAdmin

**Model:** small

- [x] Institution-scoping helpers/branches removed from the admin view layer (excluding catalog
      views).
- [x] Full existing admin test suite still green with no behavior change.

## Delete the admin-account-request workflow

GitHub: [#3](https://github.com/RayDomD/studybuddy-ui/issues/3)

**What to build:** The "request to become institutional Admin" model, endpoint, and any frontend
surface are removed entirely. The separate "request a new partner institution" workflow is
untouched and still works.

**Blocked by:** Convert institutional Admins to SuperAdmin

**Model:** small

- [x] Admin-account-request model, endpoint, and UI references deleted.
- [x] Institution-request workflow verified unchanged/still passing.
- [x] Any tests referencing the deleted workflow removed or updated.

## Global subject/course catalog

GitHub: [#4](https://github.com/RayDomD/studybuddy-ui/issues/4)

**What to build:** The per-institution course-catalog table and per-institution subject ownership
are dropped via migration. Catalog management becomes one global subject/course CRUD screen with no
institution picker.

**Blocked by:** Convert institutional Admins to SuperAdmin

**Model:** mid

- [x] Migration drops the per-institution course-catalog table and the per-institution
      subject-ownership field.
- [x] Catalog management views reworked into a single global subject/course CRUD surface
      (list/add/edit/remove), no institution selector.
- [x] `APITestCase` coverage: catalog endpoint has no institution scoping and the dropped table is
      gone.
- [x] Manual check: a subject previously private to one institution is now visible platform-wide.

## Update demo-data reset for the new role/catalog model

GitHub: [#5](https://github.com/RayDomD/studybuddy-ui/issues/5)

**What to build:** The demo-data reset command only seeds/preserves the SuperAdmin login (no
per-institution Admin account) and seeds the course catalog against the new global model.

**Blocked by:** Convert institutional Admins to SuperAdmin, Global subject/course catalog

**Model:** small

- [ ] Demo-data reset no longer creates/preserves a per-institution Admin account.
- [ ] Demo-data reset's catalog seeding matches the global model.
- [ ] Manual check: running the reset command leaves only the SuperAdmin login across resets.

## Consolidate frontend admin views into SuperAdmin

GitHub: [#6](https://github.com/RayDomD/studybuddy-ui/issues/6)

**What to build:** Institution-scoped admin views (dashboard, reports, withdrawals, users, support,
tutor/tutee applications) are deleted; any functionality they had that the SuperAdmin equivalents
don't yet cover is merged in. Old institution-scoped routes redirect to their SuperAdmin
equivalents.

**Blocked by:** Convert institutional Admins to SuperAdmin, Delete the admin-account-request
workflow, Global subject/course catalog

**Model:** top

- [ ] Institution-scoped admin views deleted; SuperAdmin views cover their functionality.
- [ ] Old admin routes redirect to SuperAdmin equivalents (no dead links).
- [ ] `npm run lint` and `npm run build` passing.
- [ ] Manual check: diffed institution-scoped views against SuperAdmin equivalents for feature
      parity before deletion (flagged risk in the plan — don't assume parity).

## Per-user analytics endpoint

GitHub: [#7](https://github.com/RayDomD/studybuddy-ui/issues/7)

**What to build:** A new read-only endpoint returns an all-time stats payload for one tutor or
tutee: session counts by status, average rating, total earnings, subjects taught, and student list
for tutors; session counts by status, total amount spent, subjects booked, tutor list, and ratings
given for tutees.

**Blocked by:** Convert institutional Admins to SuperAdmin

**Model:** mid

- [ ] Endpoint returns the correct tutor payload shape for a seeded tutor with known
      Bookings/Payments/ratings.
- [ ] Endpoint returns the correct tutee payload shape for a seeded tutee with known
      Bookings/Payments/ratings given.
- [ ] `APITestCase` coverage for both shapes.
- [ ] Endpoint is `SuperAdmin`-only.

## SuperAdmin user list drill-down panel

GitHub: [#8](https://github.com/RayDomD/studybuddy-ui/issues/8)

**What to build:** Clicking a tutor or tutee row in the SuperAdmin user list opens a slide-over
panel (list stays visible underneath) showing that user's all-time stats, matching the confirmed
mockup. One panel component, role-conditional body.

**Blocked by:** Per-user analytics endpoint

**Model:** mid

- [ ] Clicking a row opens the panel without navigating away from the user list.
- [ ] Tutor and tutee variants both match
      [`docs/mockups/2026-07-12-superadmin-user-drilldown.html`](mockups/2026-07-12-superadmin-user-drilldown.html).
- [ ] All-time totals only — no period toggle or export in this pass.
- [ ] `npm run lint` and `npm run build` passing.
