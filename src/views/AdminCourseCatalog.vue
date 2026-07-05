<template>
  <div class="admin-course-catalog p-4">
    <div class="d-flex flex-wrap justify-content-between align-items-start gap-3 mb-4">
      <div>
        <p class="text-uppercase text-muted small fw-bold mb-1">Institution catalog</p>
        <h3 class="mb-1">Course Catalog</h3>
        <p class="text-muted mb-0">
          Curate the subjects recognized under each course for your institution.
        </p>
      </div>

      <button
        class="btn bg-sb-primary text-white btn-sm rounded-pill px-3 sb-btn"
        :disabled="!selectedCourse || loading"
        @click="showCustomForm = !showCustomForm"
      >
        <i class="bi bi-plus-lg me-1"></i>
        Custom Subject
      </button>
    </div>

    <div class="catalog-toolbar border rounded-4 bg-white shadow-sm p-3 mb-4">
      <div class="row g-3 align-items-end">
        <div v-if="isSuperAdmin" class="col-12 col-lg-5">
          <label class="form-label small fw-bold">INSTITUTION</label>
          <select
            v-model="selectedInstitutionId"
            class="form-select rounded-3 sb-field"
            @change="reloadForSelection"
          >
            <option disabled value="">Select institution</option>
            <option
              v-for="institution in catalogStore.institutions"
              :key="institution.id"
              :value="institution.id"
            >
              {{ institution.institution_name }}
            </option>
          </select>
        </div>

        <div class="col-12" :class="isSuperAdmin ? 'col-lg-5' : 'col-lg-7'">
          <label class="form-label small fw-bold">COURSE</label>
          <button
            type="button"
            class="btn btn-outline-secondary rounded-3 sb-field w-100 text-start d-flex justify-content-between align-items-center"
            :disabled="isSuperAdmin && !selectedInstitutionId"
            @click="openCourseModal"
          >
            <span v-if="selectedCourse">
              {{ selectedCourse }} &mdash; {{ selectedCourseName }}
            </span>
            <span v-else class="text-muted">Select course</span>
            <i class="bi bi-chevron-down ms-2"></i>
          </button>
        </div>

        <div class="col-12 col-lg-2 d-grid">
          <button class="btn btn-light rounded-pill sb-btn" :disabled="loading" @click="reloadForSelection">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- Course picker modal -->
    <div v-if="showCourseModal" class="modal-backdrop fade show"></div>

    <div
      class="modal fade"
      :class="{ show: showCourseModal, 'd-block': showCourseModal }"
      tabindex="-1"
      aria-labelledby="coursePickerModalLabel"
      @click.self="showCourseModal = false"
    >
      <div class="modal-dialog modal-dialog-scrollable">
        <div class="modal-content border-0 shadow rounded-4">
          <div class="modal-header border-0">
            <h5 class="modal-title fw-bold" id="coursePickerModalLabel">Select Course</h5>
            <button
              type="button"
              class="btn-close shadow-none"
              aria-label="Close"
              @click="showCourseModal = false"
            ></button>
          </div>
          <div class="modal-body p-0">
            <div class="p-3 border-bottom">
              <input
                v-model.trim="courseSearch"
                class="form-control rounded-3 sb-field"
                placeholder="Search by code or name"
              >
            </div>
            <div class="list-group list-group-flush">
              <button
                v-for="course in filteredCourses"
                :key="course.course_code"
                type="button"
                class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
                :class="{ active: selectedCourse === course.course_code }"
                @click="pickCourse(course)"
              >
                <div>
                  <div class="fw-semibold">{{ course.course_code }}</div>
                  <div class="small" :class="selectedCourse === course.course_code ? 'text-white-50' : 'text-muted'">{{ course.course_name }}</div>
                </div>
                <i v-if="selectedCourse === course.course_code" class="bi bi-check2"></i>
              </button>
              <div v-if="!filteredCourses.length" class="p-4 text-center text-muted small">
                No courses match your search.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showCustomForm" class="border rounded-4 bg-white shadow-sm p-3 mb-4">
      <form class="row g-3 align-items-end" @submit.prevent="submitCustomSubject">
        <div class="col-12 col-md-3">
          <label class="form-label small fw-bold">SUBJECT CODE</label>
          <input
            v-model.trim="customForm.subjectCode"
            class="form-control rounded-3 sb-field"
            required
            placeholder="e.g. CPU-AI"
          >
        </div>

        <div class="col-12 col-md-4">
          <label class="form-label small fw-bold">SUBJECT NAME</label>
          <input
            v-model.trim="customForm.subjectName"
            class="form-control rounded-3 sb-field"
            required
            placeholder="e.g. Applied AI Studio"
          >
        </div>

        <div class="col-12 col-md-3">
          <label class="form-label small fw-bold">DEPARTMENT</label>
          <input
            v-model.trim="customForm.department"
            class="form-control rounded-3 sb-field"
            required
            placeholder="e.g. Computer Science"
          >
        </div>

        <div class="col-12 col-md-2 d-grid">
          <button class="btn bg-sb-primary text-white rounded-pill sb-btn" :disabled="savingCustom">
            <span v-if="savingCustom" class="spinner-border spinner-border-sm me-2"></span>
            Save
          </button>
        </div>
      </form>
    </div>

    <div v-if="!selectedCourse" class="empty-state border rounded-4 bg-white shadow-sm text-center p-5">
      <i class="bi bi-journal-bookmark fs-1 text-muted d-block mb-3"></i>
      <h5 class="fw-bold">Select a course</h5>
      <p class="text-muted mb-0">Choose a course to review and curate its recognized subjects.</p>
    </div>

    <div v-else class="row g-4">
      <div class="col-12 col-xl-5">
        <div class="border rounded-4 bg-white shadow-sm overflow-hidden">
          <div class="catalog-panel-header p-3 border-bottom">
            <h5 class="mb-1 fw-bold">Recognized Subjects</h5>
            <p class="text-muted small mb-0">{{ catalogEntries.length }} subjects in this course</p>
          </div>

          <div v-if="loading" class="p-4 placeholder-glow">
            <span v-for="i in 5" :key="i" class="placeholder col-12 rounded mb-3"></span>
          </div>

          <div v-else-if="!catalogEntries.length" class="p-4 text-center text-muted">
            <i class="bi bi-inbox fs-2 d-block mb-2"></i>
            No subjects added yet.
          </div>

          <div v-else class="list-group list-group-flush">
            <div
              v-for="entry in catalogEntries"
              :key="entry.id"
              class="list-group-item d-flex justify-content-between align-items-center gap-3"
            >
              <div>
                <div class="fw-semibold">{{ entry.subject_code }}</div>
                <div class="small text-muted">{{ entry.subject_name }}</div>
              </div>

              <button
                class="btn btn-sm btn-light rounded-circle sb-btn"
                :disabled="removingId === entry.id"
                :title="`Remove ${entry.subject_code}`"
                @click="removeEntry(entry)"
              >
                <span v-if="removingId === entry.id" class="spinner-border spinner-border-sm"></span>
                <i v-else class="bi bi-trash"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="col-12 col-xl-7">
        <div class="border rounded-4 bg-white shadow-sm overflow-hidden">
          <div class="catalog-panel-header p-3 border-bottom">
            <h5 class="mb-1 fw-bold">Available Subjects</h5>
            <p class="text-muted small mb-0">Global subjects plus private subjects for this institution</p>
          </div>

          <div class="p-3 border-bottom">
            <input
              v-model.trim="search"
              class="form-control rounded-3 sb-field"
              placeholder="Search by code, name, or department"
            >
          </div>

          <div v-if="!availableSubjects.length" class="p-4 text-center text-muted">
            <i class="bi bi-search fs-2 d-block mb-2"></i>
            No available subjects match this search.
          </div>

          <div v-else class="list-group list-group-flush subject-list">
            <div
              v-for="subject in availableSubjects"
              :key="subject.subject_code"
              class="list-group-item d-flex justify-content-between align-items-center gap-3"
            >
              <div>
                <div class="d-flex flex-wrap align-items-center gap-2">
                  <span class="fw-semibold">{{ subject.subject_code }}</span>
                  <span
                    v-if="subject.owning_institution"
                    class="badge bg-info-subtle text-info rounded-pill"
                  >
                    Custom
                  </span>
                </div>
                <div class="small text-muted">{{ subject.subject_name }}</div>
                <div class="small text-muted">{{ subject.department }}</div>
              </div>

              <button
                class="btn btn-sm rounded-pill sb-btn"
                :class="isCataloged(subject.subject_code) ? 'btn-success' : 'btn-outline-primary'"
                :disabled="isCataloged(subject.subject_code) || addingCode === subject.subject_code"
                @click="addEntry(subject)"
              >
                <span v-if="addingCode === subject.subject_code" class="spinner-border spinner-border-sm me-1"></span>
                {{ isCataloged(subject.subject_code) ? 'Added' : 'Add' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCatalogStore } from '@/stores/catalog'
import { useToastStore } from '@/stores/toast'

const authStore = useAuthStore()
const catalogStore = useCatalogStore()
const toastStore = useToastStore()

const selectedCourse = ref('')
const selectedInstitutionId = ref('')
const search = ref('')
const courseSearch = ref('')
const loading = ref(false)
const addingCode = ref(null)
const removingId = ref(null)
const showCustomForm = ref(false)
const savingCustom = ref(false)
const showCourseModal = ref(false)

const customForm = reactive({
  subjectCode: '',
  subjectName: '',
  department: '',
})

const isSuperAdmin = computed(() => authStore.userRole?.toLowerCase?.() === 'superadmin')
const activeInstitutionId = computed(() => (isSuperAdmin.value ? selectedInstitutionId.value : null))
const catalogEntries = computed(() => catalogStore.courseCatalog)

const selectedCourseName = computed(() => {
  const course = catalogStore.courses.find((c) => c.course_code === selectedCourse.value)
  return course?.course_name ?? ''
})

const filteredCourses = computed(() => {
  const query = courseSearch.value.toLowerCase()
  if (!query) return catalogStore.courses
  return catalogStore.courses.filter(
    (c) =>
      c.course_code.toLowerCase().includes(query) ||
      c.course_name.toLowerCase().includes(query),
  )
})

const catalogedCodes = computed(() => new Set(catalogEntries.value.map((entry) => entry.subject_code)))

const availableSubjects = computed(() => {
  const query = search.value.toLowerCase()
  return catalogStore.subjects
    .filter((subject) => {
      if (!query) return true
      return [subject.subject_code, subject.subject_name, subject.department]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(query))
    })
    .sort((a, b) => a.subject_code.localeCompare(b.subject_code))
})

