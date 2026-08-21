<template>
  <div class="admin-dashboard">
    <header class="dashboard-role-header" aria-label="Current admin dashboard">
      <div>
        <p class="eyebrow">Dashboard view</p>
        <h1>Admin</h1>
        <p v-if="institutionName" class="header-sub">
          <i class="bi bi-building"></i> {{ institutionName }}
        </p>
      </div>
      <span class="admin-role-pill">
        <i class="bi bi-building-lock" aria-hidden="true"></i>
        Institution Admin
      </span>
    </header>

    <div
      v-if="store.error.stats || store.error.operationalQueue"
      class="alert alert-danger border-0 rounded-4 mb-4"
    >
      <div class="d-flex align-items-center gap-3">
        <i class="bi bi-exclamation-triangle-fill fs-4"></i>
        <div>
          <p class="fw-bold mb-0">Some dashboard data did not load</p>
          <p class="small mb-0">{{ store.error.stats || store.error.operationalQueue }}</p>
        </div>
        <button type="button" class="btn btn-sm btn-danger rounded-pill ms-auto" @click="refreshDashboard">
          Retry
        </button>
      </div>
    </div>

    <!-- KPI grid -->
    <section class="kpi-grid" aria-label="Institution overview">
      <article v-for="card in kpiCards" :key="card.label" class="kpi-card sb-card-lift">
        <div class="kpi-icon" :class="card.tone">
          <i class="bi" :class="card.icon"></i>
        </div>
        <p class="kpi-label">{{ card.label }}</p>
        <Transition name="fade" mode="out-in">
          <div v-if="store.loading.stats" class="placeholder-glow">
            <h2 class="placeholder col-5 rounded mb-2"></h2>
            <p class="placeholder col-9 rounded mb-0"></p>
          </div>
          <div v-else>
            <h2>{{ card.value }}</h2>
            <span class="kpi-delta">{{ card.delta }}</span>
          </div>
        </Transition>
      </article>
    </section>

    <!-- enrollment + operational queue -->
    <section class="dashboard-split">
      <article class="surface-panel">
        <div class="panel-heading">
          <div>
            <p class="eyebrow">Enrollment</p>
            <h3>New members</h3>
          </div>
          <span class="soft-pill">14 days</span>
        </div>

        <div class="sparkline-wrap">
          <svg viewBox="0 0 580 160" role="img" aria-label="Enrollment trend" preserveAspectRatio="none">
            <defs>
              <linearGradient id="adminEnrollmentFill" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stop-color="var(--sb-primary)" stop-opacity="0.2" />
                <stop offset="100%" stop-color="var(--sb-primary)" stop-opacity="0" />
              </linearGradient>
            </defs>
            <path :d="sparklineAreaPath" fill="url(#adminEnrollmentFill)" />
            <polyline
              :points="sparklinePoints"
              fill="none"
              stroke="var(--sb-primary)"
              stroke-width="4"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </div>

        <div class="trend-legend">
          <span><i class="bi bi-circle-fill"></i>{{ trendTotal }} new profiles</span>
          <span>{{ trendRangeLabel }}</span>
        </div>
      </article>

      <article class="surface-panel">
        <div class="panel-heading">
          <div>
            <p class="eyebrow">Operational queue</p>
            <h3>Needs your action</h3>
          </div>
          <span class="soft-pill">{{ store.operationalQueue.count }}</span>
        </div>

        <Transition name="fade" mode="out-in">
          <div v-if="store.loading.operationalQueue" class="pending-list placeholder-glow">
            <div v-for="i in 3" :key="i" class="pending-item">
              <span class="placeholder rounded pending-icon"></span>
              <div class="flex-grow-1">
                <p class="placeholder col-8 rounded mb-2"></p>
                <p class="placeholder col-6 rounded mb-0"></p>
              </div>
            </div>
          </div>
          <div v-else-if="store.operationalQueue.items.length" class="pending-list">
            <div v-for="item in store.operationalQueue.items" :key="item.type" class="pending-item">
              <div class="pending-icon" :class="getQueueMeta(item.type).tone">
                <i class="bi" :class="getQueueMeta(item.type).icon"></i>
              </div>
              <div class="pending-copy">
                <p>{{ item.title }}</p>
                <span>{{ item.meta }}</span>
              </div>
              <button type="button" class="action-button" @click="handleQueueRoute(item)">
                {{ getQueueMeta(item.type).action }}
              </button>
            </div>
          </div>
          <div v-else class="empty-state">
            <i class="bi bi-check2-circle"></i>
            <p>You're all caught up. Nothing needs attention right now.</p>
          </div>
        </Transition>
      </article>
    </section>

    <!-- subject demand + top tutors -->
    <section class="two-up">
      <article class="surface-panel">
        <div class="panel-heading">
          <div>
            <p class="eyebrow">Demand</p>
            <h3>Most requested subjects</h3>
          </div>
          <span class="soft-pill"><i class="bi bi-exclamation-triangle-fill"></i> = supply gap</span>
        </div>

        <Transition name="fade" mode="out-in">
          <div v-if="store.loading.stats" class="placeholder-glow">
            <p v-for="i in 5" :key="i" class="placeholder col-12 rounded mb-3" style="height: 16px;"></p>
          </div>
          <div v-else-if="subjectDemand.length">
            <div v-for="(row, index) in subjectDemand" :key="row.subject_name" class="demand-row">
              <span class="demand-label" :title="row.subject_name">{{ row.subject_name }}</span>
              <div class="demand-track">
                <div
                  class="demand-fill"
                  :style="{ transform: `scaleX(${demandWidth(row) / 100})`, background: demandColor(index) }"
                ></div>
              </div>
              <span class="demand-count">
                {{ row.demand }}
                <i v-if="row.gap" class="bi bi-exclamation-triangle-fill demand-gap" title="No tutors teach this yet"></i>
              </span>
            </div>
          </div>
          <div v-else class="empty-state">
            <i class="bi bi-clipboard-data"></i>
            <p>Not enough preference data yet to gauge demand.</p>
          </div>
        </Transition>
      </article>

      <article class="surface-panel">
        <div class="panel-heading">
          <div>
            <p class="eyebrow">Community</p>
            <h3>Top tutors</h3>
          </div>
          <router-link to="/admin/users" class="link-button">
            All users <i class="bi bi-arrow-right"></i>
          </router-link>
        </div>

        <Transition name="fade" mode="out-in">
          <div v-if="store.loading.stats" class="placeholder-glow">
            <div v-for="i in 4" :key="i" class="lead-row">
              <span class="placeholder rounded-circle" style="width: 36px; height: 36px;"></span>
              <p class="placeholder col-8 rounded mb-0"></p>
            </div>
          </div>
          <div v-else-if="topTutors.length">
            <div v-for="(tutor, index) in topTutors" :key="tutor.name + index" class="lead-row">
              <span class="lead-rank">{{ index + 1 }}</span>
              <span class="lead-avatar">{{ initials(tutor.name) }}</span>
              <div class="lead-info">
                <div class="lead-name">{{ tutor.name || 'Unnamed tutor' }}</div>
                <div class="lead-meta">
                  {{ tutor.completed_sessions }} session{{ tutor.completed_sessions === 1 ? '' : 's' }}
                  <span v-if="tutor.course"> · {{ tutor.course }}</span>
                </div>
              </div>
              <span class="rating-text"><i class="bi bi-star-fill"></i>{{ tutor.avg_rating.toFixed(1) }}</span>
            </div>
          </div>
          <div v-else class="empty-state">
            <i class="bi bi-people"></i>
            <p>No tutor activity to rank yet.</p>
          </div>
        </Transition>
      </article>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import { useHaptics } from '@/composables/useHaptics'
