---
title: Enable email delivery on the demo deployment
date: 2026-08-05
status: In Progress
summary: Split the email kill switch off IS_DEMO_DEPLOYMENT so the paid Render instance can send real mail over SMTP.
spec:
---

# Enable email delivery on the demo deployment

## Status/Progress Summary

In Progress as of 2026-08-05. Steps 1-4 are done and verified locally: `EMAIL_DELIVERY_DISABLED`
is split out in `settings.py`, all nine mail guards in `mailer.py`/`email_utils.py` point at it,
the flag is documented in `backend/.env.example`, and `EmailDeliveryDisabledTests` covers both
switch positions (4 tests, passing alongside the existing 4 `EmailUtilsRoleLabelTests`). Steps 5-6
remain: the user must confirm a live OTP email arrives on the deployed branch. No frontend change
was needed — `Login.vue` already handles both the OTP-challenge and direct-login responses.

Step 5 turned out to need **no env changes at all**: all five SMTP vars are already set on Render,
and `RESEND_API_KEY` / `EMAIL_DELIVERY_DISABLED` are correctly absent. The demo's Basic Auth gate
was also deliberately removed (private-group testing), so `IS_DEMO_DEPLOYMENT` is already `False`
there and the old code had already stopped suppressing email. That reframes this change: it is not
what unblocks delivery — the paid instance is — it removes the footgun where re-gating the demo
would silently switch email and login OTP back off.

## Goal

Turn real email delivery back on for the Render demo deployment. Render's free tier blocked
outbound SMTP, which forced a scoped reduction (all email suppressed, login OTP disabled) in
`docs/plans/2026-07-05-demo-deployment-plan.md`. The deployment is now on a paid instance, which
lifts the block on ports 465/587, so Gmail SMTP works and the reduction can be reversed.

## Approach

The blocker was never credentials — `backend/.env.demo` already carries working Gmail SMTP values.
It was two stacked constraints:

1. Render blocks outbound SMTP on **free** web services (ports 25/465/587). Upgrading to any paid
   instance type lifts it for 465 and 587; port 25 stays blocked platform-wide (EC2).
2. The HTTPS fallback (Resend) needs a verified domain, which StudyBuddy does not own.

The paid instance resolves (1), which makes (2) moot — SMTP on 587 needs no domain.

The code change is one flag split. `settings.IS_DEMO_DEPLOYMENT` currently does double duty: it
marks "this is the demo" *and* suppresses every outbound send, via ten guard sites in `mailer.py`,
`email_utils.py`, and `views.py`. Introduce a separate, env-driven `EMAIL_DELIVERY_DISABLED` that
the mail guards check instead, defaulting to **off** (mail sends). `IS_DEMO_DEPLOYMENT` keeps its
genuinely demo-scoped duties (Basic Auth gate). `LOGIN_OTP_DISABLED` keys off email delivery rather
than demo-ness, since the OTP is only skippable when mail cannot be sent.

Keeping the switch rather than deleting the guards preserves a one-env-var rollback if Gmail's
daily cap is hit mid-defense.

## Steps

1. Split the flags in `backend/backend/settings.py`; rewrite the stale SMTP comment.
2. Point the nine guard sites in `mailer.py` / `email_utils.py` at `EMAIL_DELIVERY_DISABLED`, and
   reword their log lines from "Demo deployment:" to "Email delivery disabled:".
3. Document `EMAIL_DELIVERY_DISABLED` in `backend/.env.example`; leave it unset in `.env.demo` so
   the demo sends.
4. Add test coverage for both flag positions (suppressed when on, delivered when off).
5. Set the SMTP env vars in the Render dashboard and verify with a real OTP login (user action).
6. Amend `docs/plans/2026-07-05-demo-deployment-plan.md` and its session summary, since this
   reverses a decision they record.

## Risks

- **Paid *instance*, not paid workspace.** The block lifts per service instance type. A paid team
  plan with the service still on Free keeps the SMTP block.
- **Gmail rewrites `From:`** to the authenticated account regardless of `DEFAULT_FROM_EMAIL`.
- **Gmail send caps** (~500/day for consumer accounts) sit above the app's own
  `EMAIL_SEND_CAP_PER_HOUR`, but a demo with many seeded users could still trip them.
- **App password handling** — it belongs in Render's env panel, never in a committed `.env`.
- Re-enabling login OTP puts a live mail send on the login critical path; a Gmail outage becomes a
  login outage. `EMAIL_DELIVERY_DISABLED=true` is the rollback.

## Checks to run

- `python manage.py test studybuddy` from `backend/` — full suite green.
- `python manage.py test studybuddy.tests.EmailDeliveryDisabledTests` — the new coverage.
- Post-deploy: request a login OTP on the demo and confirm the mail arrives.

## Changelog

- **2026-08-05** — Plan created and Steps 1-4 implemented in the same session. Confirmed against
  Render's changelog that the SMTP block applies to free web services only and that paid instances
  regain ports 465/587 (25 stays blocked platform-wide, an EC2 constraint), which is what makes
  this reversible at all. Chose to split a new flag rather than delete the nine guards, so the
  suppression stays available as a rollback. Corrected one detail from the initial write-up: there
  are nine guard sites, not ten — `views.py:1525` checks `LOGIN_OTP_DISABLED`, not the mail flag.
  The existing `@override_settings(LOGIN_OTP_DISABLED=True)` test needed no change since the
  setting name is unchanged.
- **2026-08-05 (cont.)** — Reviewed the live Render env list and found `DEMO_BASIC_AUTH_USER` /
  `DEMO_BASIC_AUTH_PASSWORD` absent; the user confirmed the gate was deliberately removed because
  testing moved to a private invited group. So `IS_DEMO_DEPLOYMENT` is already `False` on the demo,
  meaning the old code had *already* stopped suppressing email there — this change is therefore not
  what unblocks delivery (the paid instance is), but it removes a live footgun: under the old
  coupling, re-adding the Basic Auth pair to re-gate the demo would have silently switched email and
  login OTP back off. All five SMTP vars are already set on Render; `RESEND_API_KEY` and
  `EMAIL_DELIVERY_DISABLED` are correctly absent, and `EMAIL_USE_TLS` defaults to `True`. Nothing to
  add to the env. Also noted `OTP_DEBUG_CODE_ENABLED` is not a fallback for failed delivery —
  `views.py:649-657` sends first and re-raises, so a failed send 500s before `debug_code` is set.
