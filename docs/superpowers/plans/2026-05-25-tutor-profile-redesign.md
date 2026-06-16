# Tutor Profile Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign `/tutor-profile` from plain Bootstrap to Aurora Bento glassmorphism, add avatar upload wired to a new `/tutor/profile/avatar/` endpoint, and expose `profile_picture_url` from the tutor profile API.

**Architecture:** Two backend tasks (serializer update + new upload endpoint with tests) followed by one frontend task (complete `TutorProfile.vue` rewrite with scoped CSS glassmorphism). The frontend calls the same save endpoints as before plus the new avatar endpoint.

**Tech Stack:** Vue 3 Composition API, Pinia, Bootstrap Icons, scoped CSS glassmorphism, Django REST Framework, SimpleUploadedFile for backend tests.

---

## File Map

| File | Change |
|------|--------|
| `backend/studybuddy/serializers.py` | Add `profile_picture_url` SerializerMethodField to `TutorProfileSerializer` |
| `backend/studybuddy/views.py` | Fix request context in `get_tutor_profile`; add `upload_tutor_avatar` |
| `backend/studybuddy/urls.py` | Register `path('tutor/profile/avatar/', views.upload_tutor_avatar)` |
| `backend/studybuddy/tests.py` | Add `TutorProfileTests` class |
| `src/views/TutorProfile.vue` | Complete rewrite — aurora bento layout, glassmorphism CSS |

---

## Task 1: Backend — Add `profile_picture_url` to tutor profile response

**Files:**
- Modify: `backend/studybuddy/serializers.py` (around line 168 — `TutorProfileSerializer`)
- Modify: `backend/studybuddy/views.py` (around line 1116 — `get_tutor_profile`)
- Modify: `backend/studybuddy/tests.py` (append new test class at end of file)

- [ ] **Step 1: Write the failing test**

Open `backend/studybuddy/tests.py`. Scroll to the end of the file, after the `TuteeProfileTests` class. Add:

```python
class TutorProfileTests(APITestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        self.tutor_user = User.objects.create_user(
            username="tutor-test",
            email="tutor@example.com",
            password="password",
        )
        self.tutor_profile = UserProfile.objects.create(
            user=self.tutor_user,
            fname="Tutor",
            mname="",
            lname="Test",
            role="Tutor",
            year_level=14,
        )
        self.tutor = Tutor.objects.create(
            profile=self.tutor_profile,
            hourly_rate=200,
            teaching_level="College",
            can_online=True,
            can_f2f=False,
            response_time="within_1_hour",
        )

    def test_get_profile_includes_profile_picture_url(self):
        self.client.force_authenticate(user=self.tutor_user)
        response = self.client.get('/api/tutor/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('profile_picture_url', response.data)
```

- [ ] **Step 2: Run the test — confirm it fails**

```bash
cd backend && python manage.py test studybuddy.tests.TutorProfileTests.test_get_profile_includes_profile_picture_url --verbosity=2
```

Expected: `FAIL` — `'profile_picture_url' not found in response.data`.

- [ ] **Step 3: Add `profile_picture_url` to `TutorProfileSerializer`**

Open `backend/studybuddy/serializers.py`. Find `class TutorProfileSerializer` (around line 168). Add the new field and method, and add it to `Meta.fields`:

```python
class TutorProfileSerializer(serializers.ModelSerializer):

    fname = serializers.CharField(source='profile.fname', read_only=True)
    lname = serializers.CharField(source='profile.lname', read_only=True)
    email = serializers.CharField(source='profile.user.email', read_only=True)
    course = serializers.SerializerMethodField()
    year_level = serializers.IntegerField(source='profile.year_level', read_only=True, allow_null=True)
    bio = serializers.CharField(source='profile.bio', read_only=True, allow_null=True)
    response_time_label = serializers.CharField(read_only=True)
    pinned_review_id = serializers.IntegerField(read_only=True)
    pinned_review = PinnedReviewSerializer(read_only=True)
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = Tutor
        fields = [
            'fname',
            'lname',
            'email',
            'course',
            'year_level',
            'bio',
            'hourly_rate',
            'teaching_level',
            'can_online',
            'can_f2f',
            'rating_average',
            'total_sessions',
            'response_time',
            'response_time_label',
            'pinned_review_id',
            'pinned_review',
            'profile_picture_url',
        ]

    def get_course(self, obj):
        return obj.profile.course.course_code if obj.profile.course else None

    def get_profile_picture_url(self, obj):
        request = self.context.get('request')
        if obj.profile.profile_picture and request:
            return request.build_absolute_uri(obj.profile.profile_picture.url)
        return None
```

- [ ] **Step 4: Pass `request` context in `get_tutor_profile`**

Open `backend/studybuddy/views.py`. Find `def get_tutor_profile` (around line 1101). Change the serializer call to pass context:

```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tutor_profile(request):

    profile = request.user.userprofile

    try:
        tutor = Tutor.objects.select_related(
            'profile__user',
            'profile__course',
            'pinned_review__student'
        ).get(profile=profile)
    except Tutor.DoesNotExist:
        return Response({"error": "Tutor not found"}, status=404)

    serializer = TutorProfileSerializer(tutor, context={'request': request})
    return Response(serializer.data)
```

- [ ] **Step 5: Run the test — confirm it passes**

```bash
cd backend && python manage.py test studybuddy.tests.TutorProfileTests.test_get_profile_includes_profile_picture_url --verbosity=2
```

Expected: `OK`.

- [ ] **Step 6: Commit**

```bash
git add backend/studybuddy/serializers.py backend/studybuddy/views.py backend/studybuddy/tests.py
git commit -m "feat: add profile_picture_url to TutorProfileSerializer and pass request context"
```

---

## Task 2: Backend — Add `upload_tutor_avatar` endpoint

**Files:**
- Modify: `backend/studybuddy/views.py` (add after `upload_tutee_avatar`, around line 2558)
- Modify: `backend/studybuddy/urls.py`
- Modify: `backend/studybuddy/tests.py` (add to `TutorProfileTests`)

- [ ] **Step 1: Write the failing tests**

Open `backend/studybuddy/tests.py`. Inside `TutorProfileTests`, add two new test methods after `test_get_profile_includes_profile_picture_url`:

```python
    def test_upload_avatar_success(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.force_authenticate(user=self.tutor_user)
        image = SimpleUploadedFile("avatar.jpg", b"fake_image_content", content_type="image/jpeg")
        response = self.client.post('/api/tutor/profile/avatar/', {'avatar': image}, format='multipart')
        self.assertEqual(response.status_code, 200)
        self.assertIn('profile_picture_url', response.data)

    def test_upload_avatar_rejects_non_image(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.force_authenticate(user=self.tutor_user)
        bad_file = SimpleUploadedFile("doc.pdf", b"not_an_image", content_type="application/pdf")
        response = self.client.post('/api/tutor/profile/avatar/', {'avatar': bad_file}, format='multipart')
        self.assertEqual(response.status_code, 400)

    def test_upload_avatar_rejects_missing_file(self):
        self.client.force_authenticate(user=self.tutor_user)
        response = self.client.post('/api/tutor/profile/avatar/', {}, format='multipart')
        self.assertEqual(response.status_code, 400)
```

