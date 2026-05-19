<template>
  <div class="admin-withdrawals p-4">

    <!-- HEADER -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3 class="mb-0">Audit</h3>

      <div class="d-flex gap-2">

        <select
          v-model="statusFilter"
          @change="fetchWithdrawals"
          class="form-select form-select-sm rounded-pill"
          style="width: 150px;"
        >
          <option value="">All Transactions</option>
          <option value="pending">Pending</option>
          <option value="processed">Processed</option>
          <option value="failed">Failed</option>
          <option value="flagged">Flagged</option>
          <option value="rejected">Rejected</option>
        </select>

        <button
        @click="fetchWithdrawals(true)"
        :disabled="store.loading.withdrawals"
        class="btn bg-sb-primary text-white btn-sm rounded-pill ms-auto"
      >
        <span v-if="store.loading.withdrawals" class="spinner-border spinner-border-sm me-1" role="status"></span>
        <i v-else class="bi bi-arrow-clockwise me-1"></i>
        {{ store.loading.withdrawals ? 'Loading...' : 'Refresh Data' }}
      </button>

      </div>
    </div>

    <!-- EXCEPTION ALERTS -->
    <div
      v-if="!store.loading.withdrawals && exceptionWithdrawals.length"
      class="mb-5"
    >

      <h6 class="fw-bold text-danger mb-3 small text-uppercase">
        Exceptions Requiring Attention
      </h6>

      <div
        v-for="w in exceptionWithdrawals"
        :key="w.id"
        class="alert alert-danger border-0 shadow-sm rounded-4 p-3 mb-3 d-flex justify-content-between align-items-center"
      >

        <div class="d-flex align-items-center">

          <div class="icon-box bg-danger text-white rounded-circle me-3 p-2">
            <i :class="w.status === 'failed' ? 'bi bi-x-circle' : 'bi bi-flag'"></i>
          </div>

          <div>
            <p class="mb-0 fw-bold">
              ₱{{ w?.amount || 0 }}
              payout to
              {{ w?.tutor_name || 'Unknown' }}
              {{ w?.status === 'failed' ? 'FAILED' : 'FLAGGED' }}
            </p>

            <p class="small mb-0 text-danger-emphasis">
              Reason:
              {{ w?.failure_reason || 'Unknown technical error' }}
            </p>
          </div>

        </div>

        <button
          @click="openActionModal(w)"
          class="btn btn-sm btn-danger rounded-pill px-4"
        >
          Take Action
        </button>

      </div>
    </div>

    <!-- TABLE -->
    <Transition name="fade" mode="out-in">

      <!-- LOADING -->
      <div
        v-if="store.loading.withdrawals"
        class="card border-0 shadow-sm rounded-4 overflow-hidden"
      >

        <div class="table-responsive">

          <table class="table align-middle mb-0">

            <thead class="bg-light">
              <tr>
                <th class="ps-4 py-3">Tutor</th>
                <th class="py-3">Amount</th>
                <th class="py-3">Method</th>
                <th class="py-3">Account Details</th>
                <th class="py-3">Status</th>
                <th class="py-3">Date Requested</th>
                <th class="pe-4 py-3 text-end">Actions</th>
              </tr>
            </thead>

            <tbody class="placeholder-glow">

              <tr
                v-for="i in 5"
                :key="'withdrawal-skeleton-' + i"
              >

                <!-- Tutor -->
                <td class="ps-4">
                  <div class="d-flex align-items-center">

                    <div
                      class="placeholder rounded-circle me-3"
                      style="width: 36px; height: 36px;"
                    ></div>

                    <div class="flex-grow-1">
                      <p class="placeholder col-6 rounded mb-1"></p>
                      <p class="placeholder col-4 rounded mb-0 small"></p>
                    </div>

                  </div>
                </td>

                <!-- Amount -->
                <td>
                  <span class="placeholder col-6 rounded"></span>
                </td>

                <!-- Method -->
                <td>
                  <span class="placeholder col-5 rounded"></span>
                </td>

                <!-- Account -->
                <td>
                  <p class="placeholder col-7 rounded mb-1"></p>
                  <p class="placeholder col-5 rounded mb-1"></p>
                  <p class="placeholder col-4 rounded mb-0"></p>
                </td>

                <!-- Status -->
                <td>
                  <span class="placeholder col-6 rounded-pill"></span>
                </td>

                <!-- Date -->
                <td>
                  <span class="placeholder col-7 rounded"></span>
                </td>

                <!-- Actions -->
                <td class="pe-4 text-end">
                  <span class="placeholder col-8 rounded-pill"></span>
                </td>

              </tr>

            </tbody>

          </table>

        </div>
      </div>

      <!-- EMPTY -->
      <div
        v-else-if="!safeWithdrawals.length"
        class="text-center py-5 text-muted"
      >
        <i class="bi bi-inbox fs-1 d-block mb-2"></i>
        No withdrawal records found.
      </div>

      <!-- DATA -->
      <div
        v-else
        class="card border-0 shadow-sm rounded-4 overflow-hidden"
      >

        <div class="table-responsive">

          <table class="table table-hover align-middle mb-0">

            <thead class="bg-light">
              <tr>
                <th class="ps-4 py-3 fw-semibold">Tutor</th>
                <th class="py-3 fw-semibold">Amount</th>
                <th class="py-3 fw-semibold">Method</th>
                <th class="py-3 fw-semibold">Account Details</th>
                <th class="py-3 fw-semibold">Status</th>
                <th class="py-3 fw-semibold">Date Requested</th>
                <th class="pe-4 py-3 fw-semibold text-end">Actions</th>
              </tr>
            </thead>

            <tbody>

              <tr
                v-for="w in safeWithdrawals"
                :key="w.id"
              >

                <!-- Tutor -->
                <td class="ps-4">
                  <div>
                    <p class="mb-0 fw-bold">
                      {{ w?.tutor_name || 'Unknown' }}
                    </p>

                    <p class="small text-muted mb-0">
                      {{ w?.email || '-' }}
                    </p>
                  </div>
                </td>

                <!-- Amount -->
                <td class="fw-bold">
                  ₱{{ w?.amount || 0 }}
                </td>

                <!-- Method -->
                <td>
                  <span class="text-uppercase small fw-bold">
                    {{ w?.method || '-' }}
                  </span>
                </td>

                <!-- Account -->
                <td class="small">

                  <p class="mb-0">
                    {{ w?.account_name || '-' }}
                  </p>

                  <p class="mb-0 font-monospace text-muted">
                    {{ w?.account_number || '-' }}
                  </p>

                  <p
                    v-if="w?.bank_name"
                    class="mb-0 text-muted"
                  >
                    {{ w.bank_name }}
                  </p>

                </td>

                <!-- Status -->
                <td>
                  <span :class="getStatusBadgeClass(w?.status)">
                    {{ w?.status || 'unknown' }}
                  </span>
                </td>

                <!-- Date -->
                <td class="small text-muted">
                  {{ formatDate(w?.requested_at) }}
                </td>

                <!-- Actions -->
                <td class="pe-4 text-end">

                  <button
                    v-if="w?.status === 'pending'"
                    @click="markProcessed(w)"
                    class="btn btn-sm btn-outline-success rounded-pill px-3 me-2"
                  >
                    Mark Processed
                  </button>

                  <button
                    @click="openActionModal(w)"
                    class="btn btn-sm btn-light rounded-circle"
                  >
                    <i class="bi bi-eye"></i>
                  </button>

                </td>

              </tr>

            </tbody>

          </table>

        </div>
      </div>

    </Transition>

    <!-- MODAL -->
    <div
      v-if="activeWithdrawal"
      class="modal-backdrop fade show"
    ></div>

    <div
      class="modal fade"
      :class="{ show: activeWithdrawal, 'd-block': activeWithdrawal }"
      tabindex="-1"
    >

      <div class="modal-dialog modal-dialog-centered">

        <div class="modal-content border-0 shadow rounded-4">

          <div class="modal-header border-0 bg-light rounded-top-4">

            <h5 class="modal-title fw-bold">
              Withdrawal Exception Details
            </h5>

            <button
              @click="activeWithdrawal = null"
              type="button"
              class="btn-close shadow-none"
            ></button>

          </div>

          <div class="modal-body p-4">

            <div class="mb-4">
              <p class="small text-muted mb-1 text-uppercase fw-bold">
                Tutor Information
              </p>

              <h5 class="fw-bold mb-0">
                {{ activeWithdrawal?.tutor_name || 'Unknown' }}
              </h5>

              <p class="text-muted small">
                {{ activeWithdrawal?.email || '-' }}
              </p>
            </div>

            <div class="row mb-4">

              <div class="col-6">
                <p class="small text-muted mb-1 text-uppercase fw-bold">
                  Amount
                </p>

                <h4 class="fw-bold text-success">
                  ₱{{ activeWithdrawal?.amount || 0 }}
                </h4>
              </div>

              <div class="col-6 text-end">
                <p class="small text-muted mb-1 text-uppercase fw-bold">
                  Method
                </p>

                <h5 class="fw-bold text-uppercase">
                  {{ activeWithdrawal?.method || '-' }}
                </h5>
              </div>

            </div>

            <div class="bg-light rounded-3 p-3 mb-4">

              <p class="small text-muted mb-2 text-uppercase fw-bold">
                Account Details
              </p>

              <p class="mb-1">
                <strong>Name:</strong>
                {{ activeWithdrawal?.account_name || '-' }}
              </p>

              <p class="mb-1">
                <strong>Account:</strong>
                {{ activeWithdrawal?.account_number || '-' }}
              </p>

              <p
                v-if="activeWithdrawal?.bank_name"
                class="mb-0"
              >
                <strong>Bank:</strong>
                {{ activeWithdrawal.bank_name }}
              </p>

            </div>

            <div
              v-if="['failed', 'flagged'].includes(activeWithdrawal?.status)"
              class="mb-4"
            >

              <label class="form-label small fw-bold">
                FAILURE REASON / AUDIT NOTE
              </label>

              <textarea
                v-model="failureReason"
                class="form-control rounded-3"
                rows="2"
                placeholder="Describe the error or audit finding..."
              ></textarea>

            </div>

            <div class="d-grid gap-2">

              <button
                v-if="['failed', 'flagged', 'pending'].includes(activeWithdrawal?.status)"
                @click="updateStatus('processed')"
                class="btn btn-success rounded-pill py-2"
              >
                Retry & Mark Processed
              </button>

              <button
                v-if="['failed', 'flagged', 'pending'].includes(activeWithdrawal?.status)"
                @click="updateStatus('rejected')"
                class="btn btn-outline-danger rounded-pill py-2"
              >
                Reject & Refund Balance
              </button>

              <button
                v-if="activeWithdrawal?.status === 'pending'"
                @click="updateStatus('flagged')"
                class="btn btn-warning rounded-pill py-2"
              >
                Flag for Review
              </button>

            </div>

          </div>

        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAdminStore } from '@/stores/admin';

