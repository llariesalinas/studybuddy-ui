<template>
  <AuthShell>
    <template #icon>
      <i :class="statusIconClass"></i>
    </template>
    <template #title>{{ pageTitle }}</template>
    <template #subtitle>{{ statusSubtitle }}</template>

    <div v-if="loading" class="text-center py-5">
      <span class="sb-spinner" aria-hidden="true"></span>
      <p class="text-muted mt-3">Loading application details...</p>
    </div>

    <div v-else-if="error" class="sb-auth-alert">
      {{ error }}
      <button @click="fetchStatus" class="btn btn-link btn-sm p-0 d-block mt-2">Try Again</button>
    </div>

    <div v-else-if="application" class="sb-status-container">
      <div :class="['sb-status-badge', `sb-status-${statusTone}`]">
        {{ statusLabel }}
      </div>

      <div v-if="flow.kind === 'initial' && flow.status === 'pending'" class="sb-status-content">
        <p class="sb-status-text">
          Your application was submitted on
          <strong>{{ formatDate(submittedAt) }}</strong> and is currently being reviewed.
        </p>
        <div class="sb-info-card">
          <p class="small mb-0">
            We'll send an email to <strong>{{ application.email }}</strong> as soon as a decision is made.
          </p>
        </div>
      </div>

      <div v-else-if="flow.kind === 'initial' && flow.status === 'approved'" class="sb-status-content">
        <p class="sb-status-text">
          Great news! Your application has been approved. You can now access your dashboard.
        </p>
        <router-link :to="dashboardRoute" class="sb-btn-pill sb-btn sb-elevated sb-elevated--brand">Go to Dashboard</router-link>
      </div>

      <div v-else-if="flow.kind === 'renewal' && flow.status === 'pending'" class="sb-status-content">
        <p class="sb-status-text">
          Your updated enrollment documents were submitted on
          <strong>{{ formatDate(submittedAt) }}</strong> and are now under renewal review.
        </p>
        <div class="sb-info-card">
          <p class="small mb-0">
            No further upload is needed while the admin team reviews this renewal submission.
          </p>
        </div>
      </div>

      <div v-else-if="flow.kind === 'renewal' && flow.status === 'approved'" class="sb-status-content">
        <p class="sb-status-text">
          Your updated enrollment documents have been approved. You can continue using your dashboard.
        </p>
        <router-link :to="dashboardRoute" class="sb-btn-pill">Go to Dashboard</router-link>
      </div>

      <div v-else class="sb-status-content">
        <div v-if="flow.kind === 'renewal' && flow.status === 'due'" class="sb-info-card sb-action-card">
          <h6 class="sb-card-title">Updated enrollment documents required</h6>
          <p class="small mb-0">
            To keep your access current, upload your latest School ID and proof of enrollment.
          </p>
          <p v-if="renewalDueAt" class="small text-muted mb-0 mt-2">
            Renewal due by {{ formatDate(renewalDueAt) }}.
          </p>
        </div>

        <div v-if="flow.status === 'rejected'" class="sb-rejection-box">
          <h6 class="sb-rejection-title">
            {{ flow.kind === 'renewal' ? 'Reason for renewal rejection:' : 'Reason for rejection:' }}
          </h6>
          <p class="sb-rejection-reason">
            "{{ rejectionReason || 'No specific reason provided.' }}"
          </p>
        </div>

        <p class="sb-status-text mb-4">
          {{ uploadPrompt }}
        </p>

        <form v-if="flow.needsUpload" @submit.prevent="handleDocumentSubmit" class="sb-resubmit-form">
          <div v-if="resubmitError" class="sb-auth-alert mb-3">{{ resubmitError }}</div>

          <div class="sb-auth-field">
            <label class="sb-auth-label">Updated School ID (Image)</label>
            <input
              type="file"
              @change="handleFileChange($event, 'schoolId')"
              class="sb-auth-input"
              accept="image/*"
              required
            />
          </div>

          <div class="sb-auth-field">
            <label class="sb-auth-label">Updated Proof of Enrollment (Image or PDF)</label>
            <input
              type="file"
              @change="handleFileChange($event, 'enrollmentProof')"
              class="sb-auth-input"
              accept="image/*,application/pdf"
              required
            />
          </div>

          <div class="sb-auth-field">
            <label class="sb-auth-label">{{ notesLabel }}</label>
            <textarea
              v-model="resubmitData.reasonToTutor"
              class="sb-auth-input sb-field"
              :placeholder="notesPlaceholder"
              rows="3"
            ></textarea>
          </div>

          <button type="submit" class="sb-btn-pill sb-btn sb-elevated sb-elevated--brand" :disabled="isResubmitting">
            <span v-if="isResubmitting" class="sb-spinner me-2"></span>
            {{ submitButtonLabel }}
          </button>
        </form>
      </div>

      <hr class="my-4 opacity-10" />

      <div class="d-flex flex-column gap-3 align-items-center text-center">
        <button @click="handleLogout" class="btn btn-link text-muted small p-0 text-decoration-none shadow-none">
          <i class="bi bi-box-arrow-left me-1"></i> Log out from {{ application.email }}
        </button>

        <p class="small text-muted mb-0">
          Need help? Contact <a href="mailto:StudyBuddySupport@gmail.com" class="text-primary fw-bold">StudyBuddySupport@gmail.com</a>
        </p>
      </div>
    </div>

    <div v-else-if="showInitialTuteeSubmission" class="sb-status-container">
      <p class="sb-status-text mb-4">
        Submit your School ID and proof of enrollment to get verified before booking your first session.
      </p>

      <form @submit.prevent="handleDocumentSubmit" class="sb-resubmit-form">
        <div v-if="resubmitError" class="sb-auth-alert mb-3">{{ resubmitError }}</div>

        <div class="sb-auth-field">
          <label class="sb-auth-label">School ID (Image)</label>
          <input
            type="file"
            @change="handleFileChange($event, 'schoolId')"
            class="sb-auth-input"
            accept="image/*"
            required
          />
        </div>

        <div class="sb-auth-field">
          <label class="sb-auth-label">Proof of Enrollment (Image or PDF)</label>
          <input
            type="file"
            @change="handleFileChange($event, 'enrollmentProof')"
            class="sb-auth-input"
            accept="image/*,application/pdf"
            required
          />
        </div>

        <div class="sb-auth-field">
          <label class="sb-auth-label">Motivation (Optional)</label>
          <textarea
            v-model="resubmitData.reasonToTutor"
            class="sb-auth-input"
            placeholder="Tell us about your motivation..."
            rows="3"
          ></textarea>
        </div>

        <button type="submit" class="sb-btn-pill" :disabled="isResubmitting">
          <span v-if="isResubmitting" class="sb-spinner me-2"></span>
          {{ isResubmitting ? 'Submitting...' : 'Submit Documents' }}
        </button>
      </form>
    </div>

    <div v-else class="text-center py-5">
      <p class="text-muted">No application found. Please register first.</p>
      <router-link to="/register" class="sb-auth-link">Go to Registration</router-link>
    </div>
  </AuthShell>