const isCataloged = (subjectCode) => catalogedCodes.value.has(subjectCode)

const openCourseModal = () => {
  courseSearch.value = ''
  showCourseModal.value = true
}

const pickCourse = async (course) => {
  showCourseModal.value = false
  selectedCourse.value = course.course_code
  await reloadForSelection()
}

const reloadForSelection = async () => {
  if (!selectedCourse.value || (isSuperAdmin.value && !selectedInstitutionId.value)) {
    return
  }

  loading.value = true
  try {
    await Promise.all([
      catalogStore.fetchSubjects({
        force: true,
        params: {
          ...(activeInstitutionId.value ? { institution_id: activeInstitutionId.value } : {}),
          catalog_scope: 'all',
        },
      }),
      catalogStore.fetchCourseCatalog({
        course: selectedCourse.value,
        institutionId: activeInstitutionId.value,
      }),
    ])
  } catch {
    toastStore.push('Failed to load course catalog.', 'error')
  } finally {
    loading.value = false
  }
}

const addEntry = async (subject) => {
  addingCode.value = subject.subject_code
  try {
    await catalogStore.addCatalogEntry({
      course: selectedCourse.value,
      subject: subject.subject_code,
      institutionId: activeInstitutionId.value,
    })
    toastStore.push('Subject added to course catalog.', 'success')
  } catch {
    toastStore.push('Failed to add subject to course catalog.', 'error')
  } finally {
    addingCode.value = null
  }
}

