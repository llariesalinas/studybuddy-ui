---
title: Instant Booking
date: 2026-07-15
status: In Progress
summary: Replace request-to-book with instant confirmation, Grace Cutoff cancellations, strike accountability, and auto-generated meeting links.
spec: ../adr/0008-instant-booking-replaces-request-to-book.md
---

# Instant Booking

> **Partly superseded (2026-08-10).** The Monthly Strike Cap described below (3 *counted* strikes
> per calendar month) is now a rolling 14-day window of 3 *active* strikes, counted provisionally
> from the moment the ticket opens. See
> [ADR-0011](../adr/0011-provisional-late-cancellation-strikes.md).

## Status & Progress Summary

**In Progress.** Design settled in the 2026-07-15 grilling session; ADR 0008 and glossary terms
written. Codex ran the 2026-07-16 brief and delivered steps 1-5, 6 (load-limit banner only), and
8; `/codex-review` verified independently (full suite reproduces its 28 failures/5 errors
identically on clean `main`, none attributable), fixed two dead-code nits itself, and committed in
three stops. Remaining: the tutor cancel-before-cutoff affordance (rest of step 6), all of step 7
(admin surfaces), and test coverage for steps 2/2b/3 — tracked as Fix round 1 in the same brief.
Team handoff summary: `docs/mockups/2026-07-16-bookings-subjects-handoff.html`.

## Goal

Implement the panel's ask — sessions confirm instantly on submission with auto-generated meeting
links, no manual tutor acceptance — without inheriting the no-show and stale-availability risks
that a naive cut would create. Design settled in a grilling session on 2026-07-15; decisions
recorded in ADR 0008 and the `CONTEXT.md` glossary (Instant Booking, Grace Cutoff, Late
Cancellation, Counted Strike, Monthly Strike Cap, Booking Horizon, Meeting Link).

## Approach

Instant Booking becomes the only booking model. Tutor protection moves from pre-confirmation
review to post-hoc accountability:

- **Grace Cutoff (12h, platform constant):** cancellation before it is free and untracked, for
  both roles. After it, cancellation is still self-serve and immediate, but auto-opens a Support
  Ticket (existing model, new system-opened category) for institution-admin review.
- **Counted Strike:** admin resolves the ticket excused or counted. Counted costs a tutor a flat
  P50 wallet deduction (platform-bound, may go negative); tutees pay no fee. Both roles share a
  Monthly Strike Cap of 3 — hitting it suspends booking (tutee) or search visibility (tutor) for
  the rest of the calendar month.
- **Booking-time gates:** the three tutor gates formerly in `approve_booking` (verification /
  Renewal Required, non-negative wallet, Accepted Session Load Limit) move to booking creation.
  A tutor failing any gate is hidden from search (reusing the search-visibility mechanism from
  the tutor-onboarding branch); the server check remains the authoritative backstop. Tutors at
  their load limit see a dashboard banner explaining their invisibility.
- **Booking Horizon (14 days):** bounds stale recurring-availability damage. No dormancy pause,
  no freshness re-confirmation (considered, rejected).
- **Meeting Link:** server-generated Jitsi room URL (unguessable slug per session group) at
  booking creation, Online mode only. UX copy notes the meet.jit.si moderator sign-in requirement.
- **Notifications:** tutor gets immediate in-app + email with the penalty-free-cancel deadline
  stated; tutee gets confirmation with Meeting Link / Preferred Location and the same deadline;
  the chat thread is auto-created/surfaced with a neutral system message. Born-late bookings
  (created inside the final 12h) are flagged at booking time as never penalty-free to cancel.
- **Teardown:** approve/reject endpoints and `TutorRequestedSessions.vue` removed outright.
  `Pending` is never assigned to new bookings but survives as a historical status value. At
  cutover, existing Pending bookings are auto-expired with a rebook-instantly notification.

## Steps

1. **Backend — booking creation becomes confirmation.** `confirm_payment_and_book` creates
   bookings as `Confirmed`, enforcing the three tutor gates plus the Booking Horizon; generate
   the Meeting Link for Online bookings; fire tutor email + both notifications; create/surface
   the chat thread with the system message.
2. **Backend — cancellation rework.** Add Grace Cutoff logic to `cancel_booking`: pre-cutoff
   cancellations unchanged; post-cutoff cancellations auto-open the system-opened Support Ticket
   category. Admin resolution gains the excused/counted verdict, the P50 tutor wallet deduction,
   strike counting, and the Monthly Strike Cap suspension effects.
