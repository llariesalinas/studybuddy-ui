<template>
    <div class="p-4">
        <div class="mb-4">
            <h2 class="fw-bold text-dark">Find Tutors</h2>
            <p class="text-muted">Browse peer tutors matched to your learning needs.</p>
        </div>

        <form @submit.prevent="searchTutor">
            <div class="row mb-5 g-1 justify-content-center">
            <div class="col-md-2">
                <label class="form-label fw-semibold small">Subject</label>
                <select v-model="initialbookStore.selectedSubject" class="form-select">
                <option disabled value="">Select Subject</option>
                <option
                    v-for="subject in subjects"
                    :key="subject.subject_code"
                    :value="subject.subject_code"
                >
                    {{ subject.subject_name  }}
                </option>
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label fw-semibold small">Mode</label>
                <select v-model="initialbookStore.selectedMode" class="form-select border-sb shadow-none py-2">
                    <option 
                    v-for="mode in modes"
                    :key="mode"
                    :value="mode">{{ mode }}</option>
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label fw-semibold small">Date</label>
                <input type="date" v-model="initialbookStore.selectedDate" class="form-control border-sb shadow-none" required />
            </div>
            <div class="col" style="flex: 0 0 12.5%; max-width: 12.5%;">
                <label class="form-label fw-semibold small">From</label>
                <button
                  type="button"
                  class="btn w-100 text-start border-sb shadow-none time-trigger"
                  :class="{ 'time-trigger-active': activePicker === 'start' }"
                  @click="openTimePicker('start')"
                >
                  {{ selectedStartLabel }}
                </button>
            </div>
            <div class="col" style="flex: 0 0 12.5%; max-width: 12.5%;">
                <label class="form-label fw-semibold small">To</label>
                <button
                  type="button"
                  class="btn w-100 text-start border-sb shadow-none time-trigger"
                  :class="{ 'time-trigger-active': activePicker === 'end' }"
                  @click="openTimePicker('end')"
                >
                  {{ selectedEndLabel }}
                </button>
            </div>
            <div class="col-md-1">
                <label class="form-label fw-semibold small invisible">Search</label>
                <button type="submit" class="btn bg-sb-primary text-white px-3 rounded-3 fw-semibold shadow-sm"
                :disabled="isSubmitting">
                    Search
                </button>
            </div> 
        </div>
        </form>

        <div v-if="activePicker" class="time-grid-panel border-sb rounded-4 p-3 mb-4">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <div>
              <div class="fw-semibold text-dark">
                {{ activePicker === 'start' ? 'Choose Start Time' : 'Choose End Time' }}
              </div>
              <div class="small text-muted">
                {{ activePicker === 'start' ? 'Pick when the session begins.' : 'Pick when the session ends.' }}
              </div>
            </div>
            <button
              type="button"
              class="btn btn-sm btn-link text-decoration-none text-muted"
              @click="activePicker = null"
            >
              Close
            </button>
          </div>

          <div class="segmented-control mb-3">
            <button
              v-for="period in ['AM', 'PM']"
              :key="period"
              type="button"
              class="segmented-option"
              :class="{ 'segmented-option-active': activePeriod === period }"
              @click="activePeriod = period"
            >
              {{ period }}
            </button>
          </div>

          <div class="time-grid">
            <button
              v-for="slot in visibleTimeSlots"
              :key="`${activePicker}-${slot.value}`"
              type="button"
              class="time-chip"
              :class="{ 'time-chip-active': isSelectedTime(slot.value) }"
              @click="selectTime(slot.value)"
            >
              {{ slot.label }}
            </button>
          </div>

          <p v-if="activePicker === 'end' && !visibleTimeSlots.length" class="small text-muted mb-0 mt-3">
            Choose a start time first to see valid end times.
          </p>
        </div>
        

        <div v-if="isLoading" class="text-center py-5">
            <div class="spinner-border text-sb-primary" role="status"></div>
            <p class="text-muted mt-2">Running matching algorithm...</p>
        </div>

        <div v-else class="row g-4">
            <div class="col-md-6" v-for="tutor in matchedTutors" :key="tutor.profile_id">
                <div class="card border-sb shadow-sm rounded-4 h-100">
                    <div class="card-body p-4">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <div class="d-flex align-items-center gap-3">
                                <div class="bg-success bg-opacity-10 text-sb-primary fw-bold rounded-circle d-flex align-items-center justify-content-center"
                                    style="width: 48px; height: 48px;">
                                    {{ tutor.initials }}
                                </div>
                                <div>
                                    <h6 class="fw-bold mb-0 text-dark">{{ tutor.name }}</h6>
                                    <p class="text-muted small mb-0">{{ tutor.year_course }}</p>
                                </div>
                            </div>
                            <div class="text-end">
                                <span class="fw-bold text-warning d-flex align-items-center">
                                    <i class="bi bi-star-fill me-1"></i> {{ tutor.rating }}
                                </span>
                            </div>
                        </div>

                        <p class="small text-dark mb-3">{{ tutor.bio }}</p>

                        <div class="d-flex gap-2 mb-4 flex-wrap">
                            <span v-for="subject in tutor.subjects" :key="subject"
                                class="badge bg-light text-dark border border-sb">
                                {{ subject }}
                            </span>
                        </div>

                        <div class="d-flex justify-content-between align-items-center mt-auto">
                            <div class="small">
                                <span class="fw-bold text-dark">₱{{ tutor.hourly_rate }}</span><span
                                    class="text-muted">/hr</span>
                                <span class="text-muted ms-2">· {{ tutor.total_sessions }} sessions</span>
                            </div>
                            <button 
                                @click="toTutorDetails(tutor)"
                                class="btn bg-sb-primary text-white px-4 rounded-3 fw-semibold shadow-sm"
                                >
                                Book Session
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api/api'
import { computed, ref, onMounted } from 'vue'

