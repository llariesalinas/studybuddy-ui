<template>
  <div class="availability-content">

    <!-- HEADER -->
    <div class="d-flex justify-content-between align-items-start mb-4">
      <div>
        <h2 class="fw-bold text-dark mb-1">My Weekly Availability</h2>
        <p class="text-muted mb-0">
          Set recurring weekly time slots.
        </p>
      </div>

      <button
        class="btn btn-success align-self-center"
        @click="showAddModal = true"
      >
        + Add Slot
      </button>
    </div>

    <!-- WEEKLY TEMPLATE TABLE -->
    <div class="table-responsive">
      <table class="table table-bordered text-center">
        <thead>
          <tr>
            <th
              v-for="day in daysOfWeek"
              :key="day.code"
            >
              {{ day.label }}
            </th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="rowIndex in maxRows" :key="rowIndex">
            <td
              v-for="day in daysOfWeek"
              :key="day.code"
            >
              <div
                v-if="groupedSlots[day.code][rowIndex - 1]"
                class="slot-cell available"
                :class="{
                  active:
                    activeSlot?.availability_id ===
                    groupedSlots[day.code][rowIndex - 1].availability_id
                }"
                @click="selectSlot(groupedSlots[day.code][rowIndex - 1])"
              >
                {{
                  groupedSlots[day.code][rowIndex - 1].time_slot
                }} –
                {{
                  addOneHour(groupedSlots[day.code][rowIndex - 1].time_slot)
                }}
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- DELETE BUTTON -->
    <div class="text-end mt-4">
      <button
        class="btn btn-outline-danger"
        :disabled="!activeSlot"
        @click="deleteActiveSlot"
      >
        Delete Selected Slot
      </button>
    </div>

    <!-- ADD SLOT MODAL -->
    <div v-if="showAddModal" class="modal-overlay">
      <div class="modal-box">
        <h5 class="mb-3">Add Weekly Slot</h5>

        <!-- Day -->
        <div class="mb-3">
          <label>Day</label>
          <select v-model="newSlot.day" class="form-control">
            <option disabled value="">Select day</option>
            <option
              v-for="day in daysOfWeek"
              :key="day.code"
              :value="day.code"
            >
              {{ day.label }}
            </option>
          </select>
        </div>

        <!-- Start Time -->
        <div class="mb-3">
          <label>Start Time</label>
          <input
            type="time"
            v-model="newSlot.start_time"
            class="form-control"
          />
        </div>

        <!-- End Time -->
        <div class="mb-3">
          <label>End Time</label>
          <input
            type="time"
            v-model="newSlot.end_time"
            class="form-control"
          />
        </div>

        <div class="d-flex justify-content-end gap-2">
          <button
            class="btn btn-secondary"
            @click="showAddModal = false"
          >
            Cancel
          </button>

          <button
            class="btn btn-success"
            @click="saveSlot"
          >
            Save
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTutorSchedStore } from '@/stores/tutorSched'

const tutorSchedStore = useTutorSchedStore()

// ===============================
// UI STATE
// ===============================
const showAddModal = ref(false)
const activeSlot = ref(null)

// ===============================
// WEEK DAY DEFINITIONS
// Must match Django DAY_CHOICES
// ===============================
const daysOfWeek = [
  { code: 'Mon', label: 'Monday' },
  { code: 'Tue', label: 'Tuesday' },
  { code: 'Wed', label: 'Wednesday' },
  { code: 'Thu', label: 'Thursday' },
  { code: 'Fri', label: 'Friday' },
  { code: 'Sat', label: 'Saturday' },
  { code: 'Sun', label: 'Sunday' }
]

// ===============================
// GROUP TEMPLATE SLOTS BY DAY
// ===============================
const groupedSlots = computed(() => {
  const result = {}

  // initialize empty arrays
  daysOfWeek.forEach(day => {
    result[day.code] = []
  })

  // group slots by day
  tutorSchedStore.availabilities.forEach(slot => {
    if (result[slot.day]) {
      result[slot.day].push(slot)
    }
  })

  // optional: sort times
  Object.keys(result).forEach(day => {
    result[day].sort((a, b) =>
      a.time_slot.localeCompare(b.time_slot)
    )
  })

  return result
})

// ===============================
// TABLE ROW COUNT
// ===============================
const maxRows = computed(() => {
  return Math.max(
    ...Object.values(groupedSlots.value).map(d => d.length),
    0
  )
})

// ===============================
// NEW SLOT MODEL
// ===============================
const newSlot = ref({
  day: '',
  start_time: '',
  end_time: ''
})

// ===============================
// SELECT SLOT
// ===============================
const selectSlot = (slot) => {
  activeSlot.value =
    activeSlot.value?.availability_id === slot.availability_id
      ? null
      : slot
}

// ===============================
// DELETE SLOT
// ===============================
const deleteActiveSlot = async () => {
  if (!activeSlot.value) return

  console.log("Deleting slot:", activeSlot.value)

  if (!confirm('Delete this slot?')) return

  await tutorSchedStore.deleteSlot(activeSlot.value.availability_id)
  await tutorSchedStore.fetchAvailability()

  activeSlot.value = null
}

// ===============================
// SAVE NEW SLOT
// ===============================
const saveSlot = async () => {
  if (!newSlot.value.day || !newSlot.value.start_time || !newSlot.value.end_time) {
    alert('Please complete all fields.')
    return
  }

  const start = new Date(`1970-01-01T${newSlot.value.start_time}`)
  const end = new Date(`1970-01-01T${newSlot.value.end_time}`)

  if (end <= start) {
    alert('End time must be after start time.')
    return
  }

  if (start.getMinutes() !== 0 || end.getMinutes() !== 0) {
    alert('Please use full-hour times (e.g., 07:00, 10:00).')
    return
  }

  try {
    let current = new Date(start)
    let createdCount = 0

    while (current < end) {
      const hourString = current.toTimeString().slice(0, 5)

      // 🔍 Check if slot already exists in store
      const alreadyExists = tutorSchedStore.availabilities.some(
        slot =>
          slot.day === newSlot.value.day &&
          slot.time_slot === hourString
      )

      if (!alreadyExists) {
        await tutorSchedStore.addSlot({
          day: newSlot.value.day,
          time_slot: hourString
        })
        createdCount++
      }

      current.setHours(current.getHours() + 1)
    }

    if (createdCount === 0) {
      alert('All selected time slots already exist.')
    }

    await tutorSchedStore.fetchAvailability()

    newSlot.value = {
      day: '',
      start_time: '',
      end_time: ''
    }

    showAddModal.value = false

  } catch (error) {
    console.error('Failed to add slots:', error)
    alert('Something went wrong.')
  }
}

// ===============================
// LOAD DATA ON MOUNT
// ===============================
onMounted(async () => {
  await tutorSchedStore.fetchAvailability()
  console.log(tutorSchedStore.availabilities)
})

const addOneHour = (timeString) => {
  const date = new Date(`1970-01-01T${timeString}`)
  date.setHours(date.getHours() + 1)
  return date.toTimeString().slice(0, 5)
}
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