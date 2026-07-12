<template>
  <div class="superadmin-dashboard">
    <header class="dashboard-role-header" aria-label="Current admin dashboard">
      <div>
        <p class="eyebrow">Dashboard view</p>
        <h1>Superadmin</h1>
      </div>
      <span class="admin-role-pill">
        <i class="bi bi-shield-lock-fill" aria-hidden="true"></i>
        Superadmin
      </span>
    </header>

    <div v-if="store.error.stats || store.error.pendingActions" class="alert alert-danger border-0 rounded-4 mb-4">
      <div class="d-flex align-items-center gap-3">
        <i class="bi bi-exclamation-triangle-fill fs-4"></i>
        <div>
          <p class="fw-bold mb-0">Some SuperAdmin data did not load</p>
          <p class="small mb-0">{{ store.error.stats || store.error.pendingActions }}</p>
        </div>
        <button type="button" class="btn btn-sm btn-danger rounded-pill ms-auto" @click="refreshDashboard">
          Retry
        </button>
      </div>
    </div>

    <section class="kpi-grid" aria-label="SuperAdmin overview">
      <article v-for="card in kpiCards" :key="card.label" class="kpi-card sb-card-lift">
        <div class="kpi-icon" :class="card.tone">
          <i class="bi" :class="card.icon"></i>
        </div>
        <p>{{ card.label }}</p>
        <h2>{{ card.value }}</h2>
        <span>{{ card.delta }}</span>
      </article>
    </section>

    <section class="dashboard-split">
      <article class="surface-panel">
        <div class="panel-heading">
          <div>
            <p class="eyebrow">Enrollment</p>
            <h3>New learners and tutors</h3>
          </div>
          <span class="soft-pill">14 days</span>
        </div>

        <div class="sparkline-wrap">
          <svg viewBox="0 0 580 160" role="img" aria-label="Enrollment trend">
            <defs>
              <linearGradient id="enrollmentFill" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stop-color="var(--sb-primary)" stop-opacity="0.2" />
                <stop offset="100%" stop-color="var(--sb-primary)" stop-opacity="0" />
              </linearGradient>
            </defs>
            <path :d="sparklineAreaPath" fill="url(#enrollmentFill)" />
            <polyline :points="sparklinePoints" fill="none" stroke="var(--sb-primary)" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </div>

        <div class="trend-legend">
          <span><i class="bi bi-circle-fill"></i>{{ trendTotal }} new profiles</span>
          <span>{{ trendRangeLabel }}</span>
        </div>
      </article>

      <article class="surface-panel pending-panel">
        <div class="panel-heading">
          <div>
            <p class="eyebrow">Pending actions</p>
            <h3>Needs SuperAdmin review</h3>
          </div>
          <span class="soft-pill">{{ store.pendingActions.count }}</span>
        </div>

        <Transition name="fade" mode="out-in">
          <div v-if="store.loading.pendingActions" class="pending-list placeholder-glow">
            <div v-for="i in 4" :key="i" class="pending-item">
              <span class="placeholder rounded-circle pending-icon"></span>
              <div class="flex-grow-1">
                <p class="placeholder col-8 rounded mb-2"></p>
                <p class="placeholder col-6 rounded mb-0"></p>
              </div>
            </div>
          </div>
          <div v-else-if="store.pendingActions.items.length" class="pending-list">
            <div v-for="item in store.pendingActions.items" :key="`${item.type}-${item.id}`" class="pending-item">
              <div class="pending-icon" :class="getPendingMeta(item.type).tone">
                <i class="bi" :class="getPendingMeta(item.type).icon"></i>
              </div>
              <div class="pending-copy">
                <p>{{ item.title }}</p>
                <span>{{ item.meta }}</span>
              </div>
              <button type="button" class="action-button" :disabled="actingKey === `${item.type}-${item.id}`" @click="handlePendingAction(item)">
                {{ getPendingMeta(item.type).action }}
              </button>
            </div>
          </div>
          <div v-else class="empty-state">
            <i class="bi bi-check2-circle"></i>
            <p>No SuperAdmin-only actions waiting right now.</p>
          </div>
        </Transition>
      </article>
    </section>

    <section class="surface-panel table-panel">
      <div class="panel-heading">
        <div>
          <p class="eyebrow">Institutions</p>
          <h3>Performance overview</h3>
        </div>
        <router-link to="/superadmin/reports" class="link-button">
          Reports <i class="bi bi-arrow-right"></i>
        </router-link>
      </div>

      <div class="table-responsive">
        <table class="table align-middle mb-0">
          <thead>
            <tr>
              <th>Institution</th>
              <th class="text-center">Tutors</th>
              <th class="text-center">Tutees</th>
              <th class="text-center">Completed</th>
              <th class="text-center">Rating</th>
              <th class="text-end">Commission</th>
            </tr>
          </thead>
          <tbody>
            <template v-if="store.loading.institutionPerformance">
              <tr v-for="i in 4" :key="`perf-${i}`" class="placeholder-glow">
                <td><span class="placeholder col-8 rounded"></span></td>
                <td class="text-center"><span class="placeholder col-4 rounded"></span></td>
                <td class="text-center"><span class="placeholder col-4 rounded"></span></td>
                <td class="text-center"><span class="placeholder col-4 rounded"></span></td>
                <td class="text-center"><span class="placeholder col-4 rounded"></span></td>
                <td class="text-end"><span class="placeholder col-6 rounded"></span></td>
              </tr>
            </template>
            <template v-else-if="store.institutionPerformance.length">
              <tr v-for="inst in store.institutionPerformance" :key="inst.id">
                <td class="fw-bold">{{ inst.institution_name }}</td>
                <td class="text-center">{{ inst.tutors }}</td>
                <td class="text-center">{{ inst.tutees }}</td>
                <td class="text-center"><span class="metric-pill">{{ inst.sessions }}</span></td>
                <td class="text-center">
                  <span class="rating-text"><i class="bi bi-star-fill"></i>{{ formatNumber(inst.avg_rating, 1) }}</span>
                </td>
                <td class="text-end fw-bold">PHP {{ formatMoney(inst.revenue) }}</td>
              </tr>
            </template>
            <tr v-else>
              <td colspan="6" class="text-center py-5 text-muted">No institution data available.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useHaptics } from '@/composables/useHaptics'
