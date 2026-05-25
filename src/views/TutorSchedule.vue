<template>
  <div class="availability-content">
    <section class="schedule-card shadow-sm">
      <div class="schedule-header">
        <div>
          <h2 class="schedule-title">Weekly Availability</h2>
        </div>
      </div>

      <div v-if="currentWeek" class="week-shell">
        <div class="week-toolbar">
          <div class="week-nav">
            <button
              type="button"
              class="week-nav-btn sb-btn"
              :disabled="weekIndex <= 0"
              @click="navigateWeek(-1)"
            >
              <i class="bi bi-chevron-left"></i>
            </button>
            <button
              type="button"
              class="week-nav-btn sb-btn"
              :disabled="weekIndex >= monthWeeks.length - 1"
              @click="navigateWeek(1)"
            >
              <i class="bi bi-chevron-right"></i>
            </button>
          </div>

          <div class="week-toolbar-copy">
            <p class="month-label mb-1">{{ currentMonthLabel }}</p>
            <p class="week-range mb-0">{{ currentWeekLabel }}</p>
          </div>
        </div>

        <div class="week-columns-shell">
          <div class="week-columns">
            <article
              v-for="day in currentWeek.days"
              :key="day.date"
              class="day-column"
            >
              <div class="day-heading">
                <div class="day-name">{{ day.shortLabel }}</div>
                <div class="day-date">{{ formatDayDate(day.date) }}</div>
                <div class="slot-count-row">
                  <span v-if="groupedSlots[day.code].length" class="slot-count-badge">
                    {{ groupedSlots[day.code].length }}
                  </span>
                </div>
                <button
                  type="button"
                  class="btn day-block-date-btn sb-btn"
                  :class="{ active: isFullDayBlocked(day.date) }"
                  @click="toggleFullDayOverride(day.date)"
                >
                  {{ isFullDayBlocked(day.date) ? 'Unblock Date' : 'Block Date' }}
                </button>
                <button
                  type="button"
                  class="btn day-add-slot-btn sb-btn"
                  @click="openAddModal(day.code)"
                >
                  + Add Slot
                </button>
              </div>

              <div
                class="day-availability-bar"
                :class="{
                  'day-availability-bar-available': groupedSlots[day.code].length,
                  'day-availability-bar-blocked': isFullDayBlocked(day.date)
                }"
              ></div>

              <div class="day-slots">
                <div v-if="isFullDayBlocked(day.date)" class="full-day-banner">
                  This date is blocked.
                </div>

                <button
                  v-for="slot in groupedSlots[day.code]"
                  :key="slot.availability_id"
                  type="button"
                  class="slot-pill sb-btn"
                  :class="{
                    selected: isSlotSelected(slot.availability_id),
                    blocked: isSlotBlocked(day.date, slot.availability_id)
                  }"
                  @click="toggleSlotSelection(slot.availability_id)"
                >
                  <span class="slot-pill-text">{{ slot.time_slot }} - {{ addThirtyMinutes(slot.time_slot) }}</span>
                  <span v-if="isSlotBlocked(day.date, slot.availability_id)" class="slot-pill-status">
                    Blocked
                  </span>
                  <span v-else-if="isSlotSelected(slot.availability_id)" class="slot-pill-check">
                    <i class="bi bi-check-lg"></i>
                  </span>
                </button>

                <div v-if="!groupedSlots[day.code].length" class="empty-day-zone">
                  <span>{{ isFullDayBlocked(day.date) ? 'Date blocked' : 'No slots yet' }}</span>
                </div>
              </div>

              <div
                v-if="groupedSlots[day.code].length"
                class="day-actions"
              >
                <button
                  v-if="selectedUnblockedCount(day) && !isFullDayBlocked(day.date)"
                  type="button"
                  class="selected-day-btn sb-btn"
                  @click="blockSelectedSlots(day)"
                >
                  Block Selected For {{ formatDayDate(day.date) }} ({{ selectedUnblockedCount(day) }})
                </button>
                <button
                  v-if="selectedBlockedCount(day)"
                  type="button"
                  class="selected-day-btn unblock-day-btn sb-btn"
                  @click="unblockSelectedSlots(day)"
                >
                  Unblock Selected ({{ selectedBlockedCount(day) }})
                </button>
                <button
                  v-if="selectedCountForDay(day.code)"
                  type="button"
                  class="selected-day-btn sb-btn"
                  @click="removeSelectedSlots(day.code)"
                >
                  Remove Selected ({{ selectedCountForDay(day.code) }})
                </button>
              </div>
            </article>
          </div>
        </div>
      </div>
    </section>

    <div v-if="showAddModal" class="modal-overlay" @click.self="closeAddModal">
      <div class="modal-box">
        <div class="time-picker-header">
          <div>
            <h5 class="mb-1">Add Weekly Slot</h5>
            <p class="time-picker-subtitle mb-0">Pick when the session begins and ends.</p>
          </div>
          <button
            type="button"
            class="time-picker-close sb-btn"
            @click="closeAddModal"
          >
            Close
          </button>
        </div>

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

        <div class="time-picker-block">
          <button
            v-if="newSlot.start_time && expandedPicker !== 'start'"
            type="button"
            class="selected-time-card sb-btn"
            @click="expandedPicker = 'start'"
          >
            <span class="selected-time-label">Start Time</span>
            <span class="selected-time-value">{{ formatDisplayTime(newSlot.start_time) }}</span>
          </button>

          <template v-else>
            <div class="time-picker-label-group">
              <h6 class="time-picker-label mb-1">Choose Start Time</h6>
              <p class="time-picker-help mb-0">Pick when the session begins.</p>
            </div>

            <div class="time-period-toggle">
              <button
                type="button"
                class="time-period-btn sb-btn"
                :class="{ active: startPeriod === 'AM' }"
                @click="startPeriod = 'AM'"
              >
                AM
              </button>
              <button
                type="button"
                class="time-period-btn sb-btn"
                :class="{ active: startPeriod === 'PM' }"
                @click="startPeriod = 'PM'"
              >
                PM
              </button>
            </div>

            <div class="time-grid">
              <button
                v-for="time in visibleStartTimes"
                :key="`start-${time}`"
                type="button"
                class="time-grid-btn sb-btn"
                :class="{ active: newSlot.start_time === time }"
                @click="selectStartTime(time)"
              >
                {{ formatDisplayTime(time) }}
              </button>
            </div>
          </template>
        </div>

        <div class="time-picker-block">
          <button
            v-if="newSlot.end_time && expandedPicker !== 'end'"
            type="button"
            class="selected-time-card sb-btn"
            @click="expandedPicker = 'end'"
          >
            <span class="selected-time-label">End Time</span>
            <span class="selected-time-value">{{ formatDisplayTime(newSlot.end_time) }}</span>
          </button>

          <template v-else>
            <div class="time-picker-label-group">
              <h6 class="time-picker-label mb-1">Choose End Time</h6>
              <p class="time-picker-help mb-0">Pick when the session ends.</p>
            </div>

            <div class="time-period-toggle">
              <button
                type="button"
                class="time-period-btn sb-btn"
                :class="{ active: endPeriod === 'AM' }"
                @click="endPeriod = 'AM'"
              >
                AM
              </button>
              <button
                type="button"
                class="time-period-btn sb-btn"
                :class="{ active: endPeriod === 'PM' }"
                @click="endPeriod = 'PM'"
              >
                PM
              </button>
            </div>

            <div class="time-grid">
              <button
                v-for="time in visibleEndTimes"
                :key="`end-${time}`"
                type="button"
                class="time-grid-btn sb-btn"
                :class="{ active: newSlot.end_time === time }"
                @click="selectEndTime(time)"
              >
                {{ formatDisplayTime(time) }}
              </button>
            </div>
          </template>
        </div>

        <div class="d-flex justify-content-end gap-2 mt-3">
          <button
            class="btn btn-secondary sb-btn"
            @click="closeAddModal"
          >
            Cancel
          </button>

          <button
            class="btn btn-success sb-btn"
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
import { computed, onMounted, ref } from 'vue'
import { useTutorSchedStore } from '@/stores/tutorSched'
import { useToastStore } from '@/stores/toast'

