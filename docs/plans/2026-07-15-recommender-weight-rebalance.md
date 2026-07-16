---
title: Recommender weight rebalance (CBF split + CF peer ratings)
date: 2026-07-15
status: Done
summary: Split CBF subject match into Specific/General with rebalanced weights, and filter CF neighbors to same-course peers with per-tutor global fallback.
spec: ../mockups/2026-07-15-recommender-weights-handoff.html
---

# Recommender weight rebalance (CBF split + CF peer ratings)

**Status & Progress Summary** (2026-07-15): **Done.** Implemented on branch
`feat/recommender-weight-rebalance` across three tickets: CBF graduated subject matching
(`/orchestrate`, commit `5ef4372`), CF same-course peer neighbors with per-tutor global
fallback (Codex loop via `docs/briefs/2026-07-15-recommender-cf-peer-neighbors.md`), and the
CONTEXT.md/docs glossary sync — both independently verified (tests rerun, baseline-compared for
pre-existing failures, lint/build green) and committed. All weight and mechanism decisions from
the 2026-07-14 grill shipped as designed, including the empty-`requested_subject` fallback
resolved 2026-07-15. The visual handoff document is saved at
`docs/mockups/2026-07-15-recommender-weights-handoff.html` (linked as this plan's spec).

Grilled end-to-end via `/grill-with-docs` on 2026-07-14. The hybrid split (`0.7 * CBF + 0.3 * (CF / 5)`)
is deliberately untouched. All decisions below are final; a visual handoff document explaining the
reasoning lives alongside this plan (see the session summary once implemented).

## Goal

Make CBF subject matching graduated instead of all-or-nothing (exact subject vs. same-field vs.
unrelated), and make CF predictions feel like "peer ratings" by preferring same-course students as
neighbors — without making either half more fragile at current data sparsity.

## Approach

### CBF — final weights (sum 1.0)

| Sub-score | Weight | Rule |
| --- | --- | --- |
| Specific Subject | 0.40 | 1 if the tutor teaches the exact requested subject code, else 0 |
| General Subject | 0.20 | `max(Specific, same-field match)`: 1 if the tutor teaches the requested subject itself, or at least one subject whose `category` equals the requested subject's `category`; a null category earns nothing |
| Expertise | 0.15 | Cascade: requested subject's `expertise_level / 5` if the tutor teaches it; else mean over the tutor's same-field subjects `/ 5`; else 0 |
| Course | 0.10 | Unchanged: same course 1, same strand 0.5, else 0 |
| Year | 0.10 | Unchanged: `1 / (1 + year gap)` |
| Teaching Level | 0.05 | Unchanged penalty flag: 0 only for SHS tutor x college student |

Key CBF decisions and why:

- **Subject block grows 0.35 -> 0.60 of CBF.** Deliberate philosophy shift: rank primarily on
  subject relevance to the booking being made; demographics (course/year/level) become
  tie-breakers.
- **General Subject = the `Subjects.category` field** (e.g. Science groups Biology, Physics).
  Binary, superset of Specific (an exact-match tutor scores 1 on both). Superset preserves the
  dominance property below; a mutually-exclusive design would shrink the exact-vs-field gap.
- **Exact-match dominance:** an exact-match tutor banks >= 0.63 (0.40 + 0.20 + minimum expertise)
  while a field-only tutor's theoretical max is 0.60. No field-only tutor can ever outrank an
  exact-match tutor.
- **Null category -> General contributes 0** (never errors, never free credit). Because General is
  `max(Specific, ...)`, a data hole can only ever cost *fallback* credit (<= 0.20 + 0.15), never
  harm an exact match. The weight is the insurance policy against missing/misspelled categories.
- **Match against the requested subject only** — the tutee's preference list no longer feeds
  subject/expertise matching (it previously made the signal mushy: a tutor matching any listed
  subject scored the same as one teaching the requested subject).
- **Expertise cascade (option c)** mirrors the Specific/General ladder: sharpest evidence when
  available (requested subject's level), field average as fallback, else 0. Option (a)
  (requested-only) would make Expertise a redundant shadow of Specific and leave field-match
  tutors undifferentiated; option (b) (field average for all) would dilute an exact-match tutor's
  known level with unrelated subjects.

### CF — same-course peer neighbors (weights unchanged)

- **Peer pool:** Top-K neighbors are drawn from students with **exact course equality**
  (`profile.course`), no strand tier. A tutee with a null course simply has an empty peer pool.
- **Per-tutor fallback (starting posture):** compute two top-5 neighbor lists once per request —
  peer pool and global pool. For each candidate tutor, use the peer prediction when its
  denominator is nonzero; otherwise fall back to the global prediction. Chosen over per-request
  fallback because at current data sparsity, per-request silently zeroes tutors the tutee's
  coursemates haven't rated (systematically burying new tutors and creating a
  never-rated-by-peers feedback loop).
- **Scalability note — revisit trigger:** when rating density is high enough that same-course
  pools reliably cover most candidate tutors, reconsider moving to **per-request fallback** for
  population purity (all CF scores in one ranking drawn from one population). This is a recorded
  intent, not a TODO.
- **Positive similarity only:** a student qualifies as a neighbor only when Pearson
  `similarity > 0`, in both pools. Small peer pools would otherwise let negative-similarity
  "anti-peers" dominate (inverting their contributions) and, worse, count as "usable peer signal"
  that blocks the global fallback. This resolves the commented-out `if similarity >= 0` in
  `CF.py:top_k` — with `> 0`, since zero similarity carries no information.
- Cold-Start behavior unchanged: CF `None` is still coerced to 0 in the hybrid; the CF weight is
  never reallocated to CBF.

### Loose end — RESOLVED 2026-07-15

- **Empty `requested_subject`:** under the new rules an empty request would zero the whole 0.60
  subject block for every tutor. **Decision: fall back to preference-list matching** — when no
  subject is requested, the tutee's preference list acts as the requested set: Specific = 1 if
  the tutor teaches any listed subject; General = `max(Specific, category match against any
  listed subject's category)`; Expertise cascade runs over the listed subjects (mean expertise
  on taught listed subjects, else same-field mean, else 0). This degrades gracefully to roughly
  today's behavior exactly when the new signal is absent, and keeps the algorithm demo tool
  (which passes `requested_subject=None`) meaningful.

### Follow-up tickets (explicitly out of scope here)

1. **Admin edit of tutor-proposed subjects** (name, code, category) during review or after
   approval — motivated by typos ("pYTHones") and missing categories.
2. **Category data hygiene** — audit `Subjects.category IS NULL`, consider a controlled
   vocabulary / case-insensitive comparison instead of free text.

## Steps

1. `cbf.py`: replace `W_SUBJECT` with `W_SPECIFIC` / `W_GENERAL`; add the new constants
   (0.40 / 0.20 / 0.15 / 0.10 / 0.10 / 0.05).
2. `cbf.py`: implement Specific (exact requested-subject match), General
   (`max(Specific, category match)`, null-safe), and the Expertise cascade; drop the
   preference-list merge (`requested_subject` append) from subject/expertise matching when a
   subject is requested; when the request is empty, apply the preference-list fallback decided
   above.
3. Update `compute_cbf_breakdown` so the demo tool (`recommender/demo.py`) shows the new
   sub-scores.
4. `CF.py`: filter `top_k` candidates to `similarity > 0`; add a course-filtered peer variant;
   compute both neighbor lists once per request in `hybrid.py` and apply the per-tutor fallback in
   `compute_cf_breakdown` / `compute_cf_score`.
5. Update the algorithm demo tool and any serializer surfaces that expose the breakdown.
6. Backend tests: dominance property (exact >= 0.63 vs field-only max 0.60), null-category
   handling, expertise cascade tiers, peer-pool fallback (pool-level and tutor-level), positive
   similarity filter, null-course tutee.
7. Update `CONTEXT.md` (CBF Score weights, CF Score / Top-K Neighbor peer-pool semantics) — the
   General/Specific Subject entries were already added during the grill.

## Risks

- Ranking shifts are guaranteed (subject block 0.35 -> 0.60) — demo/seed data expectations and any
  snapshot tests over recommendation order will need updating.
- `Subjects.category` is nullable free text; until the hygiene ticket lands, General/Expertise
  fallback credit silently under-scores miscategorized tutors (bounded at 0.35 of CBF by design).
- Two `top_k` calls per request instead of one — negligible at current scale, but worth a glance
  at the demo tool's timing display if it has one.
- Per-tutor fallback mixes populations across one ranking (peers for some tutors, global for
  others) — accepted trade-off, documented revisit trigger above.

## Checks to run

- `python manage.py test` (backend suite; new recommender tests pass, no regressions beyond
  known pre-existing failures).
- Manual: run the superadmin algorithm demo tool and confirm the breakdown shows the six CBF
  sub-scores and which CF pool (peer/global) each prediction used, for a cold-start tutee, a
  quiet-program tutee, and a dense-history tutee.
- `npm run lint` / `npm run build` only if frontend surfaces (demo tool UI) change.

## Changelog

- **2026-07-15** — Plan created from the 2026-07-14 grilling session and marked Approved. Captured
  final CBF weights (0.40/0.20/0.15/0.10/0.10/0.05), the Specific/General split with superset +
  null-category rules, the Expertise cascade, CF same-course peer pool with per-tutor global
  fallback, the positive-similarity filter, the per-request scalability revisit trigger, one open
  loose end (empty `requested_subject`), and two follow-up tickets.
- **2026-07-15** — Handoff/explainer document generated via ui-preview and promoted to
  `docs/mockups/2026-07-15-recommender-weights-handoff.html`; linked as this plan's `spec:`.
- **2026-07-15** — Handoff restyled to Studybuddy design tokens (from `src/assets/main.css`) and
  extended with a Defense Q&A section (13 anticipated panel questions with answers).
- **2026-07-15** — Loose end resolved: empty `requested_subject` falls back to preference-list
  matching (preference list acts as the requested set for Specific/General/Expertise). Status
  moved to In Progress; work started via `/orchestrate` on branch
  `feat/recommender-weight-rebalance` with tickets in `docs/tickets.md` (previous admin-
  consolidation tickets archived to `docs/tickets-2026-07-12-admin-consolidation.md`).
- **2026-07-15** — Ticket 1 (CBF graduated subject matching) shipped via `/orchestrate`
  (commit `5ef4372`): dominance property, null-category safety, expertise cascade, and the
  preference-list fallback all covered by new tests; independently reviewed and verified
  (baseline-compared full-suite run showed zero new failures).
- **2026-07-15** — Tickets 2 and 3 (CF same-course peer neighbors + per-tutor global fallback;
  CONTEXT.md/docs glossary sync) handed off to the Codex loop via
  `docs/briefs/2026-07-15-recommender-cf-peer-neighbors.md`, executed by Codex, and
  independently re-verified end to end: `CfPeerNeighborTests` +
  `RecommenderNeighborReuseTests` + `CbfGraduatedSubjectMatchTests` 14/14 pass; the 11
  `AlgorithmDemoToolTests`/`DashboardRecommendationServiceTests` failures were confirmed
  pre-existing by stashing the diff and rerunning against the unmodified baseline (identical
  names, identical counts); `npm run lint` / `npm run build` clean. Committed as two commits;
  all three tickets' acceptance boxes ticked in `docs/tickets.md`. Plan status set to Done.
