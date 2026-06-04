<template>
  <div class="tutee-profile-shell">
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
            <p class="header-kicker">Tutee Profile</p>
            <h1 class="profile-name">{{ fullName || 'Your Name' }}</h1>
            <div class="header-badges">
              <span class="role-badge">
                <i class="bi bi-mortarboard-fill"></i>
                Student
              </span>
              <span v-if="lastUpdated" class="verified-badge">
                <i class="bi bi-clock-history"></i>
                Updated {{ lastUpdated }}
              </span>
            </div>
          </div>
        </div>

        <div class="header-actions">
          <button type="button" class="btn-soft sb-btn" @click="discardChanges">
            <i class="bi bi-arrow-counterclockwise"></i>
            Discard
          </button>
          <button type="submit" class="btn-primary-action sb-btn" :disabled="isSavingProfile || isLoadingProfile">
            <span
              v-if="isSavingProfile"
              class="spinner-border spinner-border-sm"
              aria-hidden="true"
            ></span>
            {{ isSavingProfile ? 'Saving' : 'Save Profile' }}
          </button>
        </div>
      </header>

      <main class="profile-grid">
        <div class="profile-col">
          <section class="glass-segment">
            <div class="segment-header">
              <span class="segment-icon"><i class="bi bi-person-fill"></i></span>
              <div>
                <h2 class="segment-title">Identity Details</h2>
                <p class="segment-copy">Keep your student profile current for tutors.</p>
              </div>
            </div>

            <div class="field-group">
              <div class="field-row-2">
                <label class="field">
                  <span class="field-label">First Name</span>
                  <input
                    v-model.trim="profile.fname"
                    type="text"
                    class="input-glass"
                    placeholder="First name"
                  >
                </label>

                <label class="field">
                  <span class="field-label">Last Name</span>
                  <input
                    v-model.trim="profile.lname"
                    type="text"
                    class="input-glass"
                    placeholder="Last name"
                  >
                </label>
              </div>

              <label class="field">
                <span class="field-label">Middle Name</span>
                <input
                  v-model.trim="profile.mname"
                  type="text"
                  class="input-glass"
                  placeholder="Optional"
                >
              </label>

              <label class="field">
                <span class="field-label">University Email</span>
                <input
                  :value="profile.email"
                  type="email"
                  class="input-glass input-disabled"
                  disabled
                >
              </label>
            </div>
          </section>

          <section class="glass-segment">
            <div class="segment-header">
              <span class="segment-icon"><i class="bi bi-backpack-fill"></i></span>
              <div>
                <h2 class="segment-title">Academic Context</h2>
                <p class="segment-copy">Set the level tutors should use when matching support.</p>
              </div>
            </div>

            <div class="field-group">
              <div class="academic-summary-grid">
                <div class="summary-chip">
                  <span class="summary-label">Level</span>
                  <span class="summary-value">{{ currentEducationLevelLabel }}</span>
                </div>
                <div class="summary-chip">
                  <span class="summary-label">Year</span>
                  <span class="summary-value">{{ currentYearLabel }}</span>
                </div>
              </div>

              <div class="course-year-display">
                <span class="course-chip" :class="{ 'chip-unset': !profile.course || !shouldShowCourse }">
                  {{ currentCourseLabel }}
                </span>
                <button type="button" class="change-btn sb-btn" @click="openAcademicModal">
                  Change
                  <i class="bi bi-arrow-right-short"></i>
                </button>
              </div>
            </div>
          </section>
        </div>

        <div class="profile-col">
          <section class="glass-segment preferences-segment">
            <div class="segment-header segment-header-with-action">
              <span class="segment-icon"><i class="bi bi-stars"></i></span>
              <div>
                <h2 class="segment-title">Learning Preferences</h2>
                <p class="segment-copy">Pick the subjects where you want tutoring support.</p>
              </div>
              <span class="subject-counter">{{ profile.subjects.length }}</span>
            </div>

            <div class="field-group">
              <div class="subject-pill-row">
                <span
                  v-for="subject in selectedSubjectObjects"
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

                <button type="button" class="subject-add-btn sb-btn" @click="openSubjectModal">
                  <i class="bi bi-plus-lg"></i>
                  Edit Subjects
                </button>
              </div>

              <p v-if="!selectedSubjectObjects.length" class="empty-note">
                No preferred subjects selected yet.
              </p>

              <label class="field">
                <span class="field-label">Bio</span>
                <textarea
                  v-model="profile.bio"
                  class="input-glass bio-textarea"
                  :class="{ 'bio-near-limit': bioCharCount > 450, 'bio-at-limit': bioCharCount >= 500 }"
                  maxlength="500"
                  rows="5"
                  placeholder="Tell tutors about your learning style, goals, and what kind of support helps you most."
                ></textarea>
                <span class="bio-counter" :class="{ 'bio-counter-warn': bioCharCount > 450 }">
                  {{ bioCharCount }}/500
                </span>
              </label>
            </div>
          </section>

          <section class="glass-segment actions-segment">
            <div>
              <h2 class="segment-title">Profile Changes</h2>
              <p class="segment-copy mb-0">
                Save once your academic details and learning preferences are ready.
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
                class="btn-save sb-btn"
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

    <div
      v-if="isAcademicModalOpen"
      class="modal-backdrop-soft"
      role="presentation"
      @click.self="closeAcademicModal"
    >
      <section
        class="glass-modal academic-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="academic-modal-title"
      >
        <div class="modal-header-row">
          <div>
            <p class="modal-kicker">Academic Context</p>
            <h2 id="academic-modal-title" class="modal-title">Level, Course, and Year</h2>
          </div>
          <button type="button" class="modal-close sb-btn" aria-label="Close" @click="closeAcademicModal">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <div class="modal-section">
          <p class="modal-section-label">Education Level</p>
          <div class="education-grid">
            <button
              v-for="level in educationLevels"
              :key="level.value"
              type="button"
              class="education-card sb-btn"
              :class="{ 'education-card-active': draftEducationLevel === level.value }"
              @click="setDraftEducationLevel(level.value)"
            >
              <i :class="['bi', level.icon, 'education-card-icon']"></i>
              <span class="education-card-label">{{ level.label }}</span>
              <span class="education-card-meta">{{ level.meta }}</span>
            </button>
          </div>
        </div>

        <div v-if="draftShouldShowCourse" class="modal-section">
          <p class="modal-section-label">{{ draftEducationLevel === 'college' ? 'Course' : 'Strand' }}</p>
          <div class="course-grid">
            <button
              v-for="course in filteredDraftCourses"
              :key="course.course_code"
              type="button"
              class="course-card sb-btn"
              :class="{ 'course-card-active': draftCourse === course.course_code }"
              @click="draftCourse = course.course_code"
            >
              <span class="course-card-code">{{ course.course_code }}</span>
              <span class="course-card-name">{{ course.course_name }}</span>
            </button>

            <p v-if="!filteredDraftCourses.length" class="empty-note modal-empty">
              Options are not available right now.
            </p>
          </div>
        </div>

        <div class="modal-section">
          <p class="modal-section-label">Year Level</p>
          <div class="year-grid">
            <button
              v-for="year in draftYearOptions"
              :key="year.value"
              type="button"
              class="year-btn sb-btn"
              :class="{ 'year-btn-active': Number(draftYearLevel) === year.value }"
              @click="draftYearLevel = year.value"
            >
              {{ year.label }}
            </button>
          </div>
        </div>

        <div class="modal-footer-row">
          <button type="button" class="btn-ghost-sm sb-btn" @click="closeAcademicModal">
            Cancel
          </button>
          <button type="button" class="btn-confirm sb-btn" @click="confirmAcademicSelection">
            Confirm
          </button>
        </div>
      </section>
    </div>

    <div
      v-if="isSubjectModalOpen"
      class="modal-backdrop-soft"
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
            <p class="modal-kicker">Learning Preferences</p>
            <h2 id="subject-modal-title" class="modal-title">Choose Subjects</h2>
          </div>
          <button type="button" class="modal-close sb-btn" aria-label="Close" @click="closeSubjectModal">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <label class="field">
          <span class="field-label">Search Subjects</span>
          <input
            v-model.trim="subjectSearch"
            type="text"
            class="input-glass"
            placeholder="Search by subject name or code"
          >
        </label>

        <div class="modal-section">
          <p class="modal-section-label">Subject Groups</p>
          <div class="category-pills">
            <button
              v-for="category in availableCategories"
              :key="category"
              type="button"
              class="category-pill sb-btn"
              :class="{ active: activeCategory === category }"
              @click="activeCategory = category"
            >
              {{ category }}
            </button>
          </div>
        </div>

        <div class="subject-modal-list">
          <div v-if="isLoadingSubjects" class="modal-status">
            <span class="spinner-border spinner-border-sm" aria-hidden="true"></span>
            Loading subjects
          </div>
          <template v-else>
            <section
              v-for="section in groupedSubjectSections"
              :key="section.name"
              class="subject-group-section"
            >
              <div class="subject-group-header">
                <span>{{ section.name }}</span>
                <span>{{ section.subjects.length }}</span>
              </div>

              <button
                v-for="subject in section.subjects"
                :key="subject.subject_code"
                type="button"
                class="subject-option sb-btn"
                :class="{ selected: isDraftSelected(subject.subject_code) }"
                @click="toggleDraftSubject(subject.subject_code)"
              >
                <span class="subject-option-copy">
                  <span class="subject-option-name">{{ subject.subject_name }}</span>
                  <span class="subject-option-meta">
                    {{ subject.subject_code }} - {{ getSubjectGroup(subject) }}
                  </span>
                </span>
                <span class="subject-option-check" aria-hidden="true">
                  <i
                    class="bi"
                    :class="isDraftSelected(subject.subject_code) ? 'bi-check-circle-fill' : 'bi-circle'"
                  ></i>
                </span>
              </button>
            </section>

            <div v-if="!filteredSubjects.length" class="modal-status">
              No subjects match your filters.
            </div>
          </template>
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
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useSubjectCatalog } from '@/composables/useSubjectCatalog'
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
  profile_picture_url: '',
  subjects: [],
  updated_at: null
})

