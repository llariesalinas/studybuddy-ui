---
title: Verification dev tools — self-service profile-page debug panel
date: 2026-07-02
status: Approved
spec: 2026-07-01-tutee-verification-overview.md
---

# Verification Dev Tools — self-service profile-page debug panel

> Design settled via a grilling session on 2026-07-02 (7 questions, all resolved). Shares its
> backend state-manipulation helper with the SuperAdmin tools drafted in
> [Phase 4](2026-07-01-tutee-verification-phase4-email-devtools.md) — Phase 4 should import the
> helper this plan creates rather than reimplement `force_expire`.

<!-- LIVING SUMMARY: keep this section and the Changelog current on every edit -->
## Status & Progress Summary

**Status: Approved — design locked via grilling, not yet implemented.** Every decision below was
made explicitly with the user; file/line references were read against current `HEAD` on 2026-07-02.

## Goal

Give developers a `VERIFICATION_DEV_TOOLS_ENABLED`-gated, self-service panel on the tutee and tutor
profile pages to exercise enrollment verification without waiting out the real 90-day clock or
going through admin approval: jump their own account between all 7 verification states, toggle the
(tutee) booking-gate enforcement at runtime, and read their live verification state.

## Approach

Three capabilities on a plain collapsible `DEV` panel rendered below `VerificationStatusCard`,
visible only in dev builds; all mutation is server-gated and self-only.

1. **State jumper (both roles).** Deterministic "set my state = X" for all 7 states the card
   renders (`not_submitted`, `initial_pending`, `initial_rejected`, `verified`, `renewal_due`,
   `renewal_pending`, `renewal_rejected`). Each button makes the caller's own application *exactly*
   that state idempotently — sets `application_status`, stamps/backdates `reviewed_at`, wipes
   conflicting `*DocumentRenewalReview` rows and fabricates the one required (synthetic row, empty
   file fields — ORM-legal since `school_id`/`enrollment_proof` are plain File/ImageFields).
   `not_submitted` deletes the application. Reuses `get_verification_application(profile)`.
2. **Enforcement toggle (tutee only).** A three-state runtime override of
   `tutee_verification_enforced()` — *force on* (see the 403 fire), *force off* (book freely),
   *clear* (use the real env date). Cache-based (Redis), consulted **only** when the dev flag is on.
   Tutor gate has no global grace period, so this control is tutee-only; the tutor panel notes that
   its gate is state-driven (use the state jumper → `renewal_due` to block, `verified` to unblock).
3. **Live readout.** Show the raw truth: `application_status`, `document_renewal_status()`,
   `document_renewal_due_at`, and `enforced?` (+ current override) so the tester sees exactly what
   state they are in, not just the card's interpretation.

**Gating & safety.** Reuse a single flag `VERIFICATION_DEV_TOOLS_ENABLED` (added to `settings.py`
now; Phase 4 also consumes it). Endpoints are `IsAuthenticated` and check the flag **first** →
403 when off, before any query, so they are inert in prod even for a valid token. They only ever
mutate `request.user`'s own application. The frontend renders the panel only when
`import.meta.env.DEV`; the server flag is the real guard.

**Shared helper.** New module `backend/studybuddy/_verification_dev.py` holds the state-setter and
the backdate/`force_expire` logic + the cache-override get/set/clear. Both this plan's views and
Phase 4's `AdminUserVerificationDevToolsView` import it (Phase 4 plan updated to point here).

## Steps

1. **Settings** — add `VERIFICATION_DEV_TOOLS_ENABLED = env_bool('VERIFICATION_DEV_TOOLS_ENABLED',
   False)` near the other `env_bool` flags (`settings.py:22-35`). Document it in `backend/.env.example`.
2. **Shared helper** `backend/studybuddy/_verification_dev.py`:
   - `set_verification_state(profile, state)` — deterministic setter for the 7 states, role-generic
     via `get_verification_application` + each role's concrete `*Application` / `*DocumentRenewalReview`
     model. `@transaction.atomic`. Synthetic renewal rows use empty files, `reviewed_by=None`.
     `renewal_due` backdates the clock 91 days (the reusable `force_expire` bit).
     `not_submitted` deletes the application.
   - `enforcement_override_get() / _set(value) / _clear()` — cache-based, key e.g.
     `dev:tutee_verification_enforced`; value `True`/`False`/absent.