import { formatCount } from '@/utils/currency'

const store = useAdminStore()
const router = useRouter()
const { vibrate, patterns } = useHaptics()

const demandPalette = ['var(--sb-primary)', '#1d4ed8', '#92400e', '#5b21b6', '#9d174f']

const institutionName = computed(() => {
  const name = store.stats?.institution_name
  return name && name !== 'All institutions' ? name : ''
})

const kpiCards = computed(() => {
  const s = store.stats || {}
  const totalMembers = (s.total_tutors || 0) + (s.total_tutees || 0)
  const newThisMonth = s.new_members_this_month || 0

  const thisWeek = s.sessions_this_week || 0
  const lastWeek = s.sessions_last_week || 0
  let sessionDelta = 'No sessions last week'
  if (lastWeek > 0) {
    const change = Math.round(((thisWeek - lastWeek) / lastWeek) * 100)
    sessionDelta = `${change >= 0 ? '+' : ''}${change}% vs last week`
  } else if (thisWeek > 0) {
    sessionDelta = 'New this week'
  }

  return [
    {
      label: 'Active Members',
      value: formatCount(totalMembers),
      delta: `${s.total_tutors || 0} tutors / ${s.total_tutees || 0} tutees · +${newThisMonth} this month`,
      icon: 'bi-people-fill',
      tone: 'tone-primary',
    },
    {
      label: 'Sessions This Week',
      value: formatCount(thisWeek),
      delta: sessionDelta,
      icon: 'bi-calendar-check',
      tone: 'tone-info',
    },
    {
      label: 'Completion Rate',
      value: `${(s.completion_rate || 0).toFixed(1)}%`,
      delta: `${s.completed_sessions || 0} done / ${s.cancelled_sessions || 0} cancelled (30d)`,
      icon: 'bi-patch-check-fill',
      tone: 'tone-warning',
    },
    {
      label: 'Needs Attention',
      value: formatCount(store.operationalQueue.count || 0),
      delta: store.operationalQueue.count ? 'Items in your queue' : 'All clear',
      icon: 'bi-inbox-fill',
      tone: 'tone-danger',
    },
  ]
})

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

const subjectDemand = computed(() => store.stats?.subject_demand || [])
const maxDemand = computed(() => Math.max(...subjectDemand.value.map((row) => row.demand), 1))
const topTutors = computed(() => store.stats?.top_tutors || [])

