<template>
  <div class="tutor-profile-shell">
    <form class="profile-content" @submit.prevent="saveProfile">
      <header class="glass-segment profile-header-segment">
        <div class="header-left">
          <button
            type="button"
            class="avatar-wrapper sb-btn"
            aria-label="Upload profile photo"
            @click="triggerAvatarUpload"
          >
            <img
              v-if="avatarUrl && !avatarLoadError"
              :src="avatarUrl"
              class="avatar-img"
              alt="Profile photo"
              @error="avatarLoadError = true"
            >
            <span v-else class="initials-avatar">{{ initials || 'SB' }}</span>
            <span class="avatar-camera-overlay">
              <i class="bi bi-camera-fill"></i>
            </span>
          </button>
          <input
            ref="fileInputRef"
            type="file"
            accept="image/*"
            class="visually-hidden"
            @change="handleAvatarUpload"
          >

          <div class="header-info">
            <p class="header-kicker">Tutor Profile</p>
            <h1 class="profile-name">{{ profile.fullName || 'Your Name' }}</h1>
            <div class="header-badges">
              <span class="role-badge">
                <i class="bi bi-mortarboard-fill"></i>
                Tutor
              </span>
              <span
                v-if="profileStore.applicationStatus === 'approved' && profileStore.renewalStatus === 'verified'"
                class="verified-badge"
              >
                <i class="bi bi-patch-check-fill"></i>
                Verified
              </span>
            </div>
          </div>
        </div>

        <div class="header-actions">
          <button type="button" class="btn-soft sb-btn" @click="goToSchedule">
            <i class="bi bi-calendar3"></i>
            Schedule
          </button>
        </div>
      </header>

      <VerificationStatusCard />
      <VerificationDevPanel v-if="isDev" role="tutor" />

      <main class="profile-grid">
        <div class="profile-col">
          <section class="glass-segment">
            <div class="segment-header">
              <span class="segment-icon"><i class="bi bi-person-fill"></i></span>
              <div>
                <h2 class="segment-title">Identity Details</h2>
                <p class="segment-copy">Keep your visible tutor identity current.</p>
              </div>
            </div>

            <div class="field-group">
              <div class="field-row-2">
                <label class="field">
                  <span class="field-label">Full Name</span>
                  <input
                    v-model.trim="profile.fullName"
                    type="text"
                    class="input-glass sb-field"
                    placeholder="First Last"
                  >
                </label>

                <label class="field">
                  <span class="field-label">Email</span>
                  <input
                    :value="profile.email"
                    type="email"
                    class="input-glass input-disabled sb-field"
                    disabled
                  >
                </label>
              </div>

              <div class="field">
                <span class="field-label">Course</span>
                <SbSelectModal
                  v-model="profile.course"
                  :options="courseOptions"
                  title="Course"
                  placeholder="+ Add Course"
                  search-placeholder="Search courses"
                  searchable
                />
              </div>

              <div class="field">
                <span class="field-label">Year Level</span>
                <div class="year-grid" role="radiogroup" aria-label="Year level">
                  <button
                    v-for="year in filteredYearLevels"
                    :key="year.value"
                    type="button"
                    class="year-btn sb-btn"
                    :class="{ 'year-btn-active': Number(profile.year_level) === year.value }"
                    role="radio"
                    :aria-checked="Number(profile.year_level) === year.value"
                    @click="profile.year_level = year.value"
                  >
                    {{ year.label }}
                  </button>
                </div>
              </div>
            </div>
          </section>

          <section class="glass-segment">
            <div class="segment-header">
              <span class="segment-icon"><i class="bi bi-award-fill"></i></span>
              <div>
                <h2 class="segment-title">Expertise Level</h2>
                <p class="segment-copy">Choose the learner level you are ready to teach.</p>
              </div>
            </div>

            <div class="teaching-level-grid" role="radiogroup" aria-label="Teaching level">
              <button
                v-for="option in teachingLevelOptions"
                :key="option.value"
                type="button"
                class="teaching-card sb-btn"
                :class="{ 'teaching-card-active': profile.teaching_level === option.value }"
                role="radio"
                :aria-checked="profile.teaching_level === option.value"
                @click="profile.teaching_level = option.value"
              >
                <i :class="['bi', option.icon, 'teaching-card-icon']"></i>
                <span class="teaching-card-label">{{ option.label }}</span>
              </button>
            </div>
          </section>

          <section class="glass-segment">
            <div class="segment-header">
              <span class="segment-icon"><i class="bi bi-cash-coin"></i></span>
              <div>
                <h2 class="segment-title">Financials</h2>
                <p class="segment-copy">Set your rate and response goal.</p>
              </div>
            </div>

            <div class="field-group">
              <div class="field">
                <span class="field-label">Hourly Rate</span>
                <div class="rate-stepper">
                  <button
                    type="button"
                    class="stepper-btn sb-btn"
                    :disabled="normalizedRate <= minHourlyRate"
                    aria-label="Decrease hourly rate"
                    @click="decrementRate"
                  >
                    <i class="bi bi-dash-lg"></i>
                  </button>
                  <span class="rate-display">PHP {{ normalizedRate.toFixed(2) }}</span>
                  <button
                    type="button"
                    class="stepper-btn sb-btn"
                    :disabled="normalizedRate >= maxHourlyRate"
                    aria-label="Increase hourly rate"
                    @click="incrementRate"
                  >
                    <i class="bi bi-plus-lg"></i>
                  </button>
                </div>
                <p class="field-hint">
                  Maximum PHP {{ maxHourlyRate.toFixed(2) }} per hour.
                </p>
              </div>

              <div class="field">
                <span class="field-label">Response Time</span>
                <div class="response-pills" role="radiogroup" aria-label="Response time">
                  <button
                    v-for="option in responseTimeOptions"
                    :key="option.value"
                    type="button"
                    class="response-pill sb-btn"
                    :class="{ 'response-pill-active': profile.response_time === option.value }"
                    role="radio"
                    :aria-checked="profile.response_time === option.value"
                    @click="profile.response_time = option.value"
                  >
                    {{ option.label }}
                  </button>
                </div>
              </div>
            </div>
          </section>
        </div>

        <div class="profile-col">
          <section class="glass-segment specializations-segment">
            <div class="segment-header segment-header-with-action">
              <span class="segment-icon"><i class="bi bi-stars"></i></span>
              <div>
                <h2 class="segment-title">Specializations</h2>
                <p class="segment-copy">
                  Your top {{ TUTOR_SUBJECT_LIMIT }} subjects — the ones you teach best.
                </p>
              </div>
              <span
                class="subject-counter"
                :class="{ 'subject-counter-full': isAtSubjectLimit }"
              >{{ profile.subjects.length }}/{{ TUTOR_SUBJECT_LIMIT }}</span>
            </div>

            <div class="field-group">
              <div class="subject-pill-row">
                <span
                  v-for="subject in profile.subjects"
                  :key="subject.subject_code"
                  class="subject-pill"
                >
                  {{ subject.subject_name }}
                  <button
                    type="button"
                    class="subject-pill-remove sb-btn"
                    :aria-label="`Remove ${subject.subject_name}`"
                    @click="removeSubject(subject.subject_code)"
                  >
                    <i class="bi bi-x-lg"></i>
                  </button>
                </span>

                <button
                  type="button"
                  class="subject-add-btn sb-btn"
                  :disabled="isAtSubjectLimit"
                  :title="isAtSubjectLimit ? subjectLimitMessage : undefined"
                  @click="openSubjectModal"
                >
                  <i class="bi bi-plus-lg"></i>
                  Add Subject
                </button>
              </div>

              <p v-if="isAtSubjectLimit" class="limit-notice">
                <i class="bi bi-info-circle-fill"></i>
                {{ subjectLimitMessage }}
              </p>

              <p v-if="!profile.subjects.length" class="empty-note">
                No subjects selected yet.
              </p>

              <label class="field">
                <span class="field-label">Bio</span>
                <textarea
                  v-model="profile.bio"
                  class="input-glass bio-textarea sb-field"
                  :class="{ 'bio-near-limit': bioCharCount > 450, 'bio-at-limit': bioCharCount >= 500 }"
                  maxlength="500"
                  rows="5"
                  placeholder="Share your teaching philosophy, strengths, and the kind of support learners can expect."
                ></textarea>
                <span class="bio-counter" :class="{ 'bio-counter-warn': bioCharCount > 450 }">
                  {{ bioCharCount }}/500
                </span>
              </label>

              <div class="session-mode-group">
                <span class="field-label">Session Mode</span>
                <div class="mode-card-grid">
                  <label
                    class="mode-check sb-btn"
                    :class="{ 'mode-check-active': profile.can_online }"
                  >
                    <input v-model="profile.can_online" type="checkbox" class="mode-checkbox">
                    <span class="mode-copy">
                      <span class="mode-icon"><i class="bi bi-camera-video-fill"></i></span>
                      <span>
                        <span class="mode-title">Online Tutoring</span>
                        <span class="mode-subtitle">Video sessions with remote learners</span>
                      </span>
                    </span>
                    <span class="mode-checkmark" aria-hidden="true">
                      <i class="bi" :class="profile.can_online ? 'bi-check-circle-fill' : 'bi-circle'"></i>
                    </span>
                  </label>
                  <label
                    class="mode-check sb-btn"
                    :class="{ 'mode-check-active': profile.can_f2f }"
                  >
                    <input v-model="profile.can_f2f" type="checkbox" class="mode-checkbox">
                    <span class="mode-copy">
                      <span class="mode-icon"><i class="bi bi-geo-alt-fill"></i></span>
                      <span>
                        <span class="mode-title">Face-to-Face</span>
                        <span class="mode-subtitle">In-person sessions on campus or nearby</span>
                      </span>
                    </span>
                    <span class="mode-checkmark" aria-hidden="true">
                      <i class="bi" :class="profile.can_f2f ? 'bi-check-circle-fill' : 'bi-circle'"></i>
                    </span>
                  </label>
                </div>
              </div>
            </div>

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
                  :aria-expanded="openSubjectCode === subject.subject_code"
                  @click="toggleSubjectAccordion(subject.subject_code)"
                >
                  <span
                    class="subject-accordion-icon"
                    :class="{ 'subject-accordion-icon-open': openSubjectCode === subject.subject_code }"
                  >
                    <i class="bi bi-journal-bookmark-fill"></i>
                  </span>
                  <span
                    class="subject-accordion-title"
                    :class="{ 'subject-accordion-title-open': openSubjectCode === subject.subject_code }"
                  >
                    {{ subject.subject_name }}
                  </span>
                  <i
                    class="bi ms-auto subject-accordion-chevron"
                    :class="openSubjectCode === subject.subject_code ? 'bi-chevron-up' : 'bi-chevron-down'"
                  ></i>
                </button>

                <Transition name="sb-accordion">
                  <div v-if="openSubjectCode === subject.subject_code" class="subject-accordion-body">
                    <label class="subject-accordion-label" :for="`subject-${subject.subject_code}`">
                      Subject Description
                    </label>
                    <textarea
                      :id="`subject-${subject.subject_code}`"
                      v-model="subject.description"
                      rows="4"
                      class="subject-description-input sb-field"
                      placeholder="Describe your method, scope, and materials for this subject."
                    ></textarea>
                  </div>
                </Transition>
              </article>
            </div>
          </section>

          <section class="glass-segment actions-segment">
            <div>
              <h2 class="segment-title">Profile Changes</h2>
              <p class="segment-copy mb-0">
                Save your updates when every section is ready.
              </p>
            </div>
            <div class="profile-actions">
              <button
                type="button"
                class="btn-discard sb-btn"
                :disabled="isSavingProfile || isLoadingProfile"
                @click="discardChanges"
              >
                Discard Changes
              </button>
              <button
                type="submit"
                class="btn-save sb-btn sb-elevated sb-elevated--brand"
                :disabled="isSavingProfile || isLoadingProfile"
              >
                <span
                  v-if="isSavingProfile"
                  class="spinner-border spinner-border-sm"
                  aria-hidden="true"
                ></span>
                {{ isSavingProfile ? 'Saving' : 'Save Profile' }}
              </button>
            </div>
          </section>
        </div>
      </main>
    </form>

    <Teleport to="body">
    <div
      v-if="isSubjectModalOpen"
      class="modal-backdrop-soft sb-overlay"
      role="presentation"
      @click.self="closeSubjectModal"
    >
      <section
        class="glass-modal subject-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="subject-modal-title"
      >
        <div class="modal-header-row">
          <div>
            <p class="modal-kicker">Specializations</p>
            <h2 id="subject-modal-title" class="modal-title">Choose Subjects</h2>
          </div>
          <button type="button" class="modal-close sb-btn" aria-label="Close" @click="closeSubjectModal">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <div class="subject-modal-list">
          <div v-if="isLoadingSubjects" class="modal-status">
            <span class="spinner-border spinner-border-sm" aria-hidden="true"></span>
            Loading subjects
          </div>
          <div v-else-if="subjectsLoadError" class="modal-status modal-error">
            {{ subjectsLoadError }}
          </div>
          <!-- Same picker the onboarding step uses, so the browse/search/limit behaviour a tutor
               learned during onboarding is the behaviour they get when editing later. -->
          <SubjectTaxonomyPicker
            v-else
            v-model="draftSubjectCodes"
            :subjects="allSubjects"
            :max-selection="TUTOR_SUBJECT_LIMIT"
          />
        </div>

        <div class="subject-modal-footer">
          <span class="selected-count">{{ selectedDraftCountLabel }}</span>
          <div class="modal-footer-actions">
            <button type="button" class="btn-ghost-sm sb-btn" @click="closeSubjectModal">
              Cancel
            </button>
            <button type="button" class="btn-confirm sb-btn" @click="confirmSubjectSelection">
              Confirm
            </button>
          </div>
        </div>
      </section>
    </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api/api'
