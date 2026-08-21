<template>
  <TutorOnboardingShell :current-step="1">
    <h3>Tutor profile setup</h3>
    <p class="muted">Set your teaching preferences to start matching.</p>

    <form @submit.prevent="handleCompleteSetup">
      <div class="field-block">
        <label class="field-label">Course</label>
        <p class="field-hint">Your own degree program or academic track.</p>
        <SbSelectModal
          v-model="form.course"
          :options="courseOptions"
          title="Course"
          placeholder="+ Add Course"
          search-placeholder="Search courses"
          searchable
        />
      </div>

      <div class="field-block">
        <label class="field-label">Year Level</label>
        <div class="year-grid" role="radiogroup" aria-label="Year level">
          <button
            v-for="year in filteredYearLevels"
            :key="year.value"
            type="button"
            class="year-btn sb-btn"
            :class="{ 'year-btn-active': Number(form.year_level) === year.value }"
            role="radio"
            :aria-checked="Number(form.year_level) === year.value"
            @click="form.year_level = year.value"
          >
            {{ year.label }}
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
        <p class="field-hint">
          Between PHP {{ minHourlyRate }} and PHP {{ maxHourlyRate }} per hour.
        </p>
      </div>

      <div class="commission-row">
        <input class="form-check-input" type="checkbox" v-model="commissionTermsAccepted" id="commission-terms">
        <label class="form-check-label" for="commission-terms">
          I understand StudyBuddy deducts a {{ commissionRatePercent }}% platform fee from
          each completed session's payout.
        </label>
      </div>

      <button
        type="submit"
        class="btn-primary-pill sb-btn"
        :disabled="!isSetupComplete"
        :title="incompleteReason || undefined"
      >
        Continue to Subjects
      </button>

      <p v-if="incompleteReason" class="setup-blocker" role="status">
        <i class="bi bi-info-circle-fill"></i>
        {{ incompleteReason }}
      </p>
    </form>
  </TutorOnboardingShell>
</template>

<script setup>
import { computed, ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProfileStore } from '@/stores/profile'
import { useToastStore } from '@/stores/toast'
import { useCatalogStore } from '@/stores/catalog'
import api from '@/services/api/api'
import {
  MAX_HOURLY_RATE,
  MIN_HOURLY_RATE,
  PLATFORM_COMMISSION_RATE_PERCENT,
} from '@/config'
import TutorOnboardingShell from '@/components/TutorOnboardingShell.vue'
import SbSelectModal from '@/components/SbSelectModal.vue'

const router = useRouter()
const profileStore = useProfileStore()
const toastStore = useToastStore()
const catalogStore = useCatalogStore()

const commissionRatePercent = PLATFORM_COMMISSION_RATE_PERCENT

const minHourlyRate = MIN_HOURLY_RATE
const maxHourlyRate = MAX_HOURLY_RATE

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

// Course/year picker — same controls as TutorProfile.vue's Identity Details section, so a tutor
// sees one consistent way to set their course whether they are onboarding or editing later.
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

const courseOptions = computed(() =>
  courses.value.map(course => ({
    label: `${course.course_code} - ${course.course_name}`,
    value: course.course_code,
  }))
)

const filteredYearLevels = computed(() => {
  const selectedCourse = courses.value.find(course => course.course_code === form.value.course)
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

// Switching course narrows the year-level options (a college course cannot be Grade 3), so a
// year carried over from the previous course would otherwise stay selected while invisible.
watch(() => form.value.course, () => {
  const stillValid = filteredYearLevels.value.some(
    year => year.value === Number(form.value.year_level)
  )

  if (!stillValid) {
    form.value.year_level = null
  }
})

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


/* SETUP COMPLETENESS CHECK */

// The rate field is free text (see sanitizeRateInput), so "", "." and "12." all reach here.
// Returns null for anything that is not a usable number rather than leaning on Number(''), which
// is 0 and would read as a filled-in rate.
const parsedHourlyRate = computed(() => {
  const raw = String(form.value.hourly_rate ?? '').trim()

  if (!raw) {
    return null
  }

  const parsed = Number(raw)
  return Number.isFinite(parsed) ? parsed : null
})

const isHourlyRateValid = computed(() =>
  parsedHourlyRate.value !== null &&
  parsedHourlyRate.value >= minHourlyRate &&
  parsedHourlyRate.value <= maxHourlyRate
)

// Both modality flags are independent booleans, so a tutor can switch both off and end up
// bookable in no format at all.
const hasModality = computed(() => Boolean(form.value.can_online || form.value.can_f2f))

// Ordered top-to-bottom to match the form, so the message always names the first thing the tutor
// still has to do. Doubles as the reason the Continue button is disabled -- a dead submit control
// with no explanation reads as a broken page.
const incompleteReason = computed(() => {
  if (!form.value.course) {
    return 'Select your course to continue.'
  }

  if (!form.value.year_level) {
    return 'Select your year level to continue.'
  }

  if (!form.value.teaching_level) {
    return 'Select the expertise level you can teach.'
  }

  if (!hasModality.value) {
    return 'Pick at least one modality — Online, Face-to-Face, or both.'
  }

  if (parsedHourlyRate.value === null) {
    return 'Enter your hourly rate to continue.'
  }

  if (!isHourlyRateValid.value) {
    return `Your hourly rate must be between PHP ${minHourlyRate} and PHP ${maxHourlyRate}.`
  }

  if (!commissionTermsAccepted.value) {
    return 'Acknowledge the platform commission to continue.'
  }

  return ''
})

const isSetupComplete = computed(() => !incompleteReason.value)


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

  if (!hasModality.value) {
    toastStore.push("Please choose at least one modality.", 'warning')
    return
  }

  const parsedRate = Number(form.value.hourly_rate)

  if (!form.value.hourly_rate || Number.isNaN(parsedRate)) {
    toastStore.push("Please enter a valid hourly rate.", 'warning')
    return
  }

  // Checked here rather than in sanitizeRateInput: clamping mid-keystroke would fight a tutor
  // typing "200" by rewriting the "2". The server clamps to the same bounds on save.
  if (parsedRate < minHourlyRate || parsedRate > maxHourlyRate) {
    toastStore.push(
      `Your hourly rate must be between PHP ${minHourlyRate} and PHP ${maxHourlyRate}.`,
      'warning',
    )
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

.empty-note {
  margin: 0;
  color: #7b8b84;
  font-size: 0.88rem;
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

@media (max-width: 540px) {
  .teaching-level-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
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

.setup-blocker {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0.6rem 0 0;
  font-size: 0.82rem;
  color: var(--sb-text-muted);
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
