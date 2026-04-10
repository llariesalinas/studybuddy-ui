<template>
  <div v-if="showBanner" class="alert alert-warning border-0 rounded-4 d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4">
    <div>
      <strong>Session rating reminder.</strong>
      <div class="small">
        You still have a completed session waiting for a rating. Ratings are optional, but we’ll keep reminding you until one is submitted.
      </div>
    </div>

    <router-link to="/tuteeSessions" class="btn btn-dark rounded-3">
      Review Sessions
    </router-link>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useSessionsStore } from '@/stores/completedSessions'

const authStore = useAuthStore()
const sessionsStore = useSessionsStore()

const showBanner = computed(() => {
  return authStore.userRole === 'tutee' && sessionsStore.hasUnratedCompletedSessions
})

onMounted(() => {
  if (authStore.userRole === 'tutee') {
    sessionsStore.fetchSessions()
  }
})
</script>
