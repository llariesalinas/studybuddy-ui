# Dual-role account mode switch — session summary

**Date:** 2026-08-19
**Plan:** [`docs/plans/2026-08-19-dual-role-mode-switch.md`](../plans/2026-08-19-dual-role-mode-switch.md)
**Mockup:** [`docs/mockups/2026-08-19-dual-role-mode-switch.html`](../mockups/2026-08-19-dual-role-mode-switch.html)

Addresses the panel comment *"Role Flexibility: Adjust the database/auth logic so a single user
account can act as both a Tutor and a Tutee."*

## What shipped

All 14 planned steps. One account now holds both experiences, switching deliberately from the
sidebar and automatically when a link lands on the other mode's screens.

**Backend**

- `UserProfile.can_tutor` / `can_tutee` derived properties (`models.py`). `makemigrations --check`
  reports no changes — capabilities are properties, not columns, so the plan's "no data migration"
  claim held.
- `POST /api/switch-mode/` — rejects unknown modes and admin accounts; `carry_over_verification()`
  copies an approved application across roles by storage path, so documents are referenced rather
  than duplicated in media.
- `ModeAwareTokenRefreshView` returns the profile's current mode alongside `access`, so a client
  whose mode changed on another device corrects itself within one refresh cycle.
- `/api/profile/status/` now exposes `can_tutor`, `can_tutee`, and `tutor_rate_set`.
- Self-match blocked at three points: both candidate queries (`get_recommendation_candidate_tutors`
  as a queryset filter, and the subject search) plus a `self_booking` reject in
  `confirm_payment_and_book`.
- Identity checks rewritten to capability: the chat room lookup (which filtered on `role='Tutor'`
  and raised `DoesNotExist` for a tutor in Tutee mode, blocking chat entirely), the chat subtitle,
  and six `AdminUserSerializer` getters that would otherwise blank a dual-role user's own wallet.

**Frontend**

- `auth.js`: `switchMode()` plus cross-device mode-mismatch detection on refresh.
- `profile.js`: `canTutor`, `canTutee`, `tutorRateSet`.
- Router: auto-switch on cross-mode navigation with an Undo toast; a tutee-mode provisioning gate.
- `SbModeSwitcher.vue` in the sidebar footer, with the "no {role} account" modal. Hidden for
  SuperAdmin.
- Toast store gained optional `{ label, handler }` action support; `MODE_SWITCH_TOAST_MS` added to
  `config.js`.
- `TutorVerificationSetup.vue` shows an already-verified confirmation panel instead of the upload
  widgets when verification carried over.

## Deviations from the plan

1. **The capability check moved from the switch endpoint to the router guard.** Step 2 as written
   had the endpoint reject a switch into an unprovisioned mode — but that is precisely how a user
   reaches that mode's onboarding, since the onboarding routes are themselves role-gated. The
   endpoint now allows any Tutor/Tutee switch for non-admins; `can_tutor`/`can_tutee` decide
   whether the client auto-switches or shows the modal.

2. **The tutor onboarding gate needed `canTutor` added, plus a new `tutor_rate_set` flag.**
   `tutor_onboarding_complete` is true as soon as a `TutorApplication` exists, and carry-over
   creates one at switch time — so a switching tutee would have sailed past onboarding onto the
   tutor dashboard with no rate and no subjects. Separately, keying step 0 of the onboarding
   step-order off `profileCompleted` would skip the hourly-rate step for someone who had already
   completed the shared identity step, hence `tutor_rate_set`.

3. **Undo falls back to the mode's home when there is no history.** Not in the plan. The motivating
   scenario is a notification deep link, which frequently opens a fresh tab where `router.back()`
   resolves nowhere.

## Checks run

| Check | Result |
| --- | --- |
| `python manage.py check` | No issues |
| `python manage.py makemigrations --check --dry-run` | No changes detected |
| `python manage.py test --noinput --keepdb` | **Ran 478 tests — OK**, 0 failures |
| `npx vitest run` | 206 passed, 9 failed — all 9 pre-existing (verified against a stashed clean tree: `tokens.test.js`, `BookingTimeRangePicker.test.js`) |
| `npm run build` | Succeeds |
| `npm run lint` | 4 pre-existing errors in `make_algo_pptx.cjs` / `.js`, untouched by this work |

16 new tests in `DualRoleModeSwitchTests` cover capability derivation, switch-endpoint
authorization, verification carry-over (approved carries, pending does not), self-booking
rejection, search self-exclusion, the chat lookup for a tutor in Tutee mode, and wallet reporting
while in Tutee mode.

Two existing test files needed updating for the new component and store fields:
`AppSidebar.test.js` (stubs `SbModeSwitcher`) and `router/index.test.js` (profile mock gained the
capability fields).

## Not done / follow-ups

- The 214 `role` references were not exhaustively audited. The ones found during design are fixed;
  the mode-vs-identity heuristic in the plan is the classifier for the rest. Highest-risk remaining
  area is `admin_views.py` (13 references) listing users by role.
- Both applications inherit the same `reviewed_at`, so their 90-day renewal cadences fall due
  together and the user gets two renewal prompts. Arguably correct — same two files — but
  user-visible.
- Manual end-to-end verification of the notification → auto-switch → check-in flow has not been
  run against a live server.
- The other three panel items grilled in this session (dynamic 70/30 algorithm weight, OTP
  removal, category logic) are not started. The weight discussion reached a recommendation — one
  stored `cbf_weight` with `cf_weight` derived, on a dedicated singleton model — but no decision
  was recorded.
