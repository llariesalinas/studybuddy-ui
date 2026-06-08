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

      <aside class="glass-panel destinations-card">
        <header class="section-header compact">
          <div>
            <span class="eyebrow">Payout</span>
            <h3>Destinations</h3>
          </div>
          <button
            class="icon-btn sb-btn"
            @click="openDestinationModal"
            aria-label="Add payout destination"
          >
            <i class="bi bi-plus-lg"></i>
          </button>
        </header>

        <div v-if="walletStore.payoutAccounts.length === 0" class="destination-empty">
          <i class="bi bi-credit-card-2-front"></i>
          <p>No payout destinations saved.</p>
        </div>

        <div v-else class="destination-list">
          <div
            v-for="account in walletStore.payoutAccounts"
            :key="account.id"
            class="destination-card sb-interactive"
            :class="{ inactive: !account.is_active }"
          >
            <div class="destination-icon">
              <i :class="account.destination_type === 'gcash' ? 'bi bi-phone' : 'bi bi-bank'"></i>
            </div>
            <div class="destination-content">
              <div class="destination-title">
                <strong>{{ account.receiving_institution_name }}</strong>
                <span :class="account.is_active ? 'status-pill active' : 'status-pill inactive'">
                  {{ account.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
              <p>{{ formatDestinationType(account.destination_type) }} · {{ account.provider || 'rail' }}</p>
              <code>{{ maskAccount(account.account_number) }}</code>
            </div>
            <button
              v-if="account.is_active"
              class="destination-action sb-btn"
              @click.stop="deactivateAccount(account.id)"
              aria-label="Deactivate payout destination"
            >
              <i class="bi bi-slash-circle"></i>
            </button>
          </div>
        </div>

        <button class="add-destination-card sb-btn" @click="openDestinationModal">
          <i class="bi bi-plus-circle"></i>
          Add New Destination
        </button>
      </aside>
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
                {{ maskAccount(cashout.account_number) }} ·
                {{ cashout.rail || 'rail pending' }}
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
        <input v-model.number="devAmount" type="number" min="1" aria-label="Dev amount" />
        <button class="sb-btn" @click="addDevFunds">Add Test Funds</button>
        <button class="sb-btn secondary" @click="removeDevFunds">Remove Funds</button>
      </div>
    </section>

    <div v-if="showDestinationModal" class="modal-backdrop fade show"></div>
    <div v-if="showDestinationModal" class="modal fade show d-block" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content wallet-modal">
          <div class="modal-header border-0">
            <div>
              <span class="eyebrow">Payout</span>
              <h5 class="modal-title">Add Destination</h5>
            </div>
            <button type="button" class="btn-close" @click="closeDestinationModal"></button>
          </div>
          <form @submit.prevent="saveAccount">
            <div class="modal-body">
              <div class="form-grid">
                <label>
                  <span>Rail</span>
                  <SbSelectModal
                    v-model="accountForm.provider"
                    :options="providerOptions"
                    title="Rail"
                    placeholder="Select rail"
                    trigger-class="wallet-select-trigger"
                  />
                </label>
                <label>
                  <span>Type</span>
                  <SbSelectModal
                    v-model="accountForm.destination_type"
                    :options="destinationTypeOptions"
                    title="Destination Type"
                    placeholder="Select type"
                    trigger-class="wallet-select-trigger"
                  />
                </label>
              </div>

              <label>
                <span>Receiving Institution</span>
                <SbSelectModal
                  v-model="accountForm.receiving_institution_id"
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
                <input v-model.trim="accountForm.account_number" required />
              </label>

              <label>
                <span>Account Name</span>
                <input v-model.trim="accountForm.account_name" required />
              </label>
            </div>
            <div class="modal-footer border-0">
              <button type="button" class="modal-secondary sb-btn" @click="closeDestinationModal">
                Cancel
              </button>
              <button class="modal-primary sb-btn" :disabled="savingAccount">
                {{ savingAccount ? 'Saving...' : 'Save Destination' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <div v-if="showCashoutModal" class="modal-backdrop fade show"></div>
    <div v-if="showCashoutModal" class="modal fade show d-block" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content wallet-modal">
          <div class="modal-header border-0">
            <div>
              <span class="eyebrow">Wallet</span>
              <h5 class="modal-title">Cash Out</h5>
            </div>
            <button type="button" class="btn-close" @click="showCashoutModal = false"></button>
          </div>
          <form @submit.prevent="handleCashout">
            <div class="modal-body">
              <label>
                <span>Destination</span>
                <SbSelectModal
                  v-model="cashoutForm.payout_account_id"
                  :options="payoutAccountOptions"
                  title="Destination"
                  placeholder="Select saved destination"
                  :clearable="true"
                  :searchable="true"
                  trigger-class="wallet-select-trigger"
                />
              </label>

              <label>
                <span>Amount You Receive</span>
                <input
                  v-model.number="cashoutForm.amount"
                  type="number"
                  step="0.01"
                  :min="walletStore.cashoutMinimum"
                  required
                />
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
                <div>
                  <span>Rail</span>
                  <strong>{{ cashoutRail }}</strong>
                </div>
              </div>

              <p v-if="cashoutError" class="form-error">{{ cashoutError }}</p>
            </div>
            <div class="modal-footer border-0">
              <button type="button" class="modal-secondary sb-btn" @click="showCashoutModal = false">
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
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import SbSelectModal from '@/components/SbSelectModal.vue'
import { useWalletStore } from '@/stores/wallet'
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()
const walletStore = useWalletStore()
const showCashoutModal = ref(false)
const showDestinationModal = ref(false)
const isSubmitting = ref(false)
const savingAccount = ref(false)
const isDev = import.meta.env.DEV
const devAmount = ref(500)

const accountForm = reactive({
  provider: 'instapay',
  destination_type: 'gcash',
  receiving_institution_id: '',
  account_number: '',
  account_name: '',
})

const cashoutForm = reactive({
  amount: 0,
  payout_account_id: null,
})

const providerOptions = [
  { label: 'InstaPay', value: 'instapay' },
  { label: 'PESONet', value: 'pesonet' },
]

const destinationTypeOptions = [
  { label: 'GCash', value: 'gcash' },
  { label: 'Bank', value: 'bank' },
]

const activePayoutAccounts = computed(() =>
  walletStore.payoutAccounts.filter((account) => account.is_active)
)

const cashoutAmount = computed(() => Number(cashoutForm.amount) || 0)
const totalDeducted = computed(() => cashoutAmount.value + Number(walletStore.cashoutProviderFee || 0))
const cashoutRail = computed(() => (cashoutAmount.value > 50000 ? 'pesonet' : 'instapay'))
const selectedPayoutAccountId = computed(() =>
  cashoutForm.payout_account_id === null || cashoutForm.payout_account_id === ''
    ? null
    : Number(cashoutForm.payout_account_id)
)
const selectedCashoutAccount = computed(() =>
  activePayoutAccounts.value.find((account) => Number(account.id) === selectedPayoutAccountId.value)
)

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
  if (!activePayoutAccounts.value.length) return 'Add an active payout destination before cashing out.'
  if (!selectedCashoutAccount.value) return 'Select a payout destination.'
  if (cashoutAmount.value < Number(walletStore.cashoutMinimum)) {
    return `Minimum cash-out is PHP ${money(walletStore.cashoutMinimum)}.`
  }
  if (totalDeducted.value > Number(walletStore.balance || 0)) {
    return 'Balance must cover the amount plus provider fee.'
  }
  if (
    selectedCashoutAccount.value.provider &&
    selectedCashoutAccount.value.provider !== cashoutRail.value
  ) {
    return `Use a ${cashoutRail.value} destination for this amount.`
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
    walletStore.fetchPayoutAccounts(),
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
  }))
)

const payoutAccountOptions = computed(() =>
  activePayoutAccounts.value.map((account) => ({
    label: `${account.receiving_institution_name} · ${maskAccount(account.account_number)}`,
    value: Number(account.id),
    description: formatDestinationType(account.destination_type),
  }))
)

const formatDestinationType = (type) => (type === 'gcash' ? 'GCash' : 'Bank Transfer')

const maskAccount = (value = '') => {
  const account = String(value)
  if (account.length <= 4) return account || '-'
  return `${account.slice(0, 4)} •••• ${account.slice(-3)}`
}

const resetAccountForm = () => {
  accountForm.provider = 'instapay'
  accountForm.destination_type = 'gcash'
  accountForm.receiving_institution_id = ''
  accountForm.account_number = ''
  accountForm.account_name = ''
}

const openDestinationModal = async () => {
  showDestinationModal.value = true
  await walletStore.fetchReceivingInstitutions(accountForm.provider)
}

const closeDestinationModal = () => {
  showDestinationModal.value = false
  resetAccountForm()
}

const saveAccount = async () => {
  const institution = walletStore.receivingInstitutions.find(
    (item) => String(institutionId(item)) === String(accountForm.receiving_institution_id)
  )

  if (!institution) {
    toastStore.push('Select a receiving institution.', 'warning')
    return
  }

  savingAccount.value = true
  try {
    await walletStore.savePayoutAccount({
      ...accountForm,
      receiving_institution_name: institutionName(institution),
      receiving_institution_code: institutionCode(institution),
      bank_name: accountForm.destination_type === 'bank' ? institutionName(institution) : '',
    })
    closeDestinationModal()
  } catch (error) {
    toastStore.push(error.response?.data?.error || 'Unable to save payout destination.', 'error')
  } finally {
    savingAccount.value = false
  }
}

const deactivateAccount = async (id) => {
  if (!confirm('Deactivate this payout destination?')) return
  await walletStore.deactivatePayoutAccount(id)
}

const handleCashout = async () => {
  if (!selectedPayoutAccountId.value) {
    toastStore.push('Select a payout destination.', 'error')
    return
  }

  if (!canSubmitCashout.value) {
    toastStore.push(cashoutError.value, 'error')
    return
  }

  isSubmitting.value = true
  const result = await walletStore.requestWithdrawal({
    amount: cashoutForm.amount,
    payout_account_id: selectedPayoutAccountId.value,
  })
  isSubmitting.value = false

  if (result.success) {
    toastStore.push('Cash-out request submitted.')
    showCashoutModal.value = false
    cashoutForm.amount = 0
    cashoutForm.payout_account_id = null
  } else {
    toastStore.push(result.error, 'error')
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
    walletStore.fetchReceivingInstitutions(accountForm.provider),
  ])
})

