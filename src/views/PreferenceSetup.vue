<template>

  <!-- NAVBAR -->
  <nav class="navbar navbar-expand-lg sb-surface py-3">
    <div class="container d-flex justify-content-between align-items-center">
      <span class="navbar-brand fw-bold fs-4 sb-text">StudyBuddy</span>
      <SbThemeToggle />
    </div>
  </nav>

  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-lg-9">
        <div class="onboarding-shell">

          <!-- RAIL -->
          <aside class="onboarding-rail">
            <div class="rail-step" :class="railStepClass(0)">
              <span class="rail-num">{{ currentCard > 0 ? '' : '1' }}</span>
              <span>Level</span>
            </div>
            <div class="rail-step" :class="railStepClass(1)">
              <span class="rail-num">{{ currentCard > 1 ? '' : '2' }}</span>
              <span>{{ stepTwoLabel }}</span>
            </div>
            <div class="rail-step" :class="railStepClass(2)">
              <span class="rail-num">{{ currentCard > 2 ? '' : '3' }}</span>
              <span>Subjects</span>
            </div>
          </aside>

          <!-- MAIN -->
          <div class="onboarding-main sb-text">

            <!-- CARD 1: Education Level Category -->
            <div v-if="currentCard === 0">
              <h3 class="fw-bold mb-1">What is your Education Level?</h3>
              <p class="sb-muted mb-4">Select the category that best describes where you are now.</p>

              <div class="option-list">
                <div
                  v-for="level in educationLevels"
                  :key="level.value"
                  class="option-row"
                  :class="{ 'option-row-selected': educationLevel === level.value }"
                  @click="selectEducationLevel(level.value)"
                >
                  <span class="option-icon" v-html="level.icon"></span>
                  <div>
                    <div class="option-label">{{ level.label }}</div>
                    <div class="option-sub">{{ level.sub }}</div>
                  </div>
                </div>
              </div>

              <div class="d-flex justify-content-end mt-4">
                <button
                  class="btn onboarding-btn-primary"
                  :disabled="!educationLevel"
                  @click="nextCard"
                >
                  Continue
                </button>
              </div>
            </div>

            <!-- CARD 2: Specific Level (dynamic based on Card 1) -->
            <div v-if="currentCard === 1">

              <!-- Elementary: Grade 1–6 -->
              <div v-if="educationLevel === 'elementary'">
                <h3 class="fw-bold mb-1">Select Your Grade Level</h3>
                <p class="sb-muted mb-4">Elementary School — Grades 1 to 6</p>
                <div class="tile-grid tile-grid-3">
                  <div
                    v-for="g in elementaryGrades" :key="g.value"
                    class="tile"
                    :class="{ 'tile-selected': selectedGrade === g.value }"
                    @click="selectedGrade = g.value; store.selectedSubjects.splice(0)"
                  >
                    {{ g.label }}
                  </div>
                </div>
              </div>

              <!-- JHS: Grade 7–10 -->
              <div v-if="educationLevel === 'jhs'">
                <h3 class="fw-bold mb-1">Select Your Grade Level</h3>
                <p class="sb-muted mb-4">Junior High School — Grades 7 to 10</p>
                <div class="tile-grid tile-grid-2">
                  <div
                    v-for="g in jhsGrades" :key="g.value"
                    class="tile"
                    :class="{ 'tile-selected': selectedGrade === g.value }"
                    @click="selectedGrade = g.value; store.selectedSubjects.splice(0)"
                  >
                    {{ g.label }}
                  </div>
                </div>
              </div>

              <!-- SHS: Strand Selection -->
              <div v-if="educationLevel === 'shs'">
                <h3 class="fw-bold mb-1">Select Your SHS Strand</h3>
                <p class="sb-muted mb-4">Senior High School — Grade 11 or 12</p>
                <div class="tile-grid tile-grid-2 mb-4">
                  <div
                    v-for="s in shsStrands" :key="s.value"
                    class="tile tile-strand"
                    :class="{ 'tile-selected': selectedStrand === s.value }"
                    @click="selectedStrand = s.value; store.selectedSubjects.splice(0)"
                  >
                    <div class="option-label">{{ s.label }}</div>
                    <div class="option-sub">{{ s.full }}</div>
                  </div>
                </div>
                <div class="field-label">Grade Level</div>
                <div class="tile-grid tile-grid-2">
                  <div
                    v-for="g in shsGrades" :key="g.value"
                    class="tile"
                    :class="{ 'tile-selected': selectedGrade === g.value }"
                    @click="selectedGrade = g.value"
                  >
                    {{ g.label }}
                  </div>
                </div>
              </div>

              <!-- College: Course + Year Level -->
              <div v-if="educationLevel === 'college'">
                <h3 class="fw-bold mb-1">Select Your College Program</h3>
                <p class="sb-muted mb-4">Choose your degree and current year level.</p>
                <div class="field-label">Degree Program</div>
                <div class="mb-4">
                  <SbSelectModal
                    :model-value="selectedCourse"
                    :options="collegeCourseOptions"
                    title="Degree Program"
                    placeholder="-- Select your Course --"
                    searchable
                    trigger-class="onboarding-select"
                    @update:model-value="handleCourseChange"
                  />
                </div>
                <div class="field-label">Year Level</div>
                <div class="tile-grid tile-grid-4">
                  <div
                    v-for="y in collegeYears" :key="y.value"
                    class="tile"
                    :class="{ 'tile-selected': selectedCollegeYear === y.value }"
                    @click="selectedCollegeYear = y.value"
                  >
                    {{ y.label }}
                  </div>
                </div>
              </div>

              <div class="d-flex justify-content-between mt-4">
                <button class="btn onboarding-btn-outline" @click="prevCard">Back</button>
                <button
                  class="btn onboarding-btn-primary"
                  :disabled="!card2Valid"
                  @click="nextCard"
                >
                  Continue
                </button>
              </div>
            </div>

            <!-- CARD 3: Subject Selection -->
            <div v-if="currentCard === 2">
              <h3 class="fw-bold mb-1">Choose Your Target Subjects</h3>
              <p class="sb-muted mb-4">
                Showing subjects for <strong class="onboarding-accent">{{ card3Label }}</strong>.
              </p>

              <div v-if="subjects.length === 0" class="empty-state">
                <p class="fw-semibold mb-1">No subjects found for this selection.</p>
                <p class="small mb-0 sb-muted">Contact your administrator to seed subjects for this level.</p>
              </div>

              <SubjectTaxonomyPicker v-else v-model="store.selectedSubjects" :subjects="subjects" />

              <div class="d-flex justify-content-between mt-4">
                <button class="btn onboarding-btn-outline" @click="prevCard">Back</button>
                <button
                  class="btn onboarding-btn-primary"
                  :disabled="store.selectedSubjects.length === 0 || isSubmitting"
                  @click="finish"
                >
                  <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
                  Complete Onboarding
                </button>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>

