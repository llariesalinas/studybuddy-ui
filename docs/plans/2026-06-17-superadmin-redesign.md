---
title: Super Admin Redesign
date: 2026-06-17
status: Approved
spec: ../specs/2026-06-17-superadmin-redesign-design.md
---

# Super Admin Redesign — Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development to execute task-by-task.

**Goal:** Redesign the three SuperAdmin screens (Dashboard, Users, Reports), introduce two new backend models (InstitutionRequest, AdminAccountRequest), and add a pending-actions feed surfacing only SuperAdmin-exclusive items.
**Stack:** Vue 3, Pinia, Django REST, Bootstrap 5
**Artifact:** [`docs/artifacts/2026-06-17-superadmin-redesign-preview.html`](../artifacts/2026-06-17-superadmin-redesign-preview.html)

---

## Status / Progress Summary

- [ ] Task 1 — Backend models + migrations
- [ ] Task 2 — Backend endpoints (pending actions, institution requests, admin account requests)
- [ ] Task 3 — Backend analytics + stats extensions
- [ ] Task 4 — Superadmin store updates
- [ ] Task 5 — SuperAdminDashboard.vue redesign
- [ ] Task 6 — SuperAdminUsers.vue redesign + SuperAdminUserModal.vue
- [ ] Task 7 — SuperAdminReports.vue redesign

## Changelog

| Date | Change |
|---|---|
| 2026-06-17 | Plan created, status Approved |

---

## Task 1 — Backend models + migrations

**Files:**
- Modify: `backend/studybuddy/models.py`
- Create: `backend/studybuddy/migrations/XXXX_add_institution_request_admin_account_request.py` (auto-generated)

- [ ] Add `InstitutionRequest` model to `models.py`:
  ```python
  class InstitutionRequest(models.Model):
      STATUS = [('pending','Pending'),('approved','Approved'),('rejected','Rejected')]
      institution_name = models.CharField(max_length=200)
      domain           = models.CharField(max_length=100)
      contact_name     = models.CharField(max_length=200)
      contact_email    = models.EmailField()
      note             = models.TextField(blank=True)
      status           = models.CharField(max_length=20, choices=STATUS, default='pending')
      reviewed_by      = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='institution_requests_reviewed')
      created_at       = models.DateTimeField(auto_now_add=True)
      reviewed_at      = models.DateTimeField(null=True, blank=True)

      class Meta:
          ordering = ['created_at']
  ```
- [ ] Add `AdminAccountRequest` model to `models.py`:
  ```python
  class AdminAccountRequest(models.Model):
      STATUS = [('pending','Pending'),('approved','Approved'),('rejected','Rejected')]
      requesting_admin = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='admin_requests_sent')
      institution      = models.ForeignKey('Institution', on_delete=models.CASCADE)
      target_user      = models.ForeignKey(UserProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name='admin_requests_received')
      note             = models.TextField(blank=True)
      status           = models.CharField(max_length=20, choices=STATUS, default='pending')
      created_at       = models.DateTimeField(auto_now_add=True)
      reviewed_at      = models.DateTimeField(null=True, blank=True)

      class Meta:
          ordering = ['created_at']
  ```
- [ ] Run `python manage.py makemigrations` and verify migration file is generated
- [ ] Run `python manage.py migrate` and confirm no errors
- [ ] Commit — `git commit -m "feat: add InstitutionRequest and AdminAccountRequest models"`

---

## Task 2 — Pending actions + request endpoints

**Files:**
- Modify: `backend/studybuddy/admin_views.py`
- Modify: `backend/studybuddy/serializers.py`
- Modify: `backend/studybuddy/urls.py`

- [ ] Add `InstitutionRequestSerializer` and `AdminAccountRequestSerializer` to `serializers.py`:
  - `InstitutionRequestSerializer`: all fields + `reviewed_by_name` (read-only, `source='reviewed_by.get_full_name'`)
  - `AdminAccountRequestSerializer`: all fields + `requesting_admin_name`, `institution_name`, `target_user_name` as read-only computed fields

