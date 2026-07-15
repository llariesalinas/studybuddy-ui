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
            <h5 id="session-check-title" class="session-check-title">How is the session going so far?</h5>
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
            A quick response helps us spot problems while there is still time to help.
          </p>

          <div class="session-check-options">
            <button
              type="button"
              class="session-check-option session-check-option-issue sb-btn"
              :class="{ 'is-holding': holdState === 'issues' }"
              :disabled="submitting"
              @pointerdown.prevent="startHold('issues')"
              @pointerup.prevent="cancelHold"
              @pointerleave="cancelHold"
              @pointercancel="cancelHold"
              @keydown.space.prevent="handleKeyConfirm($event, 'issues')"
              @keydown.enter.prevent="handleKeyConfirm($event, 'issues')"
              @click="handleAssistiveClick($event, 'issues')"
            >
              <span class="session-check-option-fill" :style="{ width: `${holdProgress('issues')}%` }"></span>
              <strong>Having issues</strong>
              <span>Pacing is off, the tutor is missing, or you need help now.</span>
            </button>

            <button
              type="button"
              class="session-check-option session-check-option-good sb-btn"
              :class="{ 'is-holding': holdState === 'good' }"
              :disabled="submitting"
              @pointerdown.prevent="startHold('good')"
              @pointerup.prevent="cancelHold"
              @pointerleave="cancelHold"
              @pointercancel="cancelHold"
              @keydown.space.prevent="handleKeyConfirm($event, 'good')"
              @keydown.enter.prevent="handleKeyConfirm($event, 'good')"
              @click="handleAssistiveClick($event, 'good')"
            >
              <span class="session-check-option-fill" :style="{ width: `${holdProgress('good')}%` }"></span>
              <strong>Everything is on track</strong>
              <span>The session is going well and you are making progress.</span>
            </button>
          </div>
        </div>

        <footer class="session-check-actions">
          <span class="session-check-hint">Hold for a moment, or press Enter/Space, to send your answer.</span>
          <span v-if="submitting" class="session-check-saving">
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            Saving...
          </span>
        </footer>
      </section>
    </div>
  </Teleport>
</template>

<script setup>
import { onUnmounted, ref, watch } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  submitting: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'confirm'])

const HOLD_MS = 700
const holdState = ref(null)
const holdStartedAt = ref(0)
const holdTick = ref(0)
let holdTimer = null
let holdFrame = null

const holdProgress = (key) => {
  if (holdState.value !== key || !holdStartedAt.value) {
    return 0
  }

  return Math.min(100, Math.round((holdTick.value / HOLD_MS) * 100))
}

const clearHoldTimer = () => {
  if (holdTimer) {
    window.clearTimeout(holdTimer)
    holdTimer = null
  }
  if (holdFrame) {
    window.cancelAnimationFrame(holdFrame)
    holdFrame = null
  }
}

const cancelHold = () => {
  clearHoldTimer()
  holdState.value = null
  holdStartedAt.value = 0
  holdTick.value = 0
}

const tickHold = () => {
  if (!holdStartedAt.value) {
    return
  }

  holdTick.value = Date.now() - holdStartedAt.value
  holdFrame = window.requestAnimationFrame(tickHold)
}

const confirmHold = () => {
  const response = holdState.value
  cancelHold()

  if (response) {
    emit('confirm', response)
  }
}

const confirmResponse = (response) => {
  if (props.submitting) {
    return
  }

  cancelHold()
  emit('confirm', response)
}

/* Keyboard users confirm with a single press — a hold gesture is not operable
   with key auto-repeat, and some assistive tech can only emit single activations. */
const handleKeyConfirm = (event, response) => {
  if (event.repeat) {
    return
  }

  confirmResponse(response)
}

/* Switch access / voice control synthesize clicks (detail === 0) with no pointer
   hold; real pointer clicks (detail > 0) already went through the hold path. */
const handleAssistiveClick = (event, response) => {
  if (event.detail === 0) {
    confirmResponse(response)
  }
}

