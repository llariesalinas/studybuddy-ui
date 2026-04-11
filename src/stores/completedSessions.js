import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api/api'

export const useSessionsStore = defineStore('sessions', () => {

  const sessions = ref([])
  const loading = ref(false)
  const error = ref(null)
  const recommendedTutors = ref([])

  const fetchSessions = async () => {
    loading.value = true
    error.value = null

    try {
      const response = await api.get('/bookings/')
      sessions.value = response.data
    } catch (err) {
      error.value = 'Failed to load sessions.'
    } finally {
      loading.value = false
    }
  }

  const fetchRecommendations = async () => {
    try{
      const response = await api.get('/recommend-tutors/')

      recommendedTutors.value = response.data.recommendation
    }
    catch(error){
      console.error('Error loading recommended tutors.', error)
    }
  }

  const fetchSessionById = async (id) => {
      const localSession = sessions.value.find(s => String(s.id) === String(id))

      if (localSession) {
          return localSession
      }

      loading.value = true
      error.value = null

      try {
          const response = await api.get(`/bookings/${id}`)
          return response.data
          
      } catch (err) {
          console.error("Error fetching session by ID:", err)
          error.value = "Failed to load session details."
          throw err 
      } finally {
          loading.value = false
      }
  }

  const normalizeStatus = (status) =>
    status?.toLowerCase() || ''

  const completedSessions = computed(() =>
    sessions.value
      .filter(s => normalizeStatus(s.status) === 'completed')
      .sort((a, b) => new Date(b.date) - new Date(a.date))
  )

  const upcomingSessions = computed(() =>
    sessions.value
      .filter(s => normalizeStatus(s.status) === 'confirmed')
      .sort((a, b) => new Date(a.date) - new Date(b.date))
  )

  const cancelledSessions = computed(() =>
    sessions.value
      .filter(s => normalizeStatus(s.status) === 'cancelled')
      .sort((a, b) => new Date(b.date) - new Date(a.date))
  )

  const requestedSessions = computed(() =>
  sessions.value
    .filter(s => normalizeStatus(s.status) === 'pending')
    .sort((a, b) => new Date(a.date) - new Date(b.date))
  )

  const ongoingSessions = computed(() =>
  sessions.value
    .filter(s => normalizeStatus(s.status) === 'ongoing')
    .sort((a, b) => new Date(a.date) - new Date(b.date))
  )

  const approveSession = async (id) => {
  await api.post(`/bookings/${id}/approve/`)

  const session = sessions.value.find(s => s.id === id)
  if (session) {
    session.status = "Confirmed"
  }

  }

  const rejectSession = async (id) => {
  await api.post(`/bookings/${id}/reject/`)

  const session = sessions.value.find(s => s.id === id)
  if (session) {
    session.status = "Cancelled"
  }
  } 

  const completeSession = async (id, rating) => {
    await api.post(`/bookings/${id}/complete/`, { 
      rating: rating 
    })

    const session = sessions.value.find(s => s.id === id)
    if (session) {
      session.status = "Completed"
      session.rating = rating
    }
  }

  return {
    sessions,
    loading,
    error,
    recommendedTutors,
    fetchRecommendations,
    fetchSessions,
    completedSessions,
    upcomingSessions,
    cancelledSessions,
    requestedSessions,
    ongoingSessions,
    approveSession,
    rejectSession,
    completeSession,
    fetchSessionById
  }
})