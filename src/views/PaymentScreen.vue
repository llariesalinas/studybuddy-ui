<template>
  <div class="payment-mgmt-content">
    <div class="mb-4 d-flex justify-content-between align-items-center">
      <div>
        <h2 class="fw-bold text-dark">Payment Verification</h2>
        <p class="text-muted">Confirm receipt of payments from your tutees.</p>
      </div>
      <div class="text-end border border-sb rounded-3 px-4 py-2 bg-white shadow-sm">
        <span class="d-block small text-muted fw-bold text-uppercase">Pending Balance</span>
        <span class="fs-4 fw-bold text-warning">₱{{ totalPending }}</span>
      </div>
    </div>

    <div v-if="isLoading" class="text-center py-5 text-sb-primary">
      <div class="spinner-border" role="status"></div>
    </div>

    <div v-else class="card border-sb shadow-sm rounded-4">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr class="text-muted small">
                <th class="ps-4 pb-3 pt-3">Tutee</th>
                <th class="pb-3 pt-3">Session Date</th>
                <th class="pb-3 pt-3">Amount (₱)</th>
                <th class="pb-3 pt-3">Status</th>
                <th class="pe-4 pb-3 pt-3 text-end">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="payment in pendingPayments" :key="payment.payment_id" style="border-bottom: 1px solid var(--sb-card-border);">
                <td class="ps-4 py-3 fw-semibold text-dark">{{ payment.tutee_name }}</td>
                <td class="py-3 text-muted">{{ payment.booking_date }}</td>
                <td class="py-3 fw-bold">₱{{ payment.amount }}</td>
                <td class="py-3">
                  <span class="badge bg-warning bg-opacity-10 text-warning border border-warning px-3 py-1 rounded-pill">
                    {{ payment.payment_Status }}
                  </span>
                </td>
                <td class="pe-4 py-3 text-end">
                  <button @click="markAsPaid(payment)" class="btn btn-sm bg-sb-primary text-white fw-semibold rounded-3 px-3 shadow-sm" :disabled="payment.isProcessing">
                     <span v-if="payment.isProcessing" class="spinner-border spinner-border-sm me-1"></span>
                    {{ payment.isProcessing ? 'Verifying...' : 'Mark as Paid' }}
                  </button>
                </td>
              </tr>

              <tr v-if="pendingPayments.length === 0">
                <td colspan="5" class="text-center py-5 text-muted">
                  No pending payments to verify. Great job!
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const isLoading = ref(true)
const pendingPayments = ref([])

// Calculates the total directly from the reactive array
const totalPending = computed(() => {
  return pendingPayments.value.reduce((sum, p) => sum + p.amount, 0)
})

onMounted(async () => {
  // API_INTEGRATION_POINT: GET /api/v1/payments/?status=PENDING
  setTimeout(() => {
    pendingPayments.value = [
      { payment_id: 501, booking_id: 12, tutee_name: 'Liam Torres', booking_date: 'Oct 25, 2026', amount: 150, payment_Status: 'PENDING', isProcessing: false },
      { payment_id: 502, booking_id: 14, tutee_name: 'Sophia Cruz', booking_date: 'Oct 26, 2026', amount: 300, payment_Status: 'PENDING', isProcessing: false }
    ]
    isLoading.value = false
  }, 700)
})

const markAsPaid = async (payment) => {
  payment.isProcessing = true
  try {
    // API_INTEGRATION_POINT: PATCH /api/v1/payments/{payment_id}/
    // Payload: { payment_Status: 'PAID' }

    console.log(`Updating payment ${payment.payment_id} to PAID`)

    // Simulate backend response delay
    setTimeout(() => {
      // Remove from the pending list UI once the backend confirms success
      pendingPayments.value = pendingPayments.value.filter(p => p.payment_id !== payment.payment_id)
    }, 1000)

  } catch (error) {
    console.error('Failed to verify payment', error)
    payment.isProcessing = false
  }
}
</script>