const store = useAdminStore()
const statusFilter = ref('')
const activeWithdrawal = ref(null)
const failureReason = ref('')

const exceptionWithdrawals = computed(() => {
  return store.withdrawals.filter(w => ['failed', 'flagged'].includes(w.status))
})

const fetchWithdrawals = (force = false) => {
  store.fetchWithdrawals(statusFilter.value, force)
}

const safeWithdrawals = computed(() => {
  return (store.withdrawals || []).filter(w => w && w.id)
})

onMounted(() => {
  fetchWithdrawals(false)
})

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' })
}

const getStatusBadgeClass = (status) => {
  switch (status) {
    case 'processed': return 'badge bg-success-subtle text-success rounded-pill px-3';
    case 'failed': return 'badge bg-danger rounded-pill px-3';
    case 'flagged': return 'badge bg-warning text-dark rounded-pill px-3';
    case 'rejected': return 'badge bg-secondary rounded-pill px-3';
    default: return 'badge bg-info-subtle text-info rounded-pill px-3';
  }
}

const openActionModal = (w) => {
  activeWithdrawal.value = w
  failureReason.value = w.failure_reason || ''
}

const markProcessed = async (w) => {
  if (confirm(`Confirm you have manually sent ₱${w.amount} to ${w.tutor_name}?`)) {
    try {
      await store.updateWithdrawalStatus(w.id, { status: 'processed' })
    } catch (err) {
      alert('Update failed.')
    }
  }
}

const updateStatus = async (status) => {
  if (confirm(`Are you sure you want to mark this as ${status}?`)) {
    try {
      await store.updateWithdrawalStatus(activeWithdrawal.value.id, { 
        status,
        failure_reason: failureReason.value
      })
      activeWithdrawal.value = null
    } catch (err) {
      alert('Update failed.')
    }
  }
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.icon-box { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; }
.admin-withdrawals .table thead th { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: none; }
</style>
