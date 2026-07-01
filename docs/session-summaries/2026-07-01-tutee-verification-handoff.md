# Handoff — Tutee Enrollment Verification (design locked, plan not yet written)

**Date:** 2026-07-01
**Branch:** `fix/tutor-application-bugfixes` (see note in §4 — new feature likely wants its own branch off this or off `origin/main` once this branch's PR merges)
**Model in use when this was written:** Opus 4.8

---

## 0. What the next session must do (start here)

The full design for the **tutee enrollment verification** feature was grilled to completion this
session (all decisions locked, §3 below). **No plan files were written yet** — the session was
interrupted right after design sign-off, at the point of writing them.

**Immediate next action:** write the phased plan files, then regenerate the dashboard. Per the user's
argument on the `/handoff` command: **reference this handoff doc's path in the overview plan file** so
context can be cleared and picked back up. This handoff is the sole record of §3's design decisions —
once the plan files exist and capture §3, this doc is redundant.

Proposed files (all in `docs/plans/`, house format `YYYY-MM-DD-<topic>.md`, based on
`docs/plans/_template.md`):
- `2026-07-01-tutee-verification-overview.md` — parent doc: the locked design (§3), the 4-phase map,
  status `Approved`. **Must link to this handoff path.**
- `2026-07-01-tutee-verification-phase1-model.md` — **full detail** (§3 model bullets + migration care).
- `2026-07-01-tutee-verification-phase2-gate.md` — lighter outline.
- `2026-07-01-tutee-verification-phase3-ui.md` — lighter outline.
- `2026-07-01-tutee-verification-phase4-email-devtools.md` — lighter outline.

User conventions to honor (from CLAUDE.md + memory): document-before-code; **one md file per phase,
execute only the current phase, never auto-advance without explicit go-ahead**; every plan carries a
living **Status & Progress Summary** + **Changelog**, updated on every edit; regenerate
`docs/plans/index.html` after any plan change (dark theme, badge row, cards grouped by status, Done
collapsed, `vscode://file/<abs-path>` links). Task list already seeded: tasks #8/#9/#10 cover these.

Write Phase 1 in full; keep Phases 2–4 as outlines that get fleshed out when reached (Phase 1's
abstract-base outcome may reshape them).

---

## 1. This session in order

1. Resumed from `docs/session-summaries/2026-07-01-tutor-application-handoff.md`.
2. **Discovered** an undocumented commit `66c1441` ("Add tutor document renewal review flow") already on
   the branch — a large (~1400-line) feature shipped without a plan. It had incidentally completed 2 of
   the 5 planned bugfixes and reshaped a 3rd. Retro-documented it.
3. Implemented the 4 remaining tutor-application bugfixes and committed. **Done — see §2.**
4. Wrote a test plan for those fixes, handed off to Codex (not implemented here).
5. Grilled the **tutee enrollment verification** feature end to end (17 questions). **Design locked, §3.**
6. Interrupted while about to write the phased plan files → this handoff.

## 2. Bugfix work — DONE, committed (do not redo)

Two commits on `fix/tutor-application-bugfixes`:
- `57480ad` fix: gate tutor resubmission, centralize upload size limit, fail closed on login errors
- `65de9ad` docs: plan and retro-document tutor application bugfix work

Details already captured — **do not duplicate, read these**:
- `docs/plans/2026-07-01-tutor-application-bugfixes.md` (status In Progress; 4 fixes done, 1 was
  pre-done by `66c1441`)
- `docs/plans/2026-07-01-tutor-document-renewal-review.md` (retro-doc of `66c1441`, status Done)
- `docs/plans/2026-07-01-tutor-application-bugfix-tests.md` (test plan handed to Codex, status Approved)

**Open loose ends on the bugfix work** (not blocking the new feature):
- Backend `python manage.py test` never got a clean full run this session — Postgres test DB kept
  getting stuck (stale schema / locked drop / hung teardown). The one completed run showed only
  **pre-existing** failures unrelated to the changes. Recreate the test DB cleanly before trusting it.
- `npm run lint` has 18 pre-existing errors, all in untouched files. `npm run build` passes,
  `makemigrations --check` clean.
- Nothing pushed. No PR opened. User has not asked to push.

## 3. LOCKED DESIGN — tutee enrollment verification (exists only here until plan is written)

Framing throughout: **"tutees and tutors are both students"** → maximize shared code, mirror the tutor
flow, apply rules symmetrically.

**Model**
- Document-based verification for tutees (school ID + enrollment proof), mirroring tutors.
- New **abstract Django base model** holding shared fields + renewal logic
  (`document_renewal_status()`, `can_submit_document_renewal()`, `latest_approved_document_review_at()`,
  the size constant, dedup fields). Refactor existing `TutorApplication` to inherit it; add new
  `TuteeApplication` inheriting it. **Separate tables, one source of logic.** (Chose this over renaming
  `TutorApplication` to a shared concrete model — too risky against freshly-shipped `66c1441` — and over
  fully-separate duplication — drift risk, the exact class of bug just fixed with `MAX_UPLOAD_SIZE`.)
- New dedup fields on the base: `reminder_7day_sent_at`, `reminder_1day_sent_at`, reset on each renewal
  approval.
- **Migration care:** Django abstract bases create no table, so moving fields onto the base is intended
  to be schema-neutral — but Django may emit spurious alter-migrations. This is the riskiest step;
  Phase 1 must verify `makemigrations` produces nothing unexpected for `TutorApplication`.

**Verification & booking gate**
- **Forward-only** for BOTH roles: a lapsed/unverified user keeps existing bookings, wallet, dashboard.
  Only **new booking creation (tutee)** / **accepting new booking requests (tutor)** is blocked.
- This **loosens** the current tutor behavior: today `router/index.js:296-302`
  (`needsTutorApplicationAttention` → global redirect to `/application-status`) is a **full-app lockout**
  on renewal-due tutors. Change it to forward-only (redirect only away from booking/accept surfaces).
- Enforced in **two places** (defense in depth, one shared `can_book`-style check as source of truth):
  route guard (redirect to `/application-status` via CTA / booking-block, NOT global lockout) + a
  **server-side check** at the booking-create endpoint (`POST bookings/confirm/`) and the tutor
  accept-booking-request endpoint.
- **New (never-approved) `pending` tutors stay hard-blocked at login** — unchanged (`login_view`).
  "Lapsed after being verified" is a different state from "never verified."
- **New tutees: register free, gate at first booking** (NOT blocked at signup). Consistent with the
  booking-time gate; avoids a second enforcement point and meshes with the grace period below.

**Renewal cadence & rollout**
- 90-day renewal for tutees too (same `DOCUMENT_RENEWAL_INTERVAL_DAYS = 90`, inherited).
- Countdown/clock anchored to **most recent approved verification date** (existing
  `latest_approved_document_review_at()` — no new date field).
- **Existing tutees: 30-day global grace-period cutover** before enforcement kicks in (new setting, e.g.
  `TUTEE_VERIFICATION_GRACE_PERIOD_DAYS = 30`; single global cutover, NOT per-account). Open impl detail:
  cutover date as settings constant vs DB field — decide in Phase 2.
- **In-flight bookings when someone lapses: untouched** (option A). Lapse only blocks *new* work; paid,
  committed sessions proceed. Same for both roles.

**UI**
- **Generalize `/application-status`** (`TutorApplicationStatus.vue`) to serve both roles for
  submit/resubmit. Entry via CTA / booking-block for both (no more global lockout after the Phase 2
  loosening).
- **Verification card on BOTH `TuteeProfile.vue` and `TutorProfile.vue`:** "Renewed ✓" + countdown to
  next renewal. Use `.sb-card` / `.sb-badge` local patterns + `--sb-*` CSS custom properties (per
  `.claude/skills/shadcn-components.md` and `App.vue`); **no hardcoded colors**.
- **Generalize the admin queue** (`AdminTutorApplications.vue`) with a **tutor/tutee role tab**.
- **Admin renewal-status visibility (read-only for regular admins):** the admin queue gets a **renewal
  status column + filter** (`verified` / `due` / `pending` / `rejected` / `lapsed`) across ALL users of
  both roles with the due date — not just rows with a pending submission. Backend:
  `AdminTutorApplicationListView` exposes computed `document_renewal_status` + due date in the list
  serializer and accepts an optional status query filter. Same status on the admin per-user detail.
  Regular admins act ONLY through the existing review-a-submission flow (approve/reject a real
  submission) — no manual "mark verified" / force-expire (those are dev-only SuperAdmin, below).

**Email** (generalize existing `send_application_*_email` functions to take the application object +
role/label; this ALSO fixes a real gap found in `66c1441`: `AdminTutorDocumentRenewalDetailView.patch`
at `admin_views.py:531` currently sends **no email** on renewal approve/reject).
- Event-driven: **received, approved, rejected** (3 states).
- **Reminders: 7-day + 1-day before renewal due**, via **opportunistic check** (NO scheduler): piggyback
  on the profile-status code path that already computes `document_renewal_status()` — when status is read
  and the user is inside a reminder window and the matching dedup field is null, enqueue the reminder via
  the existing `async_task` path and stamp the field. Accepted tradeoff: a user who never logs in during
  their window isn't reminded until they return (they're not booking anyway under forward-only).
