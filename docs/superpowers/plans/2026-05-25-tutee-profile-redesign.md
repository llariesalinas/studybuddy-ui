# Tutee Profile Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the Tutee Profile with a glassmorphism Bento layout and context-aware academic selection.

**Architecture:** Split-view (7/12 - 5/12) grid. Backend adds an avatar upload endpoint and includes image URLs in profile data. Frontend handles dynamic education-level logic and visual enhancements.

**Tech Stack:** Vue 3 (Composition API), Django, Bootstrap Icons, Scoped CSS.

---

## File Structure Changes

### Backend
- `backend/studybuddy/views.py`: Add `upload_tutee_avatar` and update `get_tutee_profile`.
- `backend/studybuddy/urls.py`: Register avatar upload path.

### Frontend
- `src/views/TuteeProfile.vue`: Rewrite template and logic for Bento layout.
- `src/services/api/api.js`: (Verify) Ensure multipart support or simple post helper exists.

---

## Tasks

### Task 1: Backend — Avatar URL in Profile

**Files:**
- Modify: `backend/studybuddy/views.py`
- Test: `backend/studybuddy/tests.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/studybuddy/tests.py
def test_get_profile_includes_avatar_url(self):
    self.client.force_authenticate(user=self.tutee_user)
    response = self.client.get('/tutee/profile/')
    self.assertIn('profile_picture_url', response.data)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/studybuddy/tests.py -k test_get_profile_includes_avatar_url`

- [ ] **Step 3: Update `get_tutee_profile` view**

```python
# backend/studybuddy/views.py
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tutee_profile(request):
    profile = request.user.userprofile
    data = UserProfileSerializer(profile).data
    data['email'] = request.user.email
    data['profile_picture_url'] = request.build_absolute_uri(profile.profile_picture.url) if profile.profile_picture else None
    return Response(data)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/studybuddy/tests.py -k test_get_profile_includes_avatar_url`

- [ ] **Step 5: Commit**

```bash
git add backend/studybuddy/views.py
git commit -m "backend: include profile_picture_url in tutee profile data"
```

### Task 2: Backend — Avatar Upload Endpoint

**Files:**
- Modify: `backend/studybuddy/views.py`, `backend/studybuddy/urls.py`
- Test: `backend/studybuddy/tests.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/studybuddy/tests.py
def test_upload_avatar_success(self):
    from django.core.files.uploadedfile import SimpleUploadedFile
    self.client.force_authenticate(user=self.tutee_user)
    image = SimpleUploadedFile("avatar.jpg", b"file_content", content_type="image/jpeg")
    response = self.client.post('/tutee/profile/avatar/', {'avatar': image}, format='multipart')
    self.assertEqual(response.status_code, 200)
    self.assertIn('profile_picture_url', response.data)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/studybuddy/tests.py -k test_upload_avatar_success`

- [ ] **Step 3: Implement `upload_tutee_avatar` view**

```python
# backend/studybuddy/views.py
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_tutee_avatar(request):
    if 'avatar' not in request.FILES:
        return Response({'error': 'No avatar provided'}, status=400)

    avatar = request.FILES['avatar']
    if not avatar.content_type.startswith('image/'):
        return Response({'error': 'File must be an image'}, status=400)

    if avatar.size > 5 * 1024 * 1024:
        return Response({'error': 'Image must be under 5MB'}, status=400)

    profile = request.user.userprofile
    profile.profile_picture = avatar
    profile.save()

    return Response({
        "profile_picture_url": request.build_absolute_uri(profile.profile_picture.url)
    })
```

- [ ] **Step 4: Register URL**

```python
# backend/studybuddy/urls.py
path('tutee/profile/avatar/', views.upload_tutee_avatar),
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest backend/studybuddy/tests.py -k test_upload_avatar_success`

- [ ] **Step 6: Commit**

```bash
git add backend/studybuddy/views.py backend/studybuddy/urls.py
git commit -m "backend: add avatar upload endpoint"
```

