# Demo deployment cheat sheet — 2026-07-06

Quick reference for running everything locally and understanding the current demo deployment.
For the full story of how we got here (bugs found, decisions made), see
[docs/plans/2026-07-05-demo-deployment-plan.md](../plans/2026-07-05-demo-deployment-plan.md) and
its linked session-summary handoffs.

## Running everything locally

| Component | Command | Notes |
|---|---|---|
| Frontend | `npm install` then `npm run dev` (repo root) | Vite dev server, default `http://localhost:5173` |
| Backend | `cd backend && python manage.py runserver` | Django dev server, default `http://127.0.0.1:8000` |
| Backend migrations | `cd backend && python manage.py migrate` | Run after pulling new migrations |
| Seed/reset demo data | `cd backend && python manage.py reset_demo_data && python manage.py seed_data` | **Destructive** — always double-check `DB_HOST`/`DB_USER` in `.env` before running (see below); as of 2026-08-08 this is the **same database as the live demo**, not a separate local one. `reset_demo_data` wipes all Tutee/Tutor users, the subject catalog, and platform activity, while preserving staff/SuperAdmin logins; `seed_data` then reseeds fixed curated + filler personas, 2 permanent SuperAdmin accounts, and all 3 additive demo cases in one pass (see "Consolidated demo seed" below). |
| Lint | `npm run lint` | oxlint + ESLint, both `--fix` |
| Frontend tests | `npm run test` | Vitest |
| Backend tests | `cd backend && python manage.py test` | Django test runner. Against this database, `--keepdb` avoids Postgres `CREATE DATABASE`/confirmation prompts on the pooler connection and is much faster on repeat runs. |
| Build check | `npm run build` | Production build to `dist/` |

**Local dev's `.env` (`backend/.env`) currently points at the same Supabase project as the live
demo deployment** (project ref `roptktljurzhmervwsxn` in `DB_USER`) — confirmed 2026-08-08 while
debugging a stale `DB_HOST` (see "Database migration" below). There is no separate local-only
database right now; any `reset_demo_data`/`seed_data` run from a local checkout affects the live
demo immediately, no redeploy needed. Treat every seed command in this doc as touching production
until a genuinely separate local database exists. Local dev still keeps the **full OTP/2FA login
flow** (see "Login OTP" below) so it's always reviewable end-to-end.

### Running a one-off command against the demo database

Render's instance is on a paid tier, so **Render's own Shell** (Service → Shell tab) is the
preferred way to run one-off commands (seeding, promoting a SuperAdmin) — no local machine ever
touches production credentials. Env vars are already correct there; **always verify before running
anything destructive**, since a Shell session opened before an env var edit finishes redeploying
will silently keep the old values:

```
echo $DB_HOST $DB_USER $DB_PORT $DB_SSLMODE
```

If Render's Shell isn't available, fall back to pointing local `manage.py` at the demo's Supabase
pooler via temporary env vars (get current values from Render's Environment tab, never hardcode
them here):

```powershell
$env:DB_HOST = "<current Render DB_HOST value>"
$env:DB_NAME = "postgres"
$env:DB_USER = "<current Render DB_USER value>"
$env:DB_PASSWORD = "<current Render DB_PASSWORD value>"
$env:DB_PORT = "5432"
$env:DB_SSLMODE = "require"
```

Then run whatever `manage.py` command you need from `backend/`. **Close the terminal / unset these
vars afterward** so regular local dev doesn't keep pointing at the demo database.

For a full reseed, run in this order (each step depends on the one before):

```
python manage.py migrate
python manage.py reset_demo_data
python manage.py seed_data
```

`seed_data` now seeds 2 permanent SuperAdmin accounts and orchestrates the 3 additive demo cases
(tie breaker, booking load limit, wallet cases) itself — see "Consolidated demo seed" below.

### Consolidated demo seed (2026-08-08)

`reset_demo_data && seed_data` alone is now the complete reseed recipe — no more chaining
`seed_tie_breaker_demo`/`seed_booking_load_limit_demo`/`seed_wallet_cases_demo`/`make_superadmin`
by hand. `seed_data`:

