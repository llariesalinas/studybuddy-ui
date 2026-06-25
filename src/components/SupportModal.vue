<template>
  <Teleport to="body">
    <div v-if="open" class="support-modal-shell" @click.self="emit('close')">
      <div
        class="support-modal-card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="support-modal-title"
      >
        <div class="support-modal-header">
          <div>
            <span class="support-modal-eyebrow">Help & Support</span>
            <h5 id="support-modal-title" class="support-modal-title">Submit Support Ticket</h5>
          </div>
          <button
            type="button"
            class="support-modal-close sb-btn"
            aria-label="Close modal"
            @click="emit('close')"
          >
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <form @submit.prevent="handleSubmit" class="support-modal-form">
          <div v-if="contextId" class="context-alert">
            <i class="bi bi-link-45deg fs-5"></i>
            <div>
              <strong>Linked {{ contextType }}:</strong>
              <span class="small font-monospace ms-1">#{{ contextId }}</span>
            </div>
          </div>

          <div class="form-group mb-3">
            <label for="support-category" class="form-label">Category</label>
            <select
              id="support-category"
              v-model="form.category"
              class="form-select support-select sb-field"
              required
            >
              <option value="" disabled>Select a category</option>
              <option v-for="opt in categoryOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>

          <div class="form-group mb-3">
            <label for="support-subject" class="form-label">Subject</label>
            <input
              id="support-subject"
              v-model.trim="form.subject"
              type="text"
              class="form-control support-input sb-field"
              placeholder="Brief summary of the issue"
              maxlength="150"
              required
            />
          </div>

          <div class="form-group mb-4">
            <label for="support-description" class="form-label">Description</label>
            <textarea
              id="support-description"
              v-model.trim="form.description"
              class="form-control support-textarea sb-field"
              rows="4"
              placeholder="Please provide all relevant details here..."
              required
            ></textarea>
          </div>

          <div class="support-modal-footer">
            <button
              type="button"
              class="btn btn-light sb-btn px-4"
              :disabled="isSubmitting"
              @click="emit('close')"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="btn bg-sb-primary text-white sb-btn px-4"
              :disabled="isSubmitting || !isFormValid"
            >
              <span
                v-if="isSubmitting"
                class="spinner-border spinner-border-sm me-2"
                role="status"
                aria-hidden="true"
              ></span>
              {{ isSubmitting ? 'Submitting...' : 'Submit Ticket' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, reactive, ref, watch, onUnmounted } from 'vue'
import api from '@/services/api/api'
import { useToastStore } from '@/stores/toast'

const props = defineProps({
  open: { type: Boolean, default: false },
  contextType: { type: String, default: null }, // 'Booking' or 'Transaction'
  contextId: { type: [String, Number], default: null }
})

const emit = defineEmits(['close', 'submitted'])
const toastStore = useToastStore()

const isSubmitting = ref(false)
const form = reactive({
  category: '',
  subject: '',
  description: ''
})

const categoryOptions = [
  { value: 'Payment', label: 'Payment Issue' },
  { value: 'Booking', label: 'Booking/No-show' },
  { value: 'Technical', label: 'Technical Problem' },
  { value: 'Dispute', label: 'Tutor/Tutee Dispute' },
  { value: 'Other', label: 'Other' }
]

const isFormValid = computed(() => {
  return form.category && form.subject.trim() && form.description.trim()
})

const resetForm = () => {
  form.category = ''
  form.subject = ''
  form.description = ''
}

const handleSubmit = async () => {
  if (!isFormValid.value || isSubmitting.value) return
  isSubmitting.value = true

  const payload = {
    category: form.category,
    subject: form.subject,
    description: form.description
  }

  if (props.contextType === 'Booking' && props.contextId) {
    payload.booking_id = props.contextId
  } else if (props.contextType === 'Transaction' && props.contextId) {
    payload.transaction_id = props.contextId
  }

  try {
    const response = await api.post('support/tickets/create/', payload)
    toastStore.push('Support ticket created successfully.')
    emit('submitted', response.data)
    resetForm()
    emit('close')
  } catch (error) {
    console.error('Failed to submit support ticket:', error)
    toastStore.push(error.response?.data?.error || 'Failed to submit support ticket. Please try again.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
      resetForm()
      // Pre-fill subject if context exists
      if (props.contextId) {
        form.subject = `Issue with ${props.contextType} #${props.contextId}`
        if (props.contextType === 'Booking') {
          form.category = 'Booking'
        } else if (props.contextType === 'Transaction') {
          form.category = 'Payment'
        }
      }
    } else {
      document.body.style.overflow = ''
    }
  },
  { immediate: true }
)

onUnmounted(() => {
  document.body.style.overflow = ''
})
</script>

<style scoped>
.support-modal-shell {
  position: fixed;
  inset: 0;
  z-index: 1200;
  background: rgba(15, 23, 42, 0.45);
  display: grid;
  place-items: center;
  padding: 24px;
}

.support-modal-card {
  width: min(100%, 500px);
  background: #ffffff;
  border: 1px solid rgba(241, 245, 249, 0.8);
  border-radius: 24px;
  box-shadow: 0 24px 64px rgba(15, 23, 42, 0.16);
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  animation: sb-scale-in var(--sb-t-normal) var(--sb-spring) both;
}

.support-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 16px;
}

.support-modal-eyebrow {
  display: block;
  font-size: 11px;
  font-weight: 800;
  color: var(--sb-primary);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 4px;
}

.support-modal-title {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.support-modal-close {
  width: 32px;
  height: 32px;
  border: 0;
  border-radius: 50%;
  background: #f1f5f9;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform var(--sb-t-normal) var(--sb-spring);
}

.support-modal-close:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.context-alert {
  background: rgba(0, 137, 90, 0.06);
  border: 1px solid rgba(0, 137, 90, 0.15);
  border-radius: 12px;
  padding: 12px 16px;
  color: var(--sb-primary);
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.form-label {
  font-size: 13px;
  font-weight: 700;
  color: #334155;
  margin-bottom: 6px;
}

.support-select,
.support-input,
.support-textarea {
  border-radius: 12px;
  border: 1.5px solid #e2e8f0;
  padding: 10px 14px;
  font-size: 14px;
  color: #0f172a;
  background-color: #f8fafc;
  transition: none;
}

.support-select:focus,
.support-input:focus,
.support-textarea:focus {
  background-color: #ffffff;
  border-color: var(--sb-primary);
  box-shadow: 0 0 0 3px rgba(0, 137, 90, 0.12);
  outline: 0;
}

.support-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  border-top: 1px solid #f1f5f9;
  padding-top: 16px;
}

</style>
