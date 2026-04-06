<template>
  <div class="p-4">

    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="fw-bold text-dark">Teaching Hub</h2>

      <router-link
        to="/tch-availability"
        class="btn bg-sb-primary text-white rounded-3 px-4 fw-semibold shadow-sm"
      >
        Set Schedule
      </router-link>
    </div>


    <!-- Stats Cards -->
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
            {{ avgRating }}
            <i class="bi bi-star-fill text-warning fs-4 ms-2"></i>
          </h2>
        </div>
      </div>

      <div class="col-md-4">
        <div
          class="card border-0 rounded-4 p-4 shadow-sm h-100"
          style="background-color: var(--sb-dark);"
        >
          <p class="text-white-50 small fw-bold mb-2">EARNINGS</p>
          <h2 class="fw-bold text-white mb-0">₱{{ earnings }}</h2>
        </div>
      </div>

    </div>


    <!-- Upcoming Bookings -->
    <div class="card border-sb rounded-4 shadow-sm">

      <div class="card-body p-4">

        <h6 class="fw-bold text-dark mb-4">Upcoming Bookings</h6>

        <!-- No bookings -->
        <div v-if="upcomingBookings.length === 0" class="text-muted text-center py-4">
          No upcoming sessions yet.
        </div>

        <!-- Table -->
        <div v-else class="table-responsive">

          <table class="table align-middle mb-0">

            <thead>
              <tr class="small fw-bold text-muted">
                <th class="border-bottom-0 pb-3">STUDENT</th>
                <th class="border-bottom-0 pb-3">SUBJECT</th>
                <th class="border-bottom-0 pb-3">DATE</th>
                <th class="border-bottom-0 pb-3">STATUS</th>
                <th class="border-bottom-0 pb-3"></th>
              </tr>
            </thead>

            <tbody>

              <tr
                v-for="booking in upcomingBookings"
                :key="booking.id"
                style="border-top: 1px solid var(--sb-card-border);"
              >

                <!-- Student -->
                <td class="py-3 text-dark">
                  {{ booking.student }}
                </td>

                <!-- Subject -->
                <td class="py-3">
                  <span class="badge bg-light text-dark border border-sb px-2 py-1">
                    {{ booking.subject || 'General' }}
                  </span>
                </td>

                <!-- Date -->
                <td class="py-3 text-dark">
                  {{ new Date(booking.date).toLocaleDateString() }}
                </td>

                <!-- Status -->
                <td class="py-3">

                  <span
                    class="badge px-3 py-1 rounded-pill"
                    :class="{
                      'bg-warning bg-opacity-10 text-warning border border-warning':
                        booking.status === 'Pending',

                      'bg-success bg-opacity-10 text-success border border-success':
                        booking.status === 'Confirmed',

                      'bg-secondary bg-opacity-10 text-secondary border border-secondary':
                        booking.status === 'Completed'
                    }"
                  >
                    {{ booking.status }}
                  </span>

                </td>

                <!-- Action -->
                <td class="py-3 text-end">

                  <button
                    class="btn btn-success btn-sm"
                    @click="goToBookingDetails(booking.id)"
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
import { useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import api from '@/services/api/api'

const router = useRouter()

const totalSessions = ref(0)
const avgRating = ref(0)
const earnings = ref(0)
const upcomingBookings = ref([])




const goToBookingDetails = (id) => {
  router.push({
    name: 'booking-details',
    params: { id }
  })
}

const loadTutorDashboard = async () => {

  try {

    const response = await api.get('tutor-dashboard/')

    totalSessions.value = response.data.total_sessions
    avgRating.value = response.data.rating_average
<<<<<<< HEAD
    earnings.value = response.data.total_earnings

    // ✅ just assign what backend sends
    upcomingBookings.value = response.data.upcoming_bookings || []
=======
    upcomingBookings.value = response.data.upcoming_bookings
    earnings.value = response.data.total_earnings
>>>>>>> 32c6f3b (Before Merging to Another Branch)

  } catch (error) {

    console.error("Failed to load tutor dashboard:", error)

  }

}

onMounted(loadTutorDashboard)
</script>