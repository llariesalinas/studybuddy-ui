---
title: Email system hardening (async queue + resilience)
date: 2026-06-06
status: Done
spec: ../../learning/2026-06-06-email-async-architecture.html
---

# Email system hardening (async queue + resilience)

## Goal

Stop a third-party email outage (Gmail SMTP today, Resend later) from blocking logins or
silently dropping mail, and make sends retried, observable, abuse-resistant, and branded.

## Approach

Centralize all sending in one `studybuddy/mailer.py` service and route every flow through it.
Add a **Django-Q2** background queue on the **ORM (DB) broker** — no Redis to run, one
`manage.py qcluster` worker. Keep a **hybrid model**:

- **Login OTP stays synchronous but hardened** (short timeout + a couple of retries, honest
  error on failure) because the user is actively waiting for the code.
- **Password-reset link and password-changed notice go async** via `async_task`, delivered
  off the request thread by the worker (which also handles task-level retries).

A small `EmailSendLog` model backs both a **per-recipient send cap** (counts only `sent`
rows) and **failure auditing**. The three emails became **HTML + plain-text** Django
templates. The module is named `mailer.py`, not `email.py`, to avoid shadowing Python's
stdlib `email` package.

**Sync vs async retry budgets are split** (production stability): the sync OTP path uses
`EMAIL_SYNC_MAX_ATTEMPTS=2 @ EMAIL_SYNC_TIMEOUT=6s` (~12s worst case, so a provider outage
can't exhaust the request/worker pool), while the async path keeps `max_attempts=3`.

## Steps

1. Add `django-q2`; register `django_q`; add `Q_CLUSTER` (ORM broker) + email tuning constants.
2. Add `EmailSendLog` model + migration.
3. Build `mailer.py` (render, deliver+retry+log, cap, sync OTP fn, async task fns, enqueue helpers).
4. Add branded HTML+txt templates under `studybuddy/templates/email/`.
5. Rewire `views.py`: OTP sync (cap → 429); reset/changed via `async_task`; drop inline `send_*` helpers.
6. Split sync vs async retry budgets.
7. Write the interactive HTML learning artifact.

## Risks

- **Worker not running** → async mail queues but never sends. OTP (critical path) is sync so
  login is unaffected. Production: supervise `qcluster` (restart policy) + alert on failures.
- **Per-account cap false-positives** on shared inboxes — window/limit is env-configurable.
- **Cache is per-process** without `REDIS_URL`, so the cap is DB-backed (correct across the
  web + worker processes).

## Checks to run

- `python manage.py check` → no issues. ✅
- `makemigrations`/`migrate` → `EmailSendLog` + Django-Q2 tables created. ✅
- Locmem-backend verification (no external send): sync OTP, async tasks, enqueue → ORM broker,
  cap counts only `sent`, failed-only history does not trip the cap. ✅
- **Deferred (needs go-ahead):** live delivery test via Forgot Password to a real inbox.

## Changelog

<!-- Newest first. One line per meaningful alteration to this plan. -->

- **2026-06-06** — Plan finalized as **Done**: Phases 1–2 implemented and verified, sync/async
  retry split applied, learning artifact written. Deferred: live delivery test + production
  worker supervision/alerting. Shipped alongside an unrelated `after_id=0` chat fix (see summary).
