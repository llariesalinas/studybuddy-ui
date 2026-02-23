<template>
  <div class="p-4">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">Welcome back, Student!</h2>
      <p class="text-muted">Here's your tutoring overview for today.</p>
    </div>

    <div class="row g-4 mb-5">
      <div class="col-md-6">
        <div class="card border-sb shadow-sm rounded-4 h-100 p-3 d-flex flex-row align-items-center">
          <div class="bg-success bg-opacity-10 p-3 rounded-4 me-3">
            <i class="bi bi-calendar-event text-sb-primary fs-3"></i>
          </div>
          <div>
            <h6 class="text-muted small fw-bold mb-1">Upcoming Sessions</h6>
            <h2 class="fw-bold mb-0">2</h2>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card border-sb shadow-sm rounded-4 h-100 p-3 d-flex flex-row align-items-center">
          <div class="bg-success bg-opacity-10 p-3 rounded-4 me-3">
            <i class="bi bi-book text-sb-primary fs-3"></i>
          </div>
          <div>
            <h6 class="text-muted small fw-bold mb-1">Completed Sessions</h6>
            <h2 class="fw-bold mb-0">3</h2>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-md-6">
        <h5 class="fw-bold mb-3 d-flex align-items-center">
          <i class="bi bi-clock text-sb-primary me-2"></i> Upcoming Sessions
        </h5>

        <div @click="viewSessionDetails(1)" class="card border-sb shadow-sm rounded-4 mb-3 session-card">
          <div class="card-body d-flex justify-content-between align-items-center">
            <div>
              <h6 class="fw-bold text-dark mb-1">Calculus</h6>
              <p class="text-muted small mb-0">with Maria Santos</p>
            </div>
            <div class="text-end">
              <h6 class="fw-bold text-dark mb-1">2026-02-20</h6>
              <p class="text-muted small mb-0">10:00 AM</p>
            </div>
          </div>
        </div>

        <div @click="viewSessionDetails(2)" class="card border-sb shadow-sm rounded-4 mb-3 session-card">
          <div class="card-body d-flex justify-content-between align-items-center">
            <div>
              <h6 class="fw-bold text-dark mb-1">Data Structures</h6>
              <p class="text-muted small mb-0">with Carlos Tan</p>
            </div>
            <div class="text-end">
              <h6 class="fw-bold text-dark mb-1">2026-02-18</h6>
              <p class="text-muted small mb-0">2:00 PM</p>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-6">
        <h5 class="fw-bold mb-3 d-flex align-items-center">
          <i class="bi bi-star text-warning me-2"></i> Recent Sessions
        </h5>

        <div @click="viewSessionDetails(3)" class="card border-sb shadow-sm rounded-4 mb-3 session-card">
          <div class="card-body d-flex justify-content-between align-items-center">
            <div>
              <h6 class="fw-bold text-dark mb-1">Academic Writing</h6>
              <p class="text-muted small mb-0">Anna Cruz</p>
            </div>
            <div class="d-flex gap-2">
              <span class="badge bg-light text-dark border border-sb d-flex align-items-center">
                <i class="bi bi-star-fill text-dark me-1 small"></i> 5
              </span>
              <span class="badge bg-light text-dark border border-sb d-flex align-items-center">₱130</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()

const viewSessionDetails = (sessionId) => {
  // 1. We log the ID to satisfy ESLint and prep for backend integration
  console.log(`Navigating to details for session ID: ${sessionId}`)

  // 2. Route to the schedule page for now
  router.push('/schedule')
}
</script>

<style scoped>
/* Hover effect to make cards feel clickable */
.session-card {
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}
.session-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 15px rgba(0, 137, 90, 0.1) !important;
  border-color: var(--sb-primary) !important;
}
</style>
