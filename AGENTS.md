# Repository Guidelines

## Project Structure & Module Organization

This repository contains a Vue 3/Vite frontend at the root and a Django backend in `backend/`.
Frontend source lives in `src/`: reusable UI in `src/components/`, route pages in `src/views/`,
router setup in `src/router/`, Pinia stores in `src/stores/`, API helpers in `src/services/`, and
static assets in `src/assets/`. Public files served unchanged by Vite belong in `public/`. Backend
apps and APIs live under `backend/studybuddy/`, with project settings in `backend/backend/` and
uploaded media under `backend/media/`.

## Build, Test, and Development Commands

- `npm install`: install frontend dependencies from `package-lock.json`.
- `npm run dev`: start the Vite development server.
- `npm run build`: create the production frontend build in `dist/`.
- `npm run preview`: serve the built frontend locally for verification.
- `npm run lint`: run oxlint and ESLint with auto-fixes.
- `npm run format`: run Prettier over `src/`.
- `cd backend && python manage.py runserver`: start the Django API server.
- `cd backend && python manage.py qcluster`: start the async email worker. Required alongside
  `runserver` for verification-approval/rejection, document renewal reminder/result, booking
  confirmed, and password-changed-notice emails to actually send — without it they queue
  silently in `django_q.OrmQ` and never go out, with no error anywhere. (Login OTP and password
  reset are sent synchronously and don't need this.) See
  `docs/plans/2026-08-12-async-email-worker-reliability.md`.
- `cd backend && python manage.py test`: run Django tests.

## Coding Style & Naming Conventions

Use 2-space indentation, LF endings, UTF-8, final newlines, and a 100-character line limit.
Prettier uses single quotes and no semicolons. Name Vue single-file components in PascalCase, such
as `TutorWallet.vue`; keep route-level screens in `src/views/` and reusable pieces in
`src/components/`. Prefer Pinia stores named by domain, for example `auth.js` or `wallet.js`.

## Testing Guidelines

There is no frontend test script in `package.json`; use `npm run lint` and `npm run build` as
baseline frontend checks. Backend tests use Django's test runner. Add tests in the relevant app,
such as `backend/studybuddy/tests.py`, and name methods with `test_` so Django discovers them.

## Documentation

Save each confirmed plan as its own markdown file in `docs/plans/` (`YYYY-MM-DD-<topic>.md`), based on
`docs/plans/_template.md`, with frontmatter tracking `status` (Draft → Approved → In Progress → Done).
Log every plan as a row in the `docs/plans/README.md` index, and write a completion note in
`docs/session-summaries/` when the work ships. Document the plan before writing code.
For Graphify upkeep, see `docs/learning/2026-06-09-graphify-studybuddy-workflow.md`: code changes use
`graphify update .` or the post-commit hook, while new `docs/plans/` markdown needs a full `/graphify .`
only when those docs should be semantically reflected in the graph.

## Commit & Pull Request Guidelines

Recent history mixes concise feature commits with conventional fixes, for example
`fix: use Manila timezone and improve booking time validation`. Prefer short imperative messages and
use `fix:` for bug fixes. Pull requests should include a summary, linked issue when available,
screenshots for UI changes, migration notes for schema changes, and checks run (`npm run lint`,
`npm run build`, `python manage.py test`).

## Agent skills

### Issue tracker

Issues live as GitHub Issues on `llariesalinas/studybuddy-ui` (via the `gh` CLI); external PRs are
not a triage surface. GitHub issues sit alongside the existing `docs/plans/` workflow rather than
replacing it — see `docs/agents/issue-tracker.md` for how the two stay in sync.

### Triage labels

Canonical roles map 1:1 to label names (`needs-triage`, `needs-info`, `ready-for-agent`,
`ready-for-human`, `wontfix`); only `wontfix` exists on the repo today. See
`docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## Security & Configuration Tips

Keep secrets in `.env` files and do not commit credentials. Centralize frontend API changes in
`src/services/`; keep backend settings and CORS changes in `backend/backend/settings.py`, with
environment-specific values loaded from `.env`.
