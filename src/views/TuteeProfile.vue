<template>
  <div class="tutee-profile-shell py-4 py-lg-5">
    <div class="container">
      <form @submit.prevent="saveProfile">
        <div class="profile-card">

          <!-- ── HEADER ── -->
          <div class="p-header d-flex align-items-start justify-content-between flex-wrap gap-3">
            <div class="d-flex align-items-start gap-4">
              <div class="avatar-wrap">
                <img
                  v-if="profile.profile_picture_url && !avatarLoadError"
                  :src="profile.profile_picture_url"
                  class="avatar-img rounded-circle"
                  @click="triggerFileInput"
                  @error="avatarLoadError = true"
                >
                <div
                  v-else
                  class="avatar-initials rounded-circle d-flex align-items-center justify-content-center fw-bold"
                  @click="triggerFileInput"
                >
                  {{ initials }}
                </div>
                <input type="file" ref="fileInput" class="visually-hidden" accept="image/*" @change="handleAvatarUpload">
                <button type="button" class="avatar-badge sb-btn" @click="triggerFileInput" aria-label="Upload photo">
                  <i class="bi bi-pencil-fill"></i>
                </button>
              </div>
              <div class="pt-1">
                <h2 class="mb-1 fw-bold text-dark">{{ profile.fname }} {{ profile.lname }}</h2>
                <p class="mb-2 small text-muted d-flex align-items-center gap-1">
                  <i class="bi bi-mortarboard-fill"></i> Student / Tutee
                </p>
                <button type="button" class="sb-btn update-photo-btn" @click="triggerFileInput">Update Photo</button>
              </div>
            </div>
            <div class="d-flex gap-2 align-items-center pt-1">
              <button type="button" class="sb-btn btn-discard px-4 py-2" @click="discardChanges">Discard</button>
              <button type="submit" class="sb-btn btn-save-header px-4 py-2">Save Profile</button>
            </div>
          </div>

          <!-- ── BODY ── -->
          <div class="p-4 p-md-5">
            <div class="row g-5">

              <!-- LEFT: Personal Info + Bio -->
              <div class="col-lg-7">

                <section class="mb-5">
                  <p class="section-eyebrow">Personal Information</p>
                  <div class="row g-3">
                    <div class="col-6">
                      <label class="field-label">First Name</label>
                      <input type="text" v-model="profile.fname" class="form-control input-glass">
                    </div>
                    <div class="col-6">
                      <label class="field-label">Last Name</label>
                      <input type="text" v-model="profile.lname" class="form-control input-glass">
                    </div>
                    <div class="col-12">
                      <label class="field-label">Middle Name</label>
                      <input type="text" v-model="profile.mname" class="form-control input-glass">
                    </div>
                    <div class="col-12">
                      <label class="field-label">University Email</label>
                      <div class="position-relative">
                        <i class="bi bi-lock field-icon text-muted"></i>
                        <input type="email" v-model="profile.email" class="form-control input-glass input-locked" disabled>
                      </div>
                      <div class="form-text mt-1 small">
                        <i class="bi bi-info-circle"></i> Email cannot be changed after registration
                      </div>
                    </div>
                  </div>
                </section>

                <section>
                  <p class="section-eyebrow">Bio (About Me)</p>
                  <div class="position-relative">
                    <textarea
                      v-model="profile.bio"
                      :class="['form-control input-glass', { 'border-danger': bioCharCount > 450 }]"
                      rows="7"
                      maxlength="500"
                      placeholder="Tell tutors about your learning style, academic goals, or what you usually need help with..."
                    ></textarea>
                    <span :class="['bio-counter', bioCharCount > 450 ? 'text-danger fw-bold' : 'text-muted']">
                      {{ bioCharCount }} / 500
                    </span>
                  </div>
                </section>

              </div>

              <!-- RIGHT: Academic + Preferences -->
              <div class="col-lg-5">

                <section class="mb-5">
                  <p class="section-eyebrow">Academic Details</p>

                  <!-- Education Level -->
                  <label class="field-label">Education Level</label>
                  <div class="edu-grid mb-4 mt-2">
                    <label v-for="lvl in educationLevels" :key="lvl.value" class="rc-label">
                      <input type="radio" name="edu_level" class="visually-hidden" :value="lvl.value" v-model="educationLevel">
                      <div :class="['rc-inner text-center', { active: educationLevel === lvl.value }]">{{ lvl.label }}</div>
                    </label>
                  </div>

                  <!-- Year Level -->
                  <label class="field-label">Year Level</label>
                  <div class="year-grid mb-4 mt-2">
                    <label v-for="opt in yearOptions" :key="opt.value" class="rc-label">
                      <input type="radio" name="year_level" class="visually-hidden" :value="opt.value" v-model="profile.year_level">
                      <div :class="['rc-inner text-center', { active: profile.year_level === opt.value }]">{{ opt.label }}</div>
                    </label>
                  </div>

                  <!-- Course / Strand (SHS and College only) -->
                  <template v-if="educationLevel === 'college' || educationLevel === 'shs'">
                    <label class="field-label">{{ educationLevel === 'college' ? 'Course' : 'Strand' }}</label>
                    <div class="d-flex flex-column gap-2 mt-2">
                      <label v-for="c in courses" :key="c.course_code" class="rc-label">
                        <input type="radio" name="course" class="visually-hidden" :value="c.course_code" v-model="profile.course">
                        <div :class="['rc-inner d-flex align-items-center justify-content-between', { active: profile.course === c.course_code }]">
                          <span>{{ c.course_name }}</span>
                          <i v-if="profile.course === c.course_code" class="bi bi-check-circle-fill"></i>
                        </div>
                      </label>
                    </div>
                  </template>
                </section>

                <section>
                  <p class="section-eyebrow">Tutoring Preferences</p>
                  <label class="field-label">Preferred Subjects</label>
                  <div class="d-flex flex-wrap gap-2 mt-2">
                    <label v-for="s in subjects" :key="s.subject_code" class="subject-pill-label">
                      <input type="checkbox" class="visually-hidden" :value="s.subject_code" v-model="profile.subjects">
                      <span :class="['subject-pill', { active: profile.subjects.includes(s.subject_code) }]">
                        {{ s.subject_name }}
                      </span>
                    </label>
                  </div>
                </section>

              </div>

            </div>
          </div>

          <!-- ── FOOTER ── -->
          <div class="p-footer d-flex align-items-center justify-content-between flex-wrap gap-3">
            <p v-if="lastUpdated" class="mb-0 small text-muted fst-italic">Last updated: {{ lastUpdated }}</p>
            <span v-else></span>
            <button type="submit" class="sb-btn btn-save px-5 py-2 fw-semibold">Save Changes</button>
          </div>

        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import api from '@/services/api/api'
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()

