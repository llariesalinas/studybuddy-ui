---
title: Repository cleanup
date: 2026-08-14
status: Approved
summary: Remove stray debug files, quarantine non-code artifacts, delete dead scaffolding, and prune worktrees and merged branches.
spec:
---

# Repository cleanup

## Status & Progress Summary

**Approved — not yet started.** No files have been touched; this plan is the record of a grilling
session, not of work performed.

| Step | State |
| --- | --- |
| 0. Capture baseline | Not started |
| 1. Branch `chore/repo-cleanup` | Not started |
| 2. Delete junk | Not started |
| 3. Quarantine artifacts to `_attic/` | Not started |
| 4. Remove `backend/testapp/` | Not started |
| 5. Delete Vite scaffold | Not started |
| 6. Sweep untracked litter | Not started |
| 7. Prune worktrees and merged branches | Not started |

**Open question blocking step 7:** whether `develop` should be excluded from the merged-branch
deletion (see Risks).

## Goal

Make the working repository fast to navigate and stop stale files from misleading both the
developer and AI assistants. This is working-repo hygiene, not a size reduction or a submission
polish pass: all git history is preserved, no remote is touched, and nothing with future value is
deleted without the owner's say-so.

## Approach

Four decisions shape the whole plan.

**Quarantine over delete for anything with content.** Non-code artifacts (a generated pptx and its
two generator scripts, a Lighthouse report, a stray mockup, a design doc) move to a gitignored
`_attic/` at the repo root rather than being deleted. The repository becomes clean immediately for
anyone cloning it, while the files remain on disk in one place for the owner to sweep at leisure.
Git history retains every one of them regardless.

