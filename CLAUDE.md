# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Structure

Vue 3/Vite frontend at the repo root, Django backend in `backend/`. StudyBuddy is a peer-to-peer
tutoring platform for Central Philippine University students (Tutees book Tutors; Admin and
SuperAdmin roles moderate institutions, support tickets, and withdrawals).

- `src/components/` — reusable UI components (PascalCase filenames, e.g. `TutorWallet.vue`)
- `src/views/` — route-level screens, wired up in `src/router/index.js`
- `src/stores/` — Pinia stores, named by domain (`auth.js`, `wallet.js`, `chat.js`, ...)
- `src/services/` — API/service layer; `src/services/api/api.js` is the shared axios instance
- `src/router/index.js` — routes plus a single global `beforeEach` guard (auth, profile
  completion/onboarding, and role-based redirects — read this before adding a route)
- `src/config.js` — all env-derived constants and magic numbers (timeouts, poll intervals, cache
  TTLs); add new tunables here rather than inlining them
- `backend/studybuddy/` — the Django app: `models.py`, `views.py`, `serializers.py`, `urls.py`,
  `admin_views.py` (admin/superadmin endpoints), `chat/` (Django Channels websocket app),
  `recommender/` (tutor recommendation algorithm)
- `backend/backend/` — Django project settings (`settings.py`, `urls.py`, `asgi.py`)
- `backend/media/` — uploaded media

## Commands

Frontend (run from repo root):
- `npm install` — install dependencies
- `npm run dev` — start the Vite dev server
- `npm run build` — production build to `dist/`
- `npm run preview` — serve the production build locally
- `npm run lint` — oxlint + ESLint with auto-fix (`npm run lint:oxlint`, `npm run lint:eslint` individually)
- `npm run format` — Prettier over `src/`
- `npm run test` — run all Vitest tests (jsdom environment)
- `npx vitest run <path>` — run a single test file, e.g. `npx vitest run src/stores/chat.test.js`
- `npx vitest` — watch mode

Backend (run from `backend/`):
- `python manage.py runserver` — start the Django API server
- `python manage.py test` — run all Django tests
- `python manage.py test studybuddy.tests.<TestClass>.<test_method>` — run a single test

## Coding Style

- 2-space indent, LF endings, UTF-8, final newline, 100-char line limit (`.editorconfig`)
- Prettier: single quotes, no semicolons (`.prettierrc.json`)
- Vue SFCs in PascalCase; route screens live in `src/views/`, reusable pieces in `src/components/`
- Pinia stores named by domain, matching the module they own

## Architecture Notes

### Auth & routing
`src/services/api/api.js` attaches the JWT bearer token to every non-public request and handles
401s by transparently refreshing via `authStore.refreshAccessToken()` (deduped through a single
in-flight `refreshPromise`), then logs out and redirects to `/login` if refresh fails.
`PUBLIC_ENDPOINTS` in that file must stay in sync with any new unauthenticated backend endpoint.

The router guard (`src/router/index.js`) is the single source of truth for navigation rules:
auth requirement → guest-only redirect → tutor onboarding step redirect → profile-completion
gate → role-based access. New routes need a `meta: { requiresAuth, role }` entry, not ad-hoc
checks inside views.

### Booking model: Instant Booking (ADR-0008)
Booking is **not** a request/approval flow. A Tutee booking a slot inside a Tutor's published
availability is confirmed immediately (`POST bookings/confirm/`) — there is no tutor accept/reject
step. A Tutor's protection is post-hoc: penalty-free cancellation before the 12-hour **Grace
Cutoff**, and a self-serve **Late Cancellation** after it that auto-opens a Support Ticket
(excused, or a **Counted Strike** — flat ₱50 wallet deduction for tutors, none for tutees — capped
at 3/month before booking/search-visibility suspension). `Pending` survives only as a historical
status value on old rows; do not build new flows around a tutor-approval step.

Double-booking is prevented backend-side by `select_for_update()` row locking inside
`transaction.atomic()` in `confirm_payment_and_book` (`backend/studybuddy/views.py`), backstopped
by a DB `UniqueConstraint` on `(availability, session_date)` for active statuses
(`backend/studybuddy/models.py`, `Booking.Meta`). The frontend is pull-only for availability —
nothing pushes slot changes to open tabs.

