<template>
  <div class="admin-applications p-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3 class="mb-0">{{ pageTitle }}</h3>
      <div class="d-flex gap-2">
        <div class="btn-group" role="group" aria-label="Applicant role">
          <button
            type="button"
            class="btn btn-sm rounded-pill px-3 me-1"
            :class="filters.role === 'tutor' ? 'btn-dark' : 'btn-light'"
            @click="filters.role = 'tutor'"
          >
            Tutors
          </button>
          <button
            type="button"
            class="btn btn-sm rounded-pill px-3"
            :class="filters.role === 'tutee' ? 'btn-dark' : 'btn-light'"
            @click="filters.role = 'tutee'"
          >
            Tutees
          </button>
        </div>
        <select v-model="filters.status" class="form-select form-select-sm rounded-pill sb-field" style="width: 150px;">
          <option value="">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
        </select>
        <select v-model="filters.reviewType" class="form-select form-select-sm rounded-pill" style="width: 150px;">
          <option value="">All Types</option>
          <option value="initial">First-time</option>
          <option value="renewal">Renewal</option>
        </select>
        <button @click="loadApplications" class="btn btn-sm btn-light rounded-circle" title="Refresh">
          <i class="bi bi-arrow-clockwise"></i>
        </button>
      </div>
    </div>

    <div class="card border-0 shadow-sm rounded-4 overflow-hidden">
      <Transition name="fade" mode="out-in">
        <div v-if="adminStore.loading.tutorApplications && !adminStore.tutorApplications.length" class="table-responsive">
          <table class="table align-middle mb-0">
            <thead class="bg-light">
              <tr>
                <th class="ps-4 py-3">Applicant</th>
                <th class="py-3">Institution</th>
                <th class="py-3">Type</th>
                <th class="py-3">Status</th>
                <th class="py-3">Submitted</th>
                <th class="pe-4 py-3 text-end">Actions</th>
              </tr>
            </thead>
            <tbody class="placeholder-glow">
              <tr v-for="i in 5" :key="'skeleton-' + i">
                <td class="ps-4">
                  <div class="placeholder col-8 rounded mb-1"></div>
                  <div class="placeholder col-5 rounded small"></div>
                </td>
                <td><span class="placeholder col-7 rounded"></span></td>
                <td><span class="placeholder col-5 rounded-pill"></span></td>
                <td><span class="placeholder col-5 rounded-pill"></span></td>
                <td><span class="placeholder col-6 rounded small"></span></td>
                <td class="pe-4 text-end"><span class="placeholder col-4 rounded"></span></td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="bg-light">
              <tr>
                <th class="ps-4 py-3">Applicant</th>
                <th class="py-3">Institution</th>
                <th class="py-3">Type</th>
                <th class="py-3">Status</th>
                <th class="py-3">Submitted</th>
                <th class="pe-4 py-3 text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in filteredApplications" :key="`${getApplicationReviewKind(app)}-${app.id}`">
                <td class="ps-4">
                  <p class="mb-0 fw-bold">{{ app.applicant_name }}</p>
                  <p class="small text-muted mb-0">{{ app.email }}</p>
                </td>
                <td class="small">{{ app.institution_name }}</td>
                <td>
                  <span :class="['badge rounded-pill px-3', getReviewTypeBadgeClass(app)]">
                    {{ getReviewTypeLabel(app) }}
                  </span>
                </td>
                <td>
                  <span :class="['badge rounded-pill px-3', getStatusBadgeClass(getAppReviewStatus(app))]">
                    {{ formatStatus(getAppReviewStatus(app)) }}
                  </span>
                </td>
                <td class="small text-muted">{{ formatDate(getAppSubmittedAt(app)) }}</td>
                <td class="pe-4 text-end">
                  <button @click="viewDetails(app)" class="btn btn-sm btn-light rounded-pill px-3 sb-btn">
                    Review
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-if="!filteredApplications.length" class="text-center py-5">
            <i class="bi bi-inbox text-muted mb-3 d-block" style="font-size: 2rem;"></i>
            <p class="text-muted">No applications found matching your filter.</p>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Application Detail Offcanvas -->
    <div class="offcanvas offcanvas-end border-0 shadow" tabindex="-1" id="appDetailOffcanvas" style="width: 500px;">
      <div class="offcanvas-header bg-light border-bottom">
        <h5 class="offcanvas-title fw-bold">Review {{ selectedReviewTypeLabel }}</h5>
        <button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
      </div>
      <div v-if="selectedApp" class="offcanvas-body p-4">
        <div class="mb-4">
          <label class="text-muted small text-uppercase fw-bold mb-1">Applicant Information</label>
          <div class="p-3 bg-light rounded-3">
            <h5 class="mb-1 fw-bold">{{ selectedApp.applicant_name }}</h5>
            <p class="mb-1 small"><i class="bi bi-envelope me-2"></i>{{ selectedApp.email }}</p>
            <p class="mb-0 small"><i class="bi bi-building me-2"></i>{{ selectedApp.institution_name }}</p>
            <span :class="['badge rounded-pill mt-3 px-3', getReviewTypeBadgeClass(selectedApp)]">
              {{ selectedReviewTypeLabel }}
            </span>
          </div>
        </div>

        <div v-if="selectedReviewNote" class="mb-4">
          <label class="text-muted small text-uppercase fw-bold mb-1">{{ selectedReviewNoteLabel }}</label>
          <blockquote class="p-3 bg-light rounded-3 border-start border-primary border-4 small mb-0">
            "{{ selectedReviewNote }}"
          </blockquote>
        </div>

        <div class="mb-4">
          <label class="text-muted small text-uppercase fw-bold mb-2">Documents</label>
          <div class="row g-3">
            <div class="col-6">
              <div class="doc-card">
                <div class="small fw-bold mb-2 text-center text-muted">School ID</div>
                <a :href="selectedSchoolIdUrl" target="_blank" class="doc-preview rounded-3 overflow-hidden d-block bg-white shadow-sm border">
                  <img :src="selectedSchoolIdUrl" class="img-fluid" alt="School ID" @error="handleImageError" />
                  <div class="doc-overlay"><i class="bi bi-zoom-in me-1"></i> View Full</div>
                </a>
              </div>
            </div>
            <div class="col-6">
              <div class="doc-card">
                <div class="small fw-bold mb-2 text-center text-muted">Enrollment / RF Proof</div>
                <div v-if="isPdf(selectedEnrollmentProofUrl)" class="doc-preview rounded-3 bg-white d-flex align-items-center justify-content-center flex-column text-danger shadow-sm border">
                   <i class="bi bi-file-earmark-pdf" style="font-size: 2.5rem;"></i>
                   <span class="small mt-1 fw-bold">PDF File</span>
                   <a :href="selectedEnrollmentProofUrl" target="_blank" class="doc-overlay text-white"><i class="bi bi-download me-1"></i> View PDF</a>
                </div>
                <a v-else :href="selectedEnrollmentProofUrl" target="_blank" class="doc-preview rounded-3 overflow-hidden d-block bg-white shadow-sm border">
                  <img :src="selectedEnrollmentProofUrl" class="img-fluid" alt="Enrollment Proof" @error="handleImageError" />
                  <div class="doc-overlay"><i class="bi bi-zoom-in me-1"></i> View Full</div>
                </a>
              </div>
            </div>
          </div>
        </div>

        <div v-if="proposedSubjects.length" class="mb-4">
          <label class="text-muted small text-uppercase fw-bold mb-2">Proposed Subjects</label>
          <div
            v-for="subject in proposedSubjects"
            :key="subject.subject_code"
            class="proposed-subject-row"
          >
            <div>
              <div class="fw-bold">{{ subject.subject_name }}</div>
              <div class="small text-muted">{{ subject.category }}</div>
            </div>
            <div class="d-flex gap-2">
              <button
                class="btn btn-sm btn-success rounded-pill"
                :disabled="processingSubject === subject.subject_code"
                @click="handleSubjectReview(subject, 'approved')"
              >
                Approve
              </button>
              <button
                class="btn btn-sm btn-outline-danger rounded-pill"
                :disabled="processingSubject === subject.subject_code"
                @click="handleSubjectReview(subject, 'rejected')"
              >
                Reject
              </button>
            </div>
          </div>
        </div>

        <div v-if="isPendingReview(selectedApp)" class="mt-5 pt-3 border-top">
          <div v-if="rejectionMode">
            <label class="form-label fw-bold small">Reason for Rejection</label>
            <textarea v-model="rejectionReason" class="form-control mb-3 sb-field" rows="3" :placeholder="rejectionPlaceholder"></textarea>
            <div class="d-flex gap-2">
              <button @click="handleStatusUpdate('rejected')" class="btn btn-danger flex-grow-1 rounded-pill" :disabled="!rejectionReason || processing">
                <span v-if="processing" class="spinner-border spinner-border-sm me-2"></span>
                {{ processing ? 'Processing...' : 'Confirm Reject' }}
              </button>
              <button @click="rejectionMode = false" class="btn btn-light flex-grow-1 rounded-pill" :disabled="processing">
                Cancel
              </button>
            </div>
          </div>
          <div v-else class="d-flex gap-2">
            <button @click="handleStatusUpdate('approved')" class="btn btn-success flex-grow-1 rounded-pill" :disabled="processing">
              <span v-if="processing" class="spinner-border spinner-border-sm me-2"></span>
              {{ processing ? 'Processing...' : approveButtonLabel }}
            </button>
            <button @click="rejectionMode = true" class="btn btn-outline-danger flex-grow-1 rounded-pill" :disabled="processing">
              Reject
            </button>
          </div>
        </div>
        <div v-else class="mt-5 pt-3 border-top">
           <div :class="['p-3 rounded-3 text-center', getAppReviewStatus(selectedApp) === 'approved' ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger']">
             This {{ selectedReviewTypeLabel.toLowerCase() }} has already been
             <strong>{{ getAppReviewStatus(selectedApp) }}</strong>.
             <p v-if="getAppReviewedAt(selectedApp)" class="small mb-0 mt-1">
               Reviewed on {{ formatDate(getAppReviewedAt(selectedApp)) }}
             </p>
             <p v-if="getAppReviewStatus(selectedApp) === 'rejected' && getAppRejectionReason(selectedApp)" class="small mb-0 mt-1">
               Reason: {{ getAppRejectionReason(selectedApp) }}
             </p>
           </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { Offcanvas } from 'bootstrap'
