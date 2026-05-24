<template>
<div class="profile-content">
  <div class="card border-sb shadow-sm rounded-4">
  <div class="card-body p-4 p-md-5">

  <div class="d-flex align-items-center mb-4 pb-4 border-bottom">
    <div
      class="rounded-circle bg-success bg-opacity-10 d-flex justify-content-center align-items-center fw-bold fs-3 me-4"
      style="width:80px;height:80px"
    >
      {{ initials }}
    </div>

    <div>
      <h5 class="fw-bold mb-1">{{ profile.fullName }}</h5>
      <p class="text-muted small mb-2">Tutor</p>
    </div>
  </div>

<form @submit.prevent="saveProfile">

<div class="row g-4">

<div class="col-md-6">
<label class="form-label fw-semibold small">Full Name</label>
<input v-model="profile.fullName" class="form-control">
</div>

<div class="col-md-6">
<label class="form-label fw-semibold small">Email</label>
<input :value="profile.email" disabled class="form-control bg-light">
</div>

<div class="col-md-6">
<label class="form-label fw-semibold small">Course</label>

<select v-model="profile.course" class="form-select">

<option value="">Select Course</option>

<option
  v-for="c in courses"
  :key="c.course_code"
  :value="c.course_code"
>
  {{ c.course_code }} - {{ c.course_name }}
</option>

</select>
</div>

<div class="col-md-6">
<label class="form-label fw-semibold small">Year Level</label>

<select v-model.number="profile.year_level" class="form-select">

<option value="">Select Level</option>

<option
  v-for="y in yearLevels"
  :key="y.value"
  :value="y.value"
>
  {{ y.label }}
</option>

</select>
</div>

<div class="col-md-6">
<label class="form-label fw-semibold small">Hourly Rate</label>
<input type="number" v-model="profile.hourly_rate" class="form-control">
</div>

<div class="col-md-6">
<label class="form-label fw-semibold small">Response Time</label>
<select v-model="profile.response_time" class="form-select">
<option value="">Select response time</option>
<option
  v-for="option in responseTimeOptions"
  :key="option.value"
  :value="option.value"
>
  {{ option.label }}
</option>
</select>
</div>

<div class="col-md-6">
<label class="form-label fw-semibold small">Teaching Level</label>
<input v-model="profile.teaching_level" class="form-control">
</div>

<div class="col-md-6">
<label class="form-label fw-semibold small">Session Mode</label>

<div class="form-check">
<input type="checkbox" v-model="profile.can_online" class="form-check-input">
<label class="form-check-label">Online</label>
</div>

<div class="form-check">
<input type="checkbox" v-model="profile.can_f2f" class="form-check-input">
<label class="form-check-label">Face-to-Face</label>
</div>

</div>

<div class="col-12">
<label class="form-label fw-semibold small">Subjects</label>

<div class="subject-picker-shell">
  <button
    type="button"
    class="btn btn-outline-dark rounded-3 fw-semibold sb-btn"
    @click="openSubjectModal"
  >
    + Add subjects
  </button>

  <div v-if="profile.subjects.length" class="subject-pill-list">
    <span
      v-for="subject in profile.subjects"
      :key="subject.subject_code"
      class="subject-pill"
    >
      {{ subject.subject_name }}
      <button
        type="button"
        class="subject-pill-remove sb-btn"
        @click="removeSubject(subject.subject_code)"
      >
        ×
      </button>
    </span>
  </div>

  <p v-else class="text-muted small mb-0">No subjects selected yet.</p>

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

      <div v-if="openSubjectCode === subject.subject_code" class="subject-accordion-body">
        <label class="subject-accordion-label">Subject Syllabus &amp; Approach</label>
        <textarea
          v-model="subject.description"
          rows="4"
          class="subject-description-input"
          placeholder="Describe your methodology for this specific subject..."
        ></textarea>
      </div>
    </article>
  </div>

  <p class="text-muted small mb-0">Up to 8 subjects.</p>
</div>

</div>

<div class="col-12">

<label class="form-label fw-semibold small">Bio</label>

<textarea
v-model="profile.bio"
rows="4"
class="form-control"
></textarea>

</div>

</div>

<div class="text-end mt-4">
<button
  class="btn bg-sb-primary text-white px-4 d-inline-flex align-items-center gap-2 sb-btn"
  :disabled="isSavingProfile"
>
<span v-if="isSavingProfile" class="spinner-border spinner-border-sm" aria-hidden="true"></span>
{{ isSavingProfile ? 'Saving...' : 'Save Changes' }}
</button>
</div>

