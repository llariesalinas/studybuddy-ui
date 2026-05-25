# Tutor Profile Redesign — Design Spec

**Date:** 2026-05-25  
**Topic:** Tutor Profile Aurora Bento Redesign  
**Route:** `/tutor-profile` → `src/views/TutorProfile.vue`  
**Role:** Tutor only (`meta: { role: 'Tutor' }`)  
**Styling:** Scoped CSS glassmorphism (no Tailwind, Bootstrap Icons only)

---

## 1. Goal

Replace the plain Bootstrap layout of the tutor profile page with an Aurora Bento glassmorphism aesthetic matching the tutee profile system design. All existing data fields are preserved. Real avatar photo upload is wired to a new `/tutor/profile/avatar/` backend endpoint. Course + year level selection uses a combined modal sheet. Teaching level uses 3 fixed card options.

---

## 2. Architecture & Data Flow

### 2a. Backend Updates (`backend/studybuddy/`)

#### New: `POST /tutor/profile/avatar/`
- Mirrors `upload_tutee_avatar` exactly.
- Accepts `multipart/form-data` with field `avatar`.
- Validates: file present, `image/*` content-type, max size 5 MB.
- Saves to `request.user.userprofile.profile_picture`.
- Returns `{ "profile_picture_url": "..." }`.
- Auth: `@permission_classes([IsAuthenticated])`.
- Register in `urls.py`: `path('tutor/profile/avatar/', views.upload_tutor_avatar)`.

#### Update: `TutorProfileSerializer`
- Add `profile_picture_url = serializers.SerializerMethodField()`.
- Method: `return request.build_absolute_uri(obj.profile.profile_picture.url) if obj.profile.profile_picture else None`.
- The serializer needs `context={'request': request}` passed from `get_tutor_profile` view — update the view to pass context.
- Add `profile_picture_url` to `Meta.fields`.

#### Existing endpoints (no change needed)
- `PUT /tutee/profile/update/` — handles `fname`, `lname`, `course`, `year_level`, `bio`. Still called from `saveProfile()`.
- `PUT /tutor/update/` — handles `hourly_rate`, `teaching_level`, `can_online`, `can_f2f`, `response_time`. Still called from `saveProfile()`.
- `GET /tutor/profile/` — updated via serializer change above.
- `GET /tutor/subjects/`, `POST /tutor/subjects/add/`, `PATCH /tutor/subjects/update/:code/`, `DELETE /tutor/subjects/remove/:code/` — all unchanged.
- `GET /courses/`, `GET /subjects/` — unchanged.

### 2b. Frontend State (`src/views/TutorProfile.vue`)

The `profile` reactive object and all subject/modal logic carry over from the current implementation. Additions:

```js
const avatarUrl = ref(null)          // populated from profile_picture_url on load
const isCourseYearModalOpen = ref(false)
const draftCourse = ref('')          // staged inside modal, committed on confirm
const draftYearLevel = ref(null)     // staged inside modal, committed on confirm
```

**Teaching level options** (fixed array, no API call):
```js
const teachingLevelOptions = [
  { value: 'Elementary', icon: 'bi-backpack', label: 'Elementary' },
  { value: 'High School', icon: 'bi-mortarboard', label: 'High School' },
  { value: 'College', icon: 'bi-book', label: 'College' }
]
```

---

## 3. UI & Interaction Design

### 3a. Page Shell

Aurora mesh background (`--sb-bg` base + fixed radial blobs) behind a centered content column (`max-width: 1100px`, `padding: 24px`). No sidebar overlap — rendered inside App.vue's main content slot as normal.

### 3b. Segment Layout

```
┌─────────────────────────── HEADER (full width) ────────────────────────────┐
│  [Avatar]  Daniel Tan · Tutor · ✓ Verified    [View Profile] [Manage Sess] │
└────────────────────────────────────────────────────────────────────────────┘
┌──────────── LEFT col (7/12) ─────────────────┐  ┌── RIGHT col (5/12) ──────┐
│  IDENTITY SEGMENT                            │  │  FINANCIALS SEGMENT      │
│  • fname input (full name split on save)     │  │  • Hourly rate stepper   │
│  • email input (disabled)                    │  │  • Response time pills   │
│  • Course & Year Level chip + Change btn     │  │                          │
├──────────────────────────────────────────────┤  ├──────────────────────────┤
│  EXPERTISE SEGMENT                           │  │  SPECIALIZATIONS SEGMENT │
│  • 3 teaching level cards                    │  │  • Subject pills + Add   │
│                                              │  │  • Bio textarea          │
│                                              │  │  • Online / F2F checks   │
└──────────────────────────────────────────────┘  └──────────────────────────┘
┌─────────────────── BOTTOM ACTIONS (full width) ────────────────────────────┐
│                              [Discard Changes]   [Save Profile]            │
└────────────────────────────────────────────────────────────────────────────┘
```

### 3c. Header Segment

- Avatar: 80×80 rounded square. If `avatarUrl` is set, shows `<img>`. Otherwise shows initials in `--sb-primary` background.
- Clicking avatar triggers a hidden `<input type="file" accept="image/*">`.
- On file select: immediate POST to `/tutor/profile/avatar/` via `FormData`. Preview updates optimistically. Error shows toast.
- Camera overlay icon appears on hover (Bootstrap Icon `bi-camera`).
- Name below avatar: `profile.fullName` (fname + lname).
- Badge row: "Tutor" label · verified checkmark (static for now).
- Top-right: "View Public Profile" ghost button + "Manage Pending Sessions" primary button.

### 3d. Identity Segment