import {
  getApplicationReviewKind,
  getReviewRejectionReason,
  getReviewReviewedAt,
  getReviewStatus,
  getReviewSubmittedAt,
} from '@/services/tutorApplicationState'

const adminStore = useAdminStore()
const filters = reactive({
  role: 'tutor',
  status: 'pending',
  reviewType: ''
})

const selectedApp = ref(null)
const rejectionMode = ref(false)
const rejectionReason = ref('')
const processing = ref(false)
const processingSubject = ref('')
let offcanvas = null

const pageTitle = computed(() => (filters.role === 'tutee' ? 'Tutee Applications' : 'Tutor Applications'))

const applicationsForRole = computed(() =>
  filters.role === 'tutee' ? adminStore.tuteeApplications : adminStore.tutorApplications
)

const loadApplications = async () => {
  const fetchApplications = filters.role === 'tutee'
    ? adminStore.fetchTuteeApplications
    : adminStore.fetchTutorApplications

  await fetchApplications(filters.status, true, {
    reviewType: filters.reviewType
  })
}

const filteredApplications = computed(() => {
  if (!filters.reviewType) return applicationsForRole.value

  return applicationsForRole.value.filter(
    (app) => getApplicationReviewKind(app) === filters.reviewType
  )
})

const selectedReviewType = computed(() =>
  selectedApp.value ? getApplicationReviewKind(selectedApp.value) : 'initial'
)

