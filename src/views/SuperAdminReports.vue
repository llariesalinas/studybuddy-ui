<template>
  <div class="superadmin-reports">
    <header class="reports-header">
      <div>
        <p class="eyebrow">Analytics</p>
        <h1>Platform Reports</h1>
        <span v-if="selectedInstitutionName">Viewing {{ selectedInstitutionName }}</span>
      </div>
      <div class="reports-controls">
        <SbDateRangeFilter
          :model-value="period"
          :presets="periodOptions"
          :custom-value="REPORT_PERIOD_CUSTOM"
          :date-from="dateFrom"
          :date-to="dateTo"
          aria-label="Report period"
          @update:model-value="setPeriod"
          @update:date-from="dateFrom = $event"
          @update:date-to="dateTo = $event"
          @apply="applyCustomRange"
        />
        <SbSelectModal
          v-model="selectedInstitutionId"
          :options="institutionOptions"
          title="Filter Institution"
          placeholder="All institutions"
          searchable
          clearable
          clear-label="All institutions"
          trigger-class="institution-trigger"
        />
        <button type="button" class="export-button" :disabled="store.loading.export" @click="openExportModal">
          <i class="bi bi-download"></i>
          Export
        </button>
      </div>
    </header>

    <SbExportModal
      :open="isExportOpen"
      title="Export report"
      :items="exportSections"
      :scope-line="exportScopeLine"
      :combined-file-label="REPORT_COMBINED_FILE_LABEL"
      file-extension="xlsx"
      :busy="store.loading.export"
      @confirm="exportWorkbook"
      @close="isExportOpen = false"
    />

    <section class="metric-grid">
      <article v-for="metric in metrics" :key="metric.label" class="metric-card sb-card-lift" :class="{ primary: metric.primary }">
        <p>{{ metric.label }}</p>
        <h2 :title="metric.value">{{ metric.value }}</h2>
        <span>{{ metric.caption }}</span>
      </article>
    </section>

    <section class="chart-panel">
      <div class="panel-heading">
        <div>
          <p class="eyebrow">Sessions</p>
          <h2>Completed sessions over time</h2>
        </div>
        <button type="button" class="refresh-button" :disabled="store.loading.analytics" @click="loadAnalytics">
          <i class="bi bi-arrow-clockwise"></i>
          Refresh
        </button>
      </div>

      <Transition name="fade" mode="out-in">
        <div v-if="store.loading.analytics" class="chart-skeleton placeholder-glow">
          <span class="placeholder col-12 rounded"></span>
        </div>
        <div v-else class="area-chart-wrap">
          <svg viewBox="0 0 580 120" role="img" aria-label="Completed sessions chart">
            <defs>
              <linearGradient id="sessionsArea" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stop-color="var(--sb-primary)" stop-opacity="0.18" />
                <stop offset="100%" stop-color="var(--sb-primary)" stop-opacity="0" />
              </linearGradient>
            </defs>
            <path :d="areaPath" fill="url(#sessionsArea)" />
            <polyline :points="linePoints" fill="none" stroke="var(--sb-primary)" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <div class="chart-labels">
            <span>{{ chartLabels[0] || '' }}</span>
            <span>{{ chartLabels[midLabelIndex] || '' }}</span>
            <span>{{ chartLabels.at(-1) || '' }}</span>
          </div>
        </div>
      </Transition>
    </section>

    <section class="reports-grid">
      <article class="table-panel">
        <div class="panel-heading">
          <div>
            <p class="eyebrow">Tutors</p>
            <h2>Top performers</h2>
          </div>
          <RouterLink v-if="tutorTotal > REPORT_CARD_ROW_LIMIT" :to="tutorsDetailTo" class="view-all">
            View all
          </RouterLink>
        </div>
        <div class="table-responsive">
          <table class="table align-middle mb-0">
            <thead>
              <tr>
                <th>Tutor</th>
                <th>Sessions</th>
                <th>Rating</th>
                <th class="text-end">Earnings</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="tutor in store.analytics?.top_tutors || []" :key="tutor.name">
                <td class="fw-bold">{{ tutor.name }}</td>
                <td>
                  <div class="bar-cell">
                    <span :style="{ width: `${(tutor.sessions / topSessionCount) * 100}%` }"></span>
                    <strong>{{ tutor.sessions }}</strong>
                  </div>
                </td>
                <td><i class="bi bi-star-fill rating-icon"></i>{{ formatDecimal(tutor.rating, 1) }}</td>
                <td class="text-end fw-bold">{{ formatPhp(tutor.earnings) }}</td>
              </tr>
              <tr v-if="!store.analytics?.top_tutors?.length">
                <td colspan="4" class="text-center py-5 text-muted">No tutor analytics available.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>

      <article class="subject-panel">
        <div class="panel-heading">
          <div>
            <p class="eyebrow">Demand</p>
            <h2>Subject popularity</h2>
          </div>
          <RouterLink
            v-if="subjectTotal > REPORT_CARD_ROW_LIMIT"
            :to="subjectsDetailTo"
            class="view-all"
          >
            View all
          </RouterLink>
        </div>
        <div v-if="subjectPopularity.length" class="subject-list">
          <div v-for="(subject, index) in subjectPopularity" :key="subject.subject_name" class="subject-row">
            <div>
              <span>{{ subject.subject_name }}</span>
              <strong>{{ subject.booking_count }}</strong>
            </div>
            <div class="subject-track">
              <span :style="{ width: `${(subject.booking_count / maxSubjectCount) * 100}%`, background: subjectColors[index % subjectColors.length] }"></span>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <i class="bi bi-diagram-3"></i>
          <p>No subject data for this period.</p>
        </div>
      </article>
    </section>

    <section class="table-panel institution-panel">
      <div class="panel-heading">
        <div>
          <p class="eyebrow">Institutions</p>
          <h2>Breakdown</h2>
        </div>
      </div>
      <div class="table-responsive">
        <table class="table align-middle mb-0">
          <thead>
            <tr>
              <th>Institution</th>
              <th class="text-center">Tutors</th>
              <th class="text-center">Tutees</th>
              <th class="text-center">Sessions</th>
              <th class="text-center">Completion</th>
              <th class="text-end">Commission</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="inst in store.institutionPerformance"
              :key="inst.id"
              :class="{ active: String(selectedInstitutionId) === String(inst.id) }"
              @click="selectInstitution(inst)"
            >
              <td class="fw-bold">{{ inst.institution_name }}</td>
              <td class="text-center">{{ inst.tutors }}</td>
              <td class="text-center">{{ inst.tutees }}</td>
              <td class="text-center">{{ inst.sessions }}</td>
              <td class="text-center">{{ formatDecimal(inst.completion_rate, 1) }}%</td>
              <td class="text-end fw-bold">{{ formatPhp(inst.revenue) }}</td>
            </tr>
            <tr v-if="!store.institutionPerformance.length">
              <td colspan="6" class="text-center py-5 text-muted">No institution data available.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import SbDateRangeFilter from '@/components/SbDateRangeFilter.vue'
