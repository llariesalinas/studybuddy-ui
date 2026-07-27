---
title: Algorithm demo CF clarity, live what-if editing, and programming-core reseed
date: 2026-07-23
status: In Progress
summary: Make the CF half of the algorithm demo legible for the panel with a derivation waterfall, a top-5 weight table, server-side what-if rating edits, and a denser programming rating seed.
spec: ../mockups/2026-07-23-algorithm-demo-cf-waterfall.html
---

# Algorithm demo CF clarity, live what-if editing, and programming-core reseed

## Status & Progress Summary

**In Progress — steps 1, 2, 4, 5, 7 done; 8 and 9 partly done; 3 and 6 outstanding.** Design settled in a grilling session
on 2026-07-23; the visual is locked and promoted to
`docs/mockups/2026-07-23-algorithm-demo-cf-waterfall.html`, and the tier-1 rating matrix is
numerically validated against a mirror of `CF.py`. No open questions remain — the last one,
whether already-rated tutors should leave the demo candidate pool, resolved to **no** once both
production paths were traced (see Risks).

Done so far:
- **Step 1** — `compute_cf_breakdown` (`CF.py`) now returns every term of the prediction
  (`student_avg`, `student_rating`, `numerator`, `denominator`, and per-neighbour
  `neighbor_avg` / `deviation` / `weighted` / `co_rated_count`); `demo.py` passes them through.
- **Step 2** — `apply_rating_overrides` in `demo.py` plus `POST
  dev/algorithm-demo/recommend-whatif/` (`views.py`, `urls.py`) re-run the real recommender
  with overrides applied in memory and nothing written; `getAlgorithmDemoWhatIf` added to
  `src/services/api/algorithmDemo.js`.
- Four tests added to `AlgorithmDemoToolTests` covering the derivation payload, the what-if
  override changing the score while leaving the stored `Rating` untouched, out-of-range
  rejection, and the SuperAdmin/flag gate.
- **Step 4** — `AlgorithmDemoBreakdown.vue` rebuilt around the locked two-zone waterfall:
  per-neighbour similarity meter, rating slider and own-average, signed effect segment on a
  data-derived axis, the derivation formula line, a degenerate-overlap warning when
  `co_rated_count < 3`, and the accuracy callout when the tutee has already rated the tutor.
  `AlgorithmDemoRankedList.vue` owns the override list and re-scores through
  `getAlgorithmDemoWhatIf` on a 250ms debounce, with a "nothing saved" chip and a Reset
  control. Selection is held by `tutor_id`, so a tutor that changes rank stays selected, and
  the CBF stagger animation now replays only on tutor change rather than on every edit.

- **Step 5** — new `AlgorithmDemoWeightTable.vue` renders the top 5 candidates side by side:
  each cell carries the sub-score value with its weighted contribution beneath, shaded by
  sub-score so the weights that carried the ranking stand out, plus CBF total, CF with its
  pool badge (or Cold Start / no signal), and the hybrid score. Rows are clickable and drive
  the same `selectedTutorId` as the list, so the table and the waterfall stay in step.

- **Step 7** — `seed_data.py` gains tutors T6/T7/T8 (Data Structures + Algorithms, Web
  Development, SQL) and tutees S6-S10, and `CURATED_RATINGS` is replaced by the validated
  tier-1 matrix. S6 (Katrina Katigbak) is the CF protagonist; S1 is untouched and stays
  cold-start. Run against the local `postgres` database on 2026-07-24, destroying 512
  non-staff users / 747 ratings / 749 bookings and rebuilding them; the 20 staff and
  superadmin accounts survived as designed.
- **Step 8 (part)** — `_assert_tier1_co_rating_density` added to `_assert_guarantees`: every
  tier-1 pair must co-rate at least `MIN_CO_RATED` (3) tutors and no pair may land on a
  degenerate +/-1 similarity. Still outstanding: porting `validate_seed.py` into
  `backend/studybuddy/tests.py` so the invariant is checked without a reseed.