- [ ] **Step 2: Run the new tests — confirm they fail**

```bash
cd backend && python manage.py test studybuddy.tests.TutorProfileTests --verbosity=2
```

Expected: `test_get_profile_includes_profile_picture_url` PASS, three new tests FAIL with 404.

- [ ] **Step 3: Add `upload_tutor_avatar` to `views.py`**

Open `backend/studybuddy/views.py`. Find `upload_tutee_avatar` (around line 2538). Add the tutor version directly after it (after line 2557):

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_tutor_avatar(request):
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
        'profile_picture_url': request.build_absolute_uri(profile.profile_picture.url)
    })
```

- [ ] **Step 4: Register the URL**

Open `backend/studybuddy/urls.py`. Find the block with `tutee/profile/avatar/` (around line 56). Add the tutor route directly after it:

```python
path('tutee/profile/', views.get_tutee_profile),
path('tutee/profile/avatar/', views.upload_tutee_avatar),
path('tutee/profile/update/', views.update_tutee_profile),
path('tutor/profile/avatar/', views.upload_tutor_avatar),   # ← add this line
path('tutor/profile/', views.get_tutor_profile),
```

- [ ] **Step 5: Run all tests — confirm they pass**

```bash
cd backend && python manage.py test studybuddy.tests.TutorProfileTests --verbosity=2
```

Expected: all 4 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/studybuddy/views.py backend/studybuddy/urls.py backend/studybuddy/tests.py
git commit -m "feat: add upload_tutor_avatar endpoint POST /tutor/profile/avatar/"
```

---

## Task 3: Frontend — Complete `TutorProfile.vue` rewrite

**Files:**
- Modify (full rewrite): `src/views/TutorProfile.vue`

> No frontend test suite exists in this project (confirmed in CLAUDE.md). Verify visually after writing.

- [ ] **Step 1: Replace the full `<template>` block**

Replace everything inside `<template>` with:

