---
status: accepted
---

# Use logo.dev for Receiving Institution logos, not local assets

PayMongo's receiving-institutions data has no logo/icon field (confirmed against their live API
reference docs — only id, name, provider, and provider_code). Clearbit's logo API, the obvious
fallback, was permanently retired in December 2025. We chose logo.dev (a client-safe publishable
key embedded directly in `<img src="img.logo.dev/{domain}">`) over hosting our own logo assets for
all ~90 InstaPay institutions, and over Brandfetch (the other live alternative) for simplicity —
no strong preference existed between the two. This still requires Studybuddy to own a Receiving
Institution → domain mapping table (PayMongo gives no domain either), but avoids sourcing,
hosting, and licensing ~90 bank/e-wallet logo image files ourselves. Institutions without a mapped
domain, or whose logo fails to load, fall back to the existing generic bank/phone icon.

Displaying these logos is a trademark-usage matter, not a copyright/licensing one — the US
Copyright Office has held that standard bank/network brand marks don't meet the threshold for
copyright registration, and identifying a payout option by its real logo (the same way any
checkout page shows Visa/Mastercard marks) is standard nominative use. logo.dev itself indexes
GCash's mark this way (logo.dev/search/brands/gcash.com), which is one of the reasons it fits
this use case.
