---
title: Dashboard top 5 Redis cache
date: 2026-06-07
status: Done
spec:
---

# Dashboard top 5 Redis cache

## Goal

Backend-enforce the tutee dashboard recommendation widget as the exact top 5 tutors
selected by the existing hybrid algorithm, while using Redis-backed caching in deployed
environments to avoid repeated recommendation recomputation.

## Approach

Keep the recommender ranking path intact: collect eligible tutors, run the hybrid
algorithm, sort by score, and serialize only the top 5. Make the cache key limit- and
version-aware so stale top-10 payloads cannot leak into the dashboard API, and invalidate
or version-bump cached results when recommendation inputs change.

## Steps

1. Change the dashboard recommender default limit from 10 to 5.
2. Add limit/version-aware dashboard recommendation cache keys and defensive slicing on
   cache reads.
3. Keep Redis through `REDIS_URL` with local `LocMemCache` fallback, and add an explicit
   Redis client dependency if it is not already direct.
4. Invalidate tutee-specific cache on preference/profile subject changes.
5. Bump the dashboard recommendation cache version when ratings or tutor ranking inputs
   change.
6. Update the dashboard UI skeleton and page size to five rows.
7. Add tests for limit behavior, cache hits, fallback, ranking order, and invalidation.

## Risks

- Exact top 5 still scores all eligible tutors on cold cache misses, so cold-start CPU
  cost is mostly unchanged.
- Version bump invalidation leaves old Redis keys to expire by TTL rather than deleting
  them immediately.
- Redis is required for shared production caching; local development can still use the
  degraded in-memory fallback.

## Checks to run

- `cd backend && python manage.py test studybuddy`
- `npm run build`