const courses = ref([])
const subjects = ref([])
const educationLevel = ref('college')
const fileInputRef = ref(null)
const avatarLoadError = ref(false)
const isLoadingProfile = ref(false)
const isSavingProfile = ref(false)
const isUploadingAvatar = ref(false)
const isAcademicModalOpen = ref(false)
const isSubjectModalOpen = ref(false)
const isLoadingSubjects = ref(false)
const subjectSearch = ref('')
const activeCategory = ref('All')
const draftEducationLevel = ref('college')
const draftYearLevel = ref(null)
const draftCourse = ref('')
const draftSubjectCodes = ref([])

const educationLevels = [
  { label: 'Elementary', value: 'elementary', icon: 'bi-pencil-fill', meta: 'Grade 1-6' },
  { label: 'JHS', value: 'jhs', icon: 'bi-book-fill', meta: 'Grade 7-10' },
  { label: 'SHS', value: 'shs', icon: 'bi-journal-bookmark-fill', meta: 'Grade 11-12' },
  { label: 'College', value: 'college', icon: 'bi-mortarboard-fill', meta: '1st-4th Year' }
]

const yearLevels = [
  { label: 'Grade 1', value: 1, level: 'elementary' },
  { label: 'Grade 2', value: 2, level: 'elementary' },
  { label: 'Grade 3', value: 3, level: 'elementary' },
  { label: 'Grade 4', value: 4, level: 'elementary' },
  { label: 'Grade 5', value: 5, level: 'elementary' },
  { label: 'Grade 6', value: 6, level: 'elementary' },
  { label: 'Grade 7', value: 7, level: 'jhs' },
  { label: 'Grade 8', value: 8, level: 'jhs' },
  { label: 'Grade 9', value: 9, level: 'jhs' },
  { label: 'Grade 10', value: 10, level: 'jhs' },
  { label: 'Grade 11', value: 11, level: 'shs' },
  { label: 'Grade 12', value: 12, level: 'shs' },
  { label: '1st Year', value: 13, level: 'college' },
  { label: '2nd Year', value: 14, level: 'college' },
  { label: '3rd Year', value: 15, level: 'college' },
  { label: '4th Year', value: 16, level: 'college' }
]

