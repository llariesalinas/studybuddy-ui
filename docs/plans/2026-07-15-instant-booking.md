---
title: Instant Booking
date: 2026-07-15
status: Approved
summary: Replace request-to-book with instant confirmation, Grace Cutoff cancellations, strike accountability, and auto-generated meeting links.
spec: ../adr/0008-instant-booking-replaces-request-to-book.md
---

# Instant Booking

## Status & Progress Summary

**Approved — not started.** Design settled in the 2026-07-15 grilling session; ADR 0008 and
glossary terms written. No implementation steps begun.

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
