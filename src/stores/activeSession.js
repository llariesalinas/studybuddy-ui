import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { useSessionsStore } from '@/stores/completedSessions'
import { SESSION_POLL_INTERVAL_MS } from '@/config.js'
import { parseSessionDateTime } from '@/composables/useSessionClock'

const DISMISSED_KEY = 'studybuddy_dismissed_checkins'
const ACTIVE_STATUSES = ['ongoing', 'upcoming']
const HANDOFF_STATUSES = ['payment required', 'awaiting verification']
const UPCOMING_WINDOW_MS = 15 * 60 * 1000

const loadDismissed = () => {
  if (typeof window === 'undefined') {
    return {}
  }

  try {
    return JSON.parse(window.localStorage.getItem(DISMISSED_KEY) || '{}') || {}
  } catch {
    return {}
  }
}

const toMinutes = (timeValue) => {
  if (!timeValue) {
    return 0
  }

  const [hours = 0, minutes = 0] = String(timeValue)
    .split(':')
    .map((part) => Number.parseInt(part, 10) || 0)

  return (hours * 60) + minutes
}

const parseDateTime = (dateValue, timeValue) => {
  if (!dateValue || !timeValue) {
    return null
  }

  const parsed = parseSessionDateTime(dateValue, timeValue)

  return parsed && !Number.isNaN(parsed.getTime()) ? parsed : null
}

const normalizeStatus = (status) => String(status || '').toLowerCase()

const getSessionWindow = (session) => {
  const startAt = parseDateTime(session?.date, session?.startTime)
  const endAt = parseDateTime(session?.date, session?.endTime)

  return { startAt, endAt }
}

