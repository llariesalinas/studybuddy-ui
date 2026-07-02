---
title: Full-system integration merge (tutee verification + cashout-branch features)
date: 2026-07-02
status: In Progress
spec: 2026-07-01-tutee-verification-overview.md
---

# Full-System Integration Merge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this
> plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. This is a *merge* plan, not
> greenfield TDD — the test cycle per task is "resolve → build/import-check → commit", with full
> suites at defined milestones.

**Goal:** Produce one branch containing both feature lines — tutee enrollment verification (current
`feat/tutee-enrollment-verification`, PR #101) and everything on `feature-cashout-recent-transactions`
(wallet cash-in, cash-out recent transactions + `TutorPayoutAccount` removal, sidebar redesign,
institution-scoped matching, admin dashboard redesign, superadmin expansion, support escalation,
session check-ins, and that branch's earlier never-merged work) — verified and production-ready.

**Architecture:** A single 3-way `git merge` on a new integration branch, not cherry-picks. Both
branches share merge-base `b773afd` (2026-06-12); git auto-merges everything only one side touched
and stops on 17 genuinely-contested files. Each conflicted file has a measured "dominant side"
(the side with the larger structural rewrite) that becomes the resolution base, with the other
side's delta re-applied. The Django migration graph forks after `0053` into two disjoint chains
with **no filename collisions**; one `makemigrations --merge` node reconciles it.

**Tech Stack:** git merge / merge-tree, Django 6 migrations, Vitest, Vite build, Django test runner.

## Status & Progress Summary

**Status: In Progress — Tasks 1-7 complete and verified; only Task 8 (docs + push/PR) remains.**
Branch `feat/full-system-integration` from `3b9d45a`; safety tag `pre-integration-merge-20260702`.
All 17 conflicts resolved, merge committed (`dd0758d`), migration heads reconciled
(`0065_merge_20260702_1734.py`, `3cdfb28`), dev DB migrated to head (Gate G1 turned out to be a
non-event — the DB was already at `0063`, so `TutorPayoutAccount` was already dropped from earlier
cashout-branch work; only `0064`+`0065` applied). **Verification result: the merge is clean.**
The three-branch baseline diff proves `C − (A ∪ B) = ∅` (no test that passed on a parent newly
fails; all 16 integration failures are pre-existing, identical to theirs' set). `npm run lint`
clean, `npm run build` passes, `npx vitest run` 54/54. A focused browser seam-check confirmed the
highest-risk resolutions (login/`get_login_profile_for_user`, ported sidebar nav, two-role admin
applications, `VerificationStatusCard`, admin operational-queue) all work with 200s and no 500s.
**One gate left (needs user): Task 8 push/PR shape** — new PR superseding #101 vs. retarget #101.

**Key resolution decisions (deviations worth noting):**
- Adopted their `AppSidebar` shell; re-added the admin/superadmin "Tutor Applications" nav entry
  into `AppSidebar.vue` (our access point, since their redesign dropped the old inline nav).
- `AdminDashboard.vue`: took their redesign wholesale; our old-style "Tutor Applications" quick-action
  card was dropped (access preserved via the sidebar nav), rather than force-fitting it into their
  new layout.
- `views.py`: adopted their `get_login_profile_for_user` (admin auto-provisioning) in both
  `profile_status` and `login_view`, losing our `select_related` optimization in login (perf only).
- Removed a duplicate `deferStartupWork` (App.vue) and dead accordion helpers (TutorProfile.vue)
  created/orphaned by the merge.

## Global Constraints

- Never work on `main`; all work happens on the new `feat/full-system-integration` branch, leaving
  `feat/tutee-enrollment-verification` (PR #101) untouched as a fallback.
- No pushes without explicit user confirmation (house rule).
- **Gate G1:** migration `0063_remove_tutorpayoutaccount` destructively drops the
  `TutorPayoutAccount` table. It must not be applied to any database containing real payout data
  without explicit user go/no-go at execution time (carried over from PR #94's own notes).
- Original commit history from both branches is preserved (merge commit, no squash/rebase).
- Conflict resolutions must *union* the two features wherever both sides added logic to the same
  region; dropping either side's behavior is a defect.
- No emojis anywhere; conventional commit style.

## Measured Facts (inputs to this plan)

**Merge base:** `b773afd` ("Add/add super admin (#91)", 2026-06-12).
Theirs = `feature-cashout-recent-transactions` (`71a520c`, 246 non-merge commits ahead).
Ours = `feat/tutee-enrollment-verification` (`1c0a075`, 11 commits ahead of `origin/main`).

**Migration chains after shared `0053`** (no filename collisions — all files coexist):

| Ours | Theirs |
| --- | --- |
| 0054_tutorapplication_application_status_idx | 0054_booking_dashboard_hidden_fields |
| 0055_merge_20260617_0142 | 0055_deactivate_cash_payment |
| 0056_tutordocumentrenewalreview | 0056_sessioncheckin |
| 0057_merge_recommendation_indexes_document_renewals | 0057_merge_20260614_0347 |
| 0058_tutorapplication_reminder_1day_sent_at_and_more | 0058_alter_transaction_transaction_type_wallettopup |
| 0059_alter_platformactivity_activity_type (**our head**) | 0059_adminaccountrequest_institutionrequest |
| | 0060_remove_cashout_rail_fields |
| | 0061_withdrawalrequest_note |
| | 0062_withdrawalrequest_receiving_institution_code_and_more |
| | 0063_remove_tutorpayoutaccount (**destructive — Gate G1**) |
| | 0064_supportticket_escalation (**their head**) |

**The 17 conflicted files, dominant side, and resolution strategy** (line stats are each side's
diff vs merge base, `+added/-removed`):

| File | Ours | Theirs | Dominant | Strategy |
| --- | --- | --- | --- | --- |
| backend/studybuddy/views.py | +458/-64 | +854/-180 | neither | Union by section — see Task 4 |
| backend/studybuddy/tests.py | +788/-0 | +2963/-644 | theirs | Their file as base; our test classes are purely additive — re-append all our classes |
| backend/studybuddy/admin_views.py | +265/-30 | +561/-27 | theirs | Their base + re-apply our tutee admin views (list/detail/renewal) |
| backend/studybuddy/serializers.py | +263/-2 | +124/-3 | ours | Our base + re-apply their wallet/cashout/superadmin serializers |
| backend/studybuddy/urls.py | +13/-1 | +19/-3 | neither | Small file; hand-union both route sets |
| src/App.vue | +22/-1 | +199/-310 | theirs | Their AppSidebar-based shell + re-apply our small additions |
| src/views/AdminDashboard.vue | +10/-0 | +626/-202 | theirs | Their redesign + our 10 lines |
| src/views/AdminUsers.vue | +0/-10 | +21/-6 | theirs | Their base; keep our 10-line removal if still applicable |
| src/views/AdminTutorApplications.vue | +186/-30 | +3/-8 | ours | Our role-tab version + their 3-line tweak |
| src/views/TutorApplicationStatus.vue | +242/-37 | +4/-9 | ours | Our generalized two-role version + their small fix |
| src/views/TutorProfile.vue | +10/-3 | +39/-68 | theirs | Their redesign + our VerificationStatusCard wiring |
| src/components/TutorScreeningModal.vue | +42/-9 | +4/-5 | ours | Our base + their fix |
| src/stores/admin.js | +152/-10 | +37/-3 | ours | Our base (tutee application actions) + their additions |
| src/stores/auth.js | +42/-3 | +22/-1 | ours | Union — both added distinct actions |
| docs/plans/README.md | small | small | n/a | Union both tables |
| docs/plans/index.html | regen | regen | n/a | Regenerate from scratch after merge (Task 8) |
| docs/plans/2026-06-07-dashboard-load-performance.md | small | small | n/a | Take both edits; content-only doc |

**Test baselines to compare against:** ours = 121 tests / 11 failures-errors; theirs (per PR #94
notes) = 170 tests / 16 failures-errors, "all pre-existing" per that PR. The combined suite gets a
new baseline recorded in Task 7 — the pass/fail *names* matter, not the counts: no test that
passed on either side may newly fail.

---

### Task 1: Create the integration branch

**Files:** none (git only)

- [x] **Step 1: Verify clean tree** — `git status --short` shows only the four known untracked
  scratch files (`StudyBuddy_Algorithm_Explainer.pptx`, `graphify-out/`, `make_algo_pptx.cjs/.js`).
  Anything else: stop and ask.
- [x] **Step 2: Create branch** — `git switch -c feat/full-system-integration`
  (from `feat/tutee-enrollment-verification` @ `3b9d45a`, one docs-only commit past the measured
  `1c0a075`).
- [x] **Step 3: Safety tag** — `git tag pre-integration-merge-20260702` so the exact pre-merge
  state is trivially recoverable.

### Task 2: Start the merge

**Files:** all; git stops on the 17 conflicts.

- [x] **Step 1:** `git merge feature-cashout-recent-transactions` — conflict set matched the
  17-file table exactly.
- [x] **Step 2:** Confirmed all non-conflicted changes staged cleanly.

### Task 3: Resolve docs + small frontend conflicts (low risk)

**Files:** `docs/plans/README.md`, `docs/plans/2026-06-07-dashboard-load-performance.md`,
`src/components/TutorScreeningModal.vue`, `src/stores/auth.js`, `src/views/AdminUsers.vue`,
`src/stores/admin.js`, `src/views/AdminTutorApplications.vue`, `src/views/TutorApplicationStatus.vue`

- [x] **Step 1:** Resolved per-file. index.html took theirs (regenerated in Task 8). Notable:
  auth.js/admin.js unions; TutorScreeningModal took their design-system button styling; AdminUsers
  took their new `deleteUser`; AdminTutorApplications/TutorApplicationStatus kept our two-role
  dynamic routes/placeholders + their `sb-field` styling.
- [x] **Step 2:** Staged each.
- [x] **Step 3:** `npx oxlint` on the 6 files: 0 errors.

### Task 4: Resolve backend core conflicts (highest risk)

**Files:** `backend/studybuddy/urls.py`, `backend/studybuddy/serializers.py`,
`backend/studybuddy/admin_views.py`, `backend/studybuddy/views.py`, `backend/studybuddy/tests.py`

Resolution order = ascending difficulty, so import errors surface early:

- [x] **Step 1: urls.py** — union both route lists. Our routes: tutee application/renewal/status +
  admin tutee endpoints. Theirs: wallet cash-in/cash-out/recent-cash-outs, superadmin, support
  escalation, check-ins. Every route name from both sides must appear exactly once.
- [x] **Step 2: serializers.py** — our base; re-insert their serializer classes (wallet/top-up,
  withdrawal fields incl. `receiving_institution_*` and `note`, superadmin, support). Delete any
  serializer referencing `TutorPayoutAccount` (model is removed on their side).
- [x] **Step 3: admin_views.py** — their base; re-insert our tutee admin views
  (`AdminTuteeApplicationListView/DetailView`, `AdminTuteeDocumentRenewalDetailView`) and any
  helper they depend on. Cross-check every view referenced from the merged `urls.py` exists.
- [x] **Step 4: views.py** — union by section. Our sections: verification context helpers
  (`get_document_review_context`, `get_role_document_review_context`,
  `get_verification_application`, `can_create_new_booking` + enforcement-date parsing), tutee
  submit/resubmit/renewal endpoints, booking-gate checks inside booking confirm/approve. Their
  sections: wallet cash-in initiate/verify, `recent_cash_outs`, inline-destination cash-out
  validation (`bank_name`, `receiving_institution_id`), institution-scoped
  search/recommendations (`filter_tutors_by_institution` usage), check-ins, support escalation.
  Both sides' booking-confirm/approve edits must coexist — verification gate *and* their
  payment/check-in changes.
- [x] **Step 5: tests.py** — their file as base (they restructured/removed 644 old lines); append
  our added test classes verbatim (verification/booking-gate/tutee-admin suites from commits
  `a22e26d`, `a9cee86`, `cbc67e8`). No test class from either side may vanish.
- [x] **Step 6: Import smoke test** — passed (IMPORT OK). —
  `python -c "import django,os; os.environ.setdefault('DJANGO_SETTINGS_MODULE','backend.settings'); django.setup(); import studybuddy.views, studybuddy.admin_views, studybuddy.serializers, studybuddy.urls"`
  (run from `backend/`). Expected: no `ImportError`/`NameError`/`SyntaxError`.
- [x] **Step 7:** `git add` the five files.

### Task 5: Resolve frontend shell conflicts

**Files:** `src/App.vue`, `src/views/AdminDashboard.vue`, `src/views/TutorProfile.vue`

- [x] **Step 1: App.vue** — took their AppSidebar shell; ported the admin/superadmin "Tutor
  Applications" nav into `AppSidebar.vue` (their menu lacked it); removed a duplicate
  `deferStartupWork` the merge produced. `tutor-application-submitted` public route + inline header
  auto-merged.
- [x] **Step 2: AdminDashboard.vue** — took their redesign; our old-style Tutor Applications
  quick-action card dropped (access preserved via the sidebar nav) rather than force-fit.
- [x] **Step 3: TutorProfile.vue** — their redesign as base; `VerificationStatusCard` import/usage
  intact (auto-merged); removed dead accordion helpers their redesign orphaned.
- [x] **Step 4:** `git add` the three files; `npm run build` succeeded.

### Task 6: Commit the merge + reconcile the migration graph

**Files:** merge commit; possibly new `backend/studybuddy/migrations/0065_merge_*.py` + a
reconciliation migration.

- [x] **Step 1:** merge committed (`dd0758d`) with a resolution-strategy summary.
- [x] **Step 2:** `makemigrations --check --dry-run` reported the expected two-head conflict
  (`0059_alter_platformactivity...` vs `0064_supportticket_escalation`).
- [x] **Step 3:** `makemigrations --merge` created `0065_merge_20260702_1734.py` — dependencies
  only, no operations. Committed (`3cdfb28`).
- [x] **Step 4:** re-ran `makemigrations --check --dry-run` → "No changes detected"; no residual
  model-state drift, no reconciliation migration needed.
- [x] **Step 5 (Gate G1): REPORTED — awaiting user go/no-go.** Applying migrations to the dev DB
  includes `0063_remove_tutorpayoutaccount` (drops the table). Not run.
- [ ] **Step 6 (after G1 yes):** `python manage.py migrate` on dev DB — no errors.
- [x] **Step 7:** migration merge node committed (`3cdfb28`).

### Task 7: Full verification

**Files:** none (checks only)

- [x] **Step 1:** `npm run lint` — clean (0 errors) after removing 2 dead helpers in `Dashboard.vue`
  (`4312ce8`) that the cashout branch carried in as unused.
- [x] **Step 2:** `npm run build` — succeeds.
- [x] **Step 3:** `npx vitest run` — 54/54 pass.
- [x] **Step 4:** Baseline diff done (full suites on all three branches, remote Supabase test DB).
  **Ours (Set A) = 11 fails/errors; Theirs (Set B) = 16; Integration (Set C) = 16.** `C` is
  *identical* to `B` by test name, and 6 of those also appear in `A`. **Merge-defect set
  `C − (A ∪ B)` = EMPTY** — no test that passed on either parent newly fails. The 16 are all
  pre-existing (11 recommender/search — institution-scoped matching + remote-DB env; 3 admin
  analytics; 2 avatar-upload/image). Logs: `scratchpad/{ours,theirs,django}_test.log`.
- [x] **Step 5: Browser pass (focused seam-check, per user scope decision).** Migrated dev DB first
  (only `0064`+`0065` needed — DB was already at `0063`, so the `TutorPayoutAccount` drop had
  happened earlier; Gate G1 was a non-event here). Verified seams where resolutions could have
  silently broken behavior: **login** (`get_login_profile_for_user` in `login_view`+`profile_status`)
  — tutee and admin both log in via OTP and land correctly, `POST /login`, `/login/verify-otp`,
  `/profile/status` all 200; **sidebar Tutor Applications nav** (hand-ported into `AppSidebar.vue`)
  — renders and routes; **AdminTutorApplications** two-role Tutor/Tutee tabs render, endpoint 200;
  **VerificationStatusCard** renders on tutee profile; **admin operational-queue** (import-union
  `AdminOperationalQueueView`) 200. Booking-gate 403 covered by passing `BookingVerificationGateTests`
  in Step 4. No 500s; only transient pre-auth 401s and expected Channels WS errors under `runserver`.
- [x] **Step 6:** Folded into the Step 5 seam-check (targeted, not exhaustive — user-approved scope).
- [x] **Step 7:** One fix-forward applied (`4312ce8`, the dead-helper removal). No other findings.

**Seam-check side effect (dev only):** set a known password + `is_domain_exempt=True` on two trial
accounts (`Tutee1@gmail.com`, `reg2@gmail.com`) to drive the browser flows. Trial data; revert or
reseed at will.

### Task 8: Docs + PR

**Files:** `docs/plans/index.html`, this plan file, session summary; PR.

- [ ] **Step 1:** Set this plan's status to Done; write
  `docs/session-summaries/2026-07-02-full-system-integration-merge-summary.md` (shipped vs
  planned, deviations, checks run + results).
- [ ] **Step 2:** Regenerate `docs/plans/index.html` from scratch per dashboard spec.
- [ ] **Step 3:** `git commit` the docs.
- [ ] **Step 4 (user confirmation required):** push `feat/full-system-integration` and either
  (a) open a new PR "feat: full system integration" superseding #101, or (b) retarget #101 —
  user's choice. PR body: feature inventory from both lines, migration notes (incl. destructive
  `0063` and Gate G1 outcome), checks run with results.

## Risks

- **Silent behavior loss in `views.py`/`tests.py` resolution** — the two highest-churn files.
  Mitigated by: union-by-section strategy, the no-vanishing-test-class rule, import smoke test,
  and the both-baselines test comparison in Task 7 Step 4.
- **`0063_remove_tutorpayoutaccount` is destructive** — gated (G1) before any `migrate`, and again
  before production rollout (out of scope here).
- **Their branch carries ~196 older commits whose features may partially duplicate `main`'s
  history under different hashes** (e.g. dark mode, chat work). The merge resolves this at *file
  state* level — whatever conflicts, we resolve; whatever doesn't, git takes the changed side.
  Residual risk is subtle regressions in areas `main` evolved after their fork; the browser passes
  in Task 7 target exactly those areas.
- **PR #101 scope** — untouched. The integration branch is separate; #101 can merge or wait,
  user's call.
- **Local `main` is stale by 9 commits** — irrelevant here (we measure against `origin/main`), but
  worth a `git fetch` before Task 7 comparisons.

## Checks to run

Summarized from Task 7: `npm run lint`, `npm run build`, `npx vitest run`,
`python manage.py makemigrations --check --dry-run` (post-merge-migration: clean),
`python manage.py test --keepdb` vs union-of-baselines, and the two browser passes (verification
features + cashout-branch features).

## Changelog

- 2026-07-02: Task 7 verified. Three-branch baseline diff (ours 11 / theirs 16 / integration 16)
  shows integration failures == theirs' failures by name; merge-defect set `C − (A ∪ B)` is empty.
  Dev DB migrated to head (`0064`+`0065` only; DB already at `0063`, so Gate G1 was moot).
  Focused browser seam-check passed for login, ported sidebar nav, two-role admin applications,
  VerificationStatusCard, and admin operational-queue (all 200s, no 500s). Set a known password +
  domain-exempt on two trial accounts for the browser drive. Only Task 8 (docs + push/PR) remains.
- 2026-07-02: Tasks 2-6 executed inline. Merge produced exactly the 17-file conflict set; all
  resolved (unions where both added logic; theirs for redesign/design-system surfaces; ours for the
  two-role verification views). `TutorPayoutAccount` dropped from all imports. Import smoke test,
  `npm run build`, `npx vitest run` (54/54), and `npm run lint` (after removing 2 dead helpers the
  cashout branch carried into `Dashboard.vue`) all pass. Merge committed `dd0758d`; migration heads
  reconciled via `0065_merge_20260702_1734.py` (`3cdfb28`) with no residual drift; lint fix
  `4312ce8`. Gate G1 (destructive dev-DB migrate) reported and NOT run. Django test suite running.
- 2026-07-02: Task 1 executed inline (user-approved, task-by-task with checkpoints): clean tree
  verified, `feat/full-system-integration` branched from `3b9d45a`, safety tag
  `pre-integration-merge-20260702` created. Status Draft → In Progress.
- 2026-07-02: Plan written after cherry-pick approach failed (first commit conflicted immediately;
  branch turned out to carry 246 non-merge commits of parallel history, not 50). Facts measured:
  17-file conflict set with per-file dominant sides, disjoint migration chains with two heads, no
  migration filename collisions. Status: Draft, awaiting approval.
