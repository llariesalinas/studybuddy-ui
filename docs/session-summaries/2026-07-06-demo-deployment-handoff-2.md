# Demo deployment handoff #2 — 2026-07-06

## Where this picks up from

Previous handoff: [2026-07-05-demo-deployment-handoff.md](2026-07-05-demo-deployment-handoff.md).
Plan: [docs/plans/2026-07-05-demo-deployment-plan.md](../plans/2026-07-05-demo-deployment-plan.md)
(status: **In Progress**, moved from Approved this session).

Picking up from: the 6 reviewed-but-uncommitted code changes from last session's handoff were
committed at the start of this one, then this session did the actual first deploy attempt across
Render, Vercel, and Supabase — and hit (and fixed) five real bugs along the way. **Login on the
live demo is not yet confirmed working** — that's the very next thing to check.

## Branches and remotes — IMPORTANT, this changed this session

- `origin` = `https://github.com/llariesalinas/studybuddy-ui` (unchanged — the real repo).
- **New**: `fork` = `https://github.com/RayDomD/studybuddy-ui` — added as a second git remote
  this session. `RayDomD` is the current user's own GitHub account; this is a real fork of
  `llariesalinas/studybuddy-ui` (confirmed via `gh repo view --json isFork,parent`).
- **Why the fork exists**: Vercel's "Import Git Repository" picker will not show
  `llariesalinas/studybuddy-ui` under the current user's Vercel account, even though the user has
  push/collaborator access to it. This is a real Vercel/GitHub limitation: Vercel's repo picker is
  scoped to namespaces (personal accounts or orgs) the signed-in identity actually owns/belongs to,
  not repos you merely collaborate on under someone else's *personal* account. Render did not have
  this problem (it deploys directly from `origin`, no fork needed).
- **Working pattern established this session**: every commit gets pushed to **both** remotes on
  the same branch name, e.g.:
  ```
  git push origin feat/demo-data-reset:chore/deploy-debug
  git push fork feat/demo-data-reset:chore/deploy-debug
  ```
  Render watches `chore/deploy-debug` on `origin`. Vercel watches `chore/deploy-debug` on `fork`.
  **Keep pushing to both** until the access issue is resolved properly (see "Not started yet").