const tutorSchedStore = useTutorSchedStore()
const toastStore = useToastStore()

const showAddModal = ref(false)
const monthOffset = ref(0)
const weekIndex = ref(0)
const startPeriod = ref('AM')
const endPeriod = ref('AM')
const expandedPicker = ref('start')
const selectedSlotIds = ref([])

const daysOfWeek = [
  { code: 'Mon', label: 'Monday', shortLabel: 'Mon' },
  { code: 'Tue', label: 'Tuesday', shortLabel: 'Tue' },
  { code: 'Wed', label: 'Wednesday', shortLabel: 'Wed' },
  { code: 'Thu', label: 'Thursday', shortLabel: 'Thu' },
  { code: 'Fri', label: 'Friday', shortLabel: 'Fri' },
  { code: 'Sat', label: 'Saturday', shortLabel: 'Sat' },
  { code: 'Sun', label: 'Sunday', shortLabel: 'Sun' }
]

const groupedSlots = computed(() => {
  const result = {}

  daysOfWeek.forEach(day => {
    result[day.code] = []
  })

  tutorSchedStore.availabilities.forEach(slot => {
    if (result[slot.day]) {
      result[slot.day].push(slot)
    }
  })

  Object.keys(result).forEach(day => {
    result[day].sort((a, b) => a.time_slot.localeCompare(b.time_slot))
  })

  return result
})

