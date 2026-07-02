# Handoff — Tutee Enrollment Verification, Phase 4 next

**Date:** 2026-07-02
**Branch:** `feat/tutee-enrollment-verification` (3 commits ahead of `main`, clean working tree, nothing
pushed, no PR opened)

---

## 0. What the next session must do (start here)

Phases 1-3 of the tutee enrollment verification feature are **Done, tested, browser-verified, and
committed**. Phase 4 (email & dev tools) is the last phase — its outline is written but **not yet fleshed
out into full detail**, per this project's "flesh out only once the previous phase lands" convention.

**Immediate next action:**
1. Read [`docs/plans/2026-07-01-tutee-verification-phase4-email-devtools.md`](../plans/2026-07-01-tutee-verification-phase4-email-devtools.md)
   — the outline (Approach/Risks/Checks) is already written; flesh it out into the same level of detail
   Phases 1-3 have (see those files for the expected shape: numbered Approach steps with exact
   file/line/function references, explicit scope decisions, Checks to run).
2. Implement with TDD (tests first, mirroring the pattern used in every prior phase).
3. Run the full suite, browser-verify (this phase is UI-touching via `SuperAdminUsers.vue`), run
   `/code-review`, commit.
4. Update `docs/plans/2026-07-01-tutee-verification-overview.md` (checklist + changelog), `docs/plans/README.md`,
   and regenerate `docs/plans/index.html` (dark theme dashboard) — every phase file's own changelog shows the
   exact pattern to follow.

No design decisions are outstanding for Phase 4 — the outline below is what's locked. Don't re-brainstorm.

## 1. This session in order

1. Resumed from the prior handoff, which had the tutee-verification design locked (17 decisions) but no
   plan files written yet.
2. Wrote the overview + 4 phase plan files from that locked design.
3. Implemented and shipped Phases 1, 2, and 3 in full — each with: a detailed plan written before code,
   TDD, a full backend-suite run, `/code-review` (8-angle finder + verify), and a commit. See each phase's
   own plan file for its complete changelog — they're the authoritative record, not repeated here.
4. Along the way: fixed a live bug in `docs/plans/index.html`'s dashboard link (was pointing at an OS temp
   file instead of the repo), caught and stripped an unwanted `Co-Authored-By: Claude` trailer the
   build-commit hook had added to an early commit (squashed before it caused problems), and found two real
   gaps during browser verification that unit tests hadn't caught (see §3 Phase 3).

## 2. Work done — DONE, committed (do not redo)

Three commits on `feat/tutee-enrollment-verification`, one per phase:

- `a22e26d` **Phase 1** — abstract base models (`ApplicationVerificationBase`, `DocumentRenewalReviewBase`),
  `TutorApplication` refactored onto them (byte-identical behavior, verified), new `TuteeApplication` /
  `TuteeDocumentRenewalReview`. No user-facing behavior change.
- `a9cee86` **Phase 2** — server-side `can_create_new_booking` gate on tutee booking-creation and tutor
  accept-request; tutor router lockout narrowed to forward-only (renewal-lapse no longer locks out the
  whole app); env-driven grace-period cutover, unset/inactive by default.
- `cbc67e8` **Phase 3** — mirrored Tutee serializers/admin views/endpoints; `profile_status` generalized via
  `get_role_document_review_context`; `/application-status` generalized to both roles (including a genuine
  first-submission path — tutees don't submit at registration like tutors do); new shared
  `VerificationStatusCard.vue` on both profile views; admin queue Tutor/Tutee role tab; the tutee router
  gate Phase 2 deferred is now wired in.

Each phase's plan file (`docs/plans/2026-07-01-tutee-verification-phase{1,2,3}-*.md`) has a full
`Changelog` documenting exact scope decisions, what was found/fixed during review or browser verification,
and the checks run. **Read those instead of re-deriving this context.**

**Open loose ends (not blocking Phase 4):**
- Nothing pushed, no PR opened — user hasn't asked.
- A follow-up chip was spawned (not yet acted on) for a **pre-existing** bug found while touching
  `TutorProfile.vue`'s "Verified" badge: `src/views/TutorDetails.vue` (the public tutor-browsing page
  tutees see) still shows that badge unconditionally. Not a security gap (booking gate is enforced
  server-side regardless), but a trust-signal inaccuracy. Needs a design call (should granular renewal
  status be exposed to public browsing at all?) before fixing — flagged as its own task, not part of this
  feature's phases.
