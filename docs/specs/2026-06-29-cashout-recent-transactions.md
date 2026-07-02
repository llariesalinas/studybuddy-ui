---
title: Cash-Out Recent Transactions (Remove Standalone Destinations)
date: 2026-06-29
status: Draft
feature-slug: cashout-recent-transactions
roles: tutor
---

# Cash-Out Recent Transactions — PRD

## Problem Statement

A tutor who wants to withdraw their earnings currently has to manage payout destinations as a
separate, upfront step: open the wallet, add a destination (GCash or bank account) through its
own modal, then later open a different modal to actually cash out and pick from that saved list.

This is friction for the common case — most tutors repeatedly cash out to the same one or two
accounts — and it doesn't help the less common case either: if a tutor wants to send to a
slightly different account "real quick," they still have to leave the cash-out flow, go add a
destination, then come back to cash out. There's also no quick way to glance at "what did I send
last time and to where" without digging through transaction history.

## Solution

Collapse "add a destination" and "cash out" into one flow. The cash-out modal becomes a single
form: destination type, institution, account number, account name, amount, and an optional note
— always editable, no separate add/manage step required first.

To keep the common case fast, the modal also surfaces the tutor's last 4 cash-out transactions
as tappable shortcuts. Tapping one pre-fills the destination fields (not the amount), so
repeating a recent payout is mostly "tap, set amount, submit" while still allowing every field to
be changed.

Because destinations are no longer a separately verified, saved concept, a lightweight
confirmation step appears whenever the submitted destination details don't match a recent
transaction — a brief "you haven't sent to this account recently, please confirm" checkpoint
before money moves.

## User Stories

1. As a tutor, I want to cash out without first having to add a destination in a separate step,
   so that withdrawing my earnings takes fewer steps.
2. As a tutor, I want to see my last 4 cash-out transactions when I open the cash-out modal, so
   that I can quickly tell what I've sent recently and to where.
3. As a tutor, I want to tap a recent transaction to reuse its account details, so that I don't
   have to retype an account number and name I've used before.
4. As a tutor, I want the amount field to stay blank even after picking a recent transaction, so
   that I don't accidentally repeat a stale amount.
5. As a tutor, I want every field (including ones pre-filled from a recent transaction) to remain
   editable, so that I can correct a typo or update an account name without starting over.
6. As a tutor with no prior cash-out history, I want a blank, fully manual form, so that I can
   still cash out on my very first withdrawal.
7. As a tutor, I want to choose between GCash and bank account destination types inline in the
   cash-out form, so that I'm not forced into a separate destination-type setup step.
8. As a tutor, I want to pick my receiving institution from the existing catalog (the same list
   used today), so that institution names/logos stay consistent with the rest of the app.
9. As a tutor, I want an optional note field on a cash-out, so that I can label what a particular
   withdrawal was for if I want to (e.g. "weekly payout"), without being forced to categorize it.
10. As a tutor, I want to be warned before sending to an account I haven't used in my recent
    transactions, so that I get one last chance to catch a typo before a real transfer happens.
11. As a tutor, I do NOT want to be warned when reusing an account that already appears in my
    recent transactions, so that repeat cash-outs to a known account stay fast.
12. As a tutor, I want the wallet page to no longer show a separate "Destinations" list/section,
    so that there's one less place to manage and one less concept to learn.
13. As a tutor, I expect the ₱50,000 InstaPay-only cap and existing fee logic to keep working
    unchanged, so that this change doesn't affect limits I already understand.
14. As a tutor, I expect my existing transaction history to still show past cash-outs correctly,
    so that nothing about my history changes just because the underlying destination concept
    changed.
15. As a developer, I want the cash-out API to accept destination fields directly on the
    request, so that the backend no longer needs to look up a separately persisted destination
    record to process a withdrawal.
16. As a developer, I want the persisted-destination model and its dedicated endpoints removed
    once nothing references them, so that the codebase doesn't carry an unused parallel concept
    alongside the new inline flow.

## Implementation Decisions

- **Wallet view:** remove the standalone "Destinations" card/section and its add/list UI
  entirely. No replacement management surface is introduced.
- **Cash-out modal:** becomes the single form for this feature — destination type (GCash/Bank),
  receiving institution (from the existing institutions catalog), account number, account name,
  amount, and an optional free-text note. The form is identical whether or not the tutor has
  prior history; history only affects whether fields start pre-filled.
- **Recent transactions:** the modal fetches and displays the tutor's last 4 withdrawal records,
  ordered most-recent-first, with no deduplication and no status filtering (failed/pending/
  completed all count). Each is rendered as a selectable shortcut showing enough detail to
  distinguish accounts (institution, masked account number, date).
- **Pre-fill behavior:** selecting a recent transaction copies its destination type, institution,
  account number, and account name into the form. The amount field is left blank and the note
  field is left blank/independent. All copied fields remain editable afterward.