```html
<template>
  <div class="tutor-profile-shell">

    <!-- Aurora background blobs -->
    <div class="aurora-blob aurora-blob-1"></div>
    <div class="aurora-blob aurora-blob-2"></div>
    <div class="aurora-blob aurora-blob-3"></div>

    <div class="profile-content">

      <!-- ── HEADER SEGMENT ─────────────────────────────── -->
      <header class="glass-segment profile-header-segment">
        <div class="header-left">
          <div class="avatar-wrapper" @click="triggerAvatarUpload" role="button" aria-label="Upload profile photo">
            <img v-if="avatarUrl" :src="avatarUrl" class="avatar-img" alt="Profile photo">
            <div v-else class="initials-avatar">{{ initials }}</div>
            <div class="avatar-camera-overlay">
              <i class="bi bi-camera-fill"></i>
            </div>
          </div>
          <input ref="fileInputRef" type="file" accept="image/*" class="d-none" @change="handleAvatarUpload">

          <div class="header-info">
            <h2 class="profile-name">{{ profile.fullName || 'Your Name' }}</h2>
            <div class="header-badges">
              <span class="role-badge">Tutor</span>
              <span class="verified-badge"><i class="bi bi-patch-check-fill"></i> Verified</span>
            </div>
          </div>
        </div>

        <div class="header-actions">
          <button type="button" class="btn-ghost sb-btn">View Public Profile</button>
          <button type="button" class="btn-primary-action sb-btn">Manage Pending Sessions</button>
        </div>
      </header>

      <!-- ── MAIN GRID ──────────────────────────────────── -->
      <div class="profile-grid">

        <!-- LEFT COLUMN -->
        <div class="profile-col-left">

          <!-- Identity Segment -->
          <section class="glass-segment">
            <div class="segment-header">
              <div class="segment-icon"><i class="bi bi-person-fill"></i></div>
              <h3 class="segment-title">Identity Details</h3>
            </div>

            <div class="field-group">
              <div class="field-row-2">
                <div class="field">
                  <label class="field-label">Full Name</label>
                  <input type="text" v-model="profile.fullName" class="input-glass" placeholder="First Last">
                </div>
                <div class="field">
                  <label class="field-label">Email</label>
                  <input type="email" :value="profile.email" class="input-glass input-disabled" disabled>
                </div>
              </div>

              <div class="field">
                <label class="field-label">Course &amp; Year Level</label>
                <div class="course-year-display">
                  <span class="course-chip" :class="{ 'chip-unset': !profile.course }">
                    {{ currentCourseLabel }}
                  </span>
                  <span class="year-chip" :class="{ 'chip-unset': !profile.year_level }">
                    {{ currentYearLabel }}
                  </span>
                  <button type="button" class="change-btn sb-btn" @click="openCourseYearModal">
                    Change <i class="bi bi-arrow-right-short"></i>
                  </button>
                </div>
              </div>
            </div>
          </section>

          <!-- Expertise Segment -->
          <section class="glass-segment">
            <div class="segment-header">
              <div class="segment-icon"><i class="bi bi-award-fill"></i></div>
              <h3 class="segment-title">Expertise Level</h3>
            </div>

            <div class="teaching-level-grid">
              <button
                v-for="opt in teachingLevelOptions"
                :key="opt.value"
                type="button"
                class="teaching-card sb-btn"
                :class="{ 'teaching-card-active': profile.teaching_level === opt.value }"
                @click="profile.teaching_level = opt.value"
              >
                <i :class="`bi ${opt.icon} teaching-card-icon`"></i>
                <span class="teaching-card-label">{{ opt.label }}</span>
              </button>
            </div>
          </section>

        </div>

        <!-- RIGHT COLUMN -->
        <div class="profile-col-right">

          <!-- Financials Segment -->
          <section class="glass-segment">
            <div class="segment-header">
              <div class="segment-icon"><i class="bi bi-cash-coin"></i></div>
              <h3 class="segment-title">Financials</h3>
            </div>

            <div class="field-group">
              <div class="field">
                <label class="field-label">Hourly Rate (PHP)</label>
                <div class="rate-stepper">
                  <button
                    type="button"
                    class="stepper-btn sb-btn"
                    :disabled="Number(profile.hourly_rate) <= 50"
                    @click="decrementRate"
                  ><i class="bi bi-dash-lg"></i></button>
                  <span class="rate-display">₱{{ Number(profile.hourly_rate).toFixed(2) }}</span>
                  <button type="button" class="stepper-btn sb-btn" @click="incrementRate">
                    <i class="bi bi-plus-lg"></i>
                  </button>
                </div>
              </div>

              <div class="field">
                <label class="field-label">Response Goal</label>
                <div class="response-pills">
                  <button
                    v-for="opt in responseTimeOptions"
                    :key="opt.value"
                    type="button"
                    class="response-pill sb-btn"
                    :class="{ 'response-pill-active': profile.response_time === opt.value }"
                    @click="profile.response_time = opt.value"
                  >{{ opt.label }}</button>
                </div>
              </div>
            </div>
          </section>

          <!-- Specializations Segment -->
          <section class="glass-segment">
            <div class="segment-header">
              <div class="segment-icon"><i class="bi bi-stars"></i></div>
              <h3 class="segment-title">Specializations</h3>
              <span class="subject-counter">{{ profile.subjects.length }}/8</span>
            </div>

            <div class="field-group">
              <div class="subject-pill-row">
                <div
                  v-for="subject in profile.subjects"
                  :key="subject.subject_code"
                  class="subject-pill"
                >
                  {{ subject.subject_name }}
                  <button
                    type="button"
                    class="subject-pill-remove sb-btn"
                    @click="removeSubject(subject.subject_code)"
                  ><i class="bi bi-x"></i></button>
                </div>
                <button
                  type="button"
                  class="subject-add-btn sb-btn"
                  @click="openSubjectModal"
                ><i class="bi bi-plus-lg"></i> Add</button>
              </div>

              <div class="field">
                <label class="field-label">Bio</label>
                <textarea
                  v-model="profile.bio"
                  class="input-glass bio-textarea"
                  :class="{ 'bio-near-limit': bioCharCount > 450, 'bio-at-limit': bioCharCount >= 500 }"
                  placeholder="Share your teaching philosophy..."
                  maxlength="500"
                  rows="4"
                ></textarea>
                <span class="bio-counter" :class="{ 'bio-counter-warn': bioCharCount > 450 }">
                  {{ bioCharCount }}/500
                </span>
              </div>

              <div class="session-mode-group">
                <label class="field-label">Session Mode</label>
                <label class="mode-check">
                  <input type="checkbox" v-model="profile.can_online" class="mode-checkbox">
                  <span>Online Tutoring</span>
                </label>
                <label class="mode-check">
                  <input type="checkbox" v-model="profile.can_f2f" class="mode-checkbox">
                  <span>Face-to-Face</span>
                </label>
              </div>
            </div>

            <!-- Subject accordion list -->
            <div v-if="profile.subjects.length" class="subject-accordion-list">
              <article
                v-for="subject in profile.subjects"
                :key="`${subject.subject_code}-accordion`"
                class="subject-accordion-card"
                :class="{ 'subject-accordion-card-open': openSubjectCode === subject.subject_code }"
              >
                <button
                  type="button"
                  class="subject-accordion-header sb-btn"
                  @click="toggleSubjectAccordion(subject.subject_code)"
                >
                  <span
                    class="subject-accordion-icon"
                    :class="{ 'subject-accordion-icon-open': openSubjectCode === subject.subject_code }"
                  ><i class="bi bi-journal-bookmark-fill"></i></span>
                  <span
                    class="subject-accordion-title"
                    :class="{ 'subject-accordion-title-open': openSubjectCode === subject.subject_code }"
                  >{{ subject.subject_name }}</span>
                  <i
                    class="bi ms-auto subject-accordion-chevron"
                    :class="openSubjectCode === subject.subject_code ? 'bi-chevron-up' : 'bi-chevron-down'"
                  ></i>
                </button>

                <Transition
                  @before-enter="el => { el.style.maxHeight = '0'; el.style.opacity = '0' }"
                  @enter="el => { el.offsetHeight; el.style.maxHeight = el.scrollHeight + 'px'; el.style.opacity = '1' }"
                  @after-enter="el => { el.style.maxHeight = ''; el.style.opacity = '' }"
                  @before-leave="el => { el.style.maxHeight = el.scrollHeight + 'px'; el.style.opacity = '1' }"
                  @leave="el => { el.offsetHeight; el.style.maxHeight = '0'; el.style.opacity = '0' }"
                  @after-leave="el => { el.style.maxHeight = ''; el.style.opacity = '' }"
                >
                  <div v-if="openSubjectCode === subject.subject_code" class="subject-accordion-body">
                    <label class="subject-accordion-label">Subject Syllabus &amp; Approach</label>
                    <textarea
                      v-model="subject.description"
                      rows="4"
                      class="subject-description-input"
                      placeholder="Describe your methodology for this specific subject..."
                    ></textarea>
                  </div>
                </Transition>
              </article>
            </div>
          </section>

        </div>
      </div>

      <!-- ── BOTTOM ACTIONS ──────────────────────────────── -->
      <div class="glass-segment profile-actions">
        <button type="button" class="btn-discard sb-btn" @click="discardChanges">
          Discard Changes
        </button>
        <button
          type="button"
          class="btn-save sb-btn"
          :disabled="isSavingProfile"
          @click="saveProfile"
        >
          <span v-if="isSavingProfile" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
          {{ isSavingProfile ? 'Saving...' : 'Save Profile' }}
        </button>
      </div>

    </div>

    <!-- ── COURSE & YEAR MODAL ────────────────────────────── -->
    <div
      v-if="isCourseYearModalOpen"
      class="modal-backdrop"
      @click.self="cancelCourseYear"
    >
      <div class="glass-modal course-year-modal">
        <div class="modal-header-row">
          <h4 class="modal-title">Course &amp; Year Level</h4>
          <button type="button" class="btn-close" @click="cancelCourseYear"></button>
        </div>

        <div class="modal-section">
          <p class="modal-section-label">Course</p>
          <div class="course-grid">
            <button
              v-for="c in courses"
              :key="c.course_code"
              type="button"
              class="course-card sb-btn"
              :class="{ 'course-card-active': draftCourse === c.course_code }"
              @click="draftCourse = c.course_code"
            >
              <span class="course-card-code">{{ c.course_code }}</span>
              <span class="course-card-name">{{ c.course_name }}</span>
            </button>
          </div>
        </div>

        <div class="modal-section">
          <p class="modal-section-label">Year Level</p>
          <div class="year-grid">
            <button
              v-for="y in yearLevels"
              :key="y.value"
              type="button"
              class="year-btn sb-btn"
              :class="{ 'year-btn-active': draftYearLevel === y.value }"
              @click="draftYearLevel = y.value"
            >{{ y.label }}</button>
          </div>
        </div>

        <div class="modal-footer-row">
          <button type="button" class="btn-ghost-sm sb-btn" @click="cancelCourseYear">Cancel</button>
          <button type="button" class="btn-confirm sb-btn" @click="confirmCourseYear">
            Confirm Selection
          </button>
        </div>
      </div>
    </div>

    <!-- ── SUBJECT PICKER MODAL ───────────────────────────── -->
    <div
      v-if="isSubjectModalOpen"
      class="modal-backdrop"
      @click.self="closeSubjectModal"
    >
      <div class="glass-modal subject-modal">
        <div class="d-flex justify-content-between align-items-start gap-3 mb-3">
          <div>
            <h5 class="fw-bold mb-1">Pick Subjects</h5>
            <p class="text-muted small mb-0">Search and filter by category before confirming.</p>
          </div>
          <button type="button" class="btn-close" @click="closeSubjectModal"></button>
        </div>

        <div class="mb-3">
          <input
            v-model="subjectSearch"
            type="text"
            class="input-glass w-100"
            placeholder="Search subjects"
          >
        </div>

        <div class="category-pills mb-3">
          <button
            v-for="category in availableCategories"
            :key="category"
            type="button"
            class="category-pill sb-btn"
            :class="{ active: activeCategory === category }"
            @click="activeCategory = category"
          >{{ category }}</button>
        </div>

        <div class="subject-modal-list">
          <div v-if="isLoadingSubjects" class="text-center text-muted py-4">Loading subjects...</div>
          <div v-else-if="subjectsLoadError" class="text-center text-danger py-4">{{ subjectsLoadError }}</div>
          <template v-else>
            <button
              v-for="subject in filteredSubjects"
              :key="subject.subject_code"
              type="button"
              class="subject-option sb-btn"
              :class="{ selected: isDraftSelected(subject.subject_code) }"
              @click="toggleDraftSubject(subject.subject_code)"
            >
              <div class="subject-option-copy">
                <span class="subject-option-name">{{ subject.subject_name }}</span>
                <span class="subject-option-meta">{{ normalizeCategory(subject.category) }}</span>
              </div>
              <div class="subject-option-check">
                <input
                  type="checkbox"
                  class="form-check-input"
                  :checked="isDraftSelected(subject.subject_code)"
                  tabindex="-1"
                  @change.prevent
                >
              </div>
            </button>
            <div v-if="!filteredSubjects.length" class="text-center text-muted py-4">
              No subjects match your filters.
            </div>
          </template>
        </div>

        <div class="subject-modal-footer mt-3">
          <span class="text-muted small">{{ selectedDraftCountLabel }}</span>
          <div class="d-flex gap-2">
            <button type="button" class="btn btn-outline-secondary sb-btn" @click="closeSubjectModal">
              Cancel
            </button>
            <button type="button" class="btn bg-sb-primary text-white sb-btn" @click="confirmSubjectSelection">
              Confirm
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>
```