watch(
  () => profile.value.profile_picture_url,
  () => {
    avatarLoadError.value = false
  }
)

const fullName = computed(() =>
  [profile.value.fname, profile.value.lname].filter(Boolean).join(' ')
)

const avatarUrl = computed(() => profile.value.profile_picture_url || '')

const initials = computed(() => {
  const first = profile.value.fname?.charAt(0) || ''
  const last = profile.value.lname?.charAt(0) || ''
  return `${first}${last}`.toUpperCase()
})

const bioCharCount = computed(() => profile.value.bio?.length || 0)

const shouldShowCourse = computed(() =>
  educationLevel.value === 'shs' || educationLevel.value === 'college'
)

const draftShouldShowCourse = computed(() =>
  draftEducationLevel.value === 'shs' || draftEducationLevel.value === 'college'
)

const currentEducationLevelLabel = computed(() => {
  const level = educationLevels.find(item => item.value === educationLevel.value)
  return level?.label || 'Select level'
})

const currentYearLabel = computed(() => {
  const year = yearLevels.find(item => item.value === Number(profile.value.year_level))
  return year?.label || 'Select year'
})

const currentCourseLabel = computed(() => {
  if (!shouldShowCourse.value) {
    return 'No course needed'
  }

  if (!profile.value.course) {
    return educationLevel.value === 'college' ? 'Select course' : 'Select strand'
  }

  const course = courses.value.find(item => item.course_code === profile.value.course)
  return course ? `${course.course_code} - ${course.course_name}` : profile.value.course
})

