<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="session-cancel-shell sb-overlay"
      @click.self="emit('close')"
    >
      <section
        class="session-cancel-card"
        :class="{ 'is-late': showPenaltyCopy }"
        role="dialog"
        aria-modal="true"
        aria-labelledby="session-cancel-title"
      >
        <header class="session-cancel-header">
          <div>
            <span class="session-cancel-eyebrow">{{ isPending ? 'Withdraw request' : 'Cancel session' }}</span>
            <h5 id="session-cancel-title" class="session-cancel-title">
              {{ showPenaltyCopy ? 'This cancellation is late' : 'Are you sure?' }}
            </h5>
          </div>
          <button
            type="button"
            class="session-cancel-close sb-btn"
            aria-label="Close"
            :disabled="submitting"
            @click="emit('close')"
          >
            <i class="bi bi-x-lg"></i>
          </button>
        </header>

        <div class="session-cancel-body">
          <!-- Pending requests never reach the Grace Cutoff rules, so they get neither the
               penalty-free promise nor the strike warning. -->
          <p v-if="isPending" class="session-cancel-lead">
            You can withdraw this pending request.
          </p>

          <p v-else-if="!isLate" class="session-cancel-lead">
            You're still before the Grace Cutoff ({{ cutoffLabel }}). Cancelling now is free — no
            strike, no review ticket.
          </p>

          <div v-else class="session-cancel-warning">
            <p class="session-cancel-warning-line">
              <strong>This cancellation is late.</strong>
              The Grace Cutoff passed at {{ cutoffLabel }}. This opens a review ticket and counts as
              a strike unless an admin excuses it.<template v-if="walletPenalty">
              If an admin rules it counted, ₱50 is deducted from your wallet.</template>
            </p>

            <p v-if="strikesLoading" class="session-cancel-warning-line">
              <span class="session-cancel-skeleton" aria-hidden="true"></span>
              <span class="visually-hidden">Loading your strike count</span>
            </p>
            <p v-else-if="!strikesUnavailable" class="session-cancel-warning-line">
              You have {{ strikeCount }} of {{ strikeCap }} strikes from the last 14 days<template
                v-if="strikeProvisionalCount > 0"
              > ({{ strikeProvisionalCount }} under review)</template>.
            </p>

            <p v-if="!strikesUnavailable" class="session-cancel-warning-line">
              <template v-if="isFinalStrike">
                This will be your {{ strikeCapOrdinal }} strike — you won't be able to book new
                sessions until your oldest strike expires, about 14 days after it was issued.
              </template>
              <template v-else-if="walletPenalty">
                At {{ strikeCap }} strikes you stop appearing in tutee search until a strike expires.
              </template>
              <template v-else>
                At {{ strikeCap }} strikes you can't book new sessions until a strike expires.
              </template>
            </p>
          </div>

          <label class="session-cancel-label" for="session-cancel-reason">Reason (required)</label>
          <textarea
            id="session-cancel-reason"
            v-model="reason"
            class="session-cancel-field"
            rows="3"
            :placeholder="`Let your ${counterpartLabel} know why you're cancelling...`"
            :disabled="submitting"
          ></textarea>
          <p class="session-cancel-hint">
            Please also
            <a href="#" @click.prevent="emit('go-to-chat')">message your {{ counterpartLabel }} in Chat</a>
            to coordinate.
          </p>
        </div>

        <div class="session-cancel-footer">
          <button
            type="button"
            class="session-cancel-btn session-cancel-btn-soft sb-btn"
            :disabled="submitting"
            @click="emit('close')"
          >
            {{ isPending ? 'Keep request' : 'Keep session' }}
          </button>
          <button
            type="button"
            class="session-cancel-btn session-cancel-btn-danger sb-btn"
            :disabled="submitting || !reasonValid"
            @click="emit('confirm', reason.trim())"
          >
            <span
              v-if="submitting"
              class="spinner-border spinner-border-sm"
              role="status"
              aria-hidden="true"
            ></span>
            {{ confirmLabel }}
          </button>
        </div>
      </section>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, onUnmounted, ref, watch } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  submitting: { type: Boolean, default: false },
  isPending: { type: Boolean, default: false },
  isLate: { type: Boolean, default: false },
  cutoffLabel: { type: String, default: '' },
  strikeCount: { type: Number, default: 0 },
  strikeCap: { type: Number, default: 3 },
  strikeProvisionalCount: { type: Number, default: 0 },
  strikesLoading: { type: Boolean, default: false },
  strikesUnavailable: { type: Boolean, default: false },
  // Who the canceller has to coordinate with -- 'tutor' when a tutee is cancelling, 'tutee' when
  // a tutor is.
  counterpartLabel: { type: String, default: 'tutor' },
  // Tutors also lose P50 from their wallet if an admin rules the strike counted. Tutees have no
  // wallet, so this stays off for them.
  walletPenalty: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'confirm', 'go-to-chat'])

const reason = ref('')

