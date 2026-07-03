---
title: Remove Applicant Review from Super Admin
date: 2026-07-03
status: Done
---

# Remove Applicant Review from Super Admin

## Goal

Remove the ability for Super Admins to review and approve/reject applicant applications (tutor/tutee and document renewals). This is an institution-Admin responsibility.

## Approach

- Add a `assert_not_super_admin()` helper method to `BaseAdminView`.
- Call this helper in all applicant-touching endpoints in `backend/studybuddy/admin_views.py`.
- Remove the `SuperAdmin` role from the `/admin/tutor-applications` route in the frontend router (`src/router/index.js`).

## Steps

1. Updated `BaseAdminView` with `assert_not_super_admin(request)`.
2. Added the helper call to the `get` and `patch` methods of the 4 applicant review classes (10 call sites).
3. Removed `'SuperAdmin'` from the `role` array of the `/admin/tutor-applications` route in `src/router/index.js`.
4. Verified `App.vue` sidebar has no `/admin/tutor-applications` link conditionally rendered for SuperAdmin.
5. Added `SuperAdminApplicantReviewBlockedTests` to `tests.py` with 12 tests (10 403 cases for SuperAdmin and 2 200 cases for regular Admin).

## Checks to run

- `python manage.py test studybuddy.tests.SuperAdminApplicantReviewBlockedTests` - PASS