- [ ] **Step 2: Replace the full `<script setup>` block**

Replace everything between `<script setup>` and `</script>` with:

```js
import { computed, onMounted, ref } from 'vue'
import api from '@/services/api/api'
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()

// ── Profile state ────────────────────────────────────────────────
const profile = ref({
  fullName: '',
  email: '',
  course: '',
  year_level: null,
  subjects: [],
  bio: '',
  hourly_rate: 50,
  teaching_level: '',
  can_online: true,
  can_f2f: false,
  response_time: ''
})

const avatarUrl = ref(null)
const fileInputRef = ref(null)
const isSavingProfile = ref(false)

// ── Lookup data ──────────────────────────────────────────────────
const courses = ref([])

const yearLevels = [
  { label: 'Grade 1', value: 1 },
  { label: 'Grade 2', value: 2 },
  { label: 'Grade 3', value: 3 },
  { label: 'Grade 4', value: 4 },
  { label: 'Grade 5', value: 5 },
  { label: 'Grade 6', value: 6 },
  { label: 'Grade 7', value: 7 },
  { label: 'Grade 8', value: 8 },
  { label: 'Grade 9', value: 9 },
  { label: 'Grade 10', value: 10 },
  { label: 'Grade 11', value: 11 },
  { label: 'Grade 12', value: 12 },
  { label: '1st Year College', value: 13 },
  { label: '2nd Year College', value: 14 },
  { label: '3rd Year College', value: 15 },
  { label: '4th Year College', value: 16 }
]

const responseTimeOptions = [
  { value: 'within_1_hour', label: '1 Hr' },
  { value: 'within_few_hours', label: 'Few Hrs' },
  { value: 'within_a_day', label: 'Next Day' }
]

const teachingLevelOptions = [
  { value: 'Elementary', icon: 'bi-backpack2', label: 'Elementary' },
  { value: 'High School', icon: 'bi-mortarboard', label: 'High School' },
  { value: 'College', icon: 'bi-book', label: 'College' }
]

// ── Course/Year modal ────────────────────────────────────────────
const isCourseYearModalOpen = ref(false)
const draftCourse = ref('')
const draftYearLevel = ref(null)

function openCourseYearModal() {
  draftCourse.value = profile.value.course
  draftYearLevel.value = profile.value.year_level
  isCourseYearModalOpen.value = true
}

function confirmCourseYear() {
  profile.value.course = draftCourse.value
  profile.value.year_level = draftYearLevel.value
  isCourseYearModalOpen.value = false
}

function cancelCourseYear() {
  isCourseYearModalOpen.value = false
}

// ── Subject modal ────────────────────────────────────────────────
const allSubjects = ref([])
const initialSubjectCodes = ref([])
const initialSubjectDescriptions = ref(new Map())
const isSubjectModalOpen = ref(false)
const subjectSearch = ref('')
const activeCategory = ref('All')
const draftSubjectCodes = ref([])
const openSubjectCode = ref(null)
const isLoadingSubjects = ref(false)
const subjectsLoadError = ref('')

// ── Computed ─────────────────────────────────────────────────────
const initials = computed(() => {
  const parts = profile.value.fullName.trim().split(/\s+/).filter(Boolean)
  return parts.map(p => p[0]).join('').toUpperCase().slice(0, 2) || '?'
})

const bioCharCount = computed(() => profile.value.bio?.length || 0)

const currentCourseLabel = computed(() => {
  const match = courses.value.find(c => c.course_code === profile.value.course)
  return match ? `${match.course_code} – ${match.course_name}` : 'Not set'
})

const currentYearLabel = computed(() => {
  const match = yearLevels.find(y => y.value === profile.value.year_level)
  return match ? match.label : 'Not set'
})

const availableCategories = computed(() => {
  const cats = allSubjects.value
    .map(s => normalizeCategory(s.category))
    .filter(Boolean)
  return ['All', ...new Set(cats)]
})

const filteredSubjects = computed(() => {
  const query = subjectSearch.value.trim().toLowerCase()
  return allSubjects.value.filter(s => {
    const cat = normalizeCategory(s.category)
    const matchesCat = activeCategory.value === 'All' || cat === activeCategory.value
    const matchesSearch =
      !query ||
      s.subject_name.toLowerCase().includes(query) ||
      s.subject_code.toLowerCase().includes(query)
    return matchesCat && matchesSearch
  })
})

const selectedDraftCountLabel = computed(() => {
  const n = draftSubjectCodes.value.length
  return `${n} subject${n === 1 ? '' : 's'} selected`
})

// ── API loaders ──────────────────────────────────────────────────
const loadProfile = async () => {
  try {
    const res = await api.get('/tutor/profile/')
    const d = res.data
    profile.value.fullName = `${d.fname} ${d.lname}`.trim()
    profile.value.email = d.email
    profile.value.course = d.course || ''
    profile.value.year_level = d.year_level ?? null
    profile.value.bio = d.bio || ''
    profile.value.hourly_rate = Number(d.hourly_rate) || 50
    profile.value.teaching_level = d.teaching_level || ''
    profile.value.can_online = d.can_online
    profile.value.can_f2f = d.can_f2f
    profile.value.response_time = d.response_time || ''
    avatarUrl.value = d.profile_picture_url || null

    const subRes = await api.get('/tutor/subjects/')
    profile.value.subjects = subRes.data.map(s => ({ ...s, description: s.description || '' }))
    initialSubjectCodes.value = profile.value.subjects.map(s => s.subject_code)
    initialSubjectDescriptions.value = new Map(
      profile.value.subjects.map(s => [s.subject_code, s.description || ''])
    )
  } catch (err) {
    console.error('Failed to load tutor profile:', err)
    toastStore.push('Failed to load profile', 'error')
  }
}

const loadCourses = async () => {
  try {
    const res = await api.get('/courses/')
    courses.value = res.data
  } catch (err) {
    console.error('Failed to load courses:', err)
  }
}

const loadSubjects = async () => {
  if (isLoadingSubjects.value) return
  isLoadingSubjects.value = true
  subjectsLoadError.value = ''
  try {
    const res = await api.get('/subjects/')
    allSubjects.value = res.data
  } catch {
    subjectsLoadError.value = 'Could not load subjects right now.'
  } finally {
    isLoadingSubjects.value = false
  }
}

// ── Avatar upload ─────────────────────────────────────────────────
function triggerAvatarUpload() {
  fileInputRef.value.click()
}

async function handleAvatarUpload(event) {
  const file = event.target.files[0]
  if (!file) return

  const formData = new FormData()
  formData.append('avatar', file)

  try {
    const res = await api.post('/tutor/profile/avatar/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    avatarUrl.value = res.data.profile_picture_url
    toastStore.push('Avatar updated')
  } catch {
    toastStore.push('Failed to upload avatar', 'error')
  }

  event.target.value = ''
}

// ── Rate stepper ─────────────────────────────────────────────────
function incrementRate() {
  profile.value.hourly_rate = Number(profile.value.hourly_rate) + 10
}

function decrementRate() {
  const current = Number(profile.value.hourly_rate)
  if (current > 50) profile.value.hourly_rate = current - 10
}

// ── Subject modal helpers ────────────────────────────────────────
function normalizeCategory(category) {
  return category?.trim() || 'Uncategorized'
}

function getSubjectByCode(code) {
  return (
    allSubjects.value.find(s => s.subject_code === code) ||
    profile.value.subjects.find(s => s.subject_code === code)
  )
}

function syncProfileSubjectsFromCodes(codes) {
  const existing = new Map(
    profile.value.subjects.map(s => [s.subject_code, { ...s, description: s.description || '' }])
  )
  profile.value.subjects = codes
    .map(code => {
      const base = getSubjectByCode(code)
      if (!base) return null
      return { ...base, description: existing.get(code)?.description || '' }
    })
    .filter(Boolean)
    .sort((a, b) => a.subject_name.localeCompare(b.subject_name))
}

async function openSubjectModal() {
  if (!allSubjects.value.length) await loadSubjects()
  draftSubjectCodes.value = profile.value.subjects.map(s => s.subject_code)
  subjectSearch.value = ''
  activeCategory.value = 'All'
  isSubjectModalOpen.value = true
}

function closeSubjectModal() {
  isSubjectModalOpen.value = false
  subjectSearch.value = ''
  activeCategory.value = 'All'
  draftSubjectCodes.value = []
}

function isDraftSelected(code) {
  return draftSubjectCodes.value.includes(code)
}

function toggleDraftSubject(code) {
  if (isDraftSelected(code)) {
    draftSubjectCodes.value = draftSubjectCodes.value.filter(c => c !== code)
    return
  }
  if (draftSubjectCodes.value.length >= 8) return
  draftSubjectCodes.value = [...draftSubjectCodes.value, code]
}

function confirmSubjectSelection() {
  syncProfileSubjectsFromCodes(draftSubjectCodes.value)
  closeSubjectModal()
}

function removeSubject(code) {
  profile.value.subjects = profile.value.subjects.filter(s => s.subject_code !== code)
  if (openSubjectCode.value === code) openSubjectCode.value = null
}

function toggleSubjectAccordion(code) {
  openSubjectCode.value = openSubjectCode.value === code ? null : code
}

// ── Subject sync (diff-based API calls) ─────────────────────────
async function syncSubjects() {
  const current = profile.value.subjects.map(s => ({ ...s, description: s.description || '' }))
  const currentCodes = current.map(s => s.subject_code)
  const added = currentCodes.filter(c => !initialSubjectCodes.value.includes(c))
  const removed = initialSubjectCodes.value.filter(c => !currentCodes.includes(c))
  const changed = current.filter(s => {
    if (added.includes(s.subject_code)) return false
    return (initialSubjectDescriptions.value.get(s.subject_code) || '') !== (s.description || '')
  })

  await Promise.all([
    ...added.map(code => {
      const s = current.find(x => x.subject_code === code)
      return api.post('/tutor/subjects/add/', { subject_code: code, description: s?.description || '' })
    }),
    ...changed.map(s =>
      api.patch(`/tutor/subjects/update/${s.subject_code}/`, { description: s.description || '' })
    ),
    ...removed.map(code => api.delete(`/tutor/subjects/remove/${code}/`))
  ])

  initialSubjectCodes.value = [...currentCodes]
  initialSubjectDescriptions.value = new Map(
    current.map(s => [s.subject_code, s.description || ''])
  )
}

// ── Save / Discard ───────────────────────────────────────────────
const saveProfile = async () => {
  if (isSavingProfile.value) return

  const names = profile.value.fullName.trim().split(/\s+/)

  const tuteePayload = {
    fname: names[0] || '',
    lname: names.slice(1).join(' ') || '',
    course: profile.value.course,
    year_level: profile.value.year_level,
    bio: profile.value.bio
  }

  const tutorPayload = {
    hourly_rate: profile.value.hourly_rate,
    teaching_level: profile.value.teaching_level,
    can_online: profile.value.can_online,
    can_f2f: profile.value.can_f2f,
    response_time: profile.value.response_time || null
  }

  try {
    isSavingProfile.value = true
    await api.put('/tutee/profile/update/', tuteePayload)
    await api.put('/tutor/update/', tutorPayload)
    await syncSubjects()
    toastStore.push('Profile Updated')
  } catch (err) {
    console.error('Profile update failed:', err)
    toastStore.push('Profile update failed. Please try again.', 'error')
  } finally {
    isSavingProfile.value = false
  }
}

const discardChanges = async () => {
  await loadProfile()
}

onMounted(() => {
  loadProfile()
  loadCourses()
  loadSubjects()
})
```

