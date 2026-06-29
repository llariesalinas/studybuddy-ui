<!-- src/views/TutorWallet.vue -->
<template>
  <div class="wallet-shell">
    <section class="wallet-grid wallet-top-grid">
      <article class="glass-panel performance-card sb-interactive">
        <div class="ring-wrap" aria-label="Wallet performance">
          <svg class="progress-rings" viewBox="0 0 120 120" role="img">
            <circle class="ring-base" cx="60" cy="60" r="50" pathLength="100"></circle>
            <circle class="ring-base ring-base-inner" cx="60" cy="60" r="36" pathLength="100"></circle>
            <circle
              class="ring-progress ring-primary"
              cx="60"
              cy="60"
              r="50"
              pathLength="100"
              :style="{ strokeDashoffset: 100 - netRetainedPercent }"
            ></circle>
            <circle
              class="ring-progress ring-secondary"
              cx="60"
              cy="60"
              r="36"
              pathLength="100"
              :style="{ strokeDashoffset: 100 - deductionPercent }"
            ></circle>
          </svg>
          <div class="ring-center">
            <i class="bi bi-graph-up-arrow"></i>
          </div>
        </div>

        <div class="performance-copy">
          <span class="eyebrow">Wallet Ledger</span>
          <h3>Performance Track</h3>
          <p>
            Your wallet activity is based on completed online sessions, platform deductions,
            provider fees, and cash-out ledger entries.
          </p>

          <div class="metric-grid">
            <div class="metric-item">
              <span class="metric-dot metric-dot-primary"></span>
              <div>
                <p>Gross Earned</p>
                <strong>PHP {{ money(walletStore.grossEarned) }}</strong>
              </div>
            </div>
            <div class="metric-item">
              <span class="metric-dot metric-dot-secondary"></span>
              <div>
                <p>Net Gained</p>
                <strong>PHP {{ money(walletStore.netEarned) }}</strong>
              </div>
            </div>
          </div>

          <div class="ledger-note">
            <i class="bi bi-info-circle"></i>
            <span>
              Cash-outs deduct the requested amount plus PHP
              {{ money(walletStore.cashoutProviderFee) }} provider fee.
            </span>
          </div>
        </div>
      </article>

      <article class="balance-card glass-panel sb-interactive">
        <div>
          <span class="eyebrow balance-eyebrow">Available Balance</span>
          <h2>PHP {{ money(walletStore.balance) }}</h2>
          <p v-if="walletStore.pendingAmount > 0">
            PHP {{ money(walletStore.pendingAmount) }} pending verification
          </p>
          <p v-else>Ready for eligible cash-outs.</p>
        </div>

        <div class="balance-actions">
          <button class="balance-cashout-btn sb-btn" @click="showCashinModal = true">
            <i class="bi bi-plus-circle"></i>
            Cash In
          </button>
          <button class="balance-cashout-btn sb-btn" @click="showCashoutModal = true">
            <i class="bi bi-cash-coin"></i>
            Cash Out
          </button>
          <button
            class="balance-refresh-btn sb-btn"
            :disabled="walletStore.loading"
            @click="refreshData"
            aria-label="Refresh wallet"
          >
            <i class="bi bi-arrow-clockwise" :class="{ spin: walletStore.loading }"></i>
          </button>
        </div>
      </article>
    </section>

    <section class="wallet-grid wallet-main-grid">
      <article class="glass-panel activity-card">
        <header class="section-header">
          <div>
            <span class="eyebrow">Ledger</span>
            <h3>Recent Activity</h3>
          </div>
          <button class="section-action sb-btn" @click="refreshData">Refresh</button>
        </header>

        <div v-if="walletStore.transactions.length === 0" class="empty-state">
          <i class="bi bi-wallet2"></i>
          <p>No transactions found.</p>
        </div>

        <TransitionGroup v-else name="wallet-list" tag="div" class="activity-list">
          <div
            v-for="tx in walletStore.transactions.slice(0, 8)"
            :key="tx.id"
            class="activity-row sb-interactive"
          >
            <div class="activity-icon" :class="transactionTone(tx.transaction_type)">
              <i :class="transactionIcon(tx.transaction_type)"></i>
            </div>

            <div class="activity-body">
              <div class="activity-title-line">
                <h4>{{ tx.description }}</h4>
                <strong :class="Number(tx.amount) < 0 ? 'amount-negative' : 'amount-positive'">
                  {{ Number(tx.amount) > 0 ? '+' : '-' }} PHP
                  {{ money(Math.abs(Number(tx.amount))) }}
                </strong>
              </div>
              <div class="activity-meta">
                <span class="type-chip" :class="transactionTone(tx.transaction_type)">
                  {{ formatType(tx.transaction_type) }}
                </span>
                <span>{{ formatDate(tx.created_at) }}</span>
                <span v-if="tx.reference_id">ID: {{ tx.reference_id }}</span>
              </div>
            </div>
          </div>
        </TransitionGroup>
      </article>
    </section>

    <section class="wallet-grid wallet-history-grid">
      <article class="glass-panel cashout-history-card">
        <header class="section-header">
          <div>
            <span class="eyebrow">Cash-Outs</span>
            <h3>Cash-Out History</h3>
          </div>
          <span class="history-summary">
            Minimum PHP {{ money(walletStore.cashoutMinimum) }}
          </span>
        </header>

        <div v-if="walletStore.withdrawals.length === 0" class="empty-state compact-empty">
          <i class="bi bi-send"></i>
          <p>No cash-outs yet.</p>
        </div>

        <TransitionGroup v-else name="wallet-list" tag="div" class="cashout-list">
          <div
            v-for="cashout in walletStore.withdrawals.slice(0, 6)"
            :key="cashout.id"
            class="cashout-row sb-interactive"
          >
            <div>
              <div class="cashout-title">
                <strong>{{ cashout.account_name || 'Cash-out destination' }}</strong>
                <span :class="getWithdrawalStatusClass(cashout.status)">
                  {{ cashout.status }}
                </span>
              </div>
              <p>
                {{ formatDestinationType(cashout.method) }} ·
                {{ maskAccount(cashout.account_number) }}
              </p>
              <small v-if="cashout.provider_reference_number">
                Ref: {{ cashout.provider_reference_number }}
              </small>
              <small v-if="cashout.failure_reason || cashout.provider_error_message" class="failure-text">
                {{ cashout.failure_reason || cashout.provider_error_message }}
              </small>
            </div>
            <div class="cashout-amount">
              <strong>- PHP {{ money(cashout.amount) }}</strong>
              <span>Fee PHP {{ money(cashout.provider_fee || 0) }}</span>
              <small>{{ formatDate(cashout.requested_at) }}</small>
            </div>
          </div>
        </TransitionGroup>
      </article>
    </section>

    <section v-if="isDev" class="glass-panel dev-tools-card">
      <div class="dev-label">
        <span><i class="bi bi-tools"></i></span>
        <div>
          <strong>Dev Tools</strong>
          <p>Internal testing environment</p>
        </div>
      </div>
      <div class="dev-actions">
        <input v-model.number="devAmount" class="sb-field" type="number" min="1" aria-label="Dev amount" />
        <button class="sb-btn" @click="addDevFunds">Add Test Funds</button>
        <button class="sb-btn secondary" @click="removeDevFunds">Remove Funds</button>
      </div>
    </section>

    <div v-if="showCashoutModal" class="modal-backdrop fade show"></div>
    <div v-if="showCashoutModal" class="modal fade show d-block" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content wallet-modal">
          <div class="modal-header border-0">
            <div>
              <span class="eyebrow">Wallet</span>
              <h5 class="modal-title">Cash Out</h5>
            </div>
            <button type="button" class="btn-close" @click="closeCashoutModal"></button>
          </div>

          <div v-if="showConfirmStep" class="modal-body">
            <div class="confirm-summary">
              <p class="confirm-lead">
                This is a new payout destination. Please confirm the details below before we
                send your cash-out.
              </p>
              <div class="confirm-row">
                <span>Destination type</span>
                <strong>{{ formatDestinationType(cashoutForm.destination_type) }}</strong>
              </div>
              <div class="confirm-row">
                <span>Receiving institution</span>
                <strong>{{ cashoutForm.receiving_institution_name || '-' }}</strong>
              </div>
              <div class="confirm-row">
                <span>Account number</span>
                <strong>{{ maskAccount(cashoutForm.account_number) }}</strong>
              </div>
              <div class="confirm-row">
                <span>Account name</span>
                <strong>{{ cashoutForm.account_name || '-' }}</strong>
              </div>
              <div class="confirm-row">
                <span>Amount you receive</span>
                <strong>PHP {{ money(cashoutAmount) }}</strong>
              </div>
              <div class="confirm-row">
                <span>Total deducted</span>
                <strong>PHP {{ money(totalDeducted) }}</strong>
              </div>
            </div>

            <p v-if="cashoutError" class="form-error">{{ cashoutError }}</p>

            <div class="modal-footer border-0">
              <button type="button" class="modal-secondary sb-btn" @click="showConfirmStep = false">
                Edit
              </button>
              <button
                type="button"
                class="modal-primary sb-btn"
                :disabled="isSubmitting"
                @click="submitCashout(true)"
              >
                {{ isSubmitting ? 'Processing...' : 'Confirm & Send' }}
              </button>
            </div>
          </div>

          <form v-else @submit.prevent="handleCashout">
            <div class="modal-body">
              <div v-if="walletStore.recentCashOuts.length" class="recent-shortcuts">
                <span class="field-hint">Recent destinations</span>
                <div class="recent-shortcut-list">
                  <button
                    v-for="recent in walletStore.recentCashOuts.slice(0, 4)"
                    :key="recent.id"
                    type="button"
                    class="recent-shortcut-card sb-interactive"
                    @click="applyRecentShortcut(recent)"
                  >
                    <strong>{{ recent.receiving_institution_name }}</strong>
                    <code>{{ maskAccount(recent.account_number) }}</code>
                    <small>{{ formatDate(recent.requested_at) }}</small>
                  </button>
                </div>
              </div>

              <label>
                <span>Destination Type</span>
                <SbSelectModal
                  v-model="cashoutForm.destination_type"
                  :options="destinationTypeOptions"
                  title="Destination Type"
                  placeholder="Select type"
                  trigger-class="wallet-select-trigger"
                />
              </label>

              <label>
                <span>Receiving Institution</span>
                <SbSelectModal
                  v-model="cashoutForm.receiving_institution_id"
                  :options="receivingInstitutionOptions"
                  title="Receiving Institution"
                  placeholder="Select institution"
                  :clearable="true"
                  :searchable="true"
                  trigger-class="wallet-select-trigger"
                />
              </label>

              <label>
                <span>Account Number</span>
                <input v-model.trim="cashoutForm.account_number" class="sb-field" required />
              </label>

              <label>
                <span>Account Name</span>
                <input v-model.trim="cashoutForm.account_name" class="sb-field" required />
              </label>

              <label v-if="cashoutForm.destination_type === 'bank'">
                <span>Bank Name</span>
                <input v-model.trim="cashoutForm.bank_name" class="sb-field" />
              </label>

              <label>
                <span>Amount You Receive</span>
                <input
                  v-model.number="cashoutForm.amount"
                  class="sb-field"
                  type="number"
                  step="0.01"
                  :min="walletStore.cashoutMinimum"
                  :max="walletStore.cashoutMaximum"
                  required
                />
                <small class="field-hint">
                  Minimum PHP {{ money(walletStore.cashoutMinimum) }} · Maximum PHP
                  {{ money(walletStore.cashoutMaximum) }} per request
                </small>
              </label>

              <label>
                <span>Note (optional)</span>
                <textarea v-model.trim="cashoutForm.note" class="sb-field" rows="2"></textarea>
              </label>

              <div class="cashout-summary">
                <div>
                  <span>You receive</span>
                  <strong>PHP {{ money(cashoutAmount) }}</strong>
                </div>
                <div>
                  <span>Provider fee</span>
                  <strong>PHP {{ money(walletStore.cashoutProviderFee) }}</strong>
                </div>
                <div>
                  <span>Total deducted</span>
                  <strong>PHP {{ money(totalDeducted) }}</strong>
                </div>
              </div>

              <p v-if="cashoutError" class="form-error">{{ cashoutError }}</p>
            </div>
            <div class="modal-footer border-0">
              <button type="button" class="modal-secondary sb-btn" @click="closeCashoutModal">
                Cancel
              </button>
              <button class="modal-primary sb-btn" :disabled="isSubmitting || !canSubmitCashout">
                {{ isSubmitting ? 'Processing...' : 'Confirm Cash Out' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <CashInModal v-if="showCashinModal" @close="showCashinModal = false" />
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SbSelectModal from '@/components/SbSelectModal.vue'
import CashInModal from '@/components/CashInModal.vue'
import { useWalletStore } from '@/stores/wallet'
import { useToastStore } from '@/stores/toast'
import { getReceivingInstitutionLogoUrl } from '@/data/receivingInstitutionLogos'
import { LOGO_DEV_TOKEN } from '@/config'

const route = useRoute()
const router = useRouter()
const toastStore = useToastStore()
const walletStore = useWalletStore()
const showCashinModal = ref(false)
const showCashoutModal = ref(false)
const isSubmitting = ref(false)
const isDev = import.meta.env.DEV
const devAmount = ref(500)

const cashoutForm = reactive({
  amount: 0,
  destination_type: 'gcash',
  receiving_institution_id: '',
  receiving_institution_name: '',
  receiving_institution_code: '',
  account_number: '',
  account_name: '',
  bank_name: '',
  note: '',
})

const showConfirmStep = ref(false)

const destinationTypeOptions = [
  { label: 'GCash', value: 'gcash' },
  { label: 'Bank', value: 'bank' },
]

const cashoutAmount = computed(() => Number(cashoutForm.amount) || 0)
const totalDeducted = computed(() => cashoutAmount.value + Number(walletStore.cashoutProviderFee || 0))

const grossValue = computed(() => Number(walletStore.grossEarned) || 0)
const netValue = computed(() => Number(walletStore.netEarned) || 0)
const deductionValue = computed(() => Number(walletStore.totalDeductions) || 0)
const netRetainedPercent = computed(() =>
  grossValue.value > 0 ? Math.min(100, Math.round((netValue.value / grossValue.value) * 100)) : 0
)
const deductionPercent = computed(() =>
  grossValue.value > 0 ? Math.min(100, Math.round((deductionValue.value / grossValue.value) * 100)) : 0
)

const cashoutError = computed(() => {
  if (!cashoutForm.destination_type) return 'Select a destination type.'
  if (!cashoutForm.receiving_institution_id) return 'Select a receiving institution.'
  if (!cashoutForm.account_number) return 'Enter the account number.'
  if (!cashoutForm.account_name) return 'Enter the account name.'
  if (cashoutAmount.value < Number(walletStore.cashoutMinimum)) {
    return `Minimum cash-out is PHP ${money(walletStore.cashoutMinimum)}.`
  }
  if (totalDeducted.value > Number(walletStore.balance || 0)) {
    return 'Balance must cover the amount plus provider fee.'
  }
  if (cashoutAmount.value > Number(walletStore.cashoutMaximum)) {
    return `Maximum cash-out per request is PHP ${money(walletStore.cashoutMaximum)}.`
  }
  return ''
})

const canSubmitCashout = computed(() => !cashoutError.value)

const money = (value) =>
  Number(value || 0).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })

