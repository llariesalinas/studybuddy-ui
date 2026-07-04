<script setup>
import { reactive, ref, watch, onBeforeUnmount } from 'vue'

const props = defineProps({
  row: {
    type: Object,
    default: null
  }
})

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

function animate(row) {
  clearTimers()
  resetBars()
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
          <div v-for="neighbor in row.cf.neighbors" :key="neighbor.neighbor_id">
            {{ neighbor.name }} — similarity {{ neighbor.similarity.toFixed(2) }}, rated this tutor
            {{ neighbor.rating }}/5
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

.neighbor-list p,
.neighbor-list div {
  padding: 3px 0;
  margin: 0;
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