- Infra note: project has **django-q2** (`Q_CLUSTER`, `async_task` in `mailer.py`) for off-thread email,
  but **no scheduled/cron tasks configured** — deliberately avoided adding a scheduler. Also note the
  app-level `EMAIL_SEND_CAP_PER_HOUR = 10` throttle (settings.py:265); irrelevant for a demo (user: "it's
  for a demo anyways we can just change our provider down the line"). Mail is SMTP via Gmail app password
  (500/day free, 2000/day Workspace) or Resend via Anymail — NOT the Gmail API.

**Dev-only tooling (SuperAdmin, BACKEND-gated, not just UI-hidden)**
- On the per-user detail offcanvas in `SuperAdminUsers.vue` (`selectedUser`, opened via `openDetail`,
  has precedent action `toggleSuspension`): buttons to **send each email** (received / approved /
  rejected / 7-day / 1-day) to that user, and **force-expire** that user's verification.
- Force-expire + on-demand reminder send are the **demo mechanism** — 90-day/30-day windows never elapse
  during a live demo, so this is how lapse and reminders get shown.
- **Gate dev-only** via a flag enforced server-side (e.g. `DEBUG`-derived or a dedicated
  `VITE_ENABLE_DEV_TOOLS` mirrored to backend). Client-side hiding alone is insufficient — the endpoint
  itself must reject when the flag is off (it sends real, possibly-false status emails to real users).

## 4. Phasing (each phase independently testable, leaves app working)

1. **Phase 1 — Model & backend foundation:** abstract base refactor of `TutorApplication`, new
   `TuteeApplication`, migrations (verify schema-neutral), dedup fields, expose
   `document_renewal_status` broadly. Riskiest; validate in isolation first. **Write in full detail.**
2. **Phase 2 — Booking gate & forward-only:** loosen tutor guard → forward-only for both; server-side
   checks at booking-create + tutor accept-request endpoints; grace-period cutover logic. Outline.
3. **Phase 3 — UI surfaces:** generalized `/application-status`; verification card on both profiles;
   generalized admin queue with role tab + read-only renewal-status column/filter. Outline.
4. **Phase 4 — Email & dev tools:** generalize `send_application_*` (fixes tutor-renewal email gap);
   opportunistic 7-day/1-day reminders; dev-only SuperAdmin send-email + force-expire. Outline.

**Branch decision to make:** this feature is large and logically distinct from the bugfixes sitting on
`fix/tutor-application-bugfixes`. Recommend confirming with the user whether to (a) open the bugfix PR
first and branch the feature off `origin/main` after merge, or (b) start the feature on a new branch now.
Do not start feature code on the bugfix branch without deciding.

## 5. Key code references (verified this session)

- `backend/studybuddy/models.py`: `TutorApplication` L240+ (`STATUS_CHOICES` L243, `application_status`
  L266 with `db_index=True`, renewal methods L285–324, `DOCUMENT_RENEWAL_INTERVAL_DAYS=90` L241);
  `TutorDocumentRenewalReview` L330+.
- `backend/studybuddy/views.py`: `login_view` L844 (tutor hard-block L879-887); `register_user` L729+;
  `tutor_application_resubmit` L4436 (approved→renewal branch, rejected-only gate, size check);
  `create_tutor_document_renewal_submission` L4521; profile-status context builder ~L142-174
  (`document_renewal_status`, `document_renewal_required`, etc. — the opportunistic-reminder hook point).
- `backend/studybuddy/admin_views.py`: `AdminTutorApplicationListView` L426, `...DetailView` L469
  (patch L479), `AdminTutorDocumentRenewalDetailView` L514 (patch L531 — **no email sent: the gap**).
- `backend/studybuddy/mailer.py`: `async_task` usage L181/187; `email_utils.py`:
  `send_application_approved_email` / `send_application_rejected_email` (generalize these).
- `src/router/index.js`: renewal guard L287-302 (`needsTutorApplicationAttention` → `/application-status`
  redirect — the full-lockout to loosen).
- `src/views/SuperAdminUsers.vue`: detail offcanvas L120+, `selectedUser` L195, `openDetail` L239,
  `toggleSuspension` L173 (precedent for the dev buttons).
- `backend/backend/settings.py`: `MAX_DOCUMENT_UPLOAD_SIZE` (added this session, ~L249),
  `EMAIL_SEND_CAP_PER_HOUR` L265, `Q_CLUSTER` L276, `django_q` L115.

## 6. Environment gotchas (recurring on this machine)

- **Stale `.git/index.lock`** blocks git repeatedly. No real git process holds it (short-lived
  `git.exe` PIDs cycle — IDE/hook polling). `rm -f .git/index.lock` clears it. Hit 3rd time this session.
- **Postgres `test_postgres` DB gets stuck** across runs (stale schema / locked drop / hung teardown).
  `--keepdb` reuses a stale schema (missing tables); plain run prompts interactively (needs `yes`);
  `yes | ...` sends `y` not the literal `yes` Django wants (`yes "yes" | ...`). Recreate the DB cleanly
  before trusting backend test output.
- Prefer the `Grep`/`Read` tools over shelling `grep`/`cat` through the RTK proxy (garbled multi-match
  output). `python manage.py` must run from `backend/` not `backend/backend/`.

## 7. Untracked, pre-existing, leave alone

`StudyBuddy_Algorithm_Explainer.pptx`, `graphify-out/`, `make_algo_pptx.cjs`, `make_algo_pptx.js` —
present since before this thread, unrelated, not staged.

## 8. Suggested skills for the next session

- **`superpowers:writing-plans`** — to write the phased plan files from §3/§4 (design is already locked;
  no need to re-brainstorm or re-grill).
- **`feature-planner`** (project skill) — the studybuddy-specific pipeline for Vue 3 + Django features;
  appropriate if the user wants it to drive plan → spec → implementation. Note it bundles brainstorming,
  which is already done — steer it to the planning/spec stage, not rediscovery.
- **`superpowers:executing-plans`** — once Phase 1's plan is written and approved, to implement it with
  review checkpoints. Respect the "one phase at a time, no auto-advance" rule.
- Do **not** re-run brainstorming/grilling for this feature — the design in §3 is signed off.
- If the user pivots to shipping the bugfixes: **`superpowers:finishing-a-development-branch`**.