- [ ] Add `pending_actions_view` to `admin_views.py`:
  ```python
  @api_view(['GET'])
  @permission_classes([IsAuthenticated])
  def pending_actions_view(request):
      # Require SuperAdmin
      if request.user.userprofile.role != 'SuperAdmin':
          return Response(status=403)
      items = []
      # Institution registration requests
      for r in InstitutionRequest.objects.filter(status='pending'):
          items.append({'type':'institution_request','id':r.id,'title':f'Institution registration: {r.institution_name}','meta':f'{r.domain} · {timesince(r.created_at)} ago','created_at':r.created_at})
      # Institutions pending activation
      for inst in Institution.objects.filter(is_active=False):
          items.append({'type':'institution_activation','id':inst.id,'title':f'Activation pending: {inst.institution_name}','meta':f'Added {timesince(inst.created_at)} ago','created_at':inst.created_at})
      # Admin account requests
      for r in AdminAccountRequest.objects.filter(status='pending'):
          items.append({'type':'admin_account_request','id':r.id,'title':'Admin account request','meta':f'{r.institution.institution_name} · from {r.requesting_admin.user.email}','created_at':r.created_at})
      # Domain exemption reviews
      partner_domains = set(Institution.objects.filter(is_active=True).values_list('domain', flat=True))
      for profile in UserProfile.objects.filter(is_domain_exempt=False, profile_completed=True).select_related('user'):
          domain = profile.user.email.split('@')[-1]
          if domain not in partner_domains:
              items.append({'type':'domain_exemption','id':profile.id,'title':'Domain exemption review','meta':f'{profile.user.email} · profile complete','created_at':profile.user.date_joined})
      items.sort(key=lambda x: x['created_at'])
      return Response({'count': len(items), 'items': items})
  ```

- [ ] Add institution request CRUD views:
  - `GET/POST /admin/institution-requests/` — list + create
  - `PATCH /admin/institution-requests/:id/` — approve (creates `Institution`, sets `is_active=True`) or reject

- [ ] Add admin account request views:
  - `GET /admin/admin-account-requests/` — list (SuperAdmin only)
  - `POST /admin/admin-account-requests/` — create (Admin role required)
  - `PATCH /admin/admin-account-requests/:id/` — approve (sets `target_user.role = 'Admin'`) or reject

- [ ] Wire all new URLs into `urls.py`

- [ ] Extend `PATCH /admin/users/:id/` in `admin_views.py` to accept `role` and `institution` fields (SuperAdmin only); validate that `role` is one of `['Tutee','Tutor','Admin','SuperAdmin']`

- [ ] Run `python manage.py test studybuddy.tests` — all existing tests pass
- [ ] Commit — `git commit -m "feat: add pending-actions, institution-request, and admin-account-request endpoints"`

---

## Task 3 — Analytics + stats extensions

**Files:**
- Modify: `backend/studybuddy/admin_views.py`
- Modify: `backend/studybuddy/serializers.py`

- [ ] Extend `GET /admin/stats` response to include `enrollment_trend`: list of 14 dicts `{date, new_tutors, new_tutees}` (use `UserProfile.objects.filter(user__date_joined__date=date, role=...)` grouped by day)

- [ ] Extend `GET /admin/analytics` to accept `period` query param:
  - `7d` → last 7 days, `30d` → last 30 days (default), `3m` → last 90 days, `all` → no date filter
  - Add `completion_rate` key: `(completed_sessions / total_sessions) * 100`, rounded to 1 decimal
  - Add `subject_popularity` key: list of `{subject_name, booking_count}` ordered by count desc, limit 10

- [ ] Add `GET /admin/analytics/export/` returning `text/csv` with headers: `date, institution, tutors, tutees, sessions, completion_rate, gross_revenue, commissions`

- [ ] Run `python manage.py test studybuddy.tests` — all pass
- [ ] Commit — `git commit -m "feat: extend analytics with period filter, completion rate, subject popularity, and CSV export"`

---

## Task 4 — Superadmin store updates

**Files:**
- Modify: `src/stores/superadmin.js`

- [ ] Add state keys:
  ```js
  const pendingActions = ref({ count: 0, items: [] })
  const institutionRequests = ref([])
  const adminAccountRequests = ref([])
  ```
  Add corresponding loading/error keys for each.

- [ ] Add `fetchPendingActions(force = false)` — `GET /admin/pending-actions/`, deduplicated with a promise guard

- [ ] Add `fetchInstitutionRequests(force = false)` — `GET /admin/institution-requests/`

- [ ] Add `approveInstitutionRequest(id)` — `PATCH /admin/institution-requests/${id}/` with `{ action: 'approve' }`, then `fetchPendingActions(true)`