const selectedDraftCourse = computed(() =>
  courses.value.find(course => course.course_code === draftCourse.value)
)

const draftYearLevelSource = computed(() =>
  getCourseEducationLevel(selectedDraftCourse.value) || draftEducationLevel.value
)

const draftYearOptions = computed(() =>
  yearLevels.filter(year => year.level === draftYearLevelSource.value)
)

const filteredDraftCourses = computed(() =>
  courses.value.filter(course => {
    const courseLevel = getCourseEducationLevel(course)

    if (draftEducationLevel.value === 'college') {
      return courseLevel === 'college' || courseLevel === null
    }

    return courseLevel === draftEducationLevel.value
  })
)

const selectedCourseCode = computed(() => profile.value.course)

const profileSubjectCodes = computed({
  get: () => profile.value.subjects,
  set: value => {
    profile.value.subjects = value
  }
})

const {
  availableCategories,
  filteredSubjects,
  groupedSubjectSections,
  selectedSubjectObjects,
  getPreferredSubjectCategory,
  getSubjectGroup,
  pruneSubjectsForCurrentLevel,
  refreshSubjectFilterForAcademicContext
} = useSubjectCatalog({
  subjects,
  courses,
  educationLevel,
  selectedCourseCode,
  subjectSearch,
  activeCategory,
  selectedSubjectCodes: profileSubjectCodes,
  draftSubjectCodes,
  isSubjectModalOpen
})

const selectedDraftCountLabel = computed(() => {
  const count = draftSubjectCodes.value.length
  return `${count} subject${count === 1 ? '' : 's'} selected`
})

const lastUpdated = computed(() => {
  if (!profile.value.updated_at) {
    return null
  }

  return new Date(profile.value.updated_at).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
})

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