const removeEntry = async (entry) => {
  removingId.value = entry.id
  try {
    await catalogStore.removeCatalogEntry(entry.id)
    toastStore.push('Subject removed from course catalog.', 'success')
  } catch {
    toastStore.push('Failed to remove subject from course catalog.', 'error')
  } finally {
    removingId.value = null
  }
}

const submitCustomSubject = async () => {
  savingCustom.value = true
  try {
    await catalogStore.addCustomSubject({
      subjectCode: customForm.subjectCode,
      subjectName: customForm.subjectName,
      department: customForm.department,
      institutionId: activeInstitutionId.value,
    })
    Object.assign(customForm, { subjectCode: '', subjectName: '', department: '' })
    toastStore.push('Custom subject created.', 'success')
  } catch {
    toastStore.push('Failed to create custom subject. The code may already exist.', 'error')
  } finally {
    savingCustom.value = false
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await catalogStore.fetchCourses({ force: true })
    if (catalogStore.courses.length) {
      selectedCourse.value = catalogStore.courses[0].course_code
    }

    if (isSuperAdmin.value) {
      await catalogStore.fetchPartnerInstitutions({ force: true })
      if (catalogStore.institutions.length) {
        selectedInstitutionId.value = catalogStore.institutions[0].id
      }
    }

    await reloadForSelection()
  } catch {
    toastStore.push('Failed to load catalog setup.', 'error')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.catalog-panel-header {
  background: #f8f9fa;
}

.subject-list {
  max-height: 560px;
  overflow-y: auto;
}

.placeholder {
  height: 44px;
  display: block;
}
</style>
