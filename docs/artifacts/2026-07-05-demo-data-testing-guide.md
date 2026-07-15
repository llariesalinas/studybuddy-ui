# Demo Data Testing Guide (thesis defense)

Companion to [the demo data reset plan](../plans/2026-07-05-demo-data-reset.md). Everything below
assumes you have just run:

```
cd backend
venv\Scripts\python.exe manage.py reset_demo_data
```

The command is destructive (local/dev only): it deletes all Tutee/Tutor users and everything that
cascades from them, then reseeds. Admin and SuperAdmin logins are never touched. Re-running it is
safe and produces the same personas (fixed random seed).

## Logins

**Every demo account's password is `studybuddy123`.**

| Role | Login | Notes |
|---|---|---|
| SuperAdmin | `superadmin@studybuddy.test` | Preserved untouched by the reset — verified valid as of 2026-07-08 |
| Admin (CPU) | `demo.admin@cpu.edu.ph` | Scoped to Central Philippine University |
| Admin (North) | `demo.admin@north.edu.ph` | Scoped to North University |

### Named personas (all `@cpu.edu.ph`)

| Persona | Login | What they prove |
|---|---|---|
| Bea Santos (Tutee) | `bea.santos@cpu.edu.ph` | Cold-Start: no rating history, Hybrid = 0.7 × CBF |
| Carlo Reyes (Tutee) | `carlo.reyes@cpu.edu.ph` | CBF and CF agree on Miguel Torres |
| Diane Cruz (Tutee) | `diane.cruz@cpu.edu.ph` | CF overrides CBF: Elena outranks Miguel |
| Miguel Torres (Tutor) | `miguel.torres@cpu.edu.ph` | Strongest CBF fit; loved by Cluster A, panned by Cluster B |
| Elena Bautista (Tutor) | `elena.bautista@cpu.edu.ph` | Weaker CBF fit, but Cluster B's favorite — the CF-override target |
| Ramon Aquino (Tutor) | `ramon.aquino@cpu.edu.ph` | CF anchor #1 (creates the Pearson signal) |
| Cecilia Mercado (Tutor) | `cecilia.mercado@cpu.edu.ph` | CF anchor #2 (Pearson needs ≥ 2 shared rated tutors) |
| Nico Villareal (Tutor) | `nico.villareal@cpu.edu.ph` | Brand-new: zero sessions/ratings (empty-state UI) |
| Grace Domingo (Tutor) | `grace.domingo@cpu.edu.ph` | Accepted Session Load 10/10 — new accepts blocked |
| Paolo Ramirez (Tutor) | `paolo.ramirez@cpu.edu.ph` | Accepted Session Load 8/10 — still accepting |
| Isabel Fernandez (Tutor) | `isabel.fernandez@cpu.edu.ph` | High earner: top-ups + withdrawals in every state |

### Additional test accounts

| Persona | Login |
|---|---|
| Shelby Waller (Tutor) | `tutor.shelby.waller.cpu67@cpu.edu.ph` |
| Grace Domingo (Tutor) | `grace.domingo@cpu.edu.ph` |
| Paolo Ramirez (Tutor) | `paolo.ramirez@cpu.edu.ph` |

## Objective 1 — Localized platform (institution scoping)

1. Log in as `demo.admin@cpu.edu.ph` → the Admin dashboard shows only CPU tutors/tutees/sessions
   (institution name in the header stats).
2. Log in as `demo.admin@north.edu.ph` → same screens, entirely different numbers — North's own
   100 tutees / 100 tutors, none of CPU's data.
3. Log in as SuperAdmin → platform-wide totals (sum of both), with the optional institution
   filter narrowing to either.
4. Matching is institution-scoped too: any North tutee's recommendations only ever contain North
   tutors (the named personas are all CPU and never appear for North accounts).

## Objective 2 — Hybrid Recommendation (CBF + CF)

Use the SuperAdmin **Algorithm Demo** page (Ranked List / Compare Pair tabs). Search subject
`CS-211` context where relevant. Verified rankings as-seeded:

1. **Bea Santos — Cold Start.** Every tutor shows `CF: none` and the Cold Start badge. Top pick is
   Miguel Torres on pure CBF (hybrid 0.63 = 0.7 × 0.905). Talking point: CF's 0.3 weight is never
   reallocated, so a cold-start tutee's hybrid is capped below 0.7.
2. **Carlo Reyes — agreement.** Miguel Torres tops both halves: CBF 0.98 *and* CF 4.2 → hybrid
   0.94. Both signals point the same way.
