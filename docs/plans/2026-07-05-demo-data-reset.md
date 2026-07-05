---
title: Demo data reset (thesis defense seed)
date: 2026-07-05
status: Approved
spec:
---

# Demo data reset (thesis defense seed)

<!-- LIVING SUMMARY: keep this section and the Changelog current on every edit -->

**Status & Progress Summary** (2026-07-05): Approved, not yet started. Plan captures 19 decisions
from a full grilling session (DB scope, targeted clear, multi-institution, booking-lifecycle
coverage, named CBF/CF personas with engineered rating clusters, tutor rating/schedule coverage,
scheduling load-limit demo, compensation/wallet data, activity feed, subject depth, and a
growth-shaped ~60-day backdating scheme) plus technical gotchas found while reading the actual
recommender/admin-dashboard code (day-of-week booking bug, `auto_now_add` backdating trap, CF
Pearson math requiring ≥2 shared differentiated ratings, money reconciliation). No code written
yet.

## Goal

Replace the ad-hoc, purely-additive `seed_data.py` with a new, destructive-and-deliberate
`reset_demo_data` management command that clears the local dev database of demo-seedable data and
reseeds it so every one of the thesis's 5 Specific Objectives has real, discoverable data to
demonstrate during the defense — not just plausible-looking bulk data, but named, memorable
scenarios an examiner can be walked through live.

## Approach

**Scope discipline.** Target the local/dev Postgres DB only (never the deployment DB in this
pass). Do a *targeted* clear — delete demo-seedable domain data but preserve existing
SuperAdmin/Admin logins — rather than a full `flush`. Ship as a brand-new command,
`reset_demo_data.py`, leaving `seed_data.py` untouched.

**Named personas over pure randomness.** A large randomized pool (400 users total) proves scale,
but an examiner needs to find specific, repeatable scenarios by name. So: a bulk "filler" pool
(random Faker data, 100 tutees + 100 tutors per institution) coexists with a small set of
hand-picked, fixed-name personas for CPU that each map to one objective or recommender scenario.
North University (the second institution) gets bulk data only — its role is to prove institution
scoping/isolation, not to duplicate every scenario.

**Objective-to-data mapping:**

| Objective | Data needed | Personas |
|---|---|---|
| 1. Localized platform (institution scoping) | Two institutions (CPU, North University — `north.edu.ph`), each with its own Admin login and fully separate tutor/tutee pools | Both Admin logins |
| 2. Hybrid Recommendation (CBF + CF) | Correlated rating clusters producing real Pearson signal; a Cold-Start case; a CBF/CF agreement case; a CBF/CF divergence case | Bea Santos, Carlo Reyes, Diane Cruz, Miguel Torres, Elena Bautista |
| 3. Scheduling (workload/limits) | Varied tutor availability patterns; two tutors carrying in-flight bookings at/near their Accepted Session Load Limit | Grace Domingo (10/10, blocked), Paolo Ramirez (8/10, near-limit) |
| 4. Compensation | Wallets, Transactions (session_credit + commission_deduction), Withdrawal Requests across all outcome states incl. one near the ₱50,000 InstaPay cap | Isabel Fernandez |
| 5. Reporting & Analytics | ~60 days of backdated, growth-shaped booking/signup/transaction history so trend charts and per-tutor session history look earned, not fabricated in one instant | (all of the above, via backdated timestamps) |

**Fix, don't inherit, existing bugs.** The current `seed_data.py` has three latent bugs the new
script must not repeat: it never matches a `Booking.session_date` to the actual weekday of the
`TutorAvailability` slot being booked; it uses `date.today()` instead of
`timezone.localtime(timezone.now()).date()` (can drift from what the admin views consider
"today"); and several models use `auto_now_add` (`Transaction.created_at`,
`PlatformActivity.created_at`, `WithdrawalRequest.requested_at`) which silently ignores any
backdated value passed at creation — these need a second `.update()` call after creation to
actually backdate them. `User.date_joined` is a plain `default=timezone.now` field and *can* be
set directly at creation.