- [ ] **Step 3: Replace the full `<style scoped>` block**

Replace everything between `<style scoped>` and `</style>` with:

```css
/* ── Shell & Aurora ───────────────────────────────── */
.tutor-profile-shell {
  position: relative;
  min-height: 100vh;
  padding: 2rem;
  background:
    radial-gradient(circle at 0% 0%, rgba(16, 185, 129, 0.32), transparent 38%),
    radial-gradient(circle at 96% 6%, rgba(139, 92, 246, 0.2), transparent 36%),
    radial-gradient(circle at 88% 74%, rgba(14, 165, 233, 0.18), transparent 42%),
    linear-gradient(135deg, #f8fafc 0%, #f5fbf4 100%);
  overflow-x: hidden;
}

.aurora-blob {
  position: fixed;
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
  filter: blur(80px);
  opacity: 0.18;
}
.aurora-blob-1 { width: 480px; height: 480px; top: -80px; left: -80px; background: rgba(16, 185, 129, 0.5); }
.aurora-blob-2 { width: 560px; height: 560px; bottom: -100px; right: -100px; background: rgba(14, 165, 233, 0.45); }
.aurora-blob-3 { width: 400px; height: 400px; top: 55%; left: 15%; background: rgba(139, 92, 246, 0.35); }

.profile-content {
  position: relative;
  z-index: 1;
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* ── Glass segment ────────────────────────────────── */
.glass-segment {
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(15, 23, 42, 0.08);
  padding: 1.75rem;
}

/* ── Header ───────────────────────────────────────── */
.profile-header-segment {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.avatar-wrapper {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 18px;
  cursor: pointer;
  flex-shrink: 0;
  overflow: hidden;
}

.avatar-img,
.initials-avatar {
  width: 80px;
  height: 80px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.initials-avatar {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: #fff;
  font-weight: 700;
  font-size: 1.5rem;
  letter-spacing: 0.02em;
}

.avatar-camera-overlay {
  position: absolute;
  inset: 0;
  border-radius: 18px;
  background: rgba(10, 25, 22, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 1.4rem;
  opacity: 0;
  transition: opacity 0.25s ease;
}

.avatar-wrapper:hover .avatar-camera-overlay { opacity: 1; }
.avatar-wrapper:hover .avatar-img,
.avatar-wrapper:hover .initials-avatar { transform: scale(1.04); }

.profile-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.25rem;
  line-height: 1.2;
}

.header-badges {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.role-badge {
  font-size: 0.78rem;
  font-weight: 600;
  color: #475569;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  padding: 3px 10px;
}

.verified-badge {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--sb-primary, #00895a);
  display: flex;
  align-items: center;
  gap: 4px;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  align-items: center;
}

.btn-ghost {
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  color: #334155;
  font-weight: 600;
  font-size: 0.875rem;
  padding: 0.5rem 1.25rem;
  transition: all 0.2s ease;
}
.btn-ghost:hover { background: #fff; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }

.btn-primary-action {
  background: var(--sb-primary, #00895a);
  border: none;
  border-radius: 12px;
  color: #fff;
  font-weight: 600;
  font-size: 0.875rem;
  padding: 0.5rem 1.25rem;
  transition: all 0.2s ease;
}
.btn-primary-action:hover { background: #007a50; box-shadow: 0 4px 14px rgba(0,137,90,0.3); }

/* ── Grid layout ─────────────────────────────────── */
.profile-grid {
  display: grid;
  grid-template-columns: 7fr 5fr;
  gap: 1.25rem;
  align-items: start;
}

.profile-col-left,
.profile-col-right {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* ── Segment header ──────────────────────────────── */
.segment-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.segment-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(0, 137, 90, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--sb-primary, #00895a);
  font-size: 1rem;
  flex-shrink: 0;
}

.segment-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.subject-counter {
  margin-left: auto;
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
  background: rgba(100, 116, 139, 0.1);
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 2px 8px;
}

/* ── Fields ──────────────────────────────────────── */
.field-group {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.field-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.field-label {
  font-size: 0.78rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-left: 4px;
}

.input-glass {
  background: rgba(248, 250, 252, 0.8);
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  padding: 0.65rem 1rem;
  font-size: 0.9rem;
  color: #0f172a;
  transition: all 0.2s ease;
  width: 100%;
}
.input-glass:focus {
  background: #fff;
  border-color: var(--sb-primary, #00895a);
  box-shadow: 0 0 0 4px rgba(0, 137, 90, 0.1);
  outline: none;
}

.input-disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ── Course & Year display ───────────────────────── */
.course-year-display {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.course-chip,
.year-chip {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--sb-primary, #00895a);
  background: rgba(0, 137, 90, 0.08);
  border: 1px solid rgba(0, 137, 90, 0.2);
  border-radius: 8px;
  padding: 5px 12px;
}

.chip-unset {
  color: #94a3b8;
  background: #f8fafc;
  border-color: #e2e8f0;
}

.change-btn {
  background: transparent;
  border: 1.5px dashed #cbd5e1;
  border-radius: 8px;
  color: #64748b;
  font-size: 0.82rem;
  font-weight: 600;
  padding: 5px 12px;
  transition: all 0.2s ease;
}
.change-btn:hover { border-color: var(--sb-primary, #00895a); color: var(--sb-primary, #00895a); }

/* ── Teaching level cards ────────────────────────── */
.teaching-level-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.teaching-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 0.5rem;
  border-radius: 14px;
  border: 1.5px solid #e2e8f0;
  background: rgba(248, 250, 252, 0.8);
  transition: all 0.25s ease;
  cursor: pointer;
}
.teaching-card:hover { border-color: rgba(0, 137, 90, 0.4); background: rgba(0, 137, 90, 0.03); }
.teaching-card-active { border-color: var(--sb-primary, #00895a) !important; background: rgba(0, 137, 90, 0.07) !important; }
.teaching-card-active .teaching-card-icon { color: var(--sb-primary, #00895a); }

.teaching-card-icon {
  font-size: 1.4rem;
  color: #94a3b8;
  transition: color 0.2s ease;
}
.teaching-card:hover .teaching-card-icon { color: var(--sb-primary, #00895a); }

.teaching-card-label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #64748b;
  transition: color 0.2s ease;
}
.teaching-card-active .teaching-card-label { color: var(--sb-primary, #00895a); }

/* ── Rate stepper ─────────────────────────────────── */
.rate-stepper {
  display: flex;
  align-items: center;
  gap: 0;
  background: rgba(0, 137, 90, 0.05);
  border: 1.5px solid rgba(0, 137, 90, 0.15);
  border-radius: 14px;
  padding: 0.5rem 1rem;
  justify-content: space-between;
}

.stepper-btn {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  background: #fff;
  color: var(--sb-primary, #00895a);
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}
.stepper-btn:hover:not(:disabled) { background: var(--sb-primary, #00895a); color: #fff; border-color: var(--sb-primary, #00895a); }
.stepper-btn:disabled { opacity: 0.35; cursor: not-allowed; }

.rate-display {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--sb-primary, #00895a);
  min-width: 100px;
  text-align: center;
}

/* ── Response time pills ─────────────────────────── */
.response-pills {
  display: flex;
  gap: 0.5rem;
}

.response-pill {
  flex: 1;
  padding: 0.5rem 0.25rem;
  border-radius: 10px;
  border: 1.5px solid #e2e8f0;
  background: rgba(248, 250, 252, 0.8);
  color: #64748b;
  font-size: 0.78rem;
  font-weight: 700;
  text-align: center;
  transition: all 0.2s ease;
}
.response-pill:hover { border-color: rgba(0, 137, 90, 0.4); color: var(--sb-primary, #00895a); }
.response-pill-active { background: var(--sb-primary, #00895a) !important; color: #fff !important; border-color: var(--sb-primary, #00895a) !important; }

/* ── Subject pills ───────────────────────────────── */
.subject-pill-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}

.subject-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 10px;
  border-radius: 8px;
  background: var(--sb-primary, #00895a);
  color: #fff;
  font-weight: 600;
  font-size: 0.82rem;
}

.subject-pill-remove {
  border: 0;
  background: transparent;
  color: inherit;
  font-size: 0.9rem;
  line-height: 1;
  padding: 0;
  display: flex;
  align-items: center;
}

.subject-add-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px 12px;
  border-radius: 8px;
  border: 1.5px dashed rgba(0, 137, 90, 0.4);
  background: transparent;
  color: var(--sb-primary, #00895a);
  font-weight: 600;
  font-size: 0.82rem;
  transition: all 0.2s ease;
}
.subject-add-btn:hover { background: rgba(0, 137, 90, 0.05); border-style: solid; }

/* ── Bio ─────────────────────────────────────────── */
.bio-textarea {
  resize: vertical;
  min-height: 90px;
}
.bio-near-limit { border-color: #f59e0b !important; }
.bio-at-limit { border-color: #dc3545 !important; box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.12) !important; }

.bio-counter {
  font-size: 0.75rem;
  color: #94a3b8;
  align-self: flex-end;
  margin-top: -0.25rem;
}
.bio-counter-warn { color: #ef4444; font-weight: 600; }

/* ── Session mode ────────────────────────────────── */
.session-mode-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.mode-check {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.9rem;
  color: #334155;
  cursor: pointer;
}

.mode-checkbox {
  width: 18px;
  height: 18px;
  accent-color: var(--sb-primary, #00895a);
  cursor: pointer;
}

/* ── Subject accordion ───────────────────────────── */
.subject-accordion-list { margin-top: 1rem; display: grid; gap: 10px; }

.subject-accordion-card {
  border: 1px solid #dbe7e1;
  border-radius: 16px;
  background: #f6f8f7;
  overflow: hidden;
  transition: border-color 180ms ease, box-shadow 180ms ease, background-color 180ms ease;
}
.subject-accordion-card-open { border-color: #9fd0ba; background: #eef7f3; box-shadow: 0 8px 20px rgba(10,122,81,0.08); }

.subject-accordion-header {
  width: 100%;
  border: 0;
  background: transparent;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  text-align: left;
}

.subject-accordion-icon {
  width: 32px; height: 32px;
  border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
  background: #dfe5e2; color: #65756d;
  flex-shrink: 0;
  transition: background-color 180ms ease, color 180ms ease;
}
.subject-accordion-icon-open { background: var(--sb-primary, #00895a); color: #fff; }

.subject-accordion-title { font-size: 0.95rem; font-weight: 700; color: #1f2f2a; transition: color 180ms ease; }
.subject-accordion-title-open { color: var(--sb-primary, #00895a); }
.subject-accordion-chevron { color: #5d7168; font-size: 0.9rem; }

.subject-accordion-body {
  padding: 0 16px 16px;
  display: grid; gap: 8px;
  overflow: hidden;
  transition: max-height 0.4s cubic-bezier(0.16,1,0.3,1), opacity 0.25s ease;
}

.subject-accordion-label { font-size: 0.7rem; font-weight: 800; letter-spacing: 0.07em; text-transform: uppercase; color: #6d8178; }

.subject-description-input {
  width: 100%; min-height: 110px;
  border: 0; border-radius: 14px;
  background: #fff; padding: 12px 14px;
  color: #183129; resize: vertical;
  box-shadow: inset 0 0 0 1px rgba(224,231,227,0.85);
}
.subject-description-input:focus { outline: none; box-shadow: 0 0 0 3px rgba(10,122,81,0.14); }

/* ── Bottom actions ──────────────────────────────── */
.profile-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 1rem;
}

.btn-discard {
  background: transparent;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  color: #64748b;
  font-weight: 600;
  font-size: 0.9rem;
  padding: 0.6rem 1.5rem;
  transition: all 0.2s ease;
}
.btn-discard:hover { border-color: #94a3b8; color: #334155; background: rgba(241,245,249,0.8); }

.btn-save {
  background: var(--sb-primary, #00895a);
  border: none;
  border-radius: 12px;
  color: #fff;
  font-weight: 700;
  font-size: 0.95rem;
  padding: 0.65rem 2.5rem;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 14px rgba(0, 137, 90, 0.25);
}
.btn-save:hover:not(:disabled) { background: #007a50; box-shadow: 0 6px 20px rgba(0,137,90,0.35); transform: translateY(-1px); }
.btn-save:disabled { opacity: 0.7; cursor: not-allowed; transform: none; }

/* ── Modal backdrop ──────────────────────────────── */
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1050;
  display: grid;
  place-items: center;
  padding: 1.5rem;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(4px);
}

.glass-modal {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  box-shadow: 0 24px 80px rgba(15, 23, 42, 0.2);
  padding: 1.75rem;
  width: 100%;
  overflow: hidden;
}

/* ── Course/Year modal ───────────────────────────── */
.course-year-modal {
  max-width: 600px;
  max-height: 85vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.modal-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.modal-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.modal-section-label {
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
  margin: 0;
}

.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 0.5rem;
}

.course-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  padding: 0.65rem 0.85rem;
  border-radius: 12px;
  border: 1.5px solid #e2e8f0;
  background: rgba(248, 250, 252, 0.8);
  text-align: left;
  transition: all 0.2s ease;
}
.course-card:hover { border-color: rgba(0,137,90,0.35); }
.course-card-active { border-color: var(--sb-primary, #00895a) !important; background: rgba(0,137,90,0.06) !important; }
.course-card-active .course-card-code { color: var(--sb-primary, #00895a); }

.course-card-code { font-size: 0.82rem; font-weight: 800; color: #0f172a; }
.course-card-name { font-size: 0.72rem; color: #64748b; }

.year-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.4rem;
}

.year-btn {
  padding: 0.45rem 0.25rem;
  border-radius: 10px;
  border: 1.5px solid #e2e8f0;
  background: rgba(248, 250, 252, 0.8);
  font-size: 0.75rem;
  font-weight: 600;
  color: #334155;
  text-align: center;
  transition: all 0.18s ease;
}
.year-btn:hover { border-color: rgba(0,137,90,0.35); }
.year-btn-active { background: var(--sb-primary, #00895a) !important; color: #fff !important; border-color: var(--sb-primary, #00895a) !important; }

.modal-footer-row {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.btn-ghost-sm {
  background: transparent;
  border: 1.5px solid #e2e8f0;
  border-radius: 10px;
  color: #64748b;
  font-weight: 600;
  font-size: 0.875rem;
  padding: 0.5rem 1.25rem;
  transition: all 0.2s ease;
}
.btn-ghost-sm:hover { background: #f8fafc; }

.btn-confirm {
  background: var(--sb-primary, #00895a);
  border: none;
  border-radius: 10px;
  color: #fff;
  font-weight: 700;
  font-size: 0.875rem;
  padding: 0.5rem 1.5rem;
  transition: all 0.2s ease;
}
.btn-confirm:hover { background: #007a50; }

/* ── Subject picker modal ────────────────────────── */
.subject-modal {
  max-width: 680px;
  max-height: 85vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.category-pills { display: flex; flex-wrap: wrap; gap: 6px; }

.category-pill {
  border: 1px solid #d8e3de;
  background: #fff;
  color: #315447;
  border-radius: 999px;
  padding: 5px 14px;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.15s ease;
}
.category-pill.active { background: rgba(0,137,90,0.08); border-color: var(--sb-primary, #00895a); color: var(--sb-primary, #00895a); }

.subject-modal-list { display: grid; gap: 8px; max-height: 380px; overflow-y: auto; }

.subject-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #dde7e2;
  border-radius: 12px;
  background: #fff;
  text-align: left;
  transition: all 0.15s ease;
}
.subject-option.selected { background: #eef8f4; border-color: #86d0af; }

.subject-option-copy { display: grid; gap: 2px; }
.subject-option-name { font-weight: 700; color: #163127; font-size: 0.9rem; }
.subject-option-meta { font-size: 0.8rem; color: #6e8178; }
.subject-option-check { flex-shrink: 0; }

.subject-modal-footer { display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap; }

/* ── Responsive ──────────────────────────────────── */
@media (max-width: 991px) {
  .profile-grid { grid-template-columns: 1fr; }
  .field-row-2 { grid-template-columns: 1fr; }
  .teaching-level-grid { grid-template-columns: repeat(3, 1fr); }
  .year-grid { grid-template-columns: repeat(4, 1fr); }
}

@media (max-width: 575px) {
  .tutor-profile-shell { padding: 1rem; }
  .glass-segment { padding: 1.25rem; }
  .profile-header-segment { flex-direction: column; align-items: flex-start; }
  .header-actions { width: 100%; }
  .btn-ghost, .btn-primary-action { flex: 1; text-align: center; }
  .teaching-level-grid { grid-template-columns: repeat(3, 1fr); gap: 0.5rem; }
  .year-grid { grid-template-columns: repeat(2, 1fr); }
  .course-grid { grid-template-columns: 1fr 1fr; }
  .response-pills { flex-direction: column; }
  .profile-actions { flex-direction: column-reverse; }
  .btn-discard, .btn-save { width: 100%; justify-content: center; }
}
```

