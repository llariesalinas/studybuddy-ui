<template>
  <div class="report-detail">
    <header class="detail-header">
      <div>
        <RouterLink :to="backTo" class="crumb">
          <i class="bi bi-arrow-left"></i>
          Platform Reports
        </RouterLink>
        <p class="eyebrow">{{ dataset.eyebrow }}</p>
        <h1>{{ dataset.title }}</h1>
        <p class="scope">{{ scopeLine }}</p>
      </div>
      <div class="detail-controls">
        <SbDateRangeFilter
          :model-value="period"
          :presets="periodOptions"
          :custom-value="REPORT_PERIOD_CUSTOM"
          :date-from="draftFrom"
          :date-to="draftTo"
          aria-label="Report period"
          @update:model-value="setPeriod"
          @update:date-from="draftFrom = $event"
          @update:date-to="draftTo = $event"
          @apply="applyCustomRange"
        />
        <button
          type="button"
          class="export-button"
          :disabled="store.loading.export || !rows.length"
          @click="exportDataset"
        >
          <i class="bi bi-download"></i>
          Export
        </button>
      </div>
    </header>

    <section class="table-panel">
      <div class="table-toolbar">
        <div class="search-field">
          <i class="bi bi-search"></i>
          <input
            v-model="search"
            type="search"
            :placeholder="dataset.searchPlaceholder"
            :aria-label="dataset.searchPlaceholder"
          />
        </div>
        <p class="result-count">{{ resultCountLabel }}</p>
      </div>

      <div v-if="store.loading.analyticsDetail" class="detail-skeleton placeholder-glow">
        <span v-for="line in SKELETON_ROWS" :key="line" class="placeholder col-12 rounded"></span>
      </div>

      <div v-else-if="store.error.analyticsDetail" class="empty-state">
        <i class="bi bi-exclamation-triangle"></i>
        <p>{{ store.error.analyticsDetail }}</p>
        <button type="button" class="retry-button" @click="loadDetail">Try again</button>
      </div>

      <div v-else-if="!visibleRows.length" class="empty-state">
        <i class="bi bi-inbox"></i>
        <p>{{ rows.length ? 'No rows match your search.' : dataset.emptyMessage }}</p>
      </div>

      <div v-else class="table-responsive">
        <table class="table align-middle mb-0">
          <thead>
            <tr>
              <th
                v-for="column in dataset.columns"
                :key="column.key"
                :class="{ 'text-end': isNumeric(column), sorted: sort.key === column.key }"
              >
                <button type="button" class="sort-button" @click="toggleSort(column.key)">
                  {{ column.header }}
                  <i v-if="sort.key === column.key" :class="sortIconClass"></i>
                </button>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in visibleRows" :key="rowKey(row, index)">
              <td
                v-for="column in dataset.columns"
                :key="column.key"
                :class="cellClass(column)"
              >
                {{ formatCell(row[column.key], column) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import SbDateRangeFilter from '@/components/SbDateRangeFilter.vue'
import { useHaptics } from '@/composables/useHaptics'
import { useSuperAdminStore } from '@/stores/superadmin'
import { useToastStore } from '@/stores/toast'
import { exportFilename } from '@/utils/csv'
import { formatCount, formatDecimal, formatPhp } from '@/utils/currency'
import {
  ALL_INSTITUTIONS_LABEL,
  REPORT_DEFAULT_PERIOD,
  REPORT_DETAIL_DATASETS,
  REPORT_COLUMN_MONEY,
  REPORT_COLUMN_NUMBER,
  REPORT_COLUMN_PERCENT,
  REPORT_COLUMN_RATING,
  REPORT_COLUMN_TEXT,
  REPORT_PERIOD_CUSTOM,
  REPORT_PERIOD_OPTIONS,
  SORT_ASCENDING,
  SORT_DESCENDING,
  reportPeriodScopeLabel,
  sortReportRows,
} from '@/constants/superadminReports'

const SKELETON_ROWS = 8
const NUMERIC_COLUMN_TYPES = [
  REPORT_COLUMN_NUMBER,
  REPORT_COLUMN_RATING,
  REPORT_COLUMN_MONEY,
  REPORT_COLUMN_PERCENT,
]

const route = useRoute()
const router = useRouter()
const store = useSuperAdminStore()
const toastStore = useToastStore()
const { vibrate, patterns } = useHaptics()

const periodOptions = REPORT_PERIOD_OPTIONS

// Which dataset this page shows comes from the route, so both routes share one component.
const dataset = computed(() => REPORT_DETAIL_DATASETS[route.meta.dataset])

// Filters live in the query string rather than component state: the page must show the same slice
// as the card that opened it, survive a refresh, and be linkable.
const period = computed(() => {
  const requested = route.query.period
  return periodOptions.some((option) => option.value === requested)
    ? requested
    : REPORT_DEFAULT_PERIOD
})
const institutionId = computed(() => route.query.institution || '')

// Like every other filter here, the range lives in the query string so the page stays linkable
// and matches the card that opened it. The drafts are the unconfirmed input values.
const dateFrom = computed(() => (period.value === REPORT_PERIOD_CUSTOM ? String(route.query.from || '') : ''))
const dateTo = computed(() => (period.value === REPORT_PERIOD_CUSTOM ? String(route.query.to || '') : ''))

const draftFrom = ref(String(route.query.from || ''))
const draftTo = ref(String(route.query.to || ''))

const search = ref('')
const sort = ref({ ...dataset.value.defaultSort })

const filterQuery = computed(() => {
  const query = { period: period.value }
  if (institutionId.value) query.institution = institutionId.value
  if (dateFrom.value) query.from = dateFrom.value
  if (dateTo.value) query.to = dateTo.value
  return query
})

// Carries the filters back so the dashboard reopens on the slice this page was reached from.
const backTo = computed(() => ({
  name: 'superadmin-reports',
  query: filterQuery.value,
}))

const institutionName = computed(() => {
  if (!institutionId.value) return ALL_INSTITUTIONS_LABEL
  const match = store.institutions.find(
    (institution) => String(institution.id) === String(institutionId.value),
  )
  return match?.institution_name || ALL_INSTITUTIONS_LABEL
})

const total = computed(() => store.analyticsDetail?.[dataset.value.totalKey] ?? 0)

const scopeLine = computed(() =>
  [
    `${total.value} ${dataset.value.countNoun}`,
    reportPeriodScopeLabel(period.value, dateFrom.value, dateTo.value),
    institutionName.value,
  ].join(' · '),
)

const rows = computed(() => dataset.value.rows(store.analyticsDetail))

const searchedRows = computed(() => {
  const term = search.value.trim().toLowerCase()
  if (!term) return rows.value
  const key = dataset.value.searchKey
  return rows.value.filter((row) => String(row[key] ?? '').toLowerCase().includes(term))
})

const visibleRows = computed(() =>
  sortReportRows(searchedRows.value, sort.value.key, sort.value.direction),
)

const resultCountLabel = computed(() => {
  const shown = visibleRows.value.length
  return shown === rows.value.length
    ? `${shown} shown`
    : `${shown} of ${rows.value.length} shown`
})

const sortIconClass = computed(() =>
  sort.value.direction === SORT_ASCENDING ? 'bi bi-caret-up-fill' : 'bi bi-caret-down-fill',
)

watch(
  () => [period.value, institutionId.value, dateFrom.value, dateTo.value],
  () => loadDetail(),
)

watch(
  () => route.meta.dataset,
  () => {
    search.value = ''
    sort.value = { ...dataset.value.defaultSort }
    loadDetail()
  },
)

onMounted(() => {
  if (!store.institutions.length) store.fetchInstitutions()
  loadDetail()
})

function loadDetail() {
  // An incomplete custom range would 400; wait for Apply to fill both endpoints.
  if (period.value === REPORT_PERIOD_CUSTOM && (!dateFrom.value || !dateTo.value)) return
  store.fetchAnalyticsDetail(institutionId.value || null, period.value, dateFrom.value, dateTo.value)
}

// `replace` rather than `push`: changing a filter on this page is a refinement, not a new
// destination, so Back still returns to the dashboard instead of walking every period tried.
function setPeriod(value) {
  vibrate(patterns.light)
  const query = { ...filterQuery.value, period: value }

  if (value !== REPORT_PERIOD_CUSTOM) {
    delete query.from
    delete query.to
  }

  router.replace({ query })
}

function applyCustomRange() {
  vibrate(patterns.light)
  router.replace({
    query: {
      ...filterQuery.value,
      period: REPORT_PERIOD_CUSTOM,
      from: draftFrom.value,
      to: draftTo.value,
    },
  })
}

function toggleSort(key) {
  vibrate(patterns.light)
  if (sort.value.key === key) {
    sort.value = {
      key,
      direction: sort.value.direction === SORT_ASCENDING ? SORT_DESCENDING : SORT_ASCENDING,
    }
    return
  }
  sort.value = { key, direction: SORT_DESCENDING }
}

function isNumeric(column) {
  return NUMERIC_COLUMN_TYPES.includes(column.type)
}

function cellClass(column) {
  return {
    'text-end': isNumeric(column),
    'fw-bold': column.type === REPORT_COLUMN_TEXT,
  }
}

function rowKey(row, index) {
  return `${row[dataset.value.searchKey] ?? 'row'}-${index}`
}

function formatCell(value, column) {
  if (value === null || value === undefined || value === '') return '--'

  switch (column.type) {
    case REPORT_COLUMN_MONEY:
      return formatPhp(value)
    case REPORT_COLUMN_RATING:
      return formatDecimal(value, 2)
    case REPORT_COLUMN_PERCENT:
      return `${formatDecimal(Number(value) * 100, 1)}%`
    case REPORT_COLUMN_NUMBER:
      return formatCount(value)
    default:
      return value
  }
}

async function exportDataset() {
  try {
    await store.exportAnalyticsWorkbook({
      institutionId: institutionId.value || null,
      period: period.value,
      dateFrom: dateFrom.value,
      dateTo: dateTo.value,
      sections: [dataset.value.exportSection],
      filename: exportFilename(dataset.value.exportFileLabel, 'xlsx'),
    })
  } catch {
    toastStore.push('Failed to export the report.', 'error')
  }
}
</script>

<style scoped>
.report-detail {
  padding: 1.5rem 1.75rem 3rem;
  color: var(--sb-text-main);
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1.25rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.crumb {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--sb-primary);
  text-decoration: none;
  margin-bottom: 0.6rem;
}

.crumb:hover { text-decoration: underline; }

.eyebrow {
  font-size: 0.68rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--sb-text-muted);
  margin: 0;
}

.detail-header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0.2rem 0 0;
}