**CF signal requires engineering, not just randomness.** `CF.py`'s Pearson `sim()` returns 0 when
two students share fewer than 2 rated tutors, or when they rate every shared tutor identically
(zero variance). Cluster personas must share **at least 2 rated tutors with differentiated
scores**, deliberately assigned — not left to the generic random booking/rating loop.

**Documentation.** A companion testing guide (`docs/artifacts/2026-07-05-demo-data-testing-guide.md`)
ships alongside the code, listing every login (SuperAdmin, both Admins, all named personas) and
step-by-step instructions for demonstrating each objective.

## Steps

1. **Fix the stale glossary entry.** `CONTEXT.md`'s "Payout Destination" entry says it's "stored as
   `TutorPayoutAccount`," but migration `0063_remove_tutorpayoutaccount.py` shows that model was
   removed — `WithdrawalRequest` now stores `account_number`/`account_name`/`bank_name`/
   `receiving_institution_*` directly. Correct the entry before touching seed code.

2. **Scaffold `backend/studybuddy/management/commands/reset_demo_data.py`.** Fixed `Faker.seed()`
   / `random.seed()` for reproducibility. Structure as clearly labeled phases (clear → catalog →
   institutions/admins → users → tutor setup → bookings/ratings → money → activity feed →
   summary print).

