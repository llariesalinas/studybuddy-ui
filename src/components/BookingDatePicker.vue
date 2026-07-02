<template>
  <div class="date-picker-wrap">
    <button
      type="button"
      class="btn w-100 text-start border-sb shadow-none date-trigger sb-btn"
      :class="{ 'date-trigger-active': isOpen }"
      @click="openModal"
    >
      <span>{{ selectedDateLabel }}</span>
      <i class="bi bi-calendar3"></i>
    </button>

    <Teleport to="body">
      <div v-if="isOpen" class="date-modal-backdrop" @click.self="closeModal">
        <section
          class="date-modal"
          role="dialog"
          aria-modal="true"
          aria-labelledby="booking-date-picker-title"
        >
          <header class="date-modal-header">
            <div>
              <p class="date-modal-kicker mb-1">Select Date</p>
              <h2 id="booking-date-picker-title" class="date-modal-title mb-0">
                {{ calendar.monthLabel }}
              </h2>
            </div>

            <div class="date-modal-actions">
              <button
                type="button"
                class="date-icon-btn sb-btn"
                :disabled="!canGoPrevious"
                aria-label="Previous month"
                @click="changeMonth(-1)"
              >
                <i class="bi bi-chevron-left"></i>
              </button>
              <button
                type="button"
                class="date-icon-btn sb-btn"
                aria-label="Next month"
                @click="changeMonth(1)"
              >
                <i class="bi bi-chevron-right"></i>
              </button>
              <button
                type="button"
                class="date-icon-btn sb-btn"
                aria-label="Close date picker"
                @click="closeModal"
              >
                <i class="bi bi-x-lg"></i>
              </button>
            </div>
          </header>

          <div class="date-weekdays" aria-hidden="true">
            <span v-for="weekday in weekdays" :key="weekday">{{ weekday }}</span>
          </div>

          <div class="date-month-grid">
            <button
              v-for="day in calendar.days"
              :key="day.dateKey"
              type="button"
              class="date-cell sb-btn"
              :class="{
                'date-cell-outside': !day.inMonth,
                'date-cell-past': day.isPast,
                'date-cell-today': day.isToday,
                'date-cell-selected': day.isSelected,
              }"
              :disabled="day.isPast || !day.inMonth"
              @click="selectDate(day)"
            >
              <span>{{ day.dayNumber }}</span>
            </button>
          </div>

          <footer class="date-modal-footer">
            <button type="button" class="date-today-btn sb-btn" @click="selectToday">Today</button>
          </footer>
        </section>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: null,
  },
  placeholder: {
    type: String,
    default: 'Select date',
  },
})

const emit = defineEmits(['update:modelValue'])

const weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const isOpen = ref(false)
const monthOffset = ref(0)

const padNumber = (value) => String(value).padStart(2, '0')

const getDateKey = (date) => {
  return `${date.getFullYear()}-${padNumber(date.getMonth() + 1)}-${padNumber(date.getDate())}`
}

const parseDateKey = (dateKey) => {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(String(dateKey || ''))) {
    return null
  }

  const [year, month, day] = dateKey.split('-').map(Number)
  return new Date(year, month - 1, day)
}

const addDays = (date, days) => {
  const next = new Date(date)
  next.setDate(next.getDate() + days)
  return next
}

const getMondayIndex = (date) => {
  return (date.getDay() + 6) % 7
}

const todayKey = computed(() => getDateKey(new Date()))

const selectedDateLabel = computed(() => {
  const selectedDate = parseDateKey(props.modelValue)

  if (!selectedDate) {
    return props.placeholder
  }

  return selectedDate.toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  })
})

const canGoPrevious = computed(() => monthOffset.value > 0)

const calendar = computed(() => {
  const today = new Date()
  const totalMonths = today.getFullYear() * 12 + today.getMonth() + monthOffset.value
  const targetYear = Math.floor(totalMonths / 12)
  const targetMonth = totalMonths % 12
  const monthStart = new Date(targetYear, targetMonth, 1)
  const monthEnd = new Date(targetYear, targetMonth + 1, 0)
  const calendarStart = addDays(monthStart, -getMondayIndex(monthStart))
  const calendarEnd = addDays(monthEnd, 6 - getMondayIndex(monthEnd))
  const days = []

  let currentDate = calendarStart

  while (currentDate <= calendarEnd) {
    const dateKey = getDateKey(currentDate)

    days.push({
      dateKey,
      dayNumber: currentDate.getDate(),
      inMonth: currentDate >= monthStart && currentDate <= monthEnd,
      isPast: dateKey < todayKey.value,
      isToday: dateKey === todayKey.value,
      isSelected: dateKey === props.modelValue,
    })

    currentDate = addDays(currentDate, 1)
  }

  return {
    monthLabel: monthStart.toLocaleDateString('en-US', {
      month: 'long',
      year: 'numeric',
    }),
    days,
  }
})

