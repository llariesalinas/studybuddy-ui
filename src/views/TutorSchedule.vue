<template>
  <div class="availability-content">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">My Availability</h2>
      <p class="text-muted">Set the times you are free to accept bookings.</p>
    </div>

    <div v-if="isLoading" class="text-center py-5 text-sb-primary">
      <div class="spinner-border" role="status"></div>
      <p class="mt-2 fw-semibold">Loading schedule...</p>
    </div>

    <div v-else class="card border-sb shadow-sm rounded-4">
      <div class="card-body p-4 p-md-5">
        <div v-for="day in daysOfWeek" :key="day" class="mb-4 pb-3 border-bottom border-sb">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h6 class="fw-bold mb-0 text-dark" style="width: 100px;">{{ day }}</h6>
            <button @click="addSlot(day)" class="btn btn-sm btn-outline-dark rounded-pill px-3">
              <i class="bi bi-plus-lg me-1"></i> Add Slot
            </button>
          </div>

          <div class="d-flex flex-column gap-2">
            <div v-for="(slot, index) in getSlotsForDay(day)" :key="index" class="d-flex gap-3 align-items-center">
              <div class="form-check form-switch mb-0">
                <input class="form-check-input shadow-none" type="checkbox" v-model="slot.is_active" @change="saveAvailability">
              </div>
              <input type="time" v-model="slot.start_time" class="form-control form-control-sm border-sb shadow-none w-auto" @change="saveAvailability">
              <span class="text-muted small">to</span>
              <input type="time" v-model="slot.end_time" class="form-control form-control-sm border-sb shadow-none w-auto" @change="saveAvailability">

              <span v-if="slot.is_booked" class="badge bg-danger bg-opacity-10 text-danger border border-danger ms-2">Booked</span>

              <button v-if="!slot.is_booked" @click="removeSlot(day, index)" class="btn btn-link text-danger p-0 ms-auto shadow-none">
                <i class="bi bi-trash"></i>
              </button>
            </div>

            <p v-if="getSlotsForDay(day).length === 0" class="small text-muted mb-0 font-italic">No availability set for {{ day }}.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const isLoading = ref(true)
const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

// ERD Mapping: TUTOR_AVAILABILITY
const availabilities = ref([])

onMounted(async () => {
  // API_INTEGRATION_POINT: GET /api/v1/tutors/availability/
  // Fetch existing slots for the logged-in tutor
  setTimeout(() => {
    availabilities.value = [
      { availability_id: 1, day_of_week: 'Monday', start_time: '10:00', end_time: '12:00', is_booked: false, is_active: true },
      { availability_id: 2, day_of_week: 'Wednesday', start_time: '14:00', end_time: '16:00', is_booked: true, is_active: true }
    ]
    isLoading.value = false
  }, 600)
})

const getSlotsForDay = (day) => availabilities.value.filter(s => s.day_of_week === day)

const addSlot = (day) => {
  availabilities.value.push({
    availability_id: null, // Null means it's a new unsaved record for Django
    day_of_week: day,
    start_time: '09:00',
    end_time: '10:00',
    is_booked: false,
    is_active: true
  })
}

const removeSlot = (day, index) => {
  const daySlots = getSlotsForDay(day)
  const slotToRemove = daySlots[index]
  // In reality, if availability_id is not null, trigger a DELETE request here
  availabilities.value = availabilities.value.filter(s => s !== slotToRemove)
}

const saveAvailability = async () => {
  // API_INTEGRATION_POINT: PATCH or POST /api/v1/tutors/availability/
  // Fires off quietly in the background when they tweak a time or toggle switch
  console.log('Syncing schedule to database...', availabilities.value)
}
</script>
