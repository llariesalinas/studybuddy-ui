<template>
  <div class="booking-details container py-2">

    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="fw-bold mb-0">Booking Details</h2>
    </div>

    <div v-if="bookingDetailsStore.isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status" />
    </div>

    <div v-else-if="!bookingDetailsStore.booking">
      <div class="alert alert-warning">Booking not found.</div>
    </div>

    <div v-else class="row g-4">

      <div class="col-12 col-md-8">
        <div class="card shadow-sm p-3 d-flex flex-row align-items-stretch h-100 gap-3">
          <img
            v-if="bookingDetailsStore.tuteeProfile?.avatar"
            :src="bookingDetailsStore.tuteeProfile.avatar.replace('150', '300')"
            style="width: 50%; height: 100%; object-fit: cover; border-radius: 10pt;"
            alt="Tutee Avatar"
            />
            

          <div class="flex-grow-1">
            <h3 class="fw-bold mb-2">
              {{ bookingDetailsStore.tuteeProfile?.name || 'N/A' }}
            </h3>
            <p class="text-muted mb-1">
              <strong>Email:</strong> {{ bookingDetailsStore.tuteeProfile?.email || 'N/A' }}
            </p>
            <p class="text-muted mb-1">
              <strong>Course:</strong> {{ bookingDetailsStore.tuteeProfile?.course || 'N/A' }}
            </p>
            <p class="text-muted mb-1">
              <strong>Year Level:</strong> {{ bookingDetailsStore.tuteeProfile?.year_level || 'N/A' }}
            </p>
            <p class="text-muted mb-0">
              <strong>Bio:</strong> {{ bookingDetailsStore.tuteeProfile?.bio || 'N/A' }}
            </p>
          </div>
        </div>
      </div>

      <div class="col-12 col-md-4">
        <div class="card shadow-sm p-3 h-100 d-flex flex-column justify-content-between">
          <div>
            <h5 class="fw-bold mb-3">Payment Summary</h5>

            <div class="row mb-2">
              <div class="col-5 text-muted">Transaction ID</div>
              <div class="col-7 text-end fw-semibold">
                {{ bookingDetailsStore.paymentInfo?.transaction_id || 'N/A' }}
              </div>
            </div>

            <div class="row mb-2">
              <div class="col-5 text-muted">Method</div>
              <div class="col-7 text-end fw-semibold">
                {{ bookingDetailsStore.paymentInfo?.method || 'N/A' }}
              </div>
            </div>

            <div class="row mb-2">
              <div class="col-5 text-muted">Amount Paid</div>
              <div class="col-7 text-end fw-semibold">
                ₱{{ bookingDetailsStore.paymentInfo?.amount_paid?.toFixed(2) || '0.00' }}
              </div>
            </div>

            <div class="row mb-2">
              <div class="col-5 text-muted">Tutor Earned</div>
              <div class="col-7 text-end fw-semibold">
                ₱{{ bookingDetailsStore.paymentInfo?.tutor_earned?.toFixed(2) || '0.00' }}
              </div>
            </div>

            <div class="row mb-2">
              <div class="col-5 text-muted">Platform Fee</div>
              <div class="col-7 text-end fw-semibold">
                ₱{{ bookingDetailsStore.paymentInfo?.platform_fee?.toFixed(2) || '0.00' }}
              </div>
            </div>

            <div
            class="row mb-2"
            v-if="Number(bookingDetailsStore.paymentInfo?.transaction_fee || 0) > 0"
            >
                <div class="col-5 text-muted">Transaction Fee</div>
                <div class="col-7 text-end fw-semibold">
                    ₱{{ bookingDetailsStore.paymentInfo?.transaction_fee?.toFixed(2) || '0.00' }}
                </div>
            </div>

            <div class="row mb-3">
              <div class="col-5 text-muted">Status</div>
              <div class="col-7 text-end">
                <span
                  class="badge"
                  :class="{
                    'bg-success': bookingDetailsStore.paymentInfo?.status === 'Paid',
                    'bg-warning text-dark': bookingDetailsStore.paymentInfo?.status === 'Pending',
                    'bg-danger': bookingDetailsStore.paymentInfo?.status === 'Failed'
                  }"
                >
                  {{ bookingDetailsStore.paymentInfo?.status || 'N/A' }}
                </span>
              </div>
            </div>
          </div>

          <div class="d-flex justify-content-end">
            <button
              v-if="bookingDetailsStore.sessionInfo?.status === 'Awaiting Verification'"
              class="btn btn-success"
              @click="handleComplete"
            >
              Complete Session
            </button>
          </div>
        </div>
      </div>

      <!-- Session Information (Full Width) -->
      <div class="col-12">
        <div class="card shadow-sm">
          <div class="card-body">
            <h5 class="fw-bold mb-3">Session Information</h5>

            <div class="row text-center fw-semibold mb-2">
              <div class="col">Subject</div>
              <div class="col">Date</div>
              <div class="col">Time</div>
              <div class="col">Rating</div>
              <div class="col">Status</div>
            </div>

            <div class="row text-center">
              <div class="col">{{ bookingDetailsStore.sessionInfo?.subject || 'N/A' }}</div>
              <div class="col">{{ bookingDetailsStore.sessionInfo?.date || 'N/A' }}</div>
              <div class="col">
                {{ bookingDetailsStore.sessionInfo?.start_time || 'N/A' }} –
                {{ bookingDetailsStore.sessionInfo?.end_time || 'N/A' }}
              </div>
              <div class="col">{{ bookingDetailsStore.sessionInfo?.rating ?? '—' }}⭐</div>
              <div class="col">{{ bookingDetailsStore.sessionInfo?.status || 'N/A' }}</div>
            </div>

          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { useTutorBookingDetailStore } from '@/stores/tutorBookingDetails'

const route = useRoute()
const bookingId = route.params.id
const bookingDetailsStore = useTutorBookingDetailStore()
const store = useTutorBookingDetailStore()

const handleComplete = async () => {
  try {
    await bookingDetailsStore.completeSession()
    alert("Session marked as completed.")
  } catch (error) {
    alert(error.response?.data?.error || "Failed to complete session.")
  }
}

const handleComplete = async () => {
  try {
    await bookingDetailsStore.completeSession()
    alert("Session marked as completed.")
  } catch (error) {
    alert(error.response?.data?.error || "Failed to complete session.")
  }
}

const handleComplete = async () => {
  try {
    await bookingDetailsStore.completeSession()
    alert("Session marked as completed.")
  } catch (error) {
    alert(error.response?.data?.error || "Failed to complete session.")
  }
}

onMounted(() => {
    bookingDetailsStore.fetchBookingDetails(route.params.id)
})

onBeforeUnmount(() => {
  bookingDetailsStore.resetStore()
})
</script>

<style scoped>
.card {
  border-radius: 12px;
}

.card-body {
  padding: 1.5rem;
}

.list-group-item {
  border: none;
  padding-left: 0;
  padding-right: 0;
}
</style>
