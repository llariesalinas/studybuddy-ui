# PR #139 handoff verification — 2026-10-16

Status: In Progress. Verification started against `aa212c1` (fixes in `94bf7f1`).
No application code changed. Existing local reel and documentation work is preserved.

## Database and approval

The configured `backend/.env` matches the documented shared demo project. Database host:
`aws-1-ap-southeast-1.pooler.supabase.com`; database name: `postgres`. The user explicitly approved
backing up and migrating that shared demo in this chat on 2026-10-16. That approval remains valid
for migrations 0087/0088 after the required backup is taken and verified.

The connection is currently rejected by Supabase: `FATAL: (ENOTFOUND) tenant/user not found`.
Both Django and pg_dump reproduce this error, including the retry after approval. No usable
backup was created, no migration was attempted, and database contents were not changed.
The failed archive from the approved retry was marked `.failed` outside the repository.

A working database connection is required next. Restore the Supabase project/connection or
update `backend/.env` locally with the correct connection values. Do not paste credentials into
chat. A different database target requires rechecking its purpose before proceeding.

## Completed checks

| Task | Result |
| --- | --- |
| Fetch branch and confirm code | `claude/beautiful-archimedes-8fu8tm`, fixes at 94bf7f1 included |
| `npm ci` | Pass |
| Virtual-environment `pip install -r backend/requirements.txt` | Pass |
| `npm run lint` | Pass; no application-file changes |
| `npm run build` | Pass |
| Full Vitest suite | 249 pass, 1 skip, 9 known failures; zero new failures versus 045cfe0 |
| Two clock-sensitive tests, `TZ=Asia/Manila` | 2 pass |
| Same two tests, `TZ=UTC` | 2 fail on this branch and on 045cfe0 |
| `python manage.py test --noinput`, from backend/, booking dev tools enabled | 556 discovered; cannot create/connect to test database; no tests executed |
| `makemigrations --check --dry-run` | No changes detected; database-history verification unavailable |
| Backup | Cannot connect; no verified backup |
| Migrations and data spot checks | Pending database connection |

The nine full-suite frontend failures remain six BookingTimeRangePicker cases and three
CSS-token checks. No pre-existing failure was fixed.

The timezone explanation is confirmed: the two tests construct dates and wall-clock fixtures in
the host timezone, while `parseSessionDateTime` in `src/composables/useSessionClock.js` always
interprets session timestamps as Manila time (`+08:00`). Under UTC those fixtures describe different
instants. A separate test-only fix should use explicit offset timestamps and Manila-formatted
fixtures (with a fixed clock for the composable test), or standardize the test process timezone.
No fix was made on this branch.

## Browser checklist

All eight items are pending a working database. They have not been reported as passed or as
application regressions; no failure screenshots exist because browser verification did not start.

| Step | Status |
| --- | --- |
| 1. Established tutor removes final subject | Blocked: database connection |
| 2. First tutee-to-tutor switch still requires setup | Blocked: database connection |
| 3. Deep link reaches commission terms | Blocked: database connection |
| 4. Undo and navigation expiry | Blocked: database connection |
| 5. Two-session remote switch and confirmation | Blocked: database connection |
| 6. Empty categories and system rename protection | Blocked: database connection |
| 7. Review-panel category save refresh | Blocked: database connection |
| 8. Throttled preview and Save | Blocked: database connection |

No regression has been traced to 94bf7f1 during this pass. Database-dependent checks are incomplete,
so this is not a full verification sign-off. The handoff remains In Progress.
