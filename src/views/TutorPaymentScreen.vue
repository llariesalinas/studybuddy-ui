<template>
  <div class="p-4">
    <h2 class="fw-bold mb-4">Payment Verification</h2>

    <div class="card border-sb rounded-4 shadow-sm overflow-hidden">
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
                <button @click="verify(pay.id)" class="btn btn-sm bg-sb-primary text-white px-3 fw-bold">Verify Paid</button>
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
const payments = ref([
  { id: 1, name: 'Lia Salinas', amount: 250 },
  { id: 2, name: 'Reggie Cruz', amount: 500 }
])
const verify = (id) => {
  payments.value = payments.value.filter(p => p.id !== id)
  alert('Payment verified! Booking finalized.')
}
</script>