- **Step 9 (part)** — `docs/architecture/algorithm-demo-guide.html` updated: T6-T8 and S6-S10
  added to the curated cast with real logins, a new "Who to demo with" section explaining the
  tier-1 core and the co-rating threshold, the walkthrough rewritten around the top-5 table and
  the waterfall, and "Live rating edit" replaced by "What-if rating edits" describing the
  server-side override model. The existing CBF demo script still holds — S1's documented
  0.9333 for T1 was re-verified against the reseeded data. Outstanding:
  `docs/learning/2026-07-16-algorithm-demo-cheat-sheet.md`, and
  `docs/architecture/demo-data-testing-accounts.html` whose account IDs are stale post-reseed
  (flagged inline in the guide for now).
- **Regression found and fixed** — step 4 replaced the breakdown component's `rating-updated`
  emit with `override`, but `AlgorithmDemoPairPicker.vue` also renders that component and was
  still listening for the old event, leaving the Compare Pair tab's sliders inert. The pair
  picker now owns its own override list and re-scores through the same what-if endpoint, with
  the same chip and Reset control.

**Verified after reseed** (real recommender, not the mirror): for S6, T1 returns CF 4.742 with
neighbour similarities +0.970 / +0.853 / +0.852 / +0.308, co-rated counts 5/4/4/4, and one
backward pull of -0.25. Matches the pre-seed prediction to three decimals. T6 tops the ranking
at 0.949 ahead of T1's 0.927; a filler tutor holds the best CBF of all (0.935) but has no CF
signal and falls to 4th; S6's own rating of 5 on T1 makes the accuracy callout reachable. S1
returns `cold_start: True` on all 18 candidates.

**Not yet verified in a browser.** Step 4 is confirmed by lint and a production build only;
the demo page needs a running server, a SuperAdmin session and
`ALGORITHM_DEMO_TOOLS_ENABLED` to exercise visually, and the data it would show is still the
pre-reseed data whose similarities are all 1.00.

**Decision deferred to the user:** whether to also delete the backend
`algorithm_demo_update_rating` view, route and its six tests. The plan's step 3 named only the
frontend caller; removing the persisting endpoint outright is a wider change and it may still be
wanted for deliberately saving a rating during a demo. Left in place for now.

## Goal

The superadmin algorithm demo currently shows the Collaborative Filtering result as a single
bar and a list of neighbour names. For the oral defense the panel needs to see *how* CF
reaches its number, compare the top candidates' weights side by side, and watch the ranking
respond to a changed rating. The seeded rating data is also too thin and too uniform to
produce believable similarity values.

## Approach

Four decisions, settled in a grilling session on 2026-07-23:

1. **Two-zone waterfall** for CF (locked mockup: `docs/mockups/2026-07-23-algorithm-demo-cf-waterfall.html`).
   Each neighbour row splits into evidence (similarity meter, rating dots) and effect (a signed
   step on the 1-5 rating axis). Chosen over thickness-encoding and shared-axis variants because
   every quantity is read off its own labelled scale — nothing is encoded in a channel the panel
   has to decode.
2. **Top-5 weight comparison table** replaces the one-tutor-at-a-time view as the primary
   surface. Every cell shows the sub-score value with its weighted contribution beneath, shaded
   by contribution.
3. **Server-side what-if editing.** Rating edits are posted as in-memory overrides to a new
   endpoint that runs the real recommender and returns fresh rows. Nothing is written to the
   database. Chosen over a client-side JS recompute (which would be a second implementation of
   the algorithm, and indefensible when the panel asks whether it is real) and over the existing
   persist-and-refetch path (which mutates demo data irreversibly mid-defense).
   Default editing scope is **the selected tutor's ratings only**, which leaves similarity fixed;
   editing the co-rated ratings — which makes similarity live and can add or drop neighbours — sits
   behind an explicit advanced toggle.
4. **Tiered reseed** that deepens the programming cohort and leaves everything else alone.

### Why the seed has to change

