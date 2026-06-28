---
status: accepted
---

# InstaPay-only tutor cash-outs, no PESONet rail

Studybuddy previously picked between InstaPay and PESONet per Withdrawal Request based on amount
(PESONet above ₱50,000, InstaPay at or below), and pinned each Payout Destination to whichever
rail its first cash-out used — causing a confirmed bug where a saved bank account became unusable
once a withdrawal needed the other rail. We decided to drop PESONet entirely and always use
InstaPay, confirming via PayMongo's docs that InstaPay's real per-transaction cap is ₱50,000.
Withdrawal Requests above that cap are now blocked client- and server-side with a validation
error instead of being routed to a slower settlement network. This trades the ability to cash out
more than ₱50,000 in a single request for: no more dual-rail logic, no more lock-in bug, and
same-day settlement on every cash-out instead of next-business-day for large ones.

The ₱50,000 cap applies uniformly to both `bank` and `gcash` Payout Destinations. GCash's own
wallet-to-wallet API (used by some other PayMongo/Adyen integrations) advertises a higher
₱100,000 limit, but Studybuddy does not use that API — GCash destinations are disbursed through
the same InstaPay network rail as bank destinations, so GCash inherits InstaPay's cap, not GCash's
own. A direct GCash wallet integration with a higher limit is a distinct, larger integration
effort and is explicitly out of scope here.
