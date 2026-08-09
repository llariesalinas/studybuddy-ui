<template>
  <section class="glass-segment session-rail">
    <div class="session-rail-head">
      <h4>{{ actionTitle }}</h4>
      <span v-if="isOngoing" class="session-live-pill">
        <span></span>
        Live
      </span>
    </div>

    <div class="session-rail-list">
      <template v-if="isOngoing">
        <button
          class="session-rail-cta sb-btn btn-primary-action sb-elevated sb-elevated--brand"
          @click="emit('open-chat')"
        >
          <i class="bi bi-chat-dots"></i>
          Open chat
        </button>

        <div
          v-if="midpointCheckIn"
          class="session-rail-status"
          :class="`is-${midpointCheckIn.response || 'saved'}`"
        >
          <strong>{{ midpointStatusTitle }}</strong>
          <span>{{ midpointStatusCopy }}</span>
        </div>
        <button
          v-else
          class="session-rail-button sb-btn"
          :disabled="isQuickSubmitting"
          @click="emit('open-progress')"
        >
          <i class="bi bi-activity"></i>
          Progress check
        </button>

        <button
          class="session-rail-button sb-btn"
          :disabled="isQuickSubmitting"
          @click="emit('venue-arrived')"
        >
          <i class="bi bi-geo-alt"></i>
          I've arrived
        </button>
      </template>

      <template v-else-if="canSubmitPayment">
        <p class="session-rail-copy">
          Your session has ended. Submit your post-session payment details so your tutor can
          verify them.
        </p>
        <button
          class="session-rail-cta sb-btn btn-primary-action sb-elevated sb-elevated--brand"
          @click="emit('submit-payment')"
        >
          Submit Payment
        </button>
      </template>

      <template v-else-if="isAwaitingPaymentVerification">
        <p class="session-rail-copy">Waiting for your tutor to review the submitted payment.</p>
        <button class="session-rail-cta sb-btn btn-soft" disabled>
          Waiting for tutor verification...
        </button>
      </template>

      <template v-else-if="isCompleted && !ratingSubmitted">
        <p class="session-rail-copy">
          Your session is complete. A rating is optional, but it helps improve StudyBuddy matches.
        </p>
        <button
          class="session-rail-cta sb-btn btn-primary-action sb-elevated sb-elevated--brand"
          @click="emit('open-rating')"
        >
          <i class="bi bi-star"></i>
          Leave a Rating
        </button>
      </template>

      <template v-else-if="showCancelAction">
        <p class="session-rail-copy">{{ cancelActionMessage }}</p>
        <button
          class="session-rail-cta sb-btn btn-danger-soft"
          :disabled="isCancelling || !canCancelSession"
          @click="emit('open-cancel')"
        >
          {{ isCancelling ? 'Cancelling...' : isPending ? 'Withdraw request' : 'Cancel Session' }}
        </button>
      </template>

      <template v-else>
        <p class="session-rail-copy">No pending action for this session right now.</p>
      </template>
    </div>

    <div class="session-rail-support">
      <button class="session-rail-report" @click="emit('report')">
        <i class="bi bi-exclamation-circle"></i>
        Report an issue
      </button>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  isOngoing: { type: Boolean, default: false },
  canSubmitPayment: { type: Boolean, default: false },
  isAwaitingPaymentVerification: { type: Boolean, default: false },
  isCompleted: { type: Boolean, default: false },
  ratingSubmitted: { type: Boolean, default: false },
  showCancelAction: { type: Boolean, default: false },
  canCancelSession: { type: Boolean, default: false },
  isCancelling: { type: Boolean, default: false },
  isPending: { type: Boolean, default: false },
  isQuickSubmitting: { type: Boolean, default: false },
  cancelActionMessage: { type: String, default: '' },
  midpointCheckIn: { type: Object, default: null },
  midpointStatusTitle: { type: String, default: '' },
  midpointStatusCopy: { type: String, default: '' },
})

const emit = defineEmits([
  'open-chat',
  'open-progress',
  'venue-arrived',
  'submit-payment',
  'open-rating',
  'open-cancel',
  'report',
])

