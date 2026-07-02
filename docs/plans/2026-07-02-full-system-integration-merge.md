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

**Status: In Progress — Task 1 complete.** Branch `feat/full-system-integration` created from
`3b9d45a` (one docs-only commit ahead of the measured `1c0a075`); safety tag
`pre-integration-merge-20260702` set. All facts below (conflict list, dominant sides, migration
chains) were measured against the real branches on 2026-07-02, not assumed.

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

- [ ] **Step 1:** `git merge feature-cashout-recent-transactions` — expect
  "Automatic merge failed; fix conflicts and then commit the result." with exactly the 17 files
  above in `git diff --name-only --diff-filter=U`. If the set differs from the table, update this
  plan's table before resolving anything.
- [ ] **Step 2:** Confirm all non-conflicted changes staged cleanly: `git status` shows the
  conflicts as "both modified" and everything else staged.

### Task 3: Resolve docs + small frontend conflicts (low risk)

**Files:** `docs/plans/README.md`, `docs/plans/2026-06-07-dashboard-load-performance.md`,
`src/components/TutorScreeningModal.vue`, `src/stores/auth.js`, `src/views/AdminUsers.vue`,
`src/stores/admin.js`, `src/views/AdminTutorApplications.vue`, `src/views/TutorApplicationStatus.vue`

