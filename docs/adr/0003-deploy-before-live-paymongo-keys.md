# Deploy to production before live PayMongo keys are approved

PayMongo requires business verification before issuing live (`sk_live_...`) API keys, a process outside our control that can take days to weeks. All PayMongo config (`PAYMONGO_SECRET_KEY`, `PAYMONGO_CASHOUT_MOCK`, etc.) is env-driven, so switching sandbox keys to live keys later is a same-day env var change on the production host, not a redeploy. We decided to stand up production now on sandbox (`sk_test_...`) keys rather than block the whole deployment pipeline on PayMongo approval, then run a manual verification pass with real transactions (small self-funded test payments and cash-outs performed by the team) before opening live payments to all users once live keys land.

**Consequence:** production will briefly run with real user accounts but simulated payments. The `PAYMONGO_CASHOUT_MOCK` flag must be hard-blocked outside local dev (see cleanup phase) so it can never coexist with live keys once the switch happens.
