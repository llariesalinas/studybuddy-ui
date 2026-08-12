<template>
  <TutorOnboardingShell :current-step="1">
    <h3>Tutor profile setup</h3>
    <p class="muted">Set your teaching preferences to start matching.</p>

    <form @submit.prevent="handleCompleteSetup">
      <div class="field-block">
        <label class="field-label">Course and Year Level</label>
        <div class="course-year-display">
          <span class="course-chip" :class="{ 'chip-unset': !form.course }">
            {{ currentCourseLabel }}
          </span>
          <span class="year-chip" :class="{ 'chip-unset': !form.year_level }">
            {{ currentYearLabel }}
          </span>
          <button type="button" class="change-btn sb-btn" @click="openCourseYearModal">
            Change
            <i class="bi bi-arrow-right-short"></i>
          </button>
        </div>
      </div>

      <div class="field-block">
        <label class="field-label">Expertise Level</label>
        <p class="field-hint">Choose the learner level you are ready to teach.</p>
        <div class="teaching-level-grid" role="radiogroup" aria-label="Teaching level">
          <button
            v-for="option in teachingLevelOptions"
            :key="option.value"
            type="button"
            class="teaching-card sb-btn"
            :class="{ 'teaching-card-active': form.teaching_level === option.value }"
            role="radio"
            :aria-checked="form.teaching_level === option.value"
            @click="form.teaching_level = option.value"
          >
            <i :class="['bi', option.icon, 'teaching-card-icon']"></i>
            <span class="teaching-card-label">{{ option.label }}</span>
          </button>
        </div>
      </div>

      <div class="field-block">
        <label class="field-label">Modality</label>
        <div class="modality-pill-group">
          <button
            type="button"
            class="modality-pill sb-btn sb-pill"
            :class="{ 'modality-pill-active': form.can_online }"
            :aria-pressed="form.can_online"
            @click="form.can_online = !form.can_online"
          >
            <span class="modality-pill-icon"><i class="bi bi-camera-video-fill"></i></span>
            <span>Online</span>
          </button>
          <button
            type="button"
            class="modality-pill sb-btn sb-pill"
            :class="{ 'modality-pill-active': form.can_f2f }"
            :aria-pressed="form.can_f2f"
            @click="form.can_f2f = !form.can_f2f"
          >
            <span class="modality-pill-icon"><i class="bi bi-geo-alt-fill"></i></span>
            <span>Face-to-Face</span>
          </button>
        </div>
      </div>

      <div class="field-block">
        <label class="field-label" for="hourly-rate-input">Hourly Rate (PHP)</label>
        <div class="rate-input-shell">
          <span class="rate-prefix">PHP</span>
          <input
            id="hourly-rate-input"
            type="text"
            inputmode="numeric"
            class="rate-input"
            v-model="form.hourly_rate"
            placeholder="0.00"
            required
            @input="sanitizeRateInput"
          >
        </div>
      </div>

      <div class="commission-row">
        <input class="form-check-input" type="checkbox" v-model="commissionTermsAccepted" id="commission-terms">
        <label class="form-check-label" for="commission-terms">
          I understand StudyBuddy deducts a {{ commissionRatePercent }}% platform fee from
          each completed session's payout.
        </label>
      </div>

      <button type="submit" class="btn-primary-pill sb-btn" :disabled="!commissionTermsAccepted">
        Continue to Subjects
      </button>
    </form>
  </TutorOnboardingShell>

  <div
    v-if="isCourseYearModalOpen"
    class="modal-backdrop-soft"
    role="presentation"
    @click.self="closeCourseYearModal"
  >
    <section
      class="glass-modal course-year-modal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="course-year-title"
    >
      <div class="modal-header-row">
        <div>
          <p class="modal-kicker">Academic Context</p>
          <h2 id="course-year-title" class="modal-title">Course and Year Level</h2>
        </div>
        <button type="button" class="modal-close sb-btn" aria-label="Close" @click="closeCourseYearModal">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>

      <div class="modal-section">
        <p class="modal-section-label">Course</p>
        <div class="course-grid">
          <button
            v-for="course in courses"
            :key="course.course_code"
            type="button"
            class="course-card sb-btn"
            :class="{ 'course-card-active': draftCourse === course.course_code }"
            @click="draftCourse = course.course_code"
          >
            <span class="course-card-code">{{ course.course_code }}</span>
            <span class="course-card-name">{{ course.course_name }}</span>
          </button>

          <p v-if="!courses.length" class="empty-note modal-empty">
            Courses are not available right now.
          </p>
        </div>
      </div>

      <div class="modal-section">
        <p class="modal-section-label">Year Level</p>
        <div class="year-grid">
          <button
            v-for="year in filteredDraftYearLevels"
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
        <button type="button" class="btn-ghost-sm sb-btn" @click="closeCourseYearModal">
          Cancel
        </button>
        <button type="button" class="btn-confirm sb-btn" @click="confirmCourseYearSelection">
          Confirm
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProfileStore } from '@/stores/profile'
import { useToastStore } from '@/stores/toast'
import { useCatalogStore } from '@/stores/catalog'
import api from '@/services/api/api'
import { PLATFORM_COMMISSION_RATE_PERCENT } from '@/config'
import TutorOnboardingShell from '@/components/TutorOnboardingShell.vue'