</form>

</div>
</div>

<div
  v-if="isSubjectModalOpen"
  class="subject-modal-backdrop"
  @click.self="closeSubjectModal"
>
  <div class="subject-modal card border-0 shadow rounded-4">
    <div class="card-body p-4">
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
          class="form-control"
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
        >
          {{ category }}
        </button>
      </div>

      <div class="subject-modal-list">
        <div v-if="isLoadingSubjects" class="text-center text-muted py-4">
          Loading subjects...
        </div>

        <div v-else-if="subjectsLoadError" class="text-center text-danger py-4">
          {{ subjectsLoadError }}
        </div>

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
              <span class="subject-option-meta">
                {{ normalizeCategory(subject.category) }}
              </span>
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
</div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '@/services/api/api'

const profile = ref({
  fullName: '',
  email: '',
  course: '',
  year_level: null,
  subjects: [],
  bio: '',
  hourly_rate: '',
  teaching_level: '',
  can_online: true,
  can_f2f: false,
  response_time: ''
})

const courses = ref([])
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
const isSavingProfile = ref(false)

const responseTimeOptions = [
  { value: 'within_1_hour', label: 'Within 1 hour' },
  { value: 'within_few_hours', label: 'Within a few hours' },
  { value: 'within_a_day', label: 'Within a day' }
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
  { label: '1st Year College', value: 13 },
  { label: '2nd Year College', value: 14 },
  { label: '3rd Year College', value: 15 },
  { label: '4th Year College', value: 16 }
]

const initials = computed(() => {
  if (!profile.value.fullName) return ''

  return profile.value.fullName
    .split(' ')
    .map(name => name[0])
    .join('')
})

const availableCategories = computed(() => {
  const categories = allSubjects.value
    .map(subject => normalizeCategory(subject.category))
    .filter(Boolean)

  return ['All', ...new Set(categories)]
})

const filteredSubjects = computed(() => {
  const query = subjectSearch.value.trim().toLowerCase()

  return allSubjects.value.filter(subject => {
    const category = normalizeCategory(subject.category)
    const matchesCategory = activeCategory.value === 'All' || category === activeCategory.value
    const matchesSearch =
      !query ||
      subject.subject_name.toLowerCase().includes(query) ||
      subject.subject_code.toLowerCase().includes(query)

    return matchesCategory && matchesSearch
  })
})

const selectedDraftCountLabel = computed(() => {
  const count = draftSubjectCodes.value.length
  return `${count} subject${count === 1 ? '' : 's'} selected`
})