const selectedReviewTypeLabel = computed(() =>
  selectedReviewType.value === 'renewal' ? 'Renewal Submission' : 'Application'
)

const proposedSubjects = computed(() => {
  if (filters.role !== 'tutor' || selectedReviewType.value !== 'initial') return []
  return selectedApp.value?.proposed_subjects || []
})

const approveButtonLabel = computed(() =>
  selectedReviewType.value === 'renewal' ? 'Approve Renewal' : 'Approve Applicant'
)

const rejectionPlaceholder = computed(() =>
  selectedReviewType.value === 'renewal'
    ? 'Explain why the renewal documents are being rejected...'
    : 'Explain why the application is being rejected...'
)

const readFirst = (source, keys) => {
  for (const key of keys) {
    if (source?.[key]) return source[key]
  }

  return null
}

const selectedSchoolIdUrl = computed(() => {
  if (!selectedApp.value) return ''

  return readFirst(selectedApp.value, [
    'renewal_school_id_url',
    'document_renewal_school_id_url',
    'school_id_url'
  ])
})

const selectedEnrollmentProofUrl = computed(() => {
  if (!selectedApp.value) return ''

  return readFirst(selectedApp.value, [
    'renewal_enrollment_proof_url',
    'document_renewal_enrollment_proof_url',
    'enrollment_proof_url'
  ])
})