3. **Wire the override into the gate** — in `tutee_verification_enforced()` (`views.py:221-239`),
   short-circuit at the top: `if settings.VERIFICATION_DEV_TOOLS_ENABLED:` read the override; if not
   `None`, return it; else fall through to today's env-date logic (prod path byte-identical when
   flag off).
4. **Endpoints** (`views.py`, function-based, `@permission_classes([IsAuthenticated])`, flag-first
   403):
   - `GET  dev/verification/` → readout dict.
   - `POST dev/verification/set-state/` `{ "state": "<one of 7>" }` → set + return readout; 400 on
     bad state.
   - `POST dev/verification/enforcement/` `{ "mode": "on"|"off"|"clear" }` → set/clear override.
   Register in `urls.py` (unconditionally; the flag-first 403 is the gate, matching Phase 4's design).
   Log a `PlatformActivity` row per mutation, like other state changes.
5. **Frontend service** — `src/services/api/verificationDev.js` (centralized per the services rule):
   `getState()`, `setState(state)`, `setEnforcement(mode)`.
6. **Panel component** `src/components/VerificationDevPanel.vue` — collapsible `<details>` "DEV:
   Verification" with: 7 state buttons, a tutee-only 3-way enforcement control, and the readout;
   calls the service then `profileStore.checkProfileStatus()` to refresh the card. Props: `role`.
7. **Mount** below `<VerificationStatusCard />` in `TuteeProfile.vue:64` and `TutorProfile.vue:63`,
   wrapped `v-if="isDev"` (`import.meta.env.DEV`), passing `role`.
8. **Phase 4 cross-reference** — add a note to the Phase 4 plan that `force_expire` + state logic
   now live in `_verification_dev.py`; its `AdminUserVerificationDevToolsView` should import them.

## Risks

- **Destructive to real rows** — the setter overwrites/deletes the caller's application + renewal
  rows. Acceptable (dev/trial data, self-only, flag-gated); re-submit rebuilds. Not reachable in
  prod (flag defaults `False`, checked before any work).
- **Cache-flush resets the enforcement override** — harmless; reverts to the env default. Documented
  in the readout so the tester isn't surprised.
- **`tutee_verification_enforced()` is on a hot path** — the override read is guarded by the flag
  check, so prod does zero extra work; dev does one cache read.
- **Empty-file synthetic rows** — valid at the ORM layer but would fail serializer/form validation
  if some other code path re-saves them through a serializer; the dev states are display/gate-only,
  so acceptable. Note it near the helper.

## Checks to run

- `python manage.py test studybuddy` — new tests: each of the 7 `set_verification_state` outcomes
  yields the expected `application_status` + `document_renewal_status()`; enforcement override
  on/off/clear flips `tutee_verification_enforced()`; endpoints 403 when
  `VERIFICATION_DEV_TOOLS_ENABLED` is off even for an authenticated user; 400 on bad state. Baseline:
  no new failures vs the known pre-existing set.
- `python manage.py makemigrations --check --dry-run` — clean (no schema change; helper + cache only).
- `npm run lint` and `npm run build` — pass.
- Browser (with `VERIFICATION_DEV_TOOLS_ENABLED=True`): on a tutee, click each state → card updates
  to match; set enforcement *on* while `renewal_due`/unverified → booking-confirm returns 403; set
  *off* → booking allowed. Repeat state jumps on a tutor profile.

## Changelog

- 2026-07-02: Plan written straight out of a grilling session (7 resolved decisions: separate
  self-service panel sharing a Phase 4 helper; 3 capabilities; reuse `VERIFICATION_DEV_TOOLS_ENABLED`
  self-only; both roles with tutee-only enforcement toggle; cache-based 3-state override;
  deterministic overwrite setter; no mockups). Status Approved, awaiting go-ahead to implement.
