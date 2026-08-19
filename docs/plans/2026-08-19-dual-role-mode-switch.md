---
title: Dual-role account mode switch
date: 2026-08-19
status: Done
summary: One account can act as both Tutor and Tutee via a persisted active-mode switch, with derived capabilities and auto-switch on cross-mode navigation.
spec: ../mockups/2026-08-19-dual-role-mode-switch.html
---

# Dual-role account mode switch

Panel comment being addressed: *"Role Flexibility: Adjust the database/auth logic so a single user
account can act as both a Tutor and a Tutee."*

## Status & Progress Summary

**Status:** Done — all 14 steps implemented and verified.

Full backend suite: **478 tests, OK** (0 failures). `manage.py check` clean.
`makemigrations --check` reports no changes — capabilities are properties, not columns, so the
"no data migration" claim held. `npm run build` succeeds. `npx vitest run` is back to its 9
pre-existing failures (`tokens.test.js`, `BookingTimeRangePicker.test.js`, both confirmed failing
on a stashed clean tree). 16 new `DualRoleModeSwitchTests` all pass.

Outcome recorded in
[`docs/session-summaries/2026-08-19-dual-role-mode-switch-summary.md`](../session-summaries/2026-08-19-dual-role-mode-switch-summary.md).

Two corrections made during implementation, both recorded in the Changelog: the capability check
moved from the switch endpoint to the router guard, and the tutor onboarding gate had to be
widened to include `canTutor` because carry-over makes `tutorOnboardingComplete` true too early.

## Goal

Let one account hold both the Tutor and the Tutee experience, switching between them deliberately
from the sidebar and automatically when a link lands on the other mode's screens — without
rewriting the 214 `role` checks that assume a user is exactly one thing.

## Approach

**Active-mode switch, not a merged experience.** `UserProfile.role` survives, but its meaning
narrows from *identity* to *current mode*. It still holds exactly one value at any instant, so
every existing `role == 'Tutor'` check and every `meta.role` route guard keeps working unchanged.
A merged both-navs-at-once design would invalidate all of them at once, and would also make
"which role's rules apply to this action" unanswerable — the platform's rules are role-asymmetric
(a tutor's late cancellation costs a ₱50 Counted Strike, a tutee's costs nothing).

**Capability is derived, never stored.** Two properties on `UserProfile`:

- `can_tutor` — a `Tutor` row exists with `hourly_rate` set and at least one `TutorSubjects`.
- `can_tutee` — a `Preference` row exists.

These mean *provisioned*, not *permitted* — every non-admin student is permitted both, so a
permission-flavoured definition would be useless as a gate. Deriving rather than adding
`tutor_onboarding_completed` / `tutee_onboarding_completed` columns avoids state that can drift
from reality; the codebase already carries `tutor_onboarding_skipped_at` and a derived
`tutor_onboarding_complete`, so this follows existing precedent rather than introducing a fourth
and fifth flag to keep consistent.

One concept does three jobs: it drives the router guard, decides whether the "you don't have a
{role} account" modal fires, and answers the serializers' identity checks.

**No data migration.** Because capability derives from rows that already exist, every current
account lands correctly on deploy. An existing Tutee has no `Tutor` row so `can_tutor` is false;
an existing Tutor has no `Preference` row so `can_tutee` is false. Both get a switcher; neither's
current experience changes.

**Verification carries over.** `TutorApplication` and `TuteeApplication` are separate
`OneToOneField`s on `UserProfile` with distinct `related_name`s, both subclassing
`ApplicationVerificationBase`, and both collecting the *same two documents* (`school_id`,
`enrollment_proof`). Re-asking for them would ask "is this a real enrolled CPU student" twice and
double the SuperAdmin review queue. On adding the second role, the second application is created
already `approved`, copying the file references plus `reviewed_at` / `reviewed_by`.

Rejected alternative: hoisting verification onto `UserProfile` and deleting the per-role
duplication. That is the principled fix but means rewriting `ApplicationVerificationBase`, both
renewal-review models, and the admin review panel — far beyond what the panel asked for.

