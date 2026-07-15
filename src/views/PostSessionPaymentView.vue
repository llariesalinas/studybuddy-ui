<template>
  <div class="booking-content container py-2">
    <div class="mb-3">
      <button class="btn btn-outline-secondary d-flex align-items-center gap-2 sb-btn" @click="backButton">
        <i class="bi bi-arrow-left"></i>
        Back
      </button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-sb-primary" role="status"></div>
      <p class="text-muted mt-3 mb-0">Loading payment details...</p>
    </div>

    <div v-else-if="!bookingDetail" class="alert alert-warning">
      Unable to load this session.
    </div>

    <div v-else class="row justify-content-center py-3">
      <div class="col-lg-8">
        <div class="card border-sb shadow-sm rounded-4 p-4" :class="{ 'sb-success-card': showSuccess }">
          <Transition name="pop">
            <div v-if="showSuccess" class="success-icon-overlay">
              <div class="success-icon">✓</div>
            </div>
          </Transition>
          <div class="summary-card rounded-4 p-3 mb-4">
            <h5 class="fw-bold mb-3">Session Payment Summary</h5>
            <div class="summary-grid">
              <div>
                <span class="summary-label">Tutor</span>
                <div class="summary-value">{{ bookingDetail.tutor?.name }}</div>
              </div>
              <div>
                <span class="summary-label">Subject</span>
                <div class="summary-value">{{ bookingDetail.session?.subject }}</div>
              </div>
              <div>
                <span class="summary-label">Date</span>
                <div class="summary-value">{{ bookingDetail.session?.date }}</div>
              </div>
              <div>
                <span class="summary-label">Hours</span>
                <div class="summary-value">{{ bookingDetail.session?.duration_hours }}</div>
              </div>
              <div>
                <span class="summary-label">Total</span>
                <div class="summary-total">{{ totalAmount }}</div>
              </div>
            </div>
          </div>

          <div class="mb-4">
            <h5 class="fw-bold mb-3">Payment Method</h5>
            <div class="payment-method-card payment-method-card--fixed">
              <i :class="['bi', paymentMethodIcon, 'payment-method-icon']"></i>
              <div>
                <div class="fw-semibold">{{ paymentMethodLabel }}</div>
                <div class="text-muted small">{{ paymentMethodDescription }}</div>
              </div>
            </div>
          </div>

          <div class="card border-sb rounded-4 p-3">
            <template v-if="paymentMethodUnavailableMessage">
              <div class="alert alert-danger mb-0">
                {{ paymentMethodUnavailableMessage }}
              </div>
            </template>

            <template v-else-if="requiredMethodCode === 'PAYMONGO'">
              <div class="alert alert-info mb-3 small">
                <i class="bi bi-shield-check me-2"></i>
                You will be redirected to a secure payment page. Accepted: GCash, Maya, Visa, Mastercard.
              </div>
              <button
                class="btn bg-sb-primary text-white w-100 sb-btn"
                :disabled="isSubmitting"
                @click="initiateOnlinePayment"
              >
                {{ isSubmitting ? 'Redirecting...' : 'Pay Online' }}
              </button>
            </template>

            <template v-else-if="requiredMethodCode === 'CASH'">
              <div class="alert alert-info mb-3 small">
                <i class="bi bi-cash-coin me-2"></i>
                This face-to-face session uses cash payment. Attach a photo of your proof of payment so the tutor and admins can verify it.
              </div>
              <div class="mb-3">
                <label class="form-label">Receipt Image</label>
                <input
                  type="file"
                  class="form-control"
                  accept="image/*"
                  @change="handleReceiptChange"
                />
                <div class="form-text">A receipt image is required for cash payments.</div>
              </div>

              <button
                class="btn bg-sb-primary text-white w-100 sb-btn"
                :disabled="isSubmitting || !canSubmitCashPayment"
                @click="submitPayment"
              >
                {{ isSubmitting ? 'Submitting...' : 'Submit Payment Receipt' }}
              </button>
            </template>

            <template v-else>
              <p class="text-muted text-center mb-0">
                Payment details are unavailable for this session.
              </p>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api/api'
import { useCatalogStore } from '@/stores/catalog'
import { useNotificationsStore } from '@/stores/notifications'
import { usePaymentStore } from '@/stores/tuteePaymentDetails'
import { useSessionsStore } from '@/stores/completedSessions'
import { useToastStore } from '@/stores/toast'

const route = useRoute()
const router = useRouter()
const catalogStore = useCatalogStore()
const notificationsStore = useNotificationsStore()
const paymentStore = usePaymentStore()
const sessionsStore = useSessionsStore()
const toastStore = useToastStore()

const bookingId = route.params.bookingId
const bookingDetail = ref(null)
const paymentMethods = ref([])
const loading = ref(true)
const isSubmitting = ref(false)
const showSuccess = ref(false)

const sessionMode = computed(() =>
  String(bookingDetail.value?.session?.session_mode || bookingDetail.value?.session_mode || '').trim()
)

