import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import api from '@/services/api/api'

export const useSessionsStore = defineStore('sessions', () => {
  const sessions = ref([])
  const loading = ref(false)
  const error = ref(null)
  const seenPendingRequestIds = ref([])
  const recommendedTutors = ref([])
  const SESSION_FRESHNESS_MS = 15_000
  let sessionsRequest = null
  let lastSessionsFetchedAt = 0

  if (typeof window !== 'undefined') {
    try {
      const storedIds = JSON.parse(
        window.localStorage.getItem('studybuddy_seen_pending_request_ids') || '[]'
      )
      seenPendingRequestIds.value = Array.isArray(storedIds)
        ? storedIds.map(id => String(id))
        : []
    } catch {
      seenPendingRequestIds.value = []
    }
  }

  const normalizeStatus = (status) => String(status || '').toLowerCase()

  const normalizeDateKey = (dateValue) => {
    const rawString = String(dateValue || '')

    if (/^\d{4}-\d{2}-\d{2}$/.test(rawString)) {
      return rawString
    }

    return rawString.slice(0, 10)
  }

  const getDashboardPillKey = (session) => {
    const sessionDateKey = normalizeDateKey(session?.date)

    if (session?.booking_request_id) {
      return `request-${sessionDateKey}-${session.booking_request_id}`
    }

    if (session?.session_group_id) {
      return `group-${sessionDateKey}-${session.session_group_id}`
    }

    return `booking-${session?.id}`
  }

  const fetchRecommendations = async () => {
    try {
      const response = await api.get('/recommendations')
      recommendedTutors.value = response.data.recommendations || []
    } catch (error) {
      recommendedTutors.value = []
      console.error('Error loading recommended tutors.', error)
    }
  }

  const toMinutes = (timeValue) => {
    if (!timeValue) return 0

    const [hours = 0, minutes = 0] = String(timeValue)
      .split(':')
      .map((part) => Number.parseInt(part, 10) || 0)

    return (hours * 60) + minutes
  }

  const formatMinutes = (totalMinutes) => {
    const safeMinutes = Math.max(0, totalMinutes)
    const hours = Math.floor(safeMinutes / 60)
    const minutes = safeMinutes % 60

    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`
  }

  const compareSessionsByDateTime = (left, right, direction = 'asc') => {
    const dateDifference = new Date(normalizeDateKey(left.date)) - new Date(normalizeDateKey(right.date))

    if (dateDifference !== 0) {
      return direction === 'asc' ? dateDifference : -dateDifference
    }

    const timeDifference = toMinutes(left.startTime) - toMinutes(right.startTime)
    return direction === 'asc' ? timeDifference : -timeDifference
  }

  const mergeGroupedSessions = (rawSessions = []) => {
    const groupedSessions = new Map()

    rawSessions.forEach((session) => {
      const sessionDateKey = normalizeDateKey(session.date)
      const groupKey = session.session_group_id
        ? `${sessionDateKey}-${session.session_group_id}`
        : `booking-${session.id}`
      const existingSession = groupedSessions.get(groupKey)

      if (!existingSession) {
        groupedSessions.set(groupKey, { ...session })
        return
      }

      const existingStart = toMinutes(existingSession.startTime)
      const nextStart = toMinutes(session.startTime)
      const existingEnd = toMinutes(existingSession.endTime)
      const nextEnd = toMinutes(session.endTime)

      groupedSessions.set(groupKey, {
        ...existingSession,
        id: existingStart <= nextStart ? existingSession.id : session.id,
        date: sessionDateKey,
        startTime: formatMinutes(Math.min(existingStart, nextStart)),
        endTime: formatMinutes(Math.max(existingEnd, nextEnd)),
        duration_hours: (existingSession.duration_hours || 0) + (session.duration_hours || 0),
        tutee_confirmed: existingSession.tutee_confirmed || session.tutee_confirmed,
        tutor_confirmed: existingSession.tutor_confirmed || session.tutor_confirmed,
        rating: existingSession.rating ?? session.rating,
        rating_submitted: existingSession.rating_submitted || session.rating_submitted,
        dashboard_hidden_by_current_user: (
          existingSession.dashboard_hidden_by_current_user
          || session.dashboard_hidden_by_current_user
        ),
      })
    })

    return Array.from(groupedSessions.values()).sort((left, right) => {
      const dateComparison = new Date(normalizeDateKey(left.date)) - new Date(normalizeDateKey(right.date))

      if (dateComparison !== 0) {
        return dateComparison
      }

      return toMinutes(left.startTime) - toMinutes(right.startTime)
    })
  }

  const syncSessionSummary = (updatedSession) => {
    const index = sessions.value.findIndex(session => String(session.id) === String(updatedSession.id))

    if (index === -1) {
      return
    }

    sessions.value[index] = {
      ...sessions.value[index],
      status: updatedSession.session?.status || sessions.value[index].status,
      tutee_confirmed: updatedSession.tutee_confirmed,
      tutor_confirmed: updatedSession.tutor_confirmed,
      rating: updatedSession.session?.rating,
      rating_submitted: updatedSession.rating_submitted,
    }
  }

  const fetchSessions = async ({ force = false } = {}) => {
    const now = Date.now()

    if (!force && sessionsRequest) {
      return sessionsRequest
    }

    if (!force && lastSessionsFetchedAt && now - lastSessionsFetchedAt < SESSION_FRESHNESS_MS) {
      return sessions.value
    }

    loading.value = true
    error.value = null

    sessionsRequest = (async () => {
      try {
        const response = await api.get('/bookings/')
        sessions.value = mergeGroupedSessions(response.data)
        lastSessionsFetchedAt = Date.now()
      } catch (err) {
        console.error('Failed to load sessions:', err)
        error.value = 'Failed to load sessions.'
      }

      return sessions.value
    })()

    try {
      return await sessionsRequest
    } finally {
      loading.value = false
      sessionsRequest = null
    }
  }

  const fetchSessionById = async (id) => {
    loading.value = true
    error.value = null

    try {
      const response = await api.get(`/bookings/${id}/`)
      syncSessionSummary(response.data)
      return response.data
    } catch (err) {
      console.error('Error fetching session by ID:', err)
      error.value = 'Failed to load session details.'
      throw err
    } finally {
      loading.value = false
    }
  }

  const approveSession = async (id) => {
    await api.post(`/bookings/${id}/approve/`)
    await fetchSessions({ force: true })
  }

  const rejectSession = async (id) => {
    await api.post(`/bookings/${id}/reject/`)
    await fetchSessions({ force: true })
  }

  const cancelSession = async (id, reason) => {
    await api.post(`/bookings/${id}/cancel/`, { reason })
    await fetchSessions({ force: true })
    return fetchSessionById(id)
  }

  const dismissDashboardPill = async (id) => {
    const targetSession = sessions.value.find(session => String(session.id) === String(id))
    const targetPillKey = targetSession ? getDashboardPillKey(targetSession) : null
    const response = await api.delete(`/bookings/${id}/dashboard-pill/`)
    const hiddenBookingIds = new Set((response.data?.hidden_booking_ids || []).map(value => String(value)))

    sessions.value = sessions.value.map((session) => {
      const isHiddenBookingId = hiddenBookingIds.has(String(session.id))
      const isSamePill = targetPillKey && getDashboardPillKey(session) === targetPillKey

      if (!isHiddenBookingId && !isSamePill) {
        return session
      }

      return {
        ...session,
        dashboard_hidden_by_current_user: true,
      }
    })

    await fetchSessions({ force: true })
  }

  const submitPayment = async (id, payload) => {
    await api.post(`/bookings/${id}/submit-payment/`, payload, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    await fetchSessions({ force: true })
    return fetchSessionById(id)
  }

  const verifyOnlinePayment = async (id) => {
    await api.post(`/bookings/${id}/verify-online-payment/`)
    await fetchSessions({ force: true })
    return fetchSessionById(id)
  }

  const submitRating = async (id, ratingScore, comment = '') => {
    await api.post(`/bookings/${id}/rating/`, {
      rating_score: ratingScore,
      comment
    })

    await fetchSessions({ force: true })
    return fetchSessionById(id)
  }

  const confirmVenue = async (id, response) => {
    await api.post(`/bookings/${id}/venue-confirmation/`, { response })
    await fetchSessions({ force: true })
    return fetchSessionById(id)
  }

  const submitMidpointCheckIn = async (id, response) => {
    await api.post(`/bookings/${id}/midpoint-check-in/`, { response })
    await fetchSessions({ force: true })
    return fetchSessionById(id)
  }

  const completedSessions = computed(() =>
    sessions.value
      .filter(session => normalizeStatus(session.status) === 'completed')
      .sort((left, right) => compareSessionsByDateTime(left, right, 'desc'))
  )

  const upcomingSessions = computed(() =>
    sessions.value
      .filter(session => ['upcoming', 'ongoing', 'payment required', 'awaiting verification'].includes(normalizeStatus(session.status)))
      .sort((left, right) => compareSessionsByDateTime(left, right, 'asc'))
  )

  const ongoingSessions = computed(() =>
    sessions.value
      .filter(session => normalizeStatus(session.status) === 'ongoing')
      .sort((left, right) => compareSessionsByDateTime(left, right, 'asc'))
  )

  const requestedSessions = computed(() =>
    sessions.value
      .filter(session => normalizeStatus(session.status) === 'pending')
      .sort((left, right) => compareSessionsByDateTime(left, right, 'asc'))
  )

  const currentPendingRequestIds = computed(() =>
    requestedSessions.value.map(session => String(session.id))
  )

  const unseenPendingRequestIds = computed(() =>
    currentPendingRequestIds.value.filter(id => !seenPendingRequestIds.value.includes(id))
  )

  const hasNewPendingRequests = computed(() =>
    unseenPendingRequestIds.value.length > 0
  )

  const rejectedSessions = computed(() =>
    sessions.value
      .filter(session => normalizeStatus(session.status) === 'rejected')
      .sort((left, right) => compareSessionsByDateTime(left, right, 'desc'))
  )

  const cancelledSessions = computed(() =>
    sessions.value
      .filter(session => normalizeStatus(session.status) === 'cancelled')
      .sort((left, right) => compareSessionsByDateTime(left, right, 'desc'))
  )

  const unratedCompletedSessions = computed(() =>
    completedSessions.value.filter(session => !session.rating_submitted)
  )

  const hasUnratedCompletedSessions = computed(() =>
    unratedCompletedSessions.value.length > 0
  )

  const markPendingRequestsSeen = () => {
    seenPendingRequestIds.value = [...currentPendingRequestIds.value]

    if (typeof window !== 'undefined') {
      window.localStorage.setItem(
        'studybuddy_seen_pending_request_ids',
        JSON.stringify(seenPendingRequestIds.value)
      )
    }
  }

  return {
    sessions,
    loading,
    error,
    recommendedTutors,
    completedSessions,
    unratedCompletedSessions,
    upcomingSessions,
    ongoingSessions,
    requestedSessions,
    unseenPendingRequestIds,
    hasNewPendingRequests,
    rejectedSessions,
    cancelledSessions,
    hasUnratedCompletedSessions,
    fetchSessions,
    fetchRecommendations,
    fetchSessionById,
    approveSession,
    rejectSession,
    cancelSession,
    dismissDashboardPill,
    markPendingRequestsSeen,
    submitPayment,
    verifyOnlinePayment,
    submitRating,
    confirmVenue,
    submitMidpointCheckIn,
  }
})
