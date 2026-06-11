<template>
  <Teleport to="body">
    <div v-if="open" class="session-check-shell" @click.self="emit('close')">
      <section
        class="session-check-card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="session-check-title"
      >
        <header class="session-check-header">
          <div>
            <span class="session-check-eyebrow">Mid-session check-in</span>
            <h5 id="session-check-title" class="session-check-title">Is your session going well?</h5>
          </div>
          <button
            type="button"
            class="session-check-close sb-btn"
            aria-label="Close modal"
            :disabled="submitting"
            @click="emit('close')"
          >
            <i class="bi bi-x-lg"></i>
          </button>
        </header>

        <div class="session-check-body">
          <p class="session-check-copy">
            A quick response helps us spot session issues while there is still time to help.
          </p>
        </div>

        <footer class="session-check-actions">
          <button
            type="button"
            class="btn btn-light sb-btn"
            :disabled="submitting"
            @click="emit('confirm', 'issues')"
          >
            Having issues
          </button>
          <button
            type="button"
            class="btn bg-sb-primary text-white sb-btn"
            :disabled="submitting"
            @click="emit('confirm', 'good')"
          >
            <span
              v-if="submitting"
              class="spinner-border spinner-border-sm me-2"
              role="status"
              aria-hidden="true"
            ></span>
            All good
          </button>
        </footer>
      </section>
    </div>
  </Teleport>
</template>

<script setup>
import { onUnmounted, watch } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  submitting: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'confirm'])

watch(
  () => props.open,
  (isOpen) => {
    document.body.style.overflow = isOpen ? 'hidden' : ''
  },
  { immediate: true },
)

onUnmounted(() => {
  document.body.style.overflow = ''
})
</script>

<style scoped>
.session-check-shell {
  position: fixed;
  inset: 0;
  z-index: 1200;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgba(15, 23, 42, 0.45);
}

.session-check-card {
  width: min(100%, 460px);
  padding: 28px;
  background: #fff;
  border: 1px solid rgba(241, 245, 249, 0.9);
  border-radius: 20px;
  box-shadow: 0 24px 64px rgba(15, 23, 42, 0.16);
}

.session-check-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f1f5f9;
}

.session-check-eyebrow {
  display: block;
  margin-bottom: 4px;
  color: var(--sb-primary);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}

.session-check-title {
  margin: 0;
  color: #0f172a;
  font-size: 18px;
  font-weight: 700;
}

.session-check-close {
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  border: 0;
  border-radius: 50%;
  background: #f1f5f9;
  color: #64748b;
}

.session-check-body {
  padding: 20px 0;
}

.session-check-copy {
  margin: 0;
  color: #1f2937;
  font-size: 15px;
  line-height: 1.6;
}

.session-check-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
}

@media (max-width: 575px) {
  .session-check-actions {
    flex-direction: column-reverse;
  }

  .session-check-actions .btn {
    width: 100%;
  }
}
</style>
