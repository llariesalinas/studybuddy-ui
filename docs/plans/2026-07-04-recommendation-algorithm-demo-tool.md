---
title: Recommendation algorithm live demo tool
date: 2026-07-04
status: Done
spec:
---

# Recommendation algorithm live demo tool

## Goal

Give the thesis/capstone panel a way to see the real hybrid recommendation algorithm run
live against real seeded data — not just a static explainer — so they can watch the Hybrid
Score (CBF + CF) get computed for real tutees/tutors in real time.

## Approach

Grilled end-to-end (10+ decisions resolved) plus a visual mockup pass (Visual Companion) for
the tool's layout and calculation animation. Key decisions:

- **Demo type**: an interactive score-breakdown tool, not a narrated code walkthrough or a
  wired-up version of the existing static explainer (`docs/artifacts/2026-07-04-recommendation-algorithm-explainer.html`).
- **Hosting**: a standalone HTML/JS page in `docs/artifacts/` (same pattern as the existing
  explainer) backed by a new debug API endpoint — avoids needing to log into the real app's
  Vue/superadmin routes live in front of the panel.
- **Auth**: new endpoint(s) gated by `IsAuthenticated` + staff/superadmin role check + a new
  `settings.ALGORITHM_DEMO_TOOLS_ENABLED` flag, mirroring the existing
  `VERIFICATION_DEV_TOOLS_ENABLED` pattern (`backend/studybuddy/views.py:299-323`) so the
  endpoints are inert unless explicitly enabled. The standalone tool has its own login form
  that calls the real login endpoint for a JWT.
- **Output**: a ranked tutor list per tutee (mirrors `get_dashboard_recommendations`), using the
  same institution/availability candidate filtering as production, with the full CBF sub-score
  breakdown (subject/expertise/course/year/level, with weights) and the CF score plus
  contributing Top-K Neighbors (see `CONTEXT.md` — Hybrid Score, CBF Score, CF Score, Top-K
  Neighbor, Cold-Start Tutee) for every candidate tutor.
- **Layout** (visual mockup, option B): split view — ranked list stays visible on the left,
  clicking a tutor updates a detail panel on the right. Chosen over an expandable accordion
  list and a "hero + carousel" single-tutor view because it lets the presenter compare tutors
  without losing the ranking context on screen.
- **Calculation animation** (visual mockup, option A): the detail panel doesn't render the
  final numbers instantly — it replays the calculation as a staged sequence: the five CBF
  sub-score bars fill one at a time (~250-300ms stagger) labeled with weight and value, then
  the CF bar fills with the Top-K Neighbor list appearing below it (or a "Cold Start" badge if
  the tutee has no rating history), then the bars visually merge into one stacked Hybrid Score
  bar. All values come from the already-computed API response — the animation only stages the
  reveal, it does not recompute anything client-side, so timing is predictable for a live demo.
- **Cold-Start Tutee handling**: labeled explicitly in the UI ("Cold Start" badge + "CF
  unavailable — no rating history" subtext) rather than left silent, since a cold-start tutee's
  Hybrid Score is structurally capped at `0.7 * CBF Score` (CF weight is coerced to 0, not
  reallocated to CBF) and an unexplained score gap would raise unplanned questions live.
- **Branch**: continues on `feat/verification-phase4-session-redesign` (per explicit user
  choice, despite being unrelated in scope).

## Steps

1. Backend: add `ALGORITHM_DEMO_TOOLS_ENABLED` setting (default off; env-driven), following the
   `VERIFICATION_DEV_TOOLS_ENABLED` pattern.
2. Backend: add `backend/studybuddy/recommender/demo.py` with functions to (a) list/search real
   tutee profiles and (b) run `recommend_tutors_hybrid` for a tutee and shape the response with
   full CBF sub-scores, CF score, Top-K Neighbor detail, and a `cold_start` flag per tutor.
3. Backend: wire two `@api_view` endpoints in `views.py` (list tutees, get ranked breakdown),
   gated by `IsAuthenticated` + staff/superadmin check + the settings flag (403 when disabled).
4. Backend: Django tests covering the disabled-flag 403, the non-staff 403, and that returned
   scores match direct calls to `compute_cbf_score`/`compute_cf_score`.
5. Frontend: build the standalone HTML/JS tool in `docs/artifacts/2026-07-04-recommendation-algorithm-live-demo.html`
   — login form, searchable tutee dropdown, split-view ranked list + detail panel, and the
   staged bar-cascade calculation animation.
6. Manually verify against the local dev server (real seeded data) before treating this as done.
7. Write the session summary once shipped; update `docs/plans/README.md` and regenerate
   `docs/plans/index.html`.

## Risks

- Seeded `Rating` data may be sparse for some tutees, making CF/neighbor detail look thin for
  those specific tutees during the live demo — worth a quick pre-demo check of which seeded
  tutees have the richest rating history and rehearsing with those.
- The CORS setup relies on `DEBUG=True` (`CORS_ALLOW_ALL_ORIGINS`) — this tool must only be run
  against a local/dev backend, never production.
- If the panel asks to see a tutee with zero candidate tutors (e.g. no institution match), the
  UI must show a clear empty state rather than an error or blank screen.

## Checks to run

- `python manage.py test studybuddy.tests.<NewDemoEndpointTestClass>` — new endpoint tests pass
- `npm run lint` / `python manage.py test` (full suite) — no regressions
- Manual run-through against local dev server: log in via the tool, pick a tutee with rating
  history and one without, confirm the Cold Start badge and bar animation both behave correctly
