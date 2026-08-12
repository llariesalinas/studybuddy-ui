# 0011 — Provisional Late-Cancellation Strikes in a Rolling Window (Supersedes part of ADR-0008)

## Status

Approved (2026-08-10)

## Context

[ADR-0008](0008-instant-booking-replaces-request-to-book.md) replaced tutor pre-approval with
post-hoc accountability: a cancellation inside the 12-hour Grace Cutoff opens a system Support
Ticket, an admin rules excused or counted, and 3 counted strikes in a calendar month suspend the
user's core privilege.

In practice that penalty never fired, for three compounding reasons:

1. **Unreachable.** `can_create_new_booking` returned `True` for any Tutee before it reached the
   strike check, because the tutee-verification grace period short-circuits first and
   `TUTEE_VERIFICATION_ENFORCEMENT_START_DATE` is unset by default. A tutee could late-cancel
   without limit.
2. **Invisible.** Nothing in the app showed a tutee their strike count, and the cancel dialog said
   only "Are you sure?" — no mention of the cutoff, the strike, or the consequence.
3. **Unjudgeable.** Late Cancellation tickets are created `Open` and unescalated, but the
   SuperAdmin ticket list showed only *escalated* tickets, so no admin ever saw one. Since only a
   `counted` verdict incremented the count, the count was permanently zero.

The calendar-month window had its own problem independent of the bugs: three cancellations on
Jan 30, Jan 31 and Feb 1 counted as one, while three in the first week of a month counted as
three. The reset date was also shared and arbitrary — everyone's slate cleared at midnight on the
1st regardless of when they misbehaved.

## Decision

**The window is rolling.** A strike is active from the moment its ticket is opened until
`STRIKE_WINDOW_DAYS` (14) later, then it expires on its own. There is no shared reset date. The
cap (`STRIKE_CAP`, 3) counts active strikes. The boundary is strict — a ticket at exactly 14 days
has expired.

**Counting is provisional.** An unresolved ticket counts against the cap immediately, before any
admin looks at it. Only an explicit `excused` verdict relieves it. Resolving as `counted` changes
nothing about the count, because the ticket was already counting.

The alternative — count only after an admin rules — is what shipped with ADR-0008 and is what made
the penalty a no-op. It also makes the penalty depend on admin responsiveness: a user who
late-cancels on a Friday faces no consequence until someone reviews the ticket, which is precisely
when the deterrent is needed. Provisional counting inverts the default: the cost is immediate, and
review is the appeal.

**The block is provisional; the money is not.** The P50 tutor wallet deduction stays gated on an
explicit `counted` verdict. This asymmetry is deliberate and is the crux of this ADR. A block is
recoverable — excusing the ticket lifts it, and in the worst case it expires in 14 days. A wallet
debit is not: it writes a `Transaction` row and can push the balance negative. Applying money
automatically to unreviewed tickets would make every erroneous auto-open a real financial loss
requiring a manual reversal. So the cheap, reversible consequence is automatic, and the expensive,
irreversible one waits for a human.

**Verdicts are not reversible.** A confirmed `counted` is final; the pre-existing idempotency
guard (`if ticket.resolution_verdict: return 400`) stays. The guard against a misclick is a
two-step confirmation modal in the admin UI, which names the penalized user, states that the
verdict cannot be reversed, and calls out the P50 deduction when the penalized user is a Tutor.

**Existing tickets are excused at cutover** by data migration (`0081_strike_window_index`). Every
unresolved Late Cancellation ticket that exists when the migration runs is marked `excused`.
Without this, provisional counting is retroactive: users would be blocked on deploy for
cancellations made under the old, invisible, month-based rule, having never seen a count.

## Consequences

- **This is a live behavior change, not just a bug fix.** Tutee strike caps were unreachable
  before; they now bite. The cutover backfill is what makes that safe.
- A misclicked `counted` verdict blocks a user for up to 14 days and is recoverable only through
  Django admin. Accepted in exchange for a simple, auditable one-shot verdict; the confirmation
  modal is the only guard.
- The strike query broadened from `resolution_verdict='counted'` to
  `.exclude(resolution_verdict='excused')`, which matches rows the old query skipped. Because the
  recommender runs this check once per candidate tutor, the composite index
  `ticket_strike_window_idx` on `(penalized_user, category, created_at)` ships in the same
  migration and is required, not an optimization.
- A strike excused after a user was told "you can book again on X" unblocks them early, and there
  is no push channel to tell them — they find out on the next `/profile/status/` hydration.
  Accepted; a notification is a later improvement.
- `STRIKE_WINDOW_DAYS` (14) and `BOOKING_HORIZON_DAYS` (14) are numerically equal and completely
  unrelated. They must not be merged into one constant.
- The cancel modal now reads strike state from `/profile/status/`, so a slow or failed call must
  never block cancelling — the modal opens instantly and silently drops the strike line when the
  refresh fails.

## Related

- [ADR-0008](0008-instant-booking-replaces-request-to-book.md) — establishes the Grace Cutoff and
  the post-hoc accountability model; its calendar-month cap is superseded here.
- `CONTEXT.md` — canonical definitions of Active Strike, Counted Strike, and Strike Cap.
