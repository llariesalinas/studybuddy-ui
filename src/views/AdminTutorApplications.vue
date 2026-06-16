<template>
  <div class="admin-applications p-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3 class="mb-0">Tutor Applications</h3>
      <div class="d-flex gap-2">
        <select v-model="filters.status" class="form-select form-select-sm rounded-pill" style="width: 150px;">
          <option value="">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
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
                <th class="py-3">Status</th>
                <th class="py-3">Submitted</th>
                <th class="pe-4 py-3 text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in adminStore.tutorApplications" :key="app.id">
                <td class="ps-4">
                  <p class="mb-0 fw-bold">{{ app.applicant_name }}</p>
                  <p class="small text-muted mb-0">{{ app.email }}</p>
                </td>
                <td class="small">{{ app.institution_name }}</td>
                <td>
                  <span :class="['badge rounded-pill px-3', getStatusBadgeClass(app.application_status)]">
                    {{ formatStatus(app.application_status) }}
                  </span>
                </td>
                <td class="small text-muted">{{ formatDate(app.submitted_at) }}</td>
                <td class="pe-4 text-end">
                  <button @click="viewDetails(app)" class="btn btn-sm btn-light rounded-pill px-3 sb-btn">
                    Review
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-if="!adminStore.tutorApplications.length" class="text-center py-5">
            <i class="bi bi-inbox text-muted mb-3 d-block" style="font-size: 2rem;"></i>
            <p class="text-muted">No applications found matching your filter.</p>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Application Detail Offcanvas -->
    <div class="offcanvas offcanvas-end border-0 shadow" tabindex="-1" id="appDetailOffcanvas" style="width: 500px;">
      <div class="offcanvas-header bg-light border-bottom">
        <h5 class="offcanvas-title fw-bold">Review Application</h5>
        <button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
      </div>
      <div v-if="selectedApp" class="offcanvas-body p-4">
        <div class="mb-4">
          <label class="text-muted small text-uppercase fw-bold mb-1">Applicant Information</label>
          <div class="p-3 bg-light rounded-3">
            <h5 class="mb-1 fw-bold">{{ selectedApp.applicant_name }}</h5>
            <p class="mb-1 small"><i class="bi bi-envelope me-2"></i>{{ selectedApp.email }}</p>
            <p class="mb-0 small"><i class="bi bi-building me-2"></i>{{ selectedApp.institution_name }}</p>
          </div>
        </div>

        <div v-if="selectedApp.reason_to_tutor" class="mb-4">
          <label class="text-muted small text-uppercase fw-bold mb-1">Motivation</label>
          <blockquote class="p-3 bg-light rounded-3 border-start border-primary border-4 small mb-0">
            "{{ selectedApp.reason_to_tutor }}"
          </blockquote>
        </div>

        <div class="mb-4">
          <label class="text-muted small text-uppercase fw-bold mb-2">Documents</label>
          <div class="row g-3">
            <div class="col-6">
              <div class="doc-card">
                <div class="small fw-bold mb-2 text-center text-muted">School ID</div>
                <a :href="selectedApp.school_id_url" target="_blank" class="doc-preview rounded-3 overflow-hidden d-block bg-white shadow-sm border">
                  <img :src="selectedApp.school_id_url" class="img-fluid" alt="School ID" @error="handleImageError" />
                  <div class="doc-overlay"><i class="bi bi-zoom-in me-1"></i> View Full</div>
                </a>
              </div>
            </div>
            <div class="col-6">
              <div class="doc-card">
                <div class="small fw-bold mb-2 text-center text-muted">Enrollment Proof</div>
                <div v-if="isPdf(selectedApp.enrollment_proof_url)" class="doc-preview rounded-3 bg-white d-flex align-items-center justify-content-center flex-column text-danger shadow-sm border">
                   <i class="bi bi-file-earmark-pdf" style="font-size: 2.5rem;"></i>
                   <span class="small mt-1 fw-bold">PDF File</span>
                   <a :href="selectedApp.enrollment_proof_url" target="_blank" class="doc-overlay text-white"><i class="bi bi-download me-1"></i> View PDF</a>
                </div>
                <a v-else :href="selectedApp.enrollment_proof_url" target="_blank" class="doc-preview rounded-3 overflow-hidden d-block bg-white shadow-sm border">
                  <img :src="selectedApp.enrollment_proof_url" class="img-fluid" alt="Enrollment Proof" @error="handleImageError" />
                  <div class="doc-overlay"><i class="bi bi-zoom-in me-1"></i> View Full</div>
                </a>
              </div>
            </div>
          </div>
        </div>

        <div v-if="selectedApp.application_status === 'pending'" class="mt-5 pt-3 border-top">
          <div v-if="rejectionMode">
            <label class="form-label fw-bold small">Reason for Rejection</label>
            <textarea v-model="rejectionReason" class="form-control mb-3" rows="3" placeholder="Explain why the application is being rejected..."></textarea>
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
              {{ processing ? 'Processing...' : 'Approve Applicant' }}
            </button>
            <button @click="rejectionMode = true" class="btn btn-outline-danger flex-grow-1 rounded-pill" :disabled="processing">
              Reject
            </button>
          </div>
        </div>
        <div v-else class="mt-5 pt-3 border-top">
           <div :class="['p-3 rounded-3 text-center', selectedApp.application_status === 'approved' ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger']">
             This application has already been <strong>{{ selectedApp.application_status }}</strong>.
             <p v-if="selectedApp.reviewed_at" class="small mb-0 mt-1">Reviewed on {{ formatDate(selectedApp.reviewed_at) }}</p>
           </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { Offcanvas } from 'bootstrap'

const adminStore = useAdminStore()
const filters = reactive({
  status: 'pending'
})

const selectedApp = ref(null)
const rejectionMode = ref(false)
const rejectionReason = ref('')
const processing = ref(false)
let offcanvas = null

const loadApplications = async () => {
  await adminStore.fetchTutorApplications(filters.status, true)
}

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
  
  processing.value = true
  try {
    await adminStore.updateTutorApplicationStatus(selectedApp.value.id, status, rejectionReason.value)
    offcanvas.hide()
    // Notifications/Toast here? admin store should handle refresh
  } catch (err) {
    console.error('Status update failed:', err)
  } finally {
    processing.value = false
  }
}

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

watch(() => filters.status, () => {
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
  transition: all 0.2s;
  font-weight: 500;
}

.sb-btn:hover {
  transform: translateY(-1px);
}

.doc-preview {
  position: relative;
  background: #eee;
  min-height: 120px;
  cursor: pointer;
  border: 1px solid var(--sb-card-border);
  transition: all 0.2s;
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

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
