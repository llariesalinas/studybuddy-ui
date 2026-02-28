<template>
  <div class="availability-content">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">My Availability</h2>
      <p class="text-muted">Set the times you are free to accept bookings.</p>
    </div>

    <div v-if="tuteeSchedStore.isLoading" class="text-center py-5 text-sb-primary">
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
            <div v-for="slot in tuteeSchedStore.availabilities" :key="slot.availability_id" class="d-flex gap-3 align-items-center">
              <div class="form-check form-switch mb-0">
                <input class="form-check-input shadow-none" type="checkbox" v-model="slot.is_active" @change="updateSlot(slot)">
              </div>
              <input type="time" v-model="slot.start_time" class="form-control form-control-sm border-sb shadow-none w-auto" @change="updateSlot(slot)">
              <span class="text-muted small">to</span>
              <input type="time" v-model="slot.end_time" class="form-control form-control-sm border-sb shadow-none w-auto" @change="updateSlot(slot)">

              <span v-if="slot.is_booked" class="badge bg-danger bg-opacity-10 text-danger border border-danger ms-2">Booked</span>

              <button v-if="!slot.is_booked" @click="removeSlot(slot)" class="btn btn-link text-danger p-0 ms-auto shadow-none">
                <i class="bi bi-trash"></i>
              </button>
            </div>

            <p v-if="tuteeSchedStore.availabilities.length === 0" class="small text-muted mb-0 font-italic">No availability set for {{ day }}.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useTuteeSchedStore } from '@/stores/tuteeSched'

const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
const tuteeSchedStore = useTuteeSchedStore()


const dayIndexMap = {
  'Monday': 0,
  'Tuesday': 1,
  'Wednesday': 2,
  'Thursday': 3,
  'Friday': 4,
  'Saturday': 5,
  'Sunday': 6
}

function getSlotDate(day) {
  const monday = new Date()

  monday.setDate(monday.getDate() - monday.getDay() + 1)

  const slotDate = new Date(monday)
  slotDate.setDate(monday.getDate() + dayIndexMap[day])

  return slotDate.toISOString().split('T')[0]
}

onMounted(async () => {
  // API_INTEGRATION_POINT: GET /api/v1/tutors/availability/
  // Fetch existing slots for the logged-in tutor
  tuteeSchedStore.fetchSchedule()
})


const addSlot = (day) => {

  const newSlot = {
    day_of_week: day,
    date: getSlotDate(day), 
    start_time: '09:00',
    end_time: '10:00',
    is_booked: false,
    is_active: true
  }

  tuteeSchedStore.addSlot(newSlot)
}

const updateSlot = (slot) => {

  const updatedSlot = {
    ...slot,
    date: getSlotDate(slot.day_of_week)
  }

  tuteeSchedStore.updateSlot(updatedSlot)
}

const removeSlot = (slot) => {
  tuteeSchedStore.deleteSlot(slot.availability_id)
}
</script>