const router = useRouter()
const profileStore = useProfileStore()
const toastStore = useToastStore()
const catalogStore = useCatalogStore()

const commissionRatePercent = PLATFORM_COMMISSION_RATE_PERCENT

// A tutor's hourly rate can't be negative.
const MIN_HOURLY_RATE = 0

const form = ref({
  course: '',
  year_level: null,
  teaching_level: '',
  can_online: true,
  can_f2f: false,
  hourly_rate: null
})

// Pre-checked once accepted (see profileStore.checkProfileStatus) so a returning tutor editing
// their profile isn't asked to re-acknowledge every time — see ADR-0010.
const commissionTermsAccepted = ref(profileStore.commissionTermsAccepted)

const teachingLevelOptions = [
  { label: 'Elementary', value: 'Elementary', icon: 'bi-pencil-fill' },
  { label: 'High School', value: 'High School', icon: 'bi-book-fill' },
  { label: 'College', value: 'College', icon: 'bi-mortarboard-fill' },
]

// Course/year picker — same picker as TutorProfile.vue's "Change" flow (Identity Details),
// reused here so it's collected at onboarding instead of only after the tutor already has a
// profile to edit.
const courses = ref([])
const isCourseYearModalOpen = ref(false)
const draftCourse = ref('')
const draftYearLevel = ref(null)

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

const currentCourseLabel = computed(() => {
  if (!form.value.course) {
    return 'Select course'
  }

  const course = courses.value.find(item => item.course_code === form.value.course)
  if (!course) {
    return form.value.course
  }

  return `${course.course_code} - ${course.course_name}`
})

const currentYearLabel = computed(() => {
  const year = yearLevels.find(item => item.value === Number(form.value.year_level))
  return year?.label || 'Select year'
})

