<template>
  <div class="onboarding-page">
    <nav class="navbar sb-surface py-3">
      <div class="container d-flex justify-content-between align-items-center">
        <span class="navbar-brand fw-bold fs-4 sb-text">StudyBuddy</span>
        <SbThemeToggle />
      </div>
    </nav>

    <main class="container py-5">
      <div class="row justify-content-center">
        <div class="col-lg-9">
          <div class="onboarding-shell">
            <aside class="onboarding-rail">
              <div class="rail-step rail-step-done">
                <span class="rail-num"></span><span>Preferences</span>
              </div>
              <div class="rail-step rail-step-active">
                <span class="rail-num">2</span><span>Subjects</span>
              </div>
              <div class="rail-step"><span class="rail-num">3</span><span>Verify</span></div>
            </aside>

            <section class="onboarding-main sb-text">
              <h3>
                Add your subjects<span class="subject-counter"
                  >{{ selectedSubjects.length }}/{{ SUBJECT_LIMIT }}</span
                >
              </h3>
              <p class="muted">Search the catalog, or propose one that's missing.</p>

              <div v-if="selectedSubjects.length" class="subject-pill-row">
                <span
                  v-for="subject in selectedSubjects"
                  :key="subject.subject_code"
                  class="subject-pill"
                  :class="{ pending: subject.status === 'pending' }"
                >
                  {{ subject.subject_name }}
                  <button
                    type="button"
                    class="pill-remove sb-btn"
                    :aria-label="`Remove ${subject.subject_name}`"
                    @click="handleRemove(subject)"
                  >
                    <i class="bi bi-x"></i>
                  </button>
                </span>
              </div>

              <div class="field-label">Search subjects</div>
              <div class="search-wrap">
                <input
                  v-model.trim="searchText"
                  class="mini-input sb-field"
                  type="search"
                  placeholder="Search by subject name or code"
                  autocomplete="off"
                />
                <div v-if="searchText" class="dropdown-preview">
                  <button
                    v-for="subject in matchingSubjects"
                    :key="subject.subject_code"
                    type="button"
                    class="dropdown-row sb-btn"
                    @click="handleCatalogPick(subject)"
                  >
                    <span>{{ subject.subject_name }}</span>
                    <span class="meta">{{ subject.department }}</span>
                  </button>
                  <div v-if="isSearching" class="dropdown-empty">Searching...</div>
                  <div v-else-if="!matchingSubjects.length" class="dropdown-empty">
                    No catalog subjects match “{{ searchText }}”.
                  </div>
                </div>
              </div>

              <button
                v-if="searchText && !isSearching && !matchingSubjects.length && !showProposalForm"
                type="button"
                class="btn-outline-pill sb-btn propose-trigger"
                @click="openProposalForm"
              >
                + Propose new subject
              </button>

              <form v-if="showProposalForm" class="proposal-form" @submit.prevent="handleProposal">
                <div>
                  <label class="field-label" for="proposal-name">Subject name</label>
                  <input
                    id="proposal-name"
                    v-model.trim="proposal.subject_name"
                    class="mini-input sb-field"
                    required
                  />
                </div>
                <div>
                  <label class="field-label" for="proposal-department">Department</label>
                  <select
                    id="proposal-department"
                    v-model="proposal.department"
                    class="mini-input sb-field"
                    required
                  >
                    <option value="" disabled>Select a department</option>
                    <option v-for="department in departments" :key="department" :value="department">
                      {{ department }}
                    </option>
                  </select>
                </div>
                <div>
                  <label class="field-label" for="proposal-description"
                    >Description (optional)</label
                  >
                  <textarea
                    id="proposal-description"
                    v-model.trim="proposal.description"
                    class="mini-input sb-field"
                    rows="3"
                  ></textarea>
                </div>
                <div class="proposal-actions">
                  <button type="submit" class="btn-primary-pill sb-btn" :disabled="isSubmitting">
                    {{ isSubmitting ? 'Proposing...' : 'Add proposal' }}
                  </button>
                  <button
                    type="button"
                    class="btn-outline-pill sb-btn"
                    @click="showProposalForm = false"
                  >
                    Cancel
                  </button>
                </div>
              </form>

              <button
                type="button"
                class="btn-primary-pill continue-button sb-btn"
                :disabled="!selectedSubjects.length || isSubmitting"
                @click="continueToVerification"
              >
                Continue to Verification
              </button>
            </section>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import SbThemeToggle from '@/components/SbThemeToggle.vue'
import { useProfileStore } from '@/stores/profile'
import { useToastStore } from '@/stores/toast'
import {
  addTutorSubject,
  fetchApprovedSubjects,
  fetchSubjectDepartments,
  fetchTutorSubjects,
  proposeTutorSubject,
  removeTutorSubject,
} from '@/services/tutorOnboarding'

