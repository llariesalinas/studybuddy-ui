<template>
  <div class="availability-content">
    <div class="d-flex justify-content-between align-items-start mb-4">
      <div>
        <h2 class="fw-bold text-dark mb-1">My Availability</h2>
        <p class="text-muted mb-0">
          Set the times you are free to accept bookings.
        </p>
      </div>

      <button
        class="btn btn-success align-self-center"
        @click="showAddModal = true"
      >
        + Add Session
      </button>
    </div>
    <h4 class="fw-bold mt-4">Current Week</h4>

    <div class="table-responsive">
      <table class="table table-bordered text-center">
        <thead>
          <tr>
            <th v-for="day in daysOfWeek" :key="day">{{ day }}</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="rowIndex in maxRows" :key="rowIndex">
            <td v-for="day in daysOfWeek" :key="day">
              <div
                v-if="groupedCurrentWeek[day][rowIndex - 1]"
                class="slot-cell available"
                :class="{
                  active:
                    activeSlot?.availability_id ===
                    groupedCurrentWeek[day][rowIndex - 1].availability_id
                }"
                @click="selectSlot(groupedCurrentWeek[day][rowIndex - 1])"
              >
                <div class="slot-time">
                  {{ groupedCurrentWeek[day][rowIndex - 1].start_time }}
                  –
                  {{ groupedCurrentWeek[day][rowIndex - 1].end_time }}
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <h4 class="fw-bold mt-5">Next Week</h4>

    <div class="table-responsive">
      <table class="table table-bordered text-center">
        <thead>
          <tr>
            <th v-for="day in daysOfWeek" :key="day">{{ day }}</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="rowIndex in maxRows" :key="rowIndex">
            <td v-for="day in daysOfWeek" :key="day">
              <div
                v-if="groupedNextWeek[day][rowIndex - 1]"
                class="slot-cell available"
                :class="{
                  active:
                    activeSlot?.availability_id ===
                    groupedNextWeek[day][rowIndex - 1].availability_id
                }"
                @click="selectSlot(groupedNextWeek[day][rowIndex - 1])"
              >
                <div class="slot-time">
                  {{ groupedNextWeek[day][rowIndex - 1].start_time }}
                  –
                  {{ groupedNextWeek[day][rowIndex - 1].end_time }}
                </div>

              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="text-end mt-4 d-flex justify-content-end gap-2">
      <button
        class="btn btn-outline-danger px-4 fw-semibold"
        :disabled="!activeSlot"
        @click="deleteActiveSlot"
      >
        Delete
      </button>

      <button
        class="btn bg-sb-primary text-white px-4 fw-semibold"
        :disabled="!activeSlot"
        @click="openEditFromActive"
      >
        Edit
      </button>
    </div>

    <div v-if="showAddModal" class="modal-overlay">
      <div class="modal-box">
        <h5 class="mb-3">Add Session</h5>

        <div class="mb-2">
          <label class="form-label">Date</label>
          <input type="date" v-model="newSession.date" class="form-control" :min="today" />
        </div>

        <div class="mb-2">
          <label class="form-label">Start Time</label>
          <input type="time" v-model="newSession.start_time" class="form-control" />
        </div>

        <div class="mb-3">
          <label class="form-label">End Time</label>
          <input type="time" v-model="newSession.end_time" class="form-control" />
        </div>

        <div class="d-flex justify-content-end gap-2">
          <button class="btn btn-secondary" @click="showAddModal = false">
            Cancel
          </button>

          <button class="btn btn-success" @click="saveSession">
            Save
          </button>
        </div>
      </div>
    </div>
    <div v-if="showEditModal" class="modal-overlay">
      <div class="modal-box">
        <h5 class="mb-3">Edit Session</h5>

        <div class="mb-2">
          <label class="form-label">Date</label>
          <input type="date" v-model="editSession.date" class="form-control" />
        </div>

        <div class="mb-2">
          <label class="form-label">Start Time</label>
          <input type="time" v-model="editSession.start_time" class="form-control" />
        </div>

        <div class="mb-3">
          <label class="form-label">End Time</label>
          <input type="time" v-model="editSession.end_time" class="form-control" />
        </div>

        <div class="d-flex justify-content-end">
          <div class="d-flex gap-2">
            <button class="btn btn-secondary" @click="showEditModal = false">
              Cancel
            </button>
            <button class="btn btn-success" @click="updateSession">
              Save
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useTutorSchedStore } from '@/stores/tutorSched'

const tutorSchedStore = useTutorSchedStore()

const showEditModal = ref(false)

const showAddModal = ref(false)