const refreshData = async () => {
  await Promise.all([
    walletStore.fetchWallet(),
    walletStore.fetchTransactions(),
    walletStore.fetchWithdrawals(),
  ])
}

const institutionAttributes = (institution) => institution?.attributes || institution || {}
const institutionId = (institution) => institution?.id || institutionAttributes(institution).id || ''
const institutionName = (institution) =>
  institutionAttributes(institution).name ||
  institutionAttributes(institution).bank_name ||
  institutionAttributes(institution).institution_name ||
  institutionId(institution)
const institutionCode = (institution) =>
  institutionAttributes(institution).code || institutionAttributes(institution).bank_code || ''
const receivingInstitutionOptions = computed(() =>
  walletStore.receivingInstitutions.map((institution) => ({
    label: institutionName(institution),
    value: institutionId(institution),
    icon: getReceivingInstitutionLogoUrl({ name: institutionName(institution) }, LOGO_DEV_TOKEN),
  }))
)

const formatDestinationType = (type) => (type === 'gcash' ? 'GCash' : 'Bank Transfer')

const maskAccount = (value = '') => {
  const account = String(value)
  if (account.length <= 4) return account || '-'
  return `${account.slice(0, 4)} •••• ${account.slice(-3)}`
}

const resetCashoutForm = () => {
  cashoutForm.amount = 0
  cashoutForm.destination_type = 'gcash'
  cashoutForm.receiving_institution_id = ''
  cashoutForm.receiving_institution_name = ''
  cashoutForm.receiving_institution_code = ''
  cashoutForm.account_number = ''
  cashoutForm.account_name = ''
  cashoutForm.bank_name = ''
  cashoutForm.note = ''
}