</template>

<script setup>

import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api/api'
import { useCatalogStore } from '@/stores/catalog'
import { usePreferenceStore } from '@/stores/preferences'
import { useProfileStore } from '@/stores/profile'
import SbThemeToggle from '@/components/SbThemeToggle.vue'
import SbSelectModal from '@/components/SbSelectModal.vue'
import SubjectTaxonomyPicker from '@/components/SubjectTaxonomyPicker.vue'
import { useToastStore } from '@/stores/toast'

const router = useRouter()
const catalogStore = useCatalogStore()
const store = usePreferenceStore()
const profileStore = useProfileStore()
const toastStore = useToastStore()

const currentCard = ref(0)
const totalCards = 3
const isSubmitting = ref(false)

// Card 1
const educationLevel = ref('')

// Card 2
const selectedGrade = ref(null)
const selectedStrand = ref('')
const selectedCourse = ref('')
const selectedCollegeYear = ref(null)

// API data
const subjects = ref([])
const courses = ref([])

// ── Education Level Options ──────────────────────────────────
const ICON_ELEMENTARY = '<svg viewBox="0 0 24 24"><path d="M3 10l9-6 9 6-9 6-9-6z"/><path d="M6 12.5V18c0 1 3 2 6 2s6-1 6-2v-5.5"/></svg>'
const ICON_JHS = '<svg viewBox="0 0 24 24"><path d="M4 19V7l8-4 8 4v12"/><path d="M9 21v-6h6v6"/></svg>'
const ICON_SHS = '<svg viewBox="0 0 24 24"><path d="M2 17l10 5 10-5-10-5-10 5z"/><path d="M2 12l10 5 10-5-10-5-10 5z"/></svg>'
const ICON_COLLEGE = '<svg viewBox="0 0 24 24"><rect x="4" y="9" width="16" height="12" rx="1"/><path d="M9 21v-5h6v5"/><path d="M9 3h6v6H9z"/></svg>'