.scope {
  font-size: 0.85rem;
  color: var(--sb-text-muted);
  margin: 0.35rem 0 0;
}

.detail-controls {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.export-button {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  border: 0;
  border-radius: 999px;
  background: var(--sb-primary);
  color: #fff;
  font-size: 0.82rem;
  font-weight: 600;
  padding: 0.45rem 1.1rem;
}

.export-button:disabled { opacity: 0.6; }

.table-panel {
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid var(--sb-card-border);
  border-radius: 18px;
  overflow: hidden;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 0.85rem 1.1rem;
  border-bottom: 1px solid var(--sb-card-border);
  flex-wrap: wrap;
}

.search-field {
  position: relative;
  flex: 1 1 240px;
  max-width: 360px;
}

.search-field i {
  position: absolute;
  left: 0.85rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--sb-text-muted);
  font-size: 0.85rem;
}

.search-field input {
  width: 100%;
  border: 1px solid var(--sb-card-border);
  border-radius: 999px;
  padding: 0.4rem 0.9rem 0.4rem 2.2rem;
  font-size: 0.85rem;
  background: #fff;
  color: var(--sb-text-main);
}

.search-field input:focus {
  outline: none;
  border-color: var(--sb-primary);
}

.result-count {
  margin: 0;
  font-size: 0.78rem;
  color: var(--sb-text-muted);
}