- [ ] Add `rejectInstitutionRequest(id)` — same with `{ action: 'reject' }`

- [ ] Add `fetchAdminAccountRequests(force = false)` — `GET /admin/admin-account-requests/`

- [ ] Add `approveAdminAccountRequest(id, targetUserId)` — `PATCH /admin/admin-account-requests/${id}/` with `{ action: 'approve', target_user_id: targetUserId }`, then `fetchPendingActions(true)` and `fetchUsers({}, true)`

- [ ] Add `updateUserRole(userId, role)` — `PATCH /admin/users/${userId}/` with `{ role }`, optimistically updates `users` array

- [ ] Add `updateUserInstitution(userId, institutionId)` — `PATCH /admin/users/${userId}/` with `{ institution: institutionId }`, optimistically updates `users` array

- [ ] Add `toggleDomainExemption(userId, value)` — `PATCH /admin/users/${userId}/` with `{ is_domain_exempt: value }`, optimistically updates `users` array

- [ ] Extend `fetchAnalytics(institutionId, period)` to pass `period` query param (default `'30d'`)

- [ ] Export all new actions from the store `return` block

- [ ] Run `npm run lint` — zero errors
- [ ] Commit — `git commit -m "feat: extend superadmin store with pending actions, request flows, and user mutation actions"`

---

## Task 5 — SuperAdminDashboard.vue redesign

**Files:**
- Modify: `src/views/SuperAdminDashboard.vue`

- [ ] Replace template with redesigned layout (match artifact):
  - 4 KPI cards row with trend deltas — Total Users (`store.stats.total_tutors + store.stats.total_tutees`), Sessions Today (`store.stats.active_sessions_today`), Revenue MTD (`store.stats.commissions_this_month`), Pending Actions (`store.pendingActions.count`)
  - Two-column split: enrollment sparkline (SVG inline path built from `store.stats.enrollment_trend`) + pending actions panel
  - Pending actions panel: `v-for="item in store.pendingActions.items"` with `type`-based icon/color, one action button per item
  - Institution performance table (existing, keep same data, refine styling)
  - Remove Quick Actions block entirely

- [ ] `onMounted`: call `store.fetchStats(true)`, `store.fetchInstitutionPerformance(true)`, `store.fetchPendingActions(true)`

- [ ] Add `useHaptics` import; fire `vibrate(patterns.light)` on pending action button clicks, `vibrate(patterns.celebratory)` on "Activate" institution button, `vibrate(patterns.medium)` on "Assign" admin request button

- [ ] Apply aurora background via existing `--sb-aurora-bg` token on `.superadmin-dashboard` wrapper (matches artifact — `background: var(--sb-aurora-bg)` on a fixed pseudo-element via the existing app shell, no new CSS needed)

- [ ] Run `npm run lint` and `npm run build` — clean
- [ ] Commit — `git commit -m "feat: redesign SuperAdminDashboard with KPI trends, enrollment sparkline, and pending actions panel"`

---

## Task 6 — SuperAdminUserModal.vue + SuperAdminUsers.vue redesign

**Files:**
- Create: `src/components/SuperAdminUserModal.vue`
- Modify: `src/views/SuperAdminUsers.vue`

### SuperAdminUserModal.vue

- [ ] Props: `user` (object), `institutions` (array)
- [ ] Emits: `close`, `updated`
- [ ] Two tabs: Profile and Actions
  - **Profile tab**: avatar initials (or `profile_picture_url` if present), name, email, role badge, status badge; fields for institution, role, wallet balance (if Tutor), sessions completed (if Tutor), joined date, profile status, avg rating (if Tutor)
  - **Actions tab**: Change role (SbSelectModal, options: Tutee/Tutor/Admin/SuperAdmin), Change institution (SbSelectModal, options from `institutions` prop), Grant domain exemption (button, calls `store.toggleDomainExemption`), Suspend/Reactivate (danger button with inline confirm, calls `store.updateUserStatus`)
- [ ] "Save changes" calls `store.updateUserRole` and/or `store.updateUserInstitution` for dirty fields, then emits `updated`
- [ ] Import `useHaptics`; fire:
  - `light` on tab switch, modal open, modal close, filter pill toggle
  - `medium` on Save changes, Grant domain exemption
  - `celebratory` on Suspend/Reactivate
- [ ] No native `confirm()` — use an inline confirmation state (`suspendConfirm = ref(false)`) that shows "Are you sure?" with confirm/cancel buttons inline