const educationLevels = [
  { value: 'elementary', label: 'Elementary',  icon: ICON_ELEMENTARY, sub: 'Grade 1 – 6' },
  { value: 'jhs',        label: 'Junior High', icon: ICON_JHS,        sub: 'Grade 7 – 10' },
  { value: 'shs',        label: 'Senior High', icon: ICON_SHS,        sub: 'Grade 11 – 12' },
  { value: 'college',    label: 'College',     icon: ICON_COLLEGE,    sub: '1st – 4th Year' },
]

const stepTwoLabel = computed(() => {
  if (educationLevel.value === 'shs') return 'Strand'
  if (educationLevel.value === 'college') return 'Program'
  return 'Grade'
})

function railStepClass(stepIndex) {
  if (currentCard.value > stepIndex) return 'rail-step-done'
  if (currentCard.value === stepIndex) return 'rail-step-active'
  return ''
}

const elementaryGrades = [1,2,3,4,5,6].map(n => ({ label: `Grade ${n}`, value: n }))
const jhsGrades = [7,8,9,10].map(n => ({ label: `Grade ${n}`, value: n }))
const shsGrades = [
  { label: 'Grade 11', value: 11 },
  { label: 'Grade 12', value: 12 },
]
const shsStrands = [
  { value: 'STEM',  label: 'STEM',  full: 'Science, Tech, Engineering & Math' },
  { value: 'ABM',   label: 'ABM',   full: 'Accountancy, Business & Management' },
  { value: 'HUMSS', label: 'HUMSS', full: 'Humanities & Social Sciences' },
  { value: 'GAS',   label: 'GAS',   full: 'General Academic Strand' },
]
const collegeYears = [
  { label: '1st Year', value: 13 },
  { label: '2nd Year', value: 14 },
  { label: '3rd Year', value: 15 },
  { label: '4th Year', value: 16 },
]


// Only show actual college degree programs in the dropdown —
// excludes virtual containers like ELEMENTARY, JUNIOR_HIGH, SHS-* that
// the seed creates for internal subject grouping
const collegeCourses = computed(() =>
  courses.value.filter(c =>
    !['ELEMENTARY', 'JUNIOR_HIGH'].includes(c.course_code) &&
    !c.course_code.startsWith('SHS-')
  )
)

const collegeCourseOptions = computed(() =>
  collegeCourses.value.map(course => ({
    label: `${course.course_code} - ${course.course_name}`,
    value: course.course_code,
  }))
)

const card2Valid = computed(() => {
  if (educationLevel.value === 'elementary') return selectedGrade.value !== null
  if (educationLevel.value === 'jhs')        return selectedGrade.value !== null
  if (educationLevel.value === 'shs')        return !!selectedStrand.value && selectedGrade.value !== null
  if (educationLevel.value === 'college')    return !!selectedCourse.value && selectedCollegeYear.value !== null
  return false
})

const finalYearLevel = computed(() => {
  if (educationLevel.value === 'college') return selectedCollegeYear.value
  return selectedGrade.value
})