3. **Backend — search visibility.** Extend the tutor search-visibility conditions with negative
   wallet, load limit, strike-cap suspension; add the tutee booking block at cap.
4. **Backend — teardown + migration.** Remove `approve_booking` / `reject_booking` and their
   URLs; data migration expiring existing Pending bookings with notification.
5. **Frontend — booking flow.** TutorDetails confirm step becomes instant-confirmation UX
   (Meeting Link on success screen, deadline copy, born-late warning); FindTutors respects the
   14-day horizon.
6. **Frontend — tutor surfaces.** Delete `TutorRequestedSessions.vue` and its route/nav; upcoming
   sessions get the cancel-before-cutoff affordance; load-limit invisibility banner on the tutor
   dashboard.
7. **Frontend — admin surfaces.** Late-cancellation ticket category in the support queue with the
   excused/counted resolution control; strike count visible in Tutor Management.
8. **Docs.** Update `docs/architecture/booking-flow.md`; session summary on completion.

## Risks

- **Status-model blast radius:** `Pending` is woven through Display Status, chat services, seed
  and demo-reset data, dashboards, and tests — grep-driven cleanup, easy to miss a surface.
- **Race conditions at booking creation:** two tutees booking the last slot / the load-limit
  boundary concurrently; needs the same `select_for_update` discipline `approve_booking` had.
- **Timezone correctness for the Grace Cutoff:** cutoff comparisons must use Manila time
  consistently with existing booking-time validation.
- **meet.jit.si moderator sign-in:** first participant must authenticate; mitigated by UX copy,
  but worth a live test before demo day.
- **Small-cohort penalty tuning:** P50 / 3-per-month are first guesses; admin excusal is the
  relief valve, but watch the ticket queue volume after rollout.

## Checks to run

- `python manage.py test` — booking creation (gates, horizon, born-late flag, meeting link),
  cancellation (pre/post cutoff, ticket creation, strike effects, cap suspension), teardown
  (approve/reject endpoints gone, Pending migration).
- `npm run lint` and `npm run build` — clean.
- Manual: book → instant confirmation with link → tutor email + chat system message; late-cancel
  → ticket appears in admin queue → counted verdict deducts P50 and increments strike.

## Changelog

- **2026-07-15** — Plan created from the grilling session; status Approved. ADR 0008 and
  CONTEXT.md glossary entries (Instant Booking, Grace Cutoff, Late Cancellation, Counted Strike,
  Monthly Strike Cap, Booking Horizon, Meeting Link) written alongside.
- **2026-07-16** — Compiled `docs/briefs/2026-07-16-instant-booking.md` for Codex on
  `feat/instant-booking` (branched off `main`); status moved to In Progress. No `docs/tickets.md`
  entry existed for this plan, so the brief covers all 8 steps directly. Dispatch to Codex not
  yet run.
- **2026-07-16** — `/codex-review`: Codex delivered booking-time confirmation with all three gates
  plus the Booking Horizon and Meeting Link (step 1), Grace Cutoff cancellation with system-opened
  Late Cancellation tickets and admin excused/counted resolution with strike/wallet effects
  (steps 2, 2b), the search-visibility gate extension (step 3), the approve/reject teardown and
  Pending-expiry migration (step 4), the confirmation-UX and Booking Horizon UI (step 5), route/nav
  teardown plus the load-limit banner (part of step 6), and the architecture doc update (step 8).
  Verified independently: full suite reproduces its pre-existing 28 failures/5 errors identically
  on a clean `main` (confirmed by stashing), `npm run lint`/`build` clean, migration has no drift.
  Fixed two dead-code nits myself (leftover `approve_booking`/`reject_booking` bodies; leftover
  `approveSession`/`rejectSession` store methods hitting the removed routes) and a magic-number
  duplication in `mailer.py`. Committed in three stops (backend, frontend, docs). Opened Fix round
  1 in the same brief for the rest: the tutor cancel-before-cutoff affordance, all of step 7
  (admin surfaces), and missing test coverage for steps 2/2b/3. Status stays In Progress.
- **2026-07-16** — Built a team handoff (`/ui-preview`) summarizing Instant Booking plus the
  unrelated subject-catalog/tutor-proposed-subjects work (recommender changes excluded, already
  covered by their own handoff). Promoted to `docs/mockups/2026-07-16-bookings-subjects-handoff.html`
  and linked above.
