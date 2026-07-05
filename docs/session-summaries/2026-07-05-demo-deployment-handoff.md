# Demo deployment handoff — 2026-07-05

## Where this picks up from

Plan: [docs/plans/2026-07-05-demo-deployment-plan.md](../plans/2026-07-05-demo-deployment-plan.md) (status: Approved)
Decisions recorded as ADRs: [0003](../adr/0003-deploy-before-live-paymongo-keys.md),
[0004](../adr/0004-vercel-frontend-render-backend.md) (superseded re: Supabase),
[0005](../adr/0005-basic-auth-for-demo-protection.md), [0006](../adr/0006-protected-demo-on-vercel-render-supabase.md).

## Branches

- `main` — production-reserved, currently stale (does not have this session's work).
- `develop` — created off `feat/demo-data-reset` (same commit, `265b6ba`), pushed to `origin`. This is the long-term demo/staging branch.
- `chore/deploy-debug` — created off `develop`, pushed to `origin`. Throwaway branch currently used to get Render/Vercel/Supabase provisioning working before switching both services over to `develop`.
- Repo is `github.com/llariesalinas/studybuddy-ui` (owned by a teammate, not the current user) — `llariesalinas` already authorized the Render GitHub App for this repo, so no fork was needed in the end.

## Code changes made this session — NOT YET COMMITTED

Working tree currently has (per `git status --short`):
- Modified: `backend/backend/settings.py`, `backend/backend/urls.py`, `eslint.config.js`
- Deleted: `src/views/BookingDetails.vue`, `src/views/TuteeSessionDetails.vue` (confirmed dead, zero references)
- Untracked: `.github/workflows/ci.yml`, `backend/studybuddy/demo_basic_auth.py`, `middleware.js`

**Next session should commit these** (they've been individually reviewed/verified but never staged+committed):

1. **PayMongo cash-out mock hard-block** (`settings.py`) — `PAYMONGO_CASHOUT_MOCK` now raises `RuntimeError` at startup if `PAYMONGO_SECRET_KEY` starts with `sk_live_`, instead of just logging a warning when `DEBUG=False`. Gated on key mode, not `DEBUG`, since the demo runs `DEBUG=False` on a sandbox key and still needs the mock (PayMongo test mode has no payouts product).
2. **`DATABASES["default"]["OPTIONS"]["sslmode"]`** (`settings.py`) — new `DB_SSLMODE` env var, defaults to `"prefer"` (no change for local Postgres), set to `require` for Supabase.
3. **Demo Basic Auth** — `backend/studybuddy/demo_basic_auth.py` (Django middleware) + `middleware.js` (Vercel Edge Middleware), both no-ops unless `DEMO_BASIC_AUTH_USER`/`DEMO_BASIC_AUTH_PASSWORD` are set. Wired conditionally into `MIDDLEWARE` in `settings.py`. Exempts `OPTIONS` requests (CORS preflight never carries Basic Auth) and `/healthz` (Render's health checker doesn't send it either) — both were real bugs caught and fixed mid-session, not present in an earlier draft.
4. **`/healthz` endpoint** (`backend/backend/urls.py`) — lightweight liveness check (no DB query, no auth) for Render's Health Check Path.
5. **`.github/workflows/ci.yml`** — `frontend` (lint/build/test) and `backend` (`manage.py test` against a throwaway Postgres service container) jobs, intended as required status checks on `develop`/`main` branch protection (not yet configured on GitHub itself).
6. **`eslint.config.js`** — scoped `process` global for `middleware.js`, and excluded `.claude/worktrees/**` from lint scope (was accidentally linting a nested git worktree copy of the whole repo).

Verification already done this session: `npm run build` and `npm run lint` both pass clean. `python manage.py check` passes. Full backend test suite has 27 failures + 5 errors, but 3 were isolated and confirmed **pre-existing** (fail identically with this session's `settings.py` changes stashed out) — not caused by this work. Worth flagging to the test suite's owner separately.

## Render setup — in progress

Service created on `chore/deploy-debug` branch (later switch to `develop`):
- Root directory `backend`, Python 3, Free instance tier (cold-start risk noted for actual defense day — may want to upgrade before the real demo).
- Build command: `pip install -r requirements.txt`
- Start command: `python manage.py migrate && daphne backend.asgi:application --port $PORT --bind 0.0.0.0` (folded `migrate` into the start command since Pre-Deploy Command is a paid-tier-only Render feature).
- Health Check Path: `/healthz`.
- Env vars: being filled in via Render's dashboard (not committed anywhere). A local scratch reference file `backend/.env.demo` exists (confirmed gitignored via `.env.*` pattern) with most values filled in — `DEBUG`, `PAYMONGO_CASHOUT_MOCK`, `DB_PORT`, `DB_SSLMODE`, and the full Gmail SMTP email block are done. Still pending as of this handoff: `SECRET_KEY`, `PAYMONGO_SECRET_KEY` (real sandbox key — still needed for tutee checkout even though cash-out is mocked, see `views.py:4188`), `PAYMONGO_CASHOUT_CALLBACK_SECRET`, `DB_HOST`/`DB_NAME`/`DB_USER`/`DB_PASSWORD` (from Supabase), `DEMO_BASIC_AUTH_USER`/`DEMO_BASIC_AUTH_PASSWORD`.
- **Deliberately not yet set**: `ALLOWED_HOSTS` (needs Render's assigned URL, known only after first deploy), `CORS_ALLOWED_ORIGINS`/`CSRF_TRUSTED_ORIGINS`/`FRONTEND_URL` (need the Vercel URL, doesn't exist yet).

## Supabase setup — done

- New project created for the demo. Direct connection (not pooler) is the intended connection mode, since Render runs one persistent service, not serverless functions.
- RLS (Row Level Security) deliberately **left off** — this project's Postgres is only ever accessed by the trusted Django backend via direct DB credentials, never through Supabase's own client API/PostgREST layer, so RLS provides no benefit here.

## Not started yet

- Vercel project creation (frontend). Needs `VITE_API_BASE_URL` (→ Render backend URL + `/api/`) and `DEMO_BASIC_AUTH_USER`/`DEMO_BASIC_AUTH_PASSWORD` (read by `middleware.js`).
- Filling in `ALLOWED_HOSTS` on Render and `CORS_ALLOWED_ORIGINS`/`CSRF_TRUSTED_ORIGINS`/`FRONTEND_URL` on both, once both URLs exist.
- First real deploy + smoke test (per the plan's Checks to run: login, browse tutors, booking flow, cash-out stays sandboxed, protected URL rejects anonymous access).
- Switching Render + Vercel branch settings from `chore/deploy-debug` → `develop` once the pipeline works end-to-end, then deleting `chore/deploy-debug`.
- Running `python manage.py reset_demo_data` against the Supabase database once everything is stable, to get a clean demo dataset regardless of what happened during debugging.
- Committing the code changes listed above (currently uncommitted in the working tree).
- Setting up GitHub branch protection rules on `develop`/`main` requiring the new CI workflow's checks.
- A decision still open: Render Free tier vs. paid Starter tier for the actual thesis defense (cold-start delay risk on Free).
