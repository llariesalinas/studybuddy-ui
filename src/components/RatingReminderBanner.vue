<template>
  <div v-if="showBanner" class="alert rating-banner border-0 rounded-4 d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4">
    <div>
      <strong class="d-flex align-items-center gap-2">
        <i class="bi bi-exclamation-diamond-fill text-danger"></i>
        Session rating reminder
      </strong>
      <div class="small mt-1">
        You still have a completed session waiting for a rating. Ratings are optional, but we’ll keep reminding you until one is submitted.
      </div>
      <div v-if="latestUnratedSession" class="small text-muted mt-2">
        Latest: {{ latestUnratedSession.subject }} with {{ latestUnratedSession.tutor }} on {{ latestUnratedSession.date }}
      </div>
    </div>

    <button type="button" class="btn btn-dark rounded-3 sb-btn" @click="isModalOpen = true">
      Rate Latest Session
    </button>
  </div>

  <RatingStackModal
    :open="isModalOpen"
    :sessions="sessionsStore.unratedCompletedSessions"
    @close="isModalOpen = false"
    @rated="handleRated"
  />
</template>

<script setup>
import { computed, defineAsyncComponent, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useSessionsStore } from '@/stores/completedSessions'

const RatingStackModal = defineAsyncComponent(() => import('@/components/RatingStackModal.vue'))

const route = useRoute()
const authStore = useAuthStore()
const sessionsStore = useSessionsStore()
const isModalOpen = ref(false)

const showBanner = computed(() => {
  return authStore.userRole === 'tutee' && sessionsStore.hasUnratedCompletedSessions
})

const latestUnratedSession = computed(() => sessionsStore.unratedCompletedSessions[0] || null)

const handleRated = () => {
  if (!sessionsStore.unratedCompletedSessions.length) {
    isModalOpen.value = false
  }
}

onMounted(() => {
  if (authStore.userRole === 'tutee' && route.path !== '/dashboard') {
    sessionsStore.fetchSessions()
  }
})

watch(
  () => [route.path, showBanner.value],
  ([path, visible]) => {
    if (path === '/dashboard' && visible) {
      isModalOpen.value = true
      return
    }

    if (path !== '/dashboard') {
      isModalOpen.value = false
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.rating-banner {
  background: linear-gradient(135deg, #fff8f6 0%, #fff1ed 100%);
  color: #4a1d16;
}
</style>
