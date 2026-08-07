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
demo deployment's database. Different `DB_HOST` region (`ap-southeast-1` locally vs
`ap-northeast-1` for the demo) confirms these are different projects. Local dev also keeps the
**full OTP/2FA login flow** (see "Login OTP" below) so it's always reviewable end-to-end.

### Running a one-off command against the demo database

Render's Shell requires a paid plan, so one-off commands (seeding, promoting a SuperAdmin) are run
locally with env vars temporarily pointed at the demo's Supabase pooler:

```powershell
$env:DB_HOST = "aws-0-ap-northeast-1.pooler.supabase.com"
$env:DB_NAME = "postgres"
$env:DB_USER = "postgres.szzevdwlesfmogrxprry"
$env:DB_PASSWORD = "<current Render DB_PASSWORD value>"
$env:DB_PORT = "5432"
$env:DB_SSLMODE = "require"
```

Then run whatever `manage.py` command you need from `backend/`. **Close the terminal / unset these
vars afterward** so regular local dev doesn't keep pointing at the demo database.

For a full reseed, run in this order (each step depends on the one before):

```
python manage.py reset_demo_data
python manage.py seed_data
python manage.py seed_booking_load_limit_demo
python manage.py seed_wallet_cases_demo
```

## Branches and remotes

- `origin` = `https://github.com/llariesalinas/studybuddy-ui` — the real upstream repo.
- `fork` = `https://github.com/RayDomD/studybuddy-ui` — a personal fork, needed **only** because
  Vercel's "Import Git Repository" picker can't see `origin` under this account (collaborator
  access, not ownership, isn't enough for Vercel's picker — a real Vercel/GitHub limitation).
- **Render** watches `chore/deploy-debug` on `origin` and auto-deploys on every push.
- **Vercel** watches `chore/deploy-debug` on `fork`. Every push creates a new Preview deployment
  automatically; Production is **not** auto-updated (this Vercel project has no visible
  "Production Branch" setting) — you must manually promote via **Deployments → Create Deployment →
  paste `chore/deploy-debug` → Deploy to Production**.

### Commit workflow while on this branch

Work happens on the local branch `feat/demo-data-reset`. Every commit gets pushed to **both**
remotes under the branch name `chore/deploy-debug`:

```bash
git add <files>
git commit -m "type: message"
git push origin feat/demo-data-reset:chore/deploy-debug
git push fork feat/demo-data-reset:chore/deploy-debug
```

Keep doing both pushes until the fork situation is resolved (see "Known follow-ups" below).

## Current deployed state

### URLs
- **Backend (Render)**: `https://studybuddy-demo-backend.onrender.com` — API under `/api/`,
  liveness check at `/healthz` (bypasses all auth gates, used by Render's health checker).
- **Frontend (Vercel), stable**: `https://studybuddy-ui-omega.vercel.app` — the one to test/demo
  from once promoted to Production.
- **Frontend (Vercel), preview**: a fresh `studybuddy-<hash>-raydom-dcruz-s-projects.vercel.app`
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
  preview URLs (`studybuddy-*-raydom-dcruz-s-projects.vercel.app`), which change hash every push.
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

- **Rotate exposed credentials** — the Supabase DB password and several Render env vars were
  pasted in plaintext during this session's debugging. Rotate all of them.
- **Narrow `CORS_ALLOWED_ORIGIN_REGEXES`** before any real production use — currently allows any
  deployment under the personal Vercel project scope, broader than necessary.
- **Resolve the fork situation** — ask `llariesalinas` to grant Vercel's GitHub App direct access to
  `origin` (same as already done for Render's GitHub App), so the fork and dual-push pattern can be
  retired.
- **Decide Render Free vs. paid Starter ($7/mo) tier** for defense day — paid tier fixes both the
  free-tier cold-start delay risk and the SMTP block (confirmed via Render's changelog: "upgrade to
  any paid instance type"), which would let OTP be re-enabled on the demo too if wanted.
- **Run the full smoke-test checklist** from the deployment plan: login, browse tutors, booking
  flow, cash-out stays sandboxed, protected URL rejects anonymous access.
- **Switch both platforms from `chore/deploy-debug` to `develop`** once the pipeline is confirmed
  stable, then delete the throwaway branch.
