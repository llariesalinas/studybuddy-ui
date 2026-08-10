---
title: Co-rated set visualization in the algorithm demo
date: 2026-08-10
status: Done
summary: Make the "N co-rated" chip in the CF waterfall openable, revealing which tutors two students both rated and what each gave them, so Pearson similarity is visibly derived rather than asserted.
spec: ../mockups/2026-08-10-corated-set-panel.html
---

# Co-rated set visualization in the algorithm demo

**Status & Progress Summary** (2026-08-10): Done, pending manual verification in the running app.
All nine steps shipped on `feat/corated-set-visualization` (commit `909f00e`): `co_rated_detail` in
`CF.py`, a top-level `co_rated` map in the demo payload, the disclosure grid in
`AlgorithmDemoBreakdown.vue` threaded through both tabs, the guide section, and the glossary entry.
5/5 new backend tests, 37/37 recommender and demo tests, 14/14 frontend algorithm-demo tests (9
new), lint and build clean; the one failure in the full frontend suite was confirmed pre-existing at
HEAD. Backend ran with `--keepdb` because `DB_HOST` is the remote Supabase instance and its stale
`test_postgres` was held open by another session.
[Summary](../session-summaries/2026-08-10-corated-set-visualization-summary.md). Scope settled
through a grilling + `ui-preview` session: the request began as "add a similarity visualization to
the demo testing guide" and resolved into a live tool change in the algorithm demo, documented
afterwards in `algorithm-demo-guide.html`. Three gaps were identified (expand the co-rated set, show
the tutor's full rater roster, show excluded neighbours); only the first is in scope. Design A of
three chosen from `../mockups/2026-08-10-corated-set-panel.html`. Seed values were verified by hand
against `CURATED_RATINGS` and reproduce the guide's existing `+0.308`, `+0.970` and `4.742` exactly.

## Goal

The CF waterfall in the SuperAdmin algorithm demo tells a panelist that a neighbour's similarity is
`+0.853` over `4 co-rated` tutors, but never shows *which* four or what either student gave them.
The number is an assertion, not a derivation. Make the co-rated set inspectable so the similarity
can be checked by hand during a defense.

## Approach

Design A of three explored in `docs/mockups/2026-08-10-corated-set-panel.html` (chosen 2026-08-10):
an inline accordion beneath the neighbour row, shared tutors as columns, the two students as rows.

Key decisions:

- **Scope is the co-rated set only.** Not the candidate tutor's full rater roster, not the dropped
  negative neighbours, not a standalone student-by-student similarity heatmap. Those were considered
  and deliberately left out.
- **Payload shape: a top-level map keyed by `neighbor_id`, not nested per tutor row.** The co-rated
  set is a property of the *(tutee, neighbour)* pair, not of the candidate tutor —
  `build_algorithm_demo_recommendation` computes `peer_neighbors` / `global_neighbors` once
  (`demo.py:131-132`) and reuses them across every candidate. Nesting the detail inside each row
  would repeat identical data across 100+ rows. Only `rating` / `deviation` / `weighted` are
  genuinely per-tutor and stay where they are.
- **Both averages are shown and labelled by what each feeds.** There are two distinct averages in
  play and the expansion makes them collide:
  - `neighbor_avg` (`CF.py:149`) — the mean over *all* that neighbour's ratings, which feeds the
    deviation term.
  - `u_avg` / `v_avg` (`CF.py:42-43`) — the mean over *only the co-rated set*, which is what Pearson
    measures deviation from.

  With the current seed data each neighbour's co-rated set happens to be their entire rating
  history, so the two coincide on the neighbour's side. The divergence is on the **tutee's** side:
  S6 Katrina Katigbak has a different average per comparison (4.25 vs S2, 3.75 vs S3, 3.50 vs S4,
  3.80 vs S10), none of which is the 3.80 baseline the prediction starts from. That is the number a
  panelist will try to reconcile, so the tutee row carries the explicit label.
- **Read-only cells.** The existing neighbour slider stays the only control, keeping one clear
  what-if story. Editable co-rated cells were considered — `apply_rating_overrides` would support
  them for free — and rejected as too many simultaneous moving parts for a live demo.
- **Surname-only column headers, full name on hover.** The curated cast has deliberately
  alphabetical surnames (Aquino to Ocampo) for exactly this kind of at-a-glance identification.
- **Panel persists across what-if refetches, changed cell flashes.** When the candidate tutor is
  itself inside the co-rated set (the S6 to T1 case), dragging the slider changes a cell in the open
  grid, which moves both averages and the similarity. That chain is the best demo moment in the
  feature and should be visible, not hidden by a collapse.
- **Compare Pair inherits the same component.** `AlgorithmDemoPairPicker.vue:238` already renders
  `AlgorithmDemoBreakdown` inside a `1fr 1fr` grid. The grid tightens responsively at half width
  rather than forking into a second layout.

## Steps

1. **Backend — return the co-rated detail.** `CF.py` computes the intersection twice (once inside
   `sim`, once for `co_rated_count`) and discards it both times. Add a function that returns the
   shared tutor ids with both students' scores and both co-rated averages, without changing `sim`'s
   signature or any scoring behaviour.
2. **Backend — expose it in the demo payload.** Add a top-level `co_rated` map keyed by
   `neighbor_id` to `build_algorithm_demo_recommendation`, resolving tutor names once via the same
   name-map pattern as `_neighbor_name_map`. Existing `cf.neighbors` entries are untouched.
3. **Django test.** Assert the new map's shape and that the shared ratings reproduce the documented
   similarity for the S6 neighbour set. Assert scoring output is unchanged.
4. **Frontend — accordion in `AlgorithmDemoBreakdown.vue`.** Make the co-rated chip a disclosure
   control; single-open; render the two-row grid with both labelled averages; surname headers with
   `title` for the full name.
5. **Frontend — persistence and flash.** Keep the open neighbour across a what-if refetch (reuse the
   existing `neighborOrder` stability pattern) and flash cells whose value changed.
6. **Frontend — responsive tightening** for the half-width Compare Pair layout.
7. **Vitest case** covering open/close, both averages rendered, and read-only cells.
8. **Document it** in `docs/architecture/algorithm-demo-guide.html` — a section under Walkthrough,
   plus a line in "Things to know" about the two averages.
9. **Glossary.** Add **Co-rated Set** to `CONTEXT.md` near Top-K Neighbor and Peer Pool, carrying the
   rule that below 3 shared tutors similarity is degenerate.

## Risks

- **Documented numbers decay on reseed.** `algorithm-demo-guide.html` already warns that its sibling
  doc has stale account IDs after the 2026-07-24 reseed. The values in the new section were verified
  by hand against `CURATED_RATINGS` and reproduce the guide's existing `+0.308`, `+0.970` and
  `4.742` exactly, but a reseed can move them. Mitigation: the section names the *pattern* (S4 is
  the low-similarity neighbour that drags CF down) with numbers as illustration.
- **Grid width with a large co-rated set.** Bounded in practice — the intersection can never exceed
  the tutee's own rating count, curated tutees rate at most 5 tutors and filler tutees 2 plus
  top-ups (`seed_data.py:647`). No scrolling machinery planned; revisit if real data grows.
- **Payload size.** Mitigated by the top-level keyed map; worth confirming the response does not
  grow materially on a tutee with a full candidate pool.
- **Two averages could still confuse rather than clarify** if the labels are weak. The labels are
  the feature, not decoration.

## Checks to run

- `python manage.py test studybuddy` — new co-rated payload test passes, existing recommender and
  demo tests unchanged.
- `npx vitest run src/components/algorithm-demo/` — new accordion test passes.
- `npm run lint` — clean.
- `npm run build` — succeeds.
- Manual: open the demo tool as SuperAdmin with S6 Katrina Katigbak selected, expand each neighbour
  on Marisol Aquino, confirm the shared ratings match the table above and that dragging a slider
  keeps the panel open and flashes the changed cell.

## Changelog

- **2026-08-10** — Plan created at status Approved. Grilling session resolved seven branches: target
  doc (algorithm demo guide, not the accounts guide); live tool change rather than a static doc
  section; scope limited to expanding the co-rated set; both averages shown and labelled; read-only
  cells; surname-only column headers with hover; panel persists across what-if drags with the
  changed cell flashed; Compare Pair inherits the component with a tightened grid. Design A chosen
  from three `ui-preview` mockups (accordion / shared-tutor matrix / paired deviation bars).
  Backend payload shape decided as a top-level map keyed by `neighbor_id` after establishing that
  the co-rated set is a property of the (tutee, neighbour) pair and constant across candidate rows.
  No ADR — reversible, unsurprising, no real trade-off. Mockup corrected after fabricated tutor
  names were caught and replaced with the real `CURATED_TUTORS` values.
- **2026-08-10** — Implemented and committed as `909f00e`; status Approved to Done. Four deviations
  recorded in the summary: `--keepdb` for the remote test database, `"co_rated": {}` added to the
  two early returns for shape consistency, the tutee row labelled "This tutee" since the component
  has no tutee name, and a container query rather than a media query for the Compare Pair
  tightening. Manual in-app verification still outstanding.