const allTimeOptions = computed(() => {
  const options = []

  for (let hour = 0; hour < 24; hour += 1) {
    for (let minute = 0; minute < 60; minute += 30) {
      options.push(`${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`)
    }
  }

  return options
})

const visibleStartTimes = computed(() => filterTimesByPeriod(startPeriod.value))
const visibleEndTimes = computed(() => filterTimesByPeriod(endPeriod.value))

const viewedMonthDate = computed(() => {
  const base = new Date()
  return new Date(base.getFullYear(), base.getMonth() + monthOffset.value, 1)
})

const monthWeeks = computed(() => {
  const monthStart = viewedMonthDate.value
  const monthEnd = new Date(monthStart.getFullYear(), monthStart.getMonth() + 1, 0)
  const start = new Date(monthStart)
  const end = new Date(monthEnd)

  const mondayOffset = (start.getDay() + 6) % 7
  start.setDate(start.getDate() - mondayOffset)

  const sundayOffset = (7 - end.getDay()) % 7
  end.setDate(end.getDate() + sundayOffset)

  const weeks = []
  let cursor = new Date(start)
  while (cursor <= end) {
    const days = []

    for (let index = 0; index < 7; index += 1) {
      const current = new Date(cursor)
      const dayMeta = daysOfWeek[index]
      const dateKey = getDateKey(current)

      days.push({
        code: dayMeta.code,
        label: dayMeta.label,
        shortLabel: dayMeta.shortLabel,
        date: dateKey
      })

      cursor.setDate(cursor.getDate() + 1)
    }

    weeks.push({
      weekStart: days[0].date,
      weekEnd: days[6].date,
      days
    })
  }

  return weeks
})

const firstAvailableWeekIndex = computed(() => {
  const todayKey = getDateKey(new Date())
  const matchingWeekIndex = monthWeeks.value.findIndex(
    week => todayKey >= week.weekStart && todayKey <= week.weekEnd
  )

  return matchingWeekIndex >= 0 ? matchingWeekIndex : 0
})

const currentWeek = computed(() => monthWeeks.value[weekIndex.value] || null)
const visibleOverrideRange = computed(() => {
  if (!monthWeeks.value.length) {
    return null
  }

  return {
    start: monthWeeks.value[0].weekStart,
    end: monthWeeks.value[monthWeeks.value.length - 1].weekEnd,
  }
})

