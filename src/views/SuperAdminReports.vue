<template>
  <div class="superadmin-reports">
    <header class="reports-header">
      <div>
        <p class="eyebrow">Analytics</p>
        <h1>Platform Reports</h1>
        <span v-if="selectedInstitutionName">Viewing {{ selectedInstitutionName }}</span>
      </div>
      <div class="reports-controls">
        <div class="period-toggle" aria-label="Report period">
          <button
            v-for="option in periodOptions"
            :key="option.value"
            type="button"
            :class="{ active: period === option.value }"
            @click="setPeriod(option.value)"
          >
            {{ option.label }}
          </button>
        </div>
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
        <h2>{{ metric.value }}</h2>
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
                <td><i class="bi bi-star-fill rating-icon"></i>{{ formatNumber(tutor.rating, 1) }}</td>
                <td class="text-end fw-bold">PHP {{ formatMoney(tutor.earnings) }}</td>
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
              <td class="text-center">{{ formatNumber(inst.completion_rate, 1) }}%</td>
              <td class="text-end fw-bold">PHP {{ formatMoney(inst.revenue) }}</td>
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
import SbExportModal from '@/components/SbExportModal.vue'
import SbSelectModal from '@/components/SbSelectModal.vue'
import { useHaptics } from '@/composables/useHaptics'
import { useSuperAdminStore } from '@/stores/superadmin'
import { useToastStore } from '@/stores/toast'
import { REPORT_COMBINED_FILE_LABEL, REPORT_SECTIONS } from '@/constants/superadminExports'

const store = useSuperAdminStore()
const toastStore = useToastStore()
const { vibrate, patterns } = useHaptics()

const selectedInstitutionId = ref('')
const period = ref('30d')
const isExportOpen = ref(false)

const exportSections = REPORT_SECTIONS

const periodOptions = [
  { label: '7D', value: '7d' },
  { label: '30D', value: '30d' },
  { label: '3M', value: '3m' },
  { label: 'All', value: 'all' },
]

// Spelled-out forms of periodOptions, for the export modal's scope line where the terse
// toggle labels (7D, 3M) would read as jargon.
const periodScopeLabels = {
  '7d': 'Last 7 days',
  '30d': 'Last 30 days',
  '3m': 'Last 3 months',
  all: 'All time',
}

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
    periodScopeLabels[period.value] || period.value,
    selectedInstitutionName.value || 'All institutions',
  ].join(' · '),
)

const metrics = computed(() => [
  {
    label: 'Gross Revenue',
    value: `PHP ${formatCompact(store.analytics?.revenue_summary?.gross || 0)}`,
    caption: 'Paid completed sessions',
    primary: true,
  },
  {
    label: 'Platform Commissions',
    value: `PHP ${formatCompact(store.analytics?.revenue_summary?.commissions || 0)}`,
    caption: '10% platform fee',
  },
  {
    label: 'Tutor Payouts',
    value: `PHP ${formatCompact(store.analytics?.revenue_summary?.payouts || 0)}`,
    caption: 'Tutor-side earnings',
  },
  {
    label: 'Completion Rate',
    value: `${formatNumber(store.analytics?.completion_rate || 0, 1)}%`,
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

const subjectPopularity = computed(() => (store.analytics?.subject_popularity || []).slice(0, 5))
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
  store.fetchInstitutionPerformance()
  loadAnalytics()
})

function setPeriod(value) {
  period.value = value
  vibrate(patterns.light)
  loadAnalytics()
}

function selectInstitution(inst) {
  selectedInstitutionId.value = String(inst.id)
}

function loadAnalytics() {
  store.fetchAnalytics(selectedInstitutionId.value || null, period.value)
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
      sections: ids,
      filename,
    })
  } catch {
    toastStore.push('Failed to export the report.', 'error')
  }
}

function formatMoney(value) {
  return Number(value || 0).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

function formatCompact(value) {
  return Number(value || 0).toLocaleString(undefined, {
    notation: 'compact',
    maximumFractionDigits: 1,
  })
}

function formatNumber(value, digits = 0) {
  return Number(value || 0).toFixed(digits)
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

.period-toggle {
  display: inline-flex;
  gap: 4px;
  padding: 4px;
  border: 1px solid var(--sb-card-border);
  border-radius: 999px;
  background: #fff;
}

.period-toggle button {
  min-width: 48px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: var(--sb-text-muted);
  font-size: 13px;
  font-weight: 800;
  padding: 7px 10px;
}

.period-toggle button.active {
  background: var(--sb-primary);
  color: #fff;
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
