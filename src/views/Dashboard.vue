<template>
  <div class="p-4">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">Welcome back, {{ studentName }}!</h2>
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
            <h2 class="fw-bold mb-0">{{ upcomingCount }}</h2>
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
            <h2 class="fw-bold mb-0">{{ completedCount }}</h2>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-md-6">
        <h5 class="fw-bold mb-3 d-flex align-items-center">
          <i class="bi bi-clock text-sb-primary me-2"></i> Upcoming Sessions
        </h5>

        <div v-if="loading" class="text-muted">Loading upcoming sessions...</div>

        <div v-else>
          <div 
          v-for="session in upcomingSessions"
          :key="session.id"
          @click="viewSessionDetails(session.id)" 
          class="card border-sb shadow-sm rounded-4 mb-3 session-card">
            <div class="card-body d-flex justify-content-between align-items-center">
              <div>
                <h6 class="fw-bold text-dark mb-1">{{ session.subject }}</h6>
                <p class="text-muted small mb-0">with {{ session.tutor }}</p>
              </div>
              <div class="text-end">
                <h6 class="fw-bold text-dark mb-1">{{ session.date }}</h6>
                <p class="text-muted small mb-0">{{session.time}}</p>
              </div>
            </div>
          </div>
        </div>
        

      </div>

      <div class="col-md-6">
        <h5 class="fw-bold mb-3 d-flex align-items-center">
          <i class="bi bi-star text-warning me-2"></i> Recent Sessions
        </h5>

        <div v-if="loading" class="text-muted">Loading completed sessions...</div>

        <div v-else>
          <div 
          v-for="session in completedSessions"
          :key="session.id"
          @click="viewSessionDetails(session.id)" 
          class="card border-sb shadow-sm rounded-4 mb-3 session-card">
            <div class="card-body d-flex justify-content-between align-items-center">
              <div>
                <h6 class="fw-bold text-dark mb-1">{{ session.subject }}</h6>
                <p class="text-muted small mb-0">{{ session.tutor }}</p>
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

    <div class="mt-3">
      <h4 class="fw-bold"
      >Try out these tutors</h4>

      <div class="row g-3">
        <template v-if="loading">
          <div class="col-12 text-muted">
            Loading tutors...
          </div>
        </template>

        <template v-else>
          <div 
            v-for="tutor in recommendedTutors"
            :key="tutor.id"
            class="col-md-4"
          >
            <div 
              class="card border-sb shadow-sm h-100 p-3 tutor-card"
              @click="bookTutor(tutor.id)"
            >
              <div class="card-body">
                <h3>{{ tutor.name }}</h3>
                <p class="text-muted small mb-2">⭐ {{ tutor.rating }}</p>
                <p class="small mb-2">
                  Subjects: {{ tutor.subjects?.join(', ') }}
                </p>
                <p class="fw-bold text-sb-primary mb-0">
                  ₱{{ tutor.hourlyRate }}/hr
                </p>
              </div>
            </div>
          </div>
        </template>
      </div>

    </div>
  </div>
</template>

<script setup>
import {ref, computed, onMounted} from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api/api' 
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const recommendedTutors = ref([])
const upcomingSessions = ref([])
const completedSessions = ref([])
const loading = ref(false)

const bookTutor = (tutorId) => {
  router.push(`/tutor/${tutorId}`)
}

const fetchSessions = async() => {
  try{
    loading.value = true
   const response = await api.get('dashboard/')

    recommendedTutors.value = response.data.recommendations
    upcomingSessions.value = response.data.upcoming
    completedSessions.value = response.data.completed
  }
  catch(error) {
    console.error('Error loading sessions:', error)
  }
  finally{
    loading.value = false
  }
}

onMounted(() => {
  fetchSessions()
})

const upcomingCount = computed(() => upcomingSessions.value.length)
const completedCount = computed(() => completedSessions.value.length)

const authStore = useAuthStore()

const studentName = computed(() => {
  return authStore.user
    ? authStore.user.fname
    : 'Student'
})

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
