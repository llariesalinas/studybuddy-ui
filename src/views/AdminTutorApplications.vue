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
    <div class="offcanvas offcanvas-end border-0 shadow" tabindex="-1" id="appDetailOffcanvas" style="width: 760px;">
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
            :class="{ editing: editingSubjectCode === subject.subject_code }"
          >
            <template v-if="editingSubjectCode === subject.subject_code">
              <div class="proposed-subject-edit-form">
                <div class="mb-2">
                  <label class="form-label small fw-bold">Subject name</label>
                  <input v-model.trim="subjectEditForm.subject_name" class="form-control form-control-sm sb-field">
                </div>
                <div class="two-up-fields">
                  <div class="mb-2">
                    <label class="form-label small fw-bold">Category</label>
                    <template v-if="categoryMode === 'new'">
                      <div v-if="categoryMismatchNote" class="category-mismatch-note small mb-2">
                        <i class="bi bi-exclamation-triangle me-1"></i>{{ categoryMismatchNote }}
                      </div>
                      <input v-model.trim="subjectEditForm.category" class="form-control form-control-sm sb-field" placeholder="New category name">
                      <button type="button" class="btn btn-link btn-sm px-0 mt-1" @click="useExistingCategory">
                        Pick an existing category instead
                      </button>
                    </template>
                    <template v-else>
                      <select
                        v-model="subjectEditForm.category"
                        class="form-select form-select-sm sb-field"
                        @change="handleCategorySelectChange"
                      >
                        <option v-for="category in taxonomyCategories" :key="category" :value="category">{{ category }}</option>
                        <option value="__add_new__">+ Add new category...</option>
                      </select>
                    </template>
                  </div>
                  <div class="mb-2">
                    <label class="form-label small fw-bold">Sub-Group</label>
                    <template v-if="subgroupMode === 'new'">
                      <div v-if="subgroupMismatchNote" class="category-mismatch-note small mb-2">
                        <i class="bi bi-exclamation-triangle me-1"></i>{{ subgroupMismatchNote }}
                      </div>
                      <input v-model.trim="subjectEditForm.department" class="form-control form-control-sm sb-field" placeholder="New sub-group name">
                      <button type="button" class="btn btn-link btn-sm px-0 mt-1" @click="useExistingSubgroup">
                        Pick an existing sub-group instead
                      </button>
                    </template>
                    <template v-else>
                      <select
                        v-model="subjectEditForm.department"
                        class="form-select form-select-sm sb-field"
                        @change="handleSubgroupSelectChange"
                      >
                        <option value="">None</option>
                        <option v-for="subgroup in subgroupOptions" :key="subgroup" :value="subgroup">{{ subgroup }}</option>
                        <option value="__add_new__">+ Add new sub-group...</option>
                      </select>
                    </template>
                  </div>
                </div>
                <div class="mb-2 keyword-field">
                  <label class="form-label small fw-bold">Keywords</label>
                  <input
                    v-model.trim="subjectEditForm.keywords"
                    class="form-control form-control-sm sb-field"
                    placeholder="Comma-separated synonyms, e.g. coding, programming, cs"
                    autocomplete="off"
                    @focus="keywordSuggestionsOpen = true"
                    @blur="keywordSuggestionsOpen = false"
                  >
                  <div v-if="keywordSuggestionsOpen && keywordFragment" class="keyword-suggestions">
                    <div v-if="keywordSuggestions.length" class="keyword-suggestions-hint">Matching existing catalog keywords</div>
                    <button
                      v-for="keyword in keywordSuggestions"
                      :key="keyword"
                      type="button"
                      class="keyword-suggestion"
                      @mousedown.prevent="selectKeywordSuggestion(keyword)"
                    >
                      <template v-for="(segment, i) in highlightSegments(keyword, keywordFragment)" :key="i">
                        <strong v-if="segment.match">{{ segment.text }}</strong>
                        <template v-else>{{ segment.text }}</template>
                      </template>
                    </button>
                    <button
                      v-if="!keywordFragmentExists"
                      type="button"
                      class="keyword-suggestion keyword-add-new"
                      @mousedown.prevent="selectKeywordSuggestion(keywordFragment)"
                    >
                      + Use "{{ keywordFragment }}" as a new keyword
                    </button>
                  </div>
                </div>
                <div v-if="subject.tutor_note" class="mb-2">
                  <label class="form-label small fw-bold">Tutor's note</label>
                  <p class="tutor-note-readonly small mb-0">{{ subject.tutor_note }}</p>
                </div>
                <div class="mb-2">
                  <label class="form-label small fw-bold">Catalog description</label>
                  <textarea v-model.trim="subjectEditForm.catalog_description" class="form-control form-control-sm sb-field" rows="2" placeholder="Shown to every user and searched by the subject pickers"></textarea>
                </div>
                <div class="d-flex gap-2">
                  <button
                    class="btn btn-sm btn-primary rounded-pill"
                    :disabled="savingSubjectEdit"
                    @click="saveSubjectEdit(subject)"
                  >
                    {{ savingSubjectEdit ? 'Saving...' : 'Save changes' }}
                  </button>
                  <button class="btn btn-sm btn-light rounded-pill" :disabled="savingSubjectEdit" @click="cancelSubjectEdit">
                    Cancel
                  </button>
                </div>
              </div>
            </template>
            <template v-else>
              <div>
                <div class="fw-bold">{{ subject.subject_name }}</div>
                <div class="small text-muted">{{ subject.category }}</div>
              </div>
              <div class="d-flex gap-2">
                <button
                  class="btn btn-sm btn-outline-secondary rounded-pill"
                  :disabled="processingSubject === subject.subject_code"
                  @click="startSubjectEdit(subject)"
                >
                  Edit
                </button>
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
            </template>
          </div>
        </div>

        <div v-if="isInitialTutorReview" class="mb-4">
          <label class="text-muted small text-uppercase fw-bold mb-2">Selected from catalog</label>
          <div v-if="selectedSubjects.length" class="selected-subject-list">
            <span
              v-for="subject in selectedSubjects"
              :key="subject.subject_code"
              class="selected-subject-chip"
            >
              {{ subject.subject_name }}
              <small class="text-muted">{{ subject.category }}</small>
            </span>
          </div>
          <p v-else class="small text-muted mb-0">No catalog subjects selected.</p>
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
import { useRoute } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import { useCatalogStore } from '@/stores/catalog'
import { useToastStore } from '@/stores/toast'
import { Offcanvas } from 'bootstrap'
import {
  getApplicationReviewKind,
  getReviewRejectionReason,
  getReviewReviewedAt,
  getReviewStatus,
  getReviewSubmittedAt,
} from '@/services/tutorApplicationState'
import { deriveCategoryOptions, deriveSubgroupOptions } from '@/constants/subjectTaxonomy'
import { highlightSegments } from '@/components/subjectPicker.shared'