const closeCashoutModal = () => {
  showCashoutModal.value = false
  showConfirmStep.value = false
  resetCashoutForm()
}

const applyRecentShortcut = (recent) => {
  cashoutForm.destination_type = recent.method
  cashoutForm.receiving_institution_id = recent.receiving_institution_id
  cashoutForm.receiving_institution_name = recent.receiving_institution_name
  cashoutForm.receiving_institution_code = recent.receiving_institution_code
  cashoutForm.account_number = recent.account_number
  cashoutForm.account_name = recent.account_name
  cashoutForm.bank_name = recent.bank_name || ''
}

const matchesRecentDestination = () =>
  walletStore.recentCashOuts.slice(0, 4).some(
    (previous) =>
      previous.method === cashoutForm.destination_type &&
      String(previous.receiving_institution_id) === String(cashoutForm.receiving_institution_id) &&
      previous.account_number === cashoutForm.account_number &&
      previous.account_name === cashoutForm.account_name
  )

const buildCashoutPayload = () => ({
  amount: cashoutForm.amount,
  destination_type: cashoutForm.destination_type,
  receiving_institution_id: cashoutForm.receiving_institution_id,
  receiving_institution_name: cashoutForm.receiving_institution_name,
  receiving_institution_code: cashoutForm.receiving_institution_code,
  account_number: cashoutForm.account_number,
  account_name: cashoutForm.account_name,
  bank_name: cashoutForm.bank_name,
  note: cashoutForm.note,
})