const currentMonthLabel = computed(() => {
  return viewedMonthDate.value.toLocaleDateString([], {
    month: 'long',
    year: 'numeric'
  })
})

const currentWeekLabel = computed(() => {
  if (!currentWeek.value) {
    return ''
  }

  const start = new Date(currentWeek.value.weekStart)
  const end = new Date(currentWeek.value.weekEnd)
  const startMonth = start.toLocaleDateString([], { month: 'short' })
  const endMonth = end.toLocaleDateString([], { month: 'short' })
  const year = end.getFullYear()

  if (startMonth === endMonth) {
    return `${startMonth} ${start.getDate()}-${end.getDate()}, ${year}`
  }

  return `${startMonth} ${start.getDate()}-${endMonth} ${end.getDate()}, ${year}`
})

const newSlot = ref({
  day: '',
  start_time: '',
  end_time: ''
})

function getDateKey(date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function setInitialWeekIndex() {
  weekIndex.value = firstAvailableWeekIndex.value
}

function filterTimesByPeriod(period) {
  return allTimeOptions.value.filter(time => {
    const hour = Number(time.split(':')[0])
    return period === 'AM' ? hour < 12 : hour >= 12
  })
}

function formatDisplayTime(timeString) {
  const [hours, minutes] = timeString.split(':').map(Number)
  const suffix = hours >= 12 ? 'PM' : 'AM'
  const hour12 = hours % 12 || 12
  return `${hour12}:${String(minutes).padStart(2, '0')} ${suffix}`
}

function formatDayDate(dateString) {
  return new Date(dateString).toLocaleDateString([], {
    month: 'short',
    day: 'numeric'
  })
}

function getOverridesForDate(dateString) {
  return tutorSchedStore.overrides.filter(override => override.override_date === dateString)
}

function getFullDayOverride(dateString) {
  return getOverridesForDate(dateString).find(override => override.is_full_day) || null
}

function isFullDayBlocked(dateString) {
  return Boolean(getFullDayOverride(dateString))
}

function getSlotOverride(dateString, availabilityId) {
  return tutorSchedStore.overrides.find(
    override =>
      override.override_date === dateString
      && !override.is_full_day
      && override.availability_id === availabilityId
  ) || null
}

function isSlotBlocked(dateString, availabilityId) {
  return isFullDayBlocked(dateString) || Boolean(getSlotOverride(dateString, availabilityId))
}

function isSlotSelected(slotId) {
  return selectedSlotIds.value.includes(slotId)
}

function toggleSlotSelection(slotId) {
  if (isSlotSelected(slotId)) {
    selectedSlotIds.value = selectedSlotIds.value.filter(id => id !== slotId)
    return
  }

  selectedSlotIds.value = [...selectedSlotIds.value, slotId]
}

function selectedCountForDay(dayCode) {
  const daySlotIds = groupedSlots.value[dayCode].map(slot => slot.availability_id)
  return selectedSlotIds.value.filter(id => daySlotIds.includes(id)).length
}

function selectedUnblockedCount(day) {
  const daySlotIds = groupedSlots.value[day.code].map(slot => slot.availability_id)
  return selectedSlotIds.value.filter(
    id => daySlotIds.includes(id) && !isSlotBlocked(day.date, id)
  ).length
}

function selectedBlockedCount(day) {
  const daySlotIds = groupedSlots.value[day.code].map(slot => slot.availability_id)
  return selectedSlotIds.value.filter(
    id => daySlotIds.includes(id) && Boolean(getSlotOverride(day.date, id))
  ).length
}

function selectStartTime(time) {
  newSlot.value.start_time = time
  expandedPicker.value = newSlot.value.end_time ? '' : 'end'
}

function selectEndTime(time) {
  newSlot.value.end_time = time
  expandedPicker.value = newSlot.value.start_time ? '' : 'start'
}

function openAddModal(dayCode) {
  newSlot.value = {
    day: dayCode,
    start_time: '',
    end_time: ''
  }

  startPeriod.value = 'AM'
  endPeriod.value = 'AM'
  expandedPicker.value = 'start'
  showAddModal.value = true
}

function closeAddModal() {
  showAddModal.value = false
  expandedPicker.value = 'start'
}

function navigateWeek(direction) {
  if (direction < 0) {
    if (weekIndex.value > 0) {
      weekIndex.value -= 1
    }
    return
  }

  if (weekIndex.value < monthWeeks.value.length - 1) {
    weekIndex.value += 1
  }
}

async function refreshAvailability() {
  await tutorSchedStore.fetchAvailability()
  if (visibleOverrideRange.value) {
    await tutorSchedStore.fetchOverrides(visibleOverrideRange.value)
  }
  const availableIds = new Set(tutorSchedStore.availabilities.map(slot => slot.availability_id))
  selectedSlotIds.value = selectedSlotIds.value.filter(id => availableIds.has(id))
}

async function clearSelection() {
  selectedSlotIds.value = []
}

async function removeSelectedSlots(dayCode) {
  const daySlotIds = groupedSlots.value[dayCode].map(slot => slot.availability_id)
  const selectedForDay = selectedSlotIds.value.filter(id => daySlotIds.includes(id))

  for (const slotId of selectedForDay) {
    await tutorSchedStore.deleteSlot(slotId)
  }

  await refreshAvailability()
}

async function toggleFullDayOverride(dateString) {
  try {
    const existingOverride = getFullDayOverride(dateString)

    if (existingOverride) {
      await tutorSchedStore.deleteOverride(existingOverride.id)
    } else {
      await tutorSchedStore.createFullDayOverride(dateString)
    }

    selectedSlotIds.value = []
    await refreshAvailability()
  } catch (error) {
    console.error('Failed to toggle full-day override:', error)
    toastStore.push(error.response?.data?.error || 'Unable to update the blocked date.', 'error')
  }
}

async function blockSelectedSlots(day) {
  const daySlotIds = groupedSlots.value[day.code].map(slot => slot.availability_id)
  const selectedForDay = selectedSlotIds.value.filter(
    id => daySlotIds.includes(id) && !isSlotBlocked(day.date, id)
  )

  if (!selectedForDay.length) {
    return
  }

  try {
    await tutorSchedStore.createSlotOverrides(day.date, selectedForDay)
    selectedSlotIds.value = selectedSlotIds.value.filter(id => !selectedForDay.includes(id))
    await refreshAvailability()
  } catch (error) {
    console.error('Failed to block selected slots:', error)
    toastStore.push(error.response?.data?.error || 'Unable to block the selected slots.', 'error')
  }
}

async function unblockSelectedSlots(day) {
  const daySlotIds = groupedSlots.value[day.code].map(slot => slot.availability_id)
  const selectedBlockedSlotIds = selectedSlotIds.value.filter(
    id => daySlotIds.includes(id) && Boolean(getSlotOverride(day.date, id))
  )
  const overrideIds = selectedSlotIds.value
    .filter(id => daySlotIds.includes(id))
    .map(id => getSlotOverride(day.date, id)?.id)
    .filter(Boolean)

  if (!overrideIds.length) {
    return
  }

  try {
    for (const overrideId of overrideIds) {
      await tutorSchedStore.deleteOverride(overrideId)
    }

    selectedSlotIds.value = selectedSlotIds.value.filter(
      id => !selectedBlockedSlotIds.includes(id)
    )
    await refreshAvailability()
  } catch (error) {
    console.error('Failed to unblock selected slots:', error)
    toastStore.push(error.response?.data?.error || 'Unable to unblock the selected slots.', 'error')
  }
}

async function saveSlot() {
  if (!newSlot.value.day || !newSlot.value.start_time || !newSlot.value.end_time) {
    toastStore.push('Please complete all fields.', 'warning')
    return
  }

  const start = new Date(`1970-01-01T${newSlot.value.start_time}`)
  const end = new Date(`1970-01-01T${newSlot.value.end_time}`)

  if (end <= start) {
    toastStore.push('End time must be after start time.', 'warning')
    return
  }

  try {
    let current = new Date(start)
    let createdCount = 0

    while (current < end) {
      const hourString = current.toTimeString().slice(0, 5)

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

      current.setMinutes(current.getMinutes() + 30)
    }

    if (createdCount === 0) {
      toastStore.push('All selected time slots already exist.', 'warning')
    }

    await refreshAvailability()

    if (createdCount > 0) {
      toastStore.push(`${createdCount} slot${createdCount > 1 ? 's were' : ' was'} added successfully.`)
    }

    newSlot.value = {
      day: '',
      start_time: '',
      end_time: ''
    }

    startPeriod.value = 'AM'
    endPeriod.value = 'AM'
    expandedPicker.value = 'start'
    showAddModal.value = false
    clearSelection()
  } catch (error) {
    console.error('Failed to add slots:', error)
    toastStore.push('Something went wrong.', 'error')
  }
}

onMounted(async () => {
  await refreshAvailability()
  setInitialWeekIndex()
})

function addThirtyMinutes(timeString) {
  const date = new Date(`1970-01-01T${timeString}`)
  date.setMinutes(date.getMinutes() + 30)
  return date.toTimeString().slice(0, 5)
}
</script>

<style scoped>
.availability-content {
  min-height: 100%;
}

.schedule-card {
  background: #ffffff;
  border-radius: 24px;
  padding: 28px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
  display: grid;
  gap: 24px;
}

.schedule-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.schedule-title {
  margin: 0 0 4px;
  font-size: 1.15rem;
  font-weight: 700;
  color: #163127;
}

.schedule-subtitle {
  margin: 0;
  color: #6d8178;
}

.week-shell {
  display: grid;
  gap: 24px;
}

.week-toolbar {
  display: grid;
  grid-template-columns: auto 1fr;
  align-items: center;
  gap: 16px;
}

.week-nav {
  display: flex;
  gap: 10px;
}

.week-nav-btn {
  width: 42px;
  height: 42px;
  border: 0;
  border-radius: 14px;
  background: #edf6f1;
  color: #0a7a51;
  transition: background-color 150ms ease, transform 150ms ease, box-shadow 150ms ease;
}

.week-nav-btn:hover:not(:disabled) {
  background: #dff1e8;
  transform: translateY(-1px);
  box-shadow: 0 8px 16px rgba(0, 137, 90, 0.12);
}

.week-nav-btn:disabled {
  background: #f3f4f6;
  color: #94a3b8;
  cursor: not-allowed;
}

.week-toolbar-copy {
  display: grid;
  gap: 2px;
}

.month-label {
  color: #6d8178;
  font-size: 0.9rem;
  font-weight: 600;
}

.week-range {
  margin: 0;
  text-align: center;
  font-size: 1.2rem;
  font-weight: 700;
  color: #163127;
}

.week-columns-shell {
  overflow-x: auto;
  padding-bottom: 4px;
}

.week-columns {
  display: grid;
  grid-template-columns: repeat(7, minmax(135px, 1fr));
  gap: 14px;
  min-width: 1030px;
  align-items: start;
}

.day-column {
  min-width: 135px;
  display: grid;
  grid-template-rows: auto auto 1fr auto;
  gap: 8px;
  align-content: start;
}

.day-heading {
  display: grid;
  grid-template-rows: auto auto 22px auto;
  gap: 6px;
  justify-items: center;
  text-align: center;
  padding-bottom: 2px;
  align-content: start;
}

.day-name {
  color: #687684;
  font-size: 0.9rem;
  font-weight: 600;
}

.day-date {
  color: #163127;
  font-size: 0.95rem;
  font-weight: 700;
  line-height: 1.1;
}

.slot-count-row {
  min-height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.slot-count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 3px 8px;
  border-radius: 999px;
  background: #e1f5ee;
  color: #085041;
  font-size: 0.74rem;
  font-weight: 700;
  line-height: 1;
}

.day-add-slot-btn {
  width: 100%;
  min-height: 38px;
  background: #edf6f1;
  color: #0a7a51;
  border: 1px dashed #b8dccc;
  border-radius: 12px;
  padding: 7px 10px;
  font-size: 0.82rem;
  font-weight: 700;
}

.day-block-date-btn {
  width: 100%;
  min-height: 38px;
  background: #fff2f0;
  color: #b42318;
  border: 1px dashed #f3b7b0;
  border-radius: 12px;
  padding: 7px 10px;
  font-size: 0.82rem;
  font-weight: 700;
}

.day-block-date-btn:hover {
  background: #ffe4df;
  color: #9f1f15;
  border-color: #e79d93;
}

.day-block-date-btn.active {
  background: #b42318;
  color: #ffffff;
  border-color: #b42318;
}

.day-add-slot-btn:hover {
  background: #dff1e8;
  color: #0a7a51;
  border-color: #8dcfb2;
}

.day-availability-bar {
  height: 3px;
  border-radius: 999px;
  background: #d7e1dc;
}

.day-availability-bar-available {
  background: #00895a;
}

.day-availability-bar-blocked {
  background: #b42318;
}

.day-slots {
  display: grid;
  gap: 10px;
  align-content: start;
}

.full-day-banner {
  width: 100%;
  padding: 10px 12px;
  border-radius: 14px;
  background: #fff2f0;
  color: #b42318;
  font-size: 0.85rem;
  font-weight: 700;
  text-align: center;
}

.slot-pill {
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  width: 100%;
  min-height: 48px;
  padding: 12px 16px;
  border: 1px solid transparent;
  border-radius: 999px;
  background: #e1f5ee;
  color: #085041;
  font-weight: 700;
  font-size: 1rem;
  text-align: left;
  transition: transform 150ms ease, box-shadow 150ms ease, background-color 150ms ease, border-color 150ms ease;
}

.slot-pill:hover:not(:disabled) {
  background: #d7f0e6;
  border-color: #9fe1cb;
  box-shadow: 0 8px 18px rgba(8, 80, 65, 0.08);
  transform: translateY(-1px);
}

.slot-pill.selected {
  background: #00895a;
  border-color: #00895a;
  color: #ffffff;
  box-shadow: 0 10px 20px rgba(0, 137, 90, 0.18);
}

.slot-pill.blocked {
  background: #fff2f0;
  border-color: #f3b7b0;
  color: #b42318;
  box-shadow: none;
}

.slot-pill.blocked.selected {
  background: #b42318;
  border-color: #b42318;
  color: #ffffff;
  box-shadow: 0 10px 20px rgba(180, 35, 24, 0.18);
}

.slot-pill:disabled {
  cursor: default;
}

.slot-pill-text {
  min-width: 0;
  line-height: 1.25;
}

.slot-pill-check {
  width: 24px;
  height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.18);
  color: #ffffff;
  flex-shrink: 0;
}