const APPLICANT_ROLES = ['tutor', 'tutee']
const APPLICATION_STATUSES = ['pending', 'approved', 'rejected']

const adminStore = useAdminStore()
const catalogStore = useCatalogStore()
const toastStore = useToastStore()
const route = useRoute()
// Deep links (e.g. the SuperAdmin dashboard's pending-review queue) may preselect the tab and
// status; anything unrecognised falls back to the default pending-tutor view.
const filters = reactive({
  role: APPLICANT_ROLES.includes(route.query.role) ? route.query.role : 'tutor',
  status: APPLICATION_STATUSES.includes(route.query.status) ? route.query.status : 'pending',
  reviewType: ''
})

const selectedApp = ref(null)
const rejectionMode = ref(false)
const rejectionReason = ref('')
const processing = ref(false)
const processingSubject = ref('')
const editingSubjectCode = ref('')
const savingSubjectEdit = ref(false)
const subjectEditForm = reactive({
  subject_name: '',
  category: '',
  department: '',
  keywords: '',
  catalog_description: '',
})
// 'select' shows the taxonomy dropdown; 'new' shows the free-text "add a category" input,
// entered either by picking "+ Add new category..." or automatically when a proposed subject's
// category doesn't match anything in the derived list.
const categoryMode = ref('select')
const categoryMismatchNote = ref('')
// Same two-mode pattern as Category, scoped to whichever category is currently selected.
const subgroupMode = ref('select')
const subgroupMismatchNote = ref('')
let offcanvas = null

const taxonomyCategories = computed(() => deriveCategoryOptions(catalogStore.courseCatalog))

// Sub-group values already used by subjects under the currently-selected category — a suggestion
// list only, not an enforced relationship (see deriveSubgroupOptions).
const subgroupOptions = computed(() =>
  deriveSubgroupOptions(catalogStore.courseCatalog, subjectEditForm.category)
)