</template>

<script setup>
import { computed, onMounted, ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api/api'
import { useAuthStore } from '@/stores/auth'
import AuthShell from '@/components/AuthShell.vue'
import { MAX_DOCUMENT_UPLOAD_SIZE_BYTES } from '@/config'
import {
  getReviewRejectionReason,
  getReviewSubmittedAt,
  getTutorApplicationFlow,
} from '@/services/tutorApplicationState'

const router = useRouter()
const authStore = useAuthStore()
const isTutee = computed(() => authStore.userRole === 'tutee')
const dashboardRoute = computed(() => (isTutee.value ? '/dashboard' : '/tch-dashboard'))
const loading = ref(true)
const error = ref('')
const application = ref(null)
const showInitialTuteeSubmission = computed(
  () => isTutee.value && !loading.value && !error.value && !application.value
)

const isResubmitting = ref(false)
const resubmitError = ref('')
const resubmitData = reactive({
  schoolId: null,
  enrollmentProof: null,
  reasonToTutor: ''
})

const flow = computed(() => getTutorApplicationFlow(application.value))
const submittedAt = computed(() => getReviewSubmittedAt(application.value))
const rejectionReason = computed(() => getReviewRejectionReason(application.value))
const renewalDueAt = computed(() =>
  application.value?.renewal_due_at ||
  application.value?.document_renewal_due_at ||
  application.value?.next_document_review_due_at ||
  null
)

const fetchStatus = async () => {
  loading.value = true
  error.value = ''
  try {
    const endpoint = isTutee.value ? 'tutee-application/status/' : 'tutor-application/status/'
    const response = await api.get(endpoint)
    application.value = response.data
    resubmitData.reasonToTutor =
      application.value.renewal_note ||
      application.value.reason_to_tutor ||
      ''
  } catch (err) {
    console.error('Failed to fetch status:', err)
    if (err.response?.status === 401) {
      error.value = 'Please log in to check your application status.'
    } else if (err.response?.status === 404 && isTutee.value) {
      // Tutees register free and submit verification documents later (unlike tutors, who submit at
      // registration) — a 404 here just means they haven't submitted yet, not an error.
      application.value = null
    } else {
      error.value = 'Could not load application status. Please try again later.'
    }
  } finally {
    loading.value = false
  }
}

const pageTitle = computed(() => {
  if (showInitialTuteeSubmission.value) return 'Enrollment Verification'
  return flow.value.kind === 'renewal' ? 'Document Renewal Status' : 'Application Status'
})

const statusIconClass = computed(() => {
  if (!application.value) return 'bi bi-info-circle'
  if (flow.value.kind === 'renewal' && flow.value.status === 'due') {
    return 'bi bi-exclamation-circle-fill text-warning'
  }

  switch (flow.value.status) {
    case 'pending': return 'bi bi-hourglass-split'
    case 'approved': return 'bi bi-check-circle-fill text-success'
    case 'rejected': return 'bi bi-exclamation-triangle-fill text-danger'
    default: return 'bi bi-info-circle'
  }
})

const statusSubtitle = computed(() => {
  if (showInitialTuteeSubmission.value) return 'Verification required to book your first session'
  if (!application.value) return 'Checking your status...'

  if (flow.value.kind === 'renewal') {
    switch (flow.value.status) {
      case 'due': return 'Updated enrollment documents are required'
      case 'pending': return 'Your renewal submission is being reviewed'
      case 'rejected': return 'Action required on your renewal submission'
      default: return 'Current status of your document renewal'
    }
  }

  switch (flow.value.status) {
    case 'pending': return 'Your application is being reviewed'
    case 'approved': return 'Your application was successful!'
    case 'rejected': return 'Action required on your application'
    default: return 'Current status of your application'
  }
})

const statusLabel = computed(() => {
  if (!application.value) return ''

  if (flow.value.kind === 'renewal') {
    switch (flow.value.status) {
      case 'due': return 'Renewal Required'
      case 'pending': return 'Renewal Pending Review'
      case 'approved': return 'Renewal Approved'
      case 'rejected': return 'Renewal Not Approved'
      default: return 'Document Renewal'
    }
  }

  switch (flow.value.status) {
    case 'pending': return 'Pending Review'
    case 'approved': return 'Approved'
    case 'rejected': return 'Not Approved'
    default: return flow.value.status
  }
})

const statusTone = computed(() => {
  if (flow.value.status === 'due') return 'due'
  return flow.value.status || 'pending'
})

const uploadPrompt = computed(() => {
  if (flow.value.kind === 'renewal' && flow.value.status === 'due') {
    return 'Upload the latest copies below so an institution admin can review your renewal.'
  }

  if (flow.value.kind === 'renewal') {
    return 'Please resubmit corrected renewal documents below.'
  }

  return "Don't worry, you can re-apply by updating and resubmitting your documents below."
})

const notesLabel = computed(() =>
  flow.value.kind === 'renewal' ? 'Note to Reviewer (Optional)' : 'Updated Motivation (Optional)'
)

const notesPlaceholder = computed(() =>
  flow.value.kind === 'renewal'
    ? 'Add any context about your updated enrollment documents...'
    : 'Tell us about your motivation...'
)

const submitButtonLabel = computed(() => {
  if (isResubmitting.value) {
    return flow.value.kind === 'renewal' ? 'Submitting Renewal...' : 'Resubmitting...'
  }

  return flow.value.kind === 'renewal' ? 'Submit Renewal Documents' : 'Resubmit Application'
})

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  })
}

