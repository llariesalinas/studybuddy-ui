# Progress Log

## 2026-05-12

Implemented the chat upgrade:

- Added typed chat messages with `text`, `system`, and `booking_event` support, JSON metadata, read timestamps, and room `updated_at`.
- Added canonical one-room-per-tutor/tutee behavior for new inquiry and booking events.
- Added enriched room/history APIs with unread counts, last message, updated timestamps, and pending/upcoming booking context.
- Added a room read endpoint and WebSocket events for messages, typing indicators, read receipts, room updates, and booking context updates.
- Added booking event creation for new booking requests, approvals, rejections, and pending F2F location edits.
- Updated the chat store for a global updates socket, active room socket, reconnect handling, optimistic messages, unread badges, typing indicators, read receipts, and booking context refreshes.
- Updated the chat screen with session cards, session detail links, read status, typing display, and tutor-only pending F2F location editing.
- Added the authenticated app header unread badge and latest-message popup for chat.
- Added targeted backend tests for the read endpoint and pending location chat event.

Files/areas changed:

- `backend/studybuddy/chat/`
- `backend/studybuddy/views.py`
- `backend/studybuddy/tests.py`
- `backend/studybuddy/migrations/0042_chat_message_metadata_room_updated.py`
- `src/stores/chat.js`
- `src/views/Chat.vue`
- `src/App.vue`

Checks run:

- `npx eslint src\App.vue src\views\Chat.vue src\stores\chat.js` - passed.
- `npm run build` - passed after rerunning outside the sandbox because esbuild worker spawn failed with `EPERM` in the default sandbox.
- `.\venv\Scripts\python.exe manage.py check` - passed.
- `.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run` - passed.
- `python manage.py test studybuddy.tests.ChatFeatureTests` - blocked because the global Python environment is missing `daphne`.
- `.\venv\Scripts\python.exe manage.py test studybuddy.tests.ChatFeatureTests` - blocked by an existing `test_postgres` database requiring interactive deletion.
- `.\venv\Scripts\python.exe manage.py test studybuddy.tests.ChatFeatureTests --keepdb` - blocked by existing inconsistent test DB state, failing on duplicate `studybuddy_partnerinstitution`.
- `$env:DB_NAME='codex_chat_tests'; .\venv\Scripts\python.exe manage.py test studybuddy.tests.ChatFeatureTests --noinput` - also blocked during migration setup by duplicate `studybuddy_partnerinstitution`, indicating a pre-existing migration-history issue before the chat tests execute.

Known limitations:

- Full backend test execution is blocked by the current PostgreSQL test database/migration setup. The new chat tests are present but did not execute.
- Manual two-account real-time browser testing was not completed in this pass.
- Attachments, reactions, search, online presence, and tutee approval for location changes remain out of scope.
