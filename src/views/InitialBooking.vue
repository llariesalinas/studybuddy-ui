<template>
  <div class="initial-booking-content">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">Book a Session</h2>
      <p class="text-muted">
        Tell us what you need help with, and we'll match you with the right tutor.
      </p>
    </div>

    <div class="card border-sb shadow-sm rounded-4" style="max-width: 600px;">
      <div class="card-body p-4 p-md-5">
        <form @submit.prevent="findTutor">

          <div class="mb-3">
            <label class="form-label fw-semibold small">Subject</label>
            <select v-model="store.selectedSubject" class="form-select border-sb shadow-none" required>
              <option v-for="subject in subjects" :key="subject" :value="subject">
                {{ subject }}
              </option>
            </select>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold small">Specific Topic</label>
            <input
              type="text"
              v-model="store.selectedTopic"
              class="form-control border-sb shadow-none"
              placeholder="e.g., Calculus, Thermodynamics"
              required
            />
          </div>

          <div class="row g-3 mb-3">
            <div class="col-md-6">
              <label class="form-label fw-semibold small">Date</label>
              <input
                type="date"
                v-model="store.selectedDate"
                class="form-control border-sb shadow-none"
                required
              />
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold small">Preferred Mode</label>
              <select v-model="store.selectedMode" class="form-select border-sb shadow-none" required>
                <option v-for="mode in modes" :key="mode" :value="mode">
                  {{ mode }}
                </option>
              </select>
            </div>
          </div>

          <div class="row g-3 mb-4">
            <div class="col-6">
              <label class="form-label fw-semibold small">Time From</label>
              <input
                type="time"
                v-model="store.selectedStartTime"
                class="form-control border-sb shadow-none"
                required
              />
            </div>

            <div class="col-6">
              <label class="form-label fw-semibold small">Time To</label>
              <input
                type="time"
                v-model="store.selectedEndTime"
                class="form-control border-sb shadow-none"
                required
              />
            </div>
          </div>

          <div class="text-end mt-4">
            <button
              type="submit"
              class="btn bg-sb-primary text-white px-5 py-2 rounded-3 fw-semibold shadow-sm"
            >
              Find Tutor
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useInitialBookingPrefsStore } from '@/stores/initialbookingprefs'
import axios from 'axios'

const router = useRouter()
const store = useInitialBookingPrefsStore()

const subjects = [
  'Mathematics',
  'Science',
  'English',
  'Programming',
  'Data Structures',
  'Business'
]

const modes = ['Online', 'Face-to-face']

// Submit handler
const findTutor = async() => {
  console.log('Booking Data:', {
    subject: store.selectedSubject,
    topic: store.selectedTopic,
    date: store.selectedDate,
    mode: store.selectedMode,
    startTime: store.selectedStartTime,
    endTime: store.selectedEndTime
  }) 
  router.push('/tutors')

  //Code to send booking information to backend
  // try{
  //   console.log('Booking Data:', {
  //   subject: store.selectedSubject,
  //   topic: store.selectedTopic,
  //   date: store.selectedDate,
  //   mode: store.selectedMode,
  //   startTime: store.selectedStartTime,
  //   endTime: store.selectedEndTime
  // }) 
  // await axios.post('API link goes here', {
  //   selectedSubject: store.selectedSubject,
  //   selectedTopic: store.selectedTopic,
  //   selectedDate: store.selectedDate,
  //   selectedMode: store.selectedMode,
  //   selectedStartTime: store.selectedStartTime,
  //   selectedEndTime: store.selectedEndTime
  // })

  // router.push('/tutors')
  // }
  // catch{

  // }
}
</script>