function deriveEducationLevel(yearLevel) {
  const value = Number(yearLevel)

  if (value >= 1 && value <= 6) {
    return 'elementary'
  }

  if (value >= 7 && value <= 10) {
    return 'jhs'
  }

  if (value >= 11 && value <= 12) {
    return 'shs'
  }

  return 'college'
}

function setDraftEducationLevel(level) {
  draftEducationLevel.value = level

  if (level !== 'shs' && level !== 'college') {
    draftCourse.value = ''
  } else {
    alignDraftCourseWithLevel()
  }

  alignDraftYearWithLevel()
}

function alignDraftYearWithLevel() {
  const options = draftYearOptions.value

  if (!options.length) {
    return
  }

  const currentYear = Number(draftYearLevel.value)
  const hasCurrentYear = options.some(year => year.value === currentYear)

  if (!hasCurrentYear) {
    draftYearLevel.value = options[0].value
  }
}

function alignDraftCourseWithLevel() {
  if (!draftShouldShowCourse.value) {
    draftCourse.value = ''
    return
  }

  if (!filteredDraftCourses.value.length) {
    draftCourse.value = ''
    return
  }

  const hasCurrentCourse = filteredDraftCourses.value.some(
    course => course.course_code === draftCourse.value
  )

  if (!hasCurrentCourse) {
    draftCourse.value = filteredDraftCourses.value[0].course_code
  }
}

function openAcademicModal() {
  draftEducationLevel.value = educationLevel.value
  draftYearLevel.value = profile.value.year_level || null
  draftCourse.value = profile.value.course || ''
  isAcademicModalOpen.value = true
  alignDraftCourseWithLevel()
  alignDraftYearWithLevel()
}

function closeAcademicModal() {
  isAcademicModalOpen.value = false
}

function confirmAcademicSelection() {
  educationLevel.value = draftEducationLevel.value
  profile.value.year_level = draftYearLevel.value
  profile.value.course = draftShouldShowCourse.value ? draftCourse.value : ''
  pruneSubjectsForCurrentLevel()
  refreshSubjectFilterForAcademicContext({ preferRecommended: true })
  closeAcademicModal()
}

function openSubjectModal() {
  draftSubjectCodes.value = [...profile.value.subjects]
  subjectSearch.value = ''
  activeCategory.value = getPreferredSubjectCategory()
  isSubjectModalOpen.value = true
}

function closeSubjectModal() {
  isSubjectModalOpen.value = false
  subjectSearch.value = ''
  activeCategory.value = 'All'
  draftSubjectCodes.value = []
}

function isDraftSelected(subjectCode) {
  return draftSubjectCodes.value.includes(subjectCode)
}

function toggleDraftSubject(subjectCode) {
  if (isDraftSelected(subjectCode)) {
    draftSubjectCodes.value = draftSubjectCodes.value.filter(code => code !== subjectCode)
    return
  }

  draftSubjectCodes.value = [...draftSubjectCodes.value, subjectCode]
}

function confirmSubjectSelection() {
  profile.value.subjects = [...draftSubjectCodes.value]
  closeSubjectModal()
}

function removeSubject(subjectCode) {
  profile.value.subjects = profile.value.subjects.filter(code => code !== subjectCode)
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
    const response = await api.post('/tutee/profile/avatar/', formData)
    profile.value.profile_picture_url = response.data.profile_picture_url || ''
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
    const response = await api.get('/tutee/profile/')
    const data = response.data

    profile.value = {
      ...profile.value,
      ...data,
      course: data.course || '',
      bio: data.bio || '',
      profile_picture_url: data.profile_picture_url || '',
      subjects: Array.isArray(data.subjects) ? data.subjects : []
    }
    educationLevel.value = deriveEducationLevel(data.year_level)
  } catch (error) {
    console.error('Failed to load profile:', error)
    toastStore.push('Failed to load profile.', 'error')
  } finally {
    isLoadingProfile.value = false
  }
}