const SUBJECT_LIMIT = 8
const SUBJECT_LIMIT_MESSAGE = `You can add up to ${SUBJECT_LIMIT} subjects only.`

const router = useRouter()
const profileStore = useProfileStore()
const toastStore = useToastStore()
const matchingSubjects = ref([])
const departmentSubjects = ref([])
const selectedSubjects = ref([])
const searchText = ref('')
const showProposalForm = ref(false)
const isSubmitting = ref(false)
const isSearching = ref(false)
const proposal = reactive({ subject_name: '', department: '', description: '' })

const selectedCodes = computed(
  () => new Set(selectedSubjects.value.map((subject) => subject.subject_code)),
)
const departments = computed(() => {
  const values = departmentSubjects.value.map((subject) => subject.department).filter(Boolean)
  return [...new Set(values)].sort()
})

const atSubjectLimit = () => {
  if (selectedSubjects.value.length < SUBJECT_LIMIT) return false
  toastStore.push(SUBJECT_LIMIT_MESSAGE, 'warning')
  return true
}

const loadSubjects = async () => {
  try {
    const [catalog, selected] = await Promise.all([
      fetchSubjectDepartments(),
      fetchTutorSubjects(),
    ])
    departmentSubjects.value = catalog
    selectedSubjects.value = selected
  } catch (error) {
    toastStore.push(error.response?.data?.error || 'Could not load subjects.', 'error')
  }
}

let searchTimer = null
let searchSequence = 0
watch(searchText, (query) => {
  clearTimeout(searchTimer)
  const sequence = ++searchSequence
  if (!query) {
    matchingSubjects.value = []
    isSearching.value = false
    return
  }

  isSearching.value = true
  searchTimer = setTimeout(async () => {
    try {
      const results = await fetchApprovedSubjects(query)
      if (sequence !== searchSequence) return
      matchingSubjects.value = results.filter(
        (subject) => !selectedCodes.value.has(subject.subject_code),
      )
    } catch (error) {
      if (sequence !== searchSequence) return
      matchingSubjects.value = []
      toastStore.push(error.response?.data?.error || 'Could not search subjects.', 'error')
    } finally {
      if (sequence === searchSequence) isSearching.value = false
    }
  }, 250)
})

