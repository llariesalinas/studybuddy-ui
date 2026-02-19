<template>
  <div class="initial-booking-content">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">Book a Session</h2>
      <p class="text-muted">Tell us what you need help with, and we'll match you with the right tutor.</p>
    </div>

    <div class="card border-sb shadow-sm rounded-4" style="max-width: 600px;">
      <div class="card-body p-4 p-md-5">
        <form @submit.prevent="findTutor">
          
          <div class="mb-3">
            <label class="form-label fw-semibold small">Subject</label>
            <select class="form-select border-sb shadow-none" required>
              <option value="" disabled selected>e.g., Mathematics, Sciences</option>
              <option value="math">Mathematics</option>
              <option value="science">Sciences</option>
            </select>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold small">Specific Topic</label>
            <input type="text" class="form-control border-sb shadow-none" placeholder="e.g., Calculus, Thermodynamics" required>
          </div>

          <div class="row g-3 mb-3">
            <div class="col-md-6">
              <label class="form-label fw-semibold small">Date</label>
              <input type="date" class="form-control border-sb shadow-none" required>
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold small">Preferred Mode</label>
              <select class="form-select border-sb shadow-none" required>
                <option value="online">Online (Zoom/Meets)</option>
                <option value="f2f">Face-to-Face (Campus Library)</option>
              </select>
            </div>
          </div>

          <div class="row g-3 mb-4">
            <div class="col-6">
              <label class="form-label fw-semibold small">Time From</label>
              <input type="time" class="form-control border-sb shadow-none" required>
            </div>
            <div class="col-6">
              <label class="form-label fw-semibold small">Time To</label>
              <input type="time" class="form-control border-sb shadow-none" required>
            </div>
          </div>

          <div class="text-end mt-4">
            <button type="submit" class="btn bg-sb-primary text-white px-5 py-2 rounded-3 fw-semibold shadow-sm">
              Find Tutor
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const findTutor = () => {
  // In a real app, you would pass the form data to the matching algorithm here.
  // For now, we push the user to the Find Tutors page.
  router.push('/tutors')
}
</script>