const profile = ref({
  fname: '',
  mname: '',
  lname: '',
  email: '',
  course: '',
  year_level: null,
  bio: '',
  profile_picture_url: null,
  subjects: [],
  updated_at: null
})

const courses = ref([])
const subjects = ref([])
const educationLevel = ref('college')
const fileInput = ref(null)
const avatarLoadError = ref(false)

const educationLevels = [
  { label: 'Elementary', value: 'elementary' },
  { label: 'JHS',        value: 'jhs' },
  { label: 'SHS',        value: 'shs' },
  { label: 'College',    value: 'college' },
]

watch(() => profile.value.profile_picture_url, () => {
  avatarLoadError.value = false
})

const bioCharCount = computed(() => profile.value.bio?.length || 0)

function deriveEducationLevel(yearLevel) {
  if (!yearLevel) return 'college'
  const val = parseInt(yearLevel)
  if (val >= 1  && val <= 6)  return 'elementary'
  if (val >= 7  && val <= 10) return 'jhs'
  if (val >= 11 && val <= 12) return 'shs'
  return 'college'
}

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
  const suffix = n => ['th','st','nd','rd'][Math.min(n,3)] ?? 'th'
  return [13,14,15,16].map(v => ({ label: `${v-12}${suffix(v-12)} Year`, value: v }))
})