const catalogKeywords = computed(() => {
  const keywords = new Set()
  for (const subject of catalogStore.courseCatalog) {
    for (const keyword of (subject.keywords || '').split(',')) {
      const trimmed = keyword.trim()
      if (trimmed) keywords.add(trimmed)
    }
  }
  return [...keywords].sort()
})

// Custom dropdown instead of a native <datalist> — datalist popups render with unstyled OS/browser
// chrome that clashes with the rest of the form.
const keywordSuggestionsOpen = ref(false)

// The comma-separated fragment currently being typed (what suggestions match against).
const keywordFragment = computed(() => {
  const enteredKeywords = subjectEditForm.keywords.split(',').map((kw) => kw.trim())
  return enteredKeywords[enteredKeywords.length - 1] || ''
})

const keywordSuggestions = computed(() => {
  const fragment = keywordFragment.value.toLowerCase()
  if (!fragment) return []
  const enteredKeywords = subjectEditForm.keywords.split(',').map((kw) => kw.trim().toLowerCase())
  const alreadyEntered = new Set(enteredKeywords.filter(Boolean))

  return catalogKeywords.value
    .filter((keyword) => !alreadyEntered.has(keyword.toLowerCase()))
    .filter((keyword) => keyword.toLowerCase().includes(fragment))
    .slice(0, 8)
})

// Whether the typed fragment already exists as a catalog keyword verbatim — if so, "add as new" is
// redundant with just picking the matching suggestion.
const keywordFragmentExists = computed(() =>
  catalogKeywords.value.some((keyword) => keyword.toLowerCase() === keywordFragment.value.toLowerCase())
)

const selectKeywordSuggestion = (keyword) => {
  const lastComma = subjectEditForm.keywords.lastIndexOf(',')
  const prefix = lastComma === -1 ? '' : `${subjectEditForm.keywords.slice(0, lastComma + 1)} `
  subjectEditForm.keywords = `${prefix}${keyword}, `
}

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

const isInitialTutorReview = computed(
  () => filters.role === 'tutor' && selectedReviewType.value === 'initial'
)

const proposedSubjects = computed(() => {
  if (!isInitialTutorReview.value) return []
  return selectedApp.value?.proposed_subjects || []
})

const selectedSubjects = computed(() => {
  if (!isInitialTutorReview.value) return []
  return selectedApp.value?.selected_subjects || []
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
  editingSubjectCode.value = ''
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
    // Approving flips the subject's backend status to 'approved', which changes what tutee-facing
    // pickers should return from the cached subjects/ fetch — burst it so they see it immediately.
    if (status === 'approved') {
      catalogStore.invalidateSubjectsCache()
    }
  } catch (err) {
    console.error('Subject review failed:', err)
  } finally {
    processingSubject.value = ''
  }
}

const startSubjectEdit = (subject) => {
  editingSubjectCode.value = subject.subject_code
  Object.assign(subjectEditForm, {
    subject_name: subject.subject_name,
    category: subject.category,
    department: subject.department || '',
    keywords: subject.keywords || '',
    // Proposals arrive with no catalog copy; prefill from the tutor's note so
    // the admin edits a draft rather than starting from an empty box.
    catalog_description: subject.catalog_description || subject.tutor_note || '',
  })

  if (subject.category && !taxonomyCategories.value.includes(subject.category)) {
    categoryMode.value = 'new'
    categoryMismatchNote.value = `"${subject.category}" — not in the catalog yet`
  } else {
    categoryMode.value = 'select'
    categoryMismatchNote.value = ''
  }

  if (subject.department && !subgroupOptions.value.includes(subject.department)) {
    subgroupMode.value = 'new'
    subgroupMismatchNote.value = `"${subject.department}" — not in the catalog yet`
  } else {
    subgroupMode.value = 'select'
    subgroupMismatchNote.value = ''
  }
}

const handleCategorySelectChange = () => {
  if (subjectEditForm.category === '__add_new__') {
    subjectEditForm.category = ''
    categoryMode.value = 'new'
    categoryMismatchNote.value = ''
  }
}

const useExistingCategory = () => {
  categoryMode.value = 'select'
  categoryMismatchNote.value = ''
  if (!taxonomyCategories.value.includes(subjectEditForm.category)) {
    subjectEditForm.category = taxonomyCategories.value[0] || ''
  }
}

const handleSubgroupSelectChange = () => {
  if (subjectEditForm.department === '__add_new__') {
    subjectEditForm.department = ''
    subgroupMode.value = 'new'
    subgroupMismatchNote.value = ''
  }
}

