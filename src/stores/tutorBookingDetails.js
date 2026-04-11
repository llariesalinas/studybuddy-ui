import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api/api'

export const useTutorBookingDetailStore = defineStore('tutorBookingDetail', () => {

  const booking = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  const tuteeProfile = computed(() => booking.value?.tutee || null)
  const tutorProfile = computed(() => booking.value?.tutor || null)
  const sessionInfo = computed(() => booking.value?.session || null)
  const paymentInfo = computed(() => booking.value?.payment || null)

  const bookingId = computed(() => booking.value?.id || null)

  const fetchBookingDetails = async (bookingId) => {
    if (!bookingId) return

    isLoading.value = true
    error.value = null

    try {
      const res = await api.get(`/bookings/${bookingId}/`)
      booking.value = res.data
    } catch (err) {
      console.error('Failed to fetch booking details:', err)
      error.value = err
      booking.value = null
    } finally {
      isLoading.value = false
    }
  }

  const completeSession = async () => {
    await confirmCompletion()
  }

  const confirmCompletion = async () => {
    const id = booking.value?.id

    if (!id) {
      return
    }

    try {
      await api.post(`/bookings/${id}/tutor-confirm/`)
      await fetchBookingDetails(id)
    } catch (err) {
      console.error('Failed to confirm completion:', err)
      throw err
    }
  }


  const confirmPayment = async () => {
    if (!booking.value?.id) return

    try {
      await api.post(`/bookings/confirm/`, {
        booking_id: booking.value.id
      })

      // Refresh data after confirming
      await fetchBookingDetails(booking.value.id)

    } catch (err) {
      console.error('Failed to confirm payment:', err)
      throw err
    }
  }

  const resetStore = () => {
    booking.value = null
    error.value = null
    isLoading.value = false
  }

  return {
    booking,
    isLoading,
    error,
    tuteeProfile,
    tutorProfile,
    sessionInfo,
    paymentInfo,
    bookingId,
    fetchBookingDetails,
    confirmCompletion,
    confirmPayment,
    resetStore,
    completeSession,
  }
})
