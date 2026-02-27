<template>
  <div class="booking-content container py-4">

    <div class="mb-3">
        <button
            class="btn btn-outline-secondary d-flex align-items-center gap-2"
            @click="backButton"
        >
            <i class="bi bi-arrow-left"></i>
            Back
        </button>
    </div>

    <div class="mb-4">
      <h2 class="fw-bold text-dark">Book a Session With</h2>
    </div>

    <div class="card shadow-sm rounded-4 mb-4">
      <div class="card-body d-flex flex-column flex-md-row align-items-start gap-4">

        <div class="flex-shrink-0">
          <img
            src="https://via.placeholder.com/100"
            class="rounded-circle"
            width="100"
            height="100"
            alt="Tutor Profile"
          />
        </div>

        <div class="flex-grow-1 d-flex flex-column">
          
          <div class="d-flex justify-content-between align-items-start flex-wrap">
            <h4 class="fw-bold mb-1">{{ tutorDetails?.name }}</h4>
            <span class="fw-semibold mb-1">{{ tutorDetails?.rating || 0 }} ⭐</span>
          </div>

          <div class="subjects-list mb-2">
            <span
              v-for="subject in tutorDetails.subjects"
              :key="subject"
              class="badge bg-light text-dark me-1 mb-1"
            >
              {{ subject }}
            </span>
          </div>

          <p class="mb-2 fw-semibold">{{ tutorDetails.hourly_rate || 0}}/hr.</p>

          <div class="border-top pt-2 mt-2">
            <h6 class="fw-semibold mb-1">About the Tutor</h6>
            <p class="text-muted mb-0">
              {{ tutorDetails.bio || "This tutor is a bit shy..." }}
            </p>
          </div>

        </div>

      </div>
    </div>

    <div class="card shadow-sm rounded-4">
      <div class="card-body">
        <h5 class="fw-semibold mb-3">{{ tutorDetails.name }}'s Schedule</h5>
        <p><i class="bi bi-circle-fill text-success"></i> Available | <i class="bi bi-circle-fill text-danger"></i> Unavailable</p>

        <div class="table-responsive">
          <table class="table table-bordered text-center align-middle calendar-table">
            <thead class="table-light">
              <tr>
                <th v-for="day in days" :key="day">{{ day }}</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="rowIndex in maxRows" :key="rowIndex">
                <td v-for="day in days" :key="day">
                  <div
                    v-if="groupedSchedule[day][rowIndex - 1]"
                    class="slot-cell"
                    :class="{
                      available: !groupedSchedule[day][rowIndex - 1].is_booked,
                      booked: groupedSchedule[day][rowIndex - 1].is_booked,
                      selected: selectedSlots.some(
                        s => s.availability_id === groupedSchedule[day][rowIndex - 1].id
          )
        }"
        @click="toggleSlot(groupedSchedule[day][rowIndex - 1])"
      >
        {{ groupedSchedule[day][rowIndex - 1].time_slot }} -
        {{ addOneHour(groupedSchedule[day][rowIndex - 1].time_slot) }}
      </div>
    </td>
  </tr>
</tbody>
          </table>
        </div>
        <div class="text-end mt-3">
        <button
            class="btn bg-sb-primary text-white px-4 rounded-3 fw-semibold"
            :disabled="selectedSlots.length === 0"
            @click="bookSessions"
        >
            Book Selected ({{ selectedSlots.length }})
        </button>
        </div>


      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useBookingPrefsStore } from '@/stores/selectedSessions'
import { useBookedSessionStore } from '@/stores/bookedSessionDetails'
import api from '@/services/api/api'

const router = useRouter()
const route = useRoute()
const bookingPrefsStore = useBookingPrefsStore()
const bookedSessionStore = useBookedSessionStore()

const tutorID = route.params.id

const selectedSlots = ref([])
const tutorSchedule = ref([])

const days = [
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday'
]

