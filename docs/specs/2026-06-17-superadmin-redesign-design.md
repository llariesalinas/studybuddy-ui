# Super Admin Redesign — Design Spec

Date: 2026-06-17
Status: Approved
Reference artifact: [`docs/artifacts/2026-06-17-superadmin-redesign-preview.html`](../artifacts/2026-06-17-superadmin-redesign-preview.html)

---

## Overview

Full redesign of the three SuperAdmin screens (`SuperAdminDashboard.vue`,
`SuperAdminUsers.vue`, `SuperAdminReports.vue`) plus two new backend models
(`InstitutionRequest`, `AdminAccountRequest`) to power a new pending-actions feed.

The goals are:
- Make the dashboard actionable, not just informational — surface items only a SuperAdmin
  can act on (institution registration requests, admin account requests, domain exemptions,
  institution activations).
- Upgrade the Users tab from a read-only side panel to a proper modal that lets SuperAdmin
  change role, change institution, grant domain exemption, and suspend, all in one place.
- Deepen Reports with a time-period toggle, completion rate KPI, earnings column on top
  tutors, subject popularity chart, and CSV export.

---

## Scope

| Area | In scope | Out of scope |
|---|---|---|
| Dashboard | KPI cards with trend deltas, enrollment sparkline, pending actions panel, institution table | Escalated flags (needs separate model, deferred) |
| Users | SbSelectModal pill filters, centered detail modal (Profile + Actions tabs) | Bulk actions, pagination (server-side) |
| Reports | Time-period toggle, 4 KPIs, SVG area chart, top tutors earnings, subject popularity, institution completion rate, export | Real chart library (Chart.js etc.) — SVG inline is enough |
| Backend | `InstitutionRequest` model + endpoints, `AdminAccountRequest` model + endpoints, pending-actions aggregate endpoint, role-change PATCH, analytics time-period and subject breakdown | Public institution registration form (landing page integration deferred) |
| Email | None — role changes and approvals are silent | — |

---

## Pending Actions — what qualifies

Only items a SuperAdmin exclusively can act on appear here. Institutional admins handle
tutor applications, withdrawals, and support tickets in their own dashboards.

| Type | Source | Trigger condition |
|---|---|---|
| Institution registration request | `InstitutionRequest` | `status = 'pending'` |
| Institution activation pending | `Institution` | `is_active = False` |
| Admin account request | `AdminAccountRequest` | `status = 'pending'` |
| Domain exemption review | `UserProfile` | non-partner email domain + `is_domain_exempt = False` + `profile_completed = True` |

The `/admin/pending-actions/` endpoint aggregates all four into a single flat list with a
`type` discriminator field, ordered by `created_at` ascending (oldest first).

---

## New models

### `InstitutionRequest`

```python
class InstitutionRequest(models.Model):
    STATUS = [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')]
    institution_name = models.CharField(max_length=200)
    domain           = models.CharField(max_length=100)
    contact_name     = models.CharField(max_length=200)
    contact_email    = models.EmailField()
    note             = models.TextField(blank=True)
    status           = models.CharField(max_length=20, choices=STATUS, default='pending')
    reviewed_by      = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at       = models.DateTimeField(auto_now_add=True)
    reviewed_at      = models.DateTimeField(null=True, blank=True)
```

Approving an `InstitutionRequest` creates a new `Institution` record with `is_active=True`
and copies the domain. Rejecting just sets `status='rejected'`.

### `AdminAccountRequest`

```python
class AdminAccountRequest(models.Model):
    STATUS = [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')]
    requesting_admin = models.ForeignKey(UserProfile, on_delete=models.CASCADE,
                                         related_name='admin_requests_sent')
    institution      = models.ForeignKey('Institution', on_delete=models.CASCADE)
    target_user      = models.ForeignKey(UserProfile, null=True, blank=True,
                                          on_delete=models.SET_NULL,
                                          related_name='admin_requests_received')
    note             = models.TextField(blank=True)
    status           = models.CharField(max_length=20, choices=STATUS, default='pending')
    created_at       = models.DateTimeField(auto_now_add=True)
    reviewed_at      = models.DateTimeField(null=True, blank=True)
```

`target_user` is optional at submission time — the requesting admin may just write a note
("we need Juan Santos promoted"). SuperAdmin fills in the target when approving, which
sets `target_user.role = 'Admin'` and saves.

---

## API changes

### New endpoints