.table-panel thead th {
  font-size: 0.7rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--sb-text-muted);
  border-color: var(--sb-card-border);
  padding: 0.5rem 0.75rem;
}

.table-panel thead th.sorted { color: var(--sb-primary); }

.sort-button {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  border: 0;
  background: none;
  padding: 0;
  font: inherit;
  color: inherit;
  letter-spacing: inherit;
  text-transform: inherit;
}

.table-panel thead th.text-end .sort-button { flex-direction: row-reverse; }

.table-panel tbody td {
  border-color: var(--sb-card-border);
  font-size: 0.88rem;
  padding: 0.55rem 0.75rem;
}

.detail-skeleton {
  display: grid;
  gap: 0.6rem;
  padding: 1.1rem;
}

.detail-skeleton .placeholder { height: 1.4rem; }

.empty-state {
  display: grid;
  justify-items: center;
  gap: 0.5rem;
  padding: 3rem 1rem;
  color: var(--sb-text-muted);
}

.empty-state i { font-size: 1.6rem; }
.empty-state p { margin: 0; }

.retry-button {
  border: 1px solid var(--sb-card-border);
  border-radius: 999px;
  background: #fff;
  color: var(--sb-text-main);
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.35rem 1rem;
}

@media (max-width: 640px) {
  .report-detail { padding: 1.1rem 1rem 2.5rem; }
  .detail-header { flex-direction: column; align-items: stretch; }
}
</style>
