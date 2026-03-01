<template>
  <div class="p-1">

    <div class="d-flex mb-4 justify-content-between align-items-center">
        <div>
        <h2 class="fw-bold mb-1">Completed Sessions</h2>
        <p class="text-muted mb-0">
            Review your past tutoring sessions.
        </p>
        </div>

        <div style="width: 300px;">
            <input
                type="text"
                v-model="searchQuery"
                class="form-control"
                placeholder="Search by tutee or subject..."
            /> 
        </div>
    </div>


    <div v-if="filteredSessions.length === 0" class="text-center text-muted py-5">
        No completed sessions found.
    </div>
    
    <div v-else>
    
        <router-link
        v-for="session in filteredSessions"
        :key="session.id"
        :to="`/bookingDetails/${session.id}`"
        class="text-decoration-none text-dark"
        >
        <div class="card border mb-3 rounded-4 shadow-sm session-card">
            <div class="card-body d-flex justify-content-between align-items-center">
            <div>
                <h5 class="fw-semibold mb-1">{{ session.tuteeName}}</h5>
                <p class="mb-1 text-muted">
                Subject: {{ session.subject }}
                </p>
                <small class="text-muted">
                {{ session.date }} • {{ session.start_time }} - {{ session.end_time }}
                </small>
            </div>

            <div class="text-end">
                <span class="badge bg-success-subtle text-success">
                Completed
                </span>
                <div class="mt-2 fw-semibold">
                ₱{{ session.amount }}
                </div>
            </div>
            </div>
        </div>
        </router-link>
        
    </div>

      

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSessionsStore } from '@/stores/completedSessions'

const completedSessionsStore = useSessionsStore()

const searchQuery = ref('')


onMounted(() => {
  if(completedSessionsStore.sessions.length === 0){
    completedSessionsStore.fetchSessions()
  }
})

const filteredSessions = computed(() => {
  const sessions = completedSessionsStore.completedSessions

  if (!searchQuery.value) return sessions

  return sessions.filter(session =>
    session.student_name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    session.subject.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})
</script>

<style scoped>
.session-card {
  cursor: pointer;
  transition: all 0.2s ease;
}

.session-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(0,0,0,0.08);
}
</style>