- Longer-term fix (not done yet): ask `llariesalinas` to grant Vercel's GitHub App explicit
  repository access to `studybuddy-ui` (same as she already did for Render's GitHub App) via
  `github.com/settings/installations`. Once that's done, the fork can be dropped and both
  platforms can watch `origin` directly.

## Code changes committed this session (7 commits, all on `feat/demo-data-reset`, pushed to both remotes)

1. `feat: harden demo deployment settings` — the settings.py/urls.py changes reviewed-but-uncommitted
   from the previous handoff (PayMongo mock hard-block, `DB_SSLMODE`, demo Basic Auth wiring,
   `/healthz`).
2. `feat: add demo Basic Auth middleware` — `demo_basic_auth.py` + `middleware.js`.
3. `ci: add GitHub Actions workflow for frontend and backend`.
4. `chore: scope eslint for middleware.js and exclude nested worktree`.
5. `chore: remove dead BookingDetails and TuteeSessionDetails views`.
6. `docs: add demo deployment handoff summary` (the previous session's handoff doc).
7. `fix: stop ignoring and track missing migration 0041` — see Bug #1 below.
8. `fix: correct case-sensitive import path for superadmin store` — see Bug #2 below.
9. `fix: move demo Basic Auth off the Authorization header` — see Bug #5 below.

(Numbering above is cumulative across the session, not all one commit — 9 total commits landed.)

## Five real bugs found and fixed this session

### Bug #1 — migration file silently gitignored, never committed
`backend/studybuddy/migrations/0041_recommendation_filter_indexes.py` existed on the local disk
but was explicitly listed in `.gitignore` (line 63), so it was never committed. Migration
`0057_merge_recommendation_indexes_document_renewals` depends on it, so anyone cloning fresh
(including Render) got `NodeNotFoundError: ... dependencies reference nonexistent parent node
('studybuddy', '0041_recommendation_filter_indexes')` on `manage.py migrate`. Fixed by removing
the ignore rule and committing the file. Also removed an unrelated stray `tatusQ` garbage line
from the same `.gitignore` block.

### Bug #2 — Linux-only case-sensitivity import bug
`src/views/SuperAdminAlgorithmDemo.vue:7` imported `@/stores/superAdmin` (camelCase), but the
actual file is `src/stores/superadmin.js` (lowercase). Windows/macOS filesystems are
case-insensitive, so this worked locally and never surfaced in `npm run build` on the dev machine.
Vercel builds on Linux (case-sensitive), so it failed with
`[vite:load-fallback] Could not load /vercel/path0/src/stores/superAdmin ... ENOENT`. Fixed by
correcting the import to match the real filename.

### Bug #3 — Supabase direct connection is IPv6-only; Render has no outbound IPv6
First Render deploy attempt failed `manage.py migrate` with `psycopg2.OperationalError: ...
Network is unreachable` connecting to `db.<ref>.supabase.co`. That hostname resolves to IPv6 only,
and Render's network doesn't route outbound IPv6 — a known Render+Supabase combination issue, not
specific to this project. Fixed by switching `DB_HOST`/`DB_USER` to Supabase's **Supavisor session
pooler** (`aws-0-<region>.pooler.supabase.com`, user `postgres.<project-ref>` instead of bare
`postgres`) instead of the direct-connection endpoint. Session pooler (not transaction pooler) was
chosen because Render runs one persistent service, not serverless functions.

### Bug #4 — DB_PASSWORD field pasted as a full connection URI
Separately (an operator error, not a code bug): the `DB_PASSWORD` Render env var was initially
filled with the entire `postgresql://postgres:PASSWORD@host:5432/postgres` string instead of just
the password segment. `settings.py` uses `DB_PASSWORD` as a standalone field passed straight to
psycopg2, not parsed from a URI. Caught and corrected before it caused a deploy failure.

### Bug #5 — demo Basic Auth gate and JWT auth both wanted the `Authorization` header
After Bugs #1–#3 were fixed and the backend was confirmed live and reachable, login attempts
failed with the demo Basic Auth middleware logging `WARNING Unauthorized: /api/login/` for every
attempt — the request was being rejected by `demo_basic_auth.py` before Django's real login view
ever ran. Root cause: `demo_basic_auth.py` checked `HTTP_AUTHORIZATION` expecting `Basic
<base64>`, but `src/services/api/api.js` already uses the same `Authorization` header for JWT
(`Bearer <token>`) on authenticated requests. The two mechanisms can't share one header — this is
a structural gap in the original ADR-0005 design, not something fixable via env vars alone.
**Fixed by moving the demo gate to a dedicated `X-Demo-Auth` header**:
- `backend/studybuddy/demo_basic_auth.py` now reads `HTTP_X_DEMO_AUTH` instead of
  `HTTP_AUTHORIZATION`.
- `backend/backend/settings.py`'s production `CORS_ALLOW_HEADERS` (previously unset in the
  `DEBUG=False` branch, relying on django-cors-headers' library defaults) now explicitly lists the
  defaults plus `x-demo-auth`, so CORS preflight allows the custom header through.
- `src/config.js` exports new `DEMO_BASIC_AUTH_USER`/`DEMO_BASIC_AUTH_PASSWORD` read from
  `import.meta.env.VITE_DEMO_BASIC_AUTH_USER`/`VITE_DEMO_BASIC_AUTH_PASSWORD` (new, `VITE_`-prefixed
  — separate from the existing non-`VITE_` vars `middleware.js` uses server-side at the Vercel
  edge, which remain unchanged).
- `src/services/api/api.js` attaches `X-Demo-Auth: Basic <base64(user:password)>` as a default
  header on the shared axios instance whenever those two env vars are set (no-op otherwise, same
  pattern as other demo-only toggles in this codebase).

**This fix was pushed but not yet confirmed working** — see "Not started yet" below. It also
requires two new env vars added on Vercel (not yet done as of this handoff):
`VITE_DEMO_BASIC_AUTH_USER` / `VITE_DEMO_BASIC_AUTH_PASSWORD`, same values as Render's
`DEMO_BASIC_AUTH_USER`/`DEMO_BASIC_AUTH_PASSWORD`.

## Render — status

- Service `studybuddy-demo-backend` is live at `https://studybuddy-demo-backend.onrender.com`,
  Free tier, watching `chore/deploy-debug` on `origin`.
- All env vars filled in and confirmed present (screenshot-verified): `ALLOWED_HOSTS`, `DB_HOST`
  (pooler), `DB_NAME`, `DB_PASSWORD`, `DB_PORT`, `DB_SSLMODE`, `DB_USER` (pooler format), `DEBUG`,
  `DEFAULT_FROM_EMAIL`, `DEMO_BASIC_AUTH_PASSWORD`, `DEMO_BASIC_AUTH_USER`, `EMAIL_HOST`,
  `EMAIL_HOST_PASSWORD`, `EMAIL_HOST_USER`, `EMAIL_PORT`, `PAYMONGO_CASHOUT_CALLBACK_SECRET`,
  `PAYMONGO_CASHOUT_MOCK`, `PAYMONGO_SECRET_KEY`, `SECRET_KEY`.
- **Also added this session** (not in the screenshot above, added after the login investigation
  started): `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, `FRONTEND_URL` — all set to the Vercel
  URL. These were missing entirely for most of the session, which is *part* of why login failed
  before Bug #5 was even found (requests may have been CORS-blocked before reaching the backend at
  all in earlier attempts).
- Auto-Deploy is on (default) — every push to `chore/deploy-debug` on `origin` triggers an
  automatic rebuild + restart. No manual restart needed after commits.
- Render Shell (for running one-off management commands) requires a paid plan — not available on
  Free tier. Worked around by running `manage.py` commands locally against the Supabase pooler
  connection instead (see "Seeding," below).

## Vercel — status

- Project imported from **the fork** (`RayDomD/studybuddy-ui`), not `origin` — see "Branches and
  remotes" above for why.
- This Vercel project auto-detected the repo as a potential multi-service monorepo (Django backend
  + Vite frontend) and initially offered a `vercel.json`-based dual-service setup. **Deliberately
  configured as Vite-only** (Application Preset = Vite, Root Directory = `.`) — the Django backend
  stays on Render, not Vercel.
- This project has **no "Production Branch" setting** under Settings → General or Settings → Git
  (unclear why — possibly specific to how this project type/preset was created). Workaround in
  use: **Deployments → Create Deployment → paste branch name `chore/deploy-debug` → "Deploy to
  Production"**, repeated manually after each push. This needs to be done again for every future
  push until either the Production Branch setting is found/fixed, or the project is recreated.
- Env vars set: `VITE_API_BASE_URL` (→ Render backend `/api/`), `DEMO_BASIC_AUTH_USER`,
  `DEMO_BASIC_AUTH_PASSWORD`. **Still needed** (added in code this session, not yet added on
  Vercel as of this handoff): `VITE_DEMO_BASIC_AUTH_USER`, `VITE_DEMO_BASIC_AUTH_PASSWORD` (see
  Bug #5).
- Live URLs: `studybuddy-ui-omega.vercel.app` (primary), plus auto-generated
  `studybuddy-ui-git-main-raydom-dcruz-s-projects.vercel.app` and a per-deployment URL. The `main`
  branch deployment is now **Stale** (superseded), which is correct — production should be the
  `chore/deploy-debug` deployment.
- **Deployment Protection: Standard Protection** is enabled on this Vercel project (Vercel's own
  built-in auth layer, separate from the custom Basic Auth gate). Flagged but not yet investigated
  — worth checking whether it stacks awkwardly with the custom demo gate (e.g. requiring a Vercel
  login in addition to Basic Auth).

## Supabase — status

- Same project as previous handoff. Switched from direct connection to the **Supavisor session
  pooler** this session (Bug #3) — `DB_HOST` is now `aws-0-ap-northeast-1.pooler.supabase.com`,
  `DB_USER` is now `postgres.szzevdwlesfmogrxprry` (not bare `postgres`).
- Migrations ran successfully after Bug #1 and Bug #3 were both fixed.
- **Seeded** via `python manage.py reset_demo_data`, run locally (not via Render Shell — that
  needs a paid plan) with `$env:DB_*` PowerShell env vars temporarily pointed at the Supabase
  pooler for one session, then the terminal closed to avoid leaving those overrides in place for
  future local dev work. Confirmed populated by checking directly in Supabase's table view.
- Login credentials for seeded accounts, from
  [docs/artifacts/2026-07-05-demo-data-testing-guide.md](../artifacts/2026-07-05-demo-data-testing-guide.md):
  every demo account's password is `studybuddy123`; named personas exist for each of the thesis's
  5 Specific Objectives (e.g. `bea.santos@cpu.edu.ph` for cold-start recommendation, admin accounts
  `demo.admin@cpu.edu.ph` / `demo.admin@north.edu.ph` for institution scoping). Full persona list
  and what each proves is in that testing guide — read it before doing a real demo walkthrough.

## Not started yet / next immediate steps

1. **Confirm the Bug #5 fix actually works.** Add `VITE_DEMO_BASIC_AUTH_USER` /
   `VITE_DEMO_BASIC_AUTH_PASSWORD` on Vercel, trigger a fresh "Create Deployment" →
   `chore/deploy-debug` → "Deploy to Production" (per the Vercel workaround above), confirm Render
   has also redeployed the latest commit, then retry login with
   `bea.santos@cpu.edu.ph` / `studybuddy123`. This is the very next thing to check.
2. If login still fails, check both: (a) browser Network tab for the `/api/login/` request/response,
   and (b) Render's Logs tab filtered to the attempt's timestamp — don't guess, get the actual
   error.
3. Investigate whether Vercel's "Standard Protection" Deployment Protection setting interferes with
   the custom Basic Auth gate.
4. Resolve the fork situation properly: ask `llariesalinas` to grant Vercel's GitHub App access to
   `studybuddy-ui` directly (mirroring what she did for Render), so the fork and dual-push pattern
   can be retired.
5. Run the full smoke-test checklist from the plan: login, browse tutors, booking flow, cash-out
   stays sandboxed, protected URL rejects anonymous access.
6. Switch both Render and Vercel from `chore/deploy-debug` to `develop` once the pipeline is
   confirmed stable end-to-end, then delete `chore/deploy-debug` (and decide what to do about the
   fork remote at that point).
7. Set up GitHub branch protection on `develop`/`main` requiring the CI workflow's checks (workflow
   itself was added this session, protection rules were not).
8. Decide Render Free vs. paid Starter tier for the actual thesis defense — Free tier's cold-start
   delay (spins down with inactivity, "can delay requests by 50 seconds or more" per Render's own
   dashboard warning) is a real risk on defense day.
9. Rotate the Supabase database password — it appeared in plaintext in a terminal screenshot during
   this session's troubleshooting.