import SbExportModal from '@/components/SbExportModal.vue'
import SbSelectModal from '@/components/SbSelectModal.vue'
import { useHaptics } from '@/composables/useHaptics'
import { useSuperAdminStore } from '@/stores/superadmin'
import { useToastStore } from '@/stores/toast'
import { REPORT_COMBINED_FILE_LABEL, REPORT_SECTIONS } from '@/constants/superadminExports'
import { formatDecimal, formatPhp } from '@/utils/currency'
import {
  ALL_INSTITUTIONS_LABEL,
  REPORT_CARD_ROW_LIMIT,
  REPORT_DEFAULT_PERIOD,
  REPORT_DETAIL_DATASETS,
  REPORT_PERIOD_CUSTOM,
  REPORT_PERIOD_OPTIONS,
  reportPeriodScopeLabel,
} from '@/constants/superadminReports'

const store = useSuperAdminStore()
const toastStore = useToastStore()
const { vibrate, patterns } = useHaptics()

const route = useRoute()

// Seeded from the query string so returning from a drill-down page restores the filters the user
// left with, rather than snapping back to the defaults.
const selectedInstitutionId = ref(route.query.institution ? String(route.query.institution) : '')
const period = ref(
  REPORT_PERIOD_OPTIONS.some((option) => option.value === route.query.period)
    ? String(route.query.period)
    : REPORT_DEFAULT_PERIOD,
)
const dateFrom = ref(route.query.from ? String(route.query.from) : '')
const dateTo = ref(route.query.to ? String(route.query.to) : '')

