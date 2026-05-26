<template>

  <!-- NAVBAR -->
  <nav class="navbar navbar-expand-lg sb-surface py-3">
    <div class="container d-flex justify-content-between align-items-center">
      <a class="navbar-brand fw-bold fs-4 sb-text">
        StudyBuddy
      </a>
      <SbThemeToggle />
    </div>
  </nav>

  <div class="container py-5">

    <div class="row justify-content-center">

      <div class="col-md-7">

        <div class="card sb-card-surface sb-text shadow-sm rounded-4 p-4">

          <!-- PROGRESS -->
          <div class="mb-4">
            <SbStepBar :current="currentCard + 1" :total="totalCards" />
          </div>


          <!-- CARD 1 SUBJECTS -->
          <div v-if="currentCard === 0">

            <div class="text-center mb-4">
              <h3 class="fw-bold">What subjects are you interested in?</h3>
              <p class="sb-muted">Choose all that apply</p>
            </div>

            <div class="row g-3 mb-4">

              <div
                class="col-6"
                v-for="subject in subjects"
                :key="subject.subject_code"
              >

                <div
                  class="card sb-card-surface border rounded-4 p-3 text-center h-100 subject-card sb-interactive"
                  style="cursor:pointer"
                  :class="store.selectedSubjects.includes(subject.subject_code)
                    ? 'border-success bg-success bg-opacity-10'
                    : ''"
                  @click="toggleSubject(subject.subject_code)"
                >

                  <h6 class="fw-bold mb-0">
                    {{ subject.subject_name }}
                  </h6>

                </div>

              </div>

            </div>

            <div class="d-flex justify-content-end">

              <button
                class="btn btn-success px-4 sb-btn"
                :disabled="store.selectedSubjects.length === 0"
                @click="nextCard"
              >
                Continue
              </button>

            </div>

          </div>


          <!-- CARD 2 YEAR LEVEL -->
          <div v-else-if="currentCard === 1">

            <div class="text-center mb-4">
              <h3 class="fw-bold">Select Your Year Level</h3>
              <p class="sb-muted">Choose your current academic level</p>
            </div>

            <div class="mb-4">

              <select class="form-select" v-model="yearLevel">

                <option disabled value="">Select Year Level</option>

                <option
                  v-for="level in yearLevels"
                  :key="level.value"
                  :value="level.value"
                >
                  {{ level.label }}
                </option>

              </select>

            </div>

            <div class="d-flex justify-content-end">

              <button
                class="btn btn-success px-4 sb-btn"
                :disabled="!yearLevel"
                @click="nextCard"
              >
                Continue
              </button>

            </div>

          </div>


          <!-- CARD 3 COURSE -->
          <div v-else-if="currentCard === 2">

            <div class="text-center mb-4">
              <h3 class="fw-bold">Select Your Course</h3>
              <p class="sb-muted">Choose your academic program</p>
            </div>

            <div class="mb-4">

              <select class="form-select" v-model="selectedCourse">

                <option disabled value="">Select Course</option>

                <option
                  v-for="course in courses"
                  :key="course.course_code"
                  :value="course.course_code"
                >
                  {{ course.course_name }}
                </option>

              </select>

            </div>

            <div class="d-flex justify-content-end">

              <button
                class="btn btn-success px-4 sb-btn"
                :disabled="!selectedCourse || isSubmitting"
                @click="finish"
              >
                {{ isSubmitting ? "Saving..." : "Go to Dashboard" }}
              </button>

            </div>

          </div>

        </div>

      </div>

    </div>

  </div>

</template>

<script setup>

import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePreferenceStore } from '@/stores/preferences'
import { useProfileStore } from '@/stores/profile'
import api from '@/services/api/api'
import SbStepBar from '@/components/SbStepBar.vue'
import SbThemeToggle from '@/components/SbThemeToggle.vue'
import { useToastStore } from '@/stores/toast'

const router = useRouter()
const store = usePreferenceStore()
const profileStore = useProfileStore()
const toastStore = useToastStore()

const currentCard = ref(0)
const totalCards = 3
const isSubmitting = ref(false)

const subjects = ref([])
const courses = ref([])

const yearLevel = ref('')
const selectedCourse = ref('')

/* YEAR LEVEL OPTIONS */

const yearLevels = [

  { label: "Grade 1", value: 1 },
  { label: "Grade 2", value: 2 },
  { label: "Grade 3", value: 3 },
  { label: "Grade 4", value: 4 },
  { label: "Grade 5", value: 5 },
  { label: "Grade 6", value: 6 },
  { label: "Grade 7", value: 7 },
  { label: "Grade 8", value: 8 },
  { label: "Grade 9", value: 9 },
  { label: "Grade 10", value: 10 },
  { label: "Grade 11", value: 11 },
  { label: "Grade 12", value: 12 },

  { label: "1st Year College", value: 13 },
  { label: "2nd Year College", value: 14 },
  { label: "3rd Year College", value: 15 },
  { label: "4th Year College", value: 16 }

]

/* LOAD DATA */

onMounted(async () => {

  try {

    const subjectRes = await api.get('subjects/')
    subjects.value = subjectRes.data

    const courseRes = await api.get('courses/')
    courses.value = courseRes.data

  } catch (error) {

    console.error("Failed loading setup data", error)

  }

})

/* SUBJECT TOGGLE */

const toggleSubject = (code) => {

  const index = store.selectedSubjects.indexOf(code)

  if (index > -1) {
    store.selectedSubjects.splice(index, 1)
  } else {
    store.selectedSubjects.push(code)
  }

}

/* NEXT CARD */

const nextCard = () => {

  if (currentCard.value < totalCards - 1) {
    currentCard.value++
  }

}

/* FINISH SETUP */

const finish = async () => {

  isSubmitting.value = true

  try {

    await api.post('profile/setup/', {
      course: selectedCourse.value,
      year_level: yearLevel.value,
      bio: "Student profile"
    })

    await api.post("preferences/", {
       subjects: [...store.selectedSubjects]
    })

    profileStore.profileCompleted = true
    profileStore.loaded = true

    store.resetPreferences()

    router.push('/dashboard')

  } catch (error) {

    console.error("Failed saving preferences", error)
    toastStore.push("Could not save preferences", 'error')

  } finally {

    isSubmitting.value = false

  }

}

</script>
