<template>
  <Teleport to="body">
    <div v-if="open">
      <div class="modal-backdrop fade show campus-location-backdrop" @click="handleBackdropClick"></div>
      <div
        class="modal fade show d-block campus-location-shell"
        tabindex="-1"
        aria-modal="true"
        role="dialog"
      >
        <div
          class="modal-dialog modal-dialog-centered campus-location-dialog"
          :class="{ 'campus-location-dialog--anchored': Boolean(dialogStyle) }"
          :style="dialogStyle"
        >
          <div class="modal-content campus-location-modal">
            <div class="modal-header border-0">
              <h5 class="modal-title">
                {{ screen === 'choice' ? 'Choose Meeting Location' : 'Off-Campus Session' }}
              </h5>
              <button type="button" class="btn-close" @click="handleHeaderClose"></button>
            </div>

            <div class="modal-body">
              <div v-if="screen === 'choice'" class="mode-button-group">
                <button type="button" class="location-button sb-btn" @click="selectInsideCampus">
                  <span class="location-button-icon" aria-hidden="true">
                    <i class="bi bi-building-fill"></i>
                  </span>
                  <span>Inside Campus</span>
                </button>

                <button type="button" class="location-button sb-btn" @click="screen = 'confirm'">
                  <span class="location-button-icon" aria-hidden="true">
                    <i class="bi bi-signpost-split-fill"></i>
                  </span>
                  <span>Outside Campus</span>
                </button>
              </div>

              <p v-else class="confirm-copy">
                Sessions held outside CPU campus are not covered by StudyBuddy. Please meet in a
                safe, public location. Are you sure you want to continue?
              </p>
            </div>

            <div v-if="screen === 'confirm'" class="modal-footer border-0">
              <button type="button" class="modal-secondary sb-btn" @click="backToChoice">
                Go Back
              </button>
              <button type="button" class="modal-primary sb-btn" @click="selectOutsideCampus">
                Yes, Continue
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'

const props = defineProps({
  open: { type: Boolean, required: true },
  anchorSelector: { type: String, default: '' },
})

const emit = defineEmits(['update:open', 'select', 'cancel'])

const screen = ref('choice')
const dialogPosition = ref(null)
let frameId = null

const dialogStyle = computed(() => {
  if (!dialogPosition.value) {
    return null
  }

  return {
    left: `${dialogPosition.value.left}px`,
    top: `${dialogPosition.value.top}px`,
    transform: 'translate(-50%, -50%)',
  }
})

const clearScheduledMeasurement = () => {
  if (frameId && typeof window !== 'undefined') {
    window.cancelAnimationFrame(frameId)
    frameId = null
  }
}

const updateDialogPosition = () => {
  if (typeof window === 'undefined') {
    return
  }

  if (!props.open || !props.anchorSelector) {
    dialogPosition.value = null
    return
  }

  const anchor = document.querySelector(props.anchorSelector)

  if (!anchor) {
    dialogPosition.value = null
    return
  }

  const rect = anchor.getBoundingClientRect()
  dialogPosition.value = {
    left: rect.left + rect.width / 2,
    top: rect.top + rect.height / 2,
  }
}

const scheduleDialogPosition = () => {
  if (typeof window === 'undefined') {
    return
  }

  clearScheduledMeasurement()
  frameId = window.requestAnimationFrame(() => {
    frameId = null
    updateDialogPosition()
  })
}

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      screen.value = 'choice'
      scheduleDialogPosition()
      if (typeof window !== 'undefined') {
        window.addEventListener('resize', updateDialogPosition)
        window.addEventListener('scroll', updateDialogPosition, true)
      }
    } else {
      dialogPosition.value = null
      clearScheduledMeasurement()
      if (typeof window !== 'undefined') {
        window.removeEventListener('resize', updateDialogPosition)
        window.removeEventListener('scroll', updateDialogPosition, true)
      }
    }
  },
)

watch(
  () => props.anchorSelector,
  () => {
    if (props.open) {
      scheduleDialogPosition()
    }
  },
)

onBeforeUnmount(() => {
  clearScheduledMeasurement()
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', updateDialogPosition)
    window.removeEventListener('scroll', updateDialogPosition, true)
  }
})

const dismissChoice = () => {
  emit('cancel')
  emit('update:open', false)
}

const backToChoice = () => {
  screen.value = 'choice'
}

const handleBackdropClick = () => {
  if (screen.value === 'choice') {
    dismissChoice()
    return
  }

  backToChoice()
}

const handleHeaderClose = () => {
  if (screen.value === 'choice') {
    dismissChoice()
    return
  }

  backToChoice()
}

const selectInsideCampus = () => {
  emit('select', 'inside')
  emit('update:open', false)
}

const selectOutsideCampus = () => {
  emit('select', 'outside')
  emit('update:open', false)
}
</script>

<style scoped>
.campus-location-shell {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px 16px;
}

.campus-location-dialog {
  width: min(100%, 560px);
  margin: 0 auto;
}

.campus-location-dialog--anchored {
  position: fixed;
  margin: 0;
  width: min(calc(100vw - 32px), 560px);
}

.campus-location-modal {
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 24px 80px rgba(15, 23, 42, 0.18);
}

.campus-location-modal .modal-header,
.campus-location-modal .modal-body,
.campus-location-modal .modal-footer {
  padding-left: 24px;
  padding-right: 24px;
}

.campus-location-modal .modal-title {
  font-size: 22px;
  font-weight: 900;
  color: var(--sb-text-main);
}

.mode-button-group {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.location-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  min-height: 52px;
  border: 1px solid var(--sb-card-border);
  border-radius: 14px;
  background: var(--sb-card-bg);
  color: var(--sb-text-main);
  padding: 12px 14px;
  font-size: 14px;
  font-weight: 700;
  line-height: 1.2;
  transition: transform var(--sb-t-normal) var(--sb-spring);
}

.location-button:hover,
.location-button:focus-visible {
  border-color: var(--sb-primary);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--sb-primary) 12%, transparent);
  outline: none;
}

.location-button:active {
  transform: scale(0.98);
}

.location-button-icon {
  display: inline-flex;
  flex: 0 0 auto;
  color: var(--sb-primary);
}

.confirm-copy {
  margin: 0;
  color: var(--sb-muted, #475569);
  font-size: 14px;
  line-height: 1.6;
}

.modal-primary,
.modal-secondary {
  min-height: 42px;
  padding: 10px 18px;
  border: 0;
  border-radius: 14px;
  font-size: 13px;
  font-weight: 900;
}

.modal-primary {
  color: #fff;
  background: var(--sb-primary);
}

.modal-secondary {
  background: rgba(255, 255, 255, 0.7);
  color: var(--sb-text-main);
}

.btn-close:focus-visible {
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--sb-primary) 12%, transparent);
  outline: none;
}

.campus-location-backdrop {
  z-index: 1050;
}

.campus-location-shell {
  z-index: 1055;
}

@media (max-width: 575px) {
  .campus-location-shell {
    padding: 16px;
  }

  .campus-location-dialog--anchored {
    position: relative;
    left: auto !important;
    top: auto !important;
    transform: none !important;
    width: 100%;
    margin: auto;
  }

  .mode-button-group {
    grid-template-columns: 1fr;
  }
}
</style>
