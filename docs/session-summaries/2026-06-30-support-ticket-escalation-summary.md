# Support Ticket Escalation Summary

Plan: [`docs/plans/2026-06-30-support-ticket-escalation.md`](../plans/2026-06-30-support-ticket-escalation.md)
Issue: [#95](https://github.com/llariesalinas/studybuddy-ui/issues/95)
Date: 2026-06-30

## What shipped

- Added `Escalated` as a Support Ticket lifecycle status.
- Added escalation metadata: reason, escalated-by, and escalated-at.
- Added an institution-admin escalation endpoint that requires a short reason.
- Escalation clears the institution admin as active owner and removes them from the support chatroom.
- Escalation adds a reporter-facing system message in the existing support chat.
- Institution admin support lists exclude active escalated tickets.
- SuperAdmin support lists include escalated tickets and resolved tickets that were previously escalated.
- SuperAdmins can claim escalated tickets without changing the ticket out of `Escalated`.
- Institution admins cannot resolve escalated tickets; SuperAdmins can.
- Added `/superadmin/support` using the existing Support Desk screen.
- Added SuperAdmin sidebar navigation and page header for the support desk.
- Added frontend controls for escalation, including a reason modal and escalation metadata display.

## Checks run

- `python manage.py test studybuddy.tests.SupportTicketEscalationTests --keepdb` passed.
- `python manage.py makemigrations --check --dry-run` passed.
- `npm run build` passed.
- `npm run lint` failed on pre-existing unused variables in `src/views/Dashboard.vue`.
- `python manage.py test --keepdb` ran once and failed in unrelated dashboard recommendation, password reset, SuperAdmin analytics, recommendation, and avatar tests. The new `SupportTicketEscalationTests` class passed.

## Notes

- The implementation keeps escalation on the original Support Ticket and original support chat.
- SuperAdmin claim keeps the ticket status as `Escalated` so the SuperAdmin queue remains stable until resolution.
- The GitHub issue remains linked from the plan doc and plan index.
