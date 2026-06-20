import { computed, onBeforeUnmount, ref, unref, watch } from 'vue'

const MANILA_OFFSET = '+08:00'
const SECOND_MS = 1000
const MINUTE_MS = 60 * SECOND_MS

const normalizeTime = (timeValue) => {
  if (!timeValue) {
    return null
  }

  const [hour = '00', minute = '00', second = '00'] = String(timeValue).split(':')
  return `${hour.padStart(2, '0')}:${minute.padStart(2, '0')}:${second.padStart(2, '0')}`
}

export const parseSessionDateTime = (dateValue, timeValue) => {
  const time = normalizeTime(timeValue)

  if (!dateValue || !time) {
    return null
  }

  const parsed = new Date(`${String(dateValue).slice(0, 10)}T${time}${MANILA_OFFSET}`)
  return Number.isNaN(parsed.getTime()) ? null : parsed
}

const clamp = (value, min, max) => Math.min(Math.max(value, min), max)

const formatDuration = (seconds) => {
  const safeSeconds = Math.max(0, Math.floor(seconds))
  const hours = Math.floor(safeSeconds / 3600)
  const minutes = Math.floor((safeSeconds % 3600) / 60)
  const remainingSeconds = safeSeconds % 60

  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`
}

const formatClockTime = (date) => {
  if (!date) {
    return 'N/A'
  }

  return new Intl.DateTimeFormat(undefined, {
    hour: 'numeric',
    minute: '2-digit',
    timeZone: 'Asia/Manila',
  }).format(date)
}

export const getSessionClockState = ({ date, startTime, endTime, now = new Date() }) => {
  const startAt = parseSessionDateTime(date, startTime)
  const endAt = parseSessionDateTime(date, endTime)

  if (!startAt || !endAt || endAt <= startAt) {
    return {
      startAt,
      endAt,
      isLive: false,
      elapsedSeconds: 0,
      totalSeconds: 0,
      minutesLeft: 0,
      progress: 0,
      formattedElapsed: '00:00:00',
      startedLabel: formatClockTime(startAt),
      endsLabel: formatClockTime(endAt),
    }
  }

  const totalMs = endAt.getTime() - startAt.getTime()
  const elapsedMs = clamp(now.getTime() - startAt.getTime(), 0, totalMs)
  const remainingMs = Math.max(0, endAt.getTime() - now.getTime())
  const elapsedSeconds = Math.floor(elapsedMs / SECOND_MS)

  return {
    startAt,
    endAt,
    isLive: now.getTime() >= startAt.getTime() && now.getTime() < endAt.getTime(),
    elapsedSeconds,
    totalSeconds: Math.floor(totalMs / SECOND_MS),
    minutesLeft: Math.ceil(remainingMs / MINUTE_MS),
    progress: totalMs ? Math.round((elapsedMs / totalMs) * 1000) / 10 : 0,
    formattedElapsed: formatDuration(elapsedSeconds),
    startedLabel: formatClockTime(startAt),
    endsLabel: formatClockTime(endAt),
  }
}

export function useSessionClock({ date, startTime, endTime, isOngoing }) {
  const now = ref(new Date())
  let intervalId = null

  const state = computed(() =>
    getSessionClockState({
      date: unref(date),
      startTime: unref(startTime),
      endTime: unref(endTime),
      now: now.value,
    }),
  )

  const isActive = () => {
    if (typeof document !== 'undefined' && document.hidden) {
      return false
    }

    return Boolean(unref(isOngoing)) || state.value.isLive
  }

  const clearTicker = () => {
    if (intervalId) {
      window.clearInterval(intervalId)
      intervalId = null
    }
  }

  const startTicker = () => {
    if (typeof window === 'undefined' || intervalId || !isActive()) {
      return
    }

    now.value = new Date()
    intervalId = window.setInterval(() => {
      now.value = new Date()
    }, SECOND_MS)
  }

  const syncTicker = () => {
    if (isActive()) {
      startTicker()
    } else {
      clearTicker()
    }
  }

  const handleVisibilityChange = () => {
    now.value = new Date()
    syncTicker()
  }

  if (typeof document !== 'undefined') {
    document.addEventListener('visibilitychange', handleVisibilityChange)
  }

  watch(
    () => Boolean(unref(isOngoing)) || state.value.isLive,
    syncTicker,
    { immediate: true },
  )

  onBeforeUnmount(() => {
    clearTicker()

    if (typeof document !== 'undefined') {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  })

  return {
    now,
    isLive: computed(() => state.value.isLive),
    startAt: computed(() => state.value.startAt),
    endAt: computed(() => state.value.endAt),
    elapsedSeconds: computed(() => state.value.elapsedSeconds),
    totalSeconds: computed(() => state.value.totalSeconds),
    minutesLeft: computed(() => state.value.minutesLeft),
    progress: computed(() => state.value.progress),
    formattedElapsed: computed(() => state.value.formattedElapsed),
    startedLabel: computed(() => state.value.startedLabel),
    endsLabel: computed(() => state.value.endsLabel),
  }
}
