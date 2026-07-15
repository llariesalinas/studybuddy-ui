<script setup>
import { onBeforeUnmount, reactive, ref, watch } from 'vue'
import { updateAlgorithmDemoRating } from '@/services/api/algorithmDemo'

const props = defineProps({
  row: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['rating-updated'])

const CBF_PARTS = [
  ['subject', 'Subject match'],
  ['expertise', 'Expertise'],
  ['course', 'Course match'],
  ['year', 'Year proximity'],
  ['level', 'Teaching level']
]
const STAGGER_MS = 280

const bars = reactive(
  Object.fromEntries(CBF_PARTS.map(([key]) => [key, { widthPct: 0, label: '–' }]))
)
const cfBar = reactive({ widthPct: 0, label: '–' })
const cfMessage = ref('')
const hybridBar = reactive({ widthPct: 0 })
const hybridFinal = ref('…')
const neighborDrafts = reactive({})
const neighborSaving = reactive({})
const neighborError = reactive({})

let timers = []

function clearTimers() {
  timers.forEach(clearTimeout)
  timers = []
}

function resetBars() {
  CBF_PARTS.forEach(([key]) => {
    bars[key].widthPct = 0
    bars[key].label = '–'
  })
  cfBar.widthPct = 0
  cfBar.label = '–'
  cfMessage.value = ''
  hybridBar.widthPct = 0
  hybridFinal.value = '…'
}

function syncNeighborState(row) {
  const activeNeighborIds = new Set((row?.cf?.neighbors || []).map((neighbor) => neighbor.neighbor_id))

  Object.keys(neighborDrafts).forEach((key) => {
    if (!activeNeighborIds.has(Number(key))) delete neighborDrafts[key]
  })
  Object.keys(neighborSaving).forEach((key) => {
    if (!activeNeighborIds.has(Number(key))) delete neighborSaving[key]
  })
  Object.keys(neighborError).forEach((key) => {
    if (!activeNeighborIds.has(Number(key))) delete neighborError[key]
  })

  if (!row) return

  row.cf.neighbors.forEach((neighbor) => {
    neighborDrafts[neighbor.neighbor_id] = neighbor.rating
  })
}

function animate(row) {
  clearTimers()
  resetBars()
  syncNeighborState(row)
  if (!row) return

  const steps = []

  CBF_PARTS.forEach(([key]) => {
    steps.push(() => {
      const sub = row.cbf[key]
      bars[key].widthPct = Math.round(Math.max(0, Math.min(1, sub.value)) * 100)
      bars[key].label = sub.value.toFixed(2)
    })
  })

  steps.push(() => {
    if (row.cold_start) {
      cfBar.label = 'unavailable'
      cfMessage.value = 'CF unavailable — no rating history.'
    } else if (row.cf.score === null) {
      cfBar.label = 'no signal'
      cfMessage.value = "None of this tutee's similar peers have rated this tutor yet."
      cfBar.widthPct = 0
    } else {
      cfBar.widthPct = Math.round(Math.max(0, Math.min(1, row.cf.score / 5)) * 100)
      cfBar.label = row.cf.score.toFixed(2)
      cfMessage.value = ''
    }
  })

  steps.push(() => {
    hybridBar.widthPct = Math.round(Math.max(0, Math.min(1, row.hybrid_score)) * 100)
    hybridFinal.value = row.hybrid_score.toFixed(3)
  })

  steps.forEach((step, index) => {
    timers.push(setTimeout(step, index * STAGGER_MS))
  })
}

async function saveNeighborRating(neighbor) {
  const draft = neighborDrafts[neighbor.neighbor_id]
  neighborSaving[neighbor.neighbor_id] = true
  neighborError[neighbor.neighbor_id] = ''
  try {
    await updateAlgorithmDemoRating(neighbor.neighbor_id, props.row.tutor_id, draft)
    emit('rating-updated')
  } catch (err) {
    neighborError[neighbor.neighbor_id] =
      err.response?.data?.error || 'Could not save this rating.'
  } finally {
    neighborSaving[neighbor.neighbor_id] = false
  }
}

watch(() => props.row, animate, { immediate: true })
onBeforeUnmount(clearTimers)
</script>

<template>
  <div class="algo-breakdown sb-card">
    <template v-if="row">
      <h2>{{ row.name }}</h2>
      <p class="final-score">Hybrid Score <b>{{ hybridFinal }}</b></p>

      <div v-for="[key, label] in CBF_PARTS" :key="key" class="bar-row">
        <div class="bar-label">
          <span>{{ label }} (weight {{ row.cbf[key].weight.toFixed(2) }})</span>
          <span>{{ bars[key].label }}</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill" :style="{ width: bars[key].widthPct + '%' }"></div>
        </div>
      </div>

      <div class="bar-row">
        <div class="bar-label">
          <span>
            CF (peer ratings)
            <span v-if="row.cold_start" class="sb-badge cold">Cold Start</span>
          </span>
          <span>{{ cfBar.label }}</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill cf" :style="{ width: cfBar.widthPct + '%' }"></div>
        </div>
        <div class="neighbor-list">
          <p v-if="cfMessage">{{ cfMessage }}</p>
          <div v-for="neighbor in row.cf.neighbors" :key="neighbor.neighbor_id" class="neighbor-row">
            <span>
              {{ neighbor.name }} — similarity {{ neighbor.similarity.toFixed(2) }}, rated this
              tutor
            </span>
            <input
              v-model.number="neighborDrafts[neighbor.neighbor_id]"
              type="number"
              min="1"
              max="5"
              class="neighbor-rating-input"
            />
            <button
              type="button"
              class="neighbor-save-btn"
              :disabled="
                neighborSaving[neighbor.neighbor_id] ||
                neighborDrafts[neighbor.neighbor_id] === neighbor.rating
              "
              @click="saveNeighborRating(neighbor)"
            >
              {{ neighborSaving[neighbor.neighbor_id] ? 'Saving…' : 'Save' }}
            </button>
            <span v-if="neighborError[neighbor.neighbor_id]" class="neighbor-error">
              {{ neighborError[neighbor.neighbor_id] }}
            </span>
          </div>
        </div>
      </div>

      <div class="bar-row">
        <div class="bar-label">
          <span>Hybrid Score = 0.7×CBF + 0.3×(CF/5)</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill hybrid" :style="{ width: hybridBar.widthPct + '%' }"></div>
        </div>
      </div>
    </template>
    <p v-else class="empty-state">Select a tutor to see the calculation.</p>
  </div>
</template>

<style scoped>
.algo-breakdown {
  min-height: 320px;
}

.sb-card {
  background: var(--sb-card-bg);
  border: 1px solid var(--sb-card-border);
  border-radius: 14px;
  padding: 20px 22px;
}

.algo-breakdown h2 {
  margin: 0 0 2px;
  font-size: 18px;
}

.final-score {
  font-size: 13px;
  color: var(--sb-text-muted);
  margin: 0 0 18px;
}

.final-score b {
  color: var(--sb-primary);
  font-size: 22px;
}

.bar-row {
  margin-bottom: 14px;
}

.bar-label {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--sb-text-muted);
  margin-bottom: 4px;
}

