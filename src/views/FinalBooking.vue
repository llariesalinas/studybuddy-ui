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
        <div class="card-body">

            <div class="d-flex align-items-center mb-3">
            <div class="me-4">
                <img
                src="https://via.placeholder.com/100"
                class="rounded-circle"
                width="100"
                height="100"
                />
            </div>

            <div>
                <h4 class="fw-bold mb-1">John Doe</h4>
                <p class="text-muted mb-1">Mathematics Specialist</p>
                <p class="mb-0 fw-semibold">$30/hour</p>
            </div>
            </div>

            <div class="border-top pt-3">
            <h6 class="fw-semibold">About the Tutor</h6>
            <p class="text-muted mb-0">
                Mathematics doesn’t have to be a mystery. I’m Maria, a dedicated tutor on a mission to turn "I can’t do this" into "Oh, I see it now!" With a focus on building confidence alongside core skills, I help students navigate everything from Pre-Algebra to Calculus without the stress. My goal isn't just to help you pass the next test—it's to give you the tools to tackle any problem that comes your way.
            </p>
            </div>

        </div>
    </div>

    <div class="card shadow-sm rounded-4">
      <div class="card-body">
        <h5 class="fw-semibold mb-3">Maria's Schedule</h5>
        <p><i class="bi bi-circle-fill text-success"></i> Available | <i class="bi bi-circle-fill text-danger"></i> Unavailable</p>

        <div class="table-responsive">
          <table class="table table-bordered align-middle text-center">
            <thead class="table-light">
              <tr>
                <th>Monday</th>
                <th>Tuesday</th>
                <th>Wednesday</th>
                <th>Thursday</th>
                <th>Friday</th>
                <th>Saturday</th>
                <th>Sunday</th>
              </tr>
            </thead>
            <tbody>
                <tr v-for="(row, rowIndex) in schedule" :key="rowIndex">

                    <td
                    v-for="day in days"
                    :key="day"
                    @click="row[day] && toggleSlot(`${row.time}-${day}`)"
                    :class="[
                        row[day]
                        ? 'bg-success time-cell'
                        : 'bg-danger',

                        selectedSlots.includes(`${row.time}-${day}`)
                        ? 'selected-cell'
                        : ''
                    ]"
                    >
                    {{ row.time }}
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBookingPrefsStore } from '@/stores/bookedSessions'
import axios from 'axios'

const router = useRouter()
const store = useBookingPrefsStore()

const selectedSlots = ref([])
const schedule = ref([])

/* Load schedule */
onMounted(async () => {
  try {
    const { data } = await axios.get('API link goes here')
    schedule.value = data
  } catch (error) {
    console.error("Error loading schedule", error)
  }
})

/* Toggle selection */
const toggleSlot = (slotId) => {
  if (selectedSlots.value.includes(slotId)) {
    selectedSlots.value =
      selectedSlots.value.filter(id => id !== slotId)
  } else {
    selectedSlots.value.push(slotId)
  }
}

const days = [
  'monday',
  'tuesday',
  'wednesday',
  'thursday',
  'friday',
  'saturday',
  'sunday'
]

const backButton = () => {
    router.push('/tutors')
}

const bookSessions = async () => {
    console.log('Booked Slots:', selectedSlots.value)

    store.bookedSessions = selectedSlots.value

    router.push('/')
//   try {
//     console.log('Booked Slots:', selectedSlots.value)

//     store.bookedSessions = selectedSlots.value

//     await axios.post(
//       'API link goes here',
//       {
//         slots: selectedSlots.value
//       }
//     )

//     router.push('/')
//   } catch (error) {
//     console.error('Booking failed', error)
//   }
}
</script>

<style scoped>
.time-cell {
  cursor: pointer;
  transition: 0.2s ease;
}

.time-cell:hover {
  filter: brightness(0.9);
}

.selected-cell {
  border: 2px solid #00895A !important;
  font-weight: bold;
}
</style>