const submitCashout = async (confirmNewDestination = false) => {
  isSubmitting.value = true
  try {
    await walletStore.requestWithdrawal({
      ...buildCashoutPayload(),
      confirm_new_destination: confirmNewDestination,
    })
    toastStore.push('Cash-out request submitted.')
    closeCashoutModal()
  } catch (error) {
    if (error.response?.status === 409 && error.response?.data?.error === 'new_destination_confirmation_required') {
      showConfirmStep.value = true
    } else {
      toastStore.push(error.response?.data?.error || 'Unable to submit cash-out request.', 'error')
    }
  } finally {
    isSubmitting.value = false
  }
}

const handleCashout = async () => {
  if (!canSubmitCashout.value) {
    toastStore.push(cashoutError.value, 'error')
    return
  }

  const institution = walletStore.receivingInstitutions.find(
    (item) => String(institutionId(item)) === String(cashoutForm.receiving_institution_id)
  )
  if (institution) {
    cashoutForm.receiving_institution_name = institutionName(institution)
    cashoutForm.receiving_institution_code = institutionCode(institution)
  }

  if (matchesRecentDestination()) {
    await submitCashout(false)
  } else {
    showConfirmStep.value = true
  }
}

const addDevFunds = async () => {
  await walletStore.devAddFunds(devAmount.value)
  await refreshData()
}