async function loadSubjects() {
  try {
    isLoadingSubjects.value = true
    const response = await api.get('/subjects/')
    subjects.value = response.data
  } catch (error) {
    console.error('Failed to load subjects:', error)
    toastStore.push('Failed to load subjects.', 'error')
  } finally {
    isLoadingSubjects.value = false
  }
}

async function loadCourses() {
  try {
    const response = await api.get('/courses/')
    courses.value = response.data
  } catch (error) {
    console.error('Failed to load courses:', error)
    toastStore.push('Failed to load courses.', 'error')
  }
}

async function discardChanges() {
  await loadProfile()
  toastStore.push('Changes discarded.')
}

async function saveProfile() {
  if (isSavingProfile.value) {
    return
  }

  const payload = {
    fname: profile.value.fname,
    mname: profile.value.mname,
    lname: profile.value.lname,
    course: shouldShowCourse.value ? profile.value.course : '',
    year_level: profile.value.year_level,
    bio: profile.value.bio || '',
    subjects: profile.value.subjects
  }

  try {
    isSavingProfile.value = true
    await api.put('/tutee/profile/update/', payload)
    toastStore.push('Profile updated successfully.')
    await loadProfile()
  } catch (error) {
    console.error('Profile update failed:', error)
    toastStore.push(error.response?.data?.error || 'Failed to update profile.', 'error')
  } finally {
    isSavingProfile.value = false
  }
}

watch(draftYearOptions, () => {
  if (!isAcademicModalOpen.value) {
    return
  }

  alignDraftYearWithLevel()
})

watch(filteredDraftCourses, () => {
  if (!isAcademicModalOpen.value) {
    return
  }

  alignDraftCourseWithLevel()
})

watch([educationLevel, () => profile.value.course], () => {
  refreshSubjectFilterForAcademicContext()
})

watch(availableCategories, () => {
  if (!availableCategories.value.includes(activeCategory.value)) {
    activeCategory.value = getPreferredSubjectCategory()
  }
})

onMounted(() => {
  loadProfile()
  loadCourses()
  loadSubjects()
})
</script>

