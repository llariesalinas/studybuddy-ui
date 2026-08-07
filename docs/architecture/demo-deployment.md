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
| Seed/reset demo data | `cd backend && python manage.py reset_demo_data && python manage.py seed_data` | **Destructive, local/dev only** — `reset_demo_data` wipes all Tutee/Tutor users, the subject catalog, and platform activity; `seed_data` then reseeds fixed curated + filler personas. `seed_data` refuses to run if non-staff data still exists, so the two always run in that order. Never touches Admin/SuperAdmin. |
| Restore load-limit demo case | `cd backend && python manage.py seed_booking_load_limit_demo` | Additive, reversible (`--remove`). Run after `seed_data`. Creates Grace Domingo (at her Session Load Limit, hidden from search) and Paolo Ramirez (still accepting). See [demo-data-testing-accounts.html](demo-data-testing-accounts.html). |
| Restore wallet demo cases | `cd backend && python manage.py seed_wallet_cases_demo` | Additive, reversible (`--remove`). Run after `seed_data`. Creates Isabel Fernandez (full wallet-state ledger) and Miguel Torres (forced-negative wallet, debt banner). See [demo-data-testing-accounts.html](demo-data-testing-accounts.html). |
| Lint | `npm run lint` | oxlint + ESLint, both `--fix` |
| Frontend tests | `npm run test` | Vitest |
| Backend tests | `cd backend && python manage.py test` | Django test runner |
| Build check | `npm run build` | Production build to `dist/` |

Local dev's `.env` (`backend/.env`) points at a **local/dev Supabase project** — separate from the
demo deployment's database. As of the 2026-08-08 migration both happen to be in `ap-southeast-1`,
so check the project ref in `DB_USER` (`postgres.<project-ref>`), not the region, to tell them
apart. Local dev also keeps the **full OTP/2FA login flow** (see "Login OTP" below) so it's always
reviewable end-to-end.

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
python manage.py seed_tie_breaker_demo
python manage.py seed_booking_load_limit_demo
python manage.py seed_wallet_cases_demo
python manage.py make_superadmin <email> --create
```

`seed_tie_breaker_demo`'s default `--tutee` id is tuned to a specific database's row numbering and
will not resolve after a reseed onto a fresh database (a new DB renumbers every profile). If it
errors with `No Tutee with profile id <n>`, find a real tie group first:

```
python manage.py shell -c "
from studybuddy.models import UserProfile
from studybuddy.recommender.demo import build_algorithm_demo_recommendation
for tutee in UserProfile.objects.filter(role='Tutee').order_by('id')[:50]:
    result = build_algorithm_demo_recommendation(tutee)
    rows = result.get('rows') or []
    if any(r.get('tie_group_id') is not None for r in rows):
        print('Found tie group for tutee id', tutee.id, tutee.fname, tutee.lname)
        break
else:
    print('No tie group found in first 50 tutees')
"
```

then `python manage.py seed_tie_breaker_demo --tutee <id-it-printed>`.

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
- SuperAdmin — not auto-seeded; promote one with
  `python manage.py make_superadmin <email> --create` (run against the demo DB per the steps
  above; prompts for password interactively, never logged).

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

- **Rotate the Supabase DB password** used during the 2026-08-08 database migration — it was
  pasted in plaintext during that session's debugging (deliberately deferred at the time, not
  forgotten).
- **Narrow `CORS_ALLOWED_ORIGIN_REGEXES`** before any real production use — currently allows any
  deployment under llarie's personal Vercel project scope, broader than necessary.
- **Run the full smoke-test checklist** from the deployment plan against the new database/frontend:
  login, browse tutors, booking flow, cash-out stays sandboxed, protected URL rejects anonymous
  access.

Resolved as of 2026-08-08: the fork/dual-push workaround (both platforms now deploy from `origin`
directly, see "Branches and remotes" above) and the Render tier question (confirmed on a paid
instance — outbound SMTP to Gmail on 587 works, and Render's own Shell is available).
