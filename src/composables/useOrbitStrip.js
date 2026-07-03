import { computed, onBeforeUnmount, ref, unref } from 'vue'
import { storeToRefs } from 'pinia'
import { useActiveSessionStore } from '@/stores/activeSession'
import { parseSessionDateTime } from '@/composables/useSessionClock'

export const ORBIT_UPCOMING_WINDOW_MS = 15 * 60 * 1000
export const ORBIT_HANDOFF_CAP_MS = 24 * 60 * 60 * 1000

const SECOND_MS = 1000
const MINUTE_MS = 60 * SECOND_MS
const HANDOFF_STATUSES = ['payment required', 'awaiting verification']
const TERMINAL_STATUSES = ['pending', 'rejected', 'cancelled', 'completed']

const clamp = (value, min, max) => Math.min(Math.max(value, min), max)
const normalizeStatus = (status) => String(status || '').toLowerCase()

const pickPersonName = (value) => {
  if (!value) {
    return ''
  }

  if (typeof value === 'string') {
    return value
  }

  return value.name || [value.fname, value.lname].filter(Boolean).join(' ')
}

export const normalizeOrbitSession = (session) => {
  if (!session) {
    return null
  }

  const detail = session.session || session

  return {
    id: session.id ?? detail.id ?? null,
    status: detail.status || session.status || '',
    rawStatus: detail.raw_status || session.raw_status || '',
    date: detail.date || session.date || '',
    startTime: detail.start_time || detail.startTime || session.start_time || session.startTime || '',
    endTime: detail.end_time || detail.endTime || session.end_time || session.endTime || '',
    subject: detail.subject || session.subject || 'Tutoring session',
    tutorName: pickPersonName(session.tutor),
    tuteeName: pickPersonName(session.tutee) || session.tuteeName || session.student || '',
  }
}

export const getOrbitWindow = (session) => {
  const normalized = normalizeOrbitSession(session)

  if (!normalized) {
    return { normalized: null, startAt: null, endAt: null }
  }

  return {
    normalized,
    startAt: parseSessionDateTime(normalized.date, normalized.startTime),
    endAt: parseSessionDateTime(normalized.date, normalized.endTime),
  }
}

export const getOrbitPhase = (session, now = new Date()) => {
  const { normalized, startAt, endAt } = getOrbitWindow(session)

  if (!normalized) {
    return null
  }

  const status = normalizeStatus(normalized.status)

  if (HANDOFF_STATUSES.includes(status)) {
    return 'handoff'
  }

  if (!startAt || !endAt || endAt <= startAt) {
    return null
  }

  const nowMs = now.getTime()
  const startMs = startAt.getTime()
  const endMs = endAt.getTime()

  if (!TERMINAL_STATUSES.includes(status) && nowMs >= startMs && nowMs < endMs) {
    return 'live'
  }

  const msUntilStart = startMs - nowMs
  if (status === 'upcoming' && msUntilStart > 0 && msUntilStart <= ORBIT_UPCOMING_WINDOW_MS) {
    return 'upcoming'
  }

  return null
}

export const shouldShowOrbitStripForSession = (session, now = new Date()) => Boolean(getOrbitPhase(session, now))

const formatDuration = (milliseconds) => {
  const totalSeconds = Math.max(0, Math.floor(milliseconds / SECOND_MS))
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60

  if (hours > 0) {
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
  }

  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
}

const formatRelative = (milliseconds) => {
  const absoluteMs = Math.abs(milliseconds)

  if (absoluteMs < MINUTE_MS) {
    return milliseconds >= 0 ? 'in less than a minute' : 'just now'
  }

  const minutes = Math.round(absoluteMs / MINUTE_MS)

  return milliseconds >= 0 ? `in ${minutes} min` : `${minutes} min ago`
}

const getPartnerLabel = (session, isTutor) => {
  if (isTutor) {
    return session.tuteeName ? `with ${session.tuteeName}` : 'with your tutee'
  }

  return session.tutorName ? `with ${session.tutorName}` : 'with your tutor'
}

const getStateLabel = (state, status) => {
  if (state === 'live') {
    return 'Live now'
  }

  if (state === 'handoff') {
    return normalizeStatus(status) === 'awaiting verification'
      ? 'Verification handoff'
      : 'Payment handoff'
  }

  return 'Starting soon'
}

const getPrimaryText = (state, subject, partnerLabel) => {
  if (state === 'live') {
    return `${subject} ${partnerLabel}`
  }

  if (state === 'handoff') {
    return `${subject} needs follow-up`
  }

  return `${subject} ${partnerLabel}`
}