- [ ] **Step 4: Start the dev server and verify the page loads**

```bash
npm run dev
```

Navigate to `http://localhost:5173`. Log in as a tutor account. Go to `/tutor-profile`.

Check that:
- [ ] Page renders with aurora glass background (no white/blank screen)
- [ ] Avatar placeholder shows initials
- [ ] All five segments are visible (Header, Identity, Expertise, Financials, Specializations)
- [ ] No console errors about undefined refs or missing imports

- [ ] **Step 5: Verify interactions**

- [ ] Click avatar → file picker opens
- [ ] Click "Change →" button → Course & Year modal opens with current values
- [ ] Select a different course + year in modal → "Confirm" updates the chips
- [ ] Click a teaching level card → it highlights with green border
- [ ] Click `−` rate button when rate is ₱50 → button is disabled / nothing changes
- [ ] Click `+` rate button → rate increments by ₱10
- [ ] Click response time pill → it fills with green
- [ ] Click "Add" in subjects → subject modal opens
- [ ] Type in bio → counter updates
- [ ] Click "Discard Changes" → fields reset to server values

- [ ] **Step 6: Commit**

```bash
git add src/views/TutorProfile.vue
git commit -m "feat: redesign TutorProfile.vue with aurora bento glassmorphism layout"
```

---