// The range is only sent once it is complete; a half-filled custom range would otherwise 400 on
// every keystroke. `appliedRange` is what requests actually use.
const appliedRange = ref({
  from: period.value === REPORT_PERIOD_CUSTOM ? dateFrom.value : '',
  to: period.value === REPORT_PERIOD_CUSTOM ? dateTo.value : '',
})

const isExportOpen = ref(false)

const exportSections = REPORT_SECTIONS

const periodOptions = REPORT_PERIOD_OPTIONS

const subjectColors = ['#00895a', '#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899']

const institutionOptions = computed(() => [
  { label: 'All institutions', value: '' },
  ...store.institutions.map((institution) => ({
    label: institution.institution_name,
    value: institution.id,
    description: institution.school_email_domain,
  })),
])

const selectedInstitutionName = computed(() => {
  if (!selectedInstitutionId.value) return null
  const inst = store.institutionPerformance.find((item) => String(item.id) === String(selectedInstitutionId.value))
  return inst?.institution_name || null
})

const exportScopeLine = computed(() =>
  [
    reportPeriodScopeLabel(period.value, appliedRange.value.from, appliedRange.value.to),
    selectedInstitutionName.value || ALL_INSTITUTIONS_LABEL,
  ].join(' · '),
)

// Carried into the drill-down routes so a detail page opens on the slice that was clicked, and so
// the crumb back from it restores these same filters.
const detailQuery = computed(() => {
  const query = { period: period.value }
  if (selectedInstitutionId.value) query.institution = selectedInstitutionId.value
  if (appliedRange.value.from) query.from = appliedRange.value.from
  if (appliedRange.value.to) query.to = appliedRange.value.to
  return query
})

// Totals come from the API rather than the rendered rows: the cards are truncated, so the row
// count cannot say how many exist behind them, and the figure moves with the period.
const tutorTotal = computed(() => store.analytics?.tutor_total ?? 0)
const subjectTotal = computed(() => store.analytics?.subject_total ?? 0)

const tutorsDetailTo = computed(() => ({
  name: REPORT_DETAIL_DATASETS.tutors.routeName,
  query: detailQuery.value,
}))

const subjectsDetailTo = computed(() => ({
  name: REPORT_DETAIL_DATASETS.subjects.routeName,
  query: detailQuery.value,
}))

const metrics = computed(() => [
  {
    label: 'Gross Revenue',
    value: formatPhp(store.analytics?.revenue_summary?.gross || 0),
    caption: 'Paid completed sessions',
    primary: true,
  },
  {
    label: 'Platform Commissions',
    value: formatPhp(store.analytics?.revenue_summary?.commissions || 0),
    caption: '10% platform fee',
  },
  {
    label: 'Tutor Payouts',
    value: formatPhp(store.analytics?.revenue_summary?.payouts || 0),
    caption: 'Tutor-side earnings',
  },
  {
    label: 'Completion Rate',
    value: `${formatDecimal(store.analytics?.completion_rate || 0, 1)}%`,
    caption: 'Completed / total sessions',
  },
])

const chartData = computed(() => store.analytics?.sessions_over_time?.data || [])
const chartLabels = computed(() => store.analytics?.sessions_over_time?.labels || [])
const midLabelIndex = computed(() => Math.floor((chartLabels.value.length - 1) / 2))

const linePoints = computed(() => {
  if (!chartData.value.length) return '0,105 580,105'
  const max = Math.max(...chartData.value, 1)
  const width = 580
  const height = 90
  const step = chartData.value.length > 1 ? width / (chartData.value.length - 1) : width

  return chartData.value
    .map((value, index) => {
      const x = index * step
      const y = 105 - (value / max) * height
      return `${x.toFixed(1)},${y.toFixed(1)}`
    })
    .join(' ')
})