import { useAuthStore } from '@/stores/auth'
import { useCatalogStore } from '@/stores/catalog'
import { useToastStore } from '@/stores/toast'
import { useProfileStore } from '@/stores/profile'
import {
  HOURLY_RATE_STEP,
  MAX_HOURLY_RATE,
  MIN_HOURLY_RATE,
  TUTOR_SUBJECT_LIMIT,
} from '@/config'
import SbSelectModal from '@/components/SbSelectModal.vue'
import SubjectTaxonomyPicker from '@/components/SubjectTaxonomyPicker.vue'
import VerificationStatusCard from '@/components/VerificationStatusCard.vue'
import VerificationDevPanel from '@/components/VerificationDevPanel.vue'

const isDev = import.meta.env.DEV

const router = useRouter()
const authStore = useAuthStore()
const catalogStore = useCatalogStore()
const toastStore = useToastStore()
const profileStore = useProfileStore()

const minHourlyRate = MIN_HOURLY_RATE
const maxHourlyRate = MAX_HOURLY_RATE
const hourlyRateStep = HOURLY_RATE_STEP

const profile = ref({
  fullName: '',
  fname: '',
  lname: '',
  email: '',
  course: '',
  year_level: null,
  subjects: [],
  bio: '',
  hourly_rate: minHourlyRate,
  teaching_level: 'College',
  can_online: true,
  can_f2f: false,
  response_time: '',
  profile_picture_url: ''
})