const card3Label = computed(() => {
  if (educationLevel.value === 'elementary') return `Grade ${selectedGrade.value}`
  if (educationLevel.value === 'jhs')        return `Grade ${selectedGrade.value}`
  if (educationLevel.value === 'shs')        return `${selectedStrand.value} — Grade ${selectedGrade.value}`
  if (educationLevel.value === 'college')    return `${selectedCourse.value} — Year ${selectedCollegeYear.value}`
  return ''
})

const recognizedCourseCode = computed(() => {
  if (educationLevel.value === 'elementary') return 'ELEMENTARY'
  if (educationLevel.value === 'jhs') return 'JUNIOR_HIGH'
  if (educationLevel.value === 'shs') return selectedStrand.value || ''
  if (educationLevel.value === 'college') return selectedCourse.value || ''
  return ''
})

const loadSubjectsForSelection = async () => {
  if (!recognizedCourseCode.value) {
    subjects.value = []
    return
  }

  subjects.value = await catalogStore.fetchSubjects({
    force: true,
    params: {
      recognized_only: 1,
      course_code: recognizedCourseCode.value,
    },
  })
}

onMounted(async () => {
  try {
    courses.value = await catalogStore.fetchCourses()
  } catch (error) {
    console.error('Failed to load onboarding data:', error)
  }
})

const selectEducationLevel = (value) => {
  educationLevel.value = value
  selectedGrade.value = null
  selectedStrand.value = ''
  selectedCourse.value = ''
  selectedCollegeYear.value = null
  store.selectedSubjects.splice(0)
}

const handleCourseChange = (courseCode) => {
  selectedCourse.value = courseCode
  store.selectedSubjects.splice(0)
}

const nextCard = () => {
  if (currentCard.value < totalCards - 1) currentCard.value++
}

const prevCard = () => {
  if (currentCard.value > 0) currentCard.value--
}