- [ ] **Step 1:** For each, open the conflict, apply the per-file strategy from the table (dominant
  side as base, re-apply the other side's delta). For `docs/plans/index.html`, resolve arbitrarily
  (it gets regenerated in Task 8).
- [ ] **Step 2:** After each file: `git add <file>`.
- [ ] **Step 3:** Sanity: `npx oxlint src/stores/auth.js src/stores/admin.js` (or full
  `npm run lint` once at the end of the task) — no *new* errors vs the known-18 baseline.

### Task 4: Resolve backend core conflicts (highest risk)

**Files:** `backend/studybuddy/urls.py`, `backend/studybuddy/serializers.py`,
`backend/studybuddy/admin_views.py`, `backend/studybuddy/views.py`, `backend/studybuddy/tests.py`

Resolution order = ascending difficulty, so import errors surface early:

- [ ] **Step 1: urls.py** — union both route lists. Our routes: tutee application/renewal/status +
  admin tutee endpoints. Theirs: wallet cash-in/cash-out/recent-cash-outs, superadmin, support
  escalation, check-ins. Every route name from both sides must appear exactly once.
- [ ] **Step 2: serializers.py** — our base; re-insert their serializer classes (wallet/top-up,
  withdrawal fields incl. `receiving_institution_*` and `note`, superadmin, support). Delete any
  serializer referencing `TutorPayoutAccount` (model is removed on their side).
- [ ] **Step 3: admin_views.py** — their base; re-insert our tutee admin views
  (`AdminTuteeApplicationListView/DetailView`, `AdminTuteeDocumentRenewalDetailView`) and any
  helper they depend on. Cross-check every view referenced from the merged `urls.py` exists.
- [ ] **Step 4: views.py** — union by section. Our sections: verification context helpers
  (`get_document_review_context`, `get_role_document_review_context`,
  `get_verification_application`, `can_create_new_booking` + enforcement-date parsing), tutee
  submit/resubmit/renewal endpoints, booking-gate checks inside booking confirm/approve. Their
  sections: wallet cash-in initiate/verify, `recent_cash_outs`, inline-destination cash-out
  validation (`bank_name`, `receiving_institution_id`), institution-scoped
  search/recommendations (`filter_tutors_by_institution` usage), check-ins, support escalation.
  Both sides' booking-confirm/approve edits must coexist — verification gate *and* their
  payment/check-in changes.
- [ ] **Step 5: tests.py** — their file as base (they restructured/removed 644 old lines); append
  our added test classes verbatim (verification/booking-gate/tutee-admin suites from commits
  `a22e26d`, `a9cee86`, `cbc67e8`). No test class from either side may vanish.
- [ ] **Step 6: Import smoke test** —
  `python -c "import django,os; os.environ.setdefault('DJANGO_SETTINGS_MODULE','backend.settings'); django.setup(); import studybuddy.views, studybuddy.admin_views, studybuddy.serializers, studybuddy.urls"`
  (run from `backend/`). Expected: no `ImportError`/`NameError`/`SyntaxError`.
- [ ] **Step 7:** `git add` the five files.

### Task 5: Resolve frontend shell conflicts

**Files:** `src/App.vue`, `src/views/AdminDashboard.vue`, `src/views/TutorProfile.vue`

- [ ] **Step 1: App.vue** — their AppSidebar-based shell is the base. Re-apply our +22 lines
  (identified via `git diff b773afd..1c0a075 -- src/App.vue`): whatever of it isn't already
  represented in their shell (e.g. nav entries for `/application-status`, toast usage) gets ported
  into `AppSidebar.vue` instead if the nav moved there.
- [ ] **Step 2: AdminDashboard.vue** — their redesign as base; re-apply our +10 lines (same
  identification method).
- [ ] **Step 3: TutorProfile.vue** — their redesign as base; re-wire our `VerificationStatusCard`
  import/usage and the conditional "Verified" badge from `cbc67e8`.
- [ ] **Step 4:** `git add` the three files; `npm run build` — must succeed (build failures here
  are almost always a missed import or duplicate template block from resolution).

### Task 6: Commit the merge + reconcile the migration graph

**Files:** merge commit; possibly new `backend/studybuddy/migrations/0065_merge_*.py` + a
reconciliation migration.

- [ ] **Step 1:** `git commit` (default merge message + one-line summary of resolution strategy).
- [ ] **Step 2:** `python manage.py makemigrations --check --dry-run` — expected: complaint about
  conflicting heads (`0059_alter_platformactivity...` vs `0064_supportticket_escalation`).
- [ ] **Step 3:** `python manage.py makemigrations --merge` — creates `0065_merge_*.py`. Read it:
  it must contain only `dependencies`, no operations.
- [ ] **Step 4:** `python manage.py makemigrations` again — if model-state drift remains (e.g.
  both sides altered the same field's choices), it emits a small reconciliation migration; read it
  and confirm it's state-only or trivially additive before accepting.
- [ ] **Step 5 (Gate G1):** STOP. Report to user: applying migrations to the local dev DB includes
  `0063_remove_tutorpayoutaccount` (drops the table). Proceed against local dev DB only on
  explicit yes. Production rollout of this migration is a separate, later decision.
- [ ] **Step 6 (after G1 yes):** `python manage.py migrate` on dev DB — no errors.
- [ ] **Step 7:** `git add backend/studybuddy/migrations/ && git commit -m "chore: merge migration heads after full-system integration"`.

### Task 7: Full verification

**Files:** none (checks only)

- [ ] **Step 1:** `npm run lint` — compare against pre-merge baseline (18 pre-existing errors in
  untouched files); no new errors in files this merge resolved.
- [ ] **Step 2:** `npm run build` — succeeds.
- [ ] **Step 3:** `npx vitest run` — all frontend tests pass (both sides' test files present).
- [ ] **Step 4:** `python manage.py test --keepdb` (~5-10 min) — record the combined baseline:
  every test that passed on either branch still passes. Known-acceptable failures: the union of
  ours (11) and theirs (16) *pre-existing* sets, deduplicated; anything outside that union is a
  merge defect — fix before proceeding.
- [ ] **Step 5: Browser pass, ours:** tutee first-submission on `/application-status`; admin queue
  Tutor/Tutee tabs approve/reject; `VerificationStatusCard` on both profiles; booking gate 403
  when enforced-and-unverified. (Full script:
  `docs/artifacts/2026-07-02-tutee-verification-manual-test-guide.html`.)
- [ ] **Step 6: Browser pass, theirs:** tutor wallet cash-in initiate/verify; cash-out modal with
  inline destination + recent-transactions shortcuts + unrecognized-destination confirmation;
  sidebar collapse/persist + dark mode; admin dashboard operational queue; institution-scoped Find
  Tutors results; superadmin session details.
- [ ] **Step 7:** Fix-forward any findings as small `fix:` commits on the integration branch.

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

- 2026-07-02: Task 1 executed inline (user-approved, task-by-task with checkpoints): clean tree
  verified, `feat/full-system-integration` branched from `3b9d45a`, safety tag
  `pre-integration-merge-20260702` created. Status Draft → In Progress.
- 2026-07-02: Plan written after cherry-pick approach failed (first commit conflicted immediately;
  branch turned out to carry 246 non-merge commits of parallel history, not 50). Facts measured:
  17-file conflict set with per-file dominant sides, disjoint migration chains with two heads, no
  migration filename collisions. Status: Draft, awaiting approval.
