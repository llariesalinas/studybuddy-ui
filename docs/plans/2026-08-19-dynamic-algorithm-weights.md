---
title: Admin-editable algorithm weights
date: 2026-08-19
status: Done
summary: SuperAdmins tune the hybrid blend and the six CBF component weights from a settings screen, stored per-weight with actor and timestamp, normalised at score time.
spec: ../mockups/2026-08-19-dynamic-algorithm-weights.html
---

# Admin-editable algorithm weights

Panel comment being addressed: *the admin should be able to edit each part of the algorithm — for
example the weights.*

## Status & Progress Summary

**Status:** Done - all 15 steps implemented and verified.

Full backend suite: **506 tests, OK** (0 failures) - the 478 baseline plus 28 new.
`makemigrations --check` reports no changes. `npm run build` succeeds. `npm run lint` shows only
the 4 pre-existing `no-undef` errors in `make_algo_pptx.cjs` / `.js`. `npx vitest run` is back to
its 9 pre-existing failures, and `tokens.test.js` is back to its baseline 20 violations.

A two-axis `/code-review` found seven issues, all fixed before commit. The two that mattered:
the preview endpoint parsed its weight overrides without validation (a non-numeric value 500'd,
and negatives passed through, defeating the normalise-don't-validate guarantee on that path), and
the preview's movement markers were baselined against pending rather than saved weights, so
dragging before picking a tutee showed no movement at all. Both now covered by tests. The standards
axis caught that this screen reached for `--sb-primary-deep` and `--sb-warning`, which exist only
in the never-imported `admin.css` - the exact failure `tokens.test.js` was written to catch.

Outcome recorded in
[`docs/session-summaries/2026-08-19-dynamic-algorithm-weights-summary.md`](../session-summaries/2026-08-19-dynamic-algorithm-weights-summary.md).

Design decisions were taken through an interview plus two rounds of interactive mockups; the chosen
screen is saved at
[`docs/mockups/2026-08-19-dynamic-algorithm-weights.html`](../mockups/2026-08-19-dynamic-algorithm-weights.html).

Scope was widened once during design: the work began as "make the 70/30 split adjustable" and became
"make both weight groups adjustable" after the panel's ask was clarified. That widening invalidated
an earlier decision to store a single number on a singleton model; see the Changelog.

## Goal

Let a SuperAdmin change how tutor recommendations are ranked from inside the product, and be able to
say who changed a weight and when — replacing eight module-level constants that today can only be
altered by editing code and redeploying.

## Approach

**Two weight groups, one uniform concept.** Every editable value is a float weight belonging to a
group whose members are normalised together:

| Group | Members | Current values | Source |
| --- | --- | --- | --- |
| `hybrid` | `cbf`, `cf` | 0.70 / 0.30 | `recommender/hybrid.py:20-21` |
| `cbf` | `specific`, `general`, `expertise`, `course`, `year`, `level` | 0.40 / 0.20 / 0.15 / 0.10 / 0.10 / 0.05 | `recommender/cbf.py:7-12` |

Both groups already sum to exactly 1.0, and that is not cosmetic. Every CBF sub-score and the
normalised CF score lands in 0–1, so summing-to-1 is the only reason a hybrid score is itself 0–1
and therefore comparable between tutors. A design that lets an admin enter weights totalling 1.2
would silently rescale every score in the system without raising an error anywhere.

**Raw values stored, normalised at score time.** Rather than validating that weights sum to 1, the
scorer divides each weight by its group total. `40/20/15/10/10/5` and `8/4/3/2/2/1` are the same
algorithm. This makes the invalid state *non-existent* rather than merely rejected, and removes a
validation rule that would otherwise have to be remembered at every write path. The UI shows the
derived share, so the screen still reads "40%".

**One row per weight.** An `AlgorithmWeight` table keyed by `(group, key)` with `value`,
`updated_by`, `updated_at`. All values are floats, so the usual objection to key-value settings
tables — untyped values needing parsing and validation at every read — does not apply here. Audit
lands per weight rather than per screen, which is finer than the panel asked for and costs nothing
extra.

**Read once per request, never per tutor.** `recommend_tutors_hybrid` loops over every candidate.
Weights must be loaded into a plain dict once at the top of a request and threaded down through
`hybrid_prediction`, `hybrid_prediction_breakdown`, `compute_cbf_score` and
`compute_cbf_breakdown`, exactly as `target_categories` already is to avoid an N+1 query.

**A settings screen the flag does not gate.** The control lives on a new ungated
`/superadmin/algorithm-settings` route, because a page behind `ALGORITHM_DEMO_TOOLS_ENABLED` (off by
default) could not satisfy "an admin can adjust it". The *preview* is gated, though — it renders
real tutee names and session counts, which is precisely the data that flag exists to protect. With
the flag off the weight controls stay fully usable and the preview half is replaced by a short note.

**The preview is the confirmation.** Saving is a single action with no dialog: the ranked list
already shows the consequence before the admin commits, and a confirm step would duplicate that
while training people to click through it. The change is trivially reversible and fully audited.

### Deliberately left in code

- `CF_MAX_RATING = 5` — the rating scale itself. Editing it rescales every CF score with no error,
  the same trap that ruled out independent unconstrained weights.
- `HYBRID_SCORE_PRECISION = 3` and `UPCOMING_WEEK_DAYS = 7` — tie-breaker knobs justified in
  `docs/adr/0009-tie-breaker-upcoming-week-load.md`.
- `DEFAULT_NEIGHBOR_COUNT`, `POSITIVE_SIMILARITY_THRESHOLD` — CF neighbourhood tuning; a different
  kind of number with different validation, and a second UI pattern for no panel-facing gain.
- `TEACHING_LEVEL_MAX_YEAR` — a mapping, not a number.
- Dashboard cache TTL / limits, demo search limit — infrastructure, not algorithm.

## Steps

1. Add the `AlgorithmWeight` model (`group`, `key`, `value`, `updated_by`, `updated_at`), with a
   `unique_together` on `(group, key)`.
2. Data migration seeding the eight rows from the current constants, so behaviour is byte-identical
   on deploy.
3. Add a loader returning `{group: {key: value}}` with the group already normalised, falling back to
   the in-code defaults when a row is missing.
4. Thread weights through `compute_cbf_breakdown` / `compute_cbf_score` as an optional argument
   defaulting to the current constants. Single use site: `cbf.py:143-148`.
5. Thread weights through `hybrid_prediction` / `hybrid_prediction_breakdown`. Use sites:
   `hybrid.py:80` and `hybrid.py:138`.
6. Load once in `recommend_tutors_hybrid` and pass down to every candidate.
7. `GET` / `PATCH` endpoints for the weights, SuperAdmin-only, ungated. `PATCH` stamps `updated_by`
   from the request user.
8. A preview endpoint reusing `search_tutees` and `build_algorithm_demo_recommendation` from
   `recommender/demo.py`, accepting uncommitted weights and writing nothing — the read-only
   counterpart to the existing `recommend-whatif`. Gated on `ALGORITHM_DEMO_TOOLS_ENABLED`.
9. Frontend service functions in `src/services/api/`, alongside `algorithmDemo.js`.
10. `SuperAdminAlgorithmSettings.vue` — the two weight groups, split bars, 5% sliders, derived share
    readouts, audit line, single Save. Per the mockup.
11. Gated preview half: searchable tutee picker plus ranked list with movement markers; placeholder
    note when the flag is off.
12. Route `/superadmin/algorithm-settings` with `meta.role: 'SuperAdmin'`, plus a sidebar entry.
13. Backend tests: normalisation, the seeded defaults reproducing today's scores exactly, audit
    stamping, permission and gating behaviour.
14. Update the two existing tests that read the constants directly — `tests.py:10256` uses
    `hybrid.CBF_WEIGHT`, and a docstring at `tests.py:6125` names the approved values.
15. Note in `docs/adr/0009-tie-breaker-upcoming-week-load.md` why the tie-breaker knobs stayed fixed
    while the weights became editable.

## Risks

- **Silent score drift.** The seeded values must reproduce today's rankings exactly. Step 13's
  regression test is the guard; if it fails, the normalisation or the threading is wrong, not the
  test.
- **A weight set to all zeros.** Normalising a group summing to 0 must not divide by zero — fall
  back to defaults, and consider refusing to save an all-zero group.
- **The 0.7 × 0.3 documentation trail.** `CLAUDE.md`, the recommender docs and at least one test
  docstring state the weights as fixed facts. They become defaults, not constants, and the prose
  needs to say so or it will mislead the next reader.
- **Per-tutor loading.** The easy mistake in steps 4–6 is reading weights inside the candidate loop.
  It would work and be slow in exactly the way that is hard to notice in dev.
- **Cached recommendations.** `recommender/dashboard.py` caches for 600s with a version key. Saving
  new weights should bump that version, or admins will change a weight and see nothing happen for
  ten minutes and conclude it is broken.

## Checks to run

- `python manage.py test` — expect **478 tests OK** as the baseline from `f87552d`, plus the new
  cases. Takes ~20 minutes; run it in the background.
- `python manage.py makemigrations --check` — expect no unexpected changes beyond the two intended
  migrations.
- `npm run lint` — expect the **4 pre-existing `no-undef` errors** in `make_algo_pptx.cjs` / `.js`
  and nothing new.
- `npm run build` — expect success.
- `npx vitest run` — expect the **9 pre-existing failures** in `tokens.test.js` and
  `BookingTimeRangePicker.test.js` and nothing new.

## Changelog

- **2026-08-19** — Plan created and approved. Design settled across two mockup rounds.
- **2026-08-19** - Reviewed and corrected. `/code-review` surfaced seven issues, all fixed
  before commit: preview override validation (now shared with PATCH via
  `parse_algorithm_weight_groups`, closing a 500 and a negative-weight gap), the movement baseline
  now loading against saved weights, the seed migration's literals frozen rather than imported from
  live code, two undeclared CSS tokens and a hardcoded colour ramp replaced with `color-mix` over
  real tokens, two magic numbers named, `.sb-btn-pill` / `.sb-card` restored to their documented
  semantics, and step 14's stale test prose updated. Five tests added for the preview validation.
- **2026-08-19** — Implemented. Two deviations from the plan as written, both additive: the
  PATCH endpoint refuses an all-zero group at the edge rather than relying only on the score-time
  fallback (the fallback stays as a backstop), and display labels moved into `weights.py` so the
  settings screen renders backend-defined copy instead of keeping its own. `bump_dashboard_recs_cache_version()`
  already existed, so the cache risk needed no new machinery.
- **2026-08-19** — Scope widened from the hybrid blend alone to both weight groups after the panel's
  ask was clarified as "each part of the algorithm". This superseded two earlier decisions: storing a
  single number (the six-member CBF group cannot derive six values from five) and the singleton model
  shape (replaced by one row per weight). The sum-to-1 constraint moved from "derive the last value"
  to "normalise at score time" for the same reason.