const today = new Date().toISOString().split('T')[0]

const groupedCurrentWeek = computed(() =>
  groupByDay(currentWeekSchedule.value)
)

const groupedNextWeek = computed(() =>
  groupByDay(nextWeekSchedule.value)
)

const activeSlot = ref(null)

const daysOfWeek = [
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday'
]

const maxRows = computed(() => {
  const currentLengths = Object.values(groupedCurrentWeek.value).map(d => d.length)
  const nextLengths = Object.values(groupedNextWeek.value).map(d => d.length)

  return Math.max(...currentLengths, ...nextLengths, 0)
})

const newSession = ref({
  date: '',
  start_time: '',
  end_time: '',
  is_booked: false,
  is_active: true
})

const getWeekRange = (weekOffset = 0) => {
  const today = new Date()

  const monday = new Date(today)
  const dayOfWeek = monday.getDay()

  const diff = (dayOfWeek === 0 ? -6 : 1) - dayOfWeek
  monday.setDate(monday.getDate() + diff)

  monday.setDate(monday.getDate() + (weekOffset * 7))
  monday.setHours(0, 0, 0, 0)

  const weekStart = new Date(monday)

  const weekEnd = new Date(monday)
  weekEnd.setDate(weekStart.getDate() + 6)
  weekEnd.setHours(23, 59, 59, 999)

  return { weekStart, weekEnd }
}

const currentWeekSchedule = computed(() => {
  const { weekStart, weekEnd } = getWeekRange(0)

  return tutorSchedStore.availabilities.filter(slot => {
    const [y, m, d] = slot.date.split('-')
    const slotDate = new Date(y, m - 1, d)

    return slotDate >= weekStart && slotDate <= weekEnd
  })
})

const nextWeekSchedule = computed(() => {
  const { weekStart, weekEnd } = getWeekRange(1)

  return tutorSchedStore.availabilities.filter(slot => {
    const [y, m, d] = slot.date.split('-')
    const slotDate = new Date(y, m - 1, d)

    return slotDate >= weekStart && slotDate <= weekEnd
  })
})

const groupByDay = (schedule) => {
  const result = {}

  daysOfWeek.forEach(day => {
    result[day] = []
  })

  schedule.forEach(slot => {
    if (result[slot.day_of_week]) {
      result[slot.day_of_week].push(slot)
    }
  })

  return result
}

const editSession = ref({
  availability_id: null,
  date: '',
  start_time: '',
  end_time: '',
  is_active: true
})

const selectSlot = (slot) => {
  activeSlot.value =
    activeSlot.value?.availability_id === slot.availability_id
      ? null
      : slot
}

const openEditFromActive = () => {
  if (!activeSlot.value) return
  editSession.value = { ...activeSlot.value }
  showEditModal.value = true
}

const updateSession = async () => {
  if (
    !editSession.value.date ||
    !editSession.value.start_time ||
    !editSession.value.end_time
  ) {
    alert('Please complete all fields.')
    return
  }

  try {
    await tutorSchedStore.updateSlot({
      ...editSession.value
    })

    // Refresh the availability list so table updates
    await tutorSchedStore.fetchAvailability()

    // Close the modal and reset active selection
    showEditModal.value = false
    activeSlot.value = null

  } catch (error) {
    console.error('Failed to update session:', error)
  }
}

const deleteActiveSlot = async () => {
  if (!activeSlot.value) return

  if (!confirm('Delete this session?')) return

  await tutorSchedStore.deleteSlot(activeSlot.value.availability_id)
  await tutorSchedStore.fetchAvailability()

  activeSlot.value = null
}

const saveSession = async () => {
  if (
    !newSession.value.date ||
    !newSession.value.start_time ||
    !newSession.value.end_time
  ) {
    alert('Please complete all fields.')
    return
  }

  try {
    await tutorSchedStore.addSlot({
      ...newSession.value
    })

    await tutorSchedStore.fetchAvailability()

    newSession.value = {
      date: '',
      start_time: '',
      end_time: '',
      is_booked: false,
      is_active: true
    }

    showAddModal.value = false

  } catch (error) {
    console.error('Failed to add session:', error)
  }
}


onMounted(async () => {
  await tutorSchedStore.fetchAvailability()
  console.log(tutorSchedStore.availabilities)
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.modal-box {
  background: white;
  padding: 20px;
  border-radius: 10px;
  width: 400px;
}

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

.slot-cell:hover {
  outline: 2px solid #00895a;
  font-weight: 600;
}

.slot-cell.active {
  outline: 2px solid #00895a;
  background-color: #dff3ec;
  font-weight: 600;
}
</style>