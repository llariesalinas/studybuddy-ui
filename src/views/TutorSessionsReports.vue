<template>
  <div class="reports-content">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">Sessions & Reports</h2>
      <p class="text-muted">Track your tutoring history, earnings, and performance.</p>
    </div>

    <div class="row g-4 mb-5">
      <div class="col-md-3">
        <div class="card border-sb shadow-sm h-100 rounded-4">
          <div class="card-body d-flex flex-column justify-content-center text-center py-4">
            <div class="d-flex align-items-center justify-content-center mb-2 gap-2">
              <div class="rounded-circle bg-success bg-opacity-10 text-sb-primary d-flex justify-content-center align-items-center stat-icon">
                <i class="bi bi-calendar-event"></i>
              </div>
              <span class="text-muted small fw-semibold">Total Sessions</span>
            </div>
            <h3 class="fw-bold mb-0">{{ totalSessions }}</h3>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-sb shadow-sm h-100 rounded-4">
          <div class="card-body d-flex flex-column justify-content-center text-center py-4">
            <div class="d-flex align-items-center justify-content-center mb-2 gap-2">
              <div class="rounded-circle bg-success bg-opacity-10 text-sb-primary d-flex justify-content-center align-items-center stat-icon">
                <i class="bi bi-currency-dollar"></i>
              </div>
              <span class="text-muted small fw-semibold">Total Earnings</span>
            </div>
            <h3 class="fw-bold mb-0">{{ totalEarnings }}</h3>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-sb shadow-sm h-100 rounded-4">
          <div class="card-body d-flex flex-column justify-content-center text-center py-4">
            <div class="d-flex align-items-center justify-content-center mb-2 gap-2">
              <div class="rounded-circle bg-warning bg-opacity-10 text-warning d-flex justify-content-center align-items-center stat-icon">
                <i class="bi bi-star"></i>
              </div>
              <span class="text-muted small fw-semibold">Avg Rating</span>
            </div>
            <h3 class="fw-bold mb-0">{{ averageRating }}</h3>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-sb shadow-sm h-100 rounded-4">
          <div class="card-body d-flex flex-column justify-content-center text-center py-4">
            <div class="d-flex align-items-center justify-content-center mb-2 gap-2">
              <div class="rounded-circle bg-info bg-opacity-10 text-info d-flex justify-content-center align-items-center stat-icon">
                <i class="bi bi-graph-up-arrow"></i>
              </div>
              <span class="text-muted small fw-semibold">Hours Tutored</span>
            </div>
            <h3 class="fw-bold mb-0">{{ totalHours.toFixed(1) }}h</h3>
          </div>
        </div>
      </div>
    </div>

    <div class="card border-sb border-1 shadow-sm rounded-4">
      <div class="card-body p-4 p-md-5">
        <h4 class="fw-bold mb-4 d-flex align-items-center">
          <i class="bi bi-file-earmark-text text-sb-primary me-3"></i> Session History
        </h4>

        <div class="d-flex gap-2 mb-4 bg-light p-2 rounded-3 d-inline-flex border border-sb">
          <button
            v-for="filter in filters"
            :key="filter.value"
            @click="currentFilter = filter.value"
            class="btn rounded-pill px-3 py-1 fw-semibold text-muted shadow-none transition-all"
            :class="currentFilter === filter.value ? 'bg-white text-dark shadow-sm' : 'btn-light'"
          >
            {{ filter.label }}
          </button>
        </div>

        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead>
              <tr class="text-muted small align-bottom reports-header-row">
                <th class="fw-semibold pb-3">Subject</th>
                <th class="fw-semibold pb-3">Tutor</th>
                <th class="fw-semibold pb-3">Date</th>
                <th class="fw-semibold pb-3">Duration</th>
                <th class="fw-semibold pb-3">Status</th>
                <th class="fw-semibold pb-3">Rating</th>
                <th class="fw-semibold pb-3">Earnings</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="sessionStore.loading">
                <td colspan="8" class="text-center py-5 text-muted">Loading sessions...</td>
              </tr>

              <tr v-else-if="sessionStore.error">
                <td colspan="8" class="text-center py-5 text-danger">{{ sessionStore.error }}</td>
              </tr>

              <template v-else-if="filteredSessions.length">
                <tr
                  v-for="session in filteredSessions"
                  :key="session.id"
                  class="session-row"
                >
                  <td class="py-3 fw-bold">{{ session.subject }}</td>
                  <td class="py-3">{{ session.tutor }}</td>
                  <td class="py-3">{{ session.date }}</td>
                  <td class="py-3">{{ session.startTime }} - {{ session.endTime }}</td>
                  <td class="py-3">
                    <span class="badge rounded-pill px-3 py-1 fw-normal" :class="getStatusClass(session.status)">
                      {{ formatStatus(session.status) }}
                    </span>
                  </td>
                  <td class="py-3">
                    <span v-if="session.rating" class="d-flex align-items-center text-warning fw-bold small">
                      <i class="bi bi-star-fill me-1"></i> {{ session.rating }}
                    </span>
                    <span v-else class="text-muted">-</span>
                  </td>
                  <td class="py-3 fw-bold">
                    {{ session.earnings ? `PHP ${session.earnings}` : '-' }}
                  </td>
                  <td class="py-3 text-end action-cell">
                    <button
                      class="btn btn-sm bg-sb-primary text-white"
                      @click="goToDetails(session.id)"
                    >
                      View Details
                    </button>
                  </td>
                </tr>
              </template>

              <tr v-else>
                <td colspan="8" class="text-center py-5 text-muted">
                  No sessions found for this category.
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
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionsStore } from '@/stores/completedSessions'