- seeds 2 permanent SuperAdmin accounts (`superadmin.demo@cpu.edu.ph`,
  `superadmin2.demo@cpu.edu.ph`, password `studybuddy123`) — both `is_staff=True`, so
  `reset_demo_data`'s existing deletion filter already protects them on every future reset;
- orchestrates the three additive demo-case commands via `call_command()`, in an order that
  matters: tie-breaker discovery runs *first* (it needs a real tie group among the curated/filler
  tutees, before the load-limit/wallet commands' brand-new tutors — which have no CF signal of
  their own — can produce an incidental unrelated tie);
- fixes `seed_tie_breaker_demo`'s old hardcoded `--tutee` default breaking on every reseed, by
  discovering a real tutee with a tie group itself and passing it explicitly.

The three demo-case commands still exist standalone (with `--remove`) for tweaking one case live
without a full reseed. See [demo-data-testing-accounts.html](demo-data-testing-accounts.html) and
[the consolidation plan](../plans/2026-08-08-consolidate-demo-seed.md) for full details.

## Branches and remotes

As of 2026-08-08, the fork workaround described in earlier revisions of this doc has been dropped.
Both Render and Vercel now deploy directly from `origin` under llarie's own accounts, since the
database and repo ownership both moved to her (see the "Database migration" note below) — no
personal fork or dual-push is needed anymore.

- `origin` = `https://github.com/llariesalinas/studybuddy-ui` — the only remote in play.
- **Render** and **Vercel** both watch `main` on `origin` and auto-deploy on every push/merge.

A personal fork (`RayDomD/studybuddy-ui`) may still exist for historical reasons but is no longer
part of the deploy pipeline — don't push to it expecting either platform to pick it up.

### Database migration (2026-08-08)

The demo's Supabase project moved from a personal project (`ap-northeast-1`) to llarie's own
(`ap-southeast-1`, project ref `roptktljurzhmervwsxn`). Render's `DB_HOST`/`DB_USER`/`DB_PASSWORD`
(and `CORS_ALLOWED_ORIGINS`/`CORS_ALLOWED_ORIGIN_REGEXES`/`CSRF_TRUSTED_ORIGINS` for the matching
Vercel frontend move) were updated accordingly. If a Render Shell session was opened before an env
var edit finished redeploying, it silently keeps the old values — always run the `echo` check above
before trusting a shell session's environment.

**Found live and fixed, same day:** Render's `DB_HOST` env var had reverted to (or never fully
moved off) the old `aws-0-ap-northeast-1.pooler.supabase.com`, while `DB_USER` already pointed at
the new project ref — a host/user mismatch that meant Postgres rejected every connection
(`tenant/user ... not found`) from both local `manage.py` and Render's own Shell, i.e. the live
demo backend could not reach its database at all. Confirmed via Supabase's own dashboard
(Project Settings → Database → Connection pooling) that the correct host is
`aws-1-ap-southeast-1.pooler.supabase.com`; corrected in Render's Environment tab and redeployed.
The DB password was also reset directly in Supabase during this same debugging session (the prior
password, itself already a placeholder from the original migration, no longer matched what
Supabase had) — **still pending a final rotation**, tracked below.

## Current deployed state

