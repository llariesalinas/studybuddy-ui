# 0010 — Persisted Commission Disclosure Acceptance (Deviates from ADR-0007)

## Status

Approved (2026-08-07)

## Context

Tutors are charged a flat 10% platform commission (`COMMISSION_RATE`, `backend/studybuddy/views.py`),
deducted automatically at session completion (`credit_tutor_wallet`). Today this is disclosed only
after the fact, as line items in the wallet transaction ledger (`TutorWallet.vue`) — no tutor is
told about the commission before they start earning under it.

The only existing precedent for an "acknowledge before proceeding" UI pattern in this codebase is
[ADR-0007](0007-off-campus-liability-acknowledgment-not-persisted.md): a Tutee confirming an
off-campus F2F booking sees a click-through warning that is **deliberately never persisted** —
UI-only, no DB record.

## Decision

Commission disclosure acceptance **will be persisted**, not UI-only — a new nullable
`commission_terms_accepted_at` timestamp field on `Tutor` (`backend/studybuddy/models.py`), set
when a tutor acknowledges the disclosure.

This deviates from the ADR-0007 pattern. The distinction: ADR-0007's liability warning is a
one-off safety notice for a single booking; commission is a recurring financial term that affects
every payout a tutor ever receives. If a wallet/commission dispute reaches an admin or support
ticket, an auditable "tutor agreed to the 10% rate on this date" is worth the one column, in a way
a per-booking safety click-through is not.

**Placement:** inline in `TutorPreferenceSetup.vue`, next to the existing `hourly_rate` field —
the first point in onboarding a tutor enters a money figure. No new onboarding step/route.

**Content:** a short disclosure line + checkbox ("StudyBuddy deducts a 10% platform fee from each
completed session's payout"). Not a full Terms & Conditions document or contract — no such
document exists in this app today, and none is introduced by this feature.

**Existing tutors:** rather than grandfathering (`NULL` left in place for tutors who onboarded
before this shipped), existing tutors are **forced to accept retroactively**. Enforced via the
same router-guard mechanism `src/router/index.js` already uses for profile-completion/onboarding
redirects: any Tutor-role route load checks `commission_terms_accepted_at`; if null, force-redirect
to a one-time acceptance screen before any other Tutor route is reachable. This was chosen (over
leaving existing/seeded accounts ungated) specifically because current tutor accounts are test/seed
data, so there is no real-user disruption cost to closing the audit-trail gap for every tutor,
not just new signups.

## Consequences

- New nullable column on `Tutor`; additive migration, no seed-data breakage.
- A second gate joins the router guard's existing set (auth → guest-only → onboarding-step →
  profile-completion → role) — commission-acceptance sits alongside these, evaluated for any
  Tutor-role route.
- Because acceptance is forced retroactively, `commission_terms_accepted_at IS NULL` should not
  persist for any real tutor account post-rollout — unlike ADR-0007's intentionally-absent record,
  a null here after rollout indicates a bug in the guard, not a deliberate design choice.
- If a fuller Terms & Conditions document is wanted later, the same checkbox can be pointed at a
  dedicated Terms page without changing the acceptance/persistence mechanic itself.

## Related

- [ADR-0007](0007-off-campus-liability-acknowledgment-not-persisted.md) — the UI-only pattern this
  decision deviates from.
- [ADR-0008](0008-instant-booking-replaces-request-to-book.md) — establishes the "tutor gates
  enforced via router/search visibility, server-side check as backstop" style this borrows from.
