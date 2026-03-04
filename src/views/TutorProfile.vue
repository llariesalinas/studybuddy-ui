<template>
  <div class="profile-content">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">My Profile</h2>
      <p class="text-muted">Manage your personal information and tutoring preferences.</p>
    </div>

    <div class="card border-sb shadow-sm rounded-4" style="max-width: 800px;">
      <div  class="card-body p-4 p-md-5">
        
        <div class="d-flex align-items-center mb-4 pb-4 border-bottom border-sb">
          <div class="rounded-circle bg-success bg-opacity-10 text-sb-primary d-flex justify-content-center align-items-center fw-bold fs-3 me-4" style="width: 80px; height: 80px;">
            JD
          </div>
          <div>
            <h5 class="fw-bold mb-1">{{ tutorProfile.fullName }}</h5>
            <p class="text-muted small mb-2">Student / Tutor</p>
            <button class="btn btn-outline-dark btn-sm rounded-3 fw-semibold px-3">Update Photo</button>
          </div>
        </div>

        <form @submit.prevent="saveProfile">
          <div class="row g-4 mb-4">
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">Full Name</label>
              <input type="text" v-model="tutorProfile.fullName" class="form-control border-sb shadow-none">
            </div>
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">University Email</label>
              <input type="email" class="form-control border-sb shadow-none bg-light text-muted" value="juan@university.edu" disabled>
              <div class="form-text small">Email cannot be changed after registration.</div>
            </div>
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">Major / Degree Program</label>
              <input type="text" v-model="tutorProfile.major" class="form-control border-sb shadow-none" placeholder="e.g., Computer Science">
            </div>
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">Year Level</label>
              <select v-model="tutorProfile.yearLevel" class="form-select border-sb shadow-none">
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
                <span 
                v-for="subject in tutorProfile.subjects"
                :key="subject"
                class="badge bg-sb-primary text-white px-3 py-2 rounded-pill">
                  {{ subject }}
                </span>
              </div>

            </div>

            <div class="col-12">
              <label class="form-label fw-semibold small text-dark">Bio (About Me)</label>
              <textarea v-model="tutorProfile.bio" class="form-control border-sb shadow-none" rows="4" placeholder="Tell tutors a bit about your learning style or what you usually need help with..."></textarea>
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
import {ref, onMounted} from 'vue'
import api from '@/services/api/api'

const tutorProfile = ref({
    fullName: '',
    major: '',
    yearLevel: '',
    subjects: []
})

const fetchUserProfile = async () => {
  try {
    const response = await api.get('/userProfile')

    const data = response.data

    tutorProfile.value = {
      fullName: data.fullName,
      major: data.major || '',
      yearLevel: data.yearLevel || '',
      subjects: data.subjects || [], 
      bio: data.bio || ''
    }

  } catch (error) {
    console.error('Failed to fetch profile', error)
  }
}

onMounted(fetchUserProfile)

const saveProfile = async () => {
  try {
    await api.patch('/userProfile', tutorProfile.value)

    console.log('Profile updated successfully')
  } catch (error) {
    console.error('Failed to update profile', error)
  }
}
</script>

<style scoped>
.form-control:focus, .form-select:focus {
  border-color: var(--sb-primary);
  box-shadow: 0 0 0 0.25rem rgba(0, 137, 90, 0.25);
}
</style>