| Method | URL | Description |
|---|---|---|
| `GET` | `/admin/pending-actions/` | Aggregate list of all pending items + total count |
| `GET` | `/admin/institution-requests/` | List `InstitutionRequest` records |
| `POST` | `/admin/institution-requests/` | Create a new registration request (public or admin-submitted) |
| `PATCH` | `/admin/institution-requests/:id/` | Approve (creates `Institution`) or reject |
| `GET` | `/admin/admin-account-requests/` | List `AdminAccountRequest` records |
| `POST` | `/admin/admin-account-requests/` | Institutional admin submits a request |
| `PATCH` | `/admin/admin-account-requests/:id/` | SuperAdmin approves (promotes target user) or rejects |

### Modified endpoints

- `PATCH /admin/users/:id/` — add `role` and `institution` to the allowed patch fields
  (currently only `is_suspended` is accepted). Validate that only a SuperAdmin can change
  `role` to `Admin` or `SuperAdmin`.
- `GET /admin/analytics` — add `period` query param (`7d`, `30d`, `3m`, `all`; default `30d`)
  and return two new keys: `subject_popularity` (list of `{subject, bookings}`) and
  `completion_rate` (float, 0–100).
- `GET /admin/stats` — add `enrollment_trend` key: list of 14 `{date, tutors, tutees}` dicts.

### Pending actions response shape

```json
{
  "count": 4,
  "items": [
    {
      "type": "institution_request",
      "id": 12,
      "title": "New institution: WVSU",
      "meta": "wvsu.edu.ph · submitted 2h ago",
      "created_at": "2026-06-17T08:00:00Z"
    },
    {
      "type": "institution_activation",
      "id": 5,
      "title": "Institution pending activation",
      "meta": "EARIST · added 1d ago",
      "created_at": "2026-06-16T10:00:00Z"
    },
    {
      "type": "admin_account_request",
      "id": 7,
      "title": "Admin account request",
      "meta": "UPV · from admin@upv.edu.ph",
      "created_at": "2026-06-17T06:30:00Z"
    },
    {
      "type": "domain_exemption",
      "id": 44,
      "title": "Domain exemption review",
      "meta": "ana@gmail.com · registered 3h ago",
      "created_at": "2026-06-17T09:15:00Z"
    }
  ]
}
```

---

## Frontend component structure

### Modified files

| File | Changes |
|---|---|
| `src/views/SuperAdminDashboard.vue` | Full rewrite — 4 KPI cards with deltas, enrollment sparkline, pending actions panel, compact institution table. Remove Quick Actions block. |
| `src/views/SuperAdminUsers.vue` | Replace native `<select>` filters with `SbSelectModal` pill triggers. Replace offcanvas side panel with a centered Bootstrap modal. Add Profile and Actions tabs. |
| `src/views/SuperAdminReports.vue` | Add time-period toggle. 4th KPI card (completion rate). SVG area chart (replace CSS bars). Top tutors gains earnings column. Add subject popularity bar chart. Institution breakdown gains completion rate column. Add export CSV button. |
| `src/stores/superadmin.js` | Add: `pendingActions`, `fetchPendingActions`, `approveInstitutionRequest`, `rejectInstitutionRequest`, `fetchAdminAccountRequests`, `approveAdminAccountRequest`, `updateUserRole`, `updateUserInstitution`, `toggleDomainExemption`. Modify `fetchAnalytics` to accept `period` param. Modify `fetchStats` to use new `enrollment_trend` key. |

### New files

| File | Purpose |
|---|---|
| `src/components/SuperAdminUserModal.vue` | Extracted user detail modal (Profile + Actions tabs). Keeps `SuperAdminUsers.vue` lean. |

---

## Design decisions

| Decision | Choice | Reason |
|---|---|---|
| Filters | `SbSelectModal` pill triggers | Consistent with every other filter surface in the app since June 3 |
| User detail | Centered modal, not offcanvas | Offcanvas is awkward on narrow viewports and doesn't support tabbed content cleanly |
| Role change | Direct PATCH, no email | Requested — no notification flow needed |
| Chart library | Inline SVG, no new dependency | Current CSS bar chart upgraded to an SVG area path; avoids a new npm dep |
| Pending actions | Aggregated endpoint, single store key | Avoids four separate fetches on dashboard mount |
| Admin request target user | Optional at submission | Institutional admin may not know the exact user; SuperAdmin picks when approving |
| Export | CSV via `/admin/analytics/export/` returning `text/csv` | Simple, no frontend processing |

---

## Checks to run

- `npm run lint` — zero errors
- `npm run build` — clean build
- `python manage.py test studybuddy.tests` — all existing tests pass
- Manual: SuperAdmin dashboard shows correct pending count matching badge on sidebar
- Manual: Changing a user's role in the modal persists on page reload
- Manual: Time-period toggle in Reports re-fetches and updates all four KPI cards
- Manual: CSV export downloads a valid file with headers