const router = useRouter()
const sessionStore = useSessionsStore()
const currentFilter = ref('all')

const filters = computed(() => [
  {
    label: `All (${sessionStore.sessions.length})`,
    value: 'all',
  },
  {
    label: `Completed (${sessionStore.completedSessions.length})`,
    value: 'completed',
  },
  {
    label: `Upcoming (${sessionStore.upcomingSessions.length})`,
    value: 'upcoming',
  },
  {
    label: `Rejected (${sessionStore.rejectedSessions.length})`,
    value: 'rejected',
  },
])

onMounted(() => {
  sessionStore.fetchSessions()
})

const goToDetails = (sessionId) => {
  router.push(`/booking-details/${sessionId}`)
}

const totalSessions = computed(() => sessionStore.sessions.length)

const totalEarnings = computed(() =>
  sessionStore.completedSessions.reduce((sum, session) => sum + Number(session.earnings || 0), 0)
)

const averageRating = computed(() => {
  const ratedSessions = sessionStore.completedSessions.filter((session) => session.rating)

  if (!ratedSessions.length) {
    return 0
  }

  return (
    ratedSessions.reduce((sum, session) => sum + Number(session.rating), 0) /
    ratedSessions.length
  ).toFixed(1)
})

const totalHours = computed(() =>
  sessionStore.completedSessions.reduce((sum, session) => {
    const start = new Date(`1970-01-01T${session.startTime}`)
    const end = new Date(`1970-01-01T${session.endTime}`)
    return sum + ((end - start) / (1000 * 60 * 60))
  }, 0)
)

const filteredSessions = computed(() => {
  switch (currentFilter.value) {
    case 'completed':
      return sessionStore.completedSessions
    case 'upcoming':
      return sessionStore.upcomingSessions
    case 'rejected':
      return sessionStore.rejectedSessions
    default:
      return sessionStore.sessions
  }
})

const formatStatus = (status) => {
  const normalized = String(status || '').toLowerCase()

  if (normalized === 'awaiting payment verification') {
    return 'Awaiting Verification'
  }

  return status
}

const getStatusClass = (status) => {
  switch (String(status || '').toLowerCase()) {
    case 'confirmed':
    case 'awaiting payment verification':
      return 'bg-warning bg-opacity-25 text-dark'
    case 'completed':
      return 'bg-sb-primary text-white'
    case 'rejected':
    case 'cancelled':
      return 'bg-danger text-white'
    case 'pending':
      return 'bg-secondary text-white'
    default:
      return 'bg-secondary text-white'
  }
}
</script>

<style scoped>
.transition-all {
  transition: all 0.2s ease-in-out;
}

.stat-icon {
  width: 32px;
  height: 32px;
}

.table > :not(caption) > * > * {
  border-bottom-width: 0;
}

.reports-header-row {
  border-bottom: 2px solid var(--sb-card-border);
}

.session-row {
  position: relative;
  border-bottom: 1px solid var(--sb-card-border);
}
</style>
