<template>
  <div class="time-picker-wrap" @keydown.esc.stop="closePanel">
    <button
      type="button"
      class="time-trigger sb-btn"
      :class="{ 'time-trigger-active': isOpen }"
      :disabled="disabled"
      :aria-expanded="isOpen"
      aria-haspopup="listbox"
      @click="togglePanel"
    >
      <span class="time-trigger-text" :class="{ 'is-placeholder': !hasRange }">
        {{ triggerLabel }}
      </span>

      <span
        v-if="hasRange && !disabled"
        class="time-trigger-clear"
        role="button"
        tabindex="0"
        aria-label="Clear time range"
        data-testid="time-clear"
        @click.stop="commit(null, null)"
        @keydown.enter.stop.prevent="commit(null, null)"
        @keydown.space.stop.prevent="commit(null, null)"
      >
        <i class="bi bi-x-lg"></i>
      </span>
      <i v-else class="bi bi-chevron-down time-trigger-icon"></i>
    </button>

    <div v-if="isOpen" class="time-dropdown" role="group" :aria-label="title">
      <div class="time-columns">
        <div class="time-column">
          <p class="time-column-label">Start</p>
          <ul class="time-option-list" role="listbox" aria-label="Start time">
            <li v-for="slot in startSlots" :key="slot.value">
              <button
                type="button"
                class="time-option sb-btn"
                :class="{ 'time-option-active': slot.value === pendingStart }"
                role="option"
                :aria-selected="slot.value === pendingStart"
                :data-testid="`time-start-${slot.value}`"
                @click="selectStart(slot.value)"
              >
                {{ slot.label }}
              </button>
            </li>
          </ul>
        </div>

        <div class="time-column">
          <p class="time-column-label">End</p>
          <p v-if="!endSlots.length" class="time-column-empty">Pick a start time first</p>
          <ul v-else class="time-option-list" role="listbox" aria-label="End time" ref="endListRef">
            <li v-for="slot in endSlots" :key="slot.value">
              <button
                type="button"
                class="time-option sb-btn"
                :class="{ 'time-option-active': slot.value === end && slot.value === pendingEnd }"
                role="option"
                :aria-selected="slot.value === pendingEnd"
                :data-testid="`time-end-${slot.value}`"
                @click="selectEnd(slot.value)"
              >
                <span>{{ slot.label }}</span>
                <span v-if="slot.duration" class="time-option-hint">{{ slot.duration }}</span>
              </button>
            </li>
          </ul>
        </div>
      </div>

      <footer class="time-dropdown-footer">
        <p class="time-hint mb-0">{{ hintLabel }}</p>
        <button type="button" class="time-any-btn sb-btn" data-testid="time-any" @click="commit(null, null)">
          Any time
        </button>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import {
  formatDurationLabel,
  formatTimeLabel,
  formatTimeRangeLabel,
  isPastTimeForDate,
  padNumber,
  timeToMinutes,
} from '@/utils/time'

