<template>
  <div class="p-4">
    <h2 class="fw-bold mb-4">Payment Verification</h2>

    <div class="card border-sb rounded-4 shadow-sm overflow-hidden" :class="{ 'sb-success-card': showSuccess }">
      <Transition name="pop">
        <div v-if="showSuccess" class="verify-success">
          <div class="success-icon">✓</div>
          <span class="ms-2 fw-semibold">Payment verified!</span>
        </div>
      </Transition>
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="bg-light">
            <tr>
              <th class="ps-4">Tutee</th>
              <th>Amount</th>
              <th>Status</th>
              <th class="text-end pe-4">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pay in payments" :key="pay.id">
              <td class="ps-4 fw-semibold">{{ pay.name }}</td>
              <td class="fw-bold">₱{{ pay.amount }}</td>
              <td><span class="badge bg-warning-subtle text-warning border border-warning">Pending</span></td>
              <td class="text-end pe-4">
                <button @click="verify(pay.id)" class="btn btn-sm bg-sb-primary text-white px-3 fw-bold sb-btn">Verify Paid</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()
const showSuccess = ref(false)
const payments = ref([
  { id: 1, name: 'Lia Salinas', amount: 250 },
  { id: 2, name: 'Reggie Cruz', amount: 500 }
])

const verify = (id) => {
  payments.value = payments.value.filter(p => p.id !== id)
  showSuccess.value = true
  toastStore.push('Payment verified! Booking finalized.')
  setTimeout(() => { showSuccess.value = false }, 1500)
}
</script>

<style scoped>
.verify-success {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
  background: rgba(0, 137, 90, 0.07);
  border-bottom: 1px solid rgba(0, 137, 90, 0.15);
  color: var(--sb-primary);
  font-size: 14px;
}

.success-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--sb-primary);
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 800;
}

.pop-enter-active {
  animation: sb-pop var(--sb-t-normal) var(--sb-spring) both;
}
</style>