const handleFileChange = (event, type) => {
  const file = event.target.files[0]
  if (!file) return

  if (file.size > MAX_DOCUMENT_UPLOAD_SIZE_BYTES) {
    resubmitError.value = `"${file.name}" is too large. Each file must be under 5 MB.`
    event.target.value = ''
    return
  }

  resubmitError.value = ''
  if (type === 'schoolId') resubmitData.schoolId = file
  else if (type === 'enrollmentProof') resubmitData.enrollmentProof = file
}

const handleDocumentSubmit = async () => {
  resubmitError.value = ''
  if (!resubmitData.schoolId || !resubmitData.enrollmentProof) {
    resubmitError.value = 'Please upload both required documents.'
    return
  }

  isResubmitting.value = true
  try {
    const formData = new FormData()
    formData.append('school_id', resubmitData.schoolId)
    formData.append('enrollment_proof', resubmitData.enrollmentProof)
    formData.append('reason_to_tutor', resubmitData.reasonToTutor)

    const prefix = isTutee.value ? 'tutee-application' : 'tutor-application'

    if (flow.value.kind === 'renewal') {
      formData.append('renewal_note', resubmitData.reasonToTutor)
      await api.post(`${prefix}/renewal/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    } else {
      await api.post(`${prefix}/resubmit/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }

    await fetchStatus()
  } catch (err) {
    console.error('Document submission failed:', err)
    resubmitError.value =
      err.response?.data?.error ||
      err.response?.data?.detail ||
      'Document submission failed. Please try again.'
  } finally {
    isResubmitting.value = false
  }
}

const handleLogout = async () => {
  authStore.logout()
  router.push('/login')
}

onMounted(() => {
  fetchStatus()
})
</script>

<style scoped>
.sb-status-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sb-status-badge {
  display: inline-flex;
  align-self: center;
  padding: 6px 16px;
  border-radius: 99px;
  font-size: 14px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.sb-status-pending,
.sb-status-due {
  background: #fef3c7;
  color: #92400e;
}

.sb-status-approved {
  background: #d1fae5;
  color: #065f46;
}

.sb-status-rejected {
  background: #fee2e2;
  color: #991b1b;
}

.sb-status-text {
  text-align: center;
  font-size: 15px;
  color: var(--sb-text-main);
  line-height: 1.6;
}

.sb-info-card {
  background: var(--sb-surface-variant, #f8f9fa);
  border: 1px solid var(--sb-card-border);
  border-radius: 12px;
  padding: 12px 16px;
  text-align: center;
  color: var(--sb-text-muted);
}

.sb-action-card {
  text-align: left;
}

.sb-card-title {
  color: var(--sb-text-main);
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 4px;
}

.sb-rejection-box {
  background: #fff5f5;
  border: 1px solid #fecaca;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
}

.sb-rejection-title {
  color: #b91c1c;
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 4px;
}

.sb-rejection-reason {
  color: #7f1d1d;
  font-size: 14px;
  font-style: italic;
  margin-bottom: 0;
}

.sb-resubmit-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sb-auth-field {
  text-align: left;
}

.sb-auth-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--sb-text-main);
  margin-bottom: 6px;
}

.sb-auth-input {
  width: 100%;
  padding: 10px 14px;
  font-size: 14px;
  border: 1px solid var(--sb-card-border);
  border-radius: 10px;
  background: var(--sb-surface);
  color: var(--sb-text-main);
}

.sb-btn-pill {
  width: 100%;
  padding: 12px;
  border-radius: 99px;
  background: var(--sb-primary);
  color: white;
  border: none;
  font-weight: 600;
  transition: none;
}

.sb-btn-pill:hover:not(:disabled) {
  background: var(--sb-primary-hover);
}

.sb-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  display: inline-block;
  animation: spin 0.75s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.sb-auth-alert {
  background: #fff5f5;
  border: 1px solid #fecaca;
  color: #b91c1c;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 13px;
}
</style>