- Backend dev DB needed a manual `python manage.py migrate` mid-session (see §4) — already done, current.

## 3. Key gotchas discovered this session (save yourself the rediscovery)

- **`git status`/`git add` intermittently fail with a stale `.git/index.lock`.** No real git process holds
  it (confirmed via `Get-Process git`). `rm -f .git/index.lock` clears it safely. Hit repeatedly.
- **Bash `cd` keeps resetting to `backend/` or `backend/backend/` unpredictably** across tool calls in this
  environment — always `pwd` before running `python manage.py ...`, or use an absolute `cd` path. Cost real
  time this session (background test runs silently ran from the wrong directory and produced empty logs
  more than once).
- **`grep`/`rg` via the RTK shell proxy garbles multi-match output** (shows byte offsets instead of content).
  Use the `Grep` tool, never shell `grep`, for anything with >1 match.
- **The dev Postgres DB and the test Postgres DB are separate and can drift.** Phase 2 discovered the dev DB
  had never had a migration applied that the test DB (via `--keepdb`) already had. Run `python manage.py
  migrate` against the dev DB explicitly before any browser verification session, don't assume it's current.
- **Backend test suite takes ~5 minutes.** Always run it via `run_in_background` + wait for the completion
  notification (or `ScheduleWakeup`), never block synchronously.
- **11 pre-existing, unrelated test failures/errors are the baseline** — `ChatFeatureTests` (2),
  `EmailAuthTests` (2), `RecommendTutorsViewTests` (7 errors, a pre-existing `Tutor.objects.exclude(id__in=...)`
  FieldError bug in `get_recommendation_candidate_tutors`). Confirmed via `git stash` against clean `HEAD`
  in Phase 1 — not caused by this feature. Any full-suite run should match this exact count; anything more
  is a real regression.
- **Browser verification needs real dev-seeded accounts** (no throwaway test users exist). Password resets
  via `python manage.py shell` are one-way — can't restore the original hash. Low-risk on a local dev DB,
  but always clean up any *data* you create (test applications, activity log rows) even though passwords
  can't be restored.
- **Admin role-tab buttons in `AdminTutorApplications.vue` share CSS classes with inactive-tab styling** —
  don't `click()` by class selector (e.g. `.btn-sm.btn-light.rounded-pill` matches multiple buttons); match
  by exact `textContent` instead when driving the browser.

## 4. Environment state

- Dev DB: migrated and current as of this session (migration `0059_alter_platformactivity_activity_type`
  applied). Backend dev server config: `studybuddy-backend` in `.claude/launch.json` (port 8000). Frontend:
  `studybuddy-ui` (port 5173, Vite).
- `TUTEE_VERIFICATION_ENFORCEMENT_START_DATE` env var is unset in this environment (grace period never
  ends) — intentional default; only set it explicitly in tests via `@override_settings`.

## 5. Untracked, pre-existing, leave alone

`StudyBuddy_Algorithm_Explainer.pptx`, `graphify-out/`, `make_algo_pptx.cjs`, `make_algo_pptx.js` — present
since before this feature work, unrelated, not staged.

## 6. Suggested skills for the next session

- **`superpowers:writing-plans`** or just direct editing — to flesh out Phase 4's outline into full detail
  (mirroring Phases 1-3's plan files as the template). Design is locked; nothing to re-brainstorm.
- **`superpowers:executing-plans`** or **`superpowers:test-driven-development`** — once Phase 4's plan is
  fleshed out, to implement it TDD-first with the same rigor as prior phases.
- **`/code-review`** — after implementation, same 8-angle process used every phase so far. Expect a high
  false-positive rate on `getattr`/OneToOneField and serializer-duplication claims specifically — both have
  been independently raised and refuted with direct evidence (passing tests, Django internals) in every
  phase's review so far; verify against actual code/tests before accepting any finding, don't take agent
  claims at face value.
- **`superpowers:finishing-a-development-branch`** — once Phase 4 ships, to decide whether to open a PR
  (branch has never been pushed).
