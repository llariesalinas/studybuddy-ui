# Admin Role Consolidation — Orchestrate Run Summary (ended early by design)

**Date:** 2026-07-13
**Branch:** `feat/admin-role-consolidation` (off `feat/demo-data-reset`)
**Plan:** `docs/plans/2026-07-12-admin-role-consolidation.md` (stays In Progress)
**Tickets:** `docs/tickets.md`, mirrored as GitHub Issues #1-8 on the fork

## What happened vs. planned

An `/orchestrate` run started on the 8-ticket graph. After ticket 1 was dispatched, the user
directed the run to stop after ticket 1 and hand the remaining tickets (2-8) to the Codex CLI via
`/codex-brief` / `/codex-review`. Ticket 1 completed, passed review, and is committed; the run then
ended. This early stop is a deliberate executor handoff, not a blockage.

## Run report

| Ticket | Model | Escalations | Review outcome | Commit |
| --- | --- | --- | --- | --- |
| 1. Convert institutional Admins to SuperAdmin | top (bumped from mid at dispatch: cross-cutting permissions + real-DB migration + wide test surface) | none | Pass on first attempt | `feat: consolidate institutional Admin role into SuperAdmin` |

## What ticket 1 shipped

- Migration `0072_convert_admin_to_superadmin`: data op converts `role='Admin'` rows to
  `SuperAdmin` (plain UPDATE, signal-free, real-DB-safe), then drops `Admin` from
  `UserProfile.ROLE_CHOICES`.
- `IsAdminUser` permission class deleted; all 17 admin views in `admin_views.py` re-gated to
  `IsSuperAdminUser`; scattered role checks in `views.py` (login domain check, staff-login profile
  defaults, support-ticket claim/list/resolve) tightened to SuperAdmin-only.
- Tests: new `AdminEndpointsRequireSuperAdminTests` (401 unauth / 403 Tutor / 403 legacy
  unmigrated Admin row / 200 SuperAdmin across 4 representative endpoints) and
  `AdminToSuperAdminMigrationTests` (exercises the 0072 forward function). Ten tests that
  exclusively verified the removed Admin-vs-SuperAdmin institution-scoping behavior were deleted;
  six were rewritten/re-fixtured (details in the ticket 1 executor report, reproduced in the
  conversation).

## Deliberate leftovers (owned by later tickets)

- `AdminAccountRequestView` internals still reference/assign role `'Admin'` — deleted wholesale by
  ticket 3.
- `admin_escalate_ticket` requires role `'Admin'` and is now unreachable (no user can hold that
  role) — the escalation workflow dies with the Admin tier; endpoint removal belongs to ticket 2's
  dead-code cleanup. Flagged as a spec deviation-by-implication: the spec never mentioned support
  ticket escalation.
- `reset_demo_data.py` still seeds a per-institution Admin account — ticket 5.
- Institution-scoping branches in admin views (`BaseAdminView.get_queryset_for_user` etc.) are now
  dead code — ticket 2.
- Historical migrations 0003/0051 keep their Admin choice text (never edit old migrations).

## Checks run

- Executor: 47 targeted tests across 9 classes (both new classes plus every touched class) — all
  green except one pre-existing failure; `makemigrations --check --dry-run` clean.
- Orchestrator (independent): full backend suite against local PostgreSQL
  (`DB_HOST=localhost ... manage.py test`) — 289 tests, 28 failures / 5 errors, every one verified
  by name to be in the known pre-existing baseline categories (recommender cluster 25, PaymentMethod
  duplicate-key analytics test, avatar uploads 2, PayMongo cashout 2, DevWallet debug flag,
  VerificationDevTools 2). Zero failures in permission/role/admin-endpoint territory. Baseline was
  30F/5E on 2026-07-07; the small drop is the deleted scoped tests.
- Frontend checks not run: ticket 1 touched no frontend files.

## Frontier at handoff

Tickets 2, 3, 4, and 7 are unblocked. Caution for the Codex handoff: they overlap heavily in
`admin_views.py`, `views.py`, `urls.py`, and `tests.py` — run them one at a time, not in parallel.
Ticket 1's "leftover" list above is the starting state Codex briefs should assume.