### SuperAdminUsers.vue

- [ ] Replace native `<select>` filter dropdowns with `SbSelectModal` pill triggers:
  - Role filter: options `[{label:'All roles',value:''},{label:'Tutee',value:'Tutee'},...]`
  - Institution filter: options built from `store.institutions`
  - Status filter: options `[{label:'All statuses',value:''},{label:'Active',value:'Active'},{label:'Suspended',value:'Suspended'}]`
- [ ] Replace offcanvas side panel with `<SuperAdminUserModal>` centered modal (`v-if="selectedUser"`)
- [ ] Add Export CSV button (calls `/admin/analytics/export/` via `api.get` with `responseType: 'blob'`, triggers browser download)
- [ ] Keep `filteredUsers` computed — filter logic unchanged
- [ ] Run `npm run lint` and `npm run build` — clean
- [ ] Commit — `git commit -m "feat: redesign SuperAdminUsers with SbSelectModal filters and SuperAdminUserModal"`

---

## Task 7 — SuperAdminReports.vue redesign

**Files:**
- Modify: `src/views/SuperAdminReports.vue`

- [ ] Add time-period pill toggle state (`period = ref('30d')`); on change call `store.fetchAnalytics(selectedInstitutionId.value, period.value)`

- [ ] Replace 3-card KPI row with 4-card row:
  - Gross Revenue (`store.analytics.revenue_summary.gross`)
  - Platform Commissions (`store.analytics.revenue_summary.commissions`)
  - Tutor Payouts (`store.analytics.revenue_summary.payouts`)
  - Completion Rate (`store.analytics.completion_rate + '%'`)

- [ ] Replace CSS bar chart with SVG area chart:
  - Build a `<polyline>` and filled `<path>` from `store.analytics.sessions_over_time.data`
  - Compute `maxVal` for normalization; map data to SVG coordinates (viewBox `0 0 580 90`, Y-axis inverted)
  - Gradient fill using `<linearGradient>` with primary color at 18% opacity → 0%

- [ ] Add Top tutors table with new Earnings column (`store.analytics.top_tutors[n].earnings`)

- [ ] Add Subject popularity horizontal bar chart below institution breakdown:
  - `v-for` over `store.analytics.subject_popularity` (max 5)
  - Each row: label, proportional filled bar, count number
  - Bar width: `(count / max_count) * 100 + '%'`; colors cycle through `--sb-primary`, `#3b82f6`, `#f59e0b`, `#8b5cf6`, `#ec4899`

- [ ] Add completion rate column to institution breakdown table

- [ ] Add Export CSV button — `GET /admin/analytics/export/` with current `period` and `institution_id` params, download as `studybuddy-report-{date}.csv`

- [ ] Import `useHaptics`; fire `light` on time-period toggle, institution filter changes, export button

- [ ] Run `npm run lint` and `npm run build` — clean
- [ ] Commit — `git commit -m "feat: redesign SuperAdminReports with time-period toggle, SVG chart, subject popularity, and CSV export"`

---

## Risks

- `navigator.vibrate` is only available on Android Chrome; iOS silently ignores it. No fallback needed — haptics are enhancement only.
- `enrollment_trend` query groups by date — ensure the Django query uses `Manila` timezone via `django.utils.timezone` when extracting dates, consistent with the rest of the backend.
- `color-mix()` in CSS is used in the app's aurora background; confirm target browser support aligns with what's already shipped.
- `AdminAccountRequest.target_user` is optional at submission; approve endpoint must validate `target_user_id` is present before promoting, returning 400 if missing.
- Subject popularity depends on booking data — if `BookingRequest` or `SessionRecord` doesn't have a direct subject FK, adapt the query to join through the tutor's subjects or session notes.

## Checks to run

- `python manage.py makemigrations --check` — no unapplied model changes
- `python manage.py test studybuddy.tests` — all pass
- `npm run lint` — zero errors
- `npm run build` — clean, no TS/module errors
- Manual: SuperAdmin dashboard pending badge count matches pending actions panel item count
- Manual: Changing a user's role in the modal persists on page reload (check via Network tab — PATCH succeeds)
- Manual: Time-period toggle re-fetches and updates all 4 KPI cards in Reports
- Manual: Export CSV downloads a valid file with correct headers
- Manual: Haptics fire on mobile (Android Chrome) for all wired interactions