const courses = ref([])
const allSubjects = ref([])
const initialSubjectCodes = ref([])
const initialSubjectDescriptions = ref(new Map())
const fileInputRef = ref(null)
const avatarLoadError = ref(false)
const isLoadingProfile = ref(false)
const isSavingProfile = ref(false)
const isUploadingAvatar = ref(false)
const isSubjectModalOpen = ref(false)
const draftSubjectCodes = ref([])
const openSubjectCode = ref(null)
const isLoadingSubjects = ref(false)
const subjectsLoadError = ref('')

const responseTimeOptions = [
  { value: 'within_1_hour', label: 'Within 1 hour' },
  { value: 'within_few_hours', label: 'Within a few hours' },
  { value: 'within_a_day', label: 'Within a day' }
]

const teachingLevelOptions = [
  { value: 'Elementary', label: 'Elementary', icon: 'bi-pencil-fill' },
  { value: 'High School', label: 'High School', icon: 'bi-book-fill' },
  { value: 'College', label: 'College', icon: 'bi-mortarboard-fill' }
]

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
  { label: '1st Year', value: 13 },
  { label: '2nd Year', value: 14 },
  { label: '3rd Year', value: 15 },
  { label: '4th Year', value: 16 }
]

watch(
  () => profile.value.profile_picture_url,
  () => {
    avatarLoadError.value = false
  }
)

const bioCharCount = computed(() => profile.value.bio?.length || 0)

// Clamped at both ends so a tutor carrying a pre-cap rate (seeded demo data had 350) sees the
// value the server will actually store, rather than a figure that silently changes on save.
const normalizedRate = computed(() => {
  const rate = Number(profile.value.hourly_rate)
  if (!Number.isFinite(rate)) return minHourlyRate
  return Math.min(Math.max(rate, minHourlyRate), maxHourlyRate)
})

