---
title: Demo deployment plan
date: 2026-07-05
status: In Progress
spec:
---

# Demo deployment plan

## Status/Progress Summary

In progress as of 2026-07-06: Render backend and Vercel frontend are both provisioned and live
(Render on `origin`'s `chore/deploy-debug`, Vercel on a fork — `RayDomD/studybuddy-ui` — pushed in
parallel, needed only because Vercel's GitHub import can't see a personal repo you're a
collaborator, not owner, on). Supabase is provisioned, migrated, and seeded via
`reset_demo_data`. Fixed along the way: a migration file (`0041_recommendation_filter_indexes`)
that was accidentally gitignored and never committed; a Linux case-sensitivity import bug
(`@/stores/superAdmin` vs the real `superadmin.js`) that only broke Vercel's build, never local;
Supabase's direct-connection host being IPv6-only (Render has no outbound IPv6) — switched to the
Supavisor session pooler; and a structural conflict where the demo Basic Auth gate
(`demo_basic_auth.py`) and the app's JWT both wanted the `Authorization` header — moved the demo
gate to `X-Demo-Auth`. See
[2026-07-06 handoff](../session-summaries/2026-07-06-demo-deployment-handoff-2.md) for full detail.
Also hit a CORS gap this session: Vercel's per-deployment preview URLs (a new hash on every push)
aren't covered by the fixed-list `CORS_ALLOWED_ORIGINS`, so login failed with a CORS preflight
error from those URLs. Worked around with a new `CORS_ALLOWED_ORIGIN_REGEXES` setting
(`backend/backend/settings.py:67-73`) — flagged as a critical item to narrow before production
(see Risks).
Remaining: confirm the `X-Demo-Auth` fix actually resolves login on the live deploy, confirm the
new CORS regex env var is set on Render and login works from a fresh preview URL, decide Render's
Free vs. paid tier for defense day, run the smoke-test checklist, and switch both platforms off the
throwaway fork/branch onto `develop` once stable.

