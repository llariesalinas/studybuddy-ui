<template>
  <nav class="navbar navbar-expand-lg bg-white py-3">
    <div class="container">
      <a class="navbar-brand d-flex align-items-center fw-bold fs-4" href="#">
        <i class="bi bi-book text-sb-primary me-2"></i>
        <span class="text-dark">StudyBuddy</span>
      </a>
    </div>
  </nav>

  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-md-7">
        <div class="card border-sb shadow-sm rounded-4 p-4">

          <div class="mb-4">
            <div class="progress" style="height: 8px;">
              <div class="progress-bar bg-success" :style="{ width: progressPercentage + '%' }"></div>
            </div>
          </div>

          <div v-if="currentCard === 0">
            <div class="text-center mb-4">
              <h3 class="fw-bold text-dark">What subjects are you interested in?</h3>
              <p class="text-muted">Choose all that apply.</p>
            </div>

            <div class="row g-3 mb-4">
              <div class="col-6" v-for="subject in subjects" :key="subject">
                <div
                  class="card border rounded-4 p-3 text-center h-100"
                  :class="store.selectedSubjects.includes(subject)
                    ? 'border-success bg-success bg-opacity-10'
                    : 'border-sb'"
                  style="cursor:pointer;"
                  @click="toggleSubject(subject)"
                >
                  <h6 class="fw-bold mb-0">{{ subject }}</h6>
                </div>
              </div>
            </div>

            <div class="d-flex justify-content-end">
              <button
                type="button"
                class="btn bg-sb-primary text-white px-4 rounded-3 fw-semibold"
                :disabled="store.selectedSubjects.length === 0"
                @click="nextCard"
              >
                Continue
              </button>
            </div>
          </div>

          <div v-else-if="currentCard === 1">
            <div class="text-center mb-4">
              <h3 class="fw-bold text-dark">Select Your Level</h3>
              <p class="text-muted">Choose your proficiency level for the subjects.</p>
            </div>

            <div class="row g-3 mb-4 justify-content-center">
              <div class="col-6" v-for="level in levels" :key="level">
                <div
                  class="card border rounded-4 p-3 text-center h-100"
                  :class="store.selectedLevel === level
                    ? 'border-success bg-success bg-opacity-10'
                    : 'border-sb'"
                  style="cursor:pointer;"
                  @click="selectLevel(level)"
                >
                  <h6 class="fw-bold mb-0">{{ level }}</h6>
                </div>
              </div>
            </div>

            <div class="d-flex justify-content-end">
              <button
                class="btn bg-sb-primary text-white px-4 rounded-3 fw-semibold"
                :disabled="!store.selectedLevel"
                @click="nextCard"
              >
                Continue
              </button>
            </div>
          </div>

          <div v-else-if="currentCard === 2">
            <div class="text-center mb-4">
              <h3 class="fw-bold text-dark">Preferred Study Time</h3>
              <p class="text-muted">Select the time you prefer to study.</p>
            </div>

            <div class="row g-3 mb-4 justify-content-center">
              <div class="col-6" v-for="time in studyTimes" :key="time">
                <div
                  class="card border rounded-4 p-3 text-center h-100"
                  :class="store.selectedTime === time
                    ? 'border-success bg-success bg-opacity-10'
                    : 'border-sb'"
                  style="cursor:pointer;"
                  @click="selectTime(time)"
                >
                  <h6 class="fw-bold mb-0">{{ time }}</h6>
                </div>
              </div>
            </div>

            <div class="d-flex justify-content-end">
              <button
                class="btn bg-sb-primary text-white px-4 rounded-3 fw-semibold"
                :disabled="!store.selectedTime || isSubmitting"
                @click="finish"
              >
                <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
                {{ isSubmitting ? 'Saving...' : 'Go to Dashboard' }}
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { usePreferenceStore } from '@/stores/preferences'
import { useProfileStore } from '@/stores/profile'
import api from '@/services/api/api'

const router = useRouter()
const store = usePreferenceStore()
const profileStore = useProfileStore()

const currentCard = ref(0)
const totalCards = 3
const isSubmitting = ref(false)


// ---------- SELECT LEVEL ----------
const levels = ['Highschool', 'University']

const selectLevel = (level) => {
  store.selectedLevel = level
}


// ---------- SELECT STUDY TIME ----------
const studyTimes = ['Morning', 'Afternoon', 'Evening']

const selectTime = (time) => {
  store.selectedTime = time
}


// ---------- SUBJECT LIST ----------
const subjects = [
  'Mathematics',
  'Science',
  'English',
  'Programming',
  'Data Structures',
  'Business'
]


// ---------- TOGGLE SUBJECT ----------
const toggleSubject = (subject) => {

  if (store.selectedSubjects.includes(subject)) {

    store.selectedSubjects = store.selectedSubjects.filter(
      s => s !== subject
    )

  } else {

    store.selectedSubjects.push(subject)

  }

}


// ---------- CARD NAVIGATION ----------
const nextCard = () => {

  if (currentCard.value === 0 && store.selectedSubjects.length === 0) {
    alert("Please select at least one subject.")
    return
  }

  if (currentCard.value === 1 && !store.selectedLevel) {
    alert("Please select your study level.")
    return
  }

  if (currentCard.value === 2 && !store.selectedTime) {
    alert("Please select your preferred study time.")
    return
  }

  if (currentCard.value < totalCards - 1) {

    currentCard.value += 1

  } else {

    finish()

  }

}


// ---------- FINISH SETUP ----------
const finish = async () => {

  isSubmitting.value = true

  try {

    const payload = {

      // mapped to backend UserProfile fields
      course: store.selectedLevel,
      year_level: 1, // temporary until year-level UI added
      bio: `Prefers ${store.selectedTime} study sessions`,

    }

    // SAVE PROFILE SETUP
    await api.post('/profile/setup/', payload)

    // unlock profile guard
    profileStore.profileCompleted = true

    console.log('Preferences saved successfully')

    router.push('/dashboard')

  } catch (error) {

    console.error('Failed to save preferences:', error)

    alert('Could not save preferences. Please try again.')

  } finally {

    isSubmitting.value = false

  }

}


// ---------- PROGRESS BAR ----------
const progressPercentage = computed(() => {
  return ((currentCard.value + 1) / totalCards) * 100
})

</script>