const getTimerAndProgress = ({ state, startAt, endAt, now }) => {
  const nowMs = now.getTime()

  if (state === 'upcoming') {
    const remainingMs = Math.max(0, startAt.getTime() - nowMs)
    const progress = clamp(((ORBIT_UPCOMING_WINDOW_MS - remainingMs) / ORBIT_UPCOMING_WINDOW_MS) * 100, 0, 100)

    return {
      timerText: `Starts in ${formatDuration(remainingMs)}`,
      progress,
    }
  }

  if (state === 'live') {
    const totalMs = Math.max(1, endAt.getTime() - startAt.getTime())
    const remainingMs = Math.max(0, endAt.getTime() - nowMs)
    const progress = clamp(((nowMs - startAt.getTime()) / totalMs) * 100, 0, 100)

    return {
      timerText: `Ends in ${formatDuration(remainingMs)}`,
      progress,
    }
  }

  const elapsedMs = endAt ? Math.max(0, nowMs - endAt.getTime()) : ORBIT_HANDOFF_CAP_MS

  return {
    timerText: `Ended ${formatDuration(elapsedMs)} ago`,
    progress: clamp((elapsedMs / ORBIT_HANDOFF_CAP_MS) * 100, 0, 100),
  }
}

const getZone = (progress) => {
  if (progress >= 75) {
    return 4
  }

  if (progress >= 50) {
    return 3
  }

  if (progress >= 25) {
    return 2
  }

  return 1
}

const getUpNextHint = ({ session, state, now, isTutor }) => {
  const { normalized, startAt, endAt } = getOrbitWindow(session)

  if (!normalized) {
    return ''
  }

  const label = getStateLabel(state || getOrbitPhase(session, now), normalized.status)
  const partner = getPartnerLabel(normalized, isTutor)
  const referenceMs = state === 'handoff' && endAt
    ? endAt.getTime() - now.getTime()
    : startAt?.getTime() - now.getTime()
  const relative = Number.isFinite(referenceMs) ? formatRelative(referenceMs) : ''

  return ['Up next:', label, '-', normalized.subject, partner, relative].filter(Boolean).join(' ')
}

export const getOrbitPresentation = ({
  session,
  state = null,
  nextSession = null,
  nextState = null,
  now = new Date(),
  isTutor = false,
} = {}) => {
  const { normalized, startAt, endAt } = getOrbitWindow(session)
  const phase = state || getOrbitPhase(session, now)

  if (!normalized || !phase || (phase !== 'handoff' && (!startAt || !endAt))) {
    return {
      hasOrbit: false,
      state: null,
      progress: 0,
      zone: 1,
      upNextHint: '',
    }
  }

  const partnerLabel = getPartnerLabel(normalized, isTutor)
  const timer = getTimerAndProgress({ state: phase, startAt, endAt, now })
  const zone = getZone(timer.progress)

  return {
    hasOrbit: true,
    id: normalized.id,
    state: phase,
    stateLabel: getStateLabel(phase, normalized.status),
    primaryText: getPrimaryText(phase, normalized.subject, partnerLabel),
    subject: normalized.subject,
    partnerLabel,
    timerText: timer.timerText,
    progress: Math.round(timer.progress * 10) / 10,
    zone,
    zoneLabel: `Orbit zone ${zone}`,
    upNextHint: nextSession ? getUpNextHint({ session: nextSession, state: nextState, now, isTutor }) : '',
  }
}

export function useOrbitStrip(options = {}) {
  const hasExplicitSession = Object.prototype.hasOwnProperty.call(options, 'session')
  const activeSession = useActiveSessionStore()
  const { queueItem, queueState, nextQueueItem, nextQueueState } = storeToRefs(activeSession)
  const now = ref(new Date())
  let intervalId = null

  const tick = () => {
    now.value = new Date()
  }

  const clearTicker = () => {
    if (intervalId) {
      window.clearInterval(intervalId)
      intervalId = null
    }
  }

  const startTicker = () => {
    if (typeof window === 'undefined' || intervalId) {
      return
    }

    tick()
    intervalId = window.setInterval(tick, SECOND_MS)
  }

  const syncTicker = () => {
    if (typeof document !== 'undefined' && document.hidden) {
      clearTicker()
      return
    }

    startTicker()
  }

  const handleVisibilityChange = () => {
    tick()
    syncTicker()
  }

  if (typeof document !== 'undefined') {
    document.addEventListener('visibilitychange', handleVisibilityChange)
  }

  startTicker()

  onBeforeUnmount(() => {
    clearTicker()

    if (typeof document !== 'undefined') {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  })

  const sourceSession = computed(() => (
    hasExplicitSession ? unref(options.session) : queueItem.value
  ))
  const sourceState = computed(() => (
    Object.prototype.hasOwnProperty.call(options, 'state') ? unref(options.state) : queueState.value
  ))
  const sourceNextSession = computed(() => (
    Object.prototype.hasOwnProperty.call(options, 'nextSession') ? unref(options.nextSession) : nextQueueItem.value
  ))
  const sourceNextState = computed(() => (
    Object.prototype.hasOwnProperty.call(options, 'nextState') ? unref(options.nextState) : nextQueueState.value
  ))
  const isTutor = computed(() => Boolean(unref(options.isTutor)))

  const presentation = computed(() => getOrbitPresentation({
    session: sourceSession.value,
    state: sourceState.value,
    nextSession: sourceNextSession.value,
    nextState: sourceNextState.value,
    now: now.value,
    isTutor: isTutor.value,
  }))

  return {
    now,
    presentation,
    hasOrbit: computed(() => presentation.value.hasOrbit),
  }
}
