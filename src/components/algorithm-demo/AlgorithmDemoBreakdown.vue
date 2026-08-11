<script setup>
import { computed, onBeforeUnmount, reactive, ref, watch } from 'vue'
import { HYBRID_SCORE_PRECISION, UPCOMING_WEEK_DAYS } from '@/config'

const props = defineProps({
  row: {
    type: Object,
    default: null
  },
  // Every row sharing the selected tutor's tie group, already ranked. Empty when
  // the selected tutor's score is unique, which is the common case.
  tieGroup: {
    type: Array,
    default: () => []
  },
  // The co-rated set behind each neighbour's similarity, keyed by neighbour id.
  // Keyed rather than carried on the row because it belongs to the (tutee,
  // neighbour) pair and does not vary by candidate tutor — see _build_co_rated_map.
  coRated: {
    type: Object,
    default: () => ({})
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
// How long a co-rated cell stays highlighted after a what-if edit changed it.
const FLASH_MS = 1400

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

// Neighbours arrive sorted by similarity, which is live-recomputed on every what-if
// edit — without freezing the order, dragging one slider reshuffles every row and the
// panel becomes impossible to track mid-edit. The order is captured once per tutor
// selection and held fixed; a neighbour that leaves or joins the co-rated set (advanced
// editing, or a target tutor inside it) still appears/disappears, just without reordering
// everyone else.
const neighborOrder = ref([])

const orderedNeighbors = computed(() => {
  if (!cf.value) return []
  const neighbors = cf.value.neighbors
  const order = neighborOrder.value
  if (!order.length) return neighbors

  const byId = new Map(neighbors.map((n) => [n.neighbor_id, n]))
  const ordered = order.filter((id) => byId.has(id)).map((id) => byId.get(id))
  const newArrivals = neighbors.filter((n) => !order.includes(n.neighbor_id))
  return [...ordered, ...newArrivals]
})

const steps = computed(() => {
  if (!cf.value || !cf.value.denominator) return []

  let cumulative = cf.value.student_avg
  return orderedNeighbors.value.map((neighbor) => {
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

// --- Co-rated set ------------------------------------------------------------------
// The collapsed row asserts a similarity; this expansion shows the shared ratings it
// was computed from, so the panel can check it by hand. Single-open: two neighbours
// side by side invite comparing rows that are measured against different averages.
// See docs/mockups/2026-08-10-corated-set-panel.html

const openNeighborId = ref(null)
const flashedCells = ref(new Set())
let flashTimer = null
// Seeded from the initial prop rather than null: the watcher needs a previous
// snapshot to diff against, and the very first what-if edit is the one most worth
// highlighting.
let lastCoRated = props.coRated

function toggleCoRated(neighborId) {
  openNeighborId.value = openNeighborId.value === neighborId ? null : neighborId
}

const openCoRated = computed(() => {
  if (openNeighborId.value === null) return null
  return props.coRated[openNeighborId.value] || null
})

function isFlashed(key) {
  return flashedCells.value.has(key)
}

// A what-if edit lands on a co-rated cell whenever the tutee has also rated the
// candidate tutor. Highlighting exactly what moved is what makes the chain from
// cell to average to similarity followable at demo speed.
watch(
  () => props.coRated,
  (next) => {
    const previous = lastCoRated
    lastCoRated = next
    if (!previous || previous === next) return

    const changed = new Set()

    Object.entries(next).forEach(([neighborId, detail]) => {
      const before = previous[neighborId]
      if (!before) return

      const beforeByTutor = new Map(before.shared.map((e) => [e.tutor_id, e]))
      detail.shared.forEach((entry) => {
        const was = beforeByTutor.get(entry.tutor_id)
        if (!was) return
        if (was.student_rating !== entry.student_rating) {
          changed.add(`${neighborId}:${entry.tutor_id}:student`)
        }
        if (was.neighbor_rating !== entry.neighbor_rating) {
          changed.add(`${neighborId}:${entry.tutor_id}:neighbor`)
        }
      })

      if (before.student_avg_over_set !== detail.student_avg_over_set) {
        changed.add(`${neighborId}:avg:student`)
      }
      if (before.neighbor_avg_over_set !== detail.neighbor_avg_over_set) {
        changed.add(`${neighborId}:avg:neighbor`)
      }
    })

    if (!changed.size) return

    flashedCells.value = changed
    clearTimeout(flashTimer)
    flashTimer = setTimeout(() => {
      flashedCells.value = new Set()
    }, FLASH_MS)
  }
)

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
  neighborOrder.value = row?.cf?.neighbors?.map((n) => n.neighbor_id) || []
  // Only on a genuine tutor change — the early return above keeps the panel open
  // across what-if refetches, which is where the flashed cell has to be visible.
  openNeighborId.value = null
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
onBeforeUnmount(() => {
  clearTimers()
  clearTimeout(flashTimer)
})
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
          <div class="cf-zone-headers">
            <span class="cf-zone-label">Evidence — similarity &amp; rating</span>
            <span></span>
            <span class="cf-zone-label">Effect on baseline</span>
          </div>

          <div class="cf-row">
            <div class="cf-evidence">
              <div class="cf-name">Baseline<small>tutee's own average</small></div>
            </div>
            <div class="cf-divider"></div>
            <div class="cf-track">
              <div class="cf-seg base" :style="{ left: '0%', width: pct(cf.student_avg) + '%' }"></div>
              <span class="cf-segval" :style="{ left: `calc(${pct(cf.student_avg)}% + 6px)` }">
                {{ cf.student_avg.toFixed(2) }}
              </span>
            </div>
          </div>

          <template v-for="step in steps" :key="step.neighbor.neighbor_id">
          <div class="cf-row">
            <div class="cf-evidence">
              <div class="cf-name">
                {{ step.neighbor.name }}
                <button
                  type="button"
                  class="cf-corated-toggle"
                  :class="{ warn: step.neighbor.co_rated_count < MIN_MEANINGFUL_CO_RATED }"
                  :aria-expanded="openNeighborId === step.neighbor.neighbor_id"
                  @click="toggleCoRated(step.neighbor.neighbor_id)"
                >
                  <span aria-hidden="true">{{
                    openNeighborId === step.neighbor.neighbor_id ? '▾' : '▸'
                  }}</span>
                  <template v-if="step.neighbor.co_rated_count < MIN_MEANINGFUL_CO_RATED">
                    only {{ step.neighbor.co_rated_count }} co-rated
                  </template>
                  <template v-else>{{ step.neighbor.co_rated_count }} co-rated</template>
                </button>
              </div>

              <div class="cf-evidence-line">
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
                </div>
                <span class="cf-avg">avg {{ step.neighbor.neighbor_avg.toFixed(2) }}</span>
              </div>
            </div>

            <div class="cf-divider"></div>

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

          <!-- The evidence behind the similarity meter above: the tutors both
               students rated, and what each gave them. -->
          <div
            v-if="openNeighborId === step.neighbor.neighbor_id && openCoRated"
            class="cf-corated"
          >
            <div
              class="cf-corated-grid"
              :style="{ '--shared-count': openCoRated.shared.length }"
            >
              <div class="cf-corated-head cf-corated-rowlabel">shared tutor</div>
              <div
                v-for="entry in openCoRated.shared"
                :key="`h-${entry.tutor_id}`"
                class="cf-corated-head"
                :title="entry.name"
              >
                {{ entry.last_name }}
              </div>
              <div class="cf-corated-head cf-corated-avg">avg over these</div>

              <div class="cf-corated-rowlabel me">This tutee</div>
              <div
                v-for="entry in openCoRated.shared"
                :key="`s-${entry.tutor_id}`"
                class="cf-corated-cell me"
                :class="{ flash: isFlashed(`${step.neighbor.neighbor_id}:${entry.tutor_id}:student`) }"
              >
                {{ entry.student_rating }}
              </div>
              <div
                class="cf-corated-cell cf-corated-avg me"
                :class="{ flash: isFlashed(`${step.neighbor.neighbor_id}:avg:student`) }"
              >
                {{ openCoRated.student_avg_over_set.toFixed(2) }}
                <small>feeds similarity</small>
              </div>

              <div class="cf-corated-rowlabel">{{ step.neighbor.name }}</div>
              <div
                v-for="entry in openCoRated.shared"
                :key="`n-${entry.tutor_id}`"
                class="cf-corated-cell"
                :class="{ flash: isFlashed(`${step.neighbor.neighbor_id}:${entry.tutor_id}:neighbor`) }"
              >
                {{ entry.neighbor_rating }}
              </div>
              <div
                class="cf-corated-cell cf-corated-avg"
                :class="{ flash: isFlashed(`${step.neighbor.neighbor_id}:avg:neighbor`) }"
              >
                {{ openCoRated.neighbor_avg_over_set.toFixed(2) }}
                <small>feeds similarity</small>
              </div>
            </div>

            <p class="cf-corated-note">
              Similarity is measured over these shared tutors only, against each student's
              average across them. That is a different baseline from the deviation term,
              which uses this neighbour's average over
              <b>all</b> their ratings ({{ step.neighbor.neighbor_avg.toFixed(2) }}) and this
              tutee's baseline of <b>{{ cf.student_avg.toFixed(2) }}</b>.
            </p>
          </div>
          </template>

          <div class="cf-row cf-row-total">
            <div class="cf-evidence">
              <div class="cf-name total">CF score</div>
            </div>
            <div class="cf-divider"></div>
            <div class="cf-track">
              <div class="cf-seg total" :style="{ left: '0%', width: pct(cf.score) + '%' }"></div>
              <span class="cf-segval total" :style="{ left: `calc(${pct(cf.score)}% + 6px)` }">
                {{ cf.score.toFixed(2) }}
              </span>
              <div class="cf-axis">
                <span>{{ axis.lo.toFixed(1) }}</span>
                <span>{{ ((axis.lo + axis.hi) / 2).toFixed(1) }}</span>
                <span>{{ axis.hi.toFixed(1) }}</span>
              </div>
            </div>
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

      <section v-if="tieGroup.length > 1" class="tie-block">
        <h5>Tie Breaker — Upcoming Week Load</h5>
        <p class="tie-note">
          {{ tieGroup.length }} tutors tied at
          {{ row.hybrid_score.toFixed(HYBRID_SCORE_PRECISION) }}. Fewer sessions booked in the next
          {{ UPCOMING_WEEK_DAYS }} days ranks higher.
        </p>
        <div
          v-for="peer in tieGroup"
          :key="peer.tutor_id"
          class="tie-cmp"
          :class="{ current: peer.tutor_id === row.tutor_id }"
        >
          <span>{{ peer.name }}</span>
          <span>
            {{ peer.upcoming_week_load }}
            {{ peer.upcoming_week_load === 1 ? 'session' : 'sessions' }} → rank {{ peer.rank }}
          </span>
        </div>
      </section>
    </template>
    <p v-else class="empty-state">Select a tutor to see the calculation.</p>
  </div>
</template>

<style scoped>
.algo-breakdown {
  min-height: 320px;
  /* Compare Pair renders this component at half width; the co-rated grid tightens
     against the component's own width, not the viewport's. */
  container-type: inline-size;
}

.tie-block {
  border: 1px dashed color-mix(in srgb, var(--sb-warning, #d29922) 50%, transparent);
  background: color-mix(in srgb, var(--sb-warning, #d29922) 7%, transparent);
  border-radius: 8px;
  padding: 10px 12px;
  margin-top: 14px;
}

.tie-block h5 {
  margin: 0 0 8px;
  font-size: 11px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--sb-warning, #d29922);
}

.tie-note {
  margin: 0 0 8px;
  font-size: 11px;
  color: var(--sb-text-muted);
}

.tie-cmp {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 3px 0;
  font-size: 12px;
}

.tie-cmp.current {
  font-weight: 700;
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

.cf-zone-headers,
.cf-row {
  display: grid;
  grid-template-columns: minmax(220px, 320px) 1px 1fr;
  gap: 20px;
  align-items: center;
}

.cf-zone-headers {
  font-size: 10.5px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--sb-text-muted);
  padding-bottom: 10px;
  border-bottom: 1px solid var(--sb-card-border);
}

.cf-zone-label {
  display: block;
}

.cf-row {
  padding: 14px 0;
  border-bottom: 1px solid var(--sb-card-border);
  align-items: center;
}

.cf-row:last-of-type {
  border-bottom: none;
}

.cf-divider {
  align-self: stretch;
  background: var(--sb-card-border);
}

.cf-evidence {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cf-name {
  font-size: 13.5px;
  font-weight: 700;
}

.cf-name.total {
  font-weight: 700;
}

.cf-name small {
  display: inline-block;
  font-weight: 400;
  font-size: 11px;
  color: var(--sb-text-muted);
  margin-left: 6px;
}

.cf-name small.warn {
  color: var(--sb-danger);
}

/* Co-rated set: disclosure control on the neighbour row, and the grid it opens. */
.cf-corated-toggle {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-left: 6px;
  padding: 0;
  border: 0;
  background: none;
  font: inherit;
  font-weight: 400;
  font-size: 11px;
  color: var(--sb-text-muted);
  cursor: pointer;
  text-decoration: underline dotted;
  text-underline-offset: 2px;
}

.cf-corated-toggle:hover,
.cf-corated-toggle:focus-visible {
  color: var(--sb-primary);
}

.cf-corated-toggle.warn {
  color: var(--sb-danger);
}

.cf-corated {
  margin: 2px 0 10px 10px;
  padding: 10px 0 4px 14px;
  border-left: 2px solid var(--sb-primary);
}

.cf-corated-grid {
  display: grid;
  grid-template-columns: auto repeat(var(--shared-count), minmax(0, 1fr)) auto;
  gap: 0 10px;
  align-items: center;
  font-variant-numeric: tabular-nums;
}

.cf-corated-grid > div {
  padding: 4px 0;
  text-align: center;
}

.cf-corated-head {
  font-size: 11px;
  color: var(--sb-text-muted);
  border-bottom: 1px solid var(--sb-card-border);
}

.cf-corated-head[title] {
  cursor: help;
}

.cf-corated-rowlabel {
  text-align: left;
  font-size: 12px;
  color: var(--sb-text-muted);
  white-space: nowrap;
}

.cf-corated-cell.me,
.cf-corated-rowlabel.me {
  color: var(--sb-primary);
}

.cf-corated-avg {
  text-align: right;
  font-weight: 700;
}

.cf-corated-avg small {
  display: block;
  font-weight: 400;
  font-size: 10px;
  color: var(--sb-warning, #d29922);
}

/* A what-if edit can land inside the co-rated set; highlight exactly what moved. */
.cf-corated-cell.flash {
  border-radius: 3px;
  box-shadow: 0 0 0 1px var(--sb-primary);
  transition: box-shadow 0.3s ease;
}

.cf-corated-note {
  margin: 8px 0 0;
  font-size: 11px;
  line-height: 1.5;
  color: var(--sb-text-muted);
}

/* Compare Pair renders this component two-up, so the grid has to survive half
   width rather than fork into a second layout. */
@container (max-width: 560px) {
  .cf-corated-grid {
    gap: 0 4px;
    font-size: 12px;
  }

  .cf-corated-head {
    font-size: 10px;
  }

  .cf-corated-rowlabel {
    font-size: 11px;
  }
}

.cf-evidence-line {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.cf-meter-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cf-meter {
  width: 80px;
  background: var(--sb-card-border);
  border-radius: 5px;
  height: 10px;
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
  font-size: 12px;
  font-weight: 700;
  color: var(--sb-primary);
  min-width: 30px;
}

.cf-rate {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cf-rate input[type='range'] {
  width: 100px;
  accent-color: var(--sb-primary);
  cursor: pointer;
}

.cf-rateval {
  font-size: 13px;
  font-weight: 700;
  min-width: 24px;
}

.cf-avg {
  font-size: 11px;
  color: var(--sb-text-muted);
}

.cf-track {
  position: relative;
  height: 30px;
}

.cf-seg {
  position: absolute;
  top: 7px;
  height: 18px;
  border-radius: 5px;
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
  height: 22px;
  top: 5px;
}

.cf-segval {
  position: absolute;
  top: 7px;
  font-size: 12.5px;
  font-weight: 700;
  color: var(--sb-primary);
  white-space: nowrap;
  transition: left 0.28s ease;
}

.cf-segval.neg {
  color: var(--sb-danger);
}

.cf-segval.total {
  font-size: 14px;
}

.cf-row-total .cf-track {
  height: 46px;
}

.cf-axis {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--sb-text-muted);
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
}

.cf-formula {
  font-size: 13px;
  color: var(--sb-text-muted);
  margin: 16px 0 0;
  padding-top: 12px;
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