const removeDevFunds = async () => {
  await walletStore.devRemoveFunds(devAmount.value)
  await refreshData()
}

const formatDate = (dateStr) =>
  new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })

const transactionIcon = (type) => {
  const icons = {
    session_credit: 'bi bi-mortarboard',
    withdrawal: 'bi bi-send',
    withdrawal_reversal: 'bi bi-arrow-counterclockwise',
    cashout_fee: 'bi bi-receipt',
    cashout_fee_reversal: 'bi bi-arrow-counterclockwise',
    commission_deduction: 'bi bi-bank',
    cash_in: 'bi bi-plus-circle',
  }
  return icons[type] || 'bi bi-wallet2'
}

const transactionTone = (type) => {
  const tones = {
    session_credit: 'tone-positive',
    withdrawal: 'tone-secondary',
    withdrawal_reversal: 'tone-warning',
    cashout_fee: 'tone-negative',
    cashout_fee_reversal: 'tone-warning',
    commission_deduction: 'tone-negative',
    cash_in: 'tone-positive',
  }
  return tones[type] || 'tone-neutral'
}

const formatType = (type) =>
  String(type || '')
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')

const getWithdrawalStatusClass = (status) => {
  const classes = {
    pending: 'cashout-status status-pending',
    processed: 'cashout-status status-processed',
    rejected: 'cashout-status status-rejected',
    failed: 'cashout-status status-failed',
    flagged: 'cashout-status status-flagged',
  }
  return classes[status] || 'cashout-status'
}

onMounted(async () => {
  await Promise.allSettled([
    refreshData(),
    walletStore.fetchReceivingInstitutions(),
  ])

  if (route.query.cashin === 'success' && route.query.id) {
    try {
      await walletStore.verifyCashIn(route.query.id)
      toastStore.push('Wallet topped up successfully.', 'success')
    } catch {
      toastStore.push(
        'We could not confirm your top-up. Refresh to check your balance.',
        'error'
      )
    } finally {
      router.replace({ query: {} })
    }
  } else if (route.query.cashin === 'cancelled') {
    toastStore.push('Cash-in cancelled.', 'info')
    router.replace({ query: {} })
  }
})

watch(showCashoutModal, async (isOpen) => {
  if (!isOpen) return
  await Promise.all([refreshData(), walletStore.fetchRecentCashOuts()])
  if (!cashoutForm.amount) {
    cashoutForm.amount = walletStore.cashoutMinimum
  }
})
</script>

