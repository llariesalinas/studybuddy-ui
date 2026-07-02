---
title: Full-system integration merge — session summary
date: 2026-07-02
plan: ../plans/2026-07-02-full-system-integration-merge.md
status: Done (branch verified; push/PR deferred to user)
---

# Full-System Integration Merge — Summary

## What shipped

A single integration branch, `feat/full-system-integration`, containing **both** feature lines:

- **Tutee enrollment verification** (ours — was `feat/tutee-enrollment-verification`, PR #101):
  tutee application/renewal/status endpoints and admin queue, booking-gate (forward-only)
  enforcement, `VerificationStatusCard`, two-role admin applications UI.
- **Cashout-branch features** (theirs — `feature-cashout-recent-transactions`): wallet cash-in,
  cash-out recent transactions + `TutorPayoutAccount` removal, `AppSidebar` redesign,
  institution-scoped matching, admin dashboard redesign, superadmin expansion, support-ticket
  escalation, session check-ins.

Delivered as a real 3-way `git merge` (history from both sides preserved), not cherry-picks.

## How it was done vs. planned

Followed the plan (`2026-07-02-full-system-integration-merge.md`) task-by-task. The plan's measured
facts held exactly: the merge produced precisely the predicted **17-file conflict set**, and the two
migration chains reconciled with a single `makemigrations --merge` node and **no residual
model-state drift**.

Resolution approach: union wherever both sides added logic; dominant-side base for structural
rewrites. Key decisions:

- **Backend imports** (`urls`, `serializers`, `admin_views`, `views`, `tests`): unioned; dropped
  `TutorPayoutAccount` everywhere (model removed on theirs). Import smoke test passed.
- **`views.py`**: unioned our verification helpers + booking gate with their wallet/support/checkin
  code; adopted their `get_login_profile_for_user` in `login_view` and `profile_status` (admin
  auto-provisioning); kept `get_cashout_minimum` and support-escalation ticket filtering.
- **Frontend**: adopted their `AppSidebar` shell + admin/tutor-profile redesigns; kept our
  two-role application-status/admin views and `VerificationStatusCard` wiring.

## Deviations from the plan

- **Branched from `3b9d45a`**, one docs-only commit past the measured `1c0a075` (no code impact).
- **`AppSidebar.vue` edited beyond the listed conflict files**: their sidebar redesign dropped the
  admin/superadmin "Tutor Applications" nav entry, so it was hand-ported into `AppSidebar.vue`
  (menu is a data array). Verified rendering + routing in the browser.
- **`AdminDashboard.vue`**: took their redesign wholesale; our old-style "Tutor Applications"
  quick-action card was dropped rather than force-fit — access is preserved via the sidebar nav.
- **Merge-artifact cleanups**: removed a duplicate `deferStartupWork` in `App.vue`, dead accordion
  helpers in `TutorProfile.vue`, and (post-merge lint) two unused tutor helpers in `Dashboard.vue`
  the cashout branch had carried in.
- **`login_view`** lost a `select_related('tutor_application','institution')` optimization by
  adopting `get_login_profile_for_user` — perf only, not correctness.
- **Gate G1 was a non-event.** The plan gated the destructive `0063_remove_tutorpayoutaccount`
  behind explicit go/no-go. On execution, the dev DB was already at `0063` (dropped during earlier
  cashout-branch work), so only `0064` + the merge node `0065` applied. User confirmed the DB is a
  shared-but-idle pre-production Supabase instance with throwaway data; reseed is the rollback.

## Checks run + results

- `python -c "... django.setup(); import studybuddy.{views,admin_views,serializers,urls}"` — **OK**.
- `npm run lint` — **0 errors** (after `4312ce8` dead-helper removal).
- `npm run build` — **succeeds**.
- `npx vitest run` — **54/54 pass**.
- `makemigrations --check --dry-run` (post-merge-node) — **"No changes detected"**.
- `migrate` on dev DB — applied `0064`+`0065`; `migrate --check` exit 0.
- **Three-branch Django baseline diff** (remote Supabase test DB):
  - Ours (`3b9d45a`): 121 tests, 11 fails/errors.
  - Theirs (`feature-cashout-recent-transactions`): 176 tests, 16.
  - Integration: 205 tests, 16.
  - **`C − (A ∪ B)` = empty** — integration failures are identical by name to theirs', 6 also on
    ours. No test that passed on either parent newly fails. The 16 pre-existing: 11 recommender/
    search (institution-scoped matching + remote-DB env), 3 admin analytics, 2 avatar/image.
- **Focused browser seam-check** (tutee + admin, OTP via dev `debug_code`): login →
  land-correctly, ported sidebar nav renders/routes, two-role admin applications tabs render,
  `VerificationStatusCard` renders, admin `operational-queue` + `stats` + `tutor-applications` all
  200. Booking-gate 403 covered by passing `BookingVerificationGateTests`. No 500s.

## Commits

`dd0758d` merge · `3cdfb28` migration merge node · `4312ce8` lint fix · plus docs commits.

## Not done / follow-ups

- **Push + PR deferred to user** (chose "finish docs, don't push yet"). Options still open: new PR
  superseding #101, or retarget #101.
- **Pre-existing recommender/search failures** (11) predate this merge on both branches — worth a
  separate look, likely tied to institution-scoped matching test setup and the remote test DB.
- **Two trial accounts** (`Tutee1@gmail.com`, `reg2@gmail.com`) had a known password +
  `is_domain_exempt=True` set for the browser drive; reseed to clear.
- **Dev servers** (Django :8000, Vite :5173) were left running during the session.