.bar-track {
  background: var(--sb-card-border);
  border-radius: 5px;
  height: 10px;
  width: 100%;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 5px;
  background: var(--sb-primary);
  transition: width 0.5s ease;
}

.bar-fill.cf {
  background: var(--sb-info-bg);
}

.bar-fill.hybrid {
  background: var(--sb-dark);
}

.neighbor-list {
  margin-top: 8px;
  font-size: 12px;
  color: var(--sb-text-muted);
}

.neighbor-list p {
  padding: 3px 0;
  margin: 0;
}

.neighbor-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 3px 0;
}

.neighbor-rating-input {
  width: 56px;
  border: 1px solid var(--sb-card-border);
  border-radius: 8px;
  padding: 4px 6px;
  background: var(--sb-card-bg);
  color: var(--sb-dark);
}

.neighbor-save-btn {
  background: var(--sb-primary);
  color: var(--sb-white, #fff);
  border: none;
  border-radius: 9999px;
  padding: 5px 10px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s ease, opacity 0.15s ease;
}

.neighbor-save-btn:hover:not(:disabled) {
  background: var(--sb-primary-hover, var(--sb-primary));
}

.neighbor-save-btn:disabled {
  cursor: default;
  opacity: 0.55;
}

.neighbor-error {
  color: var(--sb-danger);
  font-size: 11px;
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

.empty-state {
  color: var(--sb-text-muted);
  font-size: 14px;
  text-align: center;
  padding: 60px 0;
  margin: 0;
}
</style>