- **New-destination confirmation:** before submitting, compare the entered destination fields
  against the tutor's recent transactions. If there's no exact match, show a confirmation
  step/dialog summarizing the destination and amount before the request is actually sent. If it
  matches a recent transaction, submit goes straight through with no extra step.
- **API contract change:** the cash-out submission endpoint accepts destination fields directly
  in the request body (destination type, institution id/name/code, account number, account name,
  bank name where applicable) plus amount and the optional note — instead of referencing a
  separately created destination by id. The resulting withdrawal record remains fully
  self-contained, as it already stores these same fields today; this change removes the
  intermediate destination lookup, it doesn't change what gets stored on the withdrawal record.
- **Backend cleanup (bundled in this change, not deferred):**
  - Remove the dedicated destination list/create/update endpoints.
  - Remove the corresponding frontend store actions that fetched/saved/deactivated destinations.
  - Remove the persisted-destination model once the cash-out endpoint no longer depends on it,
    via a schema migration.
- **Destructive migration handling:** dropping the persisted-destination model's table is
  irreversible — any destination data not already mirrored onto past withdrawal records is lost.
  This PRD authorizes the code-level removal and the migration being written, but the actual
  migration run against any environment with real data must get its own explicit go/no-go
  confirmation at execution time, separate from approval of this document.
- **Reason/Note field:** a single optional free-text field. No categorized reason codes (e.g. no
  "payout" vs "urgent" vs "other" picker) — this was explicitly considered and rejected as
  unnecessary friction for an internal, self-directed payout rather than a P2P transfer.
- **Unaffected:** the InstaPay-only rail, the ₱50,000 per-withdrawal cap, fee calculation, and
  the institutions catalog/logo source all stay exactly as they are today.

## Testing Decisions

- **Good tests here assert observable behavior at the API boundary** — request in, response and
  persisted state out — not internal helper call counts or implementation details of how the
  view assembles the withdrawal record.
- **Single highest-level seam:** an API-level Django test (`APITestCase`) extending the existing
  cash-out test class that already exercises `POST` to the cash-out endpoint and asserts wallet
  balance/transaction effects. This is the existing, highest seam for this area of the codebase
  and should be reused rather than introducing a new one.
- **New cases to add to that test class:**
  - A cash-out submitted with inline destination fields (no destination id) succeeds, deducts
    the wallet balance/fee as before, and the resulting withdrawal record stores the submitted
    destination fields.
  - A request for recent transactions returns at most 4 of the authenticated tutor's most recent
    withdrawal records, most-recent-first, with no filtering by status and no deduplication.
  - A cash-out whose destination fields don't match any of the tutor's recent transactions
    requires/triggers the new-destination confirmation path before the withdrawal is created;
    one whose fields do match a recent transaction does not.
  - The now-removed destination list/create/update endpoints return 404 (or are absent from
    `urls.py`), confirming the cleanup landed.
- **No new frontend automated test** is added for this change — the existing repo has no test
  file for the wallet store, and this PRD doesn't introduce one. The frontend change is verified
  through a manual run-through of the cash-out modal (recent-transaction pre-fill, blank-history
  first-time flow, new-destination confirmation) per the project's manual-verification practice
  for UI changes.
- **Prior art:** the existing cash-out test class in the backend test suite, which already mocks
  the relevant external call and asserts balance/transaction effects — extend it rather than
  building a parallel test class.

## Out of Scope

- Any standalone destination editing/deactivating UI or concept — there is no replacement
  "manage my accounts" surface; accounts only exist as fields on past/new withdrawal requests.
- Categorized reason codes for a cash-out (decided against in favor of one optional free-text
  note).
- Actually executing the destructive table-drop migration in any environment with real tutor
  data — that is a separate, explicitly-confirmed step at implementation/deploy time, not
  something this PRD's approval alone authorizes.
- Any change to the InstaPay-only cap, fee logic, recommender system, or the wallet cash-in
  (top-up) feature — none of those are touched by this change.
- Admin-facing tooling for viewing or managing tutor payout history.
- A new frontend automated test seam for the wallet store — explicitly deferred; the chosen seam
  is API-level only.

## Further Notes

- This builds directly on the recently completed InstaPay-only rail consolidation: destinations
  already behave uniformly regardless of which account is used, which is part of why collapsing
  the separate "add destination" step into the cash-out flow doesn't interact with any rail- or
  cap-specific logic.
- The withdrawal record already stores every destination field needed to repeat a transaction,
  which is what makes removing the separately persisted destination model safe without losing
  the data the "recent transactions" feature depends on.
- The destructive migration point is called out twice in this document deliberately — it should
  not be treated as quietly pre-approved by sign-off on the PRD as a whole.
