import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api/api'

export const useTutorBookingDetailStore = defineStore('tutorBookingDetail', () => {

  const booking = ref(null)
  const isLoading = ref(false)
  const error = ref(null)


  const tuteeProfile = computed(() => booking.value?.tutee ?? null)

  const sessionInfo = computed(() => booking.value?.session ?? null)

  const paymentInfo = computed(() => booking.value?.payment ?? null)

  const bookingId = computed(() => booking.value?.id ?? null)

//   const fetchBookingDetails = async (bookingId) => {
//     if (!bookingId) return

//     isLoading.value = true
//     error.value = null

//     try {
//       const res = await api.get(`/bookings/${bookingId}/`)
//       booking.value = res.data
//     } catch (err) {
//       console.error('Failed to fetch booking details:', err)
//       error.value = err
//       booking.value = null
//     } finally {
//       isLoading.value = false
//     }
//   }

    const fetchBookingDetails = async () => {
    isLoading.value = true

    // ⏳ simulate loading
    setTimeout(() => {
        booking.value = {
        id: 101,

        tutee: {
            avatar: 'https://i.pravatar.cc/150?img=12',
            name: 'Juan Dela Cruz',
            email: 'juan.delacruz@student.edu.ph',
            course: 'BS Computer Science',
            year_level: '3rd Year',
            bio: 'Hardworking student preparing for exams and projects.'
        },

        session: {
            subject: 'Mathematics',
            topic: 'Integral Calculus',
            date: 'March 12, 2026',
            start_time: '2:00 PM',
            end_time: '3:00 PM',
            rating: 4.5,
            status: 'Completed'
        },

        payment: {
            transaction_id: 'GCASH-8F23K92X',
            method: 'GCash',
            amount_paid: 500,
            tutor_earned: 400,
            platform_fee: 80,
            transaction_fee: 20,
            status: 'Pending'
        }
        }

        isLoading.value = false
    }, 800)
    }

  const confirmPayment = async () => {
    if (!booking.value?.id) return

    try {
      await api.post(`/bookings/${booking.value.id}/confirm-payment/`)
      await fetchBookingDetails(booking.value.id) // refresh data
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
    sessionInfo,
    paymentInfo,
    bookingId,
    fetchBookingDetails,
    confirmPayment,
    resetStore
  }
})