const avatarUrl = computed(() => profile.value.profile_picture_url || '')

const initials = computed(() => {
  const displayName = profile.value.fullName
    || [profile.value.fname, profile.value.lname].filter(Boolean).join(' ')

  const parts = String(displayName || '')
    .trim()
    .split(/\s+/)
    .filter(Boolean)

  if (!parts.length) {
    return ''
  }

  return parts
    .slice(0, 2)
    .map(part => part.charAt(0).toUpperCase())
    .join('')
})

const courseOptions = computed(() =>
  courses.value.map(course => ({
    label: `${course.course_code} - ${course.course_name}`,
    value: course.course_code,
  }))
)

const filteredYearLevels = computed(() => {
  const selectedCourse = courses.value.find(course => course.course_code === profile.value.course)
  const level = getCourseEducationLevel(selectedCourse)

  if (level === 'elementary') {
    return yearLevels.filter(year => year.value >= 1 && year.value <= 6)
  }

  if (level === 'jhs') {
    return yearLevels.filter(year => year.value >= 7 && year.value <= 10)
  }

  if (level === 'shs') {
    return yearLevels.filter(year => year.value >= 11 && year.value <= 12)
  }

  if (level === 'college') {
    return yearLevels.filter(year => year.value >= 13 && year.value <= 16)
  }

  return yearLevels
})

const selectedDraftCountLabel = computed(() => {
  const count = draftSubjectCodes.value.length
  return `${count} of ${TUTOR_SUBJECT_LIMIT} subject${count === 1 ? '' : 's'} selected`
})

const isAtSubjectLimit = computed(() => profile.value.subjects.length >= TUTOR_SUBJECT_LIMIT)

const subjectLimitMessage =
  `You've reached the ${TUTOR_SUBJECT_LIMIT}-subject limit. Remove one to add another.`

function getCourseEducationLevel(course) {
  if (!course) {
    return null
  }

  const code = String(course.course_code || '').toLowerCase()
  const name = String(course.course_name || '').toLowerCase()
  const label = `${code} ${name}`

  if (label.includes('elementary') || label.includes('primary') || label.includes('grade school')) {
    return 'elementary'
  }

  if (label.includes('jhs') || label.includes('junior high')) {
    return 'jhs'
  }

  if (
    label.includes('shs') ||
    label.includes('senior high') ||
    ['stem', 'abm', 'humss', 'gas', 'tvl'].includes(code)
  ) {
    return 'shs'
  }

  if (code.startsWith('bs') || label.includes('college')) {
    return 'college'
  }

  return null
}

function splitFullName(fullName) {
  const parts = String(fullName || '').trim().split(/\s+/).filter(Boolean)
  return {
    fname: parts[0] || '',
    lname: parts.slice(1).join(' ')
  }
}

function getSubjectByCode(subjectCode) {
  return allSubjects.value.find(subject => subject.subject_code === subjectCode)
    || profile.value.subjects.find(subject => subject.subject_code === subjectCode)
}

function syncProfileSubjectsFromCodes(subjectCodes) {
  const existingSubjects = new Map(
    profile.value.subjects.map(subject => [
      subject.subject_code,
      {
        ...subject,
        description: subject.description || ''
      }
    ])
  )

  profile.value.subjects = subjectCodes
    .map(code => {
      const baseSubject = getSubjectByCode(code)

      if (!baseSubject) {
        return null
      }

      return {
        ...baseSubject,
        description: existingSubjects.get(code)?.description || ''
      }
    })
    .filter(Boolean)
    .sort((left, right) => left.subject_name.localeCompare(right.subject_name))
}

// Switching course narrows the year-level options (a college course cannot be Grade 3), so a year
// carried over from the previous course would otherwise stay selected while no longer on screen.
// Guarded against the initial hydration, where the stored course and year arrive as separate
// assignments and must not clear each other.
watch(() => profile.value.course, () => {
  if (isLoadingProfile.value) {
    return
  }

  const stillValid = filteredYearLevels.value.some(
    year => year.value === Number(profile.value.year_level)
  )

  if (!stillValid) {
    profile.value.year_level = null
  }
})

async function openSubjectModal() {
  if (!allSubjects.value.length) {
    await loadSubjects()
  }

  draftSubjectCodes.value = profile.value.subjects.map(subject => subject.subject_code)
  isSubjectModalOpen.value = true
}

function closeSubjectModal() {
  isSubjectModalOpen.value = false
  draftSubjectCodes.value = []
}

function confirmSubjectSelection() {
  syncProfileSubjectsFromCodes(draftSubjectCodes.value)
  closeSubjectModal()
}

function removeSubject(subjectCode) {
  profile.value.subjects = profile.value.subjects.filter(
    subject => subject.subject_code !== subjectCode
  )

  if (openSubjectCode.value === subjectCode) {
    openSubjectCode.value = null
  }
}

function toggleSubjectAccordion(subjectCode) {
  openSubjectCode.value = openSubjectCode.value === subjectCode ? null : subjectCode
}

function incrementRate() {
  profile.value.hourly_rate = Math.min(maxHourlyRate, normalizedRate.value + hourlyRateStep)
}

function decrementRate() {
  profile.value.hourly_rate = Math.max(minHourlyRate, normalizedRate.value - hourlyRateStep)
}

function triggerAvatarUpload() {
  if (!isUploadingAvatar.value) {
    fileInputRef.value?.click()
  }
}