function demandWidth(row) {
  return Math.max((row.demand / maxDemand.value) * 100, 6)
}

function demandColor(index) {
  return demandPalette[index % demandPalette.length]
}

function getQueueMeta(type) {
  switch (type) {
    case 'withdrawal':
      return { icon: 'bi-cash-stack', tone: 'tone-primary', action: 'Review' }
    case 'support':
      return { icon: 'bi-headset', tone: 'tone-info', action: 'Open desk' }
    case 'tutor_application':
      return { icon: 'bi-person-plus', tone: 'tone-warning', action: 'Vet' }
    default:
      return { icon: 'bi-dot', tone: 'tone-primary', action: 'Open' }
  }
}

function handleQueueRoute(item) {
  vibrate(patterns.light)
  router.push(item.route)
}

function initials(name) {
  const parts = String(name || '').trim().split(/\s+/).filter(Boolean)
  if (!parts.length) return 'SB'
  return parts.slice(0, 2).map((part) => part.charAt(0).toUpperCase()).join('')
}

function formatShortDate(value) {
  return new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function refreshDashboard() {
  store.fetchStats(true)
  store.fetchOperationalQueue(true)
}

onMounted(() => {
  refreshDashboard()
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from,
.fade-leave-to { opacity: 0; }

.admin-dashboard {
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

.eyebrow {
  color: var(--sb-text-muted);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  margin: 0;
}

.dashboard-role-header h1 {
  margin: 4px 0 0;
  font-size: 30px;
  line-height: 1.1;
  font-weight: 800;
}

.header-sub {
  margin: 6px 0 0;
  color: var(--sb-text-muted);
  font-size: 13px;
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

.kpi-label {
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

.kpi-delta {
  color: var(--sb-text-muted);
  font-size: 13px;
}

.dashboard-split {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(340px, 0.75fr);
  gap: 18px;
  margin-bottom: 18px;
}

.two-up {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
  margin-bottom: 18px;
}

.surface-panel { padding: 20px; }

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

.soft-pill {
  border-radius: 999px;
  background: #edf6f1;
  color: var(--sb-primary);
  font-size: 12px;
  font-weight: 800;
  padding: 5px 11px;
  white-space: nowrap;
}

.link-button {
  color: var(--sb-primary);
  font-weight: 700;
  font-size: 13px;
  text-decoration: none;
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
  color: var(--sb-text-muted);
  font-size: 13px;
}

.trend-legend i {
  color: var(--sb-primary);
  font-size: 9px;
  margin-right: 6px;
}

.pending-list { display: grid; gap: 12px; }

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

.pending-copy { min-width: 0; }
.pending-copy p { margin: 0; font-weight: 700; font-size: 14px; }
.pending-copy span { color: var(--sb-text-muted); font-size: 12px; }

.action-button {
  border: 1px solid var(--sb-primary);
  color: var(--sb-primary);
  background: #fff;
  font-weight: 700;
  font-size: 12px;
  padding: 6px 12px;
  border-radius: 999px;
  cursor: pointer;
  white-space: nowrap;
  transition: none;
}

.action-button:hover { background: var(--sb-primary); color: #fff; }

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 32px 12px;
  color: var(--sb-text-muted);
  text-align: center;
}

.empty-state i { font-size: 28px; color: var(--sb-primary); }
.empty-state p { margin: 0; font-size: 14px; }

.demand-row {
  display: grid;
  grid-template-columns: 130px 1fr 48px;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.demand-label {
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.demand-track {
  height: 12px;
  border-radius: 999px;
  background: #eef2f0;
  overflow: hidden;
}

.demand-fill {
  width: 100%;
  height: 100%;
  border-radius: 999px;
  transform-origin: left center;
  transition: transform var(--sb-t-normal) var(--sb-spring);
}

.demand-count {
  font-size: 13px;
  font-weight: 800;
  text-align: right;
}

.demand-gap { color: #b91c1c; font-size: 11px; margin-left: 2px; }

.lead-row {
  display: grid;
  grid-template-columns: 24px 36px 1fr auto;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid var(--sb-card-border);
}

.lead-row:last-child { border-bottom: 0; }

.lead-rank { font-weight: 800; color: var(--sb-text-muted); text-align: center; }

.lead-avatar {
  width: 36px;
  height: 36px;
  border-radius: 999px;
  background: var(--sb-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 13px;
}

.lead-info { min-width: 0; }
.lead-name { font-weight: 700; font-size: 14px; }
.lead-meta { color: var(--sb-text-muted); font-size: 12px; }

.rating-text { color: #92400e; font-weight: 800; font-size: 13px; }
.rating-text i { margin-right: 4px; }

@media (max-width: 991px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .dashboard-split,
  .two-up { grid-template-columns: 1fr; }
}

@media (max-width: 600px) {
  .admin-dashboard { padding: 16px; }
  .kpi-grid { grid-template-columns: 1fr; }
  .dashboard-role-header { align-items: flex-start; flex-direction: column; }
}
</style>