### URLs
- **Backend (Render)**: `https://studybuddy-demo-backend.onrender.com` — API under `/api/`,
  liveness check at `/healthz` (bypasses all auth gates, used by Render's health checker).
- **Frontend (Vercel), stable**: `https://studybuddy-peertutoring.vercel.app` — the one to
  test/demo from.
- **Frontend (Vercel), preview**: a fresh `studybuddy-<hash>-llariesalinas-projects.vercel.app`
  URL is generated on every push. Covered by CORS now (see below), so these work for testing too.

### Two separate auth layers — easy to confuse
1. **Vercel edge Basic Auth** (`middleware.js`) — a native browser Basic Auth popup, checked against
   the plain `authorization` header. Gates the whole frontend before any page loads.
2. **Backend demo gate** (`demo_basic_auth.py`) — checked against a custom `X-Demo-Auth` header
   (moved off `Authorization` because JWT Bearer tokens already own that header). Sent
   automatically by the frontend's axios instance once `VITE_DEMO_BASIC_AUTH_USER/PASSWORD` are set
   — you never see a prompt for this one, it's transparent.

Both currently use the same shared credential (`studybuddy` / `studybuddy123` as of this writing —
**rotate if this value has been exposed anywhere**). This shared password is **not** an app login —
it only unlocks access to the demo site at all. Real logins need a seeded persona (see below).

### Login accounts
Full list and what each proves:
[demo-data-testing-accounts.html](demo-data-testing-accounts.html). Quick picks, all with
password `studybuddy123`:
- `s1.felipe.fernandez@cpu.edu.ph` — cold-start recommendation tutee
- `t1.marisol.aquino@cpu.edu.ph` — strongest-CBF-fit tutor
- There is no institutional Admin tier anymore (role removed in migration `0072`) and no
  second institution — only CPU is seeded.
- SuperAdmin — auto-seeded by `seed_data` as of 2026-08-08: `superadmin.demo@cpu.edu.ph` and
  `superadmin2.demo@cpu.edu.ph`, same shared password. For a third/custom account, promote one
  with `python manage.py make_superadmin <email> --create` (prompts for password interactively,
  never logged).

### Login OTP is disabled on the demo only
`LOGIN_OTP_DISABLED` (`backend/backend/settings.py`) skips the OTP-email challenge and logs in
directly, **only** when `DEMO_BASIC_AUTH_USER`/`PASSWORD` are set (i.e., only on Render's demo
deployment). Reason: Render blocks outbound SMTP on all plans below paid (confirmed via Render's
own changelog), and Resend (the HTTPS alternative already wired into the code) needs a verified
domain StudyBuddy doesn't own. **Local dev and any future real production keep the full OTP flow**
— useful to show a panel/reviewer that 2FA is actually implemented, just gated off for this specific
deployment.

### Known fixes baked into `settings.py` (Render-specific)
- `CORS_ALLOWED_ORIGINS` + `CORS_ALLOWED_ORIGIN_REGEXES` — the regex covers Vercel's per-deployment
  preview URLs (`studybuddy-*-llariesalinas-projects.vercel.app`), which change hash every push.
- IPv4-only DNS resolution (`socket.getaddrinfo` patched when `DEBUG=False`) — Render has no
  outbound IPv6 route at all; this fixed the Supabase direct-connection issue (superseded by
  switching to the Supavisor pooler) and would apply to any other IPv6-resolving host too.
- Explicit `LOGGING` config — without it, Django's default handler swallows tracebacks and only
  logs a bare one-line summary, which made the SMTP-block bug hard to diagnose. Full tracebacks now
  print to Render's console.

### Frontend-specific fix
- `vercel.json` — SPA rewrite fallback (`/(.*) → /index.html`). Vue Router uses `createWebHistory`,
  which needs server-side fallback for any direct/hard navigation to an internal route. Without
  this, the idle-session logout (`window.location.replace('/login')`, fires after **10 minutes**
  of inactivity — `IDLE_LOGOUT_MS` in `src/config.js`) or a failed token refresh mid-session hits
  Vercel's static host directly and shows a bare `404: NOT_FOUND` instead of the login page.

## Known follow-ups (not yet done)

- **Rotate the Supabase DB password** — reset once already during the 2026-08-08 host-mismatch
  debugging session (see "Database migration" above), but it was pasted in plaintext again during
  that same session and the user has said they'll do a final rotation once things are settled;
  still deliberately deferred, not forgotten.
- **Narrow `CORS_ALLOWED_ORIGIN_REGEXES`** before any real production use — currently allows any
  deployment under llarie's personal Vercel project scope, broader than necessary.
- **Run the full smoke-test checklist** from the deployment plan against the new database/frontend:
  login, browse tutors, booking flow, cash-out stays sandboxed, protected URL rejects anonymous
  access.

Resolved as of 2026-08-08: the fork/dual-push workaround (both platforms now deploy from `origin`
directly, see "Branches and remotes" above) and the Render tier question (confirmed on a paid
instance — outbound SMTP to Gmail on 587 works, and Render's own Shell is available).
