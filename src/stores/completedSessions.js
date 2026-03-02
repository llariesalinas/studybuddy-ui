import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api/api'

export const useSessionsStore = defineStore('sessions', () => {

  const sessions = ref([])
  const loading = ref(false)
  const error = ref(null)

  // const fetchSessions = async () => {
  //   loading.value = true
  //   error.value = null

  //   try {
  //     const response = await api.get('/bookings')
  //     sessions.value = response.data
  //   } catch (err) {
  //     error.value = 'Failed to load sessions.'
  //   } finally {
  //     loading.value = false
  //   }
  // }
  const fetchSessions = async () => {
  loading.value = true
  error.value = null

  try {
    // 🔥 MOCK DATA FOR TESTING
    sessions.value = [
      {
        id: 1,
        subject: 'Calculus',
        tutor: 'Maria Santos',
        date: '2026-03-01',
        startTime: '09:00',
        endTime: '10:00',
        status: 'completed',
        rating: 5,
        earnings: 150
      },
      {
        id: 2,
        subject: 'Physics',
        tutor: 'James Reyes',
        date: '2026-03-02',
        startTime: '13:00',
        endTime: '14:30',
        status: 'completed',
        rating: 4,
        earnings: 200
      },
      {
        id: 3,
        subject: 'Statistics',
        tutor: 'Anna Cruz',
        date: '2026-03-03',
        startTime: '08:00',
        endTime: '09:00',
        status: 'completed',
        rating: 5,
        earnings: 180
      },
      {
        id: 4,
        subject: 'Data Structures',
        tutor: 'Carlos Tan',
        date: '2026-03-05',
        startTime: '10:00',
        endTime: '11:00',
        status: 'upcoming',
        rating: null,
        earnings: null
      },
      {
        id: 5,
        subject: 'Biology',
        tutor: 'Sofia Garcia',
        date: '2026-03-06',
        startTime: '15:00',
        endTime: '16:00',
        status: 'upcoming',
        rating: null,
        earnings: null
      },
      {
        id: 6,
        subject: 'Academic Writing',
        tutor: 'Leo Mendoza',
        date: '2026-02-25',
        startTime: '14:00',
        endTime: '15:00',
        status: 'cancelled',
        rating: null,
        earnings: null
      }
    ]

  } catch (err) {
    error.value = 'Failed to load sessions.'
  } finally {
    loading.value = false
  }
}

  // Helper to prevent crashes if status is null
  const normalizeStatus = (status) =>
    status?.toLowerCase() || ''

  // ✅ Completed
  const completedSessions = computed(() =>
    sessions.value
      .filter(s => normalizeStatus(s.status) === 'completed')
      .sort((a, b) => new Date(b.date) - new Date(a.date))
  )

  // ✅ Upcoming
  const upcomingSessions = computed(() =>
    sessions.value
      .filter(s => normalizeStatus(s.status) === 'upcoming')
      .sort((a, b) => new Date(a.date) - new Date(b.date))
  )

  // ✅ Cancelled
  const cancelledSessions = computed(() =>
    sessions.value
      .filter(s => normalizeStatus(s.status) === 'cancelled')
      .sort((a, b) => new Date(b.date) - new Date(a.date))
  )

  return {
    sessions,
    loading,
    error,
    fetchSessions,
    completedSessions,
    upcomingSessions,
    cancelledSessions
  }
})