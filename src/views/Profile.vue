<template>
  <div class="profile-content">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">My Profile</h2>
      <p class="text-muted">Manage your personal information and tutoring preferences.</p>
    </div>

    <div class="card border-sb shadow-sm rounded-4" style="max-width: 800px;">
      <div v-if="userRole === 'tutee'" class="card-body p-4 p-md-5">
        
        <div class="d-flex align-items-center mb-4 pb-4 border-bottom border-sb">
          <div class="rounded-circle bg-success bg-opacity-10 text-sb-primary d-flex justify-content-center align-items-center fw-bold fs-3 me-4" style="width: 80px; height: 80px;">
            JD
          </div>
          <div>
            <h5 class="fw-bold mb-1">Juan Dela Cruz</h5>
            <p class="text-muted small mb-2">Student / Tutee</p>
            <button class="btn btn-outline-dark btn-sm rounded-3 fw-semibold px-3">Update Photo</button>
          </div>
        </div>

        <form @submit.prevent="saveProfile">
          <div class="row g-4 mb-4">
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">Full Name</label>
              <input type="text" class="form-control border-sb shadow-none" value="Juan Dela Cruz">
            </div>
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">University Email</label>
              <input type="email" class="form-control border-sb shadow-none bg-light text-muted" value="juan@university.edu" disabled>
              <div class="form-text small">Email cannot be changed after registration.</div>
            </div>
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">Major / Degree Program</label>
              <input type="text" class="form-control border-sb shadow-none" placeholder="e.g., Computer Science">
            </div>
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">Year Level</label>
              <select class="form-select border-sb shadow-none">
                <option value="1">1st Year</option>
                <option value="2">2nd Year</option>
                <option value="3">3rd Year</option>
                <option value="4">4th Year</option>
                <option value="5">Graduate</option>
              </select>
            </div>
            
            <div class="col-12">
              <label class="form-label fw-semibold small text-dark">Bio (About Me)</label>
              <textarea class="form-control border-sb shadow-none" rows="4" placeholder="Tell tutors a bit about your learning style or what you usually need help with..."></textarea>
            </div>
            
          </div>

          <div class="text-end mt-2">
            <button type="submit" class="btn bg-sb-primary text-white px-5 py-2 rounded-3 fw-semibold shadow-sm">
              Save Changes
            </button>
          </div>
        </form>

      </div>

      <div v-else  class="card-body p-4 p-md-5">
        
        <div class="d-flex align-items-center mb-4 pb-4 border-bottom border-sb">
          <div class="rounded-circle bg-success bg-opacity-10 text-sb-primary d-flex justify-content-center align-items-center fw-bold fs-3 me-4" style="width: 80px; height: 80px;">
            JD
          </div>
          <div>
            <h5 class="fw-bold mb-1">Juan Dela Cruz</h5>
            <p class="text-muted small mb-2">Student / Tutor</p>
            <button class="btn btn-outline-dark btn-sm rounded-3 fw-semibold px-3">Update Photo</button>
          </div>
        </div>

        <form @submit.prevent="saveProfile">
          <div class="row g-4 mb-4">
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">Full Name</label>
              <input type="text" class="form-control border-sb shadow-none" value="Juan Dela Cruz">
            </div>
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">University Email</label>
              <input type="email" class="form-control border-sb shadow-none bg-light text-muted" value="juan@university.edu" disabled>
              <div class="form-text small">Email cannot be changed after registration.</div>
            </div>
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">Major / Degree Program</label>
              <input type="text" class="form-control border-sb shadow-none" placeholder="e.g., Computer Science">
            </div>
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">Year Level</label>
              <select class="form-select border-sb shadow-none">
                <option value="1">1st Year</option>
                <option value="2">2nd Year</option>
                <option value="3">3rd Year</option>
                <option value="4">4th Year</option>
                <option value="5">Graduate</option>
              </select>
            </div>
            
            <div class="col-12 mt-3">

              <div class="d-flex justify-content-between align-items-center mb-3">
                <label class="form-label fw-semibold small text-dark mb-0">
                  Subjects Offered
                </label>
                <button type="button" class="btn btn-outline-dark btn-sm rounded-3 fw-semibold px-3">
                  Edit
                </button>
              </div>

              <div class="d-flex flex-wrap gap-2">
                <span class="badge bg-sb-primary text-white px-3 py-2 rounded-pill">
                  Mathematics
                </span>

                <span class="badge bg-sb-primary text-white px-3 py-2 rounded-pill">
                  Physics
                </span>

                <span class="badge bg-sb-primary text-white px-3 py-2 rounded-pill">
                  Programming
                </span>

                <span class="badge bg-sb-primary text-white px-3 py-2 rounded-pill">
                  Data Structures
                </span>
              </div>

            </div>

            <div class="col-12">
              <label class="form-label fw-semibold small text-dark">Bio (About Me)</label>
              <textarea class="form-control border-sb shadow-none" rows="4" placeholder="Tell tutors a bit about your learning style or what you usually need help with..."></textarea>
            </div>
            
          </div>

          <div class="text-end mt-2">
            <button type="submit" class="btn bg-sb-primary text-white px-5 py-2 rounded-3 fw-semibold shadow-sm">
              Save Changes
            </button>
          </div>
        </form>

      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore()

const userRole = computed(() => authStore.user?.role?.toLowerCase() || null)

const saveProfile = () => {
  // In a real application, this would trigger an API call to update the database
  alert('Profile updated successfully! (Placeholder logic)')
}
</script>

<style scoped>
.form-control:focus, .form-select:focus {
  border-color: var(--sb-primary);
  box-shadow: 0 0 0 0.25rem rgba(0, 137, 90, 0.25);
}
</style>