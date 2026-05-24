<!-- src/views/TutorWallet.vue -->
<template>
  <div class="container-fluid p-0">
    <div class="row g-4">
      <!-- Balance Card -->
      <div class="col-12 col-lg-5">
        <div class="wallet-card p-4 rounded-4 shadow-sm h-100">
          <div class="d-flex justify-content-between align-items-start mb-4">
            <div>
              <p class="text-white-50 mb-1">Available Balance</p>
              <h1 class="display-5 fw-bold text-white mb-0">₱ {{ walletStore.balance.toLocaleString() }}</h1>
              <p class="text-white-50 mt-2 small" v-if="walletStore.pendingAmount > 0">
                <i class="bi bi-clock-history me-1"></i> ₱ {{ walletStore.pendingAmount.toLocaleString() }} pending verification
              </p>
            </div>
            <div class="wallet-icon-bg">
              <i class="bi bi-wallet2 fs-3 text-white"></i>
            </div>
          </div>
          
          <div class="d-flex gap-2">
            <button @click="showWithdrawModal = true" class="btn btn-light fw-bold flex-grow-1 py-2 rounded-3 sb-btn">
              Withdraw Funds
            </button>
            <button @click="refreshData" class="btn btn-outline-light py-2 rounded-3 sb-btn" :disabled="walletStore.loading">
              <i class="bi bi-arrow-clockwise" :class="{'spin': walletStore.loading}"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- Earnings Breakdown -->
      <div class="col-12 col-lg-7">
        <div class="card border-0 rounded-4 shadow-sm p-4 h-100">
          <h5 class="fw-bold mb-3">Earnings Breakdown</h5>
          <div class="row g-3 mb-3">
            <div class="col-4">
              <div class="p-3 rounded-3 bg-light border-start border-3 border-secondary h-100">
                <p class="text-muted small mb-1">Gross Earned</p>
                <p class="fw-bold mb-0">₱ {{ walletStore.grossEarned.toLocaleString() }}</p>
              </div>
            </div>
            <div class="col-4">
              <div class="p-3 rounded-3 bg-light border-start border-3 border-danger h-100">
                <p class="text-muted small mb-1">Deducted (10%)</p>
                <p class="fw-bold text-danger mb-0">- ₱ {{ walletStore.totalDeductions.toLocaleString() }}</p>
              </div>
            </div>
            <div class="col-4">
              <div class="p-3 rounded-3 bg-light border-start border-3 border-success h-100">
                <p class="text-muted small mb-1">Net Gained</p>
                <p class="fw-bold text-sb-primary mb-0">₱ {{ walletStore.netEarned.toLocaleString() }}</p>
              </div>
            </div>
          </div>
          <div class="alert alert-info border-0 rounded-3 small mb-0">
            <i class="bi bi-info-circle-fill me-2"></i>
            Online payments are automatically credited minus the platform commission (10%). Cash payments must be verified manually and do not affect your wallet balance.
          </div>
          <div class="mt-3">
            <p class="text-muted small mb-0">Minimum withdrawal: ₱ 500.00</p>
          </div>
        </div>
      </div>

      <!-- Transaction History -->
      <div class="col-12">
        <div class="card border-0 rounded-4 shadow-sm overflow-hidden">
          <div class="card-header bg-white border-0 p-4 pb-2">
            <h5 class="fw-bold mb-0">Recent Transactions</h5>
          </div>
          <div class="p-4 pt-3">
            <div v-if="walletStore.transactions.length === 0" class="text-center py-5 text-muted">
              No transactions found.
            </div>
            <div v-else class="tx-card-list">
              <div
                v-for="tx in walletStore.transactions"
                :key="tx.id"
                class="tx-card"
              >
                <!-- Date block -->
                <div class="tx-date-block">
                  <span class="tx-month">{{ formatMonth(tx.created_at) }}</span>
                  <span class="tx-day">{{ formatDay(tx.created_at) }}</span>
                </div>

                <!-- Session info -->
                <div class="tx-info">
                  <div class="fw-semibold text-dark">{{ tx.description }}</div>
                  <span :class="getTypeBadgeClass(tx.transaction_type)" class="tx-type-badge mt-1">
                    {{ formatType(tx.transaction_type) }}
                  </span>
                  <div
                    v-if="tx.student_name"
                    class="text-muted mt-1"
                    style="font-size:11px;"
                  >
                    Student: {{ tx.student_name }}
                  </div>
                  <div v-if="tx.reference_id" class="text-muted mt-1" style="font-size:11px;">
                    Ledger Ref: {{ tx.reference_id }}
                  </div>
                </div>

                <!-- Breakdown panels (fixed-width wrapper keeps tx-info consistent) -->
                <div class="tx-breakdown-wrapper">
                  <template v-if="tx.transaction_type === 'session_credit'">
                    <div class="tx-breakdown-item tx-gross">
                      <span class="tx-bl">Gross</span>
                      <span class="tx-bv">₱ {{ grossForCredit(tx).toLocaleString() }}</span>
                    </div>
                    <div class="tx-breakdown-item tx-deduct">
                      <span class="tx-bl">Deducted</span>
                      <span class="tx-bv">-₱ {{ deductForCredit(tx).toLocaleString() }}</span>
                    </div>
                    <div class="tx-breakdown-item tx-net">
                      <span class="tx-bl">Net Earned</span>
                      <span class="tx-bv">₱ {{ Number(tx.amount).toLocaleString() }}</span>
                    </div>
                  </template>
                  <template v-else>
                    <div class="tx-breakdown-item tx-net tx-single">
                      <span class="tx-bl">Amount</span>
                      <span class="tx-bv" :class="tx.amount < 0 ? 'text-danger' : ''">
                        {{ tx.amount > 0 ? '+' : '' }}₱ {{ Math.abs(Number(tx.amount)).toLocaleString() }}
                      </span>
                    </div>
                  </template>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Dev Tools (dev server only) -->
      <div v-if="isDev" class="col-12">
        <div class="card border-warning border-2 rounded-4 p-4">
          <h6 class="fw-bold text-warning mb-3">Dev Tools — not visible in production</h6>
          <div class="d-flex flex-wrap gap-2 align-items-center">
            <span class="input-group-text bg-light border-0">₱</span>
            <input v-model.number="devAmount" type="number" min="1" class="form-control bg-light border-0" style="max-width:140px" />
            <button @click="addDevFunds" class="btn btn-warning fw-bold px-4 sb-btn">Add Funds</button>
            <button @click="removeDevFunds" class="btn btn-outline-danger fw-bold px-4 sb-btn">Remove Funds</button>
          </div>
        </div>
      </div>

      <!-- Withdrawal History -->
      <div class="col-12">
        <div class="card border-0 rounded-4 shadow-sm overflow-hidden">
          <div class="card-header bg-white border-0 p-4">
            <h5 class="fw-bold mb-0">Withdrawal History</h5>
          </div>
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="bg-light text-muted small text-uppercase">
                <tr>
                  <th class="px-4 border-0">Amount</th>
                  <th class="border-0">Method</th>
                  <th class="border-0">Account</th>
                  <th class="border-0">Date</th>
                  <th class="px-4 border-0 text-end">Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="w in walletStore.withdrawals" :key="w.id">
                  <td class="px-4 fw-bold text-danger">-₱ {{ Number(w.amount).toLocaleString() }}</td>
                  <td class="text-capitalize">{{ w.method === 'gcash' ? 'GCash' : 'Bank Transfer' }}</td>
                  <td>
                    <div class="fw-semibold">{{ w.account_name }}</div>
                    <div class="text-muted small">{{ w.account_number }}</div>
                  </td>
                  <td class="text-muted small">{{ new Date(w.requested_at).toLocaleDateString() }}</td>
                  <td class="px-4 text-end">
                    <span :class="getWithdrawalStatusClass(w.status)">{{ w.status }}</span>
                  </td>
                </tr>
                <tr v-if="walletStore.withdrawals.length === 0">
                  <td colspan="5" class="text-center py-5 text-muted">No withdrawal requests yet.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Withdraw Modal (Using a simple v-if for control) -->
    <div v-if="showWithdrawModal" class="modal-backdrop fade show"></div>
    <div v-if="showWithdrawModal" class="modal fade show d-block" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 rounded-4 shadow-lg">
          <div class="modal-header border-0 px-4 pt-4">
            <h5 class="modal-title fw-bold">Withdraw Funds</h5>
            <button type="button" class="btn-close" @click="showWithdrawModal = false"></button>
          </div>
          <form @submit.prevent="handleWithdraw">
            <div class="modal-body px-4">
              <div class="mb-3">
                <label class="form-label small fw-bold text-muted">Amount to Withdraw</label>
                <div class="input-group">
                  <span class="input-group-text bg-light border-0">₱</span>
                  <input v-model.number="withdrawForm.amount" type="number" step="0.01" class="form-control bg-light border-0" required :max="withdrawMax" :min="withdrawMin">
                </div>
                <div class="form-text text-end">Max: ₱ {{ walletStore.balance.toLocaleString() }}</div>
                <div v-if="withdrawForm.amount < 500" class="form-text text-danger">
                  Insufficient balance. Minimum withdrawal is ₱ 500.00.
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label small fw-bold text-muted">Withdrawal Method</label>
                <div class="d-flex gap-3">
                  <div class="form-check">
                    <input v-model="withdrawForm.method" class="form-check-input" type="radio" value="gcash" id="gcash">
                    <label class="form-check-label" for="gcash">GCash</label>
                  </div>
                  <div class="form-check">
                    <input v-model="withdrawForm.method" class="form-check-input" type="radio" value="bank" id="bank">
                    <label class="form-check-label" for="bank">Bank Transfer</label>
                  </div>
                </div>
              </div>

              <div class="mb-3" v-if="withdrawForm.method === 'bank'">
                <label class="form-label small fw-bold text-muted">Bank Name</label>
                <input v-model="withdrawForm.bank_name" type="text" class="form-control bg-light border-0" placeholder="e.g. BDO, BPI" required>
              </div>

              <div class="mb-3">
                <label class="form-label small fw-bold text-muted">Account Number</label>
                <input v-model="withdrawForm.account_number" type="text" class="form-control bg-light border-0" required>
              </div>

              <div class="mb-0">
                <label class="form-label small fw-bold text-muted">Account Name</label>
                <input v-model="withdrawForm.account_name" type="text" class="form-control bg-light border-0" required>
              </div>
            </div>
            <div class="modal-footer border-0 px-4 pb-4">
              <button type="button" class="btn btn-light rounded-3 px-4 sb-btn" @click="showWithdrawModal = false">Cancel</button>
              <button type="submit" class="btn bg-sb-primary text-white rounded-3 px-4 sb-btn" :disabled="isSubmitting || !canSubmitWithdrawal">
                {{ isSubmitting ? 'Processing...' : 'Confirm Withdrawal' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, reactive, watch } from 'vue'
import { useWalletStore } from '@/stores/wallet'

const walletStore = useWalletStore()
const showWithdrawModal = ref(false)
const isSubmitting = ref(false)
const isDev = import.meta.env.DEV
const devAmount = ref(500)

const addDevFunds = async () => {
  await walletStore.devAddFunds(devAmount.value)
  await refreshData()
}

const removeDevFunds = async () => {
  await walletStore.devRemoveFunds(devAmount.value)
  await refreshData()
}

const withdrawForm = reactive({
  amount: 0,
  method: 'gcash',
  account_number: '',
  account_name: '',
  bank_name: ''
})

const balanceValue = computed(() => Number(walletStore.balance) || 0)
const hasMinimumBalance = computed(() => balanceValue.value >= 500)
const withdrawMax = computed(() => Math.max(balanceValue.value, 0))
const withdrawMin = computed(() => (hasMinimumBalance.value ? 500 : 0))
const canSubmitWithdrawal = computed(() => {
  const amount = Number(withdrawForm.amount) || 0

  if (amount < 500) {
    return false
  }

  return amount <= balanceValue.value
})

const refreshData = async () => {
  await Promise.all([
    walletStore.fetchWallet(),
    walletStore.fetchTransactions(),
    walletStore.fetchWithdrawals()
  ])
}

const handleWithdraw = async () => {
  if (!hasMinimumBalance.value) {
    return alert('Minimum withdrawal is ₱500')
  }
  if (withdrawForm.amount > balanceValue.value) return alert('Insufficient balance')
  if (withdrawForm.amount < 500) return alert('Minimum withdrawal is ₱500')
  
  isSubmitting.value = true
  const result = await walletStore.requestWithdrawal({ ...withdrawForm })
  isSubmitting.value = false
  
  if (result.success) {
    alert('Withdrawal request submitted successfully!')
    showWithdrawModal.value = false
    // Reset form
    withdrawForm.amount = 0
    withdrawForm.account_number = ''
    withdrawForm.account_name = ''
    withdrawForm.bank_name = ''
  } else {
    alert(result.error)
  }
}

const formatMonth = (dateStr) =>
  new Date(dateStr).toLocaleString('default', { month: 'short' }).toUpperCase()

const formatDay = (dateStr) =>
  new Date(dateStr).getDate()

const deductForCredit = (tx) => Math.round(Number(tx.amount) / 0.9 * 0.1)
const grossForCredit = (tx) => Number(tx.amount) + deductForCredit(tx)

const getTypeBadgeClass = (type) => {
  const classes = {
    'session_credit': 'badge bg-success-subtle text-success border border-success',
    'withdrawal': 'badge bg-primary-subtle text-primary border border-primary',
    'withdrawal_reversal': 'badge bg-warning-subtle text-warning border border-warning',
    'commission_deduction': 'badge bg-danger-subtle text-danger border border-danger'
  }
  return classes[type] || 'badge bg-secondary'
}

const formatType = (type) => {
  return type.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
}

const getWithdrawalStatusClass = (status) => {
  const classes = {
    'pending': 'badge bg-warning-subtle text-warning border border-warning',
    'processed': 'badge bg-success-subtle text-success border border-success',
    'rejected': 'badge bg-danger-subtle text-danger border border-danger'
  }
  return classes[status] || 'badge bg-secondary'
}

onMounted(() => {
  refreshData()
})

watch(showWithdrawModal, async (isOpen) => {
  if (isOpen) {
    await refreshData()
  }
})

watch([showWithdrawModal, balanceValue], () => {
  if (!showWithdrawModal.value) {
    return
  }

  if (!hasMinimumBalance.value) {
    withdrawForm.amount = 0
    return
  }

  if (withdrawForm.amount < 500) {
    withdrawForm.amount = Math.min(500, withdrawMax.value)
  }
})
</script>

<style scoped>
.wallet-card {
  background: linear-gradient(135deg, var(--sb-dark), var(--sb-primary));
  color: white;
}

.wallet-icon-bg {
  background: rgba(255, 255, 255, 0.1);
  padding: 1rem;
  border-radius: 1rem;
}

.spin {
  animation: rotation 1s infinite linear;
}

@keyframes rotation {
  from { transform: rotate(0deg); }
  to { transform: rotate(359deg); }
}

/* Transaction card rows */
.tx-card-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tx-card {
  display: flex;
  align-items: stretch;
  border: 1px solid #eee;
  border-radius: 12px;
  overflow: hidden;
  background: #fafafa;
}

.tx-date-block {
  background: var(--sb-dark);
  color: #fff;
  width: 68px;
  min-width: 68px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 14px 8px;
  text-align: center;
  flex-shrink: 0;
}

.tx-month {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1px;
  opacity: 0.65;
  line-height: 1;
}

.tx-day {
  font-size: 22px;
  font-weight: 700;
  line-height: 1.2;
}

.tx-info {
  flex: 1;
  padding: 12px 16px;
  border-right: 1px solid #eee;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
}

.tx-type-badge {
  align-self: flex-start;
  width: auto;
  max-width: 100%;
  padding: 3px 10px;
  font-size: 11px;
  font-weight: 600;
  line-height: 1.2;
  text-align: left;
  white-space: normal;
}

.tx-breakdown-wrapper {
  display: flex;
  align-items: stretch;
  width: 300px;
  flex-shrink: 0;
}

.tx-breakdown-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px 18px;
  border-right: 1px solid #eee;
  flex-shrink: 0;
}

.tx-breakdown-item:last-child {
  border-right: none;
}

.tx-bl {
  font-size: 11px;
  color: #aaa;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  margin-bottom: 3px;
  white-space: nowrap;
}

.tx-bv {
  font-weight: 700;
  font-size: 14px;
  white-space: nowrap;
}

.tx-single {
  flex: 1;
}

.tx-gross .tx-bv { color: #555; }
.tx-deduct .tx-bv { color: #dc3545; }
.tx-net .tx-bv { color: var(--sb-primary); font-size: 15px; }

.modal-backdrop {
  z-index: 1050;
}
.modal {
  z-index: 1055;
}
</style>