async function handleAvatarUpload(event) {
  const file = event.target.files?.[0]
  event.target.value = ''

  if (!file) {
    return
  }

  if (!file.type.startsWith('image/')) {
    toastStore.push('Please select an image file.', 'error')
    return
  }

  if (file.size > 5 * 1024 * 1024) {
    toastStore.push('Image must be under 5 MB.', 'error')
    return
  }

  const formData = new FormData()
  formData.append('avatar', file)

  try {
    isUploadingAvatar.value = true
    const response = await api.post('/tutor/profile/avatar/', formData)
    profile.value.profile_picture_url = response.data.profile_picture_url || ''
    authStore.patchUserProfile({ profile_picture_url: profile.value.profile_picture_url })
    toastStore.push('Photo updated successfully.')
  } catch (error) {
    console.error('Avatar upload failed:', error)
    toastStore.push(error.response?.data?.error || 'Failed to upload photo.', 'error')
  } finally {
    isUploadingAvatar.value = false
  }
}

async function loadProfile() {
  try {
    isLoadingProfile.value = true
    const profileResponse = await api.get('/tutor/profile/')
    const data = profileResponse.data

    profile.value.fname = data.fname || ''
    profile.value.lname = data.lname || ''
    profile.value.fullName = [data.fname, data.lname].filter(Boolean).join(' ')
    profile.value.email = data.email || ''
    profile.value.course = data.course || ''
    profile.value.year_level = data.year_level || null
    profile.value.bio = data.bio || ''
    profile.value.hourly_rate = data.hourly_rate || minHourlyRate
    profile.value.teaching_level = data.teaching_level || 'College'
    profile.value.can_online = Boolean(data.can_online)
    profile.value.can_f2f = Boolean(data.can_f2f)
    profile.value.response_time = data.response_time || 'within_a_day'
    profile.value.profile_picture_url = data.profile_picture_url || ''

    const subjectResponse = await api.get('/tutor/subjects/')
    profile.value.subjects = subjectResponse.data.map(subject => ({
      ...subject,
      description: subject.description || ''
    }))

    initialSubjectCodes.value = profile.value.subjects.map(subject => subject.subject_code)
    initialSubjectDescriptions.value = new Map(
      profile.value.subjects.map(subject => [subject.subject_code, subject.description || ''])
    )
  } catch (error) {
    console.error('Failed to load tutor profile:', error)
    toastStore.push('Failed to load profile.', 'error')
  } finally {
    isLoadingProfile.value = false
  }
}

async function loadSubjects() {
  if (isLoadingSubjects.value) {
    return
  }

  isLoadingSubjects.value = true
  subjectsLoadError.value = ''

  try {
    allSubjects.value = await catalogStore.fetchSubjects()
  } catch (error) {
    console.error('Failed to load subjects:', error)
    subjectsLoadError.value = 'Could not load subjects right now.'
  } finally {
    isLoadingSubjects.value = false
  }
}

async function loadCourses() {
  try {
    courses.value = await catalogStore.fetchCourses()
  } catch (error) {
    console.error('Failed to load courses:', error)
    toastStore.push('Failed to load courses.', 'error')
  }
}

async function syncSubjects() {
  const currentSubjects = profile.value.subjects.map(subject => ({
    ...subject,
    description: subject.description || ''
  }))
  const currentSubjectCodes = currentSubjects.map(subject => subject.subject_code)
  const addedCodes = currentSubjectCodes.filter(code => !initialSubjectCodes.value.includes(code))
  const removedCodes = initialSubjectCodes.value.filter(code => !currentSubjectCodes.includes(code))
  const changedDescriptions = currentSubjects.filter(subject => {
    if (addedCodes.includes(subject.subject_code)) {
      return false
    }

    return (initialSubjectDescriptions.value.get(subject.subject_code) || '') !== (subject.description || '')
  })

  await Promise.all([
    ...addedCodes.map(subjectCode => {
      const subject = currentSubjects.find(item => item.subject_code === subjectCode)

      return api.post('/tutor/subjects/add/', {
        subject_code: subjectCode,
        description: subject?.description || ''
      })
    }),
    ...changedDescriptions.map(subject =>
      api.patch(`/tutor/subjects/update/${subject.subject_code}/`, {
        description: subject.description || ''
      })
    ),
    ...removedCodes.map(subjectCode =>
      api.delete(`/tutor/subjects/remove/${subjectCode}/`)
    )
  ])

  initialSubjectCodes.value = [...currentSubjectCodes]
  initialSubjectDescriptions.value = new Map(
    currentSubjects.map(subject => [subject.subject_code, subject.description || ''])
  )
}

async function saveProfile() {
  if (isSavingProfile.value) {
    return
  }

  const names = splitFullName(profile.value.fullName)
  const profilePayload = {
    fname: names.fname,
    lname: names.lname,
    course: profile.value.course,
    year_level: profile.value.year_level,
    bio: profile.value.bio || ''
  }

  const tutorPayload = {
    hourly_rate: normalizedRate.value,
    teaching_level: profile.value.teaching_level,
    can_online: profile.value.can_online,
    can_f2f: profile.value.can_f2f,
    response_time: profile.value.response_time || null
  }

  try {
    isSavingProfile.value = true
    await api.put('/tutee/profile/update/', profilePayload)
    await api.put('/tutor/update/', tutorPayload)
    await syncSubjects()
    authStore.patchUserProfile({ fname: names.fname, lname: names.lname })
    toastStore.push('Profile updated successfully.')
    await loadProfile()
  } catch (error) {
    console.error('Profile update failed:', error)
    toastStore.push(error.response?.data?.error || 'Profile update failed. Please try again.', 'error')
  } finally {
    isSavingProfile.value = false
  }
}

async function discardChanges() {
  await loadProfile()
  toastStore.push('Changes discarded.')
}

function goToSchedule() {
  router.push('/tch-availability')
}

onMounted(() => {
  loadProfile()
  loadSubjects()
  loadCourses()
  if (!profileStore.loaded) profileStore.checkProfileStatus()
})
</script>