export const useActiveSessionStore = defineStore('activeSession', () => {
  const sessionsStore = useSessionsStore()

  const currentTime = ref(new Date())
  const activeDetail = ref(null)
  const dismissed = ref(loadDismissed())
  let pollTimer = null

  const activeBooking = computed(() => {
    const now = currentTime.value.getTime()

    const candidates = sessionsStore.sessions
      .filter((session) => ACTIVE_STATUSES.includes(String(session.status || '').toLowerCase()))
      .filter((session) => {
        const start = parseDateTime(session.date, session.startTime)
        const end = parseDateTime(session.date, session.endTime)

        if (!start || !end) {
          return false
        }

        return now >= start.getTime() && now < end.getTime()
      })
      .sort((left, right) => {
        const dateDiff = new Date(left.date) - new Date(right.date)
        return dateDiff !== 0 ? dateDiff : toMinutes(left.startTime) - toMinutes(right.startTime)
      })

    return candidates[0] || null
  })

  const queueCandidates = computed(() => {
    const now = currentTime.value.getTime()
    const live = []
    const handoff = []
    const upcoming = []

    sessionsStore.sessions.forEach((session) => {
      const status = normalizeStatus(session.status)
      const { startAt, endAt } = getSessionWindow(session)

      if (!startAt || !endAt) {
        return
      }

      if (HANDOFF_STATUSES.includes(status)) {
        handoff.push({ session, state: 'handoff', startAt, endAt })
        return
      }

      if (
        ACTIVE_STATUSES.includes(status)
        && now >= startAt.getTime()
        && now < endAt.getTime()
      ) {
        live.push({ session, state: 'live', startAt, endAt })
        return
      }

      const msUntilStart = startAt.getTime() - now
      if (
        status === 'upcoming'
        && msUntilStart > 0
        && msUntilStart <= UPCOMING_WINDOW_MS
      ) {
        upcoming.push({ session, state: 'upcoming', startAt, endAt })
      }
    })

    live.sort((left, right) => left.startAt - right.startAt)
    handoff.sort((left, right) => left.endAt - right.endAt)
    upcoming.sort((left, right) => left.startAt - right.startAt)

    return [...live, ...handoff, ...upcoming]
  })

  const queueEntry = computed(() => queueCandidates.value[0] || null)
  const queueItem = computed(() => queueEntry.value?.session || null)
  const queueState = computed(() => queueEntry.value?.state || null)
  const nextQueueEntry = computed(() => queueCandidates.value[1] || null)
  const nextQueueItem = computed(() => nextQueueEntry.value?.session || null)
  const nextQueueState = computed(() => nextQueueEntry.value?.state || null)

  const detailSession = computed(() => activeDetail.value?.session || null)
  const sessionStartAt = computed(() => parseDateTime(detailSession.value?.date, detailSession.value?.start_time))
  const sessionEndAt = computed(() => parseDateTime(detailSession.value?.date, detailSession.value?.end_time))
  const sessionMidpointAt = computed(() => {
    if (!sessionStartAt.value || !sessionEndAt.value) {
      return null
    }

    return new Date((sessionStartAt.value.getTime() + sessionEndAt.value.getTime()) / 2)
  })

  const isWithinWindow = computed(() => {
    if (!sessionStartAt.value || !sessionEndAt.value) {
      return false
    }

    const now = currentTime.value.getTime()
    return now >= sessionStartAt.value.getTime() && now < sessionEndAt.value.getTime()
  })

  const isConfirmed = computed(() => String(detailSession.value?.raw_status || '').toLowerCase() === 'confirmed')
  const isFaceToFace = computed(() => detailSession.value?.session_mode === 'F2F')
  const venueCheckIn = computed(() => activeDetail.value?.check_ins?.venue_confirm || null)
  const midpointCheckIn = computed(() => activeDetail.value?.check_ins?.midpoint_checkin || null)
  const preferredLocation = computed(() => detailSession.value?.preferred_location || '')

  const activeId = computed(() => activeDetail.value?.id ?? activeBooking.value?.id ?? null)

  const isDismissed = (event) => (
    activeId.value != null && dismissed.value[`${activeId.value}:${event}`] === true
  )

  const venueDue = computed(() => (
    isConfirmed.value
    && isFaceToFace.value
    && isWithinWindow.value
    && !venueCheckIn.value
    && !isDismissed('venue')
  ))

  const midpointDue = computed(() => (
    isConfirmed.value
    && isWithinWindow.value
    && sessionMidpointAt.value
    && currentTime.value.getTime() >= sessionMidpointAt.value.getTime()
    && !midpointCheckIn.value
    && !isDismissed('midpoint')
    && !venueDue.value
  ))

  const dueCheckIn = computed(() => {
    if (venueDue.value) {
      return 'venue'
    }

    if (midpointDue.value) {
      return 'midpoint'
    }

    return null
  })

  const sessionPhase = computed(() => {
    if (!sessionStartAt.value || !sessionEndAt.value) {
      return 'before'
    }

    const now = currentTime.value.getTime()

    if (now < sessionStartAt.value.getTime()) {
      return 'before'
    }

    if (now >= sessionEndAt.value.getTime()) {
      return 'over'
    }

    if (sessionMidpointAt.value && now >= sessionMidpointAt.value.getTime()) {
      return 'midpoint'
    }

    return 'venue-window'
  })

  const refreshActive = async () => {
    await sessionsStore.fetchSessions()

    const booking = activeBooking.value

    if (!booking) {
      activeDetail.value = null
      return
    }

    activeDetail.value = await sessionsStore.fetchSessionById(booking.id)
  }

  const startPolling = () => {
    if (pollTimer) {
      return
    }

    currentTime.value = new Date()
    refreshActive()

    pollTimer = window.setInterval(() => {
      currentTime.value = new Date()
      refreshActive()
    }, SESSION_POLL_INTERVAL_MS)
  }

  const stopPolling = () => {
    if (pollTimer) {
      window.clearInterval(pollTimer)
      pollTimer = null
    }

    activeDetail.value = null
  }

  const persistDismissed = () => {
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(DISMISSED_KEY, JSON.stringify(dismissed.value))
    }
  }

  const dismiss = (event) => {
    if (activeId.value == null) {
      return
    }

    dismissed.value = { ...dismissed.value, [`${activeId.value}:${event}`]: true }
    persistDismissed()
  }

  const confirmVenue = async (response) => {
    if (activeId.value == null) {
      return
    }

    activeDetail.value = await sessionsStore.confirmVenue(activeId.value, response)
  }

  const submitMidpointCheckIn = async (response) => {
    if (activeId.value == null) {
      return
    }

    activeDetail.value = await sessionsStore.submitMidpointCheckIn(activeId.value, response)
  }

  return {
    currentTime,
    activeDetail,
    activeBooking,
    queueCandidates,
    queueItem,
    queueState,
    nextQueueItem,
    nextQueueState,
    dueCheckIn,
    sessionPhase,
    sessionStartAt,
    sessionEndAt,
    sessionMidpointAt,
    preferredLocation,
    isWithinWindow,
    startPolling,
    stopPolling,
    refreshActive,
    dismiss,
    confirmVenue,
    submitMidpointCheckIn,
  }
})