import { useAuthStore } from '@/stores/auth'
import { useInitialBookingPrefsStore } from '@/stores/initialbookingprefs'
import { useBookedSessionStore } from '@/stores/bookedSessionDetails'

const route = useRoute()
const router = useRouter()

const authStore = useAuthStore()
const initialbookStore = useInitialBookingPrefsStore()
const bookedSessionStore = useBookedSessionStore()

const isLoading = ref(true)
const isSubmitting = ref(false)
const activePicker = ref(null)
const activePeriod = ref('AM')

const matchedTutors = ref([])
const subjects = ref([])

const modes = ['Online', 'Face-to-face']
const timeSlotOptions = computed(() => {
  const slots = []

  for (let hour = 0; hour < 24; hour += 1) {
    for (let minute = 0; minute < 60; minute += 30) {
      const value = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
      const period = hour >= 12 ? 'PM' : 'AM'
      const displayHour = hour % 12 || 12
      const displayMinute = String(minute).padStart(2, '0')

      slots.push({
        value,
        label: `${displayHour}:${displayMinute} ${period}`
      })
    }
  }

  return slots
})
const selectedStartLabel = computed(() => formatTimeLabel(initialbookStore.selectedStartTime, 'Select start time'))
const selectedEndLabel = computed(() => formatTimeLabel(initialbookStore.selectedEndTime, 'Select end time'))
const visibleTimeSlots = computed(() => {
  return timeSlotOptions.value.filter(slot => {
    const slotPeriod = Number(slot.value.slice(0, 2)) < 12 ? 'AM' : 'PM'

    if (slotPeriod !== activePeriod.value) {
      return false
    }

    if (activePicker.value === 'end' && initialbookStore.selectedStartTime) {
      return slot.value > initialbookStore.selectedStartTime
    }

    return true
  })
})

function formatTimeLabel(value, fallback) {
  if (!value) {
    return fallback
  }

  const slot = timeSlotOptions.value.find(option => option.value === value)
  return slot ? slot.label : fallback
}

function isSelectedTime(value) {
  if (activePicker.value === 'start') {
    return initialbookStore.selectedStartTime === value
  }

  return initialbookStore.selectedEndTime === value
}

function openTimePicker(picker) {
  activePicker.value = activePicker.value === picker ? null : picker

  const currentValue = picker === 'start'
    ? initialbookStore.selectedStartTime
    : initialbookStore.selectedEndTime

  if (currentValue) {
    activePeriod.value = Number(currentValue.slice(0, 2)) < 12 ? 'AM' : 'PM'
    return
  }

  if (picker === 'end' && initialbookStore.selectedStartTime) {
    activePeriod.value = Number(initialbookStore.selectedStartTime.slice(0, 2)) < 12 ? 'AM' : 'PM'
    return
  }

  activePeriod.value = 'AM'
}