const areaPath = computed(() => {
  const points = linePoints.value.split(' ')
  return `M ${points[0]} L ${points.join(' L ')} L 580,112 L 0,112 Z`
})

const topSessionCount = computed(() => {
  const tutors = store.analytics?.top_tutors || []
  if (!tutors.length) return 1
  return Math.max(...tutors.map((tutor) => tutor.sessions || 0), 1)
})

// The server also truncates, at its own larger cap. Slicing again here is what made the card show
// five subjects while the export sheet carried ten; the shared constant keeps the card's summary
// length stated once.
const subjectPopularity = computed(() =>
  (store.analytics?.subject_popularity || []).slice(0, REPORT_CARD_ROW_LIMIT),
)
const maxSubjectCount = computed(() => {
  if (!subjectPopularity.value.length) return 1
  return Math.max(...subjectPopularity.value.map((subject) => subject.booking_count || 0), 1)
})

watch(selectedInstitutionId, () => {
  vibrate(patterns.light)
  loadAnalytics()
})

onMounted(() => {
  store.fetchInstitutions()
  loadAnalytics()
})

function setPeriod(value) {
  period.value = value
  vibrate(patterns.light)

  // Selecting Custom only reveals the inputs -- nothing is refetched until Apply, since the range
  // is not yet known. Leaving Custom drops the range so the preset is unambiguous.
  if (value === REPORT_PERIOD_CUSTOM) {
    if (!appliedRange.value.from || !appliedRange.value.to) return
  } else {
    appliedRange.value = { from: '', to: '' }
  }

  loadAnalytics()
}

function applyCustomRange() {
  appliedRange.value = { from: dateFrom.value, to: dateTo.value }
  vibrate(patterns.light)
  loadAnalytics()
}

function selectInstitution(inst) {
  selectedInstitutionId.value = String(inst.id)
}

function loadAnalytics() {
  const { from, to } = appliedRange.value
  store.fetchAnalytics(selectedInstitutionId.value || null, period.value, from, to)
  // The institutions table is scoped to the same window, so it has to move with it.
  store.fetchInstitutionPerformance(true, { period: period.value, dateFrom: from, dateTo: to })
}

function openExportModal() {
  vibrate(patterns.light)
  isExportOpen.value = true
}

async function exportWorkbook({ ids, filename }) {
  isExportOpen.value = false
  try {
    await store.exportAnalyticsWorkbook({
      institutionId: selectedInstitutionId.value || null,
      period: period.value,
      dateFrom: appliedRange.value.from,
      dateTo: appliedRange.value.to,
      sections: ids,
      filename,
    })
  } catch {
    toastStore.push('Failed to export the report.', 'error')
  }
}

</script>

<style scoped>
.fade-enter-active,
.fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from,
.fade-leave-to { opacity: 0; }

.superadmin-reports {
  min-height: 100%;
  padding: 24px;
  color: var(--sb-text-main);
}

.reports-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 18px;
}

.eyebrow,
.metric-card p {
  color: var(--sb-text-muted);
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  margin: 0 0 4px;
}

h1 {
  font-size: 30px;
  font-weight: 800;
  margin: 0;
}

h2 {
  font-size: 20px;
  line-height: 1.2;
  font-weight: 800;
  margin: 0;
}

/* Exact peso figures ("₱1,234,567.89") are far wider than the abbreviated form these cards used
   to show, so the value scales with the column and is allowed to wrap rather than overflow the
   card on narrow viewports. */
.metric-card h2 {
  font-size: clamp(15px, 1.55vw + 8px, 20px);
  overflow-wrap: anywhere;
}

.reports-header span,
.metric-card span {
  color: var(--sb-text-muted);
  font-size: 13px;
}

.reports-controls {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.institution-trigger) {
  min-width: 210px;
  border-radius: 999px;
}

