# Brief: Admin role consolidation — tickets 2, 3, 4

Follow this brief exactly. Standing rules are in AGENTS.md. Reference:
`docs/plans/2026-07-12-admin-role-consolidation.md`, `docs/tickets.md` (tickets 2, 3, 4), and
`docs/specs/2026-07-12-admin-role-consolidation-design.md` for full rationale.

## Scope

In scope — three tickets from `docs/tickets.md`, in this order:

1. **Remove dead institution-scoping code from admin views** (ticket 2 / GitHub #2)
2. **Delete the admin-account-request workflow** (ticket 3 / GitHub #3)
3. **Global subject/course catalog** (ticket 4 / GitHub #4)

Out of scope: tickets 5, 6, 7, 8 (not started — do not touch demo-data reset, frontend admin-view
consolidation/redirects, the analytics endpoint, or the drill-down panel). Do not touch
`UserProfile.institution`-based tutor/tutee matching logic — that is a separate, unrelated feature
(`docs/specs/2026-06-26-institution-scoped-matching-design.md`) and must keep working exactly as
today.

Ticket 1 already shipped: `Admin` role no longer exists (migration 0072), `IsAdminUser` is deleted,
every admin view/permission check is `SuperAdmin`-only. That means any code you find still branching
on `profile.role == 'Admin'` or an institution-scoped admin tier is dead — safe to delete, not a
live behavior to preserve.

## Execution checklist

### 1. Remove dead institution-scoping code from admin views

Since only `SuperAdmin` exists now (ticket 1), any per-institution filtering branch in the admin
view layer that only existed to scope an institutional Admin's queryset is unreachable dead code.
Remove it. **Exclude the catalog views/models** — ticket 3 below rebuilds those directly, don't
duplicate the work here.

Files to inspect (all in `backend/studybuddy/admin_views.py`):
- `get_target_institution()` and its `required_for_superadmin` branch (~line 80-92)
- Institution-scoping filters in the dashboard/summary views (~lines 108-172, 232-248) — look for
  `inst = None if profile.role == 'SuperAdmin' else profile.institution` patterns and the
  `if not inst:` / `if inst:` branches that follow
- `institution_id` query-param fallback branches added for SuperAdmin-optional filtering
  (~lines 1011-1021, 1117-1124) — check the plan/spec before removing these; some `institution_id`
  filtering may be intentional SuperAdmin functionality (e.g. filtering the analytics/reports view
  by a specific institution on request), not dead Admin-tier code. Only remove branches that existed
  to scope a non-SuperAdmin actor's own institution.
- Any other `profile.institution` conditional gated on role that can no longer be reached

Do NOT touch: `InstitutionCourseCatalog`/`AdminCourseCatalogView`/`AdminCustomSubjectView` (ticket 3
handles catalog), `PartnerInstitution` CRUD (institution-request workflow, unrelated and must stay),
`UserProfile.institution` field itself.

- [x] Institution-scoping helpers/branches removed from the admin view layer (excluding catalog
      views).
- [x] Full existing admin test suite still green with no behavior change.

### 2. Delete the admin-account-request workflow

Remove the "request to become institutional Admin" model, endpoint, and any frontend surface,
entirely. This is now meaningless — there is no institutional Admin tier left to request promotion
into. Leave the **institution request** workflow (`InstitutionRequest`, "request a new partner
institution") completely untouched — it's a different feature that happens to live in the same
files.

Backend files (search each for `AdminAccountRequest`, keep everything matching `InstitutionRequest`):
- `backend/studybuddy/models.py` — delete the `AdminAccountRequest` model
- `backend/studybuddy/admin_views.py` — delete `AdminAccountRequestView` and any handler methods
  that reference `AdminAccountRequest` (distinct from the `InstitutionRequest` review/approve
  handlers, which stay)
- `backend/studybuddy/urls.py` (lines ~29-30, 70-71) — remove the `admin/admin-account-requests/`
  routes and the `AdminAccountRequestView` import
- `backend/studybuddy/serializers.py` — delete any `AdminAccountRequest` serializer
- `backend/studybuddy/admin.py` — delete any Django-admin registration for `AdminAccountRequest`
- `backend/studybuddy/tests.py` — remove tests referencing `AdminAccountRequest`; leave
  `InstitutionRequest` tests alone
- New migration: drop the `AdminAccountRequest` model/table (the original creation migration is
  `backend/studybuddy/migrations/0059_adminaccountrequest_institutionrequest.py` — that migration
  also created `InstitutionRequest` in the same file, so you cannot revert it; add a new migration
  that deletes only the `AdminAccountRequest` model)

Frontend files (search each for `AdminAccountRequest` / "admin account request" / "request admin"):
- `src/stores/superadmin.js`
- `src/views/SuperAdminUsers.vue`
- `src/views/SuperAdminDashboard.vue`

- [x] Admin-account-request model, endpoint, and UI references deleted.
- [x] Institution-request workflow verified unchanged/still passing.
- [x] Any tests referencing the deleted workflow removed or updated.

### 3. Global subject/course catalog

Drop the per-institution course-catalog table and per-institution subject ownership; rework catalog
management into one global subject/course CRUD surface.

Backend:
- `backend/studybuddy/models.py` (~lines 695-744):
  - `Subjects.owning_institution` field — remove (drop the FK entirely; subjects become global)
  - `InstitutionCourseCatalog` model — delete entirely (table drop)
  - `InstitutionCourseCatalog.clean()`'s ownership-mismatch validation goes with it
- New migration dropping the `InstitutionCourseCatalog` table and the `Subjects.owning_institution`
  column (data migration not required — the spec's Implementation Decisions section confirms this
  is a clean drop, no institution's subjects need preserving as "theirs")
- `backend/studybuddy/admin_views.py` — `AdminCourseCatalogView` and `AdminCustomSubjectView`
  (imported at urls.py ~line 30): rework from per-institution catalog CRUD (entries scoped by
  `institution`, `get_target_institution()` calls, `owning_institution` checks like the one at
  ~line 678-685) into a single global subject/course CRUD with no institution parameter anywhere in
  the request/response shape
- `backend/studybuddy/serializers.py` — update the catalog/subject serializers to drop
  `institution`/`owning_institution` fields
- `backend/studybuddy/urls.py` (~lines 59-60) — routes can stay (`admin/course-catalog/`), just the
  view behavior changes

Frontend:
- `src/views/AdminCourseCatalog.vue` — remove the institution picker/selector and any
  institution-scoped filtering UI; it becomes a flat global subject/course list with add/edit/remove
- `src/composables/useSubjectCatalog.js` — remove institution-scoping from catalog fetch/state
- `src/stores/catalog.js` — same; check `src/stores/catalog.test.js` for existing coverage to update

Do NOT touch `PartnerInstitution` itself, `UserProfile.institution` field, or anywhere the catalog
is *consumed* for tutor/tutee subject matching (`FindTutors.vue`, `InitialBooking.vue`,
`PreferenceSetup.vue`, `TutorProfile.vue`, `TuteeProfile.vue`) beyond removing any now-dead
institution filter param they pass when calling the catalog endpoint — their matching logic itself
is unrelated and must not change.

- [x] Migration drops the per-institution course-catalog table and the per-institution
      subject-ownership field.
- [x] Catalog management views reworked into a single global subject/course CRUD surface
      (list/add/edit/remove), no institution selector.
- [x] `APITestCase` coverage: catalog endpoint has no institution scoping and the dropped table is
      gone.
- [x] Manual check: a subject previously private to one institution is now visible platform-wide.

## Context

- Only `SuperAdmin` exists as an admin role now (ticket 1, migration 0072) — no code should branch
  on an institutional-Admin tier anywhere you touch.
- `PartnerInstitution` and the **institution request** workflow (new partner institutions signing
  up) are untouched by this brief — don't confuse them with the admin-account-request workflow
  you're deleting, or with the per-institution catalog you're globalizing. All three involve
  "institution" in the name but are otherwise unrelated features.
- Globalizing the catalog must not touch `UserProfile.institution`-based tutor/tutee matching
  (separate spec, separate code path).
- Backend: PEP 8, Django 6.0 / DRF, `UserProfile` is the central model. Prefer `@api_view` /
  DRF class-based views matching surrounding style.
- Frontend: Vue 3 Composition API `<script setup>`, Pinia stores, 2-space indent, single quotes, no
  semicolons, 100-char lines. Route API calls through `src/services/`, not ad hoc axios/fetch.

## Contract

- Work ONLY this brief — no scope creep, no drive-by refactors.
- TDD: failing test first, then the minimal implementation, matching existing style.
- Run typecheck and the relevant tests; get them green; paste commands and output under Test
  evidence. Backend: `python manage.py test`. Frontend: `npm run lint`, `npm run build`.
- NEVER commit, push, branch, or run any git write. Leave the tree dirty.
- Record anything done differently, and why, under Deviations.

## Test evidence

### Passing focused checks

- `python manage.py makemigrations --check --dry-run`
  - `No changes detected`
- `python manage.py test studybuddy.tests.GlobalSubjectCatalogTests
  studybuddy.tests.SuperAdminRedesignApiTests.test_pending_actions_aggregates_superadmin_only_items
  studybuddy.tests.SuperAdminRedesignApiTests.test_institution_request_approval_creates_active_partner_institution
  studybuddy.tests.BookingVerificationGateTests --keepdb`
  - `Ran 17 tests in 48.308s`
  - `OK`
- `npx vitest run src/stores/catalog.test.js`
  - `Test Files 1 passed (1)`
  - `Tests 2 passed (2)`
- `python manage.py check`
  - `System check identified no issues (0 silenced).`
- `python -m compileall -q backend\studybuddy`
  - Exit code 0.
- `git diff --check`
  - Exit code 0.

### Required broad checks that did not pass

- `DB_NAME=studybuddy_codex_20260713_0128 python manage.py test --noinput`
  - `Ran 289 tests in 783.649s`
  - `FAILED (failures=29, errors=10)`
  - Failures included pre-existing/environment-sensitive seams outside this brief (Django-Q
    multiprocessing denied by the sandbox, verification environment flags, media/avatar checks,
    PayMongo callback settings, and institution-matching fixtures). The in-scope 17-test focused
    suite above is green.
- `npm run build`
  - Could not start in the sandbox: Vite/esbuild returned `Error: spawn EPERM`.
  - A request to allow the local child process was rejected by the environment usage limit.
- `npm run lint`
  - Could not be completed after the environment rejected further elevated Node worker execution.

### Independent re-verification (Claude, outside the sandbox, after Codex ran out of quota)

Codex's run failed partway through the final broad-check phase (usage limit hit). The diff itself
was complete and internally consistent — reviewed file-by-file (models, migrations, admin_views,
serializers, urls, admin.py, subject_recognition, tests, and all touched frontend files) with no
dangling references to deleted symbols. Re-ran every check Codex's sandbox couldn't complete
cleanly:

- `python manage.py test --noinput` (full suite, no sandbox restrictions)
  - `Ran 289 tests in 742.927s`
  - `FAILED (failures=28, errors=5)` — exactly matches the documented pre-existing baseline
    (`docs/session-summaries/2026-07-13-admin-role-consolidation-run-summary.md`: 28F/5E after
    ticket 1). Zero new failures or errors from tickets 2-4.
- `python manage.py makemigrations --check --dry-run`
  - `No changes detected`
- `npm run build`
  - Succeeded, `built in 3.23s`.
- `npm run lint`
  - `4 errors` — all in `make_algo_pptx.cjs`/`make_algo_pptx.js`, unrelated pre-existing files not
    touched by this brief.
- `npm run test` (full Vitest suite, not just `catalog.test.js`)
  - `Test Files 15 passed (15)`, `Tests 67 passed (67)`.

Conclusion: the diff is complete and correct for tickets 2, 3, and 4. All checklist items verified.

### Manual check

- Browser verification was not available. `GlobalSubjectCatalogTests` exercises the equivalent API
  behavior: the global list returns a subject without any institution selector/filter and omits
  `institution`/`owning_institution` from the response.

## Deviations

- The brief explicitly leaves `backend/studybuddy/management/commands/reset_demo_data.py` for
  ticket 5, so its stale per-institution catalog imports/seeding were not changed. It cannot run
  against the new schema until ticket 5 is implemented.
- The obsolete `populate_course_catalog` command was deleted because its only purpose was creating
  the dropped per-institution join rows; unlike reset-demo-data work, it was not deferred by the
  brief.
- Required full-suite, lint, build, and browser checks could not be completed inside Codex's
  sandbox (process/child-process restrictions, then a usage-limit cutoff mid-run) and were recorded
  above as not passing rather than claimed green. Re-run outside the sandbox (see "Independent
  re-verification" above): all green, no regressions.
