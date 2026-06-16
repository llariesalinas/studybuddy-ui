# Session Summary: Email system hardening (async queue + resilience)

**Date:** 2026-06-06
**Plan:** [2026-06-06-email-async-hardening.md](../superpowers/plans/2026-06-06-email-async-hardening.md)
**Learning artifact:** [email-async-architecture.html](../learning/2026-06-06-email-async-architecture.html)

## What shipped

Hardened the email system that drives login OTP, password-reset, and password-changed mail.

- **Django-Q2 background queue** on the ORM (DB) broker — no Redis. Worker: `manage.py qcluster`.
- **`studybuddy/mailer.py`** — one service all mail routes through: template render, deliver with
  retry, `EmailSendLog` audit row per send, per-recipient cap, sync OTP fn, async task targets.
- **Hybrid model** — login OTP stays **synchronous + hardened** (honest error if it can't send);
  password-reset and password-changed go **async** via `async_task`.
- **`EmailSendLog`** model — backs the per-recipient send cap (counts only `sent` rows) and
  failure auditing. Migration `0050`.
- **Branded HTML + plain-text** templates under `studybuddy/templates/email/`.
- **`views.py` rewired** — OTP via mailer (cap exceeded → 429); reset/changed enqueued async;
  inline `send_mail` helpers removed.
- **Sync/async retry split** (production stability): sync OTP = `EMAIL_SYNC_MAX_ATTEMPTS=2 @ 6s`
  (~12s worst case), async keeps `max_attempts=3`. Prevents a provider outage from stalling
  login long enough to exhaust the request/worker pool.
- **Interactive HTML learning artifact** explaining the architecture.

## Related fix shipped alongside: chat `after_id=0`

While reviewing this work, a bug surfaced in `chat/views.py` `get_message_history` and was fixed
here. The endpoint accepts an `?after_id=` cursor to fetch only messages newer than a given id.
The guard was `if after_id:` — which is **falsy for `0`**. So a request for `?after_id=0`
("give me everything after message 0", i.e. the very start of the conversation) was treated as
*no cursor at all* and silently fell through to the "latest 50 messages, reversed" branch —
returning the **wrong page**. Message ids start at 1 so it rarely bit in practice, but it's a
real correctness trap: `0` is a valid cursor value, and `if 0:` is `False`.

**Fix:** parse the raw param separately and gate on `if after_id is not None:`, so an explicit
`0` is honored as a real cursor instead of being swallowed. This is the classic
"falsy-zero" pitfall — never use a plain truthiness check on an integer that can legitimately
be `0`.

## Decisions

- **Django-Q2 ORM broker** over Celery/Redis — lowest ops burden, Windows-friendly.
- **Cap counts only `sent` rows** — transient failures + retries never lock a user out.
- **Password-*changed* notice is not capped** — security notices should always go out.
- **DB-backed cap** (not cache) — the LocMem fallback isn't shared across web + worker processes.

## Checks run

- `manage.py check` → no issues. ✅
- `makemigrations`/`migrate` → `EmailSendLog` + Django-Q2 tables. ✅
- Locmem verification (no external send): sync OTP, async tasks, enqueue → ORM broker,
  cap counts only `sent`, failed-only history does not trip the cap, 429 on cap. ✅

## Deferred follow-ups

- **Live delivery test** (real Gmail send via Forgot Password) — needs explicit go-ahead.
- **Production ops** — supervise `qcluster` (restart policy) + alert on Django-Q failed tasks
  and `EmailSendLog` failures before calling it production-stable.
