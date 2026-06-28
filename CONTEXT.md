# Studybuddy

Peer-to-peer tutoring platform for Central Philippine University students. This file is the
project's glossary — domain terms only, no implementation detail.

## Language

### Payouts & cash-out

**Payout Destination**:
A tutor's saved place to receive cash-out funds — a GCash account or a bank account. Stored as
`TutorPayoutAccount`.
_Avoid_: Withdrawal method, payout account (use the model name only when referring to the row
itself, not the concept)

**Receiving Institution**:
The bank or e-wallet provider a Payout Destination sends funds to (e.g. BDO, GCash). Identified
by an institution ID/code sourced from PayMongo's network directory — PayMongo does not provide a
logo for these, only a name and code.
_Avoid_: Bank (too narrow — e-wallets are also receiving institutions), provider

**Withdrawal Request**:
A tutor's request to cash out wallet balance to a Payout Destination. Has its own lifecycle
(pending → processed/rejected/failed/flagged) independent of the Payout Destination it targets.
_Avoid_: Cash-out (use for the user-facing action/flow; Withdrawal Request is the record)

**Rail** _(deprecated term — see ADR 0001)_:
Previously: which interbank settlement network (InstaPay vs PESONet) a Withdrawal Request moved
through. As of ADR 0001, Studybuddy only ever uses InstaPay, so this is no longer a live decision
in the domain — only a historical term for anyone reading older code/data.

**InstaPay Cap**:
The ₱50,000 per-transaction ceiling enforced by the InstaPay network itself (not a Studybuddy
choice) that a single Withdrawal Request cannot exceed.
