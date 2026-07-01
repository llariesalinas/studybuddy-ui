# StudyBuddy — Session Handoff (2026-07-01)

Handoff for picking this thread back up (same session or a fresh one). Covers: a `/review` of the tutor
registration/screening feature, 5 bug fixes it surfaced (now planned, not yet implemented), and a deferred
larger feature (tutee-side enrollment verification) that should be grilled next.

---

## 1. What happened this session, in order

1. Ran a two-axis `/review` (Standards + Spec) of commit `f23b423` "Fix/revise tutor registration sync main
   (#92)" on `main` — the tutor screening/registration-sync feature (`TutorScreeningModal`,
   submitted/application-status routing, admin tutor-application review, migrations
   `0054_tutorapplication_application_status_idx.py` / `0055_merge_20260617_0142.py`).
2. Found 5 fixable issues (see §2).
3. User asked to also add: tutee-side enrollment verification gating booking access, a 3-month renewal
   cycle, and a dev-mode override to force/test it. This references **GitHub issue #96** ("Add 3-month tutor
   enrollment document re-verification") — but #96 is **tutor-only**; the tutee extension is new scope with
   no existing issue. Searched for "codex"-flagged issues the user mentioned; found none anywhere in the
   repo's issues/PRs/comments (checked #96, PR #92, repo-wide search). User said to skip chasing that down.
4. Grilled sequencing: bugs first, feature-design grilling paused until after the bugfix PR ships.
5. Grilled all 5 bug fixes to specific, locked-in decisions (see §2).
6. **Key discovery mid-session:** the bugs live in `f23b423` on `main`, which is **not an ancestor of**
   `feature-cashout-recent-transactions` (the branch this session started on). That branch diverged from
   `main` at `b773afd`, *before* `f23b423` landed. Verified directly: `MAX_UPLOAD_SIZE`, migration `0054`,
   and the broadened `login_view` except are all absent from `feature-cashout-recent-transactions`. Only the
   resubmit endpoint's missing status-gate (bug #1) is a pre-existing bug common to both branches.
7. User chose (via AskUserQuestion): fix all 5 on a **new branch cut from `origin/main`**, not by merging
   main into the cashout branch. Created `fix/tutor-application-bugfixes` from `origin/main` (fetched fresh;
   confirmed `f23b423` is included). Local `main` branch was stale (behind `origin/main`) — used
   `origin/main` directly, not local `main`.
8. Wrote the plan: `docs/plans/2026-07-01-tutor-application-bugfixes.md` (status: Approved).

**Not yet done:** none of the 5 fixes have been implemented in code. That's the immediate next step.

---

## 2. The 5 bugs — locked-in fix decisions

All on branch `fix/tutor-application-bugfixes` (based on `origin/main`, currently checked out).

| # | Bug | Decision |
|---|---|---|
| 1 | `tutor_application_resubmit` (`views.py:5069`) allows resubmit on `pending`/`approved`, silently reverting an approved tutor to pending | Gate: only allow when `application_status == 'rejected'`. Reject others with 400/403. |
| 2 | `TutorApplication.application_status` (`models.py:324`) missing `db_index=True` that migration `0054_tutorapplication_application_status_idx.py` already applied | Add `db_index=True` to the model field. No new migration — just sync source to migration state. |
| 3 | `MAX_UPLOAD_SIZE = 5 * 1024 * 1024` duplicated in `register_user` (`views.py:746`), `upload_tutee_avatar` (`views.py:3091`), and `MAX_FILE_SIZE` in `TutorScreeningModal.vue:80` | One `MAX_DOCUMENT_UPLOAD_SIZE` in `backend/backend/settings.py` reused by both backend sites; one mirrored constant in `src/config.js` for the frontend (comment noting it must match backend). Rejected a runtime config-fetch endpoint as overkill. |
| 4 | `tutor_application_resubmit` has no upload-size check (register endpoint does) | Add the same size check, using the new shared constant from #3. |
| 5 | `login_view` (`views.py:~1077` on this branch) widened `except TutorApplication.DoesNotExist: pass` to bare `except Exception: logger.exception(...)`, fail-opening login on unexpected errors | Narrow back to `except TutorApplication.DoesNotExist: pass`. Login must fail closed on unexpected errors. |