const startHold = (response) => {
  if (props.submitting || holdState.value === response) {
    return
  }

  cancelHold()
  holdState.value = response
  holdStartedAt.value = Date.now()
  holdTick.value = 0
  holdFrame = window.requestAnimationFrame(tickHold)
  holdTimer = window.setTimeout(confirmHold, HOLD_MS)
}

watch(
  () => props.open,
  (isOpen) => {
    document.body.style.overflow = isOpen ? 'hidden' : ''

    if (!isOpen) {
      cancelHold()
    }
  },
  { immediate: true },
)

onUnmounted(() => {
  document.body.style.overflow = ''
  cancelHold()
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
  overflow: hidden;
  padding: 28px;
  background:
    radial-gradient(circle at 12% 16%, color-mix(in srgb, var(--sb-primary) 12%, transparent), transparent 34%),
    radial-gradient(circle at 88% 84%, color-mix(in srgb, var(--sb-pop-yellow) 12%, transparent), transparent 28%),
    var(--sb-card-bg);
  border: 1px solid var(--sb-card-border);
  border-radius: 24px;
  box-shadow: 0 24px 64px rgba(15, 23, 42, 0.16);
}

.session-check-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--sb-card-border);
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
  color: var(--sb-text-main);
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
  background: color-mix(in srgb, var(--sb-text-main) 8%, transparent);
  color: var(--sb-text-muted);
}

.session-check-body {
  padding: 20px 0;
}

.session-check-copy {
  margin: 0 0 16px;
  color: var(--sb-text-main);
  font-size: 15px;
  line-height: 1.6;
}

.session-check-options {
  display: grid;
  gap: 12px;
}

.session-check-option {
  --sb-motion-lift: -1px;
  position: relative;
  display: grid;
  gap: 4px;
  overflow: hidden;
  width: 100%;
  padding: 16px 16px 16px 18px;
  border: 1px solid var(--sb-card-border);
  border-radius: 20px;
  background: color-mix(in srgb, var(--sb-card-bg) 94%, transparent);
  text-align: left;
  transition:
    transform var(--sb-t-normal) var(--sb-spring),
    border-color var(--sb-t-normal) var(--sb-spring),
    box-shadow var(--sb-t-normal) var(--sb-spring);
}

.session-check-option:hover {
  transform: translateY(-1px);
  box-shadow: 0 14px 28px rgba(15, 23, 42, 0.08);
}

.session-check-option strong,
.session-check-option span {
  position: relative;
  z-index: 1;
}

.session-check-option strong {
  color: var(--sb-text-main);
  font-size: 15px;
}

.session-check-option span {
  color: var(--sb-text-muted);
  font-size: 13px;
  line-height: 1.45;
}

.session-check-option-fill {
  position: absolute;
  inset: auto auto 0 0;
  width: 0;
  height: 100%;
  opacity: 0.18;
  transition: width 0.08s linear;
}

.session-check-option-good .session-check-option-fill {
  background: linear-gradient(
    90deg,
    color-mix(in srgb, var(--sb-primary) 24%, transparent),
    color-mix(in srgb, var(--sb-primary-mid) 26%, transparent)
  );
}

.session-check-option-issue .session-check-option-fill {
  background: linear-gradient(
    90deg,
    color-mix(in srgb, var(--sb-pop-yellow) 28%, transparent),
    color-mix(in srgb, var(--sb-pop-orange) 28%, transparent)
  );
}

.session-check-option-good.is-holding {
  border-color: color-mix(in srgb, var(--sb-primary) 32%, var(--sb-card-border));
}

.session-check-option-issue.is-holding {
  border-color: color-mix(in srgb, var(--sb-pop-orange) 34%, var(--sb-card-border));
}

.session-check-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid var(--sb-card-border);
}

.session-check-hint,
.session-check-saving {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--sb-text-muted);
  font-size: 12px;
  font-weight: 600;
}

@media (max-width: 575px) {
  .session-check-actions {
    align-items: flex-start;
    flex-direction: column;
  }
}

@media (prefers-reduced-motion: reduce) {
  .session-check-option,
  .session-check-option-fill {
    transition: none;
  }

  .session-check-option:hover {
    transform: none;
  }
}
</style>