.slot-pill-status {
  flex-shrink: 0;
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.empty-day-zone {
  width: 100%;
  min-height: 48px;
  display: grid;
  place-items: center;
  padding: 12px;
  border: 1.5px dashed #9fe1cb;
  border-radius: 8px;
  text-align: center;
  color: #7a8f86;
  font-size: 0.9rem;
}

.day-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.selected-day-btn {
  border: 0;
  background: transparent;
  color: #0a7a51;
  font-size: 0.82rem;
  font-weight: 700;
  padding: 0;
}

.selected-day-btn:hover {
  text-decoration: underline;
}

.unblock-day-btn {
  color: #b42318;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.modal-box {
  background: white;
  padding: 24px;
  border-radius: 18px;
  width: min(720px, 100%);
  max-height: 88vh;
  overflow-y: auto;
}

.time-picker-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  gap: 16px;
  margin-bottom: 18px;
}

.time-picker-subtitle {
  color: #6d8178;
  font-size: 0.92rem;
}

.time-picker-close {
  border: 0;
  background: transparent;
  color: #163127;
  font-size: 0.92rem;
  padding: 0;
  transition: color 150ms ease, transform 150ms ease;
}

.time-picker-close:hover {
  color: #0a7a51;
  transform: translateY(-1px);
}