const dayIndexMap = {
  'Monday': 0,
  'Tuesday': 1,
  'Wednesday': 2,
  'Thursday': 3,
  'Friday': 4,
  'Saturday': 5,
  'Sunday': 6
}


function addOneHour(time) {
  const [h, m] = time.split(':')
  const date = new Date()
  date.setHours(parseInt(h))
  date.setMinutes(parseInt(m))
  date.setHours(date.getHours() + 1)

  return date.toTimeString().slice(0,5)
}

function getSlotDate(slot) {
  // get Monday of the current week
  const monday = new Date()
  monday.setDate(monday.getDate() - monday.getDay() + 1)
  
  // add day offset
  const slotDate = new Date(monday)
  slotDate.setDate(monday.getDate() + dayIndexMap[slot.day])
  
  return slotDate.toISOString().split('T')[0] // YYYY-MM-DD
}

const tutorDetails = ref({
  profile_id: null,
  initials: '',
  name: '',
  year_course: 'Tutor',
  subjects: [],
  rating: 0,
  bio: '',
  hourly_rate: 0,
  total_sessions: 0
})


const getTutorDetails = async () => {
  try {
    const response = await api.get(`tutors/${tutorID}/`)
    tutorDetails.value = {
      profile_id: response.data.profile_id,
      name: `${response.data.fname} ${response.data.lname}`,
      subjects: response.data.subjects,
      rating: response.data.rating_average ?? 5.0,
      bio: response.data.bio,
      hourly_rate: response.data.hourly_rate ?? 150,
      total_sessions: response.data.total_sessions ?? 0
    }
  } catch (error) {
    console.error('Failed to load tutor details.', error)
  }
}

const getTutorSchedule = async () => {
  try {
    const response = await api.get(`tutors/${tutorID}/availability/`)
    tutorSchedule.value = response.data
  } catch (error) {
    console.error('Failed to load tutor schedule.', error)
  }
}

onMounted(async () => {
  await getTutorDetails()
  await getTutorSchedule()
})



const groupedSchedule = computed(() => {

  const result = {}

  days.forEach(day => {
    result[day] = []
  })

  tutorSchedule.value.forEach(slot => {
    if(result[slot.day]){
      result[slot.day].push(slot)
    }
  })

  return result
})

const maxRows = computed(() => {
  const lengths = days.map(day => groupedSchedule.value[day]?.length || 0)
  return lengths.length ? Math.max(...lengths) : 0
})

const toggleSlot = (slot) => {
  if (slot.is_booked) return

  const slotWithDate = {
    availability_id: slot.id,
    session_date: getSlotDate(slot),
    session_mode: "Online"
  }

  const exists = selectedSlots.value.some(
    s => s.availability_id === slot.id
  )

  if (exists) {
    selectedSlots.value = selectedSlots.value.filter(
      s => s.availability_id !== slot.id
    )
  } else {
    selectedSlots.value.push(slotWithDate)
  }
}

const backButton = () => {
    router.push('/tutors')
}

const bookSessions = async () => {
  try {

    for (const slot of selectedSlots.value) {
      await api.post('bookings/', {
        availability: slot.availability_id,
        session_date: slot.session_date,
        session_mode: slot.session_mode
      })
    }

    router.push('/payment')

  } catch (error) {
    console.error('Booking failed', error)
  }
}

</script>

<style scoped>
.slot-cell {
  padding: 8px;
  margin-bottom: 6px;
  border-radius: 6px;
  cursor: pointer;
  transition: 0.2s ease;
}

.slot-cell.available {
  background-color: #e8f7f1;
  color: #00895a;
}

.slot-cell.booked {
  background-color: #f8d7da;
  color: #842029;
  cursor: not-allowed;
}

.slot-cell.selected {
  outline: 3px solid #00895a;
  font-weight: bold;
}
.subjects-list {
  max-height: 100px; 
  overflow-y: auto;
}

.subjects-list span {
  white-space: nowrap;
}

.card-body img {
  object-fit: cover;    
}
</style>