import { useSuperAdminStore } from '@/stores/superadmin'
import { useToastStore } from '@/stores/toast'

const store = useSuperAdminStore()
const toastStore = useToastStore()
const { vibrate, patterns } = useHaptics()
const actingKey = ref('')

const kpiCards = computed(() => [
  {
    label: 'Total Users',
    value: formatCompact((store.stats?.total_tutors || 0) + (store.stats?.total_tutees || 0)),
    delta: `${store.stats?.total_tutors || 0} tutors / ${store.stats?.total_tutees || 0} tutees`,
    icon: 'bi-people-fill',
    tone: 'tone-primary',
  },
  {
    label: 'Sessions Today',
    value: formatCompact(store.stats?.active_sessions_today || 0),
    delta: 'Confirmed and currently active',
    icon: 'bi-calendar-check',
    tone: 'tone-info',
  },
  {
    label: 'Revenue MTD',
    value: `PHP ${formatCompact(store.stats?.commissions_this_month || 0)}`,
    delta: 'Platform commissions',
    icon: 'bi-wallet2',
    tone: 'tone-warning',
  },
  {
    label: 'Pending Actions',
    value: formatCompact(store.pendingActions.count || 0),
    delta: 'SuperAdmin-only queue',
    icon: 'bi-inbox-fill',
    tone: 'tone-danger',
  },
])

const trendData = computed(() =>
  (store.stats?.enrollment_trend || []).map((item) => ({
    ...item,
    total: (item.new_tutors || 0) + (item.new_tutees || 0),
  }))
)

const sparklinePoints = computed(() => {
  if (!trendData.value.length) return '0,140 580,140'
  const max = Math.max(...trendData.value.map((item) => item.total), 1)
  const width = 580
  const height = 130
  const step = trendData.value.length > 1 ? width / (trendData.value.length - 1) : width

  return trendData.value
    .map((item, index) => {
      const x = index * step
      const y = 145 - (item.total / max) * height
      return `${x.toFixed(1)},${y.toFixed(1)}`
    })
    .join(' ')
})

const sparklineAreaPath = computed(() => {
  const points = sparklinePoints.value.split(' ')
  return `M ${points[0]} L ${points.join(' L ')} L 580,150 L 0,150 Z`
})

const trendTotal = computed(() => trendData.value.reduce((sum, item) => sum + item.total, 0))
const trendRangeLabel = computed(() => {
  const first = trendData.value[0]?.date
  const last = trendData.value.at(-1)?.date
  if (!first || !last) return 'No trend data'
  return `${formatShortDate(first)} - ${formatShortDate(last)}`
})

onMounted(() => {
  refreshDashboard()
})

function refreshDashboard() {
  store.fetchStats(true)
  store.fetchInstitutionPerformance(true)
  store.fetchPendingActions(true)
}

async function handlePendingAction(item) {
  actingKey.value = `${item.type}-${item.id}`
  vibrate(patterns.light)

  try {
    if (item.type === 'institution_request') {
      await store.approveInstitutionRequest(item.id)
      toastStore.push('Institution request approved.')
      vibrate(patterns.celebratory)
    } else if (item.type === 'institution_activation') {
      await store.toggleInstitutionActive(item.id, true)
      toastStore.push('Institution activated.')
      vibrate(patterns.celebratory)
    } else if (item.type === 'domain_exemption') {
      await store.toggleDomainExemption(item.id, true)
      toastStore.push('Domain exemption granted.')
      vibrate(patterns.medium)
    }
  } catch {
    toastStore.push('Unable to complete pending action.', 'error')
  } finally {
    actingKey.value = ''
  }
}

