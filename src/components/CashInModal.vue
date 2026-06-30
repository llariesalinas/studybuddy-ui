<!-- src/components/CashInModal.vue -->
<template>
  <div class="modal-backdrop fade show"></div>
  <div class="modal fade show d-block" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content cashin-modal">
        <div class="modal-header border-0">
          <div>
            <span class="eyebrow">Wallet</span>
            <h5 class="modal-title">Cash In</h5>
          </div>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <form @submit.prevent="submit">
          <div class="modal-body">
            <p class="cashin-help">
              Load funds to settle owed platform commission. Any excess stays as a withdrawable
              balance.
            </p>
            <label>
              <span>Amount (PHP)</span>
              <input
                v-model.number="amount"
                class="sb-field"
                type="number"
                :min="walletStore.cashinMinimum"
                step="0.01"
                required
                :disabled="submitting"
              />
            </label>
            <p class="cashin-limit">Minimum PHP {{ money(walletStore.cashinMinimum) }}</p>
            <p v-if="error" class="form-error">{{ error }}</p>
          </div>
          <div class="modal-footer border-0">
            <button
              type="button"
              class="modal-secondary sb-btn"
              :disabled="submitting"
              @click="$emit('close')"
            >
              Cancel
            </button>
            <button class="modal-primary sb-btn" :disabled="submitting || !canSubmit">
              {{ submitting ? 'Redirecting...' : 'Continue to Payment' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useWalletStore } from '@/stores/wallet'
import { useToastStore } from '@/stores/toast'

defineEmits(['close'])
const walletStore = useWalletStore()
const toastStore = useToastStore()

const amount = ref(walletStore.cashinMinimum)
const submitting = ref(false)
const error = ref('')

const money = (value) =>
  Number(value || 0).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })

const canSubmit = computed(() => Number(amount.value) >= Number(walletStore.cashinMinimum))

const submit = async () => {
  if (!canSubmit.value) {
    error.value = `Minimum cash-in is PHP ${money(walletStore.cashinMinimum)}.`
    return
  }
  submitting.value = true
  error.value = ''
  try {
    const { checkout_url } = await walletStore.initiateCashIn(amount.value)
    window.location.href = checkout_url
  } catch (e) {
    submitting.value = false
    toastStore.push(
      e.response?.data?.error || 'Could not start cash-in. Please try again.',
      'error'
    )
  }
}
</script>

<style scoped>
.cashin-modal {
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 24px 80px rgba(15, 23, 42, 0.18);
}

.cashin-modal .modal-header,
.cashin-modal .modal-body,
.cashin-modal .modal-footer {
  padding-left: 24px;
  padding-right: 24px;
}

.eyebrow {
  display: inline-flex;
  color: var(--sb-primary);
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.cashin-modal .modal-title {
  margin-top: 6px;
  font-size: 22px;
  font-weight: 900;
}

.cashin-help {
  margin: 0 0 14px;
  color: var(--sb-muted, #475569);
  font-size: 13px;
  line-height: 1.5;
}

.cashin-modal label {
  display: grid;
  gap: 7px;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--sb-muted, #475569);
}

.cashin-modal input {
  width: 100%;
  min-height: 44px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 14px;
  padding: 9px 12px;
  background: rgba(255, 255, 255, 0.72);
  font-size: 14px;
  font-weight: 600;
  text-transform: none;
  letter-spacing: 0;
}

.cashin-limit {
  margin: 8px 0 0;
  color: var(--sb-muted, #475569);
  font-size: 12px;
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
}

.form-error {
  margin: 12px 0 0;
  color: #9a3e3e;
  font-size: 13px;
}

.modal-backdrop {
  z-index: 1050;
}

.modal {
  z-index: 1055;
}
</style>
