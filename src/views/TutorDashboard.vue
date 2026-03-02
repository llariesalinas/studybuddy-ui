<template>
  <div class="p-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="fw-bold text-dark">Teaching Hub</h2>
      <router-link to="/tch-availability" class="btn bg-sb-primary text-white rounded-3 px-4 fw-semibold shadow-sm">
        Set Schedule
      </router-link>
    </div>

    <div class="row g-4 mb-4">
      <div class="col-md-4">
        <div class="card border-sb rounded-4 p-4 shadow-sm h-100">
          <p class="text-muted small fw-bold mb-2">TOTAL SESSIONS</p>
          <h2 class="fw-bold mb-0 text-dark">{{ totalSessions }}</h2>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card border-sb rounded-4 p-4 shadow-sm h-100">
          <p class="text-muted small fw-bold mb-2">AVG RATING</p>
          <h2 class="fw-bold mb-0 text-dark d-flex align-items-center">
            {{ avgRating }} <i class="bi bi-star-fill text-warning fs-4 ms-2"></i>
          </h2>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card border-0 rounded-4 p-4 shadow-sm h-100" style="background-color: var(--sb-dark);">
          <p class="text-white-50 small fw-bold mb-2">EARNINGS</p>
          <h2 class="fw-bold text-white mb-0">₱{{ earnings }}</h2>
        </div>
      </div>
    </div>

    <div class="card border-sb rounded-4 shadow-sm">
      <div class="card-body p-4">
        <h6 class="fw-bold text-dark mb-4">Upcoming Bookings</h6>
        <div class="table-responsive">
          <table class="table align-middle mb-0">
            <thead>
              <tr class="small fw-bold text-muted">
                <th class="border-bottom-0 pb-3">STUDENT</th>
                <th class="border-bottom-0 pb-3">SUBJECT</th>
                <th class="border-bottom-0 pb-3">DATE</th>
                <th class="border-bottom-0 pb-3">STATUS</th>
              </tr>
            </thead>
            <tbody>
            <tr
              v-for="booking in upcomingBookings"
              :key="booking.date + booking.student"
              style="border-top: 1px solid var(--sb-card-border);"
            >
              <td class="py-3 text-dark">
                {{ booking.student }}
              </td>

              <td class="py-3">
                <span class="badge bg-light text-dark border border-sb px-2 py-1">
                  {{ booking.subject || 'General' }}
                </span>
              </td>

              <td class="py-3 text-dark">
                {{ new Date(booking.date).toLocaleDateString() }}
              </td>

              <td class="py-3">
                <span
                  class="badge px-3 py-1 rounded-pill"
                  :class="{
                    'bg-success bg-opacity-10 text-success border border-success':
                      booking.status === 'Confirmed',
                    'bg-secondary bg-opacity-10 text-secondary border border-secondary':
                      booking.status === 'Completed'
                  }"
                >
                  {{ booking.status }}
                </span>

                <!-- ✅ Complete Button -->
                <button 
                    class="btn btn-sm bg-sb-primary text-white"
                    @click="goToDetails(session.id)"
                  >
                    View Details
                  </button>
              </td>
            </tr>
          </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api/api'

const totalSessions = ref(0)
const avgRating = ref(0)
const earnings = ref(0)
const upcomingBookings = ref([])

const goToDetails = (sessionId) => {
  router.push(`/booking-details/${sessionId}`)
}

const loadTutorDashboard = async () => {
  try {
    const response = await api.get('tutor-dashboard/')

    totalSessions.value = response.data.total_sessions
    avgRating.value = response.data.rating_average
    upcomingBookings.value = response.data.upcoming_bookings
    earnings.value = totalSessions.value * response.data.hourly_rate

  } catch (error) {
    console.error("Failed to load tutor dashboard:", error)
  }
}

const completeSession = async (booking) => {
  try {
    await api.post(`bookings/${booking.id}/complete/`)
    await loadTutorDashboard()
    alert("Session marked as completed successfully.")
  } catch (error) {
    alert(error.response?.data?.error || "Failed to complete session.")
  }
}

onMounted(loadTutorDashboard)
</script>