<style scoped>
.tutee-profile-shell {
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
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
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

.glass-segment {
  background: color-mix(in srgb, var(--sb-card-bg) 84%, transparent);
  border: 1px solid color-mix(in srgb, var(--sb-card-border) 82%, transparent);
  border-radius: 24px;
  box-shadow: 0 24px 70px rgba(15, 23, 42, 0.1);
  backdrop-filter: blur(24px);
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
.course-year-display,
.profile-actions,
.modal-header-row,
.modal-footer-row,
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
  display: flex;
  align-items: center;
  justify-content: center;
  width: 104px;
  height: 104px;
  border: 4px solid rgba(255, 255, 255, 0.42);
  border-radius: 999px;
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
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 850;
  line-height: 1;
  letter-spacing: 0;
}

.header-badges,
.subject-pill-row,
.category-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.header-badges {
  margin-top: 0.75rem;
}

.role-badge,
.verified-badge,
.subject-counter {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  border-radius: 999px;
  font-weight: 800;
}

.role-badge,
.verified-badge {
  padding: 0.38rem 0.7rem;
  background: rgba(255, 255, 255, 0.14);
  color: #fff;
  font-size: 0.78rem;
}

.header-actions {
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-soft,
.btn-primary-action,
.btn-discard,
.btn-save,
.btn-ghost-sm,
.btn-confirm {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  min-height: 42px;
  border: 0;
  border-radius: 999px;
  padding: 0.72rem 1rem;
  font-weight: 850;
}

.btn-soft {
  background: rgba(255, 255, 255, 0.14);
  color: #fff;
}

.btn-soft:hover {
  background: rgba(255, 255, 255, 0.22);
}

.btn-primary-action,
.btn-save,
.btn-confirm {
  background: var(--sb-primary);
  color: #fff;
  box-shadow: 0 16px 32px rgba(0, 137, 90, 0.2);
}

.btn-primary-action {
  background: #fff;
  color: #07543a;
}

.btn-save:hover,
.btn-confirm:hover {
  background: var(--sb-primary-hover);
}

.btn-discard,
.btn-ghost-sm {
  border: 1px solid #d8e3dd;
  background: rgba(255, 255, 255, 0.72);
  color: #334155;
}

.profile-grid {
  display: grid;
  grid-template-columns: minmax(0, 0.95fr) minmax(0, 1.05fr);
  gap: 1.25rem;
}

.profile-col,
.field-group {
  display: grid;
  gap: 1.25rem;
}

.segment-header {
  gap: 0.85rem;
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
  border-radius: 16px;
  background: var(--sb-green-tint);
  color: var(--sb-primary);
  font-size: 1.1rem;
}

.segment-title {
  margin: 0;
  color: #17251f;
  font-size: 1.1rem;
  font-weight: 850;
  letter-spacing: 0;
}

.segment-copy {
  margin: 0.18rem 0 0;
  color: #6b7b74;
  font-size: 0.88rem;
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
.modal-section-label,
.summary-label {
  color: #60716a;
  font-size: 0.76rem;
  font-weight: 850;
  text-transform: uppercase;
  letter-spacing: 0;
}

.input-glass,
.subject-description-input {
  width: 100%;
  border: 1px solid #dbe7e1;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.72);
  color: #16231f;
  padding: 0.82rem 0.95rem;
  font: inherit;
  outline: none;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, background-color 0.18s ease;
}

.input-glass:focus,
.subject-description-input:focus {
  border-color: var(--sb-primary);
  background: #fff;
  box-shadow: 0 0 0 4px rgba(0, 137, 90, 0.1);
}

.input-disabled {
  color: #66756e;
  cursor: not-allowed;
}

.academic-summary-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.summary-chip {
  display: grid;
  gap: 0.2rem;
  min-height: 84px;
  border: 1px solid rgba(188, 206, 198, 0.86);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.62);
  padding: 1rem;
}

.summary-value {
  color: #17251f;
  font-size: 1rem;
  font-weight: 850;
}

.course-year-display {
  flex-wrap: wrap;
  gap: 0.65rem;
}

.course-chip,
.year-chip {
  display: inline-flex;
  align-items: center;
  min-height: 40px;
  border: 1px solid #cfe1d8;
  border-radius: 999px;
  background: rgba(0, 137, 90, 0.08);
  color: #07543a;
  padding: 0.55rem 0.8rem;
  font-size: 0.82rem;
  font-weight: 800;
}

.chip-unset {
  border-color: #e2e8f0;
  background: rgba(248, 250, 252, 0.86);
  color: #64748b;
}

.change-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  min-height: 40px;
  border: 0;
  border-radius: 999px;
  background: #17251f;
  color: #fff;
  padding: 0.56rem 0.9rem;
  font-weight: 850;
}

.preferences-segment {
  min-height: 100%;
}

.subject-counter {
  margin-left: auto;
  padding: 0.35rem 0.7rem;
  background: rgba(0, 137, 90, 0.1);
  color: var(--sb-primary);
  font-size: 0.78rem;
}

.subject-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  min-height: 38px;
  border: 1px solid rgba(0, 137, 90, 0.24);
  border-radius: 999px;
  background: rgba(0, 137, 90, 0.09);
  color: #07543a;
  padding: 0.45rem 0.55rem 0.45rem 0.8rem;
  font-size: 0.82rem;
  font-weight: 800;
}

.subject-pill-remove {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: 0;
  border-radius: 999px;
  background: rgba(0, 137, 90, 0.12);
  color: var(--sb-primary);
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
  border-style: solid;
  background: rgba(0, 137, 90, 0.06);
}

.empty-note {
  margin: 0;
  color: #7b8b84;
  font-size: 0.88rem;
}

