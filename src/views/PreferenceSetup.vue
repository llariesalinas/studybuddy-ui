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
                :disabled="!store.selectedTime"
                @click="finish"
              >
                Go to Dashboard
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

const router = useRouter()
const store = usePreferenceStore()


const currentCard = ref(0)
const totalCards = 3 

const selectLevel = (level) => {
  store.selectedLevel = level
}
const levels = ['Highschool', 'University']

const selectTime = (time) => {
  store.selectedTime = time
}
const studyTimes = ['Morning', 'Afternoon', 'Evening']

const subjects = [
  'Mathematics',
  'Science',
  'English',
  'Programming',
  'Data Structures',
  'Business'
]

const toggleSubject = (subject) => {
  if (store.selectedSubjects.includes(subject)) {
    store.selectedSubjects = store.selectedSubjects.filter(s => s !== subject)
  } else {
    store.selectedSubjects.push(subject)
  }
}

const nextCard = () => {
  if (currentCard.value === 0 && store.selectedSubjects.length === 0) return
  if (currentCard.value === 1 && !store.selectedLevel) return
  if (currentCard.value === 2 && !store.selectedTime) return

  if (currentCard.value < totalCards - 1) {
    currentCard.value += 1
  } else {
    finish()
  }
}

const finish = () => {
  // Code to send preferences to backend
  console.log('User Preferences:', {
    subjects: store.selectedSubjects,
    level: store.selectedLevel,
    time: store.selectedTime
  })
  router.push('/dashboard')
}

const progressPercentage = computed(() => ((currentCard.value + 1) / totalCards) * 100)
</script>