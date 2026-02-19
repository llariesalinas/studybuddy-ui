<template>
  <div class="tutor-details-content">
    <button @click="router.back()" class="btn btn-link text-muted text-decoration-none ps-0 mb-4">
      <i class="bi bi-arrow-left me-2"></i> Back to Results
    </button>

    <div class="row g-4">
      <div class="col-lg-4">
        <div class="card border-sb shadow-sm rounded-4 text-center p-4">
          <div class="rounded-circle bg-success bg-opacity-25 text-sb-primary d-flex justify-content-center align-items-center fw-bold mx-auto mb-3" style="width: 80px; height: 80px; font-size: 1.5rem;">
            MS
          </div>
          <h4 class="fw-bold mb-0">Maria Santos</h4>
          <p class="text-muted small mb-3">3rd Year · Mathematics</p>
          
          <div class="d-flex justify-content-center gap-2 mb-4">
            <span class="badge bg-light text-dark border">Calculus</span>
            <span class="badge bg-light text-dark border">Algebra</span>
          </div>

          <hr class="border-sb">
          
          <div class="d-flex justify-content-between align-items-center mt-3">
             <div class="d-flex align-items-center text-warning fw-bold fs-5">
                <i class="bi bi-star-fill me-2"></i> 4.9
              </div>
            <div class="text-end">
              <span class="fw-bold fs-5">₱150</span><span class="text-muted">/hr</span>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-8">
        <div class="card border-sb shadow-sm rounded-4 p-4">
          <h5 class="fw-bold mb-4">Select a Time Slot</h5>
          
          <div class="table-responsive mb-4">
            <table class="table table-bordered text-center align-middle">
              <thead class="table-light">
                <tr>
                  <th>Mon</th><th>Tue</th><th>Wed</th><th>Thu</th><th>Fri</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td class="bg-success bg-opacity-10 text-sb-primary fw-semibold cursor-pointer border-sb">1:00 PM - 2:00 PM</td>
                  <td class="text-muted bg-light border-sb">Booked</td>
                  <td class="bg-success bg-opacity-10 text-sb-primary fw-semibold cursor-pointer border-sb">10:00 AM - 12:00 PM</td>
                  <td class="text-muted bg-light border-sb">Booked</td>
                  <td class="bg-success bg-opacity-10 text-sb-primary fw-semibold cursor-pointer border-sb">3:00 PM - 4:00 PM</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="text-end">
             <router-link to="/payment" class="btn bg-sb-primary text-white px-5 py-2 rounded-3 fw-semibold shadow-sm">
              Confirm & Proceed to Payment
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<style scoped>
.cursor-pointer { cursor: pointer; }
.cursor-pointer:hover { background-color: var(--sb-primary) !important; color: white !important; }
</style>