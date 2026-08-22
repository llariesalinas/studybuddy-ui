# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

**Students at Central Philippine University (CPU).** Registration is restricted to partner email
domains (`cpu.edu.ph` and similar) unless `UserProfile.is_domain_exempt` is set, so the audience is
institutionally bounded by design rather than open to the public.

Two student-facing roles, and **one account can hold both**:

- **Tutee** - a student looking for help in a specific subject, working from a set of preferences
  (subject, availability, level) toward a booked session.
- **Tutor** - a student offering expertise, managing published availability, a wallet balance, and a
  verification status that gates whether they appear in search at all.

Neither side is subordinate. Dual-role accounts are a shipped capability, not a special case, so a
change that improves the tutee path at the tutor path's expense (or the reverse) is a regression for
the users who are both.

**Admin and SuperAdmin** are staff roles, not students: application review, support tickets, reports,
and recommender weight tuning. SuperAdmins are excluded from mode switching outright, because
`get_login_profile_for_user` force-resets staff back to SuperAdmin on every login.

## Product Purpose

Connect CPU students who need help in a subject with CPU students who can teach it, and carry the
pair all the way through discovery, booking, payment, the session itself, and its aftermath.

Success is a completed, paid tutoring session between two students who would not otherwise have found
each other - and a system that handles the failure cases (no-shows, late cancellations, disputes)
without an administrator having to adjudicate every one by hand.

## Positioning

Three things a general-purpose tutoring marketplace could not truthfully copy:

1. **Institutional gating as a trust mechanism.** Domain-validated registration means every
   participant is verifiably a CPU student. Identity is established by the institution rather than by
   reviews or badges.
2. **Instant booking rather than request-and-approve.** A tutee booking inside a tutor's published
   availability is confirmed immediately (ADR-0008). There is no tutor accept/reject step. Tutor
   protection is post-hoc - a penalty-free grace window, then a self-serve late cancellation that
   opens a support ticket - rather than a gate in front of every booking.
3. **A recommender the institution can tune.** The hybrid content-based/collaborative ranking is not
   a fixed formula: a SuperAdmin edits both the blend and the six CBF component weights from
   Algorithm Settings, and the stored values are relative and normalised at score time.

## Operating Context

**This is a capstone project under panel evaluation.** That is the operating reality that shapes
current priorities, and it has concrete consequences future work must respect:

- **Panel comments are the requirements source.** Work is scoped from a list of comments raised at
  review. The list is currently split between this developer and a teammate, and the split exists to
  prevent file collisions - taking work outside the agreed share causes merge conflicts, not just
  scope creep.
- **Demo legibility matters as much as correctness.** A feature that works but cannot be shown
  working in a defense is incompletely delivered. Screens gated behind environment flags need those
  flags identified alongside the feature.
- **The product is nonetheless built to be handed over.** Durable product truth in this file is not
  demo-shaped, and shortcuts taken for a demo belong in plan and summary documents where they can be
  found and reversed.

Operationally: sessions and times are Manila timezone; money is Philippine pesos; the deployed demo
runs on Render with a remote Supabase Postgres behind it.

## Capabilities and Constraints

**Booking.** Instant confirmation via `POST bookings/confirm/`. Double-booking is prevented
server-side by `select_for_update()` inside `transaction.atomic()`, backstopped by a database
`UniqueConstraint` on `(availability, session_date)` for active statuses. `Pending` survives only as
a historical status value on old rows; no new flow may depend on a tutor-approval step.

**Cancellation and penalties.** A 12-hour **Grace Cutoff** allows penalty-free cancellation. After
it, a self-serve **Late Cancellation** auto-opens a support ticket for admin review, resolved as
excused or as a **Counted Strike** - a flat PHP 50 wallet deduction for tutors, none for tutees.
Three strikes in a calendar month suspends booking and search visibility.

**Tutor eligibility.** Verification status, a non-negative wallet, and the Accepted Session Load
Limit gate booking creation and are surfaced by hiding the tutor from search, with a server-side
check as the authoritative backstop.

**Recommendation.** `hybrid_score = cbf_weight * cbf_score + cf_weight * (cf_score / 5)`. Weights are
admin-editable defaults, not constants; `recommender/weights.py` is the single source of truth.
Anything iterating over tutors must load weights once per request and pass them down.

**Session and identity.** JWT with silent access-token refresh; concurrent 401s coalesce into a
single refresh. Idle users are signed out. Login is OTP-gated, which is currently wired to the same
switch as email delivery (`LOGIN_OTP_DISABLED` is hard-wired to `EMAIL_DELIVERY_DISABLED`) - this is
known and is itself an open panel comment.

**Also shipped:** wallet, real-time chat (Django Channels), admin review queues, support tickets,
reports, and a compact density mode driven by CSS `zoom`.

**Explicitly undecided:** whether the OTP requirement is removed or made independently configurable;
the cause of the reported category-logic defect.

## Brand Commitments

- The product is **StudyBuddy**, built for and named around **Central Philippine University**. The
  institutional affiliation is a factual constraint, not a theme.
- **No emojis** anywhere - product copy, code, comments, commit messages, or documentation.
- Voice in the interface is plain, second-person, and non-patronising: it explains consequences
  ("your existing Tutee account stays exactly as it is") rather than issuing instructions.
- Money is always shown in Philippine pesos; times are always Manila.

## Evidence on Hand

- **Seeded development data only.** `python manage.py seed_data` populates demo tutors, tutees, and
  sessions. There are **no real students, no real sessions, no testimonials, no usage metrics, and no
  press**. Future work must not fabricate any of these, including as placeholder copy in a mockup
  that could be mistaken for real.
- Design and architecture decisions are recorded in `docs/adr/`, plans in `docs/plans/`, and outcomes
  in `docs/session-summaries/`. The incumbent visual system is documented in `DESIGN.md`, which
  includes a deliberate `## Known drift` section.
- The demo deployment is real and reachable; its email delivery and demo-only tooling sit behind
  environment flags.

## Product Principles

1. **Trust comes from the institution, not from the interface.** Because every account is
   domain-verified, the product does not need reputation theatre - ratings, badges, and social proof
   are supporting detail, never the mechanism.
2. **Prevent the conflict in the system, apologise for it in the UI.** Double-booking is stopped by a
   database constraint; strikes are counted by the server. The interface's job is to explain what
   happened, not to be the enforcement layer.
3. **Neither role is the guest.** A dual-role account is one person. Any surface that treats one mode
   as the real product and the other as a bolt-on is wrong, and the mode control itself is the most
   visible test of this.
4. **Density is the honest answer.** These screens genuinely carry a lot at once - schedules,
   wallets, session states, rankings. The system holds an 11-14px working scale and leans on weight
   rather than whitespace. Making a screen airier by hiding information is a regression.
5. **Record drift rather than hiding it.** Known gaps are written down where the next person will
   read them. A document that claims more coherence than the code has is how the last real bug got
   shipped.

## Accessibility & Inclusion

No external compliance requirement or audit is in place, and none is claimed. Accessibility is held
as a **quality bar on new and reworked surfaces**: keyboard operability, visible focus, correct
semantics for custom controls, accessible names on dialogs, and announced state changes are expected
of work as it lands, not deferred to a later pass.

The system supports light and dark themes and a compact density mode, and suppresses its motion
vocabulary under `prefers-reduced-motion`. Dark mode is acknowledged in `DESIGN.md` as partial.
