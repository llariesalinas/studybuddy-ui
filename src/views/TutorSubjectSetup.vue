<template>
  <TutorOnboardingShell :current-step="2">
    <h3>
      Add your subjects<span class="subject-counter"
        >{{ selectedSubjects.length }}/{{ SUBJECT_LIMIT }}</span
      >
    </h3>
    <p class="muted">Search the catalog, or propose one that's missing.</p>

    <SubjectTaxonomyPicker
      v-model="selectedCodes"
      :subjects="allSubjects"
      :max-selection="SUBJECT_LIMIT"
      allow-propose
      @propose="openProposalForm"
    />

    <button
      v-if="!showProposalForm"
      type="button"
      class="btn-outline-pill sb-btn propose-trigger"
      @click="openProposalForm"
    >
      + Propose a subject not in the catalog
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
        <label class="field-label" for="proposal-category">Category</label>
        <select
          id="proposal-category"
          v-model="proposal.category"
          class="mini-input sb-field"
          required
        >
          <option value="" disabled>Select a category</option>
          <option v-for="category in categories" :key="category" :value="category">
            {{ category }}
          </option>
        </select>
      </div>
      <div>
        <label class="field-label" for="proposal-description">Proposal Notes (optional):</label>
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
        <button type="button" class="btn-outline-pill sb-btn" @click="showProposalForm = false">
          Cancel
        </button>
      </div>
    </form>

    <div class="step-nav-row">
      <button
        type="button"
        class="btn-outline-pill sb-btn"
        :disabled="isSubmitting"
        @click="goBackToPreferences"
      >
        &larr; Back
      </button>
      <button
        type="button"
        class="btn-primary-pill continue-button sb-btn"
        :disabled="!selectedSubjects.length || isSubmitting"
        @click="continueToVerification"
      >
        Continue to Verification
      </button>
    </div>
  </TutorOnboardingShell>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import SubjectTaxonomyPicker from '@/components/SubjectTaxonomyPicker.vue'
import TutorOnboardingShell from '@/components/TutorOnboardingShell.vue'
import { useProfileStore } from '@/stores/profile'
import { useToastStore } from '@/stores/toast'
import {
  addTutorSubject,
  fetchSubjectCatalog,
  fetchTutorSubjects,
  proposeTutorSubject,
  removeTutorSubject,
} from '@/services/tutorOnboarding'

const SUBJECT_LIMIT = 8
const SUBJECT_LIMIT_MESSAGE = `You can add up to ${SUBJECT_LIMIT} subjects only.`

const router = useRouter()
const profileStore = useProfileStore()
const toastStore = useToastStore()
const allSubjects = ref([])
const selectedSubjects = ref([])
const showProposalForm = ref(false)
const isSubmitting = ref(false)
const proposal = reactive({ subject_name: '', category: '', description: '', keywords: '' })

const categories = computed(() => [...new Set(allSubjects.value.map((s) => s.category))].sort())

const selectedCodes = computed({
  get: () => selectedSubjects.value.map((subject) => subject.subject_code),
  set: (codes) => {
    const previousCodes = selectedSubjects.value.map((subject) => subject.subject_code)
    const addedCode = codes.find((code) => !previousCodes.includes(code))
    const removedCode = previousCodes.find((code) => !codes.includes(code))
    if (addedCode) handleAdd(addedCode)
    if (removedCode) handleRemove(removedCode)
  },
})

const loadSubjects = async () => {
  try {
    const [catalog, selected] = await Promise.all([fetchSubjectCatalog(), fetchTutorSubjects()])
    allSubjects.value = catalog
    selectedSubjects.value = selected
  } catch (error) {
    toastStore.push(error.response?.data?.error || 'Could not load subjects.', 'error')
  }
}

const handleAdd = async (subjectCode) => {
  if (selectedSubjects.value.length >= SUBJECT_LIMIT) {
    toastStore.push(SUBJECT_LIMIT_MESSAGE, 'warning')
    return
  }
  const subject = allSubjects.value.find((s) => s.subject_code === subjectCode)
  isSubmitting.value = true
  try {
    await addTutorSubject(subjectCode)
    selectedSubjects.value.push({ ...subject, status: 'approved' })
  } catch (error) {
    toastStore.push(error.response?.data?.error || 'Could not add that subject.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

const openProposalForm = (searchText) => {
  if (selectedSubjects.value.length >= SUBJECT_LIMIT) {
    toastStore.push(SUBJECT_LIMIT_MESSAGE, 'warning')
    return
  }
  const prefill = typeof searchText === 'string' ? searchText : ''
  proposal.subject_name = prefill
  proposal.category = ''
  proposal.description = ''
  proposal.keywords = prefill
  showProposalForm.value = true
}

const handleProposal = async () => {
  isSubmitting.value = true
  try {
    const subject = await proposeTutorSubject({ ...proposal })
    selectedSubjects.value.push(subject)
    allSubjects.value.push(subject)
    showProposalForm.value = false
  } catch (error) {
    toastStore.push(error.response?.data?.error || 'Could not propose that subject.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

const handleRemove = async (subjectCode) => {
  try {
    await removeTutorSubject(subjectCode)
    selectedSubjects.value = selectedSubjects.value.filter(
      (selected) => selected.subject_code !== subjectCode,
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

const goBackToPreferences = () => {
  router.push({ name: 'tutorpreferencesetup' })
}

onMounted(loadSubjects)
</script>

<style scoped>
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
.step-nav-row {
  display: flex;
  gap: 10px;
  margin-top: 24px;
}
.continue-button {
  flex: 1;
}
</style>