const handleCatalogPick = async (subject) => {
  if (atSubjectLimit()) return
  isSubmitting.value = true
  try {
    await addTutorSubject(subject.subject_code)
    selectedSubjects.value.push({ ...subject, status: 'approved' })
    searchText.value = ''
  } catch (error) {
    toastStore.push(error.response?.data?.error || 'Could not add that subject.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

const openProposalForm = () => {
  if (atSubjectLimit()) return
  proposal.subject_name = searchText.value
  proposal.department = ''
  proposal.description = ''
  showProposalForm.value = true
}

const handleProposal = async () => {
  if (atSubjectLimit()) return
  isSubmitting.value = true
  try {
    const subject = await proposeTutorSubject({ ...proposal })
    selectedSubjects.value.push(subject)
    searchText.value = ''
    showProposalForm.value = false
  } catch (error) {
    toastStore.push(error.response?.data?.error || 'Could not propose that subject.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

const handleRemove = async (subject) => {
  try {
    await removeTutorSubject(subject.subject_code)
    selectedSubjects.value = selectedSubjects.value.filter(
      (selected) => selected.subject_code !== subject.subject_code,
    )
  } catch (error) {
    toastStore.push(error.response?.data?.error || 'Could not remove that subject.', 'error')
  }
}

const continueToVerification = async () => {
  profileStore.tutorSubjectCount = selectedSubjects.value.length
  profileStore.tutorSubjectsCompleted = selectedSubjects.value.length > 0
  await router.push({ name: 'tutor-verification-setup' })
}

onMounted(loadSubjects)
</script>

<style scoped>
.onboarding-page {
  min-height: 100vh;
  background: var(--sb-bg);
}
.onboarding-shell {
  display: flex;
  background: var(--sb-card-bg);
  border: 1px solid var(--sb-card-border);
  border-radius: 18px;
  box-shadow: 0 6px 20px var(--sb-shadow-soft);
  overflow: hidden;
}
.onboarding-rail {
  width: 160px;
  flex-shrink: 0;
  background: color-mix(in srgb, var(--sb-primary) 8%, var(--sb-card-bg));
  border-right: 1px solid var(--sb-card-border);
  padding: 28px 16px;
}
.rail-step {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 24px;
  font-size: 13px;
  color: var(--sb-text-muted);
}
.rail-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 1.5px solid var(--sb-card-border);
  background: var(--sb-card-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 11px;
  flex-shrink: 0;
}
.rail-step-active {
  color: var(--sb-text-main);
  font-weight: 700;
}
.rail-step-active .rail-num,
.rail-step-done .rail-num {
  background: var(--sb-primary);
  border-color: var(--sb-primary);
  color: var(--sb-primary-contrast);
}
.rail-step-done .rail-num::after {
  content: '\2713';
  color: var(--sb-primary-contrast);
  font-size: 12px;
}
.onboarding-main {
  flex: 1;
  min-width: 0;
  padding: 32px 32px 30px;
}
.onboarding-main h3 {
  font-weight: 800;
  margin: 0 0 0.2rem;
  font-size: 1.15rem;
}
.muted {
  color: var(--sb-text-muted);
  margin: 0 0 1.25rem;
  font-size: 0.92rem;
}
.subject-counter {
  float: right;
  color: var(--sb-text-muted);
  font-size: 0.78rem;
  font-weight: 700;
}
.subject-pill-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 1rem;
}
.subject-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 8px 6px 11px;
  border-radius: 999px;
  border: 1px solid var(--sb-card-border);
  font-size: 0.82rem;
  font-weight: 600;
  background: color-mix(in srgb, var(--sb-primary) 6%, var(--sb-card-bg));
}
.subject-pill.pending {
  border-color: var(--sb-warning-text);
  background: color-mix(in srgb, var(--sb-warning-bg) 18%, var(--sb-card-bg));
  color: var(--sb-warning-text);
}
.pill-remove {
  border: 0;
  background: transparent;
  color: inherit;
  padding: 0 2px;
  line-height: 1;
}
.field-label {
  display: block;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--sb-text-muted);
  margin-bottom: 8px;
}
.search-wrap {
  position: relative;
}
.mini-input {
  width: 100%;
  padding: 10px 12px;
  border: 1.5px solid var(--sb-card-border);
  border-radius: 10px;
  font-size: 0.9rem;
  background: var(--sb-bg);
  color: var(--sb-text-main);
  font-family: inherit;
}
.mini-input:focus {
  border-color: var(--sb-primary);
}
.dropdown-preview {
  margin-top: 8px;
  border: 1px solid var(--sb-card-border);
  border-radius: 10px;
  overflow: hidden;
}
.dropdown-row {
  width: 100%;
  display: flex;
  justify-content: space-between;
  padding: 9px 12px;
  border: 0;
  border-bottom: 1px solid var(--sb-card-border);
  background: var(--sb-card-bg);
  color: var(--sb-text-main);
  font-size: 0.85rem;
  text-align: left;
}
.dropdown-row:last-child {
  border-bottom: 0;
}
.dropdown-row:hover {
  background: color-mix(in srgb, var(--sb-primary) 6%, var(--sb-card-bg));
}
.meta,
.dropdown-empty {
  color: var(--sb-text-muted);
  font-size: 0.76rem;
}
.dropdown-empty {
  padding: 10px 12px;
}
.btn-primary-pill,
.btn-outline-pill {
  width: auto;
  border-radius: 999px;
  padding: 11px 24px;
  font-weight: 700;
  font-size: 13.5px;
}
.btn-primary-pill {
  background: var(--sb-primary);
  color: var(--sb-primary-contrast);
  border: 0;
}
.btn-primary-pill:hover {
  background: var(--sb-primary-hover);
}
.btn-outline-pill {
  background: transparent;
  border: 1px solid var(--sb-card-border);
  color: var(--sb-text-main);
}
.btn-outline-pill:hover {
  border-color: var(--sb-primary);
  color: var(--sb-primary);
}
.propose-trigger {
  margin-top: 14px;
}
.proposal-form {
  display: grid;
  gap: 14px;
  margin-top: 18px;
  padding: 18px;
  border: 1px solid var(--sb-card-border);
  border-radius: 12px;
  background: color-mix(in srgb, var(--sb-primary) 4%, var(--sb-card-bg));
}
.proposal-actions {
  display: flex;
  gap: 10px;
}
.continue-button {
  display: block;
  width: 100%;
  margin-top: 24px;
}
@media (max-width: 640px) {
  .onboarding-shell {
    flex-direction: column;
  }
  .onboarding-rail {
    width: 100%;
    display: flex;
    justify-content: space-between;
    padding: 16px 18px;
    border-right: 0;
    border-bottom: 1px solid var(--sb-card-border);
  }
  .rail-step {
    margin-bottom: 0;
    flex-direction: column;
    gap: 4px;
    font-size: 11px;
  }
  .onboarding-main {
    padding: 26px 20px;
  }
}
</style>