.export-button,
.refresh-button {
  border: 0;
  border-radius: 999px;
  background: var(--sb-primary);
  color: #fff;
  font-size: 13px;
  font-weight: 800;
  padding: 9px 15px;
  display: inline-flex;
  align-items: center;
  gap: 7px;
}

.refresh-button {
  background: #fff;
  border: 1px solid var(--sb-card-border);
  color: var(--sb-text-main);
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 18px;
}

.metric-card,
.chart-panel,
.table-panel,
.subject-panel {
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid var(--sb-card-border);
  border-radius: 18px;
  box-shadow: 0 12px 32px rgba(10, 25, 22, 0.06);
}

.metric-card {
  padding: 18px;
  min-height: 150px;
}

.metric-card.primary {
  background: var(--sb-primary);
  color: #fff;
}

.metric-card.primary p,
.metric-card.primary span {
  color: rgba(255, 255, 255, 0.76);
}

.metric-card h2 {
  font-size: 28px;
  margin: 18px 0 8px;
}

.chart-panel,
.subject-panel {
  padding: 20px;
}

.panel-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.view-all {
  display: inline-flex;
  align-items: center;
  flex: none;
  padding: 5px 14px;
  border: 1px solid var(--sb-card-border);
  border-radius: 999px;
  background: #fff;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--sb-primary);
  text-decoration: none;
  white-space: nowrap;
  transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}

.view-all:hover {
  background: var(--sb-primary);
  border-color: var(--sb-primary);
  color: #fff;
}

.chart-skeleton {
  height: 190px;
}

.chart-skeleton .placeholder {
  height: 100%;
}

.area-chart-wrap svg {
  width: 100%;
  height: 190px;
}

.chart-labels {
  display: flex;
  justify-content: space-between;
  color: var(--sb-text-muted);
  font-size: 12px;
  margin-top: 8px;
}

.reports-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(340px, 0.75fr);
  gap: 18px;
  margin: 18px 0;
}

.table-panel {
  overflow: hidden;
}

.table-panel .panel-heading {
  padding: 20px;
  margin-bottom: 0;
  border-bottom: 1px solid var(--sb-card-border);
}

.table thead th {
  color: var(--sb-text-muted);
  font-size: 12px;
  text-transform: uppercase;
  border: 0;
  padding: 14px 20px;
}

.table tbody td {
  border-color: var(--sb-card-border);
  padding: 16px 20px;
}

.bar-cell {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 120px;
}

.bar-cell > span {
  display: block;
  height: 8px;
  max-width: 110px;
  min-width: 4px;
  border-radius: 999px;
  background: var(--sb-primary);
  flex: 1 1 auto;
}

.bar-cell strong {
  color: var(--sb-text-main);
}

.rating-icon {
  color: #f59e0b;
  margin-right: 5px;
}

.subject-list {
  display: grid;
  gap: 14px;
}

.subject-row > div:first-child {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 7px;
  font-size: 13px;
}

.subject-row span {
  font-weight: 800;
}

.subject-row strong {
  color: var(--sb-text-muted);
}

.subject-track {
  height: 10px;
  border-radius: 999px;
  background: var(--sb-bg);
  overflow: hidden;
}

.subject-track span {
  display: block;
  height: 100%;
  min-width: 4px;
  border-radius: inherit;
}

.empty-state {
  text-align: center;
  color: var(--sb-text-muted);
  padding: 34px 12px;
}

.empty-state i {
  display: block;
  color: var(--sb-primary);
  font-size: 34px;
  margin-bottom: 8px;
}

.institution-panel tbody tr {
  cursor: pointer;
}

.institution-panel tbody tr.active {
  background: color-mix(in srgb, var(--sb-primary) 8%, transparent);
}

@media (max-width: 1100px) {
  .metric-grid,
  .reports-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 780px) {
  .superadmin-reports {
    padding: 16px;
  }

  .reports-header,
  .reports-controls {
    display: grid;
    grid-template-columns: 1fr;
    justify-content: stretch;
  }

  .metric-grid,
  .reports-grid {
    grid-template-columns: 1fr;
  }

  :deep(.institution-trigger),
  .export-button,
  .refresh-button {
    width: 100%;
  }
}
</style>