**Mode checks vs identity checks.** Once `role` means mode, existing uses split in two and need
opposite treatment. The classifying heuristic: *if the check is about a third party being looked
up, it is identity → rewrite to capability; if it is about the requester's own current screen,
it is mode → leave as `role`.*

**Auto-switch on cross-mode navigation.** When the guard sees a mode mismatch but the capability
is present, it switches and proceeds rather than bouncing. Mode is not a permission —
`can_tutor` already established entitlement, so prompting asks a question whose answer is always
yes. Bouncing is actively harmful: a tutor sitting in Tutee mode who taps "your session starts in
15 minutes" gets silently redirected off check-in, misses it, and eats a ₱50 Counted Strike. See
the flow comparison in `docs/mockups/2026-08-19-dual-role-mode-switch.html`, and the clickable
behaviour simulation (both branches, all three persona shapes) in
`docs/mockups/2026-08-19-dual-role-mode-switch-behaviour.html`.

## Steps

### Backend

1. Add `can_tutor` / `can_tutee` properties to `UserProfile` (`backend/studybuddy/models.py`).
2. Add `POST /api/switch-mode/`: validates target is `Tutor` or `Tutee`, rejects
   `role='SuperAdmin'`, rejects a target whose capability is false, sets `profile.role`, returns
   the same payload shape as login. No token reissue — `role` is not a JWT claim, and every
   backend check reads `request.user.userprofile.role` fresh from the DB.
3. Expose `can_tutor`, `can_tutee`, and `role` from `/api/profile/status/`.
4. Wrap `token/refresh/` in a custom view returning the profile's current `role` alongside
   `access`, so the client can detect a mode changed on another device.
5. Self-match prevention:
   - `.exclude(profile_id=student_profile.id)` in `get_recommendation_candidate_tutors`
     (`views.py:3900`) and the subject search at `views.py:1915`.
   - Hard reject in `confirm_payment_and_book` — per ADR-0008 the confirm-time server check is
     authoritative and search-hiding is only the surface.
6. Rewrite identity checks to capability:
   - `chat/services.py:742` — `UserProfile.objects.get(id=..., role='Tutor')` raises
     `DoesNotExist` for a tutor in Tutee mode, blocking chat outright. Look up by
     `Tutor.objects.get(profile_id=...)` instead.
   - `chat/services.py:543` — chat subtitle prints `partner.role`, showing "Tutee" for a tutor.
   - `serializers.py:109-157` — `get_wallet_balance`, `get_tutor_sessions_completed`,
     `get_tutor_avg_rating`, `get_tutor_session_load_*` all gate on `obj.role == 'Tutor'` and
     would blank a dual-role user's own wallet while they sit in Tutee mode.
7. Second-application carry-over on first switch into an unprovisioned role.

### Frontend

8. `src/stores/auth.js` — `switchMode(target)` action; compare `role` from the refresh response
   against the stored role and re-sync + toast on mismatch.
9. `src/router/index.js` step 4 (role protection, ~line 405) — on mismatch, if the capability for
   the required role is true, call `switchMode` and proceed; if false, fall through to the
   existing redirect and let the modal fire.
10. Toast with **Undo** on auto-switch: restores the previous mode *and* returns to the previous
    route.
11. Sidebar switcher in `App.vue`, hidden for SuperAdmin.
12. "You currently don't have a {Tutor|Tutee} account" modal → the corresponding onboarding entry
    (`/tutor-setup` or `/preferencesetup`).
13. `TutorVerificationSetup.vue` step 3 — when the other role's application is already approved,
    replace the two upload widgets with a confirmation panel and submit without files. (Note: the
    existing "Verified tutors appear in tutee search" copy explains the *consequence* of
    verification; it does not detect existing verification. This behaviour has to be built.)
14. Per-mode onboarding completeness in the guard, replacing the single `profileCompleted` check
    for role-specific steps.

## Risks

