<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import SbSelectModal from '@/components/SbSelectModal.vue'
import AlgorithmDemoBreakdown from './AlgorithmDemoBreakdown.vue'
import AlgorithmDemoWeightTable from './AlgorithmDemoWeightTable.vue'
import {
  getAlgorithmDemoRecommendation,
  getAlgorithmDemoWhatIf
} from '@/services/api/algorithmDemo'
import { HYBRID_SCORE_PRECISION } from '@/config'

// Rating edits are re-scored server-side so the numbers keep coming from the real
// recommender, which costs a round trip — this paces them without feeling laggy.
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
const rows = ref([])
// The co-rated set behind each neighbour's similarity, keyed by neighbour id.
// Returned once per response rather than per row, because it belongs to the
// (tutee, neighbour) pair and is identical across every candidate tutor.
const coRated = ref({})
const reason = ref(null)
const selectedTutorId = ref(null)
const loading = ref(false)
const errorMessage = ref('')

const overrides = ref([])
let whatIfTimer = null

const selectedRow = computed(
  () => rows.value.find((row) => row.tutor_id === selectedTutorId.value) || null
)

function isTied(row) {
  return row?.tie_group_id !== null && row?.tie_group_id !== undefined
}

// The tied peers of the selected tutor, carrying the rank they were given, so the
// breakdown panel can show the comparison the Tie Breaker actually made.
const selectedTieGroup = computed(() => {
  const row = selectedRow.value
  if (!isTied(row)) return []

  return rows.value
    .map((item, index) => ({ ...item, rank: index + 1 }))
    .filter((item) => item.tie_group_id === row.tie_group_id)
})

function clearWhatIf() {
  clearTimeout(whatIfTimer)
  whatIfTimer = null
  overrides.value = []
}

async function onTuteeChange(tuteeId) {
  selectedTuteeId.value = tuteeId
  rows.value = []
  coRated.value = {}
  reason.value = null
  selectedTutorId.value = null
  errorMessage.value = ''
  clearWhatIf()

  if (!tuteeId) return

  loading.value = true
  try {
    const { data } = await getAlgorithmDemoRecommendation(tuteeId, props.institutionId)
    rows.value = data.rows
    coRated.value = data.co_rated || {}
    reason.value = data.reason
    if (data.rows.length) selectedTutorId.value = data.rows[0].tutor_id
  } catch (err) {
    errorMessage.value = err.response?.data?.error || 'Could not load recommendations.'
  } finally {
    loading.value = false
  }
}

// Overrides are applied to the rating matrix in memory by the backend and never
// written, so every edit is reversible and the demo database stays intact.
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
    // The selection is held by tutor_id, so a tutor that moves rank stays selected.
    rows.value = data.rows
    // Recomputed on every what-if edit: overriding a rating inside a co-rated set
    // moves both averages and the similarity, which is the point of the panel.
    coRated.value = data.co_rated || {}
    reason.value = data.reason
    errorMessage.value = ''
  } catch (err) {
    errorMessage.value = err.response?.data?.error || 'Could not re-score with these ratings.'
  }
}

async function resetWhatIf() {
  clearWhatIf()
  await onTuteeChange(selectedTuteeId.value)
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
  <div class="ranked-list-tab">
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

    <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

    <div v-if="overrides.length" class="whatif-bar">
      <span class="whatif-chip">What-if — {{ overrides.length }} rating
        {{ overrides.length === 1 ? 'change' : 'changes' }}, nothing saved</span>
      <button type="button" class="whatif-reset" @click="resetWhatIf">Reset</button>
    </div>

    <AlgorithmDemoWeightTable
      v-if="rows.length"
      :rows="rows"
      :selected-tutor-id="selectedTutorId"
      @select="selectedTutorId = $event"
    />

    <div class="split">
      <div class="list-pane">
        <p v-if="loading" class="empty-state">Loading…</p>
        <p v-else-if="!selectedTuteeId" class="empty-state">
          Select a tutee above to load their candidate tutors.
        </p>
        <p v-else-if="reason === 'no_preferences'" class="empty-state">
          This tutee hasn't set any subject preferences yet — nothing for the CBF matcher to score
          against.
        </p>
        <p v-else-if="reason === 'no_candidates'" class="empty-state">
          No subject-matching candidate tutors found{{ institutionId ? ' for this institution' : '' }}.
        </p>
        <div
          v-for="(row, index) in rows"
          v-else
          :key="row.tutor_id"
          class="tutor-row"
          :class="{ selected: row.tutor_id === selectedTutorId }"
          @click="selectedTutorId = row.tutor_id"
        >
          <span>
            <span class="rank">{{ index + 1 }}.</span>{{ row.name }}
            <span v-if="row.cold_start" class="sb-badge cold">Cold Start</span>
            <span v-if="isTied(row)" class="sb-badge tie">Tie Breaker</span>
          </span>
          <span class="score">{{ row.hybrid_score.toFixed(HYBRID_SCORE_PRECISION) }}</span>
        </div>
      </div>

      <AlgorithmDemoBreakdown
        :row="selectedRow"
        :tie-group="selectedTieGroup"
        :co-rated="coRated"
        @override="onOverride"
      />
    </div>
  </div>
</template>

<style scoped>
.picker-field {
  max-width: 420px;
  margin-bottom: 18px;
}

.picker-field label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--sb-text-muted);
  margin-bottom: 6px;
}

.error-text {
  color: var(--sb-danger);
  font-size: 13px;
}

.whatif-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
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

.split {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 18px;
}

.list-pane {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.empty-state {
  color: var(--sb-text-muted);
  font-size: 14px;
  text-align: center;
  padding: 40px 12px;
}

.tutor-row {
  background: var(--sb-card-bg);
  border: 1px solid var(--sb-card-border);
  border-radius: 10px;
  padding: 10px 14px;
  cursor: pointer;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.tutor-row:hover {
  border-color: var(--sb-primary);
}

.tutor-row.selected {
  border-color: var(--sb-primary);
  background: color-mix(in srgb, var(--sb-primary) 12%, transparent);
}

.rank {
  color: var(--sb-text-muted);
  font-size: 11px;
  margin-right: 6px;
}

.score {
  font-weight: 700;
  color: var(--sb-primary);
  /* 3 decimals now, so tied scores line up digit-for-digit rather than jittering. */
  font-variant-numeric: tabular-nums;
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

.sb-badge.tie {
  background: color-mix(in srgb, var(--sb-warning, #d29922) 14%, transparent);
  color: var(--sb-warning, #d29922);
  border-color: color-mix(in srgb, var(--sb-warning, #d29922) 35%, transparent);
}
</style>