const useExistingSubgroup = () => {
  subgroupMode.value = 'select'
  subgroupMismatchNote.value = ''
  if (!subgroupOptions.value.includes(subjectEditForm.department)) {
    subjectEditForm.department = ''
  }
}

const cancelSubjectEdit = () => {
  editingSubjectCode.value = ''
  categoryMode.value = 'select'
  categoryMismatchNote.value = ''
  subgroupMode.value = 'select'
  subgroupMismatchNote.value = ''
}

const saveSubjectEdit = async (subject) => {
  const isNewCategory = categoryMode.value === 'new'
    && subjectEditForm.category
    && !taxonomyCategories.value.includes(subjectEditForm.category)
  const isNewSubgroup = subgroupMode.value === 'new'
    && subjectEditForm.department
    && !subgroupOptions.value.includes(subjectEditForm.department)

  savingSubjectEdit.value = true
  try {
    const updated = await adminStore.updateTutorProposedSubject(
      selectedApp.value.id,
      subject.subject_code,
      { ...subjectEditForm },
    )
    Object.assign(subject, updated, { catalog_description: subjectEditForm.catalog_description })
    // Sync into the catalog store immediately so the category/sub-group (and keyword) pickers
    // reflect this save without waiting on the next fetchCourseCatalog().
    catalogStore.upsertLocalCatalogSubject(subject)
    editingSubjectCode.value = ''
    categoryMode.value = 'select'
    categoryMismatchNote.value = ''
    subgroupMode.value = 'select'
    subgroupMismatchNote.value = ''
    if (isNewCategory) {
      toastStore.push(`"${subjectEditForm.category}" added as a new category.`, 'success')
    }
    if (isNewSubgroup) {
      toastStore.push(`"${subjectEditForm.department}" added as a new sub-group.`, 'success')
    }
  } catch (err) {
    console.error('Subject update failed:', err)
    toastStore.push(err?.response?.data?.error || 'Failed to save subject changes.', 'error')
  } finally {
    savingSubjectEdit.value = false
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
  if (!catalogStore.courseCatalog.length) {
    catalogStore.fetchCourseCatalog().catch((err) => console.error('Catalog fetch failed:', err))
  }
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

.proposed-subject-row.editing {
  flex-direction: column;
  align-items: stretch;
}

.tutor-note-readonly {
  padding: 0.5rem 0.65rem;
  border-radius: 0.5rem;
  border: 1px solid var(--sb-card-border);
  background: var(--sb-surface-muted, var(--sb-card-bg));
  color: var(--sb-text-muted);
}

.selected-subject-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.selected-subject-chip {
  display: inline-flex;
  align-items: baseline;
  gap: 0.4rem;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  border: 1px solid var(--sb-card-border);
  background: var(--sb-card-bg);
  font-size: 0.82rem;
}

.proposed-subject-edit-form {
  width: 100%;
}

.category-mismatch-note {
  padding: 0.5rem 0.65rem;
  border-radius: 0.5rem;
  border: 1px solid var(--sb-warning-bg, #ffc107);
  background: color-mix(in srgb, var(--sb-warning-bg, #ffc107) 12%, white);
  color: var(--sb-warning-text, #997404);
}

.two-up-fields {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.keyword-field {
  position: relative;
}

.keyword-suggestions-hint {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-weight: 700;
  color: var(--sb-text-muted);
  padding: 0.4rem 0.65rem 0.15rem;
}

.keyword-add-new {
  border-top: 1px dashed var(--sb-card-border);
  color: var(--sb-primary);
  font-weight: 700;
}

.keyword-suggestions {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  z-index: 5;
  max-height: 180px;
  overflow-y: auto;
  background: var(--sb-card-bg, #fff);
  border: 1px solid var(--sb-card-border);
  border-radius: 0.5rem;
  box-shadow: var(--sb-shadow-hover, 0 8px 24px rgba(15, 23, 42, 0.12));
}

.keyword-suggestion {
  display: block;
  width: 100%;
  padding: 0.4rem 0.65rem;
  border: 0;
  background: none;
  text-align: left;
  font-size: 0.8rem;
  color: var(--sb-text-main);
}

.keyword-suggestion:hover,
.keyword-suggestion:focus {
  background: var(--sb-green-tint, var(--sb-primary-light));
  color: var(--sb-primary);
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