- **Full Name input**: single `v-model` on `profile.fullName`. Split on save (`fname = names[0]`, `lname = names.slice(1).join(' ')`).
- **Email input**: disabled, shows `profile.email`.
- **Course & Year Level row**: shows current selection as two chips (`BSIT - Info Tech` · `4th Year`). A "Change →" button opens the combined modal.
  - If neither is set: chips show "No course set" / "No year set" in muted style.

### 3e. Course & Year Level Modal

Triggered by the "Change →" button. Closes on confirm or cancel.

**Structure:**
```
[Modal Header]
  Course & Year Level
  
[Section 1 – Course]
  Radio card grid (2 cols) from GET /courses/
  Each card: course_code bold · course_name small
  Selected card: primary border + bg-primary/5

[Section 2 – Year Level]
  Grid of year buttons (3-4 cols)
  Same 16 options as current (Grade 1–12, 1st–4th Year College)
  Selected: filled primary background

[Footer]
  [Cancel]  [Confirm Selection]
```

**Behavior:**
- Opens with `draftCourse` and `draftYearLevel` pre-set to current `profile.course` / `profile.year_level`.
- On **Confirm**: `profile.course = draftCourse`, `profile.year_level = draftYearLevel`, modal closes.
- On **Cancel**: draft values discarded, modal closes.
- Changes only write to server on "Save Profile".

### 3f. Expertise Segment

Three interactive cards side-by-side:

| Option | Bootstrap Icon | Value saved |
|--------|---------------|-------------|
| Elementary | `bi-backpack` | `'Elementary'` |
| High School | `bi-mortarboard` | `'High School'` |
| College | `bi-book` | `'College'` |

- Selected card: primary border, icon fills with `--sb-primary`.
- Clicking a card sets `profile.teaching_level` immediately (staged, saved on Save Profile).

### 3g. Financials Segment

**Hourly Rate Stepper:**
- Decrement button (`−`), rate display (`₱ 280.00`), increment button (`+`).
- Minimum: ₱50. No maximum.
- Step: ₱10.
- Decrement disabled and visually muted when `profile.hourly_rate <= 50`.
- `v-model.number` bound to `profile.hourly_rate`.

**Response Time Pills:**
- Three pill buttons: `Within 1 Hour` (`within_1_hour`) · `Within a Few Hours` (`within_few_hours`) · `Within a Day` (`within_a_day`).
- Active pill: filled primary. Inactive: ghost border.
- Clicking sets `profile.response_time`.

### 3h. Specializations Segment

**Subject Pills + Add:**
- Existing subjects render as green pills with `×` remove button.
- "+ Add" opens the subject picker modal (existing logic, glassmorphism reskin).
- Counter badge: `N/8`.

**Subject Picker Modal (reskin only):**
- Keep all logic: search input, category pills, scrollable list with checkboxes, accordion per-subject description textarea.
- Reskin backdrop to `rgba(15, 23, 42, 0.5)`, modal card to `.glass-segment` style, inputs to `.input-glass` class.

**Bio Textarea:**
- `v-model` on `profile.bio`.
- Character counter below: `0/500`. Counter text transitions `var(--sb-primary)` → `var(--sb-danger)` approaching 500.

**Session Mode:**
- Two labeled checkboxes: Online (`v-model="profile.can_online"`) · Face-to-Face (`v-model="profile.can_f2f"`).

### 3i. Bottom Actions

- **Discard Changes**: reloads profile from server (calls `loadProfile()` again). Resets local state without page refresh.
- **Save Profile**: calls `saveProfile()`, which runs:
  1. `PUT /tutee/profile/update/` — fname, lname, course, year_level, bio
  2. `PUT /tutor/update/` — hourly_rate, teaching_level, can_online, can_f2f, response_time
  3. `syncSubjects()` — diffs and applies subject add/remove/update calls
  4. Success: `toastStore.push('Profile Updated')`
  5. Error: `toastStore.push('Profile update failed. Please try again.', 'error')`
- Save button shows spinner + "Saving..." while `isSavingProfile` is true.

---

## 4. Styling System

### Glassmorphism Classes (scoped CSS)

```css
.glass-shell       /* Page background: aurora mesh with fixed blobs */
.glass-segment     /* Panel: backdrop-filter blur(24px), rgba(255,255,255,0.86), 1px white border */
.input-glass       /* Input: semi-transparent bg, green focus ring */
.teaching-card     /* Expertise card: hover + selected states */
.rate-stepper      /* Stepper row */
.response-pill     /* Response time pill button */
.subject-pill      /* Subject tag with × */
.avatar-wrapper    /* Avatar container with camera hover overlay */
.course-year-modal /* Combined modal overlay + card */
```

### CSS Variables Used
```css
--sb-primary: #00895A
--sb-dark: #0A1916
--sb-bg: #F8F9FA
--sb-danger: (add as needed, e.g. #dc3545)
```

---

## 5. Testing & Validation

### Functional
- Profile data loads correctly on mount (all fields populated from API).
- Avatar upload: click → file picker → POST → preview updates immediately.
- Avatar upload errors (>5 MB, non-image): toast error, no preview change.
- Course & year modal: opens with current values, confirm updates fields, cancel discards.
- Teaching level card: selecting each card updates `profile.teaching_level`.
- Hourly rate: decrement stops at ₱50, increment works without limit.
- Response time: active pill updates on click.
- Subject add/remove/description saves correctly.
- Save Profile: all three API calls fire, toast shows on success/error.
- Discard Changes: reloads server state, all local edits reset.

### UI/UX
- Glass rendering looks correct on Chrome and Firefox.
- Responsive: single-column stacking on mobile (< 992px).
- Bio counter transitions color correctly near 500 chars.

---

## 6. Out of Scope
- Payout account setup (GCash/bank) — handled by Wallet page (`/tch-wallet`).
- Dark mode.
- Tutee profile changes.
- Public tutor detail page (`/tutor/:id`).
