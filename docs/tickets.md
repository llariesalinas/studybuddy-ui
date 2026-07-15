# Tickets: Recommender weight rebalance (CBF split + CF peer ratings)

Split the CBF subject match into Specific/General with rebalanced weights, and filter CF
neighbors to same-course peers with a per-tutor global fallback. Source plan:
[`docs/plans/2026-07-15-recommender-weight-rebalance.md`](plans/2026-07-15-recommender-weight-rebalance.md)
(all decisions final; the empty-`requested_subject` fallback is resolved in the plan).

Work the **frontier**: any ticket whose blockers are all done.

## CBF graduated subject matching

**What to build:** A tutee requesting a specific subject sees exact-match tutors ranked above
same-field tutors, who rank above unrelated tutors — instead of today's all-or-nothing subject
match. CBF weights become Specific Subject 0.40 / General Subject 0.20 / Expertise 0.15 /
Course 0.10 / Year 0.10 / Teaching Level 0.05. General Subject is a superset match via
`Subjects.category` (null category earns nothing, never errors). Expertise cascades: requested
subject's level, else same-field mean, else 0. The tutee preference list no longer feeds
subject/expertise matching when a subject is requested; when the request is empty, the
preference list acts as the requested set (fallback decided in the plan). The superadmin
algorithm demo shows the new sub-scores end to end (backend breakdown + frontend bars).

**Blocked by:** None — can start immediately.

**Model:** mid

- [ ] Dominance property holds: an exact-match tutor scores >= 0.63 on the subject+expertise
      block while a field-only tutor's theoretical max is 0.60 — covered by a test.
- [ ] Null `Subjects.category` contributes 0 to General/Expertise fallback without erroring,
      and never harms an exact match — covered by a test.
- [ ] Expertise cascade tiers (exact level / same-field mean / 0) each covered by a test.
- [ ] Empty `requested_subject` falls back to preference-list matching — covered by a test.
- [ ] CBF breakdown and the algorithm demo UI show the six new sub-scores with their weights.
- [ ] Backend suite green (no new failures); `npm run lint` and `npm run build` pass if
      frontend touched.

## CF same-course peer neighbors with per-tutor global fallback

**What to build:** CF predictions come from "peers" — Top-K neighbors drawn from students in
the same course (exact `course` equality) — so a tutee's score feels like "students in your
program rated this tutor". Two top-5 neighbor lists are computed once per request (peer pool
and global pool); per candidate tutor, the peer prediction is used when its denominator is
nonzero, otherwise the global prediction. Only positive Pearson similarity (`> 0`) qualifies a
neighbor, in both pools. A null-course tutee has an empty peer pool (global-only). Cold-Start
behavior is unchanged. The algorithm demo shows which pool (peer/global) each tutor's CF
prediction used.

**Blocked by:** None — can start immediately.

**Model:** top

- [ ] `top_k` excludes non-positive similarity neighbors in both pools — covered by a test.
- [ ] Peer pool contains only same-course students; null-course tutee gets an empty peer pool —
      covered by tests.
- [ ] Per-tutor fallback: peer prediction used when peer denominator is nonzero, global
      otherwise — covered by a test at the tutor level and the pool level.
- [ ] Neighbor lists computed once per request (existing neighbor-reuse tests still pass or are
      updated to the two-list shape).
- [ ] CF breakdown exposes which pool each prediction used; demo tool and its UI surface it.
- [ ] Backend suite green (no new failures); `npm run lint` and `npm run build` pass if
      frontend touched.

## Glossary and docs sync

**What to build:** `CONTEXT.md` reflects the shipped algorithm: CBF Score weights
(0.40/0.20/0.15/0.10/0.10/0.05 with the Specific/General/Expertise-cascade rules and the
empty-request fallback), and CF Score / Top-K Neighbor peer-pool semantics (same-course pool,
per-tutor global fallback, positive-similarity filter, recorded per-request revisit trigger).
The General/Specific Subject entries added during the grill are checked for accuracy against
the implementation.

**Blocked by:** CBF graduated subject matching, CF same-course peer neighbors with per-tutor
global fallback

**Model:** small

- [ ] CONTEXT.md CBF Score entry matches the implemented weights and rules.
- [ ] CONTEXT.md CF Score / Top-K Neighbor entries describe the peer pool, fallback, and
      positive-similarity filter, including the per-request revisit trigger.
- [ ] No stale references to the old 0.35/0.20/0.20/0.15/0.10 weights anywhere in docs.
