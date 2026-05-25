# Tutee Profile Redesign — Design Spec

**Date:** 2026-05-25  
**Route:** `/tutee-profile` → `src/views/TuteeProfile.vue`  
**Role:** Tutee only (`meta: { role: 'Tutee' }`)  
**Styling:** Scoped CSS glassmorphism — no Tailwind, no new icon systems, Bootstrap Icons only

---

## 1. Goal

Replace the plain Bootstrap card layout of the tutee profile page with the Aurora Bento glassmorphism aesthetic defined in `StudyBuddyDesign.md`. All existing data fields are preserved; education-level-aware year level selection is added as a frontend-only enhancement. Real avatar photo upload is wired to the existing `profile_picture` model field via a new backend endpoint.

---

## 2. Backend Changes

### 2a. Update `GET /tutee/profile/`

Add `profile_picture_url` to the response in `get_tutee_profile` in `backend/studybuddy/views.py`:

```python
"profile_picture_url": request.build_absolute_uri(profile.profile_picture.url) if profile.profile_picture else None,
```

No model changes. No migration.

### 2b. New endpoint — `POST /tutee/profile/avatar/`

View function `upload_tutee_avatar` in `backend/studybuddy/views.py`:

- Accepts `multipart/form-data` with a single file field named `avatar`
- Validates: file must be present, content-type must be `image/*`, max size 5 MB
- Saves to `profile.profile_picture`
- Returns `{ "profile_picture_url": "<absolute url>" }`
- Auth: `@permission_classes([IsAuthenticated])`

### 2c. URL registration in `backend/studybuddy/urls.py`

```python
path('tutee/profile/avatar/', views.upload_tutee_avatar),
```

---

## 3. Frontend — `src/views/TuteeProfile.vue`

### 3a. Template structure

```
<div class="tutee-profile-shell">          ← aurora gradient background, min-height 100%
  <div class="glass-modal">               ← main card
    <!-- Header -->
    <div class="profile-header">
      <div class="avatar-wrapper">        ← initials fallback OR <img> if profile_picture_url
        <input type="file" hidden ref="fileInput" @change="handleAvatarUpload">
        <button @click="fileInput.click()">Update Photo</button>
      </div>
      <div class="profile-identity">
        <h1>{{ fullName }}</h1>
        <p>Student / Tutee</p>
      </div>
      <div class="header-actions">
        <button @click="discardChanges">Discard</button>
        <button @click="saveProfile">Save Profile</button>
      </div>
    </div>

    <!-- Body: two-column grid -->
    <div class="profile-body">
      <!-- Left col (7/12) -->
      <section>Personal Info: fname, mname, lname, email (locked)</section>
      <section>Bio textarea with character counter (max 500)</section>

      <!-- Right col (5/12) -->
      <section>
        Education Level: 4 radio cards (Elementary / JHS / SHS / College)
        Year Level: radio card grid — options depend on educationLevel
        Course: radio cards (from API)
        Preferred Subjects: pill checkboxes (from API)
      </section>
    </div>

    <!-- Footer -->
    <div class="profile-footer">
      <p>Last updated: {{ lastUpdated }}</p>
      <button @click="saveProfile">Save Changes</button>
    </div>
  </div>
</div>
```

### 3b. Script — reactive state

```js
const profile = ref({
  fname: '', mname: '', lname: '', email: '',
  course: '', year_level: null, bio: '',
  subjects: [],          // array of subject_code strings
  profile_picture_url: null
})

const educationLevel = ref(null)   // 'elementary' | 'jhs' | 'shs' | 'college'
const courses = ref([])
const subjects = ref([])
const uploading = ref(false)
const fileInput = ref(null)
```

**Education level derivation on load:**
```js
function deriveEducationLevel(yearLevel) {
  if (yearLevel >= 1 && yearLevel <= 6)  return 'elementary'
  if (yearLevel >= 7 && yearLevel <= 10) return 'jhs'
  if (yearLevel >= 11 && yearLevel <= 12) return 'shs'
  if (yearLevel >= 13 && yearLevel <= 16) return 'college'
  return 'college'  // default
}
```