<style scoped>
.tutor-profile-shell {
  --sb-dark: #0a1916;
  --sb-ink: var(--sb-text-main);
  --sb-muted: var(--sb-text-muted);
  --sb-divider: var(--sb-card-border);
  --sb-green-tint: color-mix(in srgb, var(--sb-primary) 10%, transparent);
  --sb-green-border: color-mix(in srgb, var(--sb-primary) 28%, var(--sb-card-border));
  position: relative;
  min-height: 100vh;
  padding: 2rem;
  overflow: hidden;
  color: var(--sb-ink);
  font-family: var(--sb-font-base);
  background: transparent;
}

.profile-content {
  position: relative;
  z-index: 1;
  display: grid;
  gap: 1.25rem;
  max-width: 1180px;
  margin: 0 auto;
}

/* A global .glass-segment also lives in src/assets/main.css (same rules, kept in
   sync manually) so the session detail pages can share this look. Scoped wins
   here on specificity, but update both if this changes. */
.glass-segment {
  background: color-mix(in srgb, var(--sb-card-bg) 84%, transparent);
  border: 1px solid color-mix(in srgb, var(--sb-card-border) 82%, transparent);
  border-radius: 24px;
  box-shadow: 0 24px 70px rgba(15, 23, 42, 0.1);
  padding: 1.5rem;
}

.profile-header-segment {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  background: linear-gradient(135deg, rgba(10, 25, 22, 0.94), rgba(0, 137, 90, 0.86));
  color: #fff;
}

.header-left,
.header-actions,
.segment-header,
.profile-actions,
.modal-header-row,
.modal-footer-actions,
.subject-modal-footer {
  display: flex;
  align-items: center;
}

.header-left {
  gap: 1rem;
  min-width: 0;
}

.avatar-wrapper {
  position: relative;
  width: 104px;
  height: 104px;
  flex: 0 0 auto;
  padding: 0;
  border: 0;
  border-radius: 999px;
  background: transparent;
}

.avatar-img,
.initials-avatar {
  width: 104px;
  height: 104px;
  border: 4px solid rgba(255, 255, 255, 0.42);
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  object-fit: cover;
}

.initials-avatar {
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
  font-size: 1.7rem;
  font-weight: 800;
}

.avatar-camera-overlay {
  position: absolute;
  right: 4px;
  bottom: 6px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border: 2px solid #fff;
  border-radius: 999px;
  background: var(--sb-primary);
  color: #fff;
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.18);
}

.header-info {
  min-width: 0;
}

.header-kicker,
.modal-kicker {
  margin: 0 0 0.25rem;
  color: rgba(255, 255, 255, 0.74);
  font-size: 0.74rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0;
}

.profile-name {
  margin: 0;
  color: #fff;
  font-size: 2rem;
  font-weight: 800;
  line-height: 1.1;
}

.header-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.65rem;
}

.role-badge,
.verified-badge,
.subject-counter {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 700;
}

.role-badge,
.verified-badge {
  padding: 0.38rem 0.7rem;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.22);
  color: #fff;
}

.header-actions {
  justify-content: flex-end;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.sb-btn {
  border-radius: 12px;
}

/* .btn-soft and .btn-primary-action also exist globally in src/assets/main.css
   for the session detail pages. Scoped wins here on specificity, but a rename
   or restyle of either tier should be applied in both places. */
.btn-soft,
.btn-primary-action,
.btn-save,
.btn-discard,
.btn-confirm,
.btn-ghost-sm {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  border: 0;
  font-weight: 800;
}

.btn-soft {
  padding: 0.72rem 1rem;
  color: #fff;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.25);
}

.btn-soft:hover {
  background: rgba(255, 255, 255, 0.22);
}

.btn-primary-action,
.btn-save,
.btn-confirm {
  color: #fff;
  background: var(--sb-primary);
  box-shadow: 0 12px 24px rgba(0, 137, 90, 0.22);
}

.btn-primary-action {
  padding: 0.74rem 1.1rem;
}

.btn-primary-action:hover,
.btn-save:hover,
.btn-confirm:hover {
  background: var(--sb-primary-hover);
  color: #fff;
}

.profile-grid {
  display: grid;
  grid-template-columns: minmax(0, 0.92fr) minmax(0, 1.08fr);
  gap: 1.25rem;
}

.profile-col {
  display: grid;
  align-content: start;
  gap: 1.25rem;
}

.segment-header {
  gap: 0.8rem;
  margin-bottom: 1.25rem;
}

.segment-header-with-action {
  align-items: flex-start;
}

.segment-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  flex: 0 0 auto;
  border-radius: 14px;
  background: var(--sb-green-tint);
  color: var(--sb-primary);
  border: 1px solid var(--sb-green-border);
}

.segment-title {
  margin: 0;
  color: #10231d;
  font-size: 1.05rem;
  font-weight: 800;
  line-height: 1.25;
}

.segment-copy {
  margin: 0.18rem 0 0;
  color: #64748b;
  font-size: 0.86rem;
}

.subject-counter {
  margin-left: auto;
  padding: 0.3rem 0.6rem;
  color: var(--sb-primary);
  background: var(--sb-green-tint);
  border: 1px solid var(--sb-green-border);
}

/* At the cap the counter is the explanation for the disabled Add Subject button, so it needs to
   read as a stop rather than as a neutral tally. */
.subject-counter-full {
  color: var(--sb-pop-orange-deep);
  background: color-mix(in srgb, var(--sb-pop-orange-deep) 10%, transparent);
  border-color: color-mix(in srgb, var(--sb-pop-orange-deep) 35%, transparent);
}

.limit-notice {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0.6rem 0 0;
  padding: 0.6rem 0.85rem;
  border-radius: 12px;
  border: 1px solid color-mix(in srgb, var(--sb-pop-orange-deep) 30%, transparent);
  background: color-mix(in srgb, var(--sb-pop-orange-deep) 8%, transparent);
  color: var(--sb-text-main);
  font-size: 0.85rem;
}