3. **Diane Cruz — CF override.** Elena Bautista ranks **#1 (hybrid 0.776) despite a weaker CBF
   (0.705 vs Miguel's 0.925)** because Diane's Top-K Neighbors rated Elena 4.7 and Miguel 1.7.
   Use Compare Pair (Diane → Miguel vs Elena) to show the breakdown live.
4. **How the signal was built** (if the panel asks): two "anchor" tutors, Ramon Aquino and Cecilia
   Mercado, are rated by every cluster member with inverted patterns (Cluster A: Ramon high /
   Cecilia low; Cluster B: the opposite). Pearson similarity needs at least 2 shared, non-identical
   ratings — the anchors provide exactly that, and the inversion is what separates the clusters.
5. **Live rating edit (prove it updates in real time).** In Compare Pair, each contributing
   Top-K Neighbor row now has an editable rating input (1–5) and a Save button — no Django admin
   needed. With Diane Cruz → Elena Bautista selected, lower one neighbor's rating and Save: the
   CF bar, CF score, and Hybrid Score re-animate to new values with no page reload, and the tutor
   picker's score label updates too. Switch to Miguel Torres for the same tutee to show his
   breakdown is untouched by the edit — proves the change is scoped to the exact (student, tutor)
   pair, not a page-wide refresh. Gated by the same `ALGORITHM_DEMO_TOOLS_ENABLED` flag as the
   rest of this page; see
   [2026-07-08-algorithm-demo-live-rating-edit-design.md](../specs/2026-07-08-algorithm-demo-live-rating-edit-design.md).

## Objective 3 — Scheduling (availability, workloads, limits)

1. **Availability variety**: browse tutors in Find Tutors / schedule screens — schedules follow
   four archetypes (weekday-wide, standard 3-day, evening-only, weekend-only).
2. **Load limit blocked**: as any CPU tutee, try to book **Grace Domingo** — she is carrying
   10/10 accepted session groups (8 Confirmed + 2 Awaiting Payment Verification, all future), so
   accepting new work is blocked. As Grace (`grace.domingo@cpu.edu.ph`), an incoming pending
   request cannot be accepted.
3. **Near-limit contrast**: **Paolo Ramirez** sits at 8/10 and can still accept.
4. Admins can adjust a tutor's limit (1–20) from Tutor Management — raising Grace's limit unblocks
   her live.

## Objective 4 — Compensation

1. Log in as **Isabel Fernandez** → Wallet shows:
   - Balance **₱18,800**, pending **₱48,500**.
   - The math reconciles live: 60 completed sessions × ₱450 = ₱27,000 gross − ₱2,700 commission
     (10%) + ₱55,000 top-up − ₱12,000 processed withdrawal − ₱48,500 pending = ₱18,800.
   - The pending withdrawal (₱48,500) deliberately sits just under the ₱50,000 InstaPay cap.
2. Withdrawal states across the platform: `pending`, `processed`, `rejected` (account name
   mismatch), `failed` (receiving institution unavailable), `flagged` — visible in the admin
   Withdrawals screen.
3. Every completed+paid session produced a `session_credit` and a 10% `commission_deduction`
   transaction; the admin dashboard's "commissions this month" is non-zero because recent sessions
   fall inside the current calendar month.

## Objective 5 — Reporting & Analytics

1. **Admin dashboards** (both institutions): enrollment trend (14-day chart) rises toward the
   present — signups were backdated over ~60 days with growth-shaped weighting. Top tutors ranked
   by completed sessions (Isabel leads CPU with 60). Subject demand vs supply shows a real **gap**
   flag: `Disaster Readiness (GAS-DR)` and `Strategic Management (BUS-401)` have tutee demand and
   zero tutor supply.
2. **Tutor reports**: as Isabel (or any rated tutor), Sessions & Reports shows two months of
   historical sessions and earnings — dates spread across the window, not bunched at one instant.
3. **Operational queue**: 8 pending applications (5 tutor / 3 tutee, split across both
   institutions) + 1 pending institution request (`Western Visayas College`) populate the admin
   to-do feed; the activity feed carries ~37 backdated entries.

## Things to know / gotchas

- **Nico Villareal** and ~30 other tutors (15% of the pool) deliberately have zero sessions and
  zero ratings — that's the empty-state demo, not missing data.
- `CS-211`/`CS-212` are reserved to Miguel and Elena (no filler tutor teaches them) so the
  recommender scenarios stay top-ranked. Expect thin "supply" numbers for those two subjects.
- All bookings are terminal (`Completed`/`Cancelled`/`Rejected`) except Grace's 10 and Paolo's 8
  in-flight ones — those exist solely for the load-limit demo.
- Booking `session_date`s always fall on the actual weekday of the booked availability slot
  (a bug in the old seed script that this one fixes).
- All demo tutors have approved applications with verified documents (approved < 90 days ago);
  without that, tutors cannot accept bookings at all and the load-limit demo would be blocked by
  the wrong gate.
- Pending applications belong to dedicated "applicant" accounts (`applicant.*@...`) that have no
  tutor records — they exist only to populate the admin queue.