**Delete outright for accidents and dead one-offs.** `tatusQ` is a redirected `git status` dump,
`backend/{` is a zero-byte botched shell redirect, `script.py` is hardcoded to a path on a
different machine (`C:\Users\Reginald\Documents\ThesisApp\`), and `migration.patch` is an
already-applied diff. Quarantining these would fill the attic with things nobody will ever open.

**Code changes stay minimal and reversible.** `backend/testapp/` is removed from the codebase but
its `testapp_testmessage` table is deliberately left in place in both dev and deployed databases.
Dropping the table would turn a hygiene pass into a schema migration requiring deploy
coordination, for no functional gain — Django ignores an orphaned table entirely.

**Git pruning is local-only and non-destructive.** All 11 worktrees were verified to have zero
uncommitted changes, and removing a worktree does not delete its branch, so every removal is
reversible with `git worktree add`. Branch deletion uses `git branch -d`, which refuses to delete
anything not merged into main. No remote branches are touched.

Work lands as separate commits per category so any single step can be reverted alone.

## Steps

0. **Capture baseline.** Run `npm run build`, `npm run test`, and `python manage.py check` before
   any edit, so pre-existing failures are not misattributed to this pass. Record the results.

1. **Branch.** Create `chore/repo-cleanup` off the current `admin-review-panel-catalog-fixes`.

2. **Delete junk** — commit `chore: remove stray debug and scratch files`
   - Root: `tatusQ`, `script.py`, `migration.patch`, `GEMINI.md`
   - Backend: `backend/{`, `backend/check_settings.py`, `backend/fix_db.py`, `backend/test_err.py`

   `GEMINI.md` is a five-line pointer to `.claude/CLAUDE.md`, which `.gitignore` excludes — so it
   is a dangling reference in any fresh clone. Gemini is not used in this repo (`.gemini/` is
   gitignored too), and `AGENTS.md` already carries the same conventions.

3. **Quarantine artifacts** — commit `chore: move non-code artifacts out of the repo`
   - Create `_attic/` and add it to `.gitignore`
   - `git rm --cached` each file as it moves in:
     `StudyBuddy_Algorithm_Explainer.pptx` (419K), `make_algo_pptx.js` (40K),
     `make_algo_pptx.cjs` (44K), `lighthouse.json` (469K),
     `session-detail-redesign-preview.html` (18K), `StudyBuddyDesign.md` (27K),
     `src/views/SessionsReports.vue` (9.6K)
   - Roughly 1MB total leaves the tracked tree

   `SessionsReports.vue` is included because the router imports `TutorSessionsReports.vue`
   instead, making it a superseded predecessor — but it is 9.6K of hand-written code worth
   diffing against its replacement before it goes.

4. **Remove testapp** — commit `chore: remove dead testapp scaffolding`
   - Delete `backend/testapp/` (10 files)
   - Remove `'testapp'` from `INSTALLED_APPS` at `backend/backend/settings.py:161`

   The app has one model (`TestMessage`), no URLs, and its only view was already deleted in an
   earlier pass with a comment explaining why. `INSTALLED_APPS` is its sole remaining hook.

5. **Delete Vite scaffold** — commit `chore: remove unused Vite scaffold components`
   - `src/components/HelloWorld.vue`, `src/components/TheWelcome.vue`,
     `src/components/WelcomeItem.vue`, `src/components/icons/` (5 files),
     `src/stores/counter.js`

   All verified to have zero imports anywhere in `src/`. These shipped with
   `npm create vue@latest` and were never touched.

6. **Sweep untracked litter** — no commit, nothing here is tracked
   - `docs/graphify-out/` (a stray `.tmp` duplicating the gitignored root `graphify-out/`)
   - The 155 untracked working files in `docs/mockups/sessions/`
   - The 8 root-level `*.log` files
   - `dist/`

7. **Prune git state** — no commit, git metadata only
   - `git worktree remove` all 11 registered worktrees, plus the orphaned
     `.claude/worktrees/fix+verification-approval-email/` directory, which exists on disk but is
     not registered with git
   - `git branch -d` the 16 branches already merged into main

   Worktrees must be removed before branches, since git refuses to delete a branch that is
   checked out in a worktree.

## Explicitly out of scope

- **History rewriting.** `.git` is 53M; purging the large binaries via `filter-repo` is not
  warranted and would require force-push coordination.
- **The 38 unmerged local branches and 49 remote-only branches.** Triaging these needs a separate
  review pass, and remote deletion is irreversible for anyone else on the repo.
- **Tracked `docs/` content.** The 129 plans and 92 session summaries are the project's
  documentation trail, mandated by `CLAUDE.md`. `docs/plans/index.html` already collapses the Done
  group, so navigation is handled.
- **`CONTEXT.md`.** 427 lines of domain glossary — an asset, not clutter.
- **`middleware.js`.** Live Vercel infrastructure (ADR-0005), a no-op when its env vars are unset.
- **`AGENTS.md`.** Kept as the tracked, cross-tool conventions file.

## Risks

- **`develop` is among the 16 merged branches.** Deleting a branch named `develop` is unusual even
  when fully merged; it may be a convention branch worth keeping. Confirm before step 7, or
  exclude it.
- **`_attic/` is gitignored, so its contents live only on disk.** A later `git clean -xdf` would
  remove them from the working tree. History still holds every file, but recovery would mean
  digging through git rather than opening a folder.
- **Removing `'testapp'` from `INSTALLED_APPS` touches Django boot.** `python manage.py check`
  gates this; a failure means the app was more wired-in than the audit found.
- **Deleting scaffold components could break an import the grep missed.** `npm run build` gates
  this — a broken import fails the build loudly.
- **The orphaned `testapp_testmessage` table persists** in dev and deployed databases. Intentional,
  but it will look unexplained to anyone reading the schema later.
- **Worktree removal loses the convenience of parallel checkouts**, not any work. All 11 were
  verified clean, and each is recreatable with `git worktree add <path> <branch>`.

## Checks to run

Run before the first edit to capture a baseline, then again before each commit. All three must
pass:

- `npm run build` — production build succeeds; catches broken imports from the `src/` deletions
- `npm run test` — Vitest suite passes
- `cd backend && python manage.py check` — Django boots; catches an `INSTALLED_APPS` mistake

After step 7, confirm the git state:

- `git worktree list` — only the primary working tree remains
- `git branch | wc -l` — 67 down to 51
- `git status` — clean, with `_attic/` correctly ignored

## Changelog

<!-- Newest first. One line per meaningful alteration to this plan. -->

- **2026-08-14** — Plan created from a grilling session and saved as **Approved**. Decisions
  settled: working-repo hygiene as the goal (no history rewrite, no remote changes); quarantine to
  a gitignored `_attic/` for artifacts with content, outright delete for accidents and one-offs;
  `testapp` removed from code with its DB table deliberately left orphaned; `GEMINI.md` deleted
  rather than repointed; `docs/` limited to untracked litter only; worktrees plus the 16 merged
  branches pruned locally; full build/test/check gate with one commit per category. `develop`'s
  inclusion in the branch deletion left open for confirmation.