const filteredDraftYearLevels = computed(() => {
  const selectedCourse = courses.value.find(course => course.course_code === draftCourse.value)
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

function openCourseYearModal() {
  draftCourse.value = form.value.course || ''
  draftYearLevel.value = form.value.year_level || null
  isCourseYearModalOpen.value = true
}

function closeCourseYearModal() {
  isCourseYearModalOpen.value = false
}

function confirmCourseYearSelection() {
  form.value.course = draftCourse.value
  form.value.year_level = draftYearLevel.value
  closeCourseYearModal()
}

async function loadCourses() {
  try {
    courses.value = await catalogStore.fetchCourses()
  } catch (error) {
    console.error('Failed to load courses:', error)
    toastStore.push('Failed to load courses.', 'error')
  }
}

// The field is text (not number) so it can carry the PHP prefix inline; strip anything
// that isn't a digit or a single decimal point as the tutor types.
const sanitizeRateInput = (event) => {
  const sanitized = event.target.value
    .replace(/[^\d.]/g, '')
    .replace(/(\..*)\./g, '$1')
  form.value.hourly_rate = sanitized
}


/* LOAD EXISTING TUTOR DATA */
onMounted(async () => {

  loadCourses()

  try {

    const response = await api.get('/tutor/profile/')

    const tutor = response.data

    form.value.course = tutor.course || ''
    form.value.year_level = tutor.year_level || null
    form.value.teaching_level = tutor.teaching_level
    form.value.can_online = tutor.can_online
    form.value.can_f2f = tutor.can_f2f
    form.value.hourly_rate = tutor.hourly_rate

  } catch {

    console.log("New tutor setup")

  }

})


/* SUBMIT PROFILE SETUP */
const handleCompleteSetup = async () => {

  if (!form.value.course || !form.value.year_level) {
    toastStore.push("Please select your course and year level.", 'warning')
    return
  }

  if (!form.value.teaching_level) {
    toastStore.push("Please select your teaching level.", 'warning')
    return
  }

  const parsedRate = Number(form.value.hourly_rate)

  if (!form.value.hourly_rate || Number.isNaN(parsedRate) || parsedRate <= MIN_HOURLY_RATE) {
    toastStore.push("Please enter a valid hourly rate.", 'warning')
    return
  }

  if (!commissionTermsAccepted.value) {
    toastStore.push("Please acknowledge the platform commission before continuing.", 'warning')
    return
  }

  try {

    await api.put('/tutee/profile/update/', {
      course: form.value.course,
      year_level: form.value.year_level,
    })

    await api.post('/tutor/setup/', {
      ...form.value,
      hourly_rate: parsedRate,
      commission_terms_accepted: commissionTermsAccepted.value,
    })

    // update profile guard state
    profileStore.profileCompleted = true
    profileStore.commissionTermsAccepted = true

    router.push({ name: 'tutor-subjects-setup' })

  } catch (error) {

    console.error("Failed to save tutor profile", error)
    toastStore.push("Could not save tutor profile.", 'error')

  }

}
</script>

<style scoped>
.field-block {
  margin-bottom: 1.25rem;
}

.field-label {
  display: block;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--sb-text-muted);
  margin-bottom: 8px;
}

.field-hint {
  margin: -4px 0 10px;
  font-size: 0.82rem;
  color: var(--sb-text-muted);
}

/* Course/year chip row — same visual language as TutorProfile.vue's Identity Details card,
   reused here since this is where the course/year selector now lives during onboarding. */
.course-year-display {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1.25rem;
}

.course-chip,
.year-chip {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  max-width: 100%;
  padding: 0.42rem 0.7rem;
  border: 1px solid rgba(0, 137, 90, 0.22);
  border-radius: 10px;
  background: rgba(0, 137, 90, 0.08);
  color: var(--sb-primary);
  font-size: 0.84rem;
  font-weight: 750;
}

.course-chip {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chip-unset {
  color: #94a3b8;
  background: #f8fafc;
  border-color: #dbe3df;
}

.change-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.2rem;
  border: 1.5px dashed #b9c7c1;
  background: transparent;
  color: #4b655b;
  font-weight: 800;
  padding: 0.42rem 0.7rem;
}

.change-btn:hover {
  border-color: var(--sb-primary);
  color: var(--sb-primary);
  background: rgba(0, 137, 90, 0.05);
}

/* Expertise-level card grid — same pattern as TutorProfile.vue's Expertise Level section. */
.teaching-level-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.teaching-card {
  display: grid;
  place-items: center;
  gap: 0.45rem;
  min-height: 112px;
  border: 1.5px solid var(--sb-card-border);
  background: var(--sb-card-bg);
  color: var(--sb-text-muted);
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

/* Course/year modal — same shell and grids as TutorProfile.vue's course-year-modal. */
.modal-backdrop-soft {
  position: fixed;
  inset: 0;
  z-index: 1050;
  display: grid;
  place-items: center;
  padding: 1.5rem;
  background: rgba(15, 23, 42, 0.46);
}

.glass-modal {
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
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.modal-kicker {
  margin: 0 0 0.25rem;
  color: var(--sb-primary);
  font-size: 0.74rem;
  font-weight: 800;
  text-transform: uppercase;
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

.modal-section {
  display: grid;
  gap: 0.75rem;
}

.modal-section-label {
  margin: 0;
  color: #64748b;
  font-size: 0.74rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0;
}

.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(148px, 1fr));
  gap: 0.55rem;
}

.empty-note {
  margin: 0;
  color: #7b8b84;
  font-size: 0.88rem;
}

.course-card {
  display: grid;
  gap: 0.18rem;
  min-height: 76px;
  border: 1.5px solid #dbe7e1;
  background: rgba(248, 250, 252, 0.82);
  padding: 0.65rem 0.75rem;
  text-align: left;
}

.course-card:hover,
.course-card-active {
  border-color: var(--sb-primary);
  background: rgba(0, 137, 90, 0.08);
}

.course-card-code {
  color: #10231d;
  font-size: 0.84rem;
  font-weight: 850;
}

.course-card-name {
  color: #64748b;
  font-size: 0.75rem;
  line-height: 1.25;
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

.modal-footer-row {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-ghost-sm,
.btn-confirm {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  border: 0;
  border-radius: 999px;
  font-weight: 800;
  padding: 0.6rem 1.1rem;
}

.btn-ghost-sm {
  background: transparent;
  color: var(--sb-text-muted);
}

.btn-ghost-sm:hover {
  color: var(--sb-text-main);
}

.btn-confirm {
  color: #fff;
  background: var(--sb-primary);
  box-shadow: 0 12px 24px rgba(0, 137, 90, 0.22);
}

.btn-confirm:hover {
  background: var(--sb-primary-hover);
  color: #fff;
}

@media (max-width: 540px) {
  .teaching-level-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .course-grid {
    grid-template-columns: 1fr;
  }

  .year-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

.commission-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin: 0 0 1.5rem;
  font-size: 0.82rem;
  color: var(--sb-text-muted);
}

.commission-row .form-check-input {
  margin-top: 3px;
  flex-shrink: 0;
}

.btn-primary-pill {
  width: 100%;
  border: 0;
  border-radius: 999px;
  padding: 11px 24px;
  font-weight: 700;
  font-size: 13.5px;
  background: var(--sb-primary);
  color: var(--sb-primary-contrast);
}

.btn-primary-pill:hover:not(:disabled) {
  background: var(--sb-primary-hover);
}

.btn-primary-pill:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Modality pills — same visual language as InitialBooking.vue's "Preferred Mode"
   picker (.mode-button), but multi-select: can_online / can_f2f stay independent
   booleans since a tutor may support both at once. Motion tokens only, no new
   easing/keyframes, per docs/specs/2026-06-21-feel-haptics-unification-design.md. */
.modality-pill-group {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

/* .sb-btn / .sb-pill (main.css) already supply hover-lift, press-scale, and the
   prefers-reduced-motion guard — this block only adds the layout/color local
   overrides, mirroring InitialBooking.vue's .mode-button (same house pattern,
   applied here as multi-select instead of single-select). */
.modality-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 44px;
  border: 1px solid var(--sb-card-border);
  border-radius: 14px;
  background: var(--sb-card-bg);
  color: var(--sb-text-main);
  padding: 9px 10px;
  font-size: 14px;
  font-weight: 700;
  line-height: 1.2;
}

.modality-pill:hover,
.modality-pill:focus-visible {
  border-color: var(--sb-primary);
  box-shadow: var(--sb-halo);
  outline: none;
}

.modality-pill-active {
  border-color: var(--sb-primary);
  background: color-mix(in srgb, var(--sb-primary) 12%, var(--sb-card-bg));
  color: var(--sb-primary);
}

.modality-pill-icon {
  display: inline-flex;
  flex: 0 0 auto;
}

/* Hourly rate — plain typable field with an inline PHP prefix. .sb-field's canonical
   immediate focus snap is reproduced here via :focus-within since focus lands on the
   inner <input>, not this wrapping shell. */
.rate-input-shell {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  border: 1.5px solid var(--sb-card-border);
  border-radius: 0.6rem;
  padding: 0.65rem 0.9rem;
  background: var(--sb-card-bg);
  transition: none;
}

.rate-input-shell:focus-within {
  border-color: var(--sb-primary);
  box-shadow: var(--sb-halo);
}

.rate-prefix {
  color: var(--sb-text-muted);
  font-weight: 700;
  font-size: 0.95rem;
  pointer-events: none;
}

.rate-input {
  flex: 1 1 auto;
  min-width: 0;
  border: none;
  background: transparent;
  outline: none;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--sb-text-main);
  padding: 0;
}
</style>