.subject-add-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.field-group {
  display: grid;
  gap: 1.1rem;
}

.field {
  display: grid;
  gap: 0.45rem;
}

.field-row-2 {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.field-label,
.subject-accordion-label {
  color: #64748b;
  font-size: 0.74rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0;
}

.input-glass {
  width: 100%;
  border: 1.5px solid #dbe7e1;
  border-radius: 14px;
  background: rgba(248, 250, 252, 0.78);
  color: #0f172a;
  font-size: 0.94rem;
  padding: 0.75rem 0.9rem;
  transition: none;
}

.input-glass:focus {
  outline: none;
  background: #fff;
  border-color: var(--sb-primary);
  box-shadow: var(--sb-halo);
}

.input-disabled {
  opacity: 0.68;
}

.teaching-level-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
}

.teaching-card {
  display: grid;
  place-items: center;
  gap: 0.45rem;
  min-height: 112px;
  border: 1.5px solid #dbe7e1;
  background: rgba(248, 250, 252, 0.76);
  color: #64748b;
  padding: 1rem 0.5rem;
  text-align: center;
}

.teaching-card:hover,
.teaching-card-active {
  border-color: var(--sb-primary);
  background: rgba(0, 137, 90, 0.08);
  color: var(--sb-primary);
}

.teaching-card-icon {
  font-size: 1.55rem;
}

.teaching-card-label {
  font-size: 0.78rem;
  font-weight: 850;
}

.rate-stepper {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr) 42px;
  align-items: center;
  gap: 0.75rem;
  border: 1.5px solid rgba(0, 137, 90, 0.18);
  border-radius: 16px;
  background: rgba(0, 137, 90, 0.06);
  padding: 0.6rem;
}

.stepper-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border: 1px solid #dbe7e1;
  background: #fff;
  color: var(--sb-primary);
}

.stepper-btn:hover:not(:disabled) {
  color: #fff;
  background: var(--sb-primary);
  border-color: var(--sb-primary);
}

.rate-display {
  min-width: 0;
  color: var(--sb-primary);
  font-size: 1.35rem;
  font-weight: 850;
  text-align: center;
}

.response-pills {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.55rem;
}

.response-pill {
  min-height: 44px;
  border: 1.5px solid #dbe7e1;
  background: rgba(248, 250, 252, 0.78);
  color: #556a61;
  font-size: 0.82rem;
  font-weight: 800;
  padding: 0.55rem 0.4rem;
}

.response-pill:hover,
.response-pill-active {
  border-color: var(--sb-primary);
  background: var(--sb-primary);
  color: #fff;
}

.specializations-segment {
  min-height: 100%;
}

.subject-pill-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
}

.subject-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  max-width: 100%;
  padding: 0.42rem 0.54rem 0.42rem 0.75rem;
  border-radius: 999px;
  background: var(--sb-primary);
  color: #fff;
  font-size: 0.84rem;
  font-weight: 800;
}

.subject-pill-remove {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border: 0;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.16);
  color: #fff;
  padding: 0;
}

.subject-add-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  border: 1.5px dashed rgba(0, 137, 90, 0.42);
  background: transparent;
  color: var(--sb-primary);
  font-weight: 800;
  padding: 0.48rem 0.78rem;
}

.subject-add-btn:hover {
  background: rgba(0, 137, 90, 0.06);
  border-style: solid;
}

.empty-note {
  margin: 0;
  color: #7b8b84;
  font-size: 0.88rem;
}

.field-hint {
  margin: 0.4rem 0 0;
  color: #7b8b84;
  font-size: 0.82rem;
}

.bio-textarea {
  min-height: 132px;
  resize: vertical;
}

.bio-near-limit {
  border-color: #f59e0b;
}

.bio-at-limit {
  border-color: #dc3545;
  box-shadow: 0 0 0 4px rgba(220, 53, 69, 0.12);
}

.bio-counter {
  justify-self: end;
  margin-top: -0.2rem;
  color: #8a9a93;
  font-size: 0.78rem;
  font-weight: 700;
}

.bio-counter-warn {
  color: #dc3545;
}

.session-mode-group {
  display: grid;
  gap: 0.7rem;
}

.mode-card-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
}

.mode-check {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin: 0;
  min-height: 112px;
  padding: 1rem;
  border: 1px solid rgba(188, 206, 198, 0.86);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.68);
  box-shadow: 0 14px 34px rgba(15, 23, 42, 0.07);
  cursor: pointer;
  transition: transform var(--sb-t-normal) var(--sb-spring);
}

.mode-check:hover {
  border-color: rgba(0, 137, 90, 0.42);
  background: rgba(255, 255, 255, 0.86);
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.1);
}

.mode-check-active {
  border-color: rgba(0, 137, 90, 0.62);
  background:
    linear-gradient(135deg, rgba(0, 137, 90, 0.14), rgba(255, 255, 255, 0.88));
  box-shadow: 0 18px 42px rgba(0, 137, 90, 0.14);
}

.mode-checkbox {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
}

.mode-copy {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  min-width: 0;
  color: #334155;
}

.mode-icon,
.mode-checkmark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
}

.mode-icon {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  background: rgba(0, 137, 90, 0.1);
  color: var(--sb-primary);
  font-size: 1.25rem;
}

.mode-title,
.mode-subtitle {
  display: block;
}

.mode-title {
  color: #17251f;
  font-size: 0.98rem;
  font-weight: 850;
}

.mode-subtitle {
  margin-top: 0.18rem;
  color: #66756e;
  font-size: 0.78rem;
  font-weight: 650;
  line-height: 1.35;
}

.mode-checkmark {
  color: #9aaba3;
  font-size: 1.15rem;
}

.mode-check-active .mode-icon {
  background: var(--sb-primary);
  color: #fff;
}