.time-picker-block {
  display: grid;
  gap: 12px;
  margin-bottom: 18px;
}

.time-picker-label {
  color: #163127;
  font-size: 1rem;
  font-weight: 700;
}

.time-picker-help {
  color: #6d8178;
  font-size: 0.9rem;
}

.time-period-toggle {
  display: inline-grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 4px;
  width: 128px;
  padding: 4px;
  border-radius: 999px;
  background: #edf2ef;
}

.time-period-btn {
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: #315447;
  font-weight: 700;
  padding: 8px 0;
  transition: background-color 150ms ease, color 150ms ease, transform 150ms ease, box-shadow 150ms ease;
}

.time-period-btn:hover:not(.active) {
  background: rgba(255, 255, 255, 0.72);
  color: #0a7a51;
  transform: translateY(-1px);
}

.time-period-btn.active {
  background: #ffffff;
  color: #00895a;
  box-shadow: 0 2px 6px rgba(15, 23, 42, 0.08);
}

.time-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.time-grid-btn {
  border: 1px solid #d4dfdb;
  border-radius: 14px;
  background: #ffffff;
  color: #163127;
  padding: 10px 12px;
  font-weight: 600;
  text-align: center;
  transition: background-color 150ms ease, color 150ms ease, border-color 150ms ease, transform 150ms ease, box-shadow 150ms ease;
}

