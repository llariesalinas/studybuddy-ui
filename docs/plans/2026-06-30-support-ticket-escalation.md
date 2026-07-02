---
title: Support ticket escalation
date: 2026-06-30
status: Done
spec:
issue: https://github.com/llariesalinas/studybuddy-ui/issues/95
---

# Support ticket escalation

## Problem Statement

Institution admins can claim, chat about, and resolve support tickets for users in their institution, but they do not have a first-class escalation path when an issue needs platform-level attention. When an institution admin cannot handle a ticket, the ticket should move to SuperAdmin attention without losing the reporter context, support chat, or ticket history.

## Solution

Add a formal escalation workflow to the existing Support Ticket lifecycle. Institution admins can escalate an unresolved ticket to SuperAdmin support by entering a short reason. The same Support Ticket moves into an `Escalated` state, clears the institution admin as active owner, and appears in a SuperAdmin Support Desk at a separate `/superadmin/support` route.

SuperAdmins claim escalated tickets from that queue, become the active chat owner, and resolve the ticket when done. Reporters see a calm system message in the existing support chat when their ticket is escalated.

## User Stories

1. As an institution admin, I want to escalate a support ticket I cannot resolve, so that a SuperAdmin can take ownership without me creating a duplicate ticket.
2. As an institution admin, I want to enter a short escalation reason, so that the SuperAdmin understands why the ticket needs platform-level attention.
3. As an institution admin, I want escalated tickets to leave my active queue, so that my queue only shows tickets I can still handle.
4. As an institution admin, I want to keep the original ticket history intact after escalation, so that the SuperAdmin can see the same context I saw.
5. As an institution admin, I want to know whether escalation succeeded, so that I can move on confidently.
6. As an institution admin, I do not want to resolve an escalated ticket, so that responsibility clearly belongs to SuperAdmin support after escalation.
7. As a SuperAdmin, I want a Support Desk route separate from institution admin support, so that escalated support work is easy to find from the SuperAdmin area.
8. As a SuperAdmin, I want to see escalated tickets in a queue, so that I can pick up unresolved issues from institution admins.
9. As a SuperAdmin, I want to claim an escalated ticket, so that I become the active owner before entering the support chat.
10. As a SuperAdmin, I want claimed escalated tickets to remain visible in my support queue, so that I can continue working them until resolution.
11. As a SuperAdmin, I want to enter the existing support chat after claiming, so that I can talk to the reporter without a new conversation thread.
12. As a SuperAdmin, I want to see the escalation reason, so that I understand the blocker before responding.
13. As a SuperAdmin, I want to resolve an escalated ticket, so that the reporter and staff see the final lifecycle state.
14. As a reporter, I want my existing support chat to continue after escalation, so that I do not need to restate the issue.
15. As a reporter, I want a calm system message when the ticket is escalated, so that I understand a higher support level is handling it.
16. As a reporter, I want the same ticket ID to remain active, so that support updates do not feel fragmented.
17. As the system, I want escalation to clear the institution admin as active owner, so that chat ownership reflects the new responsibility.
18. As the system, I want SuperAdmin claim to set the SuperAdmin as active chat owner, so that chat authorization follows the claimed ticket.
19. As the system, I want escalation to preserve linked booking and transaction context, so that investigation data remains attached.
20. As the system, I want only institution admins to escalate institution-scoped tickets, so that users cannot bypass the support workflow.
21. As the system, I want only SuperAdmins to resolve escalated tickets, so that the escalation boundary is enforced server-side.

## Implementation Decisions

- Support Ticket remains the canonical object. Escalation does not create a new ticket, clone a chat, or open a new conversation.
- Add `Escalated` as a support ticket lifecycle status. The canonical lifecycle is `Open -> In Progress -> Escalated -> Resolved`.
- Escalation requires a non-empty reason.
- Escalation records who escalated the ticket and when it happened.
- Escalation clears the active institution admin owner.
- Escalation clears the staff participant from the support chatroom until a SuperAdmin claims the ticket.
- Escalation creates a system chat message for the reporter that says the ticket has been escalated to SuperAdmin support.
- SuperAdmins claim escalated tickets from the queue instead of receiving auto-assignment.
- SuperAdmin claim makes the SuperAdmin the assigned agent and active staff participant in the support chatroom.
- Claimed escalated tickets remain in the `Escalated` status until they are resolved, so the SuperAdmin queue remains stable.
- Institution admin ticket listing excludes escalated tickets from the active Support Desk queue.
- SuperAdmin Support Desk uses the same support screen with a separate route.
- SuperAdmin navigation includes the Support Desk.
- Institution admins cannot resolve escalated tickets.
- SuperAdmins can resolve escalated tickets.
- API behavior is enforced server-side; the frontend only reflects the allowed actions.

## Testing Decisions

- The primary testing seam is the support ticket API lifecycle because it covers authorization, visibility, ownership, and chat side effects at the highest useful boundary.
- Backend tests should cover institution admin escalation with a reason, missing reason rejection, cross-institution protection, institution admin visibility after escalation, SuperAdmin visibility, SuperAdmin claim behavior, and SuperAdmin-only resolution.
- Tests should assert externally visible behavior: response status, ticket status, assigned agent, escalation fields, chatroom owner, list results, and system message creation.
- Existing support chat tests provide prior art for support room creation, ticket context, and support message behavior.
- Frontend verification should ensure the production build passes and the reused Support Desk route compiles for both institution admin and SuperAdmin usage.
- If UI tests are added later, they should exercise the route-level support desk behavior rather than internal component state.

## Out of Scope

- Auto-assigning escalated tickets to a SuperAdmin.
- Creating a second ticket, child ticket, or escalation subrecord.
- Notifications outside the existing support chat system message.
- Email, SMS, or push alerts for escalation.
- A separate SuperAdmin-only support screen design.
- Multi-level escalation beyond institution admin to SuperAdmin.
- Reopening resolved support tickets.
- SLA timers, priority scoring, or escalation analytics.
- Changing the reporter-facing ticket creation flow.

## Further Notes

- The confirmed domain term is `Escalated Support Ticket`: a Support Ticket that an institution admin cannot resolve and has raised to SuperAdmin attention.
- The support chat is the conversation attached to the ticket, not a separate issue object.
- The current implementation should preserve linked booking and transaction context through the escalation lifecycle.
- Published as GitHub issue #95 with the `ready-for-agent` label.
- Implemented on 2026-06-30. See the session summary for verification notes.