const finish = async () => {
  isSubmitting.value = true
  try {
    await api.post('profile/setup/', {
      course: selectedCourse.value || null,
      year_level: finalYearLevel.value,
      bio: 'Profile initialized via onboarding.'
    })

    await api.post('preferences/', {
      subjects: [...store.selectedSubjects]
    })

    profileStore.profileCompleted = true
    profileStore.loaded = true
    store.resetPreferences()

    router.push('/dashboard')
  } catch (error) {
    console.error('Onboarding submission failed:', error)
    toastStore.push('Could not complete onboarding. Please try again.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

watch(recognizedCourseCode, () => {
  loadSubjectsForSelection().catch((error) => {
    console.error('Failed to load recognized subjects:', error)
  })
})

</script>

<style scoped>
.onboarding-shell {
  display: flex;
  background: var(--sb-card-bg);
  border: 1px solid var(--sb-card-border);
  border-radius: 18px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.onboarding-rail {
  width: 160px;
  flex-shrink: 0;
  background: color-mix(in srgb, var(--sb-primary) 8%, var(--sb-card-bg));
  border-right: 1px solid var(--sb-card-border);
  padding: 28px 16px;
}

.rail-step {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 24px;
  font-size: 13px;
  color: var(--sb-text-muted);
}

.rail-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 1.5px solid var(--sb-card-border);
  background: var(--sb-card-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 11px;
  flex-shrink: 0;
}

.rail-step-active {
  color: var(--sb-text-main);
  font-weight: 700;
}
.rail-step-active .rail-num {
  background: var(--sb-primary);
  border-color: var(--sb-primary);
  color: #fff;
}

.rail-step-done .rail-num {
  background: var(--sb-primary);
  border-color: var(--sb-primary);
}
.rail-step-done .rail-num::after {
  content: "\2713";
  color: #fff;
  font-size: 12px;
}

.onboarding-main {
  flex: 1;
  min-width: 0;
  padding: 32px 32px 30px;
}

.option-list, .subject-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.subject-list {
  max-height: 340px;
  overflow-y: auto;
  margin-bottom: 4px;
}

.option-row, .subject-row {
  display: flex;
  align-items: center;
  gap: 14px;
  border: 1px solid var(--sb-card-border);
  border-radius: 12px;
  padding: 14px 16px;
  cursor: pointer;
  transition: border-color var(--sb-t-normal, 0.15s) ease, background-color var(--sb-t-normal, 0.15s) ease;
}

.option-row:hover, .subject-row:hover {
  border-color: var(--sb-primary);
}

.option-row-selected, .subject-row-selected {
  border-color: var(--sb-primary);
  background: color-mix(in srgb, var(--sb-primary) 7%, var(--sb-card-bg));
}

.option-icon {
  width: 26px;
  height: 26px;
  flex-shrink: 0;
  color: var(--sb-primary);
}
.option-icon :deep(svg) {
  width: 100%;
  height: 100%;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.6;
}

.option-label {
  font-weight: 700;
  font-size: 14px;
  color: var(--sb-text-main);
}
.option-sub {
  font-size: 11.5px;
  color: var(--sb-text-muted);
}

.field-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--sb-text-muted);
  margin-bottom: 8px;
}

.tile-grid {
  display: grid;
  gap: 10px;
}
.tile-grid-2 { grid-template-columns: repeat(2, 1fr); }
.tile-grid-3 { grid-template-columns: repeat(3, 1fr); }
.tile-grid-4 { grid-template-columns: repeat(4, 1fr); }

.tile {
  border: 1px solid var(--sb-card-border);
  border-radius: 12px;
  padding: 14px 8px;
  text-align: center;
  font-weight: 700;
  font-size: 13px;
  color: var(--sb-text-main);
  cursor: pointer;
  transition: border-color var(--sb-t-normal, 0.15s) ease, background-color var(--sb-t-normal, 0.15s) ease;
}
.tile:hover {
  border-color: var(--sb-primary);
}
.tile-selected {
  border-color: var(--sb-primary);
  background: color-mix(in srgb, var(--sb-primary) 8%, var(--sb-card-bg));
  color: var(--sb-primary);
}
.tile-strand {
  text-align: left;
}
.tile-strand .option-label {
  font-size: 13px;
}

.empty-state {
  text-align: center;
  padding: 28px 20px;
  border: 1px solid var(--sb-card-border);
  border-radius: 14px;
}

.subject-row {
  padding: 11px 14px;
}
.subject-checkbox {
  width: 17px;
  height: 17px;
  accent-color: var(--sb-primary);
  flex-shrink: 0;
}
.subject-code {
  font-size: 10.5px;
  font-weight: 700;
  color: var(--sb-text-muted);
  background: color-mix(in srgb, var(--sb-text-main) 8%, transparent);
  padding: 3px 8px;
  border-radius: 6px;
  flex-shrink: 0;
}
.subject-name {
  font-size: 13px;
  color: var(--sb-text-main);
}

.onboarding-accent {
  color: var(--sb-primary);
}

.onboarding-btn-primary {
  background: var(--sb-primary);
  color: #fff;
  border: none;
  border-radius: 999px;
  padding: 10px 24px;
  font-weight: 700;
  font-size: 13.5px;
}
.onboarding-btn-primary:hover:not(:disabled) {
  background: var(--sb-primary-hover);
}
.onboarding-btn-primary:disabled {
  opacity: 0.5;
}

.onboarding-btn-outline {
  background: transparent;
  border: 1px solid var(--sb-card-border);
  color: var(--sb-text-main);
  border-radius: 999px;
  padding: 10px 22px;
  font-weight: 600;
  font-size: 13.5px;
}

.onboarding-select {
  border: 1px solid var(--sb-card-border);
  border-radius: 10px;
  padding: 11px 14px;
  color: var(--sb-text-main);
  background: var(--sb-card-bg);
}

@media (max-width: 640px) {
  .onboarding-shell {
    flex-direction: column;
  }
  .onboarding-rail {
    width: 100%;
    display: flex;
    justify-content: space-between;
    padding: 16px 18px;
    border-right: none;
    border-bottom: 1px solid var(--sb-card-border);
  }
  .rail-step {
    margin-bottom: 0;
    flex-direction: column;
    gap: 4px;
    font-size: 11px;
    text-align: center;
  }
  .onboarding-main {
    padding: 24px 18px;
  }
  .tile-grid-4 {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