.time-grid-btn:hover:not(.active) {
  background: #f4fbf8;
  color: #0a7a51;
  border-color: #b7d9cc;
  transform: translateY(-1px);
  box-shadow: 0 8px 16px rgba(8, 80, 65, 0.08);
}

.time-grid-btn.active {
  background: #e1f5ee;
  color: #085041;
  border-color: #9fe1cb;
}

.modal-box :deep(select.form-control) {
  transition: border-color 150ms ease, box-shadow 150ms ease, background-color 150ms ease;
}

.modal-box :deep(select.form-control:hover) {
  border-color: #9fe1cb;
  background-color: #f8fcfa;
  box-shadow: 0 0 0 4px rgba(10, 122, 81, 0.06);
}

.modal-box :deep(.btn-secondary),
.modal-box :deep(.btn-success) {
  transition: transform 150ms ease, box-shadow 150ms ease, filter 150ms ease;
}

.modal-box :deep(.btn-secondary:hover),
.modal-box :deep(.btn-success:hover) {
  transform: translateY(-1px);
  box-shadow: 0 10px 18px rgba(15, 23, 42, 0.12);
  filter: saturate(1.03);
}

.selected-time-card {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 14px 16px;
  border: 1px solid #cfe1da;
  border-radius: 16px;
  background: #e1f5ee;
  color: #085041;
  text-align: left;
  transition: transform 150ms ease, box-shadow 150ms ease, background-color 150ms ease, border-color 150ms ease;
}

.selected-time-card:hover {
  background: #d7f0e6;
  border-color: #9fe1cb;
  box-shadow: 0 10px 20px rgba(8, 80, 65, 0.08);
  transform: translateY(-1px);
}

.selected-time-card:focus-visible {
  outline: 2px solid #0a7a51;
  outline-offset: 2px;
}

.selected-time-label {
  font-size: 0.84rem;
  font-weight: 700;
  opacity: 0.8;
}

.selected-time-value {
  font-size: 0.95rem;
  font-weight: 700;
}

@media (max-width: 991px) {
  .week-toolbar {
    grid-template-columns: 1fr;
    justify-items: start;
  }

  .week-range {
    text-align: left;
  }

  .time-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .week-columns {
    min-width: 0;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .day-column {
    min-width: 0;
  }

  .time-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .selected-time-card {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