const props = defineProps({
  start: {
    type: String,
    default: null,
  },
  end: {
    type: String,
    default: null,
  },
  selectedDate: {
    type: String,
    default: null,
  },
  placeholder: {
    type: String,
    default: 'Any time',
  },
  title: {
    type: String,
    default: 'Choose a time range',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:start', 'update:end'])

const HOURS_IN_DAY = 24
// The day's final hour can never be a range *start* -- there is no later hour to end on.
const LAST_HOUR = `${padNumber(HOURS_IN_DAY - 1)}:00`

const isOpen = ref(false)
const pendingStart = ref(null)
const endListRef = ref(null)

const hasRange = computed(() => Boolean(props.start && props.end))
const pendingEnd = computed(() => (pendingStart.value === props.start ? props.end : null))

const triggerLabel = computed(() => {
  return formatTimeRangeLabel(props.start, props.end) || props.placeholder
})

const hintLabel = computed(() => {
  if (!pendingStart.value) {
    return 'Pick a start time'
  }

  return `From ${formatTimeLabel(pendingStart.value)} — pick an end time`
})

const hourValues = computed(() =>
  Array.from({ length: HOURS_IN_DAY }, (_, hour) => `${padNumber(hour)}:00`),
)

// Past hours (and the un-startable last hour) are left out entirely rather than shown
// disabled, so the list -- and its scroll position -- only ever holds pickable times.
const startSlots = computed(() =>
  hourValues.value
    .filter((value) => value !== LAST_HOUR && !isPastTimeForDate(props.selectedDate, value))
    .map((value) => ({
      value,
      label: formatTimeLabel(value),
    })),
)

const endSlots = computed(() => {
  if (!pendingStart.value) {
    return []
  }

  return hourValues.value
    .filter(
      (value) =>
        timeToMinutes(value) > timeToMinutes(pendingStart.value) &&
        !isPastTimeForDate(props.selectedDate, value),
    )
    .map((value) => ({
      value,
      label: formatTimeLabel(value),
      duration: formatDurationLabel(pendingStart.value, value),
    }))
})

const commit = (startTime, endTime) => {
  emit('update:start', startTime)
  emit('update:end', endTime)
  pendingStart.value = null
  isOpen.value = false
}

const selectStart = (value) => {
  pendingStart.value = value
}

const selectEnd = (value) => {
  commit(pendingStart.value, value)
}

const closePanel = () => {
  pendingStart.value = null
  isOpen.value = false
}

const onDocumentMousedown = (event) => {
  if (!wrapperRef.value?.contains(event.target)) {
    closePanel()
  }
}

const wrapperRef = ref(null)

const togglePanel = (event) => {
  if (props.disabled) {
    return
  }

  if (isOpen.value) {
    closePanel()
    return
  }

  wrapperRef.value = event.currentTarget.closest('.time-picker-wrap')
  pendingStart.value = props.start
  isOpen.value = true
}

watch(isOpen, (open) => {
  if (open) {
    document.addEventListener('mousedown', onDocumentMousedown)
  } else {
    document.removeEventListener('mousedown', onDocumentMousedown)
  }
})

// endSlots is rebuilt from scratch on every start pick, so the list's old scroll offset can
// leave the new (much shorter) list scrolled past its own content. Snap back to the top so
// the first pickable end hour is visible without the user having to scroll for it.
watch(pendingStart, async () => {
  await nextTick()
  if (endListRef.value) {
    endListRef.value.scrollTop = 0
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', onDocumentMousedown)
})
</script>

<style scoped>
/* Anchored dropdown, matching FindTutors' own `.budget-dropdown-panel` -- the nearest neighbour
   on that filter bar -- and the SubjectPickerModal option rows for the lists inside. Every colour
   resolves through a token: the older BookingDatePicker/BookingTimePicker generation hardcoded
   #ffffff surfaces and renders unreadable under [data-sb-theme="dark"].
   `.time-trigger` keeps its name so InitialBooking's :deep() focus overrides still apply. */

.time-picker-wrap {
  position: relative;
  min-width: 0;
}

.time-trigger {
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  width: 100%;
  min-height: 42px;
  border: 1px solid var(--sb-card-border);
  border-radius: 0.375rem;
  background: color-mix(in srgb, var(--sb-card-bg) 86%, transparent);
  color: var(--sb-text-main);
  padding: 0.5rem 0.85rem;
  font: inherit;
  text-align: left;
}

.time-trigger:hover:not(:disabled),
.time-trigger:focus-visible {
  border-color: var(--sb-primary);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--sb-primary) 12%, transparent);
  outline: none;
}

.time-trigger:disabled {
  background: color-mix(in srgb, var(--sb-card-border) 22%, transparent);
  color: var(--sb-text-subtle);
  cursor: not-allowed;
}

.time-trigger-text {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.time-trigger-text.is-placeholder {
  color: var(--sb-text-muted);
}

.time-trigger-icon {
  flex: 0 0 auto;
  color: var(--sb-primary);
}

.time-trigger-clear {
  display: inline-grid;
  place-items: center;
  flex: 0 0 auto;
  width: 22px;
  height: 22px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--sb-card-border) 55%, transparent);
  color: var(--sb-text-secondary);
  font-size: 0.7rem;
  cursor: pointer;
}

.time-trigger-clear:hover,
.time-trigger-clear:focus-visible {
  background: color-mix(in srgb, var(--sb-primary) 16%, transparent);
  color: var(--sb-primary);
  outline: none;
}

.time-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  left: 0;
  z-index: 25;
  width: min(340px, 92vw);
  border: 1px solid var(--sb-card-border);
  border-radius: 18px;
  background: var(--sb-card-bg);
  box-shadow: 0 20px 44px rgba(10, 122, 81, 0.12);
  padding: 0.85rem;
}

.time-columns {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.time-column {
  min-width: 0;
}

.time-column-label {
  margin: 0 0 0.4rem;
  color: var(--sb-text-muted);
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.time-option-list {
  max-height: 232px;
  overflow-y: auto;
  margin: 0;
  padding: 0;
  list-style: none;
}

.time-column-empty {
  margin: 0;
  color: var(--sb-text-muted);
  font-size: 0.8rem;
  font-weight: 600;
}

.time-option {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.4rem;
  width: 100%;
  border: 0;
  border-radius: 9px;
  background: transparent;
  color: var(--sb-text-main);
  padding: 0.45rem 0.55rem;
  font-size: 0.88rem;
  font-weight: 600;
  text-align: left;
}

.time-option:hover:not(:disabled) {
  background: var(--sb-primary-light);
  color: var(--sb-primary-dark);
}

.time-option:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--sb-primary) 22%, transparent);
}

.time-option:disabled {
  color: var(--sb-text-subtle);
  cursor: not-allowed;
}

.time-option-active {
  background: var(--sb-primary);
  color: var(--sb-primary-contrast);
  font-weight: 700;
}

.time-option-active:hover:not(:disabled) {
  background: var(--sb-primary);
  color: var(--sb-primary-contrast);
}

.time-option-hint {
  flex: 0 0 auto;
  color: var(--sb-text-muted);
  font-size: 0.72rem;
  font-weight: 600;
}

.time-option-active .time-option-hint {
  color: color-mix(in srgb, var(--sb-primary-contrast) 78%, transparent);
}

.time-dropdown-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  border-top: 1px solid color-mix(in srgb, var(--sb-card-border) 70%, transparent);
  margin-top: 0.7rem;
  padding-top: 0.6rem;
}

.time-hint {
  flex: 1;
  min-width: 0;
  color: var(--sb-text-muted);
  font-size: 0.76rem;
  font-weight: 600;
}

.time-any-btn {
  flex: 0 0 auto;
  border: 1px solid var(--sb-card-border);
  border-radius: 999px;
  background: transparent;
  color: var(--sb-text-secondary);
  padding: 0.3rem 0.75rem;
  font-size: 0.78rem;
  font-weight: 700;
}

.time-any-btn:hover {
  border-color: var(--sb-primary);
  color: var(--sb-primary);
}

@media (max-width: 991px) {
  .time-dropdown {
    position: static;
    width: 100%;
    margin-top: 0.5rem;
  }
}
</style>