<style scoped>
.wallet-shell {
  --wallet-primary: #00895a;
  --wallet-primary-hover: #00704a;
  --wallet-ink: #0f172a;
  --wallet-muted: #475569;
  --wallet-canvas: #f8fafc;
  --wallet-glass: rgba(255, 255, 255, 0.64);
  --wallet-glass-strong: rgba(255, 255, 255, 0.86);
  position: relative;
  isolation: isolate;
  min-height: calc(100vh - 7rem);
  padding: 4px;
  color: var(--wallet-ink);
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.wallet-shell::before {
  content: '';
  position: absolute;
  inset: -48px;
  z-index: -3;
  border-radius: 36px;
  background:
    radial-gradient(circle at 0% 0%, rgba(16, 185, 129, 0.32), transparent 38%),
    radial-gradient(circle at 96% 6%, rgba(139, 92, 246, 0.2), transparent 36%),
    radial-gradient(circle at 88% 74%, rgba(14, 165, 233, 0.18), transparent 42%),
    linear-gradient(135deg, #f8fafc 0%, #f5fbf4 100%);
}

.wallet-aurora {
  position: absolute;
  z-index: -2;
  width: 280px;
  height: 280px;
  border-radius: 999px;
  opacity: 0.45;
  pointer-events: none;
}

.wallet-aurora-one {
  top: 20px;
  left: 8%;
  background: rgba(16, 185, 129, 0.4);
}

.wallet-aurora-two {
  top: 140px;
  right: 10%;
  background: rgba(14, 165, 233, 0.25);
}

.wallet-aurora-three {
  bottom: 80px;
  left: 38%;
  background: rgba(139, 92, 246, 0.15);
}

.wallet-grid {
  display: grid;
  gap: 24px;
  margin-bottom: 24px;
}

.wallet-top-grid {
  grid-template-columns: minmax(0, 2fr) minmax(300px, 1fr);
}

.wallet-main-grid {
  grid-template-columns: minmax(0, 2fr) minmax(320px, 1fr);
  align-items: start;
}

.wallet-history-grid {
  grid-template-columns: 1fr;
}

.glass-panel {
  background: var(--wallet-glass);
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 24px;
  box-shadow: 0 12px 48px rgba(15, 23, 42, 0.06);
}

.performance-card {
  display: grid;
  grid-template-columns: 210px minmax(0, 1fr);
  align-items: center;
  gap: 28px;
  padding: 32px;
}

.ring-wrap {
  position: relative;
  width: 190px;
  height: 190px;
  display: grid;
  place-items: center;
}

.progress-rings {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.ring-base,
.ring-progress {
  fill: none;
  stroke-width: 10;
}

.ring-base {
  stroke: rgba(0, 137, 90, 0.11);
}

.ring-base-inner {
  stroke: rgba(0, 101, 145, 0.12);
}

.ring-progress {
  stroke-linecap: round;
  stroke-dasharray: 100;
  transition: stroke-dashoffset 900ms var(--sb-spring);
}

.ring-primary {
  stroke: var(--wallet-primary);
}

.ring-secondary {
  stroke: #006591;
}

.ring-center {
  position: absolute;
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  color: var(--wallet-primary);
  background: rgba(255, 255, 255, 0.74);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.9);
  font-size: 24px;
}

.eyebrow {
  display: inline-flex;
  color: var(--wallet-primary);
  font-size: 11px;
  font-weight: 800;
  line-height: 1;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.performance-copy h3,
.section-header h3 {
  margin: 8px 0 0;
  color: var(--wallet-ink);
  font-size: 24px;
  font-weight: 800;
  line-height: 1.25;
  letter-spacing: 0;
}

.performance-copy > p {
  max-width: 620px;
  margin: 10px 0 0;
  color: var(--wallet-muted);
  font-size: 14px;
  line-height: 1.55;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-top: 24px;
}

.metric-item {
  display: flex;
  gap: 12px;
  align-items: center;
}

.metric-dot {
  width: 11px;
  height: 11px;
  border-radius: 999px;
  flex: 0 0 auto;
}

.metric-dot-primary {
  background: var(--wallet-primary);
}

.metric-dot-secondary {
  background: #006591;
}

.metric-item p {
  margin: 0 0 4px;
  color: var(--wallet-muted);
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.metric-item strong {
  color: var(--wallet-primary);
  font-size: 22px;
  line-height: 1.1;
}

.ledger-note {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 24px;
  padding: 12px 14px;
  color: #005234;
  background: rgba(0, 137, 90, 0.08);
  border: 1px solid rgba(0, 137, 90, 0.12);
  border-radius: 16px;
  font-size: 12px;
  line-height: 1.45;
}

.balance-card {
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 260px;
  padding: 32px;
  background: linear-gradient(135deg, #006a44 0%, var(--wallet-primary) 100%);
  color: #fff;
}

.balance-card::after {
  content: '';
  position: absolute;
  top: -72px;
  right: -72px;
  width: 210px;
  height: 210px;
  border-radius: 999px;
  background: rgba(140, 248, 191, 0.28);
  transition: transform var(--sb-t-normal) var(--sb-spring);
}

.balance-card:hover::after {
  transform: scale(1.15);
}

.balance-card > * {
  position: relative;
  z-index: 1;
}

.balance-eyebrow {
  color: rgba(255, 255, 255, 0.72);
}

.balance-card h2 {
  margin: 10px 0 8px;
  font-size: 42px;
  font-weight: 900;
  line-height: 1.05;
  letter-spacing: 0;
}

.balance-card p {
  margin: 0;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
}

.balance-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-top: 32px;
}

.balance-cashout-btn,
.balance-refresh-btn,
.modal-primary,
.modal-secondary,
.section-action,
.dev-actions button {
  border: 0;
  user-select: none;
}

.balance-cashout-btn {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 13px 16px;
  border-radius: 14px;
  color: var(--wallet-primary);
  background: #fff;
  font-weight: 800;
}

.balance-refresh-btn {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  color: #fff;
  background: rgba(255, 255, 255, 0.16);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 28px 30px 20px;
}

.section-action {
  color: var(--wallet-primary);
  background: rgba(0, 137, 90, 0.1);
  border: 1px solid rgba(0, 137, 90, 0.14);
  border-radius: 999px;
  font-size: 13px;
  font-weight: 800;
  padding: 9px 16px;
}

.activity-card,
.cashout-history-card {
  overflow: hidden;
}

.activity-list,
.cashout-list {
  display: grid;
}

.activity-row,
.cashout-row {
  display: flex;
  gap: 16px;
  align-items: center;
  min-width: 0;
  padding: 18px 30px;
  border-top: 1px solid rgba(15, 23, 42, 0.06);
}

.activity-icon {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  font-size: 20px;
}

.activity-body {
  min-width: 0;
  flex: 1;
}

.activity-title-line {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-start;
}

.activity-title-line h4 {
  margin: 0;
  color: var(--wallet-ink);
  font-size: 14px;
  font-weight: 800;
  line-height: 1.35;
}

.activity-title-line strong {
  white-space: nowrap;
  font-size: 14px;
}

.amount-positive {
  color: var(--wallet-primary);
}

.amount-negative {
  color: #9a3e3e;
}

.activity-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin-top: 8px;
  color: var(--wallet-muted);
  font-size: 12px;
}

.type-chip {
  display: inline-flex;
  align-items: center;
  min-height: 20px;
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.tone-positive {
  color: var(--wallet-primary);
  background: rgba(0, 137, 90, 0.1);
}

.tone-secondary {
  color: #006591;
  background: rgba(0, 101, 145, 0.1);
}

.tone-negative {
  color: #9a3e3e;
  background: rgba(154, 62, 62, 0.1);
}

.tone-warning {
  color: #946200;
  background: rgba(255, 193, 7, 0.16);
}

.tone-neutral {
  color: var(--wallet-muted);
  background: rgba(71, 85, 105, 0.1);
}

.cashout-status {
  display: inline-flex;
  align-items: center;
  min-height: 22px;
  padding: 5px 9px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.status-processed {
  color: var(--wallet-primary);
  background: rgba(0, 137, 90, 0.1);
}

.status-rejected {
  color: #64748b;
  background: rgba(100, 116, 139, 0.12);
}

.status-pending {
  color: #946200;
  background: rgba(255, 193, 7, 0.16);
}

.status-failed {
  color: #9a3e3e;
  background: rgba(154, 62, 62, 0.12);
}

.status-flagged {
  color: #006591;
  background: rgba(0, 101, 145, 0.1);
}

.empty-state {
  display: grid;
  place-items: center;
  gap: 10px;
  padding: 48px 24px;
  color: var(--wallet-muted);
  text-align: center;
}

.empty-state i {
  font-size: 32px;
  color: var(--wallet-primary);
}

.compact-empty {
  padding: 28px 24px;
}

.history-summary {
  color: var(--wallet-muted);
  font-size: 12px;
  font-weight: 700;
}

.cashout-row {
  justify-content: space-between;
  align-items: flex-start;
}

.cashout-row p,
.cashout-row small {
  display: block;
  margin: 6px 0 0;
  color: var(--wallet-muted);
  font-size: 12px;
}

.cashout-title {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.cashout-title strong {
  color: var(--wallet-ink);
  font-size: 14px;
}

.failure-text {
  color: #9a3e3e !important;
}

.cashout-amount {
  display: grid;
  gap: 4px;
  justify-items: end;
  color: var(--wallet-muted);
  font-size: 12px;
  text-align: right;
  white-space: nowrap;
}

.cashout-amount strong {
  color: #9a3e3e;
  font-size: 14px;
}

.dev-tools-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-top: 24px;
  padding: 16px 18px;
  border: 1px dashed rgba(180, 83, 9, 0.24);
}

.dev-label {
  display: flex;
  gap: 12px;
  align-items: center;
}

.dev-label > span {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  color: #92400e;
  background: #fef3c7;
}

.dev-label strong {
  color: #92400e;
}

.dev-label p {
  margin: 2px 0 0;
  color: #a16207;
  font-size: 12px;
}

.dev-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.dev-actions input {
  width: 120px;
  border: 1px solid rgba(180, 83, 9, 0.18);
  border-radius: 12px;
  padding: 9px 10px;
  background: rgba(255, 255, 255, 0.6);
}

.dev-actions button {
  padding: 9px 14px;
  border-radius: 12px;
  color: #fff;
  background: #d97706;
  font-size: 12px;
  font-weight: 800;
}

.dev-actions button.secondary {
  color: #b45309;
  background: rgba(255, 255, 255, 0.56);
  border: 1px solid rgba(180, 83, 9, 0.2);
}

.wallet-modal {
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.86);
  box-shadow: 0 24px 80px rgba(15, 23, 42, 0.18);
}

.wallet-modal .modal-header,
.wallet-modal .modal-body,
.wallet-modal .modal-footer {
  padding-left: 24px;
  padding-right: 24px;
}

.wallet-modal .modal-title {
  margin-top: 6px;
  color: var(--wallet-ink);
  font-size: 22px;
  font-weight: 900;
}

.wallet-modal label {
  display: grid;
  gap: 7px;
  margin-bottom: 14px;
  color: var(--wallet-muted);
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.wallet-modal input,
.wallet-modal select,
.wallet-modal :deep(.wallet-select-trigger) {
  width: 100%;
  min-height: 44px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 14px;
  padding: 9px 12px;
  color: var(--wallet-ink);
  background: rgba(255, 255, 255, 0.72);
  font-size: 14px;
  font-weight: 600;
  text-transform: none;
  letter-spacing: 0;
}

.wallet-modal :deep(.wallet-select-trigger) {
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  text-align: left;
}

.modal-primary,
.modal-secondary {
  min-height: 42px;
  padding: 10px 18px;
  border-radius: 14px;
  font-size: 13px;
  font-weight: 900;
}

.modal-primary {
  color: #fff;
  background: var(--wallet-primary);
}

.modal-secondary {
  color: var(--wallet-ink);
  background: rgba(255, 255, 255, 0.7);
}

.cashout-summary {
  display: grid;
  gap: 9px;
  margin-top: 8px;
  padding: 14px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.52);
}

.cashout-summary div {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  font-size: 13px;
}

.cashout-summary span {
  color: var(--wallet-muted);
}

.form-error {
  margin: 12px 0 0;
  color: #9a3e3e;
  font-size: 13px;
}

.field-hint {
  color: var(--wallet-muted);
  font-size: 11px;
  font-weight: 600;
  text-transform: none;
  letter-spacing: 0;
}

.recent-shortcuts {
  display: grid;
  gap: 8px;
  margin-bottom: 16px;
}

.recent-shortcut-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
}

.recent-shortcut-card {
  display: grid;
  gap: 4px;
  padding: 10px 12px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.6);
  text-align: left;
}

.recent-shortcut-card strong {
  color: var(--wallet-ink);
  font-size: 13px;
  font-weight: 800;
}

.recent-shortcut-card code {
  color: var(--wallet-muted);
  font-size: 12px;
}

.recent-shortcut-card small {
  color: var(--wallet-muted);
  font-size: 11px;
}

.confirm-summary {
  display: grid;
  gap: 9px;
  padding: 14px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.52);
}

.confirm-lead {
  margin: 0 0 4px;
  color: var(--wallet-muted);
  font-size: 13px;
  line-height: 1.5;
}

.confirm-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  font-size: 13px;
}

