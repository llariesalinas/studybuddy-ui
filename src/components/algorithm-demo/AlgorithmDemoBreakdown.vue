<script setup>
import { computed, onBeforeUnmount, reactive, ref, watch } from 'vue'

const props = defineProps({
  row: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['override'])

const CBF_PARTS = [
  ['specific', 'Specific subject'],
  ['general', 'General subject'],
  ['expertise', 'Expertise'],
  ['course', 'Course match'],
  ['year', 'Year proximity'],
  ['level', 'Teaching level']
]
const STAGGER_MS = 280
const CF_MAX_RATING = 5
// Pearson over fewer than 3 co-rated tutors is degenerate — 2 shared items always
// give exactly +/-1 — so the panel is warned rather than shown a meaningless number.
const MIN_MEANINGFUL_CO_RATED = 3
// Axis padding either side of the plotted range, and the narrowest span we will
// draw, so a tiny shift doesn't render as a full-width bar.
const AXIS_PAD = 0.25
const AXIS_MIN_SPAN = 1

const bars = reactive(
  Object.fromEntries(CBF_PARTS.map(([key]) => [key, { widthPct: 0, label: '–' }]))
)
const hybridBar = reactive({ widthPct: 0 })
const hybridFinal = ref('…')

let timers = []

function clearTimers() {
  timers.forEach(clearTimeout)
  timers = []
}

// --- CF derivation -----------------------------------------------------------------
// Every term comes from the backend (compute_cf_breakdown) rather than being
// recomputed here, so there is only one implementation of the algorithm.

const cf = computed(() => props.row?.cf || null)

const steps = computed(() => {
  if (!cf.value || !cf.value.denominator) return []

  let cumulative = cf.value.student_avg
  return cf.value.neighbors.map((neighbor) => {
    const from = cumulative
    const share = neighbor.weighted / cf.value.denominator
    cumulative += share
    return { neighbor, from, to: cumulative, share }
  })
})

const axis = computed(() => {
  const points = [cf.value?.student_avg, cf.value?.score]
    .concat(steps.value.flatMap((step) => [step.from, step.to]))
    .filter((value) => typeof value === 'number')

  if (!points.length) return { lo: 1, hi: CF_MAX_RATING }

  let lo = Math.min(...points) - AXIS_PAD
  let hi = Math.max(...points) + AXIS_PAD

  if (hi - lo < AXIS_MIN_SPAN) {
    const mid = (lo + hi) / 2
    lo = mid - AXIS_MIN_SPAN / 2
    hi = mid + AXIS_MIN_SPAN / 2
  }

  return { lo: Math.max(0, lo), hi: Math.min(CF_MAX_RATING, hi) }
})

function pct(value) {
  const { lo, hi } = axis.value
  if (hi === lo) return 0
  return Math.max(0, Math.min(1, (value - lo) / (hi - lo))) * 100
}

function segmentStyle(step) {
  const from = pct(Math.min(step.from, step.to))
  const to = pct(Math.max(step.from, step.to))
  return { left: `${from}%`, width: `${Math.max(0.5, to - from)}%` }
}

const cfMessage = computed(() => {
  if (!props.row) return ''
  if (props.row.cold_start) return 'CF unavailable — this tutee has no rating history.'
  if (cf.value.score === null) {
    return "None of this tutee's similar peers have rated this tutor yet."
  }
  return ''
})

// The candidate pool deliberately keeps tutors the tutee has already rated (it mirrors
// production), which lets the prediction be checked against the real score.
const accuracy = computed(() => {
  if (!cf.value || cf.value.student_rating === null || cf.value.score === null) return null
  return {
    actual: cf.value.student_rating,
    predicted: cf.value.score,
    gap: Math.abs(cf.value.score - cf.value.student_rating)
  }
})

function onRatingInput(neighbor, value) {
  emit('override', {
    studentId: neighbor.neighbor_id,
    tutorId: props.row.tutor_id,
    ratingScore: Number(value)
  })
}

// --- CBF bars ----------------------------------------------------------------------

function resetBars() {
  CBF_PARTS.forEach(([key]) => {
    bars[key].widthPct = 0
    bars[key].label = '–'
  })
  hybridBar.widthPct = 0
  hybridFinal.value = '…'
}

function animate(row, previous) {
  // Re-running the stagger on every what-if edit would make the panel flicker, so it
  // only plays when a different tutor is selected.
  if (previous && row && previous.tutor_id === row.tutor_id) {
    applyBars(row)
    return
  }

  clearTimers()
  resetBars()
  if (!row) return

  const sequence = CBF_PARTS.map(([key]) => () => {
    bars[key].widthPct = Math.round(Math.max(0, Math.min(1, row.cbf[key].value)) * 100)
    bars[key].label = row.cbf[key].value.toFixed(2)
  })

  sequence.push(() => {
    hybridBar.widthPct = Math.round(Math.max(0, Math.min(1, row.hybrid_score)) * 100)
    hybridFinal.value = row.hybrid_score.toFixed(3)
  })

  sequence.forEach((step, index) => {
    timers.push(setTimeout(step, index * STAGGER_MS))
  })
}

function applyBars(row) {
  CBF_PARTS.forEach(([key]) => {
    bars[key].widthPct = Math.round(Math.max(0, Math.min(1, row.cbf[key].value)) * 100)
    bars[key].label = row.cbf[key].value.toFixed(2)
  })
  hybridBar.widthPct = Math.round(Math.max(0, Math.min(1, row.hybrid_score)) * 100)
  hybridFinal.value = row.hybrid_score.toFixed(3)
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

      <!-- CF: two-zone waterfall. Left is the evidence (similarity, rating), right is
           the effect on the tutee's baseline. See
           docs/mockups/2026-07-23-algorithm-demo-cf-waterfall.html -->
      <section class="cf-section">
        <header class="cf-header">
          <span>
            Collaborative Filtering
            <span v-if="cf.pool === 'peer'" class="cf-pool">Peer pool — same course</span>
            <span v-else-if="cf.pool === 'global'" class="cf-pool">Global pool</span>
            <span v-if="row.cold_start" class="sb-badge cold">Cold Start</span>
          </span>
          <span class="cf-score">{{ cf.score === null ? '—' : cf.score.toFixed(2) }}</span>
        </header>

        <p v-if="accuracy" class="cf-accuracy">
          This tutee has already rated this tutor <b>{{ accuracy.actual.toFixed(1) }}</b> —
          CF predicted <b>{{ accuracy.predicted.toFixed(2) }}</b>, off by
          {{ accuracy.gap.toFixed(2) }}. Editing a rating here re-runs the similarity too,
          because this tutor is inside the co-rated set.
        </p>

        <p v-if="cfMessage" class="cf-message">{{ cfMessage }}</p>

        <template v-else>
          <div class="cf-zones">
            <span></span>
            <span>Similarity</span>
            <span>Rated this tutor</span>
            <span>Effect on baseline</span>
          </div>

          <div class="cf-row">
            <div class="cf-name">Baseline<small>tutee's own average</small></div>
            <div></div>
            <div></div>
            <div class="cf-track">
              <div class="cf-seg base" :style="{ left: '0%', width: pct(cf.student_avg) + '%' }"></div>
              <span class="cf-segval" :style="{ left: `calc(${pct(cf.student_avg)}% + 6px)` }">
                {{ cf.student_avg.toFixed(2) }}
              </span>
            </div>
          </div>

          <div v-for="step in steps" :key="step.neighbor.neighbor_id" class="cf-row">
            <div class="cf-name">
              {{ step.neighbor.name }}
              <small v-if="step.neighbor.co_rated_count < MIN_MEANINGFUL_CO_RATED" class="warn">
                only {{ step.neighbor.co_rated_count }} co-rated
              </small>
              <small v-else>{{ step.neighbor.co_rated_count }} co-rated</small>
            </div>

            <div class="cf-meter-cell">
              <div class="cf-meter">
                <i :style="{ width: Math.round(Math.abs(step.neighbor.similarity) * 100) + '%' }"></i>
              </div>
              <span class="cf-meterval">{{ step.neighbor.similarity.toFixed(2) }}</span>
            </div>

            <div class="cf-rate">
              <input
                type="range"
                min="1"
                max="5"
                step="1"
                :value="step.neighbor.rating"
                @input="onRatingInput(step.neighbor, $event.target.value)"
              />
              <span class="cf-rateval">{{ step.neighbor.rating.toFixed(1) }}</span>
              <span class="cf-avg">avg {{ step.neighbor.neighbor_avg.toFixed(2) }}</span>
            </div>

            <div class="cf-track">
              <div
                class="cf-seg"
                :class="{ neg: step.share < 0 }"
                :style="segmentStyle(step)"
              ></div>
              <span
                class="cf-segval"
                :class="{ neg: step.share < 0 }"
                :style="{ left: `calc(${pct(Math.max(step.from, step.to))}% + 6px)` }"
              >
                {{ step.share >= 0 ? '+' : '−' }}{{ Math.abs(step.share).toFixed(2) }}
              </span>
            </div>
          </div>

          <div class="cf-row">
            <div class="cf-name total">CF score</div>
            <div></div>
            <div></div>
            <div class="cf-track">
              <div class="cf-seg total" :style="{ left: '0%', width: pct(cf.score) + '%' }"></div>
              <span class="cf-segval total" :style="{ left: `calc(${pct(cf.score)}% + 6px)` }">
                {{ cf.score.toFixed(2) }}
              </span>
            </div>
          </div>

          <div class="cf-axis">
            <span>{{ axis.lo.toFixed(1) }}</span>
            <span>{{ ((axis.lo + axis.hi) / 2).toFixed(1) }}</span>
            <span>{{ axis.hi.toFixed(1) }}</span>
          </div>

          <p class="cf-formula">
            CF = {{ cf.student_avg.toFixed(2) }} + ({{ cf.numerator.toFixed(3) }} ÷
            {{ cf.denominator.toFixed(2) }}) = <b>{{ cf.score.toFixed(2) }}</b>
          </p>
        </template>
      </section>

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

.bar-fill.hybrid {
  background: var(--sb-dark);
}

/* --- CF waterfall --- */

.cf-section {
  border: 1px solid var(--sb-card-border);
  border-radius: 12px;
  padding: 14px 16px;
  margin: 18px 0;
}

.cf-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 10px;
}

.cf-score {
  color: var(--sb-primary);
  font-size: 18px;
  font-weight: 700;
}

.cf-pool {
  color: var(--sb-primary);
  font-weight: 600;
  font-size: 11px;
  margin-left: 4px;
}

.cf-accuracy,
.cf-message {
  font-size: 12px;
  color: var(--sb-text-muted);
  margin: 0 0 10px;
  line-height: 1.5;
}

.cf-zones,
.cf-row {
  display: grid;
  grid-template-columns: 130px 110px 190px 1fr;
  gap: 10px;
  align-items: center;
}

.cf-zones {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--sb-text-muted);
  padding-bottom: 6px;
  border-bottom: 1px solid var(--sb-card-border);
}

