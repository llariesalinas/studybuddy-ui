<template>
  <div class="admin-institutions p-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3 class="mb-0">Partner Institutions</h3>
      <button @click="showAddModal = true" class="btn bg-sb-primary text-white btn-sm rounded-pill px-3 sb-btn">
        <i class="bi bi-plus-lg me-1"></i> Add Institution
      </button>
    </div>

    <!-- Institutions Table -->
    <div class="card border-0 shadow-sm rounded-4 overflow-hidden">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="bg-light">
            <tr>
              <th class="ps-4 py-3">Institution Name</th>
              <th class="py-3">Email Domain</th>
              <th class="py-3">Status</th>
              <th class="py-3">Added Date</th>
              <th class="pe-4 py-3 text-end">Actions</th>
            </tr>
          </thead>

          <tbody>
              <!-- Skeleton rows -->
              <template v-if="store.loading.institutions && !store.institutions.length">
                <tr
                  v-for="i in 6"
                  :key="'inst-sk-' + i"
                  class="placeholder-glow"
                >
                  <td class="ps-4">
                    <span class="placeholder col-8 rounded"></span>
                  </td>

                  <td>
                    <span class="placeholder col-6 rounded"></span>
                  </td>

                  <td>
                    <span class="placeholder col-4 rounded-pill" style="height: 24px; display: inline-block;"></span>
                  </td>

                  <td>
                    <span class="placeholder col-5 rounded"></span>
                  </td>

                  <td class="pe-4 text-end">
                    <span
                      class="placeholder rounded-circle"
                      style="width: 32px; height: 32px; display: inline-block;"
                    ></span>
                  </td>
                </tr>
              </template>

              <!-- Empty state -->
              <template v-else-if="!store.institutions.length">
                <tr key="inst-empty">
                  <td colspan="5" class="text-center py-5 text-muted">
                    <i class="bi bi-building fs-1 mb-2 d-block"></i>
                    <p class="mb-0">No institutions found.</p>
                  </td>
                </tr>
              </template>

              <!-- Real rows -->
              <template v-else>
                <tr
                  v-for="inst in store.institutions"
                  :key="inst.id"
                >
                  <td class="ps-4 fw-bold text-dark">
                    {{ inst.institution_name }}
                  </td>

                  <td>
                    <code>{{ inst.school_email_domain }}</code>
                  </td>

                  <td>
                    <span
                      :class="inst.is_active
                        ? 'badge bg-success-subtle text-success'
                        : 'badge bg-secondary-subtle text-secondary'"
                      class="rounded-pill px-3"
                    >
                      {{ inst.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </td>

                  <td class="small text-muted">
                    {{ formatDate(inst.date_added) }}
                  </td>

                  <td class="pe-4 text-end">
                    <button
                      @click="openDetail(inst)"
                      class="btn btn-sm btn-light rounded-circle sb-btn"
                    >
                      <i class="bi bi-pencil"></i>
                    </button>
                  </td>
                </tr>
              </template>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Offcanvas -->
    <div
      class="offcanvas offcanvas-end border-0 shadow"
      :class="{ show: selectedInstitution }"
      tabindex="-1"
      style="width: 450px;"
    >
      <div class="offcanvas-header bg-light">
        <h5 class="offcanvas-title fw-bold">
          Institution Details
        </h5>

        <button
          @click="selectedInstitution = null"
          type="button"
          class="btn-close shadow-none"
        ></button>
      </div>

      <div
        v-if="selectedInstitution"
        class="offcanvas-body"
      >
        <div class="text-center mb-4">
          <div
            class="avatar-lg bg-primary-subtle text-primary rounded-circle d-flex align-items-center justify-content-center fw-bold mx-auto mb-3"
            style="width: 80px; height: 80px; font-size: 2rem;"
          >
            {{ selectedInstitution.institution_name[0] }}
          </div>

          <h4 class="fw-bold mb-1">
            {{ selectedInstitution.institution_name }}
          </h4>

          <p class="text-muted mb-3">
            {{ selectedInstitution.school_email_domain }}
          </p>

          <div class="d-flex justify-content-center gap-2">
            <span
              :class="selectedInstitution.is_active
                ? 'badge bg-success rounded-pill px-3'
                : 'badge bg-secondary rounded-pill px-3'"
            >
              {{ selectedInstitution.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
        </div>

        <div class="mt-4 pt-4 border-top">
          <button
            @click="toggleActive(selectedInstitution)"
            :disabled="toggling"
            class="btn w-100 mb-2 rounded-pill py-2 sb-btn"
            :class="selectedInstitution.is_active ? 'btn-outline-danger' : 'btn-success'"
          >
            <span v-if="toggling" class="spinner-border spinner-border-sm me-2"></span>
            {{ toggling ? 'Updating...' : selectedInstitution.is_active ? 'Deactivate Institution' : 'Reactivate Institution' }}
          </button>
        </div>
      </div>
    </div>
    <div v-if="selectedInstitution" @click="selectedInstitution = null" class="offcanvas-backdrop fade show"></div>

    <!-- Add Modal -->
    <div
      v-if="showAddModal"
      class="modal-backdrop fade show"
    ></div>

    <div
      class="modal fade"
      :class="{ show: showAddModal, 'd-block': showAddModal }"
      tabindex="-1"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow rounded-4 p-2">
          <div class="modal-header border-0">
            <h5 class="modal-title fw-bold">
              Add New Institution
            </h5>

            <button
              @click="showAddModal = false"
              type="button"
              class="btn-close shadow-none"
            ></button>
          </div>

          <div class="modal-body">
            <form @submit.prevent="submitAdd">
              <div class="mb-3">
                <label class="form-label small fw-bold">
                  INSTITUTION NAME
                </label>

                <input
                  v-model="form.institution_name"
                  type="text"
                  class="form-control rounded-3 sb-field"
                  required
                  placeholder="e.g. University of the Philippines"
                >
              </div>

              <div class="mb-3">
                <label class="form-label small fw-bold">
                  EMAIL DOMAIN
                </label>

                <input
                  v-model="form.school_email_domain"
                  type="text"
                  class="form-control rounded-3 sb-field"
                  required
                  placeholder="e.g. up.edu.ph"
                >
              </div>

              <div class="mb-4">
                <label class="form-label small fw-bold">
                  CONTACT PERSON (OPTIONAL)
                </label>

                <input
                  v-model="form.contact_person"
                  type="text"
                  class="form-control rounded-3 sb-field"
                  placeholder="Name or Department"
                >
              </div>

              <div class="d-flex gap-2 mt-4">
                <button
                  type="button"
                  @click="showAddModal = false"
                  class="btn btn-light rounded-pill w-100 py-2 sb-btn"
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  class="btn bg-sb-primary text-white rounded-pill w-100 py-2 sb-btn"
                >
                  Save Institution
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useAdminStore } from '@/stores/admin';
import { useToastStore } from '@/stores/toast'

const store = useAdminStore()
const toastStore = useToastStore()
const showAddModal = ref(false)

const selectedInstitution = ref(null)

const openDetail = (institution) => {
  selectedInstitution.value = institution
}

const toggling = ref(false)

const toggleActive = async (inst) => {
  const action = inst.is_active ? 'deactivate' : 'reactivate'
  if (confirm(`Are you sure you want to ${action} ${inst.institution_name}?`)) {
    toggling.value = true
    try {
      await store.toggleInstitutionActive(inst.id, !inst.is_active)

      // Since the store fetches institutions again, we need to update selectedInstitution
      // to the new object in the store to reflect the UI change immediately if the panel stays open.
      const updated = store.institutions.find(i => i.id === inst.id)
      if (updated) {
        selectedInstitution.value = updated
      }
    } catch {
      toastStore.push('Failed to update institution status.', 'error')
    } finally {
      toggling.value = false
    }
  }
}

const form = reactive({
  institution_name: '',
  school_email_domain: '',
  contact_person: '',
})

onMounted(() => {
  store.fetchInstitutions()
})

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const submitAdd = async () => {
  try {
    await store.addInstitution(form)
    showAddModal.value = false
    Object.assign(form, { institution_name: '', school_email_domain: '', contact_person: '' })
  } catch {
    toastStore.push('Failed to add institution. Domain might already exist.', 'error')
  }
}
</script>

<style scoped>
.letter-spacing-05 { letter-spacing: 0.05em; }
code { color: var(--sb-primary); background: #f8f9fa; padding: 2px 6px; border-radius: 4px; }
.admin-institutions .table thead th { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: none; }
</style>
