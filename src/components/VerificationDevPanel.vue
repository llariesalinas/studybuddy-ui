<template>
  <details class="dev-panel">
    <summary class="dev-panel-summary">
      <i class="bi bi-bug-fill"></i> DEV: Verification tools
      <span v-if="error" class="dev-panel-flag">{{ error }}</span>
    </summary>

    <div class="dev-panel-body">
      <p class="dev-note">
        Dev-only. Requires <code>VERIFICATION_DEV_TOOLS_ENABLED</code> on the backend. Mutates only
        your own account.
      </p>

      <!-- Live readout -->
      <div class="dev-readout" v-if="readout">
        <span><b>application_status:</b> {{ readout.application_status ?? '—' }}</span>
        <span><b>renewal_status:</b> {{ readout.document_renewal_status ?? '—' }}</span>
        <span><b>due_at:</b> {{ readout.document_renewal_due_at ?? '—' }}</span>
        <span><b>enforced:</b> {{ readout.tutee_verification_enforced }}</span>
        <span><b>override:</b> {{ String(readout.enforcement_override) }}</span>
      </div>

      <!-- State jumper -->
      <div class="dev-group">
        <p class="dev-group-title">Set my verification state</p>
        <div class="dev-btn-row">
          <button
            v-for="s in states"
            :key="s"
            type="button"
            class="dev-btn"
            :disabled="busy"
            @click="setState(s)"
          >
            {{ s }}
          </button>
        </div>
      </div>

      <!-- Enforcement toggle (tutee only) -->
      <div class="dev-group" v-if="role === 'tutee'">
        <p class="dev-group-title">Booking-gate enforcement (global)</p>
        <div class="dev-btn-row">
          <button type="button" class="dev-btn" :disabled="busy" @click="setEnforcement('on')">
            Force ON
          </button>
          <button type="button" class="dev-btn" :disabled="busy" @click="setEnforcement('off')">
            Force OFF
          </button>
          <button type="button" class="dev-btn" :disabled="busy" @click="setEnforcement('clear')">
            Use default
          </button>
        </div>
      </div>
      <p v-else class="dev-note">
        Tutor gate has no global toggle — use <code>renewal_due</code> to block accepting bookings,
        <code>verified</code> to unblock.
      </p>
    </div>
  </details>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useProfileStore } from '@/stores/profile'
import {
  VERIFICATION_STATES,
  getVerificationDevState,
  setVerificationDevState,
  setVerificationDevEnforcement,
} from '@/services/api/verificationDev'

defineProps({
  role: { type: String, required: true },
})

const profileStore = useProfileStore()
const states = VERIFICATION_STATES
const readout = ref(null)
const busy = ref(false)
const error = ref('')

const refresh = async () => {
  try {
    const res = await getVerificationDevState()
    readout.value = res.data
    error.value = ''
  } catch (e) {
    error.value = e?.response?.status === 403 ? 'disabled' : 'error'
  }
}

const runAction = async (fn) => {
  busy.value = true
  try {
    const res = await fn()
    readout.value = res.data
    error.value = ''
    // Refresh the VerificationStatusCard and route-guard state.
    await profileStore.checkProfileStatus()
  } catch (e) {
    error.value = e?.response?.status === 403 ? 'disabled' : 'error'
  } finally {
    busy.value = false
  }
}

const setState = (state) => runAction(() => setVerificationDevState(state))
const setEnforcement = (mode) => runAction(() => setVerificationDevEnforcement(mode))

onMounted(refresh)
</script>

<style scoped>
.dev-panel {
  margin-top: 1rem;
  border: 1px dashed var(--sb-warning-text, #b45309);
  border-radius: 0.75rem;
  padding: 0.5rem 0.9rem;
  background: color-mix(in srgb, var(--sb-warning-bg, #fef3c7) 30%, transparent);
  font-size: 0.85rem;
}

.dev-panel-summary {
  cursor: pointer;
  font-weight: 700;
  color: var(--sb-warning-text, #b45309);
}

.dev-panel-flag {
  margin-left: 0.5rem;
  font-weight: 600;
  opacity: 0.8;
}

.dev-panel-body {
  margin-top: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.dev-note {
  margin: 0;
  font-size: 0.75rem;
  color: var(--sb-text-muted, #6b7280);
}

.dev-readout {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem 1rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.75rem;
}

.dev-group-title {
  margin: 0 0 0.4rem;
  font-weight: 600;
}

.dev-btn-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.dev-btn {
  padding: 0.3rem 0.7rem;
  border-radius: 999px;
  border: 1px solid var(--sb-border, #d1d5db);
  background: var(--sb-surface, #fff);
  font-size: 0.75rem;
  cursor: pointer;
}

.dev-btn:disabled {
  opacity: 0.5;
  cursor: default;
}
</style>
