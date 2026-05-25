<template>
  <nav class="navbar navbar-expand-lg bg-white py-3 border-bottom shadow-sm">
    <div class="container">
      <span class="navbar-brand fw-bold text-success fs-4">StudyBuddy Onboarding</span>
    </div>
  </nav>

  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-md-7">
        <div class="card shadow-lg rounded-4 p-4 border-0 bg-white">

          <!-- Progress Bar -->
          <div class="mb-4">
            <div class="progress" style="height: 8px;">
              <div
                class="progress-bar bg-success progress-bar-striped progress-bar-animated"
                :style="{ width: progressPercentage + '%' }"
              ></div>
            </div>
            <div class="text-end text-muted small mt-2">
              Step {{ currentCard + 1 }} of {{ totalCards }}
            </div>
          </div>

          <!-- CARD 1: Education Level Category -->
          <div v-if="currentCard === 0">
            <div class="text-center mb-4">
              <h3 class="fw-bold text-dark">What is your Education Level?</h3>
              <p class="text-muted">Select the category that best describes where you are now.</p>
            </div>
            <div class="row g-3">
              <div class="col-6" v-for="level in educationLevels" :key="level.value">
                <div
                  class="card border rounded-4 p-4 text-center h-100 select-card"
                  :class="educationLevel === level.value
                    ? 'border-success bg-success bg-opacity-10 shadow-sm'
                    : 'bg-light'"
                  @click="selectEducationLevel(level.value)"
                >
                  <span class="fs-3 mb-1">{{ level.icon }}</span>
                  <span class="fw-bold text-dark small">{{ level.label }}</span>
                  <span class="text-muted" style="font-size: 11px;">{{ level.sub }}</span>
                </div>
              </div>
            </div>
            <div class="d-flex justify-content-end mt-4">
              <button
                class="btn btn-success px-4 py-2 rounded-3 fw-bold shadow-sm"
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
              <div class="text-center mb-4">
                <h3 class="fw-bold text-dark">Select Your Grade Level</h3>
                <p class="text-muted">Elementary School — Grades 1 to 6</p>
              </div>
              <div class="row g-3">
                <div class="col-4" v-for="g in elementaryGrades" :key="g.value">
                  <div
                    class="card border rounded-4 p-3 text-center select-card"
                    :class="selectedGrade === g.value
                      ? 'border-success bg-success bg-opacity-10 shadow-sm'
                      : 'bg-light'"
                    @click="selectedGrade = g.value; store.selectedSubjects.splice(0)"
                  >
                    <span class="fw-bold text-dark">{{ g.label }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- JHS: Grade 7–10 -->
            <div v-if="educationLevel === 'jhs'">
              <div class="text-center mb-4">
                <h3 class="fw-bold text-dark">Select Your Grade Level</h3>
                <p class="text-muted">Junior High School — Grades 7 to 10</p>
              </div>
              <div class="row g-3">
                <div class="col-6" v-for="g in jhsGrades" :key="g.value">
                  <div
                    class="card border rounded-4 p-4 text-center select-card"
                    :class="selectedGrade === g.value
                      ? 'border-success bg-success bg-opacity-10 shadow-sm'
                      : 'bg-light'"
                    @click="selectedGrade = g.value; store.selectedSubjects.splice(0)"
                  >
                    <span class="fw-bold text-dark">{{ g.label }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- SHS: Strand Selection -->
            <div v-if="educationLevel === 'shs'">
              <div class="text-center mb-4">
                <h3 class="fw-bold text-dark">Select Your SHS Strand</h3>
                <p class="text-muted">Senior High School — Grade 11 or 12</p>
              </div>
              <div class="row g-3 mb-3">
                <div class="col-6" v-for="s in shsStrands" :key="s.value">
                  <div
                    class="card border rounded-4 p-4 text-center select-card"
                    :class="selectedStrand === s.value
                      ? 'border-success bg-success bg-opacity-10 shadow-sm'
                      : 'bg-light'"
                    @click="selectedStrand = s.value; store.selectedSubjects.splice(0)"
                  >
                    <span class="fw-bold text-dark small">{{ s.label }}</span>
                    <span class="text-muted" style="font-size: 11px;">{{ s.full }}</span>
                  </div>
                </div>
              </div>
              <div class="mb-2">
                <label class="form-label fw-semibold text-secondary small">GRADE LEVEL</label>
                <div class="d-flex gap-3">
                  <div
                    v-for="g in shsGrades" :key="g.value"
                    class="card border rounded-3 p-3 text-center flex-grow-1 select-card"
                    :class="selectedGrade === g.value
                      ? 'border-success bg-success bg-opacity-10'
                      : 'bg-light'"
                    @click="selectedGrade = g.value"
                  >
                    <span class="fw-bold text-dark">{{ g.label }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- College: Course + Year Level -->
            <div v-if="educationLevel === 'college'">
              <div class="text-center mb-4">
                <h3 class="fw-bold text-dark">Select Your College Program</h3>
                <p class="text-muted">Choose your degree and current year level.</p>
              </div>
              <div class="mb-4">
                <label class="form-label fw-semibold text-secondary small">DEGREE PROGRAM</label>
                <select
                  class="form-select form-select-lg rounded-3 border"
                  v-model="selectedCourse"
                  @change="store.selectedSubjects.splice(0)"
                >
                  <option value="" disabled>-- Select your Course --</option>
                  <option
                    v-for="course in courses"
                    :key="course.course_code"
                    :value="course.course_code"
                  >
                    {{ course.course_code }} — {{ course.course_name }}
                  </option>
                </select>
              </div>
              <div>
                <label class="form-label fw-semibold text-secondary small">YEAR LEVEL</label>
                <div class="row g-2">
                  <div class="col-3" v-for="y in collegeYears" :key="y.value">
                    <div
                      class="card border rounded-3 p-3 text-center select-card"
                      :class="selectedCollegeYear === y.value
                        ? 'border-success bg-success bg-opacity-10'
                        : 'bg-light'"
                      @click="selectedCollegeYear = y.value"
                    >
                      <span class="fw-bold text-dark small">{{ y.label }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="d-flex justify-content-between mt-4">
              <button class="btn btn-outline-secondary px-4 py-2 rounded-3" @click="prevCard">
                Back
              </button>
              <button
                class="btn btn-success px-4 py-2 rounded-3 fw-bold shadow-sm"
                :disabled="!card2Valid"
                @click="nextCard"
              >
                Continue
              </button>
            </div>
          </div>

          <!-- CARD 3: Subject Selection -->
          <div v-if="currentCard === 2">
            <div class="text-center mb-4">
              <h3 class="fw-bold text-dark">Choose Your Target Subjects</h3>
              <p class="text-muted">
                Showing subjects for
                <strong class="text-success">{{ card3Label }}</strong>.
              </p>
            </div>

            <div
              v-if="filteredSubjects.length === 0"
              class="text-center py-4 bg-light rounded-4 border text-secondary"
            >
              <p class="fw-semibold text-danger mb-1">⚠️ No subjects found for this selection.</p>
              <p class="small mb-0">Contact your administrator to seed subjects for this level.</p>
            </div>

            <div v-else class="row g-2 overflow-auto mb-4" style="max-height: 320px;">
              <div class="col-12" v-for="subject in filteredSubjects" :key="subject.subject_code">
                <div
                  class="card border rounded-3 p-3 d-flex flex-row align-items-center
                         justify-content-between select-card"
                  :class="store.selectedSubjects.includes(subject.subject_code)
                    ? 'border-success bg-success bg-opacity-10 shadow-sm'
                    : ''"
                  @click="toggleSubject(subject.subject_code)"
                >
                  <div class="d-flex align-items-center">
                    <span class="badge bg-secondary me-2 px-2">{{ subject.subject_code }}</span>
                    <div>
                      <span class="fw-semibold text-dark d-block">{{ subject.subject_name }}</span>
                      <span class="text-muted small">{{ subject.department }}</span>
                    </div>
                  </div>
                  <input
                    class="form-check-input checkbox-success"
                    type="checkbox"
                    :checked="store.selectedSubjects.includes(subject.subject_code)"
                    @click.stop="toggleSubject(subject.subject_code)"
                  >
                </div>
              </div>
            </div>

            <div class="d-flex justify-content-between mt-4">
              <button class="btn btn-outline-secondary px-4 py-2 rounded-3" @click="prevCard">
                Back
              </button>
              <button
                class="btn btn-success px-5 py-2 rounded-3 fw-bold shadow-sm"
                :disabled="store.selectedSubjects.length === 0 || isSubmitting"
                @click="finish"
              >
                <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
                Complete Onboarding 🚀
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api/api'
import { usePreferenceStore } from '@/stores/preferences'
import { useProfileStore } from '@/stores/profile'

const router = useRouter()
const store = usePreferenceStore()
const profileStore = useProfileStore()

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
const educationLevels = [
  { value: 'elementary', label: 'Elementary',      icon: '🏫', sub: 'Grade 1 – 6' },
  { value: 'jhs',        label: 'Junior High',     icon: '📚', sub: 'Grade 7 – 10' },
  { value: 'shs',        label: 'Senior High',     icon: '🎓', sub: 'Grade 11 – 12' },
  { value: 'college',    label: 'College',          icon: '🏛️', sub: '1st – 4th Year' },
]

const elementaryGrades = [1,2,3,4,5,6].map(n => ({
  label: `Grade ${n}`, value: n
}))

const jhsGrades = [7,8,9,10].map(n => ({
  label: `Grade ${n}`, value: n
}))

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
  { label: '1st Year', value: 1 },
  { label: '2nd Year', value: 2 },
  { label: '3rd Year', value: 3 },
  { label: '4th Year', value: 4 },
]

// ── Department Filter Map ────────────────────────────────────
// Keys match the filter key returned by computedFilterKey
// Values are the department strings in the Subjects table
const SUBJECT_FILTER_MAP = {
  // Elementary
  'grade-1':  ['Grade 1'],
  'grade-2':  ['Grade 2'],
  'grade-3':  ['Grade 3'],
  'grade-4':  ['Grade 4'],
  'grade-5':  ['Grade 5'],
  'grade-6':  ['Grade 6'],
  // JHS
  'grade-7':  ['Grade 7'],
  'grade-8':  ['Grade 8'],
  'grade-9':  ['Grade 9'],
  'grade-10': ['Grade 10'],
  // SHS Strands
  'STEM':     ['STEM'],
  'ABM':      ['ABM'],
  'HUMSS':    ['HUMSS'],
  'GAS':      ['GAS'],
  // College Courses
  'BSCS':     ['Computer Science', 'Mathematics', 'English'],
  'BSIT':     ['Information Technology', 'Computer Science', 'English'],
  'BSBA':     ['Business', 'Accountancy', 'English'],
}

// ── Computed Filter Key ──────────────────────────────────────
const computedFilterKey = computed(() => {
  if (educationLevel.value === 'elementary' && selectedGrade.value) {
    return `grade-${selectedGrade.value}`
  }
  if (educationLevel.value === 'jhs' && selectedGrade.value) {
    return `grade-${selectedGrade.value}`
  }
  if (educationLevel.value === 'shs' && selectedStrand.value) {
    return selectedStrand.value
  }
  if (educationLevel.value === 'college' && selectedCourse.value) {
    return selectedCourse.value
  }
  return null
})

const filteredSubjects = computed(() => {
  const key = computedFilterKey.value
  if (!key) return []
  const allowedDepts = SUBJECT_FILTER_MAP[key] ?? []
  return subjects.value.filter(s => allowedDepts.includes(s.department))
})

// ── Card 2 Validation ────────────────────────────────────────
const card2Valid = computed(() => {
  if (educationLevel.value === 'elementary') return selectedGrade.value !== null
  if (educationLevel.value === 'jhs')        return selectedGrade.value !== null
  if (educationLevel.value === 'shs')        return !!selectedStrand.value && selectedGrade.value !== null
  if (educationLevel.value === 'college')    return !!selectedCourse.value && selectedCollegeYear.value !== null
  return false
})

// ── Computed year_level for submission ───────────────────────
const finalYearLevel = computed(() => {
  if (educationLevel.value === 'college') return selectedCollegeYear.value
  return selectedGrade.value
})

// ── Card 3 Label ─────────────────────────────────────────────
const card3Label = computed(() => {
  if (educationLevel.value === 'elementary') return `Grade ${selectedGrade.value}`
  if (educationLevel.value === 'jhs')        return `Grade ${selectedGrade.value}`
  if (educationLevel.value === 'shs')        return `${selectedStrand.value} — Grade ${selectedGrade.value}`
  if (educationLevel.value === 'college')    return `${selectedCourse.value} — Year ${selectedCollegeYear.value}`
  return ''
})

// ── Progress ─────────────────────────────────────────────────
const progressPercentage = computed(() =>
  ((currentCard.value + 1) / totalCards) * 100
)

// ── Lifecycle ────────────────────────────────────────────────
onMounted(async () => {
  try {
    const [subjectRes, courseRes] = await Promise.all([
      api.get('subjects/'),
      api.get('courses/')
    ])
    subjects.value = subjectRes.data
    courses.value = courseRes.data
  } catch (error) {
    console.error('Failed to load onboarding data:', error)
  }
})

// ── Navigation ───────────────────────────────────────────────
const selectEducationLevel = (value) => {
  educationLevel.value = value
  selectedGrade.value = null
  selectedStrand.value = ''
  selectedCourse.value = ''
  selectedCollegeYear.value = null
  store.selectedSubjects.splice(0)
}

const nextCard = () => {
  if (currentCard.value < totalCards - 1) currentCard.value++
}

const prevCard = () => {
  if (currentCard.value > 0) currentCard.value--
}

const toggleSubject = (code) => {
  const index = store.selectedSubjects.indexOf(code)
  if (index > -1) store.selectedSubjects.splice(index, 1)
  else store.selectedSubjects.push(code)
}

// ── Submit ───────────────────────────────────────────────────
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
    alert('Could not complete onboarding. Please try again.')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.select-card {
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}
.select-card:hover {
  border-color: #198754 !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
.checkbox-success:checked {
  background-color: #198754;
  border-color: #198754;
}
</style>