watch(educationLevel, (newVal) => {
  if (deriveEducationLevel(profile.value.year_level) !== newVal) {
    profile.value.year_level = yearOptions.value[0].value
    profile.value.course = ''
  }
})

const loadProfile = async () => {
  try {
    const res = await api.get('/tutee/profile/')
    profile.value = { ...profile.value, ...res.data }
    educationLevel.value = deriveEducationLevel(res.data.year_level)
  } catch (err) {
    console.error('Failed to load profile', err)
    toastStore.push('Failed to load profile', 'error')
  }
}

const loadSubjects = async () => {
  try {
    const res = await api.get('subjects/')
    subjects.value = res.data
  } catch (err) {
    console.error('Failed to load subjects', err)
  }
}

const loadCourses = async () => {
  try {
    const res = await api.get('courses/')
    courses.value = res.data
  } catch (err) {
    console.error('Failed to load courses', err)
  }
}

const initials = computed(() => {
  const f = profile.value?.fname?.charAt(0) || ''
  const l = profile.value?.lname?.charAt(0) || ''
  return (f + l).toUpperCase()
})

const lastUpdated = computed(() => {
  if (!profile.value.updated_at) return null
  return new Date(profile.value.updated_at).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric'
  })
})

const triggerFileInput = () => fileInput.value.click()

const handleAvatarUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  if (!file.type.startsWith('image/')) {
    toastStore.push('Please select an image file', 'error'); return
  }
  if (file.size > 5 * 1024 * 1024) {
    toastStore.push('Image must be under 5 MB', 'error'); return
  }
  const fd = new FormData()
  fd.append('avatar', file)
  try {
    const res = await api.post('/tutee/profile/avatar/', fd)
    profile.value.profile_picture_url = res.data.profile_picture_url
    toastStore.push('Photo updated successfully')
  } catch (err) {
    console.error('Avatar upload failed', err)
    toastStore.push('Failed to upload photo', 'error')
  }
}

const discardChanges = () => loadProfile()

const saveProfile = async () => {
  try {
    await api.put('/tutee/profile/update/', profile.value)
    toastStore.push('Profile updated successfully')
  } catch (err) {
    console.error(err)
    toastStore.push('Failed to update profile', 'error')
  }
}

onMounted(() => {
  loadProfile()
  loadCourses()
  loadSubjects()
})
</script>

<style scoped>
/* ── Shell ── */
.tutee-profile-shell {
  min-height: 100%;
  background:
    radial-gradient(circle at 0% 0%,   rgba(16, 185, 129, 0.32), transparent 38%),
    radial-gradient(circle at 96% 6%,  rgba(139, 92, 246, 0.2),  transparent 36%),
    radial-gradient(circle at 88% 74%, rgba(14, 165, 233, 0.18), transparent 42%),
    linear-gradient(135deg, #f8fafc 0%, #f5fbf4 100%);
}

/* ── Card ── */
.profile-card {
  max-width: 900px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 24px;
  box-shadow: 0 24px 80px rgba(15, 23, 42, 0.18);
  overflow: hidden;
}

/* ── Header ── */
.p-header {
  padding: 2rem 2.5rem;
  border-bottom: 1px solid rgba(15, 23, 42, 0.07);
}

/* ── Avatar ── */
.avatar-wrap { position: relative; width: 80px; height: 80px; flex-shrink: 0; }

.avatar-img,
.avatar-initials {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  cursor: pointer;
  border: 3px solid white;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.12);
  transition: transform 0.25s var(--sb-spring, cubic-bezier(0.16,1,0.3,1));
}

.avatar-img:hover,
.avatar-initials:hover { transform: scale(1.04); }