### Task 3: Frontend — Scaffolding New Bento Template

**Files:**
- Modify: `src/views/TuteeProfile.vue`

- [ ] **Step 1: Update Template with Aurora Shell and Glass Modal**

Replace existing template with the Bento structure (7/12 - 5/12 split).

```html
<template>
  <div class="tutee-profile-shell">
    <div class="glass-modal">
      <!-- Header -->
      <div class="profile-header">
        <div class="avatar-wrapper" @click="triggerFileInput">
          <img v-if="profile.profile_picture_url" :src="profile.profile_picture_url" class="avatar-img">
          <div v-else class="avatar-placeholder">{{ initials }}</div>
          <div class="avatar-overlay"><i class="bi bi-camera"></i></div>
          <input type="file" ref="fileInput" hidden @change="handleAvatarUpload">
        </div>
        <div class="profile-identity">
          <h1>{{ profile.fname }} {{ profile.lname }}</h1>
          <p>Student / Tutee</p>
        </div>
        <div class="header-actions">
           <button class="btn btn-link text-muted sb-btn" @click="loadProfile">Discard</button>
           <button class="btn bg-sb-primary text-white sb-btn" @click="saveProfile">Save Changes</button>
        </div>
      </div>
      <!-- Body ... -->
    </div>
  </div>
</template>
```

- [ ] **Step 2: Commit**

```bash
git add src/views/TuteeProfile.vue
git commit -m "frontend: scaffold new tutee profile bento template"
```

### Task 4: Frontend — Academic Level Logic & Context Labels

**Files:**
- Modify: `src/views/TuteeProfile.vue`

- [ ] **Step 1: Implement Education Level Derivation**

```javascript
const educationLevel = ref('college') // default

function deriveEducationLevel(yearLevel) {
  if (!yearLevel) return 'college'
  if (yearLevel >= 1 && yearLevel <= 6) return 'elementary'
  if (yearLevel >= 7 && yearLevel <= 10) return 'jhs'
  if (yearLevel >= 11 && yearLevel <= 12) return 'shs'
  return 'college'
}

// In loadProfile:
// educationLevel.value = deriveEducationLevel(res.data.year_level)
```

- [ ] **Step 2: Implement Dynamic Year Options**

```javascript
const yearOptions = computed(() => {
  if (educationLevel.value === 'elementary') {
    return [1,2,3,4,5,6].map(v => ({ label: `Grade ${v}`, value: v }))
  }
  if (educationLevel.value === 'jhs') {
    return [7,8,9,10].map(v => ({ label: `Grade ${v}`, value: v }))
  }
  if (educationLevel.value === 'shs') {
    return [11,12].map(v => ({ label: `Grade ${v}`, value: v }))
  }
  return [13,14,15,16].map(v => ({ label: `${v-12}${v-12 == 1 ? 'st' : v-12 == 2 ? 'nd' : v-12 == 3 ? 'rd' : 'th'} Year`, value: v }))
})
```

- [ ] **Step 3: Commit**

```bash
git add src/views/TuteeProfile.vue
git commit -m "frontend: implement context-aware academic logic"
```

### Task 5: Frontend — Final Styling & Bio Counter

**Files:**
- Modify: `src/views/TuteeProfile.vue`

- [ ] **Step 1: Add Glassmorphism Scoped CSS**

Include `.tutee-profile-shell`, `.glass-modal`, `.input-glass`, and `.selection-card` styles as defined in the spec.

- [ ] **Step 2: Implement Bio Counter Color Warning**

```html
<textarea
  v-model="profile.bio"
  :class="['input-glass', { 'border-danger glow-danger': bioCount > 450 }]"
  maxlength="500"
></textarea>
```

```javascript
const bioCount = computed(() => profile.value.bio?.length || 0)
```

- [ ] **Step 3: Commit**

```bash
git add src/views/TuteeProfile.vue
git commit -m "frontend: apply glassmorphism styling and bio counter feedback"
```