.bio-textarea {
  min-height: 150px;
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

.actions-segment {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.profile-actions {
  justify-content: flex-end;
  gap: 0.75rem;
}

.modal-backdrop-soft {
  position: fixed;
  inset: 0;
  z-index: 1060;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.25rem;
  background: rgba(15, 23, 42, 0.42);
  backdrop-filter: blur(8px);
}

.glass-modal {
  display: grid;
  gap: 1.25rem;
  width: min(760px, 100%);
  max-height: calc(100vh - 2.5rem);
  overflow: auto;
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 34px 90px rgba(15, 23, 42, 0.2);
  backdrop-filter: blur(24px);
  padding: 1.5rem;
}

.subject-modal {
  width: min(820px, 100%);
}

.modal-header-row {
  justify-content: space-between;
  gap: 1rem;
}

.modal-title {
  margin: 0;
  color: #17251f;
  font-size: 1.35rem;
  font-weight: 850;
}

.modal-kicker {
  color: var(--sb-primary);
}

.modal-close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border: 0;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.06);
  color: #334155;
}

.modal-section {
  display: grid;
  gap: 0.75rem;
}

.education-grid,
.year-grid,
.course-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.education-card,
.year-btn,
.course-card,
.category-pill,
.subject-option {
  border: 1px solid #dbe7e1;
  background: rgba(255, 255, 255, 0.72);
  color: #17251f;
}

.education-card,
.course-card {
  display: grid;
  align-content: start;
  gap: 0.35rem;
  min-height: 106px;
  border-radius: 18px;
  padding: 1rem;
  text-align: left;
}

.education-card-icon {
  color: var(--sb-primary);
  font-size: 1.2rem;
}

.education-card-label,
.course-card-code,
.subject-option-name {
  color: #17251f;
  font-weight: 850;
}

.education-card-meta,
.course-card-name,
.subject-option-meta {
  color: #66756e;
  font-size: 0.82rem;
  font-weight: 650;
  line-height: 1.35;
}

.education-card-active,
.course-card-active,
.year-btn-active,
.category-pill.active,
.subject-option.selected {
  border-color: rgba(0, 137, 90, 0.62);
  background: rgba(0, 137, 90, 0.11);
  box-shadow: 0 14px 34px rgba(0, 137, 90, 0.12);
}

.year-btn,
.category-pill {
  min-height: 42px;
  border-radius: 999px;
  padding: 0.6rem 0.85rem;
  font-weight: 850;
}

.subject-modal-list {
  display: grid;
  gap: 0.9rem;
  max-height: 360px;
  overflow: auto;
  padding-right: 0.2rem;
}

.subject-group-section {
  display: grid;
  gap: 0.45rem;
}

.subject-group-header {
  position: sticky;
  top: 0;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  border: 1px solid rgba(219, 231, 225, 0.8);
  border-radius: 999px;
  background: rgba(248, 251, 249, 0.94);
  color: #60716a;
  padding: 0.42rem 0.7rem;
  font-size: 0.75rem;
  font-weight: 850;
  text-transform: uppercase;
  letter-spacing: 0;
  backdrop-filter: blur(14px);
}

.subject-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  border-radius: 18px;
  padding: 0.85rem 1rem;
  text-align: left;
}

.subject-option-copy {
  display: grid;
  gap: 0.18rem;
  min-width: 0;
}

.subject-option-check {
  color: var(--sb-primary);
  font-size: 1.1rem;
}

.modal-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-height: 100px;
  color: #64748b;
  font-size: 0.9rem;
  font-weight: 750;
}

.subject-modal-footer {
  justify-content: space-between;
  gap: 1rem;
}

.selected-count {
  color: #64748b;
  font-size: 0.86rem;
  font-weight: 750;
}

.modal-footer-row {
  justify-content: flex-end;
  gap: 0.75rem;
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
  .tutee-profile-shell {
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
  .modal-footer-actions,
  .subject-modal-footer {
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
  .academic-summary-grid,
  .education-grid,
  .year-grid,
  .course-grid {
    grid-template-columns: 1fr;
  }
}
</style>