.cf-row {
  padding: 8px 0;
  border-bottom: 1px solid var(--sb-card-border);
}

.cf-row:last-of-type {
  border-bottom: none;
}

.cf-name {
  font-size: 12px;
  font-weight: 600;
}

.cf-name.total {
  font-weight: 700;
}

.cf-name small {
  display: block;
  font-weight: 400;
  font-size: 10px;
  color: var(--sb-text-muted);
}

.cf-name small.warn {
  color: var(--sb-danger);
}

.cf-meter-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.cf-meter {
  flex: 1;
  background: var(--sb-card-border);
  border-radius: 5px;
  height: 9px;
  overflow: hidden;
}

.cf-meter i {
  display: block;
  height: 100%;
  border-radius: 5px;
  background: var(--sb-primary);
  transition: width 0.28s ease;
}

.cf-meterval {
  font-size: 10px;
  font-weight: 700;
  color: var(--sb-primary);
}

.cf-rate {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cf-rate input[type='range'] {
  width: 80px;
  accent-color: var(--sb-primary);
  cursor: pointer;
}

.cf-rateval {
  font-size: 11px;
  font-weight: 700;
  min-width: 22px;
}

.cf-avg {
  font-size: 10px;
  color: var(--sb-text-muted);
}

.cf-track {
  position: relative;
  height: 20px;
}

.cf-seg {
  position: absolute;
  top: 3px;
  height: 14px;
  border-radius: 4px;
  background: var(--sb-primary);
  transition: left 0.28s ease, width 0.28s ease;
}

.cf-seg.neg {
  background: var(--sb-danger);
}

.cf-seg.base {
  background: var(--sb-dark);
  opacity: 0.75;
}

.cf-seg.total {
  background: var(--sb-primary);
  height: 16px;
  top: 2px;
}

.cf-segval {
  position: absolute;
  top: 3px;
  font-size: 11px;
  font-weight: 700;
  color: var(--sb-primary);
  white-space: nowrap;
  transition: left 0.28s ease;
}

.cf-segval.neg {
  color: var(--sb-danger);
}

.cf-segval.total {
  font-size: 12px;
}

.cf-axis {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: var(--sb-text-muted);
  margin-left: calc(130px + 110px + 190px + 30px);
  margin-top: 2px;
}

.cf-formula {
  font-size: 12px;
  color: var(--sb-text-muted);
  margin: 12px 0 0;
  padding-top: 10px;
  border-top: 1px solid var(--sb-card-border);
}

.cf-formula b {
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

.empty-state {
  color: var(--sb-text-muted);
  font-size: 14px;
  text-align: center;
  padding: 60px 0;
  margin: 0;
}
</style>