function getPendingMeta(type) {
  switch (type) {
    case 'institution_request':
      return { icon: 'bi-building-add', tone: 'pending-green', action: 'Approve' }
    case 'institution_activation':
      return { icon: 'bi-toggle-on', tone: 'pending-blue', action: 'Activate' }
    case 'domain_exemption':
      return { icon: 'bi-shield-check', tone: 'pending-amber', action: 'Grant' }
    default:
      return { icon: 'bi-dot', tone: 'pending-green', action: 'Review' }
  }
}

function formatMoney(value) {
  return Number(value || 0).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

function formatCompact(value) {
  return Number(value || 0).toLocaleString(undefined, { notation: 'compact', maximumFractionDigits: 1 })
}

function formatNumber(value, digits = 0) {
  return Number(value || 0).toFixed(digits)
}

function formatShortDate(value) {
  return new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from,
.fade-leave-to { opacity: 0; }

.superadmin-dashboard {
  min-height: 100%;
  color: var(--sb-text-main);
  padding: 24px;
}

.dashboard-role-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
  padding: 18px 20px;
  border: 1px solid var(--sb-card-border);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 12px 32px rgba(10, 25, 22, 0.06);
}

.dashboard-role-header h1 {
  margin: 4px 0 0;
  font-size: 30px;
  line-height: 1.1;
  font-weight: 800;
}

.admin-role-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border-radius: 999px;
  background: var(--sb-primary);
  color: #fff;
  font-size: 13px;
  font-weight: 800;
  padding: 8px 14px;
  white-space: nowrap;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 18px;
}

.kpi-card,
.surface-panel {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid var(--sb-card-border);
  border-radius: 18px;
  box-shadow: 0 12px 32px rgba(10, 25, 22, 0.06);
}

.kpi-card {
  padding: 18px;
  min-height: 160px;
}

.kpi-icon {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  margin-bottom: 18px;
}

.tone-primary { background: #edf6f1; color: var(--sb-primary); }
.tone-info { background: #eff6ff; color: #1d4ed8; }
.tone-warning { background: #fffbeb; color: #92400e; }
.tone-danger { background: #fef2f2; color: #991b1b; }

.kpi-card p,
.eyebrow {
  color: var(--sb-text-muted);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  margin: 0;
}

.kpi-card h2 {
  font-size: 30px;
  line-height: 1.1;
  margin: 0 0 8px;
  font-weight: 800;
}

.kpi-card span,
.trend-legend,
.pending-copy span {
  color: var(--sb-text-muted);
  font-size: 13px;
}

.dashboard-split {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(340px, 0.75fr);
  gap: 18px;
  margin-bottom: 18px;
}

.surface-panel {
  padding: 20px;
}

.panel-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.panel-heading h3 {
  font-size: 21px;
  line-height: 1.2;
  margin: 4px 0 0;
  font-weight: 800;
}

.soft-pill,
.metric-pill {
  border-radius: 999px;
  background: #edf6f1;
  color: var(--sb-primary);
  font-size: 12px;
  font-weight: 800;
  padding: 5px 11px;
  white-space: nowrap;
}

.sparkline-wrap {
  height: 220px;
  border-radius: 16px;
  background: linear-gradient(180deg, rgba(0, 137, 90, 0.06), rgba(255, 255, 255, 0));
  display: flex;
  align-items: center;
}

.sparkline-wrap svg {
  width: 100%;
  height: 180px;
}

.trend-legend {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 12px;
}

.trend-legend i {
  color: var(--sb-primary);
  font-size: 9px;
  margin-right: 6px;
}

.pending-list {
  display: grid;
  gap: 12px;
}

.pending-item {
  display: grid;
  grid-template-columns: 40px minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid var(--sb-card-border);
  border-radius: 14px;
  background: #fff;
}

.pending-icon {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pending-green { background: #edf6f1; color: var(--sb-primary); }
.pending-blue { background: #eff6ff; color: #1d4ed8; }
.pending-purple { background: #f5f3ff; color: #5b21b6; }
.pending-amber { background: #fffbeb; color: #92400e; }

.pending-copy {
  min-width: 0;
}

.pending-copy p {
  margin: 0 0 2px;
  font-weight: 800;
  overflow-wrap: anywhere;
}

.action-button,
.link-button {
  border: 0;
  border-radius: 999px;
  background: var(--sb-primary);
  color: #fff;
  font-size: 13px;
  font-weight: 800;
  padding: 8px 14px;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.action-button:disabled {
  opacity: 0.65;
}

.empty-state {
  text-align: center;
  color: var(--sb-text-muted);
  padding: 36px 20px;
}

.empty-state i {
  display: block;
  font-size: 34px;
  color: var(--sb-primary);
  margin-bottom: 8px;
}

.table-panel {
  padding: 0;
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

.rating-text {
  color: #92400e;
  font-weight: 800;
}

.rating-text i {
  margin-right: 5px;
}

@media (max-width: 1100px) {
  .kpi-grid,
  .dashboard-split {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .superadmin-dashboard {
    padding: 16px;
  }

  .dashboard-role-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .kpi-grid,
  .dashboard-split {
    grid-template-columns: 1fr;
  }

  .pending-item {
    grid-template-columns: 40px minmax(0, 1fr);
  }

  .action-button {
    grid-column: 1 / -1;
  }
}
</style>
