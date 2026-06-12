# Dashboard top 5 Redis cache summary

Implemented backend-enforced top 5 tutee dashboard recommendations from the existing
hybrid algorithm. The dashboard recommendation cache key is now version- and
limit-aware, cache hits are defensively sliced to the requested limit, and fallback
results are cached with the same top 5 limit.

Added cache invalidation/version bumps for rating submissions, tutor setup/profile
changes, and tutor subject changes. The frontend dashboard now renders five loading
rows, pages recommendations in groups of five, and hides pagination when only one page
is available.

Verification:

- `python manage.py test studybuddy.tests.DashboardRecommendationServiceTests studybuddy.tests.StudentDashboardRecommendationTests --keepdb` passed.
- `python manage.py test studybuddy --keepdb` ran the full suite but failed in two
  pre-existing password-reset email tests where `mail.outbox` was empty.
- `npm run build` passed after rerunning outside the sandbox because Vite/esbuild hit
  `spawn EPERM` in the sandbox.
