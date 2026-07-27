<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import SbSelectModal from '@/components/SbSelectModal.vue'
import AlgorithmDemoBreakdown from './AlgorithmDemoBreakdown.vue'
import {
  getAlgorithmDemoRecommendation,
  getAlgorithmDemoWhatIf
} from '@/services/api/algorithmDemo'

// Matches AlgorithmDemoRankedList: rating edits are re-scored server-side, so they
// are paced rather than fired on every slider tick.
const WHATIF_DEBOUNCE_MS = 250

const props = defineProps({
  tutees: {
    type: Array,
    default: () => []
  },
  institutionId: {
    type: [String, Number],
    default: null
  }
})

const tuteeOptions = computed(() =>
  props.tutees.map((tutee) => ({ value: tutee.id, label: tutee.name }))
)

const selectedTuteeId = ref(null)
const selectedTutorId = ref(null)
const rows = ref([])
const reason = ref(null)
const loading = ref(false)
const errorMessage = ref('')
const overrides = ref([])
let whatIfTimer = null

function clearWhatIf() {
  clearTimeout(whatIfTimer)
  whatIfTimer = null
  overrides.value = []
}

const selectedTutee = computed(
  () => props.tutees.find((tutee) => tutee.id === selectedTuteeId.value) || null
)
const selectedRow = computed(
  () => rows.value.find((row) => row.tutor_id === selectedTutorId.value) || null
)
const tutorOptions = computed(() =>
  rows.value.map((row) => ({
    value: row.tutor_id,
    label: `${row.name} (score ${row.hybrid_score.toFixed(2)})`
  }))
)

async function onTuteeChange(tuteeId) {
  selectedTuteeId.value = tuteeId
  selectedTutorId.value = null
  rows.value = []
  reason.value = null
  errorMessage.value = ''
  clearWhatIf()
  if (!tuteeId) return
  await refetchRows()
}

async function refetchRows() {
  if (!selectedTuteeId.value) return
  loading.value = true
  errorMessage.value = ''
  try {
    const { data } = await getAlgorithmDemoRecommendation(selectedTuteeId.value, props.institutionId)
    rows.value = data.rows
    reason.value = data.reason
  } catch (err) {
    errorMessage.value = err.response?.data?.error || 'Could not load candidate tutors.'
  } finally {
    loading.value = false
  }
}

// What-if overrides are applied to the rating matrix in memory by the backend and never
// written, so every edit here is reversible — see recommender/demo.apply_rating_overrides.
function onOverride({ studentId, tutorId, ratingScore }) {
  const existing = overrides.value.find(
    (item) => item.student_id === studentId && item.tutor_id === tutorId
  )

  if (existing) {
    existing.rating_score = ratingScore
  } else {
    overrides.value.push({
      student_id: studentId,
      tutor_id: tutorId,
      rating_score: ratingScore
    })
  }

  clearTimeout(whatIfTimer)
  whatIfTimer = setTimeout(refreshWhatIf, WHATIF_DEBOUNCE_MS)
}

async function refreshWhatIf() {
  if (!selectedTuteeId.value) return

  try {
    const { data } = await getAlgorithmDemoWhatIf(
      selectedTuteeId.value,
      props.institutionId,
      overrides.value
    )
    rows.value = data.rows
    reason.value = data.reason
    errorMessage.value = ''
  } catch (err) {
    errorMessage.value = err.response?.data?.error || 'Could not re-score with these ratings.'
  }
}

async function resetWhatIf() {
  clearWhatIf()
  await refetchRows()
}

onBeforeUnmount(() => clearTimeout(whatIfTimer))

watch(
  () => props.institutionId,
  () => {
    // The tutee picker's own options are re-scoped by the parent when the
    // institution filter changes, so a previously selected tutee may no
    // longer be valid for it — clear the selection instead of silently
    // re-fetching a tutee/institution combination that no longer matches.
    onTuteeChange(null)
  }
)
</script>

