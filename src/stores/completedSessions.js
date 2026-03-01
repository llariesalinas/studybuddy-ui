import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useSessionsStore = defineStore('sessions', () => {

  const sessions = ref([])
  const loading = ref(false)
  const error = ref(null)

  const fetchSessions = async () => {
    loading.value = true
    error.value = null

    try {
      const response = await axios.get('/api/tutors/bookings')
      sessions.value = response.data
    } catch (err) {
      error.value = 'Failed to load sessions.'
    } finally {
      loading.value = false
    }
  }

  const completedSessions = computed(() =>
    [...sessions.value]
      .filter(s => s.status?.toLowerCase() === 'completed')
      .sort((a, b) => new Date(b.date) - new Date(a.date))
  )

  const pendingSessions = computed(() =>
    sessions.value.filter(
      s => s.status.toLowerCase() === 'pending'
    )
  )

  return {
    sessions,
    loading,
    error,
    fetchSessions,
    completedSessions,
    pendingSessions
  }
})