A further blocker surfaced after the CORS fix: login OTP email delivery itself was failing.
Forcing IPv4-only DNS resolution (to work around Render's missing outbound IPv6 route) changed
the failure from an instant `Errno 101 Network is unreachable` to a `TimeoutError` connecting to
`smtp.gmail.com:587` — evidence that Render blocks outbound raw SMTP outright, not just IPv6
routing. Switching to an HTTPS-based email API (Resend, already supported via `django-anymail`)
was the natural fix, but StudyBuddy has no owned domain to verify, and Resend's sandbox mode
without domain verification only allows sending to the account's own signup email — unusable for
multiple seeded demo personas.

Resolved via grilling session on 2026-07-06: **disable login OTP entirely for the demo
deployment**, since the OTP/2FA mechanism isn't part of what the thesis defense needs to
demonstrate (the recommender system and core booking/wallet flows are). `LOGIN_OTP_DISABLED`
(`backend/backend/settings.py:183-188`) reuses the existing `DEMO_BASIC_AUTH_USER`/
`DEMO_BASIC_AUTH_PASSWORD` check as its signal (no new env var needed) so local dev and any future
real production keep the full OTP flow unchanged and reviewable. `login_view`
(`backend/studybuddy/views.py:1432-1433`) returns the normal token payload directly when the flag
is set, skipping OTP challenge creation — no frontend changes needed, since `Login.vue` already
falls through to a direct login when the response has no `requires_2fa` key.

Resolved via grilling session on 2026-07-05 (see [ADR-0003](../adr/0003-deploy-before-live-paymongo-keys.md),
[ADR-0004](../adr/0004-vercel-frontend-render-backend.md), [ADR-0005](../adr/0005-basic-auth-for-demo-protection.md)):
- Database: **Supabase** (not Render-managed Postgres) — one dedicated project per environment.
- Redis: **not needed for the demo** — Channels and cache both fall back to in-memory backends
  when `REDIS_URL` is unset (`backend/backend/settings.py:323`, `:350-353`), which is fine for a
  single-instance demo.
- Demo access protection: **HTTP Basic Auth** on both the Vercel frontend and Render backend (one
  shared credential, free on any plan) — not Vercel's built-in Password Protection, which needs a
  paid add-on on Hobby/Pro.
- CI: GitHub Actions runs `frontend` (lint/build/test) and `backend` (`manage.py test` against a
  throwaway Postgres) jobs as required status checks on PRs into `develop`/`main`. Deploys
  themselves stay native (Vercel/Render build off the branch directly).
- Branch guidelines (naming, protection, hotfix reconciliation) are documented below under Steps 2.

## Goal

Ship a protected demo environment on Vercel, Render, and Supabase so the team can exercise the
real cloud stack with seeded test data and sandbox PayMongo before opening a later production
release.

## Approach

Use a simple branch model: feature branches land on `develop`, `develop` auto-deploys to a
protected demo environment, and `main` stays reserved for production later. The demo environment
should look and behave like production from the outside, but it will keep sandbox PayMongo, test
data, and separate demo infrastructure so nothing in the demo can leak into the live release.

The key decisions are:

- Vercel hosts the frontend
- Render hosts the Django backend and worker process
- Supabase hosts the PostgreSQL database
- Demo access is protected
- Demo and production use separate environments and separate secrets
- Production promotion happens by moving a proven `develop` state to `main`, not by changing the
  deployment topology at the last minute

Before the first deploy, we should also close the small production-safety gaps that already exist
in the codebase, especially the PayMongo cash-out mock path.

## Steps

1. Write down the deployment matrix for demo and production.
   - Frontend URLs
   - Backend API URLs
   - Database names and owners
   - Email provider settings
   - PayMongo key sets
   - Redis / worker requirements

2. Lock the branch strategy.
   - `feature/*` branches merge into `develop`
   - `develop` auto-deploys to the protected demo environment
   - `main` is protected and only receives promotion-ready merges
   - hotfixes branch from `main` if production ever needs an urgent fix

3. Close the pre-deploy cleanup items.
   - Make `PAYMONGO_CASHOUT_MOCK` impossible to enable in real production
   - Keep the mock path available only for local development and the protected demo environment
   - Fail fast or block the cash-out path if mock mode is requested while `DEBUG=False`
   - Keep the callback secret required whenever `DEBUG=False`
   - Keep `VERIFICATION_DEV_TOOLS_ENABLED` and `ALGORITHM_DEMO_TOOLS_ENABLED` off outside demo or
     local dev
   - Keep `DEBUG=False` for the demo so it exercises production-style security
   - Verify `ALLOWED_HOSTS`, CORS, and CSRF origins are set from environment variables
   - Confirm the current `backend/.env.example` matches the intended demo variables

4. Provision the demo infrastructure.
   - Create the Vercel project for the frontend
   - Create the Render service for the backend
   - Create the Supabase database for the demo environment
   - Add any supporting Redis or worker service only if the demo needs it for real-time or queued
     behavior

5. Configure the demo environment variables.
   - Use sandbox PayMongo keys
   - Use demo-safe email settings
   - Point the backend at the demo Supabase database
   - Set the protected frontend and backend origins explicitly
   - Keep demo-only toggles off unless the demo page actually needs them

6. Seed the demo data.
   - Load test users, tutors, institutions, and sample flows that are useful for review
   - Keep the seed repeatable so the demo can be reset cleanly
   - Make sure the demo data does not share records with production

7. Wire the release checks.
   - Run lint, build, and backend tests before each deploy
   - Add a smoke-check list for login, browsing, booking, and cash-out simulation
   - Verify the protected demo URL stays inaccessible without the chosen protection layer

8. Prepare the production handoff.
   - Promote the same code from `develop` to `main`
   - Swap demo secrets for production secrets
   - Use live PayMongo keys only after the demo has been signed off
   - Run a live-transaction verification checklist before opening payments to real users

## Risks

- `PAYMONGO_CASHOUT_MOCK` leaking into production would fake payouts, so it needs a hard stop and
  not just a warning.
- The protected demo can still use the mock path, but only as a deliberate demo-only safety valve.
- Demo and production can drift if the demo seed is not refreshed regularly.
- If the demo needs websocket or cache parity, we will need a real Redis-backed worker setup on
  Render rather than relying on in-memory defaults.
- Sandbox PayMongo can hide issues that only appear with live keys, so the later production gate
  still needs manual verification.
- **CRITICAL — revisit before production promotion**: `CORS_ALLOWED_ORIGIN_REGEXES`
  (`backend/backend/settings.py:67-73`) was added to work around Vercel minting a unique
  per-deployment URL on every push. It's set on Render to a regex matching any
  `studybuddy-*-raydom-dcruz-s-projects.vercel.app` URL, which means **any deployment created
  under that Vercel project scope is automatically an allowed CORS origin** — broader than the
  demo actually needs. Fine as a deliberate demo-only shortcut to unblock testing quickly; must be
  narrowed (or removed in favor of only the stable aliased URL) before this settings file is reused
  for real production, per the "Demo and production use separate environments and separate
  secrets" principle above.
- **Login OTP is disabled on the demo deployment** (`LOGIN_OTP_DISABLED`,
  `backend/backend/settings.py:183-188`) because Render blocks outbound SMTP and StudyBuddy has no
  domain to verify with an HTTPS email API. This is a deliberate, scoped reduction — gated on the
  same flag as the demo Basic Auth gate, so it cannot accidentally apply to local dev or real
  production — but it does mean the demo does not exercise the real 2FA path end-to-end. Full OTP
  flow remains reviewable on localhost. Revisit once a domain is available (unblocks Resend) or
  Render's SMTP restriction is confirmed/worked around another way.

## Checks to run

- `npm run build`
- `npm run lint`
- `cd backend && python manage.py test`
- `cd backend && python manage.py check`
- Demo smoke test: login, browse tutors, open a booking flow, and confirm the cash-out path stays
  in sandbox/demo mode
- Access test: confirm the protected demo URL rejects anonymous access

## Changelog

- **2026-07-05** — Grilling session resolved the open infrastructure decisions this plan had left
  implicit: database host (Supabase, superseding the Render-hosted-Postgres assumption in
  ADR-0004), confirmed Redis is unnecessary for a single-instance demo, and settled on HTTP Basic
  Auth (not Vercel's paid Password Protection) for the demo access gate. Status moved
  Draft → Approved. See ADR-0003, ADR-0004, ADR-0005 for the full reasoning behind each call.
- **2026-07-06** — Status moved Approved → In Progress: actual Render/Vercel/Supabase provisioning
  happened, plus five bugs found and fixed along the way (see Status/Progress Summary above for
  detail): the gitignored migration file, the Linux-only case-sensitivity import bug, Supabase's
  IPv6-only direct connection, and the `Authorization`-header collision between the demo Basic
  Auth gate and JWT auth. Login on the live deploy not yet confirmed working after the last fix.
- **2026-07-06 (cont.)** — Found a sixth issue while retesting: Vercel's per-deployment preview
  URLs (unique hash per push) aren't in Render's fixed `CORS_ALLOWED_ORIGINS` list, so login from
  those URLs fails CORS preflight. Added `CORS_ALLOWED_ORIGIN_REGEXES`
  (`backend/backend/settings.py:67-73`) as a demo-only workaround, set on Render to a regex
  scoped to the user's Vercel project. Flagged as a **critical pre-production item** in Risks —
  it's broader than necessary (allows any deployment under that Vercel project scope) and must be
  narrowed or removed before this settings file is reused for real production.
- **2026-07-06 (cont.)** — Chased the CORS fix further and found login OTP email itself was
  failing: forcing IPv4-only DNS resolution (workaround for Render's missing outbound IPv6, same
  class of fix as the earlier Supabase one) turned an instant `Errno 101 Network is unreachable`
  into a `TimeoutError` connecting to `smtp.gmail.com:587` — confirming Render blocks outbound raw
  SMTP outright, independent of IP version. Also added an explicit Django `LOGGING` config
  (`backend/backend/settings.py`) since the default handler was swallowing tracebacks, which is
  what let this be diagnosed at all. Investigated switching to Resend (already supported via
  `django-anymail`), but StudyBuddy has no owned domain, and Resend's unverified-sandbox mode only
  sends to the account's own signup address — not viable for multiple demo personas. Grilling
  session concluded OTP/2FA isn't part of what the thesis defense needs to demonstrate, so the
  simplest fix is disabling it for the demo only: added `LOGIN_OTP_DISABLED`
  (`backend/backend/settings.py:183-188`), reusing the existing demo Basic Auth flag as its signal
  rather than introducing a new env var. `login_view` returns the normal login payload directly
  when set, skipping OTP challenge creation; no frontend changes needed since `Login.vue` already
  handles a response without `requires_2fa`. Full OTP flow is untouched and still reviewable on
  localhost.