function normalizeCategory(category) {
  const normalized = category?.trim()
  return normalized || 'Uncategorized'
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

async function openSubjectModal() {
  if (!allSubjects.value.length) {
    await loadSubjects()
  }

  draftSubjectCodes.value = profile.value.subjects.map(subject => subject.subject_code)
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

function isDraftSelected(subjectCode) {
  return draftSubjectCodes.value.includes(subjectCode)
}

function toggleDraftSubject(subjectCode) {
  if (isDraftSelected(subjectCode)) {
    draftSubjectCodes.value = draftSubjectCodes.value.filter(code => code !== subjectCode)
    return
  }

  if (draftSubjectCodes.value.length >= 8) {
    return
  }

  draftSubjectCodes.value = [...draftSubjectCodes.value, subjectCode]
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

const loadProfile = async () => {
  try {
    const res = await api.get('/tutor/profile/')
    const data = res.data

    profile.value.fullName = `${data.fname} ${data.lname}`
    profile.value.email = data.email
    profile.value.course = data.course
    profile.value.year_level = data.year_level
    profile.value.bio = data.bio
    profile.value.hourly_rate = data.hourly_rate
    profile.value.teaching_level = data.teaching_level
    profile.value.can_online = data.can_online
    profile.value.can_f2f = data.can_f2f
    profile.value.response_time = data.response_time || ''

    const subjectRes = await api.get('/tutor/subjects/')
    profile.value.subjects = subjectRes.data.map(subject => ({
      ...subject,
      description: subject.description || ''
    }))
    initialSubjectCodes.value = profile.value.subjects.map(subject => subject.subject_code)
    initialSubjectDescriptions.value = new Map(
      profile.value.subjects.map(subject => [subject.subject_code, subject.description || ''])
    )
  } catch (err) {
    console.error('Failed to load tutor profile:', err)
  }
}

const loadSubjects = async () => {
  if (isLoadingSubjects.value) {
    return
  }

  isLoadingSubjects.value = true
  subjectsLoadError.value = ''

  try {
    const res = await api.get('/subjects/')
    allSubjects.value = res.data
  } catch (error) {
    console.error('Failed to load subjects:', error)
    subjectsLoadError.value = 'Could not load subjects right now.'
  } finally {
    isLoadingSubjects.value = false
  }
}

const loadCourses = async () => {
  const res = await api.get('/courses/')
  courses.value = res.data
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

const saveProfile = async () => {
  if (isSavingProfile.value) {
    return
  }

  const names = profile.value.fullName.split(' ')

  const tuteePayload = {
    fname: names[0],
    lname: names.slice(1).join(' '),
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

    alert('Profile Updated')
  } catch (err) {
    console.error('Profile update failed:', err)
    alert('Profile update failed. Please try again.')
  } finally {
    isSavingProfile.value = false
  }
}

onMounted(() => {
  loadProfile()
  loadSubjects()
  loadCourses()
})

</script>

<style scoped>
.subject-picker-shell {
  display: grid;
  gap: 14px;
}

.subject-pill-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.subject-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  background: #0a7a51;
  color: #ffffff;
  font-weight: 600;
  font-size: 0.9rem;
}

.subject-pill-remove {
  border: 0;
  background: transparent;
  color: inherit;
  font-size: 1rem;
  line-height: 1;
  padding: 0;
}

.subject-accordion-list {
  display: grid;
  gap: 12px;
}

.subject-accordion-card {
  border: 1px solid #dbe7e1;
  border-radius: 20px;
  background: #f6f8f7;
  overflow: hidden;
  transition: border-color 180ms ease, box-shadow 180ms ease, background-color 180ms ease;
}

.subject-accordion-card-open {
  border-color: #9fd0ba;
  background: #eef7f3;
  box-shadow: 0 12px 24px rgba(10, 122, 81, 0.08);
}

.subject-accordion-header {
  width: 100%;
  border: 0;
  background: transparent;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
  text-align: left;
}

.subject-accordion-icon {
  width: 36px;
  height: 36px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #dfe5e2;
  color: #65756d;
  flex-shrink: 0;
  transition: background-color 180ms ease, color 180ms ease;
}

.subject-accordion-icon-open {
  background: #0a7a51;
  color: #ffffff;
}

.subject-accordion-title {
  font-size: 0.98rem;
  font-weight: 700;
  color: #1f2f2a;
  transition: color 180ms ease;
}

.subject-accordion-title-open {
  color: #0a7a51;
}

.subject-accordion-chevron {
  color: #5d7168;
  font-size: 1rem;
}

.subject-accordion-body {
  padding: 0 18px 18px;
  display: grid;
  gap: 10px;
}

.subject-accordion-label {
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #6d8178;
}

.subject-description-input {
  width: 100%;
  min-height: 120px;
  border: 0;
  border-radius: 18px;
  background: #ffffff;
  padding: 14px 16px;
  color: #183129;
  resize: vertical;
  box-shadow: inset 0 0 0 1px rgba(224, 231, 227, 0.85);
}

.subject-description-input:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(10, 122, 81, 0.14);
}

.subject-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1050;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgba(15, 23, 42, 0.42);
}

.subject-modal {
  width: min(720px, 100%);
  max-height: min(85vh, 760px);
  overflow: hidden;
}

.category-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.category-pill {
  border: 1px solid #d8e3de;
  background: #ffffff;
  color: #315447;
  border-radius: 999px;
  padding: 7px 14px;
  font-size: 0.9rem;
  font-weight: 600;
}

.category-pill.active {
  background: #e8f7f1;
  border-color: #0a7a51;
  color: #0a7a51;
}

.subject-modal-list {
  display: grid;
  gap: 10px;
  max-height: 420px;
  overflow-y: auto;
}

.subject-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  width: 100%;
  padding: 14px 16px;
  border: 1px solid #dde7e2;
  border-radius: 16px;
  background: #ffffff;
  text-align: left;
}

.subject-option.selected {
  background: #eef8f4;
  border-color: #86d0af;
}

.subject-option-copy {
  display: grid;
  gap: 2px;
}

.subject-option-name {
  font-weight: 700;
  color: #163127;
}

.subject-option-meta {
  font-size: 0.85rem;
  color: #6e8178;
}

.subject-option-check {
  flex-shrink: 0;
}

.subject-modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

@media (max-width: 576px) {
  .subject-modal-footer {
    align-items: stretch;
  }
}
</style>