3. **Targeted clear.** Delete, in FK-safe order: `Rating`, `Payment`, `Booking`,
   `TutorAvailability`, `TutorSubjects`, `Preference`, `WithdrawalRequest`, `WalletTopUp`,
   `Transaction`, `Wallet`, `Tutor`, `TutorApplication`, `TuteeApplication`, `InstitutionRequest`,
   `PlatformActivity`, and `UserProfile`/`User` rows where `role in ('Tutee', 'Tutor')`. Explicitly
   exclude `role in ('Admin', 'SuperAdmin')` from deletion. Leave `Strand`/`Course`/`Subjects`/
   `PaymentMethod`/`PartnerInstitution` alone (reseeded via `update_or_create` next, matching the
   existing script's idempotent pattern).

4. **Reseed catalog data.**
   - Subjects: give every grade level (1–6 elementary, 7–10 JHS) a full, grade-appropriate core
     set (English, Math, Science, Filipino, Araling Panlipunan/Social Studies); keep SHS tracks
     (STEM/ABM/HUMSS/GAS) but verify subjects are actually level-appropriate; give BSCS/BSIT/BSBA
     explicit 1st–4th-year subject coverage (no new college courses added).
   - `PartnerInstitution`: CPU (`cpu.edu.ph`, existing) + **North University** (`north.edu.ph`,
     new).
   - `PaymentMethod`: unchanged (CASH, online).

5. **Ensure Admin accounts.** One `role='Admin'` UserProfile scoped to each institution (reuse
   `make_superadmin.py`'s profile-default pattern), created only if missing — never delete an
   existing one. Print login credentials in the final summary.

6. **Bulk-create the filler tutee/tutor pool** — 100 tutees + 100 tutors per institution (400
   total). For each profile: `year_level` scoped correctly to its actual course tier (Elementary
   1–6, JHS 7–10, SHS 11–12, College 1–4 — never a flat `[1,2,3,4]` pool regardless of course).
   Explicitly build the tutor pool to mirror the tutee pool's tier/department distribution, so
   every tutee tier has a legitimately matching tutor. Backdate `User.date_joined` across the last
   ~60 days with a growth-shaped weighting (more signups in recent weeks than 2 months ago).

7. **Insert named CPU personas** (fixed names, checked for no collision with the Faker filler
   pool):
   - **Bea Santos** (Cold-Start Tutee) — Preference set with strong subject/course/year overlap
     against Miguel Torres; zero bookings, zero ratings.
   - **Carlo Reyes** (CBF+CF Agreement) — part of "Cluster A" (6–8 tutees) with correlated ratings
     reinforcing Miguel Torres as the top pick both by CBF and CF.
   - **Diane Cruz** (CBF/CF Divergence) — CBF's top pick for her profile is Miguel Torres, but her
     Top-K Neighbors ("Cluster B") have rated Elena Bautista highly and Miguel Torres poorly,
     pulling the Hybrid Score ranking toward Elena Bautista despite the weaker CBF fit.
   - **Miguel Torres** (Tutor Alpha) — strong CBF fit for the Cluster A/B tutees' course/subjects/
     year; well-rated by Cluster A, poorly rated by Cluster B.
   - **Elena Bautista** (Tutor Beta) — weaker CBF fit for Diane specifically, but beloved by
     Cluster B — the CF-override target.
   - **Nico Villareal** (Tutor Zero) — brand-new, zero sessions/ratings — the empty-state tutor.
   - **Grace Domingo** (Tutor Fully-Booked) — in-flight `Confirmed`/`Awaiting Payment
     Verification` bookings totaling exactly her Accepted Session Load Limit (10/10) — new booking
     requests against her should be blocked.
   - **Paolo Ramirez** (Tutor Near-Limit) — in-flight bookings at 8/10 — not yet blocked, for
     contrast.
   - **Isabel Fernandez** (Tutor High-Earner) — many `Completed` sessions, a large Wallet balance,
     and a `WithdrawalRequest` near (but not over) the ₱50,000 InstaPay cap.

8. **Assign `TutorSubjects` + `Preference`.** Keep the ~15% zero-rating/zero-session carve-out
   (~30 of the 200 tutors, drawn only from the filler pool plus Nico Villareal — never from a
   persona whose story requires ratings). Leave 1–2 specific subjects with tutee demand but zero
   tutor supply, so the admin dashboard's subject-demand "gap" indicator has a real case. Give
   named personas their designed subject overlaps explicitly.

9. **Generate `TutorAvailability`** with deliberately varied patterns (wide/narrow/evening-only/
   weekend-only) instead of the current uniform random range — via `bulk_create`, not
   per-slot `get_or_create`, to keep this fast at 200 tutors. No `TutorAvailabilityOverride` rows
   (explicitly out of scope per decision).

10. **Seed the general Booking pool** — terminal-only outcomes (`Completed`/`Cancelled`/
    `Rejected`, no in-flight bookings) with `session_date` values that actually fall on the
    booked slot's weekday (fixing the existing day-of-week bug), computed via
    `timezone.localtime(timezone.now()).date()` (not raw `date.today()`), backdated over ~60 days
    with the same growth-shaped weighting as signups. Grace Domingo and Paolo Ramirez get their
    in-flight exception bookings here instead.

11. **Seed `Rating`** only for `Completed` bookings. Cluster A and Cluster B ratings are assigned
    deliberately (not via the generic random loop) so each cluster shares **at least 2 rated
    tutors with differentiated scores** — the minimum needed for `CF.py`'s Pearson `sim()` to
    produce a non-zero signal. Recompute `Tutor.rating_average`/`total_sessions` after.

12. **Seed Compensation data.** `Wallet.balance` = 90% of completed-session gross revenue minus
    already-`processed` withdrawal amounts; `Wallet.pending_amount` reflects any `pending`
    withdrawal. `WithdrawalRequest` rows spread across `pending`/`processed`/`rejected`/`failed`,
    including Isabel Fernandez's near-cap (≤ ₱50,000) one. `Transaction` rows
    (`session_credit` per completed session, `commission_deduction` at 10%) backdated — via
    `.update()` after creation, since `created_at` is `auto_now_add` — into the current calendar
    month so `AdminStatsView`'s `commissions_this_month` stat isn't ₱0.

13. **Seed the activity feed / operational queue.** `PlatformActivity` entries backdated (same
    `.update()`-after-create technique) to match the events they describe; a handful of pending
    `TutorApplication`/`TuteeApplication`/`InstitutionRequest` rows so the admin's operational
    queue isn't empty.

14. **Print a final summary** to stdout: counts for every model touched, plus a credentials table
    (SuperAdmin, both institution Admins, all 9 named personas) and each persona's one-line
    "what this proves."

15. **Write the testing guide** at `docs/artifacts/2026-07-05-demo-data-testing-guide.md`:
    login table + step-by-step walkthroughs for each objective (institution-scoped views via both
    Admin logins; CBF/CF divergence via the Algorithm Demo Tool using Bea/Carlo/Diane; the
    load-limit block by attempting a new booking against Grace Domingo; wallet/withdrawal states
    via Isabel Fernandez; the enrollment trend, top-tutors, and subject-demand-gap panels on both
    dashboards; `TutorSessionsReports.vue` for a persona with 2 months of history).

## Risks

- **Performance at 400 users.** Per-row `get_or_create` loops (especially `TutorAvailability`,
  currently ~24–36 rows per tutor) will be slow at 200 tutors — must use `bulk_create` where the
  existing script uses per-row `get_or_create`.
- **`auto_now_add` silently defeats backdating.** Any field using it (`Transaction.created_at`,
  `PlatformActivity.created_at`, `WithdrawalRequest.requested_at`) needs the create-then-`.update()`
  workaround; forgetting it makes every timestamp show "now," quietly breaking the growth-story
  trend charts and the commissions-this-month stat.
- **CF math gotcha.** A cluster persona sharing only 1 rated tutor with their "neighbors" (or
  rating everything identically) will always produce Pearson similarity 0 — silently killing the
  CBF/CF-divergence demo without any error. Must verify the cluster design actually satisfies the
  ≥2-shared-differentiated-ratings requirement before trusting the demo.
- **Persona pool collisions.** The ~15% zero-rating carve-out, the load-limit personas, and the
  CF-cluster target tutors must be drawn from disjoint pools — accidentally double-casting a
  persona (e.g. a "zero-rating" tutor who's also supposed to be Cluster A's beloved pick) breaks
  the story.
- **Money reconciliation.** `Wallet.balance`/`pending_amount` must actually net out against
  `Payment`/`Transaction`/`WithdrawalRequest` history, or the numbers won't hold up if someone
  checks the math live during the defense.
- **Destructive command safety.** `reset_demo_data` deletes real rows. It must never be pointed at
  anything but the local dev database in this pass — no code path in this command should make it
  easy to accidentally run against a deployment DB.
- **Booking unique constraint.** `unique_active_booking_per_slot_date` restricts one
  active (`Confirmed`/`Awaiting Payment Verification`/`Completed`) booking per (slot, date); at
  higher volume the random-assignment loop will collide more often and must handle retries/skips
  gracefully without silently under-shooting the target counts by too much.

## Checks to run

- `python manage.py migrate` — confirm the dev DB schema is current before seeding (session load
  limit, Wallet, WithdrawalRequest, PlatformActivity, etc. all need to exist).
- `python manage.py reset_demo_data` — review the printed summary counts and credentials table for
  sanity (no zeros where there shouldn't be any, no exceptions).
- `python manage.py test studybuddy` — confirm nothing about the new data shape breaks existing
  tests, in particular `RecommenderNeighborReuseTests`, `InstitutionScopedMatchingTests`,
  `AdminDashboardMetricsTests`, `AlgorithmDemoToolTests`.
- Manual browser check: SuperAdminDashboard.vue and AdminDashboard.vue — enrollment trend isn't
  flat, top tutors populated, subject-demand gap indicator shows for the deliberately-unmet
  subject(s), commissions-this-month is non-zero.
- Manual browser check: Algorithm Demo Tool — run Bea Santos (expect Cold-Start badge), Carlo
  Reyes (expect CBF+CF agreement on Miguel Torres), Diane Cruz (expect CF pulling the ranking
  toward Elena Bautista despite Miguel Torres's stronger CBF fit).
- Manual browser check: attempt a new booking against Grace Domingo as the tutor — confirm it's
  blocked by the Accepted Session Load Limit; Paolo Ramirez should still accept.
  history and `Wallet.balance`.
- Manual browser check: `TutorSessionsReports.vue` for a persona with backdated history — confirm
  session history and earnings actually look historical, not created at a single instant.

## Changelog

| Date | Change |
|------|--------|
| 2026-07-05 | Created plan from a full grilling session (19 decisions) covering DB scope, multi-institution setup, booking-lifecycle coverage, named CBF/CF personas with engineered rating clusters, tutor rating/schedule coverage, scheduling load-limit demo, compensation/wallet data, activity feed, subject depth, and growth-shaped backdating. Status: Approved. |