## Self-Review

**Spec coverage check:**

| Spec section | Covered by task |
|---|---|
| New `POST /tutor/profile/avatar/` endpoint | Task 2 |
| `profile_picture_url` in GET response | Task 1 |
| Avatar click → upload → preview | Task 3, Step 2 (`handleAvatarUpload`) |
| Header segment (avatar, name, verified, actions) | Task 3, Step 1 (template) |
| Identity segment (fname, lname, email) | Task 3, Step 1 |
| Course & Year combined modal with draft pattern | Task 3, Steps 1 + 2 |
| Expertise: 3 fixed teaching level cards | Task 3, Steps 1 + 2 |
| Financials: hourly rate stepper (min ₱50, +₱10) | Task 3, Steps 1 + 2 |
| Financials: response time pills | Task 3, Steps 1 + 2 |
| Specializations: subject pills + modal (reskinned) | Task 3, Steps 1 + 2 |
| Bio textarea with char counter + danger state | Task 3, Steps 1 + 3 |
| Session mode checkboxes | Task 3, Step 1 |
| Save Profile (3 APIs + syncSubjects) | Task 3, Step 2 (`saveProfile`) |
| Discard = re-fetch | Task 3, Step 2 (`discardChanges`) |
| Aurora glassmorphism scoped CSS | Task 3, Step 3 |
| Responsive mobile layout | Task 3, Step 3 (`@media`) |
| Backend tests (4 tests for 2 endpoints) | Tasks 1 + 2 |

All spec requirements are covered. No placeholders found.