const requiredMethodCode = computed(() =>
  sessionMode.value === 'F2F' ? 'CASH' : 'PAYMONGO'
)

const requiredMethod = computed(() =>
  paymentMethods.value.find(method => method.code === requiredMethodCode.value) || null
)

const paymentMethodUnavailableMessage = computed(() => {
  if (!bookingDetail.value) {
    return ''
  }

  if (requiredMethod.value) {
    return ''
  }

  if (requiredMethodCode.value === 'CASH') {
    return "Cash payment isn't available right now. Please contact support or try again later."
  }

  return "Online payment isn't available right now. Please contact support or try again later."
})

const paymentMethodLabel = computed(() =>
  requiredMethodCode.value === 'CASH' ? 'Cash Payment' : 'PayMongo Online'
)

const paymentMethodDescription = computed(() =>
  requiredMethodCode.value === 'CASH'
    ? 'Required for face-to-face sessions'
    : 'Required for online sessions'
)

const paymentMethodIcon = computed(() =>
  requiredMethodCode.value === 'CASH' ? 'bi-cash-coin' : 'bi-phone'
)

const canSubmitCashPayment = computed(() => Boolean(paymentStore.receiptImage))

const totalAmount = computed(() => {
  if (!bookingDetail.value) {
    return 'PHP 0.00'
  }

  const tutorRate = Number(bookingDetail.value.tutor?.hourly_rate || bookingDetail.value.tutor_hourly_rate || 0)
  const sessionHours = Number(bookingDetail.value.session?.duration_hours || 0)
  return `PHP ${(tutorRate * sessionHours).toFixed(2)}`
})

const backButton = () => {
  paymentStore.reset()
  router.push(`/tuteeSessionDetails/${bookingId}`)
}

const handleReceiptChange = (event) => {
  paymentStore.receiptImage = event.target.files?.[0] || null
}

const initiateOnlinePayment = async () => {
  isSubmitting.value = true
  try {
    const { data } = await api.post('payments/initiate/', { booking_id: bookingId })
    window.location.href = data.payment_url
  } catch (error) {
    console.error('Online payment initiation error:', error)
    toastStore.push(error.response?.data?.error || 'Unable to initiate payment. Please try again.', 'error')
    isSubmitting.value = false
  }
}

const submitPayment = async () => {
  if (!requiredMethod.value) {
    toastStore.push(paymentMethodUnavailableMessage.value || 'Payment method unavailable.', 'warning')
    return
  }

  if (requiredMethodCode.value === 'CASH' && !canSubmitCashPayment.value) {
    toastStore.push('Please attach a receipt image.', 'warning')
    return
  }

  const formData = new FormData()
  formData.append('payment_method', requiredMethod.value.id)

  if (paymentStore.receiptImage) {
    formData.append('receipt_image', paymentStore.receiptImage)
  }

  isSubmitting.value = true

  try {
    bookingDetail.value = await sessionsStore.submitPayment(bookingId, formData)
    await notificationsStore.fetchNotifications()
    paymentStore.reset()
    showSuccess.value = true
    await new Promise(resolve => setTimeout(resolve, 800))
    toastStore.push('Payment submitted. Waiting for tutor verification.')
    router.push(`/tuteeSessionDetails/${bookingId}`)
  } catch (error) {
    console.error('Payment submission error:', error)
    toastStore.push(error.response?.data?.error || 'Unable to submit payment.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

onMounted(async () => {
  paymentStore.reset()

  try {
    const [detailResponse, methodsResponse] = await Promise.all([
      sessionsStore.fetchSessionById(bookingId),
      catalogStore.fetchPaymentMethods(),
    ])

    bookingDetail.value = detailResponse
    paymentMethods.value = methodsResponse.map(method => ({
      id: method.id,
      label: method.name,
      code: method.code,
      icon: method.code === 'PAYMONGO' ? 'bi-phone' : 'bi-cash-coin'
    }))
    paymentStore.selectedMethod = paymentMethods.value.find(
      method => method.code === requiredMethodCode.value
    )?.id || null
  } catch (error) {
    console.error('Failed to load payment page:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.summary-card {
  background: #f7faf8;
  border: 1px solid var(--sb-card-border);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
}

.summary-label {
  display: block;
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #6b7280;
  margin-bottom: 4px;
}

.summary-value {
  font-weight: 600;
  color: #1f2937;
}

.summary-total {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--sb-primary);
}

.payment-method-card {
  border: 1px solid var(--sb-card-border);
  background: #ffffff;
  border-radius: 16px;
  padding: 16px 14px;
  display: flex;
  align-items: center;
  gap: 12px;
  color: #1f2937;
}

.payment-method-card--fixed {
  background: rgba(0, 137, 90, 0.05);
  border-color: rgba(0, 137, 90, 0.18);
}

.payment-method-icon {
  font-size: 1.5rem;
  color: var(--sb-primary);
}

.success-icon-overlay {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

.success-icon {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: var(--sb-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 800;
}

.pop-enter-active {
  animation: sb-pop var(--sb-t-normal) var(--sb-spring) both;
}
</style>