`sim()` computes Pearson over the co-rated intersection only (`CF.py:37`). Pairs sharing one
tutor score 0 and are dropped by the `sim > 0` threshold (`CF.py:59-61, 81-86`); pairs sharing
exactly two always score exactly +/-1. The current `CURATED_RATINGS` (`seed_data.py:118-121`)
gives S2, S3 and S4 exactly two co-rated tutors each, so **every similarity in the curated set
is exactly 1.00** — a wall of identical values that teaches the panel nothing.

Separately, S1 (the tutee the seeder's comments describe as the CF protagonist) appears in no
`CURATED_RATINGS` row and is exempt from the ratings-given guarantee (`seed_data.py:622`), so
S1 is absent from the rating matrix and returns `cold_start: True` for every candidate. S1 is
kept as-is and reframed as the deliberate cold-start showcase; a new S6 becomes the CF
protagonist.

### Validated tier-1 matrix

Eight BSCS tutees across six programming tutors, with opposed taste archetypes. Verified
against a mirror of `CF.py` (`scratchpad/validate_seed.py`, to be promoted into the test suite):

```
overlap:      0 pairs below 3 co-rated
similarity:   S10 +0.970 | S2 +0.853 | S3 +0.852 | S4 +0.308
              S7 -0.490, S9 -0.800, S8 -0.962 correctly excluded
CF for T1:    3.80 + (+2.811 / 2.983) = 4.742
              S10 +0.97 | S2 +0.85 | S3 +1.07 | S4 -0.08  (one backward pull)
```

## Steps

1. **Extend the demo payload.** Add `student_avg` to the recommendation response and
   `neighbor_avg` plus `co_rated_count` to each neighbour row in `demo.py`, sourced from a
   widened `compute_cf_breakdown` return in `CF.py`. Without these the derivation cannot be
   rendered at all.
2. **Add the what-if endpoint.** `POST` tutee + rating overrides; apply them to the matrix from
   `build_rating_matrix()` in memory, run `hybrid_prediction_breakdown` unchanged, return the
   same row shape as the existing GET. No writes. Route through `src/services/api/algorithmDemo.js`.
3. **Retire the persisting edit path.** Remove `updateAlgorithmDemoRating` and the dead
   `rating-updated` emit (`AlgorithmDemoBreakdown.vue:115-128`), which is currently wired to no
   listener in `AlgorithmDemoRankedList.vue:113` and silently writes to the database with no
   visible effect.
4. **Build the two-zone waterfall** as the CF section of the breakdown component, per the locked
   mockup. Debounce edits at ~250ms.
5. **Build the top-5 weight table** with per-cell value and weighted contribution, and wire the
   re-rank transition with movement indicators.
6. **Add the advanced editing toggle** exposing co-rated ratings, off by default.
7. **Reseed.** Add the tier-1 programming core to `seed_data.py` (curated tutees S6-S10 and
   tutors T6-T8), keep tier-2 adjacent cohorts thin for the global-pool fallback demo, leave
   filler generation untouched.
8. **Assert the new invariant** in `_assert_guarantees`: every tier-1 peer pair co-rates at
   least 3 tutors, and no curated similarity is degenerate. Port `validate_seed.py` into
   `backend/studybuddy/tests.py`.
9. **Update the demo guide** (`docs/architecture/algorithm-demo-guide.html`) and the cheat sheet
   (`docs/learning/2026-07-16-algorithm-demo-cheat-sheet.md`) to match the new surface and the
   new protagonist.

## Risks

- **Reseeding is destructive.** `reset_demo_data` deletes every non-staff user and the whole
  subject catalog. It must not be run against anything but a local dev database, and the
  demo accounts doc (`docs/architecture/demo-data-testing-accounts.html`) needs re-checking
  afterwards since account IDs will change.
- **Ratings require bookings.** `Rating` is `OneToOneField(Booking)` (`models.py:1015`), so
  every added rating costs a seeded completed booking. Denser ratings mean proportionally more
  booking rows and slower seeding.
- **Advanced editing can empty the neighbour list.** Crossing the `sim > 0` threshold drops a
  peer entirely, and a tutor can flip between the peer pool and the global fallback mid-demo.
  Mitigated by defaulting the toggle off; do not enable it during the defense.
- **Already-rated tutors stay in the candidate pool — by design.** `_candidate_tutors`
  (`demo.py:61-74`) does not exclude tutors the tutee has rated, and neither do the two live
  production paths: `get_dashboard_recommendations` (`dashboard.py:114-116`) and
  `get_recommendation_candidate_tutors` (`views.py:3735-3760`). The only code that skips them is
  `recommend_tutors_cf` (`CF.py:201`), which is imported nowhere and is dead. The demo therefore
  matches production and must not be changed to exclude them.

  Two consequences to handle in the UI instead:
  1. CF predicts a rating for a tutor the tutee has already rated. Her rating shapes her
     baseline average but is never compared to the prediction, so a prediction of 4.33 can sit
     beside her own score of 2 and read as a bug. Surface it: badge the row and show her actual
     rating next to the prediction. This turns the artifact into a visible accuracy check on
     the algorithm — the strongest available defense moment.
  2. For such a tutor the target *is* in the co-rated intersection, so similarity re-runs on
     edit and neighbours can reorder or drop below the `sim > 0` threshold even with the
     advanced toggle off. Flag the row as live.

  Seeding follow-on: deliberately place one already-rated tutor in S6's candidate pool so the
  accuracy moment is reliably reachable rather than accidental.
- **Latency.** Server-side recompute means sliders are not frame-smooth. If ~250ms debounce
  reads as laggy on the projector, the fallback is a client-side projection clearly labelled
  as such.

## Checks to run

- `python manage.py test studybuddy` — including the new co-rated-overlap assertions.
- `python manage.py reset_demo_data && python manage.py seed_data` on a local database;
  `_assert_guarantees` must pass without a `CommandError`.
- Query the demo endpoint for S6 and confirm four contributing neighbours with similarities
  spread between 0.31 and 0.97, and CF ~4.74 for T1.
- Query for S1 and confirm `cold_start: True` on every candidate.
- `npm run lint` and `npm run build`.
- Manual: drag a rating, confirm the waterfall, hybrid score and ranking all move, and confirm
  no `Rating` row changed in the database afterwards.

## Changelog

- **2026-07-23** — Plan created from a grilling session. Recorded four settled decisions
  (two-zone waterfall, top-5 weight table, server-side what-if editing with the advanced
  co-rated toggle off by default, tiered programming reseed). Documented two defects found
  while grounding the design: every curated similarity is currently exactly 1.00 due to
  two-item co-rating overlap, and S1 — described in the seeder's comments as the CF
  protagonist — has no ratings and is cold-start on every candidate. Locked mockup promoted
  to `docs/mockups/2026-07-23-algorithm-demo-cf-waterfall.html`; tier-1 matrix validated
  against a mirror of `CF.py`. Status set to Approved, no code written.
- **2026-07-23** — Resolved the open candidate-pool question. Traced both live production
  paths (`dashboard.py:114-116`, `views.py:3735-3760`) and confirmed neither excludes tutors
  the tutee has already rated; the only code that does is `recommend_tutors_cf` (`CF.py:201`),
  which is imported nowhere and is dead. Decision: the demo keeps them, matching production.
  Added two UI consequences to Risks — badge the row and show the tutee's actual rating beside
  the prediction as an accuracy check, and flag that similarity is live for such rows — plus a
  seeding follow-on to place one already-rated tutor in S6's pool deliberately.
- **2026-07-23** — Implemented steps 1 and 2. Widened the CF breakdown payload in `CF.py` and
  `demo.py`; added `apply_rating_overrides` and the read-only `POST
  dev/algorithm-demo/recommend-whatif/` endpoint; added `getAlgorithmDemoWhatIf` to the frontend
  service layer. Added four tests to `AlgorithmDemoToolTests`.

  The first version of the what-if test failed with the override producing no change, which
  turned out to be the degenerate-overlap defect this plan exists to fix rather than a bug in
  the endpoint: the fixture had the tutee and peer sharing exactly one co-rated tutor, so
  Pearson returned 0 (`CF.py:59-61`) and the peer was filtered out before the override could
  matter. Fixture extended to two co-rated tutors, which is also a live demonstration that the
  seed work in step 7 is necessary.

  Checks run: `AlgorithmDemoToolTests` 24 passed; `RecommenderNeighborReuseTests`,
  `CfPeerNeighborTests`, `DashboardRecommendationServiceTests` 14 passed; ESLint clean on the
  changed service file. Status moved Approved -> In Progress.
- **2026-07-24** — Implemented step 4. Rebuilt `AlgorithmDemoBreakdown.vue` as the two-zone
  waterfall and wired `AlgorithmDemoRankedList.vue` to the what-if endpoint on a 250ms
  debounce with a "nothing saved" chip and Reset. The CF axis is derived from the plotted
  points rather than fixed, so small shifts stay readable. Skipped step 3 for now: the
  frontend no longer calls `updateAlgorithmDemoRating`, but the export and the backend
  endpoint remain pending the user's decision on deleting the persisting route and its six
  tests.

  Checks run: ESLint clean on `src/components/algorithm-demo/` and the service file;
  `npm run build` succeeded in 6.22s. Not yet exercised in a browser.
- **2026-07-24** — Implemented step 5. Added `AlgorithmDemoWeightTable.vue` (top 5 side by
  side, per-cell value plus weighted contribution, contribution shading, CF pool badges) and
  mounted it above the list/breakdown split, sharing `selectedTutorId` so clicking a table row
  opens that tutor's waterfall. Step 7 (reseed) deliberately not started: it requires
  `reset_demo_data`, which deletes all non-staff data, and explicit confirmation that the
  target database is safe to wipe has not been given.

  Checks run: ESLint clean on `src/components/algorithm-demo/`; `npm run build` succeeded in
  7.75s. Not yet exercised in a browser.
- **2026-07-24** — Implemented step 7 and the seeder half of step 8, then reseeded with
  explicit user authorisation. Added curated tutors T6/T7/T8 and tutees S6-S10, replaced
  `CURATED_RATINGS` with the validated tier-1 matrix, and added
  `_assert_tier1_co_rating_density` so a later edit cannot reintroduce the degenerate
  similarities this plan was written to fix.

  Database contents were reported before the wipe and confirmed to be the demo dataset
  (512 non-staff users, 747 ratings, 749 bookings on database `postgres`) rather than
  anything unexpected.

  Checks run: `reset_demo_data` cleared 10,192 cascaded rows; `seed_data` completed with both
  guarantee blocks passing, including "all 8 tier-1 tutees co-rate >= 3 tutors pairwise with
  no degenerate similarity". Post-seed verification against the real recommender reproduced
  the predicted CF of 4.742 for S6/T1 exactly, and confirmed S1 remains cold-start on all 18
  candidates.

  Two outcomes worth keeping for the defense narrative, both emergent rather than engineered:
  T6 outranks T1 (0.949 vs 0.927), so the top of the board is a real contest; and a filler
  tutor holds the highest CBF of the whole pool (0.935) yet falls to 4th for want of any CF
  signal.
- **2026-07-24** — Updated the demo guide (step 9, part) with the eight new curated personas,
  a "Who to demo with" section covering the tier-1 core and the co-rating threshold, and a
  rewritten walkthrough reflecting the top-5 table, the waterfall and what-if editing.

  Also fixed a regression introduced by step 4: `AlgorithmDemoPairPicker.vue` renders the same
  breakdown component and was still listening for the removed `rating-updated` event, so the
  Compare Pair tab's sliders did nothing. It now owns an override list and re-scores through
  the what-if endpoint exactly as the ranked list does. Worth noting the shape of the mistake —
  the component was rewritten without checking who else consumed its events.

  Checks run: ESLint clean on `src/components/algorithm-demo/`; `npm run build` succeeded in
  6.58s; guide tag balance verified (10 sections, 168 divs, all matched). Still not exercised
  in a browser.
