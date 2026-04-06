<template>
<div class="booking-content container py-2">
    <div class="mb-3">
        <button
            class="btn btn-outline-secondary d-flex align-items-center gap-2"
            @click="backButton"
        >
            <i class="bi bi-arrow-left"></i>
            Back
        </button>
    </div>
    <div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-7">
        <div class="card border-sb shadow-sm rounded-4 p-4">

            <div class="card boarder-sb rounded-2 p-1 bg-light">
            <h5>Payment Summary</h5>
            <div v-if="paymentSummary">
                <p><strong>Hours:</strong> {{ paymentSummary.hours }}</p>
                <p><strong>Total:</strong> {{ paymentSummary.total }}</p>
                <p><strong>Subject:</strong> {{ paymentSummary.subject }}</p>
                <p><strong>Tutor:</strong> {{ paymentSummary.tutor }}</p>
            </div>

            <div v-else>
                <p>Loading summary...</p>
            </div>

            </div>

            <div class="paymentOptions">
            <h5>Payment Options</h5>

            <div class="card border-0 rounded-2 p-1 bg-transparent">
                <div class="row g-3">

                <div 
                    v-for="method in paymentMethods"
                    :key="method.id"
                    class="col-4"
                >
                    <button 
                    class="btn btn-outline-sb-primary w-100 d-flex flex-column align-items-center py-3"
                    :class="{ 'btn-sb-primary': paymentStore.selectedMethod === method.id }"
                    @click="chooseMethod(method.id)"
                    >
                    <i :class="`bi ${method.icon} fs-3`"></i>
                    <span class="mt-2 text-center">
                        {{ method.label }}
                    </span>
                    </button>
                </div>

                </div>
            </div>
            </div>

            <div class="card border-sb rounded p-3 mt-3">

            <div v-if="selectedMethodName === 'Cash'">

                <div class="alert alert-info">
                Please prepare exact amount.
                </div>

                <button
                class="btn btn-primary bg-sb-primary w-100"
                style="border-color: #00895A;"
                @click="ConfirmPayment"
                >
                Confirm Cash Payment
                </button>
            </div>

            <div v-else-if="selectedMethodName === 'GCash'">
                <div class="mb-3">
                <label class="form-label">Account Name</label>
                <input
                    type="text"
                    class="form-control"
                    v-model="paymentStore.gCashName"
                    placeholder="Enter GCash name"
                />
                </div>

                <div class="mb-3">
                <label class="form-label">GCash Number</label>
                <input
                    type="tel"
                    class="form-control"
                    v-model="paymentStore.gCashNumber"
                    placeholder="09XXXXXXXXX"
                />
                </div>

                <div class="mb-3">
                <label class="form-label">Reference Number</label>
                <input
                    type="text"
                    class="form-control"
                    v-model="paymentStore.gCashReference"
                    placeholder="Transaction reference"
                />
                </div>

                <button
                class="btn btn-primary bg-sb-primary w-100"
                style="border-color: #00895A;"
                >
                Submit GCash Payment
                </button>
            </div>

            <div v-else-if="selectedMethodName === 'Bank Transfer'">
                <div class="mb-3">
                <label class="form-label">Account Holder Name</label>
                <input
                    type="text"
                    class="form-control"
                    v-model="paymentStore.bankName"
                    placeholder="Enter account name"
                />
                </div>

                <div class="mb-3">
                <label class="form-label">Account Number</label>
                <input
                    type="text"
                    class="form-control"
                    v-model="paymentStore.bankAccount"
                    placeholder="Enter account number"
                />
                </div>

                <div class="mb-3">
                <label class="form-label">Transaction Reference</label>
                <input
                    type="text"
                    class="form-control"
                    v-model="paymentStore.bankReference"
                    placeholder="Reference number"
                />
                </div>

                <button
                class="btn btn-primary bg-sb-primary w-100"
                style="border-color: #00895A;"
                >
                Confirm Payment
                </button>
            </div>

            <div v-else>
                <p class="text-muted text-center">
                Please select a payment method.
                </p>
            </div>

            </div>
            


        </div>
        </div>
    </div>
  </div>
</div>
    
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api/api'
import { usePaymentStore } from '@/stores/tuteePaymentDetails'
import { useBookedSessionStore } from '@/stores/bookedSessionDetails'

const route = useRoute()
const router = useRouter()

const paymentStore = usePaymentStore()
const bookedSessionStore = useBookedSessionStore()

const tutorId = route.params.tutorId

const tutor = ref(null)
const paymentMethods = ref([])

const selectedMethodName = computed(() => {
  const method = paymentMethods.value.find(
    m => m.id === paymentStore.selectedMethod
  )
  return method ? method.label : null
})

// ---------------------------
// PAYMENT SUMMARY
// ---------------------------
const paymentSummary = computed(() => {
  if (!tutor.value) return null

  const hourlyRate = parseFloat(tutor.value.hourly_rate)
  const hours = bookedSessionStore.bookedSessions?.length || 0
  const total = hourlyRate * hours

  return {
    hours,
    total: `₱${total.toLocaleString()}`,
    subject: bookedSessionStore.bookedSessionSub,
    tutor: `${tutor.value.fname} ${tutor.value.lname}`
  }
})


// ---------------------------
// NAVIGATION
// ---------------------------
const backButton = () => {
  router.push(`/tutor/${tutorId}`)
  paymentStore.reset()
}


// ---------------------------
// SELECT PAYMENT METHOD
// ---------------------------
const chooseMethod = (methodId) => {
  paymentStore.selectedMethod = methodId
}


// ---------------------------
// LOAD DATA
// ---------------------------
onMounted(async () => {
  try {
    // Load tutor
    const tutorRes = await api.get(`tutors/${tutorId}/`)
    tutor.value = tutorRes.data

    // Load payment methods from backend
    const methodsRes = await api.get('payment-methods/')
    paymentMethods.value = methodsRes.data.map(m => ({
      id: m.id,
      label: m.name,
      icon:
        m.name === 'GCash' ? 'bi-wallet2' :
        m.name === 'Cash' ? 'bi-cash-coin' :
        'bi-credit-card'
    }))

  } catch (error) {
    console.error("Initialization error:", error)
    router.push('/find-tutors')
  }

  // Protect against direct URL access
  if (!bookedSessionStore.bookedSessionSub) {
    alert("No Sessions Selected.")
    router.push('/find-tutors')
  }
})

// ---------------------------
// CONFIRM PAYMENT
// ---------------------------
const ConfirmPayment = async () => {

  if (!paymentStore.selectedMethod) {
    alert("Please select a payment method.")
    return
  }

  try {

    await api.post('bookings/confirm/', {
      tutor_id: tutorId,
      date: bookedSessionStore.bookedSessionDate,
      slots: bookedSessionStore.bookedSessions,
      payment_method: paymentStore.selectedMethod   // real DB method_id
    })

    alert("Booking Confirmed!")

    paymentStore.reset()
    bookedSessionStore.resetStore()

    router.push({
      name: 'dashboard',
      query: { refresh: Date.now() }
    })

  } catch (error) {
    console.error("Payment error:", error.response?.data || error)
    alert(error.response?.data?.error || "Something went wrong.")
  }
}
</script>

<style setup>
.btn-outline-sb-primary {
  color: var(--sb-primary);
  border: 1px solid var(--sb-primary);
  background-color: transparent;
}
.btn-outline-sb-primary:hover {
  background-color: var(--sb-primary);
  color: white;
}
.btn-sb-primary {
  background-color: var(--sb-primary);
  border-color: var(--sb-primary);
  color: white;
}
</style>
