<template>
  <div class="payment-content d-flex justify-content-center">
    <div class="card border-sb shadow-sm rounded-4 w-100" style="max-width: 800px;">
      <div class="row g-0">
        
        <div class="col-md-5 bg-light p-4 p-md-5 border-end border-sb rounded-start-4">
          <h5 class="fw-bold mb-4">Payment Summary</h5>
          
          <div class="d-flex justify-content-between mb-3">
            <span class="text-muted">Tutor</span>
            <span class="fw-semibold">Maria Santos</span>
          </div>
          <div class="d-flex justify-content-between mb-3">
            <span class="text-muted">Subject</span>
            <span class="fw-semibold">Calculus</span>
          </div>
          <div class="d-flex justify-content-between mb-3">
            <span class="text-muted">Duration</span>
            <span class="fw-semibold">1 Hour</span>
          </div>
          
          <hr class="border-sb my-4">
          
          <div class="d-flex justify-content-between align-items-center">
            <span class="fw-bold fs-5">Total</span>
            <span class="fw-bold fs-3 text-sb-primary">₱150.00</span>
          </div>
        </div>

        <div class="col-md-7 p-4 p-md-5">
          <h5 class="fw-bold mb-4">Payment Options</h5>
          
          <div class="d-flex gap-2 mb-4">
            <button class="btn btn-outline-dark px-4 rounded-3 active">GCash</button>
            <button class="btn btn-outline-dark px-4 rounded-3">Card</button>
          </div>

          <form @submit.prevent="confirmPayment">
            <div class="mb-3">
              <label class="form-label fw-semibold small">Account Name</label>
              <input type="text" class="form-control border-sb shadow-none" placeholder="Juan Dela Cruz" required>
            </div>
            
            <div class="mb-4">
              <label class="form-label fw-semibold small">Mobile Number</label>
              <input type="text" class="form-control border-sb shadow-none" placeholder="09XX XXX XXXX" required>
            </div>

            <button type="submit" class="btn bg-sb-primary text-white w-100 py-3 rounded-3 fw-bold shadow-sm mt-2">
              Confirm Payment
            </button>
          </form>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const confirmPayment = () => {
  // Logic to process payment goes here
  // Redirect to the sessions report page to see the booked session
  router.push('/reports')
}
</script>