const actionTitle = computed(() => {
  if (props.isOngoing) return 'Happening now'
  if (props.canSubmitPayment) return 'Next action'
  if (props.isAwaitingPaymentVerification) return 'Payment review'
  if (props.isCompleted) return 'All done'
  return 'Next action'
})
</script>

<style scoped>
.session-rail {
  display: grid;
  align-content: start;
  gap: 0;
}

.session-rail-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.session-rail-head h4 {
  margin: 0;
  color: var(--sb-text-main);
  font-size: 0.96rem;
  font-weight: 850;
}

.session-live-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--sb-pop-pink) 16%, var(--sb-card-bg));
  color: var(--sb-pop-pink-deep);
  padding: 4px 10px;
  font-size: 0.64rem;
  font-weight: 800;
  text-transform: uppercase;
}

.session-live-pill span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
  animation: session-rail-live-beat 1.1s ease-in-out infinite;
}

.session-rail-list {
  display: grid;
  gap: 10px;
}

.session-rail-copy {
  margin: 0;
  color: var(--sb-text-muted);
  font-size: 0.8rem;
  line-height: 1.5;
}

/* Layout-only helper: the shared sb-btn tiers own the visuals. */
.session-rail-cta {
  width: 100%;
  font-size: 0.86rem;
}

.session-rail-cta:focus-visible {
  outline: 0;
  box-shadow:
    0 0 0 4px color-mix(in srgb, var(--sb-primary) 18%, transparent),
    0 10px 24px var(--sb-shadow-soft);
}

.session-rail-button {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  min-height: 46px;
  border: 1px solid var(--sb-card-border);
  border-radius: 14px;
  padding: 0 14px;
  background: color-mix(in srgb, var(--sb-card-bg) 72%, transparent);
  color: var(--sb-text-secondary);
  font: inherit;
  font-size: 0.8rem;
  font-weight: 800;
  text-align: left;
}

.session-rail-button:hover:not(:disabled) {
  border-color: color-mix(in srgb, var(--sb-primary) 34%, var(--sb-card-border));
  background: color-mix(in srgb, var(--sb-card-bg) 96%, transparent);
}

.session-rail-button:focus-visible {
  outline: 0;
  box-shadow:
    0 0 0 4px color-mix(in srgb, var(--sb-primary) 18%, transparent),
    0 10px 24px var(--sb-shadow-soft);
}

.session-rail-button i {
  color: var(--sb-primary);
  font-size: 16px;
}

.session-rail-status {
  position: relative;
  display: grid;
  gap: 3px;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid color-mix(in srgb, var(--sb-card-border) 82%, transparent);
  background: color-mix(in srgb, var(--sb-card-bg) 82%, transparent);
}

.session-rail-status::after {
  content: '';
  position: absolute;
  inset: auto 0 0;
  height: 3px;
  border-radius: 999px;
}

.session-rail-status.is-good::after {
  background: linear-gradient(90deg, var(--sb-primary), var(--sb-primary-mid));
}

.session-rail-status.is-issues::after {
  background: linear-gradient(90deg, var(--sb-pop-yellow), var(--sb-pop-orange));
}

.session-rail-status strong {
  color: var(--sb-text-dark);
  font-size: 0.84rem;
  font-weight: 850;
}

.session-rail-status span {
  color: var(--sb-text-muted);
  font-size: 0.74rem;
  line-height: 1.4;
}

.session-rail-support {
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid var(--sb-card-border);
  text-align: right;
}

.session-rail-report {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 0;
  background: none;
  padding: 0;
  color: var(--sb-danger);
  font: inherit;
  font-size: 0.78rem;
  font-weight: 700;
}

.session-rail-report:focus-visible {
  outline: 0;
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--sb-danger) 18%, transparent);
  border-radius: 6px;
}

@keyframes session-rail-live-beat {
  50% {
    transform: scale(1.7);
    opacity: 0.4;
  }
}

@media (prefers-reduced-motion: reduce) {
  .session-live-pill span {
    animation: none;
  }
}
</style>