.confirm-row span {
  color: var(--wallet-muted);
}

.spin {
  animation: rotation 1s infinite linear;
}

.wallet-list-enter-active {
  animation: wallet-list-in var(--sb-t-normal) var(--sb-spring);
}

@keyframes wallet-list-in {
  from {
    opacity: 0;
    transform: translateY(12px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes rotation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(359deg);
  }
}

.modal-backdrop {
  z-index: 1050;
}

.modal {
  z-index: 1055;
}

@media (max-width: 1180px) {
  .wallet-top-grid,
  .wallet-main-grid {
    grid-template-columns: 1fr;
  }

  .balance-card {
    min-height: 220px;
  }
}

@media (max-width: 768px) {
  .wallet-shell {
    padding: 0;
  }

  .wallet-shell::before {
    inset: -24px;
    border-radius: 24px;
  }

  .performance-card {
    grid-template-columns: 1fr;
    justify-items: center;
    padding: 24px;
  }

  .performance-copy {
    width: 100%;
  }

  .metric-grid {
    grid-template-columns: 1fr;
  }

  .balance-card h2 {
    font-size: 34px;
  }

  .section-header,
  .activity-row,
  .cashout-row {
    padding-left: 20px;
    padding-right: 20px;
  }

  .activity-row,
  .cashout-row,
  .activity-title-line {
    align-items: flex-start;
    flex-direction: column;
  }

  .activity-title-line strong,
  .cashout-amount {
    text-align: left;
    justify-items: start;
    white-space: normal;
  }

  .dev-tools-card {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