function nextTimeSlot(value) {
  const index = timeSlotOptions.value.findIndex(slot => slot.value === value)

  if (index === -1 || index === timeSlotOptions.value.length - 1) {
    return null
  }

  return timeSlotOptions.value[index + 1].value
}

function selectTime(value) {
  if (activePicker.value === 'start') {
    initialbookStore.selectedStartTime = value

    if (!initialbookStore.selectedEndTime || initialbookStore.selectedEndTime <= value) {
      initialbookStore.selectedEndTime = nextTimeSlot(value)
    }

    activePicker.value = 'end'

    if (initialbookStore.selectedEndTime) {
      activePeriod.value = Number(initialbookStore.selectedEndTime.slice(0, 2)) < 12 ? 'AM' : 'PM'
    }

    return
  }

  initialbookStore.selectedEndTime = value
  activePicker.value = null
}


/*
CBF Tutor Search
*/
const searchTutor = async () => {

  isSubmitting.value = true
  isLoading.value = true

  try {

    const response = await api.post('/recommend-tutors/', {

      subject: initialbookStore.selectedSubject,
      preferred_mode: initialbookStore.selectedMode

    })

    matchedTutors.value = response.data.map(tutor => ({

      profile_id: tutor.id,

      initials: tutor.name
        .split(' ')
        .map(n => n[0])
        .join(''),

      name: tutor.name,

      year_course: 'Tutor',

      rating: tutor.rating ?? 5.0,

      bio: 'Peer tutor available.',

      subjects: tutor.subjects ?? [],

      hourly_rate: tutor.hourly_rate ?? 150,

      total_sessions: tutor.total_sessions ?? 0,

      score: tutor.score

    }))

  } catch (error) {

    console.error('CBF search failed:', error)

  } finally {

    isSubmitting.value = false
    isLoading.value = false

  }

}


/*
Navigate to tutor details
*/
const toTutorDetails = (tutor) => {

  bookedSessionStore.bookedSessionTutorID = tutor.profile_id
  bookedSessionStore.bookedSessionTutorName = tutor.name
  bookedSessionStore.bookedSessionSub = initialbookStore.selectedSubject
  bookedSessionStore.bookedSessionMode = initialbookStore.selectedMode

  router.push(`/tutor/${tutor.profile_id}`)
}


/*
Initial page load
*/
onMounted(async () => {

  try {

    const res = await api.get('/subjects/')
    subjects.value = res.data

  } catch (error) {

    console.error("Failed to load subjects", error)

  }

  if (route.query.subject) {
    initialbookStore.selectedSubject = route.query.subject
  }

  if (initialbookStore.selectedSubject) {
    await searchTutor()
  } else {
    isLoading.value = false
  }

})
</script>

<style scoped>
.time-trigger {
  min-height: 42px;
  background: #fff;
  color: #212529;
}

.time-trigger-active {
  border-color: var(--sb-primary, #00895a);
  box-shadow: 0 0 0 0.15rem rgba(0, 137, 90, 0.12);
}

.time-grid-panel {
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.95), rgba(255, 255, 255, 1));
}

.segmented-control {
  display: inline-grid;
  grid-template-columns: repeat(2, minmax(80px, 1fr));
  padding: 4px;
  border-radius: 999px;
  background: #edf2f7;
  gap: 4px;
}

.segmented-option {
  border: 0;
  background: transparent;
  border-radius: 999px;
  padding: 0.5rem 1rem;
  font-weight: 600;
  color: #4a5568;
}

.segmented-option-active {
  background: #ffffff;
  color: var(--sb-primary, #00895a);
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
}

.time-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(96px, 1fr));
  gap: 0.65rem;
}

.time-chip {
  border: 1px solid #d7dee7;
  background: #fff;
  border-radius: 14px;
  padding: 0.7rem 0.5rem;
  font-weight: 600;
  color: #243142;
}

.time-chip-active {
  border-color: var(--sb-primary, #00895a);
  background: rgba(0, 137, 90, 0.1);
  color: var(--sb-primary, #00895a);
}
</style>
