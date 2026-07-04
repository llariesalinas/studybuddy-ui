<script setup>
import { computed, ref, watch } from 'vue'
import SbSelectModal from '@/components/SbSelectModal.vue'
import AlgorithmDemoBreakdown from './AlgorithmDemoBreakdown.vue'
import { getAlgorithmDemoRecommendation } from '@/services/api/algorithmDemo'

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
const reason = ref(null)
const selectedTutorId = ref(null)
const loading = ref(false)
const errorMessage = ref('')

const selectedRow = computed(
  () => rows.value.find((row) => row.tutor_id === selectedTutorId.value) || null
)

async function onTuteeChange(tuteeId) {
  selectedTuteeId.value = tuteeId
  rows.value = []
  reason.value = null
  selectedTutorId.value = null
  errorMessage.value = ''

  if (!tuteeId) return

  loading.value = true
  try {
    const { data } = await getAlgorithmDemoRecommendation(tuteeId, props.institutionId)
    rows.value = data.rows
    reason.value = data.reason
    if (data.rows.length) selectedTutorId.value = data.rows[0].tutor_id
  } catch (err) {
    errorMessage.value = err.response?.data?.error || 'Could not load recommendations.'
  } finally {
    loading.value = false
  }
}

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
          </span>
          <span class="score">{{ row.hybrid_score.toFixed(2) }}</span>
        </div>
      </div>

      <AlgorithmDemoBreakdown :row="selectedRow" />
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
</style>