Full plan with steps/checks: [`docs/plans/2026-07-01-tutor-application-bugfixes.md`](../plans/2026-07-01-tutor-application-bugfixes.md).

---

## 3. Environment gotchas hit this session

- **Stale `.git/index.lock`** blocked `git checkout -b`. No git process was actually running (`tasklist` showed
  nothing); the lock file was 0 bytes. Removed it (`rm -f .git/index.lock`) and the checkout succeeded. This
  matches a gotcha from an earlier handoff (`docs/session-summaries/2026-06-03-handoff.md`) — likely an IDE's
  git integration, recurring.
- **Local `main` branch is stale** — sits at `3f76987`, well behind `origin/main` (`f23b423`). Don't branch
  from local `main`; fetch and branch from `origin/main` instead, or fast-forward local `main` first.
- `rtk`/bash `grep` output through the RTK proxy was garbled/unreliable for multi-match greps this session
  (returned line numbers with no content, mislabeled file counts). The `Grep` tool worked correctly every
  time — prefer it over shelling out to grep for anything beyond a single trivial match.

---

## 4. Deferred: tutee-side enrollment verification (NOT yet designed)

Once the bugfix PR ships, resume grilling this feature. Nothing below is locked in — these are the open
questions to work through, not decisions:

- **What "enrolled" means for a tutee.** Tutees currently have **no document-based verification at all** —
  only email-domain matching (`UserProfile.is_domain_exempt`, checked in `login_view`). `TutorApplication`
  (with `school_id`/`enrollment_proof`) is tutor-only. Building tutee enrollment verification means designing
  a new model/flow from scratch, not extending an existing one. Likely needs its own model (or a generalized
  rename of `TutorApplication`?) — open question.
- **3-month renewal cadence** — for both tutors (per issue #96, tutor-only today) and now tutees per this
  session's ask. Needs: what date field marks "verified as of," how the 3-month check triggers (login-time
  check vs. scheduled job vs. both), what "renewal" requires (same documents as initial verification, or
  lighter-weight), and what happens to in-flight bookings when a tutee/tutor lapses.
  Issue #96 explicitly frames its scope as tutor-only and distinct from the existing resubmission flow — the
  tutee extension has no corresponding issue; consider filing one.
- **Booking block for lapsed tutees** — where the gate lives (route guard? booking-creation endpoint check?
  both?), and the UX for a tutee who's blocked (redirect to a renewal page, banner, etc. — mirroring
  `/application-status` for tutors).
- **Admin review queue for tutee renewals** — does this reuse `AdminTutorApplications.vue`/the admin
  tutor-application store methods, or need a parallel tutee-side surface?
- **Dev-mode override** — user wants to force/test the re-verification flow without waiting 3 months. Needs
  design: an env flag, a settings constant that shortens the interval in dev, an admin/debug endpoint to
  force-expire a given user's verification, or some combination. Not yet discussed in depth.
- Confirmed: no "codex"-authored findings exist anywhere in this repo for this feature — don't chase that
  further unless the user provides a specific source.

Resume by re-invoking `/grill-with-docs` (or plain `/grilling`) with this section as context, once the bugfix
branch is merged or at least stable.

---

## 5. Branch/file map

- **Bugfix work:** branch `fix/tutor-application-bugfixes` (off `origin/main`), currently checked out.
  Files to touch: `backend/backend/settings.py`, `backend/studybuddy/models.py`, `backend/studybuddy/views.py`
  (`tutor_application_resubmit` ~5069, `register_user` ~746, `upload_tutee_avatar` ~3091, `login_view` ~1077),
  `src/config.js`, `src/components/TutorScreeningModal.vue`.
- **Original feature work session started on:** branch `feature-cashout-recent-transactions` — unrelated to
  this bugfix/feature thread, was mid-flight when this session began (cash-out recent transactions, support
  escalation). Not touched this session; switch back to it (`git checkout feature-cashout-recent-transactions`)
  when returning to that work.
- **Untracked, pre-existing, not part of any of this:** `StudyBuddy_Algorithm_Explainer.pptx`,
  `graphify-out/`, `make_algo_pptx.cjs`, `make_algo_pptx.js` — present in `git status` at session start,
  unrelated, left alone.
