import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import api from '@/services/api/api'

export const useSessionsStore = defineStore('sessions', () => {
  const sessions = ref([])
  const loading = ref(false)
  const error = ref(null)
  const seenPendingRequestIds = ref([])
  const recommendedTutors = ref([])

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

  const fetchRecommendations = async () => {
    try{
      const response = await api.get('/dashboard')

      recommendedTutors.value = response.data.recommendation
    }
    catch(error){
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
    const dateDifference = new Date(left.date) - new Date(right.date)

    if (dateDifference !== 0) {
      return direction === 'asc' ? dateDifference : -dateDifference
    }

    const timeDifference = toMinutes(left.startTime) - toMinutes(right.startTime)
    return direction === 'asc' ? timeDifference : -timeDifference
  }

  const mergeGroupedSessions = (rawSessions = []) => {
    const groupedSessions = new Map()

    rawSessions.forEach((session) => {
      const groupKey = session.session_group_id || `booking-${session.id}`
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
        date: existingSession.date <= session.date ? existingSession.date : session.date,
        startTime: formatMinutes(Math.min(existingStart, nextStart)),
        endTime: formatMinutes(Math.max(existingEnd, nextEnd)),
        duration_hours: (existingSession.duration_hours || 0) + (session.duration_hours || 0),
        tutee_confirmed: existingSession.tutee_confirmed || session.tutee_confirmed,
        tutor_confirmed: existingSession.tutor_confirmed || session.tutor_confirmed,
        rating: existingSession.rating ?? session.rating,
        rating_submitted: existingSession.rating_submitted || session.rating_submitted,
      })
    })

    return Array.from(groupedSessions.values()).sort((left, right) => {
      const dateComparison = new Date(left.date) - new Date(right.date)

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

  const fetchSessions = async () => {
    loading.value = true
    error.value = null

    try {
      const response = await api.get('/bookings/')
      sessions.value = mergeGroupedSessions(response.data)
    } catch (err) {
      console.error('Failed to load sessions:', err)
      error.value = 'Failed to load sessions.'
    } finally {
      loading.value = false
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
    await fetchSessions()
  }

  const rejectSession = async (id) => {
    await api.post(`/bookings/${id}/reject/`)
    await fetchSessions()
  }

  const submitPayment = async (id, payload) => {
    await api.post(`/bookings/${id}/submit-payment/`, payload, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    await fetchSessions()
    return fetchSessionById(id)
  }

  const submitRating = async (id, ratingScore, comment = '') => {
    await api.post(`/bookings/${id}/rating/`, {
      rating_score: ratingScore,
      comment
    })

    await fetchSessions()
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
    markPendingRequestsSeen,
    submitPayment,
    submitRating,
  }
})
