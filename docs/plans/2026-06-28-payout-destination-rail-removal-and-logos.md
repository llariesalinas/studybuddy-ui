---
title: Payout Destination Rail Removal and Receiving Institution Logos
date: 2026-06-28
status: Done
spec:
issue: https://github.com/llariesalinas/studybuddy-ui/issues/93
---

# Payout Destination Rail Removal and Receiving Institution Logos

## Status & Progress Summary

**Status:** Done — both slices implemented directly in one `/implement` pass (user chose "both
slices" over splitting issue #93 first).
**Tasks complete:** 2 / 2 slices (rail removal; Receiving Institution logos)
**Next:** None. See
[summary](../session-summaries/2026-06-28-payout-destination-rail-removal-and-logos-summary.md)
for the one notable deviation (logo mapping coverage/keying).

## Problem Statement

Tutors cashing out their wallet balance can hit a confusing dead end: a Payout Destination
(saved GCash account or bank account) gets silently pinned to whichever settlement rail
(InstaPay or PESONet) its first cash-out happened to use. If a tutor later tries to withdraw an
amount that needs the *other* rail, the request is rejected with a message about "pesonet" or
"instapay" that means nothing to them — their saved, previously-working destination now appears
broken for no reason they can see.

Separately, when picking or reviewing a Payout Destination, tutors see only a plain text name
for their bank or e-wallet (e.g. "BANCO DE ORO UNIBANK, INC."). There's no visual brand
recognition — no GCash logo, no BDO logo — making the destination list harder to scan and feel
less trustworthy than the polished, branded experience tutors are used to from banking and
e-wallet apps.

## Solution

Remove the dual-rail concept from cash-outs entirely. Every Withdrawal Request always uses
InstaPay. Withdrawal amounts above InstaPay's real network cap (₱50,000 per transaction) are
rejected with a clear, amount-based validation message — not a rail-mismatch error tied to
destination history. Saved Payout Destinations stop being pinned to a rail, so the same bank
account or GCash account works for every withdrawal up to the cap, every time.

Receiving Institutions gain real logos. Since PayMongo's institution data has no logo field,
Studybuddy renders each institution's brand mark via logo.dev's client-safe image API, resolved
through a Studybuddy-owned Receiving Institution → domain mapping covering the institutions
PayMongo lists. Institutions without a mapped domain, or whose logo image fails to load, fall
back to the existing generic bank/phone icon — so the list never looks broken, only less
decorated, for the long tail.

See [`CONTEXT.md`](../../CONTEXT.md) for the Payout Destination / Receiving Institution / Rail /
InstaPay Cap glossary, and [ADR-0001](../adr/0001-instapay-only-cashouts.md) /
[ADR-0002](../adr/0002-logodev-for-institution-logos.md) for the architectural decisions this PRD
implements.

## User Stories

1. As a tutor, I want my saved bank account to keep working no matter what amount I withdraw, so that I don't get blocked by an error I don't understand.
2. As a tutor, I want my saved GCash destination to keep working no matter what amount I withdraw (up to the platform's limit), so that I have one reliable way to cash out.
3. As a tutor, I want to see a clear error message if I try to withdraw more than the platform allows in one request, so that I know to split it into multiple withdrawals instead of guessing why it failed.
4. As a tutor, I want the maximum withdrawal amount to be visible on the cash-out form itself, so that I don't have to submit and fail before learning the limit.
5. As a tutor, I want to recognize my bank or e-wallet by its real logo when picking a Payout Destination, so that I can find the right one faster than reading text alone.
6. As a tutor, I want to recognize my bank or e-wallet by its real logo when reviewing my saved Payout Destinations, so that I can confirm at a glance which account will receive funds.
7. As a tutor, I want institutions I haven't seen a logo for to still show a clear, non-broken icon, so that the list never looks glitchy or untrustworthy.
8. As a tutor, I want the institution picker to load at a similar speed to today, so that adding logos doesn't make the destination form feel slower.
9. As an admin, I want the withdrawal detail view to stop showing a "rail" value that no longer means anything, so that I'm not confused by a field that no longer reflects real behavior.
10. As an admin, I want historical withdrawal records to remain readable in the admin view even though the rail field is gone, so that past support investigations aren't broken by this change.
11. As a backend maintainer, I want the amount-based rail-selection logic deleted, so that there's no dead branching logic for a rail that's never chosen.
12. As a backend maintainer, I want the Payout Destination rail lock-in validation deleted at its source, so that the bug class (destination pinned to a rail) can't recur even if someone adds a similar check elsewhere later.
13. As a backend maintainer, I want a single, named maximum-withdrawal-amount constant, so that the ₱50,000 cap isn't a magic number duplicated across validation call sites.
14. As a frontend maintainer, I want the institution-to-domain mapping centralized in one data file, so that adding a newly-supported bank or e-wallet is a single, obvious edit.
15. As a frontend maintainer, I want the logo-resolution logic to be a small pure function, so that it's unit-testable without rendering the wallet UI.
16. As a tutor with an existing saved Payout Destination created before this change, I want my destination to keep working without me having to re-add it, so that this change doesn't disrupt anything I already set up.
17. As a tutor, I want withdrawing exactly ₱50,000 to succeed, so that the cap is inclusive and not an off-by-one surprise.
18. As a tutor, I want withdrawing ₱50,000.01 (or any amount above the cap) to fail clearly, so that the boundary is unambiguous.
19. As a QA engineer, I want the existing rail-mismatch test rewritten (not just deleted) to assert the new, correct behavior, so that the regression this change fixes can never silently come back.
20. As a QA engineer, I want a test asserting the cap is enforced independently of a destination's history, so that the lock-in bug class is provably gone, not just hidden by happenstance.
21. As a tutor browsing the institution picker on a slow connection, I want a failed logo image to fall back instantly rather than show a broken-image icon, so that the experience still looks polished.

## Implementation Decisions

### Rail removal

- The amount-based rail-selection function (`get_required_cashout_rail`) is deleted. Every
  Withdrawal Request created by the cash-out endpoint always uses InstaPay as its rail going
  forward.
- A single named constant for the maximum withdrawal amount (₱50,000) replaces the inline
  threshold currently used to choose between InstaPay and PESONet. The same constant is used for
  both the server-side validation and the value the frontend cash-out form uses to block
  over-limit submissions before they reach the server.
- The cap applies uniformly to both `bank` and `gcash` Payout Destinations — Studybuddy disburses
  GCash cash-outs through the same InstaPay network rail as bank cash-outs (GCash appears in
  PayMongo's InstaPay institution list), so there is no separate, higher GCash-specific limit in
  this system. (See ADR-0001 for why GCash's own ₱100,000 wallet-API limit does not apply here.)
- The Payout Destination's rail lock-in field and its associated validation (rejecting a
  withdrawal because the destination was previously used with a different rail) are removed
  entirely — not just bypassed. There is no remaining concept of a destination being "pinned" to
  a rail.
- `WithdrawalRequest`'s rail field is removed via a Django migration. Historical withdrawal rows
  lose their specific rail value (acceptable data loss, per ADR-0001 — the field's purpose no
  longer exists, and the remaining provider/reference/status fields keep historical records
  readable). The admin withdrawal detail view's display of this field is removed alongside it.
- A receiving-institutions listing endpoint that currently accepts a rail/provider query
  parameter only needs to ever resolve InstaPay going forward; PESONet is no longer a reachable
  code path anywhere in the cash-out or destination flows.

### Receiving Institution logos

- A Studybuddy-owned Receiving Institution → domain mapping is added as a frontend data file,
  keyed by the institution identifier/code PayMongo already returns. It aims for full coverage of
  PayMongo's InstaPay institution list (around 90 entries), not just a curated subset.
- Logo images are resolved at render time via logo.dev's client-safe publishable-key image
  pattern (`img.logo.dev/{domain}`) — no backend proxy is needed for this, and no logo image
  files are stored or hosted by Studybuddy.
- A pure resolution function takes an institution (id/code/name) and returns either a logo.dev
  image URL (when a domain mapping exists) or `null`. The destination-list UI renders the
  existing generic bank/phone icon whenever this function returns `null`, and also falls back to
  it on an image load error (broken/unreachable logo URL) — never showing a broken-image
  placeholder.
- Displaying these third-party brand marks is a trademark-usage matter (identifying a payout
  option by its real logo), not a copyright-licensing one — see ADR-0002. No licensing
  integration or attribution requirement applies.

## Testing Decisions

A good test here checks observable behavior at the existing API/HTTP seam or the new pure
function's input/output — not internal call counts or the deleted rail-selection function
directly (it won't exist to test).

- **Backend** (`backend/studybuddy/tests.py`, extending `TutorCashOutTests` and
  `WalletCashOutEdgeCaseTests`, `APITestCase` against `/api/wallet/cash-outs/` and
  `/api/wallet/payout-destinations/` — the existing convention for this area):
  - Rewrite `test_cashout_rejects_rail_mismatch` to assert the opposite of its current behavior:
    a Payout Destination previously used at one amount succeeds at a later withdrawal of a
    different amount (up to the cap), with no rail-mismatch error possible.
  - Add a test asserting a withdrawal of exactly the cap amount succeeds.
  - Add a test asserting a withdrawal one unit above the cap is rejected, with an error message
    referencing the amount limit (not a rail or destination-specific reason).
  - Confirm existing tests in this file that exercise successful cash-outs continue to pass
    unmodified, since they're below the cap and should be unaffected by rail removal.
- **Frontend** (new test file alongside the new institution-domain-mapping module, following the
  existing pure-logic unit-test style used in `src/stores/catalog.test.js`):
  - Test the resolution function returns a logo.dev URL for a mapped institution.
  - Test it returns `null` for an institution with no domain mapping.
  - No new Vue Test Utils component test for `TutorWallet.vue` is in scope — the resolution logic
    is the testable unit; rendering/fallback wiring in the component is exercised manually during
    implementation, consistent with this codebase's existing baseline of `npm run lint` and
    `npm run build` for areas without dedicated component tests.

## Out of Scope

- A direct GCash wallet-to-wallet integration with GCash's own (higher) transaction limit — this
  would be a separate, larger integration effort (see ADR-0001).
- Sourcing or hosting logo image files directly — logo.dev is the sole image source; no local
  asset pipeline is introduced.
- Any change to PESONet's broader availability outside of cash-outs (this PRD only removes it
  from the tutor cash-out flow).
- A new Vue component test file for `TutorWallet.vue` (explicitly deferred per the Testing
  Decisions above).
- Any change to top-up / cash-in flows, which are unaffected by this PRD.

## Further Notes

- This PRD covers two implementation slices that can proceed independently once split: (1) rail
  removal and the associated migration/validation cleanup, and (2) the Receiving Institution logo
  subsystem. Neither depends on the other being merged first.
- The ₱50,000 InstaPay cap and the absence of a logo field in PayMongo's receiving-institutions
  response were both confirmed against PayMongo's live documentation during the design session
  that produced this PRD (see ADR-0001 and ADR-0002 for sources).
- The admin withdrawal view (`AdminWithdrawals.vue`) displays the rail field today and needs its
  display updated as part of the rail-removal slice; it was identified during design but is not
  itself a new architectural decision.

## Changelog

- **2026-06-28** — PRD created from a `/grill-with-docs` session and PayMongo documentation
  research (rail/cap confirmation, logo.dev schema confirmation). Status set to Approved.
- **2026-06-28** — Published to GitHub as issue #93 with the `ready-for-agent` label; linked back
  into this file's frontmatter.
- **2026-06-28** — Implemented both slices via `/implement`. Backend rail removal (migration
  `0060_remove_cashout_rail_fields`, `CASHOUT_MAX_PHP` cap, rewritten/added cash-out tests) and
  frontend logo.dev integration (`src/data/receivingInstitutionLogos.js`, `SbSelectModal` icon
  support) both shipped. Status set to Done. See the
  [session summary](../session-summaries/2026-06-28-payout-destination-rail-removal-and-logos-summary.md)
  for the one deviation: the institution-logo mapping is keyed by name (not PayMongo id) and
  covers ~35 major institutions, not the full ~90, since PayMongo's live institution list wasn't
  reachable for verification in this session.