### Real-time: chat only
The only WebSocket/push channel in the app is chat (`backend/studybuddy/chat/consumers.py` +
`routing.py`, wired up in `src/stores/chat.js`). Everything else (availability, booking state,
notifications) is polled or fetched on mount/user action — see `SESSION_POLL_INTERVAL_MS` /
`NOTIFICATION_POLL_INTERVAL_MS` in `src/config.js`.

### Display Status vs. raw status
Sessions have two distinct status concepts: the raw `Booking.status` field (changes only on
explicit action) and the time-aware **Display Status** (`Upcoming`/`Ongoing`/`Payment
Required`/`Awaiting Verification`/`Completed`/passthrough), computed per-request server-side by
`get_display_status` (`backend/studybuddy/views.py`) and never stored. Don't conflate the two in
new code — see `CONTEXT.md` for the full distinction, including the "Handoff" and "Queue Item" UI
concepts built on top of Display Status.

### Recommender (tutor matching)
`backend/studybuddy/recommender/` implements a hybrid recommender:
`Hybrid Score = 0.7 * CBF Score + 0.3 * (CF Score / 5)` (`hybrid.py`). CBF (`cbf.py`) is a weighted
content match on subject/expertise/course/year-level/teaching-level. CF (`CF.py`) is
Pearson-similarity collaborative filtering over up to 5 nearest neighbor Tutees (preferring
same-course "Peer Pool" neighbors, falling back to a global pool per-tutor). A Tutee with no
rating history is "Cold-Start" — CF is coerced to 0, not excluded from the weighted formula.

### Verification & booking gates
Enrollment verification is enforced only at two "Booking Gates": creating a booking
(`POST bookings/confirm/`) and (legacy) accepting one. Enforcement never retroactively touches
existing bookings/wallet/dashboard access. There's a client-side "Proactive UI Gate" (disables the
button) that must mirror the server's "Reactive Gate" condition exactly — the server check is
always the actual source of truth. See `CONTEXT.md` for the full Verification Enforcement /
Renewal Required state machine.

### Multi-institution model
Each Partner Institution curates its own **Institution Course Catalog** (Course↔Subject pairings)
and may define **Custom Subjects** visible only within that institution. Admin-authored data
changes must stay scoped to the acting admin's own institution.

## Domain glossary

`CONTEXT.md` at the repo root is the canonical glossary for domain terms (Booking Gate, Hybrid
Score, Payout Destination, Handoff, Grace Cutoff, etc.), each with an `_Avoid_` line for terms not
to use. Read the relevant entries before working in an unfamiliar area, and use the glossary's
exact terminology in code, comments, and communication rather than a synonym it explicitly avoids.

`docs/adr/` holds architecture decision records (e.g. ADR-0001 InstaPay-only cashouts, ADR-0008
Instant Booking). Check for a relevant ADR before changing behavior in an area that has one, and
flag it explicitly if new work would contradict one rather than silently overriding it.

`docs/architecture/` has deeper flow write-ups (`booking-flow.md`,
`booking-realtime-and-concurrency.md`) — note `booking-flow.md` predates ADR-0008 and still
describes the old request-to-book UI flow in places; trust ADR-0008/`CONTEXT.md` over it for the
approval-step question.

## Documentation workflow

Save every confirmed plan as its own file in `docs/plans/YYYY-MM-DD-<topic>.md`, based on
`docs/plans/_template.md`, with frontmatter `status: Draft → Approved → In Progress → Blocked →
Done`. Log it as a row in `docs/plans/README.md`. Write a completion note in
`docs/session-summaries/` when the work ships. Document the plan before writing code.

Issues are tracked as GitHub Issues on `llariesalinas/studybuddy-ui` via the `gh` CLI — they sit
alongside `docs/plans/`, not in place of it (a GitHub issue for work should link to its
`docs/plans/` file, and vice versa). See `docs/agents/issue-tracker.md` and
`docs/agents/triage-labels.md` for the full workflow and label set.

## Commit conventions

Short, imperative commit messages; `fix:` prefix for bug fixes (e.g. `fix: use Manila timezone and
improve booking time validation`). PRs should include a summary, linked issue when available,
screenshots for UI changes, migration notes for schema changes, and note which checks were run
(`npm run lint`, `npm run build`, `python manage.py test`).

## Security

Keep secrets in `.env` files, never commit credentials. Centralize frontend API changes in
`src/services/`; backend settings/CORS live in `backend/backend/settings.py` with
environment-specific values loaded from `.env`.