**Year level options per education level:**

| educationLevel | options (label → value) |
|---|---|
| `elementary` | Grade 1–6 → 1–6 |
| `jhs` | Grade 7–10 → 7–10 |
| `shs` | Grade 11–12 → 11–12 |
| `college` | 1st–4th Year → 13–16 |

Switching `educationLevel` resets `profile.year_level` to `null`.

**Computed:**
```js
const fullName = computed(() => `${profile.value.fname} ${profile.value.lname}`.trim())
const initials = computed(() => (profile.value.fname?.[0] ?? '') + (profile.value.lname?.[0] ?? ''))
const bioCharCount = computed(() => profile.value.bio?.length ?? 0)
```

**Save:**  
`PUT /tutee/profile/update/` with the same payload shape as today: `{ fname, mname, lname, course, year_level, bio, subjects }`. On success: `toastStore.push("Profile updated successfully")`.

**Avatar upload:**
```js
async function handleAvatarUpload(event) {
  const file = event.target.files[0]
  if (!file) return
  if (!file.type.startsWith('image/')) {
    toastStore.push('Please select an image file', 'error'); return
  }
  if (file.size > 5 * 1024 * 1024) {
    toastStore.push('Image must be under 5 MB', 'error'); return
  }
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('avatar', file)
    const res = await api.post('/tutee/profile/avatar/', fd)
    profile.value.profile_picture_url = res.data.profile_picture_url
    toastStore.push('Photo updated')
  } catch {
    toastStore.push('Photo upload failed', 'error')
  } finally {
    uploading.value = false
  }
}
```

**Discard:** re-call `loadProfile()` to reset all local state to server values.

### 3c. Scoped CSS — key rules

Aurora shell:
```css
.tutee-profile-shell {
  min-height: 100%;
  padding: 2rem;
  background:
    radial-gradient(circle at 0% 0%, rgba(16, 185, 129, 0.32), transparent 38%),
    radial-gradient(circle at 96% 6%, rgba(139, 92, 246, 0.2), transparent 36%),
    radial-gradient(circle at 88% 74%, rgba(14, 165, 233, 0.18), transparent 42%),
    linear-gradient(135deg, #f8fafc 0%, #f5fbf4 100%);
}
```

Glass modal card:
```css
.glass-modal {
  max-width: 900px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 24px;
  box-shadow: 0 24px 80px rgba(15, 23, 42, 0.18);
  overflow: hidden;
}
```

Glass input:
```css
.input-glass {
  background: rgba(255, 255, 255, 0.4);
  border: 1px solid rgba(15, 23, 42, 0.1);
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.input-glass:focus {
  outline: none;
  border-color: var(--sb-primary);
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 0 0 4px rgba(0, 137, 90, 0.1);
}
```

Selection card (radio/checkbox):
```css
.selection-card input:checked + .card-inner {
  background-color: var(--sb-primary);
  color: white;
  border-color: var(--sb-primary);
}
.card-inner {
  padding: 0.75rem 1rem;
  border: 1px solid rgba(15, 23, 42, 0.12);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
```

Hover lift (Save/Discard buttons):
```css
.hover-lift {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.hover-lift:hover { transform: translateY(-2px); }
```

All interactive elements use `.sb-btn` per the design system haptics rule.

---

## 4. Preserved Behaviors

- `loadProfile()` → `GET /tutee/profile/`
- `loadCourses()` → `GET /api/courses/`
- `loadSubjects()` → `GET /api/subjects/`
- `saveProfile()` → `PUT /tutee/profile/update/` — payload unchanged
- `mname` field kept in the form (left column, Personal Info section)
- Toast notifications via `toastStore` for all outcomes
- Email field is always `disabled` with lock icon + helper text

---

## 5. Out of Scope

- Session rating reminder banner (dropped per decision)
- Middle name removal (kept)
- Tutor profile page (`TutorProfile.vue`) — separate task
- Any changes to the shared sidebar or `App.vue` shell
- Dark mode support