.mode-check-active .mode-checkmark {
  color: var(--sb-primary);
}

.subject-accordion-list {
  display: grid;
  gap: 0.75rem;
  margin-top: 1.25rem;
}

.subject-accordion-card {
  border: 1px solid #dbe7e1;
  border-radius: 18px;
  background: rgba(246, 248, 247, 0.9);
  overflow: hidden;
  transition: none;
}

.subject-accordion-card-open {
  border-color: #9fd0ba;
  background: #eef7f3;
  box-shadow: 0 12px 28px rgba(10, 122, 81, 0.08);
}

.subject-accordion-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  border: 0;
  background: transparent;
  padding: 0.9rem 1rem;
  text-align: left;
}

.subject-accordion-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  flex: 0 0 auto;
  border-radius: 999px;
  background: #dfe5e2;
  color: #65756d;
  transition: none;
}

.subject-accordion-icon-open {
  color: #fff;
  background: var(--sb-primary);
}

.subject-accordion-title {
  min-width: 0;
  color: #1f2f2a;
  font-size: 0.95rem;
  font-weight: 800;
}

.subject-accordion-title-open {
  color: var(--sb-primary);
}

.subject-accordion-chevron {
  color: #5d7168;
}

.subject-accordion-body {
  display: grid;
  gap: 0.55rem;
  padding: 0 1rem 1rem;
  overflow: hidden;
}

.sb-accordion-enter-active,
.sb-accordion-leave-active {
  transition:
    opacity var(--sb-t-normal) var(--sb-spring),
    transform var(--sb-t-normal) var(--sb-spring);
}

.sb-accordion-enter-from,
.sb-accordion-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.subject-description-input {
  width: 100%;
  min-height: 112px;
  border: 0;
  border-radius: 14px;
  background: #fff;
  color: #183129;
  padding: 0.8rem 0.9rem;
  resize: vertical;
  box-shadow: inset 0 0 0 1px rgba(224, 231, 227, 0.9);
}

.subject-description-input:focus {
  outline: none;
  box-shadow: var(--sb-halo);
}

.actions-segment {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.profile-actions {
  justify-content: flex-end;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn-discard {
  padding: 0.75rem 1.1rem;
  border: 1.5px solid #dbe7e1;
  background: rgba(255, 255, 255, 0.72);
  color: #4b655b;
}

.btn-discard:hover {
  background: #fff;
  border-color: #b9c7c1;
}

.btn-save {
  min-width: 138px;
  padding: 0.78rem 1.25rem;
}

.modal-backdrop-soft {
  display: grid;
  place-items: center;
  padding: 1.5rem;
  background: rgba(15, 23, 42, 0.46);
}

.glass-modal {
  position: relative;
  z-index: var(--sb-z-surface);
  width: min(100%, 680px);
  max-height: min(86vh, 780px);
  display: grid;
  gap: 1.1rem;
  overflow: auto;
  border: 1px solid rgba(255, 255, 255, 0.92);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 28px 90px rgba(15, 23, 42, 0.26);
  padding: 1.5rem;
}

.modal-header-row {
  justify-content: space-between;
  gap: 1rem;
}

.modal-kicker {
  color: var(--sb-primary);
}

.modal-title {
  margin: 0;
  color: #10231d;
  font-size: 1.25rem;
  font-weight: 850;
}

.modal-close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  flex: 0 0 auto;
  border: 1px solid #dbe7e1;
  background: #fff;
  color: #526960;
}

.year-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.5rem;
}

.year-btn {
  min-height: 42px;
  border: 1.5px solid #dbe7e1;
  background: rgba(248, 250, 252, 0.82);
  color: #334155;
  font-size: 0.8rem;
  font-weight: 800;
  padding: 0.5rem 0.3rem;
}

.year-btn:hover,
.year-btn-active {
  border-color: var(--sb-primary);
  background: var(--sb-primary);
  color: #fff;
}

.subject-modal {
  width: min(100%, 720px);
}

.subject-modal-list {
  display: grid;
  gap: 0.55rem;
  max-height: 370px;
  overflow: auto;
  padding-right: 0.15rem;
}

.modal-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  min-height: 112px;
  color: #64748b;
  text-align: center;
}

.modal-error {
  color: #dc3545;
}

.subject-modal-footer {
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.selected-count {
  color: #64748b;
  font-size: 0.86rem;
  font-weight: 750;
}

.modal-footer-actions {
  justify-content: flex-end;
  gap: 0.75rem;
}

.mb-0 {
  margin-bottom: 0;
}

@media (max-width: 991px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }

  .profile-header-segment,
  .actions-segment {
    align-items: flex-start;
    flex-direction: column;
  }

  .header-actions,
  .profile-actions {
    width: 100%;
    justify-content: flex-start;
  }
}

@media (max-width: 640px) {
  .tutor-profile-shell {
    padding: 1rem;
  }

  .glass-segment,
  .glass-modal {
    border-radius: 18px;
    padding: 1rem;
  }

  .header-left {
    align-items: flex-start;
    flex-direction: column;
  }

  .avatar-wrapper,
  .avatar-img,
  .initials-avatar {
    width: 88px;
    height: 88px;
  }

  .profile-name {
    font-size: 1.55rem;
  }

  .header-actions,
  .profile-actions,
  .modal-footer-actions {
    align-items: stretch;
    flex-direction: column;
  }

  .btn-soft,
  .btn-primary-action,
  .btn-discard,
  .btn-save,
  .btn-ghost-sm,
  .btn-confirm {
    width: 100%;
  }

  .field-row-2,
  .mode-card-grid,
  .teaching-level-grid,
  .response-pills,
  .year-grid {
    grid-template-columns: 1fr;
  }

  .rate-display {
    font-size: 1.05rem;
  }
}
</style>
