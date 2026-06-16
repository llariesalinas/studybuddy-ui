<template>
  <Teleport to="body">
    <div v-if="isOpen" class="sb-modal-backdrop" role="presentation" @click.self="close">
      <section
        class="sb-modal-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <div class="sb-modal-header">
          <h2 id="modal-title" class="sb-modal-title">Tutor Screening</h2>
          <button type="button" class="sb-modal-close-btn" aria-label="Close" @click="close">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        
        <p class="sb-modal-subtitle">Tutors are reviewed by our team before approval.</p>

        <div class="sb-modal-body">
          <div class="sb-auth-field">
            <label class="sb-auth-label">Most recent School ID (Image)</label>
            <input
              type="file"
              @change="handleFileChange($event, 'schoolId')"
              class="sb-auth-input"
              accept="image/*"
            />
          </div>

          <div class="sb-auth-field">
            <label class="sb-auth-label">Proof of Enrollment / COR (Image or PDF)</label>
            <input
              type="file"
              @change="handleFileChange($event, 'enrollmentProof')"
              class="sb-auth-input"
              accept="image/*,application/pdf"
            />
          </div>

          <div class="sb-auth-field">
            <label class="sb-auth-label">Why do you want to become a tutor? (Optional)</label>
            <textarea
              v-model="localReason"
              class="sb-auth-input sb-auth-textarea"
              placeholder="Tell us about your motivation..."
              rows="3"
            ></textarea>
          </div>
        </div>

        <div class="sb-modal-actions">
          <button type="button" class="sb-btn-pill sb-btn-outline" @click="close" :disabled="isSubmitting">Cancel</button>
          <button type="button" class="sb-btn-pill sb-btn-primary" @click="submit" :disabled="isSubmitting">
            <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
            {{ isSubmitting ? 'Submitting...' : 'Confirm & Submit' }}
          </button>
        </div>
      </section>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import { useRegistrationInfoStore } from '@/stores/registrationinfo'

defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close', 'submit'])
const store = useRegistrationInfoStore()
const isSubmitting = ref(false)

const localReason = ref(store.reasonToTutor)

const handleFileChange = (event, type) => {
  const file = event.target.files[0]
  if (type === 'schoolId') {
    store.schoolIdFile = file
  } else if (type === 'enrollmentProof') {
    store.enrollmentProofFile = file
  }
}

const close = () => {
  if (isSubmitting.value) return
  emit('close')
}

const submit = async () => {
  isSubmitting.value = true
  store.reasonToTutor = localReason.value
  await emit('submit')
  isSubmitting.value = false
}
</script>

<style scoped>

.sb-auth-field {
  display: grid;
  gap: 0.25rem;
}

.sb-auth-label {
  font-size: 0.8rem;
  font-weight: 750;
  color: var(--sb-text-main);
}

.sb-auth-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--sb-card-border);
  border-radius: 12px;
  background: color-mix(in srgb, var(--sb-card-bg) 82%, transparent);
  color: var(--sb-text-main);
  font: inherit;
}

.sb-auth-textarea {
  min-height: 100px;
  resize: vertical;
}

.sb-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1060;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.25rem;
  background: rgba(7, 19, 16, 0.48);
  backdrop-filter: blur(8px);
}

.sb-modal-dialog {
  display: grid;
  gap: 1rem;
  width: min(400px, 100%);
  border: 1px solid color-mix(in srgb, var(--sb-card-border) 78%, transparent);
  border-radius: 20px;
  background: color-mix(in srgb, var(--sb-card-bg) 94%, transparent);
  color: var(--sb-text-main);
  box-shadow: 0 30px 80px rgba(7, 19, 16, 0.28);
  padding: 1.5rem;
}

.sb-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.sb-modal-title {
  margin: 0;
  color: var(--sb-text-main);
  font-size: 1.1rem;
  font-weight: 850;
}

.sb-modal-close-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border: 0;
  border-radius: 999px;
  background: color-mix(in srgb, var(--sb-card-border) 44%, transparent);
  color: var(--sb-text-main);
  cursor: pointer;
}

.sb-modal-subtitle {
  margin: 0;
  font-size: 0.85rem;
  color: var(--sb-text-muted);
}

.sb-modal-body {
  display: grid;
  gap: 1rem;
}

.sb-modal-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
}

.sb-btn-pill {
  flex: 1;
  padding: 0.75rem;
  border-radius: 999px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.sb-btn-primary {
  background: var(--sb-primary);
  color: white;
}

.sb-btn-outline {
  background: transparent;
  border: 1px solid var(--sb-card-border);
  color: var(--sb-text-main);
}
</style>
