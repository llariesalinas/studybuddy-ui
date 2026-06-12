<script setup>
import { onMounted, ref, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import AuthShell from '@/components/AuthShell.vue'

const route = useRoute()
const email = ref(route.query.email || 'your registered email')
const isLoaded = ref(false)

onMounted(async () => {
  await nextTick()
  isLoaded.value = true
  console.log('TutorApplicationSubmitted component mounted and rendered.')
})
</script>

<template>
  <AuthShell v-if="isLoaded">
    <template #icon>
      <div class="sb-success-badge">
        <i class="bi bi-check2-circle"></i>
      </div>
    </template>
    <template #title>Application Submitted</template>
    <template #subtitle>We've received your tutor application!</template>

    <div class="sb-success-content">
      <p class="sb-success-text">
        Your application is now being reviewed by our team. We will notify you of the result via email at:
        <strong class="sb-email-highlight">{{ email }}</strong>
      </p>

      <div class="sb-info-card">
        <div class="sb-info-row">
          <i class="bi bi-clock"></i>
          <span>Estimated review time: <strong>1–3 business days</strong></span>
        </div>
        <div class="sb-info-row">
          <i class="bi bi-envelope"></i>
          <span>Questions? Email: <a href="mailto:StudyBuddySupport@gmail.com">StudyBuddySupport@gmail.com</a></span>
        </div>
      </div>

      <div class="sb-action-group">
        <router-link to="/" class="sb-btn-pill">
          Back to Home
        </router-link>
      </div>
    </div>
  </AuthShell>
</template>

<style scoped>
.sb-success-badge {
  color: var(--sb-primary);
  font-size: 3rem;
  line-height: 1;
  margin-bottom: 0.5rem;
}

.sb-success-content {
  text-align: center;
}

.sb-success-text {
  color: var(--sb-text-main);
  font-size: 15px;
  line-height: 1.6;
  margin-bottom: 24px;
}

.sb-email-highlight {
  color: var(--sb-primary);
}

.sb-info-card {
  background: var(--sb-surface-variant, #f8f9fa);
  border: 1px solid var(--sb-card-border);
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 32px;
  text-align: left;
}

.sb-info-row {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13.5px;
  color: var(--sb-text-muted);
}

.sb-info-row:not(:last-child) {
  margin-bottom: 12px;
}

.sb-info-row i {
  color: var(--sb-primary);
  font-size: 16px;
}

.sb-info-row a {
  color: var(--sb-primary);
  text-decoration: none;
  font-weight: 500;
}

.sb-action-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sb-btn-pill {
  width: 100%;
  display: inline-flex;
  justify-content: center;
  align-items: center;
  padding: 12px 24px;
  border-radius: 999px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
  background: var(--sb-primary);
  color: white;
  border: none;
}

.sb-btn-pill:hover {
  background: var(--sb-primary-hover);
  transform: translateY(-1px);
}

.sb-btn-outline {
  background: transparent;
  color: var(--sb-primary);
  border: 2px solid var(--sb-primary);
}

.sb-btn-outline:hover {
  background: var(--sb-primary-subtle, rgba(0, 137, 90, 0.05));
  color: var(--sb-primary-hover);
}
</style>
