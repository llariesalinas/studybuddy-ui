<template>
  <div class="admin-course-catalog p-4">
    <div class="d-flex flex-wrap justify-content-between align-items-start gap-3 mb-4">
      <div>
        <p class="text-uppercase text-muted small fw-bold mb-1">Platform catalog</p>
        <h3 class="mb-1">Subjects and courses</h3>
        <p class="text-muted mb-0">
          Manage the global subject list available to every partner institution.
        </p>
      </div>
      <button
        type="button"
        class="btn bg-sb-primary text-white btn-sm rounded-pill px-3 sb-btn"
        @click="startCreate"
      >
        <i class="bi bi-plus-lg me-1"></i>
        Add subject
      </button>
    </div>

    <form
      v-if="showForm"
      class="row g-3 align-items-end border rounded-4 bg-white shadow-sm p-3 mb-4"
      @submit.prevent="saveSubject"
    >
      <div class="col-12 col-md-2">
        <label class="form-label small fw-bold">SUBJECT CODE</label>
        <input
          v-model.trim="form.subject_code"
          class="form-control rounded-3 sb-field"
          :disabled="Boolean(editingCode)"
          required
        >
      </div>
      <div class="col-12 col-md-4">
        <label class="form-label small fw-bold">SUBJECT NAME</label>
        <input v-model.trim="form.subject_name" class="form-control rounded-3 sb-field" required>
      </div>
      <div class="col-12 col-md-3">
        <label class="form-label small fw-bold">DEPARTMENT</label>
        <input v-model.trim="form.department" class="form-control rounded-3 sb-field" required>
      </div>
      <div class="col-12 col-md-3">
        <label class="form-label small fw-bold">COURSE</label>
        <select v-model="form.category" class="form-select rounded-3 sb-field">
          <option value="">Uncategorized</option>
          <option
            v-for="course in catalogStore.courses"
            :key="course.course_code"
            :value="course.course_code"
          >
            {{ course.course_code }} — {{ course.course_name }}
          </option>
        </select>
      </div>
      <div class="col-12 d-flex justify-content-end gap-2">
        <button type="button" class="btn btn-light rounded-pill px-3" @click="cancelForm">
          Cancel
        </button>
        <button class="btn bg-sb-primary text-white rounded-pill px-3" :disabled="saving">
          <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
          {{ editingCode ? 'Save changes' : 'Add subject' }}
        </button>
      </div>
    </form>

    <div class="border rounded-4 bg-white shadow-sm overflow-hidden">
      <div class="catalog-toolbar p-3 border-bottom">
        <input
          v-model.trim="search"
          class="form-control rounded-3 sb-field"
          placeholder="Search by code, name, department, or course"
        >
      </div>

      <div v-if="loading" class="p-4 placeholder-glow">
        <span v-for="index in 6" :key="index" class="placeholder col-12 rounded mb-3"></span>
      </div>
      <div v-else-if="!filteredSubjects.length" class="p-5 text-center text-muted">
        <i class="bi bi-inbox fs-2 d-block mb-2"></i>
        No subjects match this search.
      </div>
      <div v-else class="table-responsive">
        <table class="table align-middle mb-0">
          <thead>
            <tr>
              <th>Subject</th>
              <th>Department</th>
              <th>Course</th>
              <th class="text-end">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="subject in filteredSubjects" :key="subject.subject_code">
              <td>
                <div class="fw-semibold">{{ subject.subject_code }}</div>
                <div class="small text-muted">{{ subject.subject_name }}</div>
              </td>
              <td>{{ subject.department }}</td>
              <td>{{ subject.category || 'Uncategorized' }}</td>
              <td class="text-end">
                <button
                  type="button"
                  class="btn btn-sm btn-light rounded-circle me-2"
                  :aria-label="`Edit ${subject.subject_code}`"
                  @click="startEdit(subject)"
                >
                  <i class="bi bi-pencil"></i>
                </button>
                <button
                  type="button"
                  class="btn btn-sm btn-light rounded-circle"
                  :disabled="removingCode === subject.subject_code"
                  :aria-label="`Remove ${subject.subject_code}`"
                  @click="removeSubject(subject)"
                >
                  <span
                    v-if="removingCode === subject.subject_code"
                    class="spinner-border spinner-border-sm"
                  ></span>
                  <i v-else class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useCatalogStore } from '@/stores/catalog'
import { useToastStore } from '@/stores/toast'

const catalogStore = useCatalogStore()
const toastStore = useToastStore()

const search = ref('')
const loading = ref(false)
const saving = ref(false)
const removingCode = ref(null)
const showForm = ref(false)
const editingCode = ref(null)
const form = reactive({
  subject_code: '',
  subject_name: '',
  department: '',
  category: '',
})

const filteredSubjects = computed(() => {
  const query = search.value.toLowerCase()
  return catalogStore.courseCatalog.filter((subject) => {
    if (!query) return true
    return [subject.subject_code, subject.subject_name, subject.department, subject.category]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(query))
  })
})

function resetForm() {
  Object.assign(form, { subject_code: '', subject_name: '', department: '', category: '' })
  editingCode.value = null
}

function startCreate() {
  resetForm()
  showForm.value = true
}

function startEdit(subject) {
  editingCode.value = subject.subject_code
  Object.assign(form, {
    subject_code: subject.subject_code,
    subject_name: subject.subject_name,
    department: subject.department,
    category: subject.category || '',
  })
  showForm.value = true
}

function cancelForm() {
  showForm.value = false
  resetForm()
}

async function saveSubject() {
  saving.value = true
  try {
    const payload = { ...form }
    if (editingCode.value) {
      delete payload.subject_code
      await catalogStore.updateCatalogSubject(editingCode.value, payload)
      toastStore.push('Subject updated.', 'success')
    } else {
      await catalogStore.addCatalogSubject(payload)
      toastStore.push('Subject added.', 'success')
    }
    cancelForm()
  } catch {
    toastStore.push('Failed to save subject. Check that the code is unique.', 'error')
  } finally {
    saving.value = false
  }
}

async function removeSubject(subject) {
  removingCode.value = subject.subject_code
  try {
    await catalogStore.removeCatalogSubject(subject.subject_code)
    toastStore.push('Subject removed.', 'success')
  } catch {
    toastStore.push('Failed to remove subject.', 'error')
  } finally {
    removingCode.value = null
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      catalogStore.fetchCourses({ force: true }),
      catalogStore.fetchCourseCatalog(),
    ])
  } catch {
    toastStore.push('Failed to load the global catalog.', 'error')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.catalog-toolbar {
  max-width: 520px;
}

.placeholder {
  display: block;
  height: 44px;
}
</style>