- **Mode is account-global, not per-device or per-tab.** Switching on a phone flips a laptop's
  sidebar on its next request. Accepted deliberately; step 4 + step 8 downgrade it from silent to
  explained, with worst-case 4-minute staleness (`ACCESS_REFRESH_INTERVAL_MS`) or immediate on a
  403.
- **The 214 `role` references are not individually audited yet.** Steps 6 covers the ones found
  during design; a sweep is needed and the heuristic above is the classifier. Highest-risk
  remaining area is `admin_views.py` (13 references) listing users by role.
- **Renewal cadence couples.** Both applications inherit the same `reviewed_at`, so both come due
  at the same 90-day `DOCUMENT_RENEWAL_INTERVAL_DAYS` mark and the user gets two renewal prompts.
  Arguably correct — they are literally the same two files — but it is user-visible.
- **`get_login_profile_for_user` force-resets staff to `SuperAdmin` on every login**
  (`views.py:631`), which is why SuperAdmin is excluded from switching rather than merely hidden.
- **Recommender cost**: unrelated to this plan, but `recommend_tutors_hybrid` loops over every
  candidate — the self-exclusion must be a queryset filter, not a per-tutor check.

## Checks to run

- `python manage.py test` in `backend/` — all existing tests pass; new tests for switch-mode
  authorization, capability derivation, self-match rejection at confirm, and chat lookup for a
  tutor in Tutee mode.
- `npm run lint` — clean.
- `npm run build` — succeeds.
- `npx vitest run` — existing suites pass.
- Manual: as a dual-role account, tap a tutor-session notification while in Tutee mode and
  confirm you land on check-in with a "Switched to Tutor mode" toast, and that Undo returns both
  the mode and the route.

## Changelog

- **2026-08-19** — Plan created from the panel-comments grilling session. Decisions recorded:
  active-mode switch over merged experience; capability derived (`can_tutor` / `can_tutee`) as
  *provisioned* rather than *permitted*; verification carried over between roles; self-match
  blocked at both the search filter and the `confirm_payment_and_book` backstop; auto-switch with
  an Undo toast on cross-mode navigation; SuperAdmin excluded from switching; mode-vs-identity
  classification heuristic adopted for the 214 `role` references. Flow comparison mockup saved to
  `docs/mockups/2026-08-19-dual-role-mode-switch.html`.
- **2026-08-19** — All 14 steps implemented. Two design corrections found while building:
  - **The capability check moved from the switch endpoint to the router guard.** As written, step
    2 had the endpoint reject a switch into an unprovisioned mode — but that is exactly how a user
    reaches that mode's onboarding, since the onboarding routes are themselves role-gated. The
    endpoint now allows any Tutor/Tutee switch for non-admins; `can_tutor`/`can_tutee` decide
    whether the *client* offers an auto-switch or shows the modal.
  - **The tutor onboarding gate now also requires `canTutor`.** `tutor_onboarding_complete` is
    true as soon as a `TutorApplication` exists, and carry-over creates one at switch time — so a
    switching tutee would have sailed past onboarding onto the tutor dashboard with no rate and no
    subjects. A new `tutor_rate_set` flag on `/profile/status/` also replaces `profileCompleted`
    for step 0 of the onboarding step-order, since a switching tutee has already completed the
    shared identity step and would otherwise skip the hourly-rate step.

  Also added: `MODE_SWITCH_TOAST_MS` to `config.js`, optional `{ label, handler }` action support
  in the toast store (for Undo), `SbModeSwitcher.vue`, and 16 tests in `DualRoleModeSwitchTests`.
  `AppSidebar.test.js` gained an `SbModeSwitcher` stub and `router/index.test.js`'s profile mock
  gained the new capability fields.
- **2026-08-19** — Verified and closed. Full backend suite 478 tests OK. One extra hardening fix
  beyond the plan: the Undo handler falls back to the restored mode's home when there is no
  history entry, since the motivating scenario (a notification deep link) often opens a fresh tab
  where `router.back()` resolves nowhere. Session summary written; status set to Done.
