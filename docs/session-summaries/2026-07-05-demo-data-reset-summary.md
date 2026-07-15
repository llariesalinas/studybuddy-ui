# Demo data reset (thesis defense seed) — summary

Plan: [docs/plans/2026-07-05-demo-data-reset.md](../plans/2026-07-05-demo-data-reset.md)
Testing guide: [docs/artifacts/2026-07-05-demo-data-testing-guide.md](../artifacts/2026-07-05-demo-data-testing-guide.md)

## What shipped

A new Django management command, `backend/studybuddy/management/commands/reset_demo_data.py`,
that replaces the ad-hoc `seed_data.py` for demo/deployment prep. It's destructive (local/dev
only): deletes all Tutee/Tutor users and everything cascading from them (bookings, ratings,
wallets, subjects, availability, applications), preserves existing Admin/SuperAdmin logins
untouched, then reseeds:

- **Two institutions** — CPU (`cpu.edu.ph`) and a new North University (`north.edu.ph`) — each
  with its own Admin login and a fully separate 100-tutee/100-tutor pool, proving institution
  scoping (Objective 1).
- **Full-depth, grade/year-appropriate subjects** — every grade 1–10 gets a core set (English,
  Math, Science, Filipino, Araling Panlipunan); BSCS/BSIT/BSBA get subjects for all 4 college
  years; `year_level` is scoped correctly per tier instead of a flat 1–4 pool regardless of course.
- **11 named personas** (all CPU) mapped to specific recommender/objective scenarios: 3 tutees
  (Bea/cold-start, Carlo/CBF-CF-agreement, Diane/CF-override) and 8 tutors (Miguel/Elena as the
  CBF/CF-divergence pair, two CF "anchor" tutors that make Pearson similarity meaningful,
  Nico/empty-state, Grace+Paolo/scheduling-load-limit, Isabel/compensation).
- **Wallet/withdrawal/transaction data** that reconciles: session credits, 10% commission
  deductions, a top-up, and withdrawals across every outcome state (pending/processed/rejected/
  failed/flagged), one deliberately under the ₱50,000 InstaPay cap.
- **~60 days of growth-shaped backdated history** (signups, bookings, transactions, activity feed)
  so trend charts rise toward the present instead of looking flat or freshly fabricated.
- A subject demand/supply gap (2 subjects with tutee demand and zero tutor supply) for the admin
  dashboard's gap indicator, and a populated operational queue (8 pending applications, 1 pending
  institution request).

## Deviations from the plan

- **Cluster design bug found during verification, not anticipated in the plan.** The plan called
  for "≥2 shared rated tutors with differentiated scores" per cluster but didn't specify the two
  clusters needed *opposing* patterns. The first implementation gave both clusters the same
  anchor-rating pattern (both liking anchor1, disliking anchor2) — Pearson similarity couldn't
  separate them, Top-K Neighbors mixed both clusters, and Diane's CF-override scenario silently
  failed (Elena did not outrank Miguel). Fixed by inverting Cluster B's anchor pattern; re-verified
  via shell that all three scenarios now produce the intended rankings.
- **Discovered, not planned: application-approval gate.** `can_create_new_booking()` blocks any
  tutor/tutee without an `approved` application and a `verified` document-renewal status — without
  this, no persona or filler tutor could accept a booking at all, silently breaking every booking
  scenario. Added `_approve_applications()` seeding approved applications (reviewed within the
  90-day renewal window) for every generated profile.
- **Discovered, not planned: pending-queue applications need dedicated accounts.** A tutor/tutee
  with a `pending` application would itself be blocked from booking activity, so the "populate the
  operational queue" step (plan step 13) uses separate `applicant.*@...` accounts with no Tutor/
  booking history, rather than repurposing existing pool members.
- **Discovered, not planned: legacy subject cleanup.** The full-depth subject rebuild replaces the
  old sparse `subjects_data` list; added an explicit delete of any `Subjects` row not in the new
  set so stale codes don't linger in dropdowns after a reseed.
- **Environment quirk, not a code issue**: the local Postgres sits behind a Supavisor connection
  pooler that kept an idle connection open to `test_postgres`, blocking Django's normal drop/
  recreate test-DB step. Resolved by running the test suite with `--keepdb` rather than fighting
  the pooler.

## Checks run

- `python manage.py migrate --check` — clean, no pending migrations.
- `python manage.py reset_demo_data` — ran twice (once to catch the cluster bug, once after the
  fix); final run: 446 users, 90 subjects, 6,580 availability slots, 1,341 bookings (1,079
  completed, 18 in-flight for the load-limit demo, remainder cancelled/rejected), 940 ratings,
  2,159 transactions, 6 withdrawal requests, 37 activity-feed entries, 5 pending applications.
- Manual verification via `manage.py shell` of `recommend_tutors_hybrid` for all three named
  tutee personas — confirmed exact rankings and scores documented in the testing guide (Bea:
  CF `None`; Carlo: Miguel hybrid 0.938; Diane: Elena 0.776 > Miguel 0.749).
  Load limit confirmed via `Tutor.accepted_session_load()`: Grace 10/10, Paolo 8/10.
  Wallet reconciliation confirmed by hand: Isabel's balance (₱18,800) matches gross-minus-
  commission-plus-topup-minus-withdrawals exactly.
- `python manage.py test studybuddy --keepdb --noinput` — 259 tests, 14 failures + 2 errors,
  identical count to the documented pre-existing baseline (avatar upload compression, dashboard
  recommendation tests) and confirmed structurally unrelated since tests run against a separate
  test database this command never touches.

## Not done in this pass

- No frontend changes — this was backend/data-only.
- No `TutorAvailabilityOverride`, Support Ticket, or chat message seeding (explicitly declined
  during grilling).
- Not run against the deployment database — this pass targeted local/dev only, as decided.
