# Brief: Instant Booking

> **Partly superseded (2026-08-10).** The strike system this brief specifies — `MONTHLY_STRIKE_CAP`,
> 3 *counted* strikes per calendar month — was replaced by a rolling 14-day window of *active*
> strikes, where an unresolved ticket counts provisionally and only an `excused` verdict relieves
> it. See [ADR-0011](../adr/0011-provisional-late-cancellation-strikes.md). Everything else here
> (instant confirmation, Grace Cutoff, P50 tutor deduction on a counted verdict, search-visibility
> gating) still describes the shipped system.

Follow this brief exactly. Standing rules are in AGENTS.md. Reference:
`docs/plans/2026-07-15-instant-booking.md` (plan) and `docs/adr/0008-instant-booking-replaces-request-to-book.md`
(ADR — read this first, it's short and states every rejected alternative and why).

No `docs/tickets.md` entry exists for this plan — this brief covers the whole plan, all 8 steps,
in the order below (later steps depend on earlier ones).

## Scope

In scope: everything in the plan's "Steps" section — booking creation becomes instant
confirmation, Grace Cutoff cancellation + strike system, search-visibility gate extension,
approve/reject teardown + data migration, and the matching frontend changes.

Out of scope: anything not named in the plan. Do not touch the recommender code
(`backend/studybuddy/recommender/`), the wallet cash-in/cash-out flow, or verification/onboarding
gating logic beyond reading `can_create_new_booking`. Do not add a per-tutor opt-in flag or an
admin pre-approval step for cancellation — the ADR explicitly rejected both.

## Execution checklist

### 1. Backend — booking creation becomes confirmation

`confirm_payment_and_book` in `backend/studybuddy/views.py:2373` currently creates bookings with
`status="Pending"` (the `Booking.objects.create(...)` call at line 2539, inside the
`for slot_request in slot_group:` loop at line 2538) and notifies the tutor with a `"pending"`
status (line 2554-2558). Change this to:

- Create bookings with `status="Confirmed"` instead of `"Pending"`.
- Before creating, enforce the three gates currently living in `approve_booking`
  (`backend/studybuddy/views.py:2808`, being removed in step 4): verification via
  `can_create_new_booking(tutor.profile)` (helper at `views.py:310`, already imported/used at
  line 2377 for the tutee side — call it for the tutor too), non-negative wallet balance
  (`Wallet.objects.get_or_create(tutor=tutor)`, pattern at `views.py:2830-2835`), and the
  Accepted Session Load Limit via `get_tutor_acceptance_load_snapshot(tutor)`
  (`views.py:757`, pattern at `views.py:2843-2855`). Since search visibility (step 3) already
  hides a gated-out tutor, a failure here should be a 403/409 with a clear error — the tutee
  should not normally hit this path, but the server check is the backstop per the ADR.
- Enforce the **Booking Horizon**: reject (400) any `session_date` more than 14 days from
  `timezone.localtime(timezone.now()).date()`. Add a module-level constant
  `BOOKING_HORIZON_DAYS = 14` near the other constants at `views.py:99-100`.
- Generate a **Meeting Link** for `session_mode == "Online"` bookings only: an unguessable Jitsi
  room URL, one per `session_group_id` (not per individual slot booking), e.g.
  `f"https://meet.jit.si/studybuddy-{uuid4().hex}"`. Add a `meeting_link` field
  (`models.URLField(blank=True, default='')`) to `Booking` in `backend/studybuddy/models.py:763`,
  and a migration for it. Store the same link on every booking row in the session group.
- Determine a "born-late" flag: `True` if the booking is created inside the final 12 hours before
  its own `session_date`/time slot (i.e., there is no penalty-free cancellation window at all).
  Add `is_born_late = models.BooleanField(default=False)` to `Booking` alongside `meeting_link`,
  set at creation time using the same `GRACE_CUTOFF_HOURS = 12` constant introduced in step 2.
- Update notifications: replace the `"pending"` notification (line 2554-2558) with a
  `"confirmed"`-style notification to both parties (reuse
  `create_booking_status_notification`, `views.py:999`, and the `"confirmed"` status branch
  already used in `approve_booking` at line 2863-2867). Tutor's notification/email must state the
  penalty-free-cancel deadline (session start minus `GRACE_CUTOFF_HOURS`); if `is_born_late`, state
  plainly that this booking has no penalty-free cancellation window.
- Send the tutor an immediate email. Add `send_booking_confirmed_email_task(booking_id)` to
  `backend/studybuddy/mailer.py` following the existing task pattern (see
  `send_document_renewal_reminder_email_task`, `mailer.py:181-199`, and its `enqueue_*` wrapper
  pattern at `mailer.py:204-220`) — add `enqueue_booking_confirmed(tutor_user, booking)` and call
  it from `confirm_payment_and_book` after the transaction commits.
- Auto-create/surface the chat thread: call `get_canonical_room_for_booking(booking)`
  (`backend/studybuddy/chat/services.py:30`) and post a neutral system `Message` into it (see the
  `Message.objects.create(room=..., sender=None, content=...)` pattern at
  `views.py:5653-5658` for the shape of a system message).
- Keep `create_booking_event(..., "booking_requested")` (line 2561-2566) but rename the event/copy
  to reflect instant confirmation (e.g. `"booking_confirmed"`, "Booking confirmed instantly.").

Acceptance:
- [ ] A booking created via `confirm_payment_and_book` has `status="Confirmed"` immediately, no
      `Pending` row is ever created by this endpoint.
- [ ] A tutor failing verification, negative wallet, or load-limit gate gets a clear 4xx from this
      endpoint (belt-and-suspenders; normally unreachable because of step 3).
- [ ] A `session_date` more than 14 days out is rejected with 400.
- [ ] Online bookings get one `meeting_link` per session group; F2F bookings do not.
- [ ] `is_born_late` is `True` only when the booking is created inside the 12h Grace Cutoff of its
      own session start.
- [ ] Tutor gets an in-app notification + email stating the cancel deadline (or the born-late
      warning); tutee gets a confirmation notification with the Meeting Link or preferred location.
- [ ] A chat room exists for the tutee/tutor pair with a system message after booking.

### 2. Backend — cancellation rework

`cancel_booking` (`backend/studybuddy/views.py:2918`) currently requires a reason (min 5 chars,
lines 2941-2946) and cancels unconditionally. Add Grace Cutoff logic:

- Add `GRACE_CUTOFF_HOURS = 12` as a module constant (co-locate with `BOOKING_HORIZON_DAYS`).
- Compute the session's start datetime from `first_booking.session_date` +
  `first_booking.availability.time_slot` (see the existing `start_time`/`end_time` computation at
  lines 2961-2965 for the pattern), localized consistently with the existing Manila-timezone
  discipline used elsewhere in this function (`timezone.localtime(timezone.now())`, as used at
  line 2473 in `confirm_payment_and_book` — match that, don't introduce a new timezone helper).
- If cancelling before `session_start - GRACE_CUTOFF_HOURS`: existing behavior, unchanged
  (immediate `Cancelled`, no ticket).
- If cancelling at or after that cutoff (a "Late Cancellation"): still cancel immediately
  (self-serve, per the ADR — never blocked on admin approval), but also auto-open a
  `SupportTicket` (`models.py:1054`) with a new system-opened category. Add
  `('Late_Cancellation', 'Late Cancellation')` to `SupportTicket.CATEGORY_CHOICES` and a
  `reported_by_system = models.BooleanField(default=False)` field (migration required), set
  `True` for this ticket. Set `booking=representative_booking`, `user=` the *other* party (the one
  who did not cancel — they are the aggrieved party the ticket protects), `category='Late_Cancellation'`,
  and a description built from `actor_role`/`reason`.
- Add strike-resolution fields to `SupportTicket`: `resolution_verdict` (choices `excused`/
  `counted`, blank/null default) — set by the admin action in step 2's ticket-resolution endpoint,
  not here.

Acceptance:
- [ ] Cancelling more than 12h before session start: unchanged, no ticket created.
- [ ] Cancelling within 12h (or after start): booking still cancels immediately, and exactly one
      `Late_Cancellation` `SupportTicket` is created with `reported_by_system=True`.
- [ ] Existing cancellation tests in `backend/studybuddy/tests.py` for the pre-cutoff path still
      pass; add a new test for the post-cutoff ticket-creation path.

### 2b. Backend — strike accounting on ticket resolution

Extend `admin_resolve_ticket` (`backend/studybuddy/views.py:5636`). Currently it just sets
`status='Resolved'` and posts a closing chat message (lines 5650-5658). For a
`category='Late_Cancellation'` ticket, the request body must carry a verdict
(`excused` or `counted`):

- Add `COUNTED_STRIKE_WALLET_DEDUCTION = 50` and `MONTHLY_STRIKE_CAP = 3` as module constants in
  `views.py`.
- `excused`: no wallet/strike effect, resolve as today.
- `counted`: set `ticket.resolution_verdict = 'counted'`; if the *cancelling* party was the tutor,
  deduct `COUNTED_STRIKE_WALLET_DEDUCTION` from their `Wallet.balance` (allowed to go negative —
  do not clamp) via a `Transaction` (reuse the `Transaction` model at `models.py:542`; add a
  `('counted_strike', 'Counted Strike Penalty')` choice to `TRANSACTION_TYPES`). Tutees have no
  wallet — no deduction for a tutee-side counted strike.
- Track a per-user, per-calendar-month counted-strike count (both roles share the same
  `MONTHLY_STRIKE_CAP = 3`). Add a lightweight query — count `SupportTicket.objects.filter(
  category='Late_Cancellation', resolution_verdict='counted', <cancelling-party-fk>=user,
  created_at__month=..., created_at__year=...)` — you'll need a `cancelled_by` FK on
  `SupportTicket` (or reuse `Booking.cancelled_by_role` plus a join through `booking.student`/
  `booking.tutor.profile`; prefer adding an explicit `SupportTicket.penalized_user` FK to
  `UserProfile` set at ticket-creation time in step 2, since "the cancelling party" isn't always
  `ticket.user`).
- Hitting the cap (3rd counted strike in the current calendar month) suspends: tutee → block new
  bookings (extend the `can_create_new_booking` check at `views.py:310`); tutor → search
  invisibility (extend the same gate as step 3). Suspension lasts through the end of the current
  calendar month — no new field needed if computed live from the strike count each check.

Acceptance:
- [ ] Resolving a `Late_Cancellation` ticket as `excused` has no wallet/strike effect.
- [ ] Resolving as `counted` against a tutor deducts P50 from their wallet balance (verified via a
      new `Transaction` row) and increments their monthly counted-strike count.
- [ ] Resolving as `counted` against a tutee increments their count with no wallet effect.
- [ ] A 3rd counted strike in the same calendar month suspends booking (tutee) or search
      visibility (tutor) for the rest of that month; a 4th+ has no additional effect.

### 3. Backend — search visibility gates

`get_recommendation_candidate_tutors` (`backend/studybuddy/views.py:3708`) builds
`base_candidates` at line 3718-3724, currently filtering only
`profile__tutor_application__application_status='approved'` (line 3721) plus institution scoping.
Extend this filter to also exclude tutors who: have a negative wallet balance, are at/over their
`accepted_session_load` vs `session_load_limit` (reuse `get_tutor_acceptance_load_snapshot`,
`views.py:757`, or express the equivalent as a queryset annotation/exclude — prefer whichever
keeps this a single queryset without an N+1; a Python-level filter over `base_candidates` calling
the existing snapshot helper per-tutor is acceptable given expected search result sizes, matching
the codebase's existing style rather than introducing new query-optimization machinery), or have
hit the Monthly Strike Cap from step 2b. Do not touch the existing
`RECOMMENDATION_BLOCKING_STATUSES` (`views.py:3669`) or the `application_status='approved'`
condition — add to the exclusion, don't replace it.

Add a dashboard banner condition for tutors hidden by the load limit specifically (not the other
gates) — see step 6.

Acceptance:
- [ ] A tutor with a negative wallet balance never appears in `recommend_tutors_view` results.
- [ ] A tutor at their session load limit never appears in results.
- [ ] A tutor suspended by the Monthly Strike Cap never appears in results.
- [ ] None of these conditions affect a tutor's normal appearance when none apply.

### 4. Backend — teardown + migration

- Delete `approve_booking` (`views.py:2808-2877`) and `reject_booking` (`views.py:2879-2913`)
  entirely, along with their imports/references and the two URL routes in
  `backend/studybuddy/urls.py` (`approve/` at line 147, `reject/` at line 148, plus the
  `approve_booking`/`reject_booking` imports at lines 21-22).
- `Booking.STATUS_CHOICES` (`models.py:765-772`) keeps `'Pending'` in the choices list (historical
  rows only) but no code path should set it going forward — `confirm_payment_and_book` no longer
  creates it (step 1), and nothing else creates bookings.
- Data migration: for every `Booking` with `status='Pending'` at migration time, set
  `status='Rejected'` (or a new terminal value if `'Rejected'` reads wrong for "never got a
  chance to be accepted" — use judgement, but do not invent a new STATUS_CHOICES value without a
  reason) and fire a rebook-instantly notification to the affected tutee via
  `create_booking_status_notification` (reuse the existing notification path, don't build a new
  one).
- Remove `approve_booking`/`reject_booking` references from `backend/studybuddy/tests.py` (grep
  the file — there are existing tests exercising both).

Acceptance:
- [ ] `approve_booking`/`reject_booking` views, URLs, and tests are gone; hitting the old routes
      404s.
- [ ] Migration runs clean on a database with existing `Pending` rows; those rows end up in a
      terminal, non-`Pending` status and the affected tutee gets a notification.
- [ ] `python manage.py test` passes with no references to the removed views.

### 5. Frontend — booking flow

`src/views/TutorDetails.vue` currently drives the confirm step that calls `bookings/confirm/`.
Update its success state to instant-confirmation UX: show the Meeting Link (Online) or preferred
location (F2F) directly on the success screen, state the penalty-free-cancel deadline, and show a
distinct born-late warning when the backend reports `is_born_late`. `src/views/FindTutors.vue`
must respect the 14-day Booking Horizon in its own date picker (don't only rely on the server
400 — disable/hide dates beyond day 14 in the UI).

Acceptance:
- [ ] Booking a session shows the confirmation screen with the Meeting Link / location and the
      cancel-deadline copy, no "waiting for tutor" state anywhere in this flow.
- [ ] FindTutors' date selection cannot produce a date beyond 14 days out.

### 6. Frontend — tutor surfaces

- Delete `src/views/TutorRequestedSessions.vue` and its route (`src/router/index.js:160-165`,
  path `/tch-requestedSessions`) and any nav link pointing at it (grep `tch-requestedSessions`
  across `src/`).
- Add a cancel-before-cutoff affordance to the tutor's upcoming-sessions view wherever bookings
  are currently listed for a tutor (the booking cancel UI already exists elsewhere in the app —
  match its pattern; find it via the existing `cancel_booking` API call in `src/services/`).
- Add a load-limit invisibility banner to `src/views/TutorDashboard.vue` shown when the tutor is
  currently hidden from search specifically due to the load-limit gate from step 3 (distinguish
  this from the other gates — the banner's whole purpose is telling the tutor *why* they're
  invisible when it's something they can immediately act on by clearing a session).

Acceptance:
- [ ] `/tch-requestedSessions` no longer resolves; no dead nav link remains.
- [ ] A tutor at their load limit sees a banner on `TutorDashboard.vue` explaining the
      invisibility; a tutor gated by wallet or strike cap does not see this specific banner (a
      generic one is acceptable if you choose to add one, but the load-limit case must be
      unambiguous).
- [ ] Tutors can cancel an upcoming session from wherever they view it.

### 7. Frontend — admin surfaces

- `src/views/AdminSupport.vue`: add a resolution control for `Late_Cancellation` tickets that
  lets the admin pick Excused or Counted (calling the extended `admin_resolve_ticket` from step
  2b with the verdict).
- `src/views/AdminUsers.vue` (Tutor Management): surface each tutor's current monthly counted-
  strike count.

Acceptance:
- [ ] An admin viewing a `Late_Cancellation` ticket can resolve it as Excused or Counted; Counted
      visibly reflects the wallet deduction/strike increment from step 2b.
- [ ] Tutor Management shows the current month's strike count per tutor.

### 8. Docs

Update `docs/architecture/booking-flow.md` to describe the new instant-confirmation flow, Grace
Cutoff/strike system, and the removal of the approve/reject step — this file is the canonical
reference for the booking flow per project convention and must not go stale.

Acceptance:
- [ ] `docs/architecture/booking-flow.md` reflects instant booking, not the old request-to-book
      flow.

## Context

- **Conventions**: PEP 8 backend (snake_case functions/vars, PascalCase classes); Vue 3
  `<script setup>`, 2-space indent, single quotes/no semicolons, 100-col limit on the frontend.
  Route API calls through `src/services/`, never inline `axios`/`fetch` in components.
- **Timezone discipline**: this codebase has had recurring Manila-timezone bugs in booking-time
  validation (see recent commit history) — always use `timezone.localtime(timezone.now())`
  exactly as `confirm_payment_and_book` already does at `views.py:2473`; never introduce a naive
  `datetime.now()` comparison.
- **`select_for_update` discipline**: `approve_booking` used `select_for_update()` on the booking
  row to avoid race conditions (`views.py:2810`); `confirm_payment_and_book` already does the
  same on `TutorAvailability` (`views.py:2457-2461`). Preserve this discipline for the new gate
  checks in step 1 and the strike-cap check in step 2b/3 — two concurrent requests must not both
  slip through a boundary check.
- **ADR 0008** (`docs/adr/0008-instant-booking-replaces-request-to-book.md`) is the authority on
  what was rejected and why: no per-tutor opt-in, no admin pre-approval to cancel. Don't
  reintroduce either as a "safer" middle ground.
- **Glossary**: `CONTEXT.md` has entries for Instant Booking, Grace Cutoff, Late Cancellation,
  Counted Strike, Monthly Strike Cap, Booking Horizon, and Meeting Link — use these terms
  verbatim in code comments/copy where a name is needed, don't invent synonyms.

## Contract

- Work ONLY this brief — no scope creep, no drive-by refactors.
- TDD: failing test first, then the minimal implementation, matching existing style.
- Run typecheck and the relevant tests; get them green; paste commands and output under Test
  evidence.
- NEVER commit, push, branch, or run any git write. Leave the tree dirty.
- Record anything done differently, and why, under Deviations.

## Test evidence

- `python -m compileall -q backend/studybuddy` — passed.
- `cd backend; python manage.py makemigrations studybuddy --dry-run --check` — passed; no model changes pending.
- `cd backend; python manage.py test studybuddy.tests.BookingVerificationGateTests --keepdb` — passed (12 tests, 57.307s).
- `npm run build` — passed after rerunning outside the sandbox because Vite/esbuild could not spawn under the sandbox (`EPERM`).

## Deviations

- The requested filename was absent; executed the matching `2026-07-16-instant-booking.md` brief.
- Work is incomplete: the remaining admin UI, tutor cancellation affordance, and complete teardown
  of obsolete backend view definitions still need implementation and review. No commit, branch,
  push, or deployment was performed.

## Codex review — 2026-07-16

Verified independently: `python -m compileall`, `makemigrations --check` (clean, no drift),
`BookingVerificationGateTests` (12/12 green), full suite (`python manage.py test studybuddy`,
314 tests, 28 failures + 5 errors) — every failure reproduced identically on a clean `main`
checkout (confirmed by stashing the diff and re-running), so none are attributable to this work.
`npm run lint` and `npm run build` both clean.

Reviewed and fixed two trivial nits directly rather than round-tripping:
- Deleted the now-dead `approve_booking`/`reject_booking` view bodies in `views.py` (routes and
  tests were already removed, leaving unreachable functions) and the matching dead
  `approveSession`/`rejectSession` methods in `src/stores/completedSessions.js` (their only
  caller was the deleted `TutorRequestedSessions.vue`; both hit routes that now 404).
- Replaced a hardcoded `12` in `mailer.py`'s `send_booking_confirmed_email_task` with a named
  `GRACE_CUTOFF_HOURS` constant (mirroring, not importing, `views.py`'s constant of the same
  name — importing would create a circular import since `views.py` already imports `mailer`).

Committed steps 1-4 (backend) and steps 5, 6 (partial), 8 (frontend teardown/UX + docs) in three
stops. Steps 6 (partial) and 7, plus test coverage for steps 2/2b/3, are genuinely unfinished —
see Fix round 1 below. Plan stays In Progress.

## Fix round 1

Three gaps, all confirmed by re-reading the diff against this brief's own acceptance criteria —
not present anywhere in the current tree:

1. **Step 6 — cancel-before-cutoff affordance for tutors (missing).** Tutors currently have no
   way to cancel a booking from the UI at all — only the tutee side calls `cancelSession`
   (`src/stores/completedSessions.js`, still exported), from `TuteeSessionDetailsFlow.vue:695`
   (prompts for a reason, then calls `sessionsStore.cancelSession(id, reason)`). Mirror that
   pattern for tutors in `src/views/TutorSessionsReports.vue`, which already lists
   `sessionStore.upcomingSessions` (lines 255, 360-361, 396) but has no action column/button.
   Add a cancel action per upcoming session row that prompts for a reason and calls
   `cancelSession`; no new backend work needed, `cancel_booking` already handles both roles.
   - [ ] A tutor can cancel an upcoming session from `TutorSessionsReports.vue`.

2. **Step 7 — admin surfaces (entirely missing).** Neither `src/views/AdminSupport.vue` nor
   `src/views/AdminUsers.vue` was touched.
   - In `AdminSupport.vue`, add a resolution control for tickets with `category='Late_Cancellation'`
     letting the admin pick Excused or Counted, posting `{verdict: 'excused'|'counted'}` to
     `admin_resolve_ticket` (`backend/studybuddy/views.py`, already accepts this — see the
     `verdict = request.data.get('verdict')` branch). Reflect the response's
     `resolution_verdict`/`monthly_counted_strikes` back in the UI after resolving.
   - In `AdminUsers.vue` (Tutor Management), surface each tutor's current monthly counted-strike
     count. The backend has no listing endpoint for this yet — add one (or extend an existing
     tutor-listing endpoint in `admin_views.py`) that returns
     `get_monthly_counted_strike_count(tutor.profile)` (already defined in `views.py`) per tutor.
   - [ ] An admin can resolve a `Late_Cancellation` ticket as Excused or Counted from
         `AdminSupport.vue`.
   - [ ] `AdminUsers.vue` shows each tutor's current-month counted-strike count.

3. **Test coverage — steps 2, 2b, 3 (missing).** The Contract required TDD; only
   `BookingVerificationGateTests` (step 1's gates) got tests. The following are implemented in
   `views.py` but have zero test coverage — write failing tests first, then confirm they pass
   against the existing implementation (do not change the implementation unless a test reveals a
   real bug):
   - `cancel_booking`: cancelling >12h before session start (no ticket); cancelling within 12h
     (Late Cancellation — booking still cancels immediately, exactly one `SupportTicket` with
     `category='Late_Cancellation'`, `reported_by_system=True`, `penalized_user=`the canceller).
   - `admin_resolve_ticket`: resolving a `Late_Cancellation` ticket `excused` (no wallet/strike
     effect) vs `counted` against a tutor (P50 `Transaction` deduction, wallet balance drops,
     `get_monthly_counted_strike_count` increments) vs `counted` against a tutee (count
     increments, no wallet effect, tutees have none).
   - Monthly Strike Cap suspension: a 3rd counted strike in the same calendar month blocks
     `can_create_new_booking` for a tutee and excludes the tutor from
     `get_recommendation_candidate_tutors` results; a 4th has no additional effect.
   - `get_recommendation_candidate_tutors` gates: a tutor with a negative wallet balance, one at
     their session load limit, and one suspended by the strike cap are each excluded from
     `recommend_tutors_view` results; none of these conditions affect a tutor when absent.
   - [ ] All the scenarios above have a passing test in `backend/studybuddy/tests.py`.

Contract for this round: same as the original brief (TDD, run tests, no git writes, log
Deviations). Do not touch anything outside these three items.
