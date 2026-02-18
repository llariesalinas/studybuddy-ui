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
              <div class="rounded-circle bg-success bg-opacity-10 text-sb-primary d-flex justify-content-center align-items-center" style="width: 32px; height: 32px;">
                <i class="bi bi-calendar-event"></i>
              </div>
              <span class="text-muted small fw-semibold">Total Sessions</span>
            </div>
            <h3 class="fw-bold mb-0">3</h3>
          </div>
        </div>
      </div>
      
      <div class="col-md-3">
        <div class="card border-sb shadow-sm h-100 rounded-4">
          <div class="card-body d-flex flex-column justify-content-center text-center py-4">
            <div class="d-flex align-items-center justify-content-center mb-2 gap-2">
               <div class="rounded-circle bg-success bg-opacity-10 text-sb-primary d-flex justify-content-center align-items-center" style="width: 32px; height: 32px;">
                <i class="bi bi-currency-dollar"></i>
              </div>
              <span class="text-muted small fw-semibold">Total Earnings</span>
            </div>
            <h3 class="fw-bold mb-0">₱495</h3>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-sb shadow-sm h-100 rounded-4">
          <div class="card-body d-flex flex-column justify-content-center text-center py-4">
             <div class="d-flex align-items-center justify-content-center mb-2 gap-2">
               <div class="rounded-circle bg-warning bg-opacity-10 text-warning d-flex justify-content-center align-items-center" style="width: 32px; height: 32px;">
                <i class="bi bi-star"></i>
              </div>
              <span class="text-muted small fw-semibold">Avg Rating</span>
            </div>
            <h3 class="fw-bold mb-0">4.7</h3>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-sb shadow-sm h-100 rounded-4">
          <div class="card-body d-flex flex-column justify-content-center text-center py-4">
            <div class="d-flex align-items-center justify-content-center mb-2 gap-2">
               <div class="rounded-circle bg-info bg-opacity-10 text-info d-flex justify-content-center align-items-center" style="width: 32px; height: 32px;">
                <i class="bi bi-graph-up-arrow"></i>
              </div>
              <span class="text-muted small fw-semibold">Hours Tutored</span>
            </div>
            <h3 class="fw-bold mb-0">3.5h</h3>
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
              <tr class="text-muted small align-bottom" style="border-bottom: 2px solid var(--sb-card-border);">
                <th class="fw-semibold pb-3">Subject</th>
                <th class="fw-semibold pb-3">Tutor</th>
                <th class="fw-semibold pb-3">Date</th>
                <th class="fw-semibold pb-3">Duration</th>
                <th class="fw-semibold pb-3">Status</th>
                <th class="fw-semibold pb-3">Rating</th>
                <th class="fw-semibold pb-3">Earnings</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="session in filteredSessions" :key="session.id" style="border-bottom: 1px solid var(--sb-card-border);">
                <td class="py-3 fw-bold">{{ session.subject }}</td>
                <td class="py-3">{{ session.tutor }}</td>
                <td class="py-3">{{ session.date }}</td>
                <td class="py-3">{{ session.duration }} min</td>
                <td class="py-3">
                  <span class="badge rounded-pill px-3 py-1 fw-normal" :class="getStatusClass(session.status)">
                    {{ session.status }}
                  </span>
                </td>
                <td class="py-3">
                  <span v-if="session.rating" class="d-flex align-items-center text-warning fw-bold small">
                    <i class="bi bi-star-fill me-1"></i> {{ session.rating }}
                  </span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td class="py-3 fw-bold">
                  {{ session.earnings ? '₱' + session.earnings : '—' }}
                </td>
              </tr>
              
              <tr v-if="filteredSessions.length === 0">
                <td colspan="7" class="text-center py-5 text-muted">
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
import { ref, computed } from 'vue'

// 1. Define the possible filters matching your design
const filters = [
  { label: 'All (6)', value: 'All' },
  { label: 'Completed (3)', value: 'completed' },
  { label: 'Upcoming (2)', value: 'upcoming' },
  { label: 'Cancelled (1)', value: 'cancelled' }
]

const currentFilter = ref('All')

// 2. Data-driven Array: This is exactly how your DB will return data
const sessions = ref([
  { id: 1, subject: 'Calculus', tutor: 'Maria Santos', date: '2026-02-20', duration: 60, status: 'upcoming', rating: null, earnings: null },
  { id: 2, subject: 'Data Structures', tutor: 'Carlos Tan', date: '2026-02-18', duration: 90, status: 'upcoming', rating: null, earnings: null },
  { id: 3, subject: 'Academic Writing', tutor: 'Anna Cruz', date: '2026-02-15', duration: 60, status: 'completed', rating: 5, earnings: 130 },
  { id: 4, subject: 'Physics', tutor: 'James Reyes', date: '2026-02-12', duration: 60, status: 'completed', rating: 4, earnings: 140 },
  { id: 5, subject: 'Statistics', tutor: 'Maria Santos', date: '2026-02-10', duration: 90, status: 'completed', rating: 5, earnings: 225 },
  { id: 6, subject: 'Biology', tutor: 'Sofia Garcia', date: '2026-02-08', duration: 60, status: 'cancelled', rating: null, earnings: null },
])

// 3. Computed Property for filtering: This handles the logic instantly on the frontend
const filteredSessions = computed(() => {
  if (currentFilter.value === 'All') {
    return sessions.value
  }
  return sessions.value.filter(session => session.status === currentFilter.value)
})

// 4. Utility function to handle the dynamic CSS classes for the badges
const getStatusClass = (status) => {
  switch (status) {
    case 'upcoming':
      return 'bg-warning bg-opacity-25 text-dark' // Soft orange
    case 'completed':
      return 'bg-sb-primary text-white' // Solid Green
    case 'cancelled':
      return 'bg-danger text-white' // Solid Red
    default:
      return 'bg-secondary text-white'
  }
}
</script>

<style scoped>
/* Smooth transition for the filter pill buttons */
.transition-all {
  transition: all 0.2s ease-in-out;
}

/* Ensure the table looks completely clean, removing default Bootstrap borders on the sides */
.table > :not(caption) > * > * {
  border-bottom-width: 0px;
}
</style>