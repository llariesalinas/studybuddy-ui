# Admin-editable algorithm weights - session summary

**Date:** 2026-08-19
**Plan:** [`docs/plans/2026-08-19-dynamic-algorithm-weights.md`](../plans/2026-08-19-dynamic-algorithm-weights.md)
**Mockup:** [`docs/mockups/2026-08-19-dynamic-algorithm-weights.html`](../mockups/2026-08-19-dynamic-algorithm-weights.html)
**Branch:** `admin-review-panel-catalog-fixes` (local only, nothing pushed)

Panel comment addressed: *the admin should be able to edit each part of the algorithm - for example
the weights.*

## What shipped

A SuperAdmin can now tune both of the recommender's weight groups from a new Algorithm Settings
screen, and the platform records who changed each weight and when.

**Backend**

- `AlgorithmWeight` model - one row per weight, keyed by `(group, key)`, with `value`, `updated_by`
  and `updated_at`. Migrations `0083` (schema) and `0084` (seeds the eight rows).
- `recommender/weights.py` - the single source of truth for defaults, normalisation, loading, and
  the display metadata the API serves. `hybrid.py`'s `CBF_WEIGHT` / `CF_WEIGHT` and `cbf.py`'s
  `W_*` names survive as aliases of it, so nothing that referenced them broke.
- Weights threaded through `compute_cbf_breakdown`, `compute_cbf_score`, `hybrid_prediction`,
  `hybrid_prediction_breakdown`, `recommend_tutors_hybrid`, `cbf.recommend_tutors` and
  `build_algorithm_demo_recommendation` - loaded once per request in every loop.
- `AdminAlgorithmWeightsView` (GET/PATCH, SuperAdmin, ungated) and
  `AdminAlgorithmWeightsPreviewView` (POST, SuperAdmin, gated on `ALGORITHM_DEMO_TOOLS_ENABLED`),
  sharing one `parse_algorithm_weight_groups` validator.

**Frontend** - `src/services/api/algorithmWeights.js`, `SuperAdminAlgorithmSettings.vue`, the
`/superadmin/algorithm-settings` route and a sidebar entry.

**Docs** - `CLAUDE.md`'s hardcoded `0.7 * cbf + 0.3 * cf` line now states the weights are defaults
rather than constants; ADR-0009 gained an addendum explaining why the tie-breaker knobs stayed in
code while the weights became editable.

## Deviations from the plan

**Scope widened mid-session, before any code.** The work started as "make the 70/30 split
adjustable" and became "make both weight groups adjustable" once the panel's ask was clarified as
*each part of the algorithm*. That invalidated two decisions already taken - storing a single number
(six CBF weights cannot derive six values from five) and the singleton model shape - and moved the
sum-to-1 constraint from "derive the last value" to "normalise at score time". The plan's Changelog
records this.

**Three additions beyond the written steps**, all defensible and all recorded:

1. The PATCH endpoint refuses an all-zero group at the edge rather than relying only on the
   score-time fallback. The fallback stays as a backstop.
2. Display labels live in `weights.py` and are served by the API, so the Vue component does not keep
   a second copy of the copy.
3. `cbf.recommend_tutors` was threaded too. It is a CBF-only path imported by `views.py` but never
   called - dead code, so not a live bug, but it would have silently ignored admin weights if
   revived. Found while reviewing the diff.

**Step 14 landed differently than written.** The plan expected edits to two tests that read the
constants directly. Because the constants survive as aliases, no code change was needed - but the
prose in both still asserted the weights as settled facts, so both comments were corrected instead.

## Review

A two-axis `/code-review` ran against the plan and found seven issues, all fixed before commit.

**Genuine defects:**

- The preview endpoint parsed weight overrides with a bare `float()` - a non-numeric value returned
  500, and negative values passed straight through. A group can sum above zero while one member
  contributes a negative share, so this defeated the normalise-don't-validate guarantee on that
  path. PATCH and preview now share one validator; five tests cover it.
- The preview's movement markers were baselined against *pending* weights, captured on the first
  preview after a tutee change. Dragging sliders before picking a tutee therefore showed no movement
  at all, and after saving the markers kept pointing at the pre-save order. The baseline now loads
  explicitly against saved weights and reloads after a save.

**Standards:** the settings screen reached for `--sb-primary-deep` and `--sb-warning`, which exist
only in the never-imported `admin.css` and resolve to `unset` - the precise failure
`src/assets/tokens.test.js` exists to catch. It took that test from 20 violations to 22 without
changing its pass/fail state, so the earlier "nothing new in vitest" reading had masked it. Also
fixed: a hardcoded six-shade colour ramp (now mixed from `--sb-primary` via `color-mix`), two magic
numbers, and `.sb-btn-pill` / `.sb-card` having been redefined with inverted semantics against
`.claude/skills/shadcn-components.md`.

**Also corrected:** the seed migration imported `DEFAULT_WEIGHTS` from live code, so a future edit to
the defaults would have retroactively changed what it seeds on a fresh database. Its literals are now
frozen with a comment saying why.

Worth knowing: `MinValueValidator(0)` on the model is inert, since Django does not validate on
`update_or_create`. The endpoint check is the only real guard.

## Checks run

| Check | Result |
| --- | --- |
| `python manage.py test` | **506 tests, OK** - 478 baseline + 28 new, 0 failures |
| `python manage.py makemigrations --check` | No changes detected |
| `npm run build` | Succeeds |
| `npm run lint` | 4 pre-existing `no-undef` errors only (`make_algo_pptx.cjs` / `.js`) |
| `npx vitest run` | 206 pass, 9 pre-existing failures only |
| `npx vitest run src/assets/tokens.test.js` | 20 violations - back to baseline |

## Not done

- **No live end-to-end run against a running server.** Covered by unit tests and the mockup, but the
  save-then-see-rankings-change flow has never been exercised in a browser. Worth doing before the
  panel demo, since the preview is gated off by default and needs
  `ALGORITHM_DEMO_TOOLS_ENABLED=true` to be visible at all.
- **The remaining panel comments.** OTP removal and the category-logic bug are still open on the
  user's side; the teammate's six are untouched by design.
