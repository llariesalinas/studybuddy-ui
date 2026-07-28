<script setup>
import { computed } from 'vue'

// Side-by-side view of the top candidates' full CBF/CF breakdown, so the panel can see
// which weights actually drove the ranking instead of inspecting one tutor at a time.
// See docs/plans/2026-07-23-algorithm-demo-cf-clarity.md.

const props = defineProps({
  rows: {
    type: Array,
    default: () => []
  },
  selectedTutorId: {
    type: [String, Number],
    default: null
  },
  limit: {
    type: Number,
    default: 5
  }
})

defineEmits(['select'])

const CBF_COLUMNS = [
  ['specific', 'Specific'],
  ['general', 'General'],
  ['expertise', 'Expertise'],
  ['course', 'Course'],
  ['year', 'Year'],
  ['level', 'Level']
]
// Alpha floor keeps a zero-value cell visible as a cell; the range above it tracks the
// sub-score so the eye lands on the weights that carried the ranking.
const SHADE_MIN_ALPHA = 0.05
const SHADE_RANGE = 0.25

const topRows = computed(() => props.rows.slice(0, props.limit))

const weights = computed(() => {
  const first = props.rows[0]
  if (!first) return {}
  return Object.fromEntries(CBF_COLUMNS.map(([key]) => [key, first.cbf[key].weight]))
})

function cellStyle(value) {
  if (value === 0) {
    return { background: 'color-mix(in srgb, var(--sb-danger) 9%, transparent)' }
  }
  const alpha = (SHADE_MIN_ALPHA + value * SHADE_RANGE) * 100
  return { background: `color-mix(in srgb, var(--sb-primary) ${alpha.toFixed(1)}%, transparent)` }
}
</script>

<template>
  <div v-if="topRows.length" class="weight-table-wrap sb-card">
    <header class="wt-header">
      <h3>Top {{ topRows.length }} side by side</h3>
      <p>Each cell shows the sub-score with its weighted contribution beneath. Click a row to
        open its full calculation.</p>
    </header>

    <div class="wt-scroll">
      <table class="wt-table">
        <thead>
          <tr>
            <th class="left">#&nbsp;&nbsp;Tutor</th>
            <th v-for="[key, label] in CBF_COLUMNS" :key="key">
              {{ label }}<br /><span class="wt-weight">w {{ weights[key]?.toFixed(2) }}</span>
            </th>
            <th>CBF<br /><span class="wt-weight">× .70</span></th>
            <th>CF<br /><span class="wt-weight">× .30</span></th>
            <th>Hybrid</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(row, index) in topRows"
            :key="row.tutor_id"
            class="wt-row"
            :class="{ selected: row.tutor_id === selectedTutorId }"
            @click="$emit('select', row.tutor_id)"
          >
            <td class="left">
              <b>{{ index + 1 }}&nbsp;&nbsp;{{ row.name }}</b>
            </td>
            <td v-for="[key] in CBF_COLUMNS" :key="key">
              <span class="wt-cell" :style="cellStyle(row.cbf[key].value)">
                <span class="wt-value">{{ row.cbf[key].value.toFixed(2) }}</span>
                <span class="wt-contrib">{{ row.cbf[key].contribution.toFixed(3) }}</span>
              </span>
            </td>
            <td><b>{{ row.cbf.score.toFixed(3) }}</b></td>
            <td class="wt-cf">
              <template v-if="row.cold_start">
                <span class="sb-badge cold">Cold Start</span>
              </template>
              <template v-else-if="row.cf.score === null">
                <span class="sb-badge none">no signal</span>
              </template>
              <template v-else>
                {{ row.cf.score.toFixed(2) }}
                <span class="sb-badge" :class="row.cf.pool">{{ row.cf.pool }}</span>
              </template>
            </td>
            <td><b class="wt-hybrid">{{ row.hybrid_score.toFixed(3) }}</b></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.weight-table-wrap {
  margin-bottom: 18px;
}

.sb-card {
  background: var(--sb-card-bg);
  border: 1px solid var(--sb-card-border);
  border-radius: 14px;
  padding: 16px 18px;
}

.wt-header h3 {
  margin: 0 0 2px;
  font-size: 14px;
}

.wt-header p {
  margin: 0 0 12px;
  font-size: 11.5px;
  color: var(--sb-text-muted);
}

.wt-scroll {
  overflow-x: auto;
}

.wt-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.wt-table th {
  padding: 6px;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--sb-text-muted);
  border-bottom: 1px solid var(--sb-card-border);
  text-align: center;
  white-space: nowrap;
}

.wt-weight {
  font-weight: 400;
  text-transform: none;
  letter-spacing: 0;
}

.wt-table th.left,
.wt-table td.left {
  text-align: left;
  white-space: nowrap;
}

.wt-table td {
  padding: 6px;
  text-align: center;
  border-bottom: 1px solid var(--sb-card-border);
}

.wt-row {
  cursor: pointer;
}

.wt-row:hover td {
  background: color-mix(in srgb, var(--sb-primary) 5%, transparent);
}

.wt-row.selected td {
  background: color-mix(in srgb, var(--sb-primary) 10%, transparent);
}

.wt-cell {
  display: block;
  border-radius: 5px;
  padding: 3px 0;
}

.wt-value {
  font-weight: 600;
}

.wt-contrib {
  display: block;
  font-size: 10px;
  color: var(--sb-text-muted);
}

.wt-cf {
  white-space: nowrap;
}

.wt-hybrid {
  color: var(--sb-primary);
  font-size: 13px;
}

.sb-badge {
  display: inline-block;
  background: color-mix(in srgb, var(--sb-primary) 12%, transparent);
  color: var(--sb-primary);
  border: 1px solid color-mix(in srgb, var(--sb-primary) 25%, transparent);
  border-radius: 9999px;
  font-size: 9.5px;
  font-weight: 600;
  padding: 1px 7px;
  margin-left: 4px;
}

.sb-badge.global {
  background: color-mix(in srgb, var(--sb-info, #2f6db3) 12%, transparent);
  color: var(--sb-info, #2f6db3);
  border-color: color-mix(in srgb, var(--sb-info, #2f6db3) 30%, transparent);
}

.sb-badge.cold,
.sb-badge.none {
  background: color-mix(in srgb, var(--sb-danger) 12%, transparent);
  color: var(--sb-danger);
  border-color: color-mix(in srgb, var(--sb-danger) 30%, transparent);
  margin-left: 0;
}
</style>