// Mirrors the server's own minimum in cancel_booking, so the button never enables into a 400.
const reasonValid = computed(() => reason.value.trim().length >= 5)

const showPenaltyCopy = computed(() => props.isLate && !props.isPending)

const isFinalStrike = computed(() => props.strikeCount === props.strikeCap - 1)

// The cap is a constant shared with the backend, so it can change -- "3th strike" is one config
// bump away from a literal suffix.
const ordinalRules = new Intl.PluralRules(undefined, { type: 'ordinal' })
const ORDINAL_SUFFIXES = { one: 'st', two: 'nd', few: 'rd', other: 'th' }

const strikeCapOrdinal = computed(() =>
  `${props.strikeCap}${ORDINAL_SUFFIXES[ordinalRules.select(props.strikeCap)] || 'th'}`,
)

const confirmLabel = computed(() => {
  if (props.submitting) {
    return props.isPending ? 'Withdrawing...' : 'Cancelling...'
  }

  return props.isPending ? 'Yes, withdraw request' : 'Yes, cancel session'
})

watch(
  () => props.open,
  (isOpen) => {
    document.body.style.overflow = isOpen ? 'hidden' : ''

    if (isOpen) {
      reason.value = ''
    }
  },
  { immediate: true },
)

onUnmounted(() => {
  document.body.style.overflow = ''
})
</script>

<style scoped>
.session-cancel-shell {
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgba(15, 23, 42, 0.45);
}

.session-cancel-card {
  position: relative;
  z-index: var(--sb-z-surface);
  width: min(100%, 440px);
  padding: 26px;
  background:
    radial-gradient(circle at 12% 16%, color-mix(in srgb, var(--sb-primary) 12%, transparent), transparent 34%),
    radial-gradient(circle at 88% 84%, color-mix(in srgb, var(--sb-pop-orange) 12%, transparent), transparent 28%),
    var(--sb-card-bg);
  border: 1px solid var(--sb-card-border);
  border-radius: 24px;
  box-shadow: 0 24px 64px rgba(15, 23, 42, 0.16);
}

.session-cancel-card.is-late {
  border-color: color-mix(in srgb, var(--sb-danger) 32%, var(--sb-card-border));
}

.session-cancel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--sb-card-border);
}

.session-cancel-eyebrow {
  display: block;
  margin-bottom: 4px;
  color: var(--sb-danger);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}

.session-cancel-title {
  margin: 0;
  color: var(--sb-text-main);
  font-size: 18px;
  font-weight: 800;
}

.session-cancel-close {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border: 0;
  border-radius: 50%;
  background: color-mix(in srgb, var(--sb-text-main) 8%, transparent);
  color: var(--sb-text-muted);
}

.session-cancel-body {
  padding: 18px 0;
}

.session-cancel-lead {
  margin: 0 0 14px;
  color: var(--sb-text-main);
  font-size: 14px;
  line-height: 1.5;
}

.session-cancel-warning {
  display: grid;
  gap: 8px;
  margin-bottom: 14px;
  padding: 14px 16px;
  border: 1px solid color-mix(in srgb, var(--sb-danger) 30%, transparent);
  border-radius: 16px;
  background: color-mix(in srgb, var(--sb-danger) 12%, transparent);
}

.session-cancel-warning-line {
  margin: 0;
  color: var(--sb-text-main);
  font-size: 13.5px;
  line-height: 1.5;
}

.session-cancel-warning-line strong {
  color: var(--sb-danger);
}

.session-cancel-skeleton {
  display: block;
  width: 70%;
  height: 13px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--sb-text-main) 12%, transparent);
}

.session-cancel-label {
  display: block;
  margin-bottom: 6px;
  color: var(--sb-text-muted);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}

.session-cancel-field {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid var(--sb-card-border);
  border-radius: 14px;
  background: color-mix(in srgb, var(--sb-card-bg) 96%, transparent);
  color: var(--sb-text-main);
  font: inherit;
  font-size: 14px;
  resize: vertical;
}

.session-cancel-field:focus {
  outline: 0;
  border-color: color-mix(in srgb, var(--sb-danger) 40%, var(--sb-card-border));
}

.session-cancel-hint {
  margin: 10px 0 0;
  color: var(--sb-text-muted);
  font-size: 12.5px;
}

.session-cancel-hint a {
  color: var(--sb-primary);
  font-weight: 700;
  text-decoration: none;
}

.session-cancel-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 16px;
  border-top: 1px solid var(--sb-card-border);
}

.session-cancel-btn {
  min-height: 42px;
  padding: 0 18px;
}

.session-cancel-btn-soft {
  border: 1px solid var(--sb-card-border);
  background: color-mix(in srgb, var(--sb-card-bg) 72%, transparent);
  color: var(--sb-text-main);
}

.session-cancel-btn-danger {
  border: 0;
  background: var(--sb-danger);
  color: #fff;
  box-shadow: 0 8px 18px rgba(239, 68, 68, 0.25);
}
</style>