.avatar-initials {
  background: var(--sb-primary);
  color: white;
  font-size: 1.5rem;
  font-weight: 700;
}

.avatar-badge {
  position: absolute;
  bottom: -1px;
  right: -1px;
  width: 26px;
  height: 26px;
  background: white;
  color: var(--sb-primary);
  border: 1.5px solid var(--sb-primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  padding: 0;
  cursor: pointer;
}

/* ── Buttons ── */
.sb-btn {
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: transform 0.15s var(--sb-spring, cubic-bezier(0.16,1,0.3,1)),
              box-shadow 0.15s ease,
              background-color 0.15s ease;
}
.sb-btn:active { transform: scale(0.96); }

.btn-save-header {
  background: var(--sb-primary-deep, #006a44);
  color: white;
}
.btn-save-header:hover { background: var(--sb-primary); color: white; }

.btn-save {
  background: var(--sb-primary);
  color: white;
}
.btn-save:hover { background: var(--sb-primary-hover); color: white; }

.btn-discard {
  background: rgba(15, 23, 42, 0.05);
  color: var(--sb-ink, #0f172a);
  border: 1px solid rgba(15, 23, 42, 0.12);
}
.btn-discard:hover { background: rgba(15, 23, 42, 0.1); }

.update-photo-btn {
  background: none;
  border: none;
  color: var(--sb-primary);
  font-size: 13px;
  font-weight: 600;
  padding: 0;
  cursor: pointer;
}
.update-photo-btn:hover { text-decoration: underline; color: var(--sb-primary-hover); }

/* ── Typography ── */
.section-eyebrow {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--sb-muted, #475569);
  margin-bottom: 1rem;
}

.field-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 0.35rem;
}

/* ── Inputs ── */
.input-glass {
  background: rgba(248, 250, 252, 0.8);
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  padding: 0.7rem 1rem;
  font-size: 15px;
  transition: all 0.2s ease;
}
.input-glass:focus {
  background: white;
  border-color: var(--sb-primary);
  box-shadow: 0 0 0 4px rgba(0, 137, 90, 0.1);
  outline: none;
}
.input-locked {
  cursor: not-allowed;
  color: var(--sb-muted, #475569);
  padding-left: 2.4rem;
}

.field-icon {
  position: absolute;
  left: 0.9rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 14px;
  pointer-events: none;
}

.bio-counter {
  position: absolute;
  bottom: 0.65rem;
  right: 0.9rem;
  font-size: 11px;
  pointer-events: none;
}

.border-danger { border-color: #dc3545 !important; }

/* ── Radio cards ── */
.rc-label   { margin: 0; cursor: pointer; display: block; }

.rc-inner {
  padding: 0.65rem 1rem;
  border-radius: 12px;
  border: 1.5px solid rgba(15, 23, 42, 0.1);
  background: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.rc-inner:hover:not(.active) {
  border-color: var(--sb-primary);
  background: rgba(255, 255, 255, 0.9);
}
.rc-inner.active {
  background: var(--sb-primary);
  color: white;
  border-color: var(--sb-primary);
}

.edu-grid,
.year-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}

/* ── Subject pills ── */
.subject-pill-label { margin: 0; cursor: pointer; }

.subject-pill {
  display: inline-block;
  padding: 0.4rem 0.9rem;
  border-radius: 9999px;
  border: 1.5px solid rgba(15, 23, 42, 0.1);
  background: rgba(255, 255, 255, 0.6);
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.18s ease;
}
.subject-pill:hover:not(.active) {
  border-color: var(--sb-primary);
  color: var(--sb-primary);
}
.subject-pill.active {
  background: var(--sb-primary);
  color: white;
  border-color: var(--sb-primary);
}

/* ── Footer ── */
.p-footer {
  padding: 1.25rem 2.5rem;
  border-top: 1px solid rgba(15, 23, 42, 0.07);
  background: rgba(248, 250, 252, 0.5);
}
</style>
