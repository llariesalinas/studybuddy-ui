# Session Summary: Remove Applicant Review from Super Admin
Date: 2026-07-03

## Completed Work
- Added `assert_not_super_admin()` to `BaseAdminView` which raises a 403 PermissionDenied if the caller has the `SuperAdmin` role.
- Added guard calls in the 10 applicant-review and document-renewal API handlers in `backend/studybuddy/admin_views.py`.
- Updated `src/router/index.js` to restrict the `/admin/tutor-applications` route to the `Admin` role only, removing `SuperAdmin`.
- Verified that the `SuperAdmin` dashboard queue (Pending Actions) is unaffected and never displays applicants.
- Added comprehensive backend tests (`SuperAdminApplicantReviewBlockedTests`) in `backend/studybuddy/tests.py` asserting that a `SuperAdmin` receives 403 on all these endpoints, while regular `Admin` access remains unaffected (200). All tests passed successfully.

## Files Touched
- `backend/studybuddy/admin_views.py`
- `backend/studybuddy/tests.py`
- `src/router/index.js`