const getMonthOffsetFromToday = (date) => {
  const today = new Date()
  return date.getFullYear() * 12 + date.getMonth() - (today.getFullYear() * 12 + today.getMonth())
}

const openModal = () => {
  const selectedDate = parseDateKey(props.modelValue)

  if (selectedDate && getDateKey(selectedDate) >= todayKey.value) {
    monthOffset.value = Math.max(0, getMonthOffsetFromToday(selectedDate))
  } else {
    monthOffset.value = 0
  }

  isOpen.value = true
}

const closeModal = () => {
  isOpen.value = false
}

const changeMonth = (direction) => {
  const nextOffset = monthOffset.value + direction

  if (nextOffset < 0) {
    return
  }

  monthOffset.value = nextOffset
}

const selectDate = (day) => {
  if (day.isPast || !day.inMonth) {
    return
  }

  emit('update:modelValue', day.dateKey)
  closeModal()
}

const selectToday = () => {
  monthOffset.value = 0
  emit('update:modelValue', todayKey.value)
  closeModal()
}
</script>

<style scoped>
.date-picker-wrap {
  min-width: 0;
}

.date-trigger {
  min-height: 42px;
  background: #ffffff;
  color: var(--sb-text-dark);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  border-radius: 0.375rem;
}

.date-trigger i {
  color: var(--sb-text-muted);
  flex-shrink: 0;
}

.date-trigger-active {
  border-color: var(--sb-primary);
  box-shadow: 0 0 0 0.15rem rgba(0, 137, 90, 0.12);
}

.date-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1060;
  display: grid;
  place-items: center;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.44);
}

.date-modal {
  width: min(420px, 100%);
  max-height: calc(100vh - 2rem);
  overflow-y: auto;
  border-radius: 18px;
  background: #ffffff;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.22);
  padding: 1.25rem;
}

.date-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.date-modal-kicker {
  color: var(--sb-text-muted-green);
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.date-modal-title {
  color: var(--sb-text-main);
  font-size: 1.15rem;
  font-weight: 800;
}

.date-modal-actions {
  display: flex;
  gap: 0.35rem;
}

.date-icon-btn {
  width: 36px;
  height: 36px;
  border: 0;
  border-radius: 10px;
  background: var(--sb-primary-light);
  color: var(--sb-primary-dark);
  display: inline-grid;
  place-items: center;
}

.date-icon-btn:hover:not(:disabled) {
  background: var(--sb-primary-lighter);
}

.date-icon-btn:disabled {
  background: var(--sb-bg);
  color: var(--sb-text-subtle);
  cursor: not-allowed;
}

.date-weekdays,
.date-month-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 0.35rem;
}

.date-weekdays {
  margin-bottom: 0.45rem;
  color: var(--sb-text-muted);
  font-size: 0.72rem;
  font-weight: 800;
  text-align: center;
}

.date-cell {
  aspect-ratio: 1;
  border: 1px solid var(--sb-border-light);
  border-radius: 12px;
  background: #ffffff;
  color: var(--sb-text-main);
  font-weight: 700;
  display: grid;
  place-items: center;
  transition: none;
}

.date-cell:hover:not(:disabled) {
  border-color: rgba(0, 137, 90, 0.36);
  background: var(--sb-primary-light);
  color: var(--sb-primary-dark);
}

.date-cell-outside {
  opacity: 0.38;
}

.date-cell-past,
.date-cell:disabled {
  color: var(--sb-text-subtle);
  background: var(--sb-bg);
  cursor: not-allowed;
}

.date-cell-today {
  border-color: rgba(0, 137, 90, 0.45);
  box-shadow: inset 0 0 0 1px rgba(0, 137, 90, 0.2);
}

.date-cell-selected {
  color: #ffffff;
  background: var(--sb-primary);
  border-color: var(--sb-primary);
  box-shadow: 0 8px 18px rgba(0, 137, 90, 0.18);
}

.date-modal-footer {
  display: flex;
  justify-content: flex-end;
  padding-top: 1rem;
}

.date-today-btn {
  border: 1px solid var(--sb-border-light);
  border-radius: 10px;
  background: #ffffff;
  color: var(--sb-primary-dark);
  padding: 0.45rem 0.8rem;
  font-weight: 700;
}

@media (max-width: 480px) {
  .date-modal {
    padding: 1rem;
  }

  .date-modal-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .date-modal-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