watch(
  () => accountForm.provider,
  async (provider) => {
    accountForm.receiving_institution_id = ''
    if (showDestinationModal.value) {
      await walletStore.fetchReceivingInstitutions(provider)
    }
  }
)

watch(showCashoutModal, async (isOpen) => {
  if (!isOpen) return
  await refreshData()
  if (activePayoutAccounts.value.length && !cashoutForm.payout_account_id) {
    cashoutForm.payout_account_id = Number(activePayoutAccounts.value[0].id)
  }
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
  box-shadow: 0 18px 60px rgba(15, 23, 42, 0.08);
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
  background: radial-gradient(circle, rgba(140, 248, 191, 0.28), rgba(140, 248, 191, 0));
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
.icon-btn,
.destination-action,
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

.section-header.compact {
  padding: 0;
}

.section-action,
.icon-btn {
  color: var(--wallet-primary);
  background: rgba(0, 137, 90, 0.1);
  border: 1px solid rgba(0, 137, 90, 0.14);
  border-radius: 999px;
  font-size: 13px;
  font-weight: 800;
}

.section-action {
  padding: 9px 16px;
}

.icon-btn {
  width: 36px;
  height: 36px;
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

.activity-icon,
.destination-icon {
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

.destinations-card {
  display: grid;
  gap: 20px;
  padding: 26px;
}

.destination-list {
  display: grid;
  gap: 12px;
}

.destination-card {
  position: relative;
  display: grid;
  grid-template-columns: 44px minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  padding: 14px;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.62);
  background: rgba(255, 255, 255, 0.5);
}

.destination-card.inactive {
  opacity: 0.58;
}

.destination-icon {
  width: 44px;
  height: 44px;
  color: #fff;
  background: var(--wallet-primary);
}

.destination-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.destination-title strong {
  min-width: 0;
  color: var(--wallet-ink);
  font-size: 14px;
}

.destination-content {
  min-width: 0;
}

.destination-content p,
.destination-content code {
  display: block;
  margin: 4px 0 0;
  color: var(--wallet-muted);
  font-size: 12px;
}

.status-pill,
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

.status-pill.active,
.status-processed {
  color: var(--wallet-primary);
  background: rgba(0, 137, 90, 0.1);
}

.status-pill.inactive,
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

.destination-action {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  color: #9a3e3e;
  background: rgba(154, 62, 62, 0.08);
}

.add-destination-card {
  display: flex;
  min-height: 96px;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border: 1px dashed rgba(15, 23, 42, 0.22);
  border-radius: 18px;
  color: var(--wallet-muted);
  background: rgba(255, 255, 255, 0.2);
  font-size: 13px;
  font-weight: 800;
}

.destination-empty,
.empty-state {
  display: grid;
  place-items: center;
  gap: 10px;
  padding: 48px 24px;
  color: var(--wallet-muted);
  text-align: center;
}

.destination-empty i,
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

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
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

  .metric-grid,
  .form-grid {
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

  .destination-card {
    grid-template-columns: 44px minmax(0, 1fr);
  }

  .destination-action {
    grid-column: 2;
    justify-self: start;
  }

  .dev-tools-card {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