<template>
  <div class="pair-picker-tab">
    <div class="picker-row">
      <div class="picker-field">
        <label>Tutee</label>
        <SbSelectModal
          :model-value="selectedTuteeId"
          :options="tuteeOptions"
          title="Select tutee"
          placeholder="Select a tutee…"
          searchable
          clearable
          @update:model-value="onTuteeChange"
        />
      </div>
      <div class="picker-field">
        <label>Tutor</label>
        <SbSelectModal
          :model-value="selectedTutorId"
          :options="tutorOptions"
          title="Select tutor"
          :placeholder="selectedTuteeId ? 'Select a tutor…' : 'Select a tutee first…'"
          searchable
          clearable
          @update:model-value="(value) => (selectedTutorId = value)"
        />
        <p class="picker-hint">
          Only tutors matching this tutee's subjects appear here — use the institution filter
          above to narrow by school.
        </p>
      </div>
    </div>

    <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

    <p v-if="loading" class="empty-state">Loading…</p>
    <p v-else-if="!selectedTuteeId" class="empty-state">
      Select a tutee, then a tutor, to see their stats and calculate the match.
    </p>
    <p v-else-if="reason === 'no_preferences'" class="empty-state">
      This tutee hasn't set any subject preferences yet — nothing for the CBF matcher to score
      against.
    </p>
    <p v-else-if="!rows.length" class="empty-state">
      No subject-matching candidate tutors found{{ institutionId ? ' for this institution' : '' }}.
    </p>
    <p v-else-if="!selectedRow" class="empty-state">
      Select a tutor above to see their stats and calculate the match.
    </p>
    <template v-else>
      <div class="stat-cards">
        <div class="stat-card">
          <span class="role-tag">Tutee</span>
          <h3>{{ selectedTutee?.name }}</h3>
          <div class="subject-pills">
            <span v-if="!selectedTutee?.subjects?.length" class="no-subjects">
              No subject preferences set
            </span>
            <span v-for="subject in selectedTutee?.subjects" :key="subject" class="subject-pill">
              {{ subject }}
            </span>
          </div>
        </div>

        <div class="stat-card">
          <span class="role-tag">Tutor</span>
          <h3>
            {{ selectedRow.name }}
            <span v-if="selectedRow.cold_start" class="sb-badge cold">Cold Start</span>
          </h3>
          <div class="stat-line">
            <span>Avg. rating</span>
            <span class="v stars">
              {{ selectedRow.rating_average ? selectedRow.rating_average.toFixed(1) + ' ★' : 'No ratings yet' }}
            </span>
          </div>
          <div class="stat-line">
            <span>Sessions completed</span>
            <span class="v">{{ selectedRow.total_sessions }}</span>
          </div>
          <div class="subject-pills">
            <span
              v-for="subject in selectedRow.tutor_subjects"
              :key="subject.code"
              class="subject-pill"
            >
              {{ subject.code }}
            </span>
          </div>
        </div>
      </div>

      <div v-if="overrides.length" class="whatif-bar">
        <span class="whatif-chip">What-if — {{ overrides.length }} rating
          {{ overrides.length === 1 ? 'change' : 'changes' }}, nothing saved</span>
        <button type="button" class="whatif-reset" @click="resetWhatIf">Reset</button>
      </div>

      <AlgorithmDemoBreakdown :row="selectedRow" @override="onOverride" />
    </template>
  </div>
</template>

<style scoped>
.picker-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
  margin-bottom: 20px;
}

.picker-field label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--sb-text-muted);
  margin-bottom: 6px;
}

.picker-hint {
  font-size: 11px;
  color: var(--sb-text-muted);
  margin: 4px 0 0;
}

.error-text {
  color: var(--sb-danger);
  font-size: 13px;
}

.empty-state {
  color: var(--sb-text-muted);
  font-size: 14px;
  text-align: center;
  padding: 40px 12px;
}

.stat-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
  margin-bottom: 20px;
}

.stat-card {
  background: var(--sb-card-bg);
  border: 1px solid var(--sb-card-border);
  border-radius: 12px;
  padding: 16px 18px;
}

.role-tag {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--sb-primary);
}

.stat-card h3 {
  margin: 4px 0 10px;
  font-size: 16px;
}

.stat-line {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  padding: 6px 0;
  border-top: 1px dashed var(--sb-card-border);
}

.stat-line:first-of-type {
  border-top: none;
}

.stat-line .v {
  font-weight: 600;
}

.stars {
  color: var(--sb-warning-text);
}

.subject-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.no-subjects {
  color: var(--sb-text-muted);
  font-size: 12px;
}

.subject-pill {
  background: color-mix(in srgb, var(--sb-primary) 12%, transparent);
  color: var(--sb-primary);
  font-size: 11px;
  font-weight: 600;
  padding: 3px 9px;
  border-radius: 9999px;
}

.sb-badge {
  display: inline-block;
  background: color-mix(in srgb, var(--sb-primary) 12%, transparent);
  color: var(--sb-primary);
  border: 1px solid color-mix(in srgb, var(--sb-primary) 25%, transparent);
  border-radius: 9999px;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 8px;
  margin-left: 6px;
}

.sb-badge.cold {
  background: color-mix(in srgb, var(--sb-danger) 12%, transparent);
  color: var(--sb-danger);
  border-color: color-mix(in srgb, var(--sb-danger) 30%, transparent);
}

.whatif-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 14px 0;
}

.whatif-chip {
  background: color-mix(in srgb, var(--sb-warning, #d29922) 14%, transparent);
  border: 1px solid color-mix(in srgb, var(--sb-warning, #d29922) 35%, transparent);
  border-radius: 9999px;
  padding: 4px 12px;
  font-size: 11px;
  font-weight: 600;
}

.whatif-reset {
  background: none;
  border: 1px solid var(--sb-card-border);
  border-radius: 9999px;
  padding: 4px 12px;
  font-size: 11px;
  font-weight: 600;
  color: var(--sb-text-muted);
  cursor: pointer;
}

.whatif-reset:hover {
  border-color: var(--sb-primary);
  color: var(--sb-primary);
}
</style>