const selectedReviewNote = computed(() => {
  if (!selectedApp.value) return ''

  return readFirst(selectedApp.value, [
    'renewal_note',
    'document_renewal_note',
    'reason_to_tutor'
  ])
})

const selectedReviewNoteLabel = 'Renewal Note'

const viewDetails = (app) => {
  selectedApp.value = app
  rejectionMode.value = false
  rejectionReason.value = ''
  if (!offcanvas) {
    offcanvas = new Offcanvas(document.getElementById('appDetailOffcanvas'))
  }
  offcanvas.show()
}

const handleStatusUpdate = async (status) => {
  if (!selectedApp.value) return

  const updateStatus = filters.role === 'tutee'
    ? adminStore.updateTuteeApplicationStatus
    : adminStore.updateTutorApplicationStatus

  processing.value = true
  try {
    await updateStatus(
      selectedApp.value.id,
      status,
      rejectionReason.value,
      { reviewType: selectedReviewType.value }
    )
    await loadApplications()
    offcanvas.hide()
  } catch (err) {
    console.error('Status update failed:', err)
  } finally {
    processing.value = false
  }
}

const handleSubjectReview = async (subject, status) => {
  processingSubject.value = subject.subject_code
  try {
    await adminStore.reviewTutorProposedSubject(
      selectedApp.value.id,
      subject.subject_code,
      status,
    )
    selectedApp.value.proposed_subjects = proposedSubjects.value.filter(
      (item) => item.subject_code !== subject.subject_code,
    )
  } catch (err) {
    console.error('Subject review failed:', err)
  } finally {
    processingSubject.value = ''
  }
}

const getAppReviewStatus = (app) => getReviewStatus(app)

const getAppSubmittedAt = (app) => getReviewSubmittedAt(app)

const getAppReviewedAt = (app) => getReviewReviewedAt(app)

const getAppRejectionReason = (app) => getReviewRejectionReason(app)

const isPendingReview = (app) => getAppReviewStatus(app) === 'pending'

const getReviewTypeLabel = (app) =>
  getApplicationReviewKind(app) === 'renewal' ? 'Renewal' : 'First-time'

const getReviewTypeBadgeClass = (app) =>
  getApplicationReviewKind(app) === 'renewal'
    ? 'bg-info-subtle text-info-emphasis border border-info-subtle'
    : 'bg-secondary-subtle text-secondary-emphasis border border-secondary-subtle'

const getStatusBadgeClass = (status) => {
  switch (status) {
    case 'pending': return 'bg-warning-subtle text-warning-emphasis border border-warning-subtle'
    case 'approved': return 'bg-success-subtle text-success-emphasis border border-success-subtle'
    case 'rejected': return 'bg-danger-subtle text-danger-emphasis border border-danger-subtle'
    default: return 'bg-secondary-subtle text-secondary-emphasis'
  }
}

const formatStatus = (status) => {
  if (!status) return ''
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

const handleImageError = (event) => {
  event.target.src = 'https://placehold.co/400x300?text=Error+Loading+Image'
}

const isPdf = (url) => {
  if (!url) return false
  return url.toLowerCase().endsWith('.pdf') || url.includes('type=pdf')
}

watch(() => [filters.role, filters.status, filters.reviewType], () => {
  loadApplications()
})

onMounted(() => {
  loadApplications()
})
</script>

<style scoped>
.admin-applications {
  background: #fcfcfc;
  min-height: 100vh;
}

.sb-btn {
  font-weight: 500;
}

.doc-preview {
  position: relative;
  background: #eee;
  min-height: 120px;
  cursor: pointer;
  border: 1px solid var(--sb-card-border);
  transition: none;
}

.doc-preview img {
  width: 100%;
  height: 120px;
  object-fit: cover;
}

.doc-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transition: opacity 0.2s;
  font-size: 0.8rem;
  font-weight: 600;
}

.doc-preview:hover .doc-overlay {
  opacity: 1;
}

.doc-preview:hover {
  border-color: var(--sb-primary);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.proposed-subject-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.85rem 0;
  border-bottom: 1px solid var(--sb-card-border);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
