<template>
  <div class="reports-content">
    <section class="metric-grid" aria-label="Tutor session metrics">
      <article
        v-for="stat in statCards"
        :key="stat.label"
        class="metric-card"
      >
        <div class="metric-copy">
          <span class="metric-icon">
            <i :class="['bi', stat.icon]"></i>
          </span>
          <span class="metric-label">{{ stat.label }}</span>
          <strong class="metric-value">{{ stat.value }}</strong>
          <span class="metric-note">{{ stat.note }}</span>
        </div>

        <div class="metric-visual" :class="`metric-visual-${stat.visual}`" aria-hidden="true">
          <svg v-if="stat.visual === 'ring'" class="metric-ring" viewBox="0 0 72 72">
            <circle class="metric-ring-track" cx="36" cy="36" r="28"></circle>
            <circle
              class="metric-ring-fill"
              cx="36"
              cy="36"
              r="28"
              :style="{ '--metric-progress': stat.progress }"
            ></circle>
          </svg>

          <div v-else class="metric-bars">
            <span
              v-for="height in stat.bars"
              :key="height"
              :style="{ height: height + '%' }"
            ></span>
          </div>
        </div>
      </article>
    </section>

    <section class="reports-panel">
      <header class="reports-panel-header">
        <div>
          <p class="panel-kicker">Tutor Workspace</p>
          <h4 class="panel-title">
            <i class="bi bi-file-earmark-text"></i>
            Sessions & Reports
          </h4>
        </div>

        <div class="view-tabs" role="tablist" aria-label="Sessions and reports">
          <button
            v-for="tab in viewTabs"
            :key="tab.value"
            type="button"
            class="view-tab sb-btn"
            :class="{ 'view-tab-active': activeTab === tab.value }"
            :aria-selected="activeTab === tab.value"
            role="tab"
            @click="activeTab = tab.value"
          >
            <i :class="['bi', tab.icon]"></i>
            <span>{{ tab.label }}</span>
          </button>
        </div>
      </header>

      <div v-if="activeTab === 'sessions'" class="tab-panel" role="tabpanel">
        <div class="sessions-toolbar">
          <div class="filter-bar" aria-label="Session filters">
            <button
              v-for="filter in filters"
              :key="filter.value"
              type="button"
              @click="currentFilter = filter.value"
              class="filter-tab sb-btn"
              :class="{ 'filter-tab-active': currentFilter === filter.value }"
            >
              {{ filter.label }}
            </button>
          </div>
        </div>

        <div v-if="sessionStore.loading" class="state-panel">
          <div class="spinner-border text-sb-primary mb-3" role="status"></div>
          <p>Loading sessions...</p>
        </div>

        <div v-else-if="sessionStore.error" class="state-panel state-panel-error">
          <i class="bi bi-exclamation-triangle"></i>
          <p>{{ sessionStore.error }}</p>
        </div>

        <div v-else-if="filteredSessions.length" class="session-list">
          <article
            v-for="session in filteredSessions"
            :key="session.id"
            class="session-row"
          >
            <div class="session-main">
              <div class="session-subject-line">
                <span class="session-icon">
                  <i class="bi bi-journal-bookmark"></i>
                </span>
                <div>
                  <h5>{{ session.subject }}</h5>
                  <p>{{ session.tutee }}</p>
                </div>
              </div>
            </div>

            <div class="session-meta-grid">
              <div class="session-meta-item">
                <span>Date</span>
                <strong>{{ session.date }}</strong>
              </div>
              <div class="session-meta-item">
                <span>Time</span>
                <strong>{{ session.startTime }} - {{ session.endTime }}</strong>
              </div>
              <div class="session-meta-item">
                <span>Rating</span>
                <strong v-if="session.rating" class="rating-value">
                  <i class="bi bi-star-fill"></i>{{ session.rating }}
                </strong>
                <strong v-else>-</strong>
              </div>
              <div class="session-meta-item">
                <span>Earnings</span>
                <strong>{{ session.earnings ? `PHP ${session.earnings}` : '-' }}</strong>
              </div>
            </div>

            <div class="session-actions">
              <span class="badge rounded-pill px-3 py-2 fw-normal" :class="getStatusClass(session.status)">
                {{ formatStatus(session.status) }}
              </span>
              <button
                class="details-btn sb-btn"
                type="button"
                @click="goToDetails(session.id)"
              >
                <span>Details</span>
                <i class="bi bi-arrow-right"></i>
              </button>
            </div>
          </article>
        </div>

        <div v-else class="state-panel">
          <i class="bi bi-calendar2-week"></i>
          <p>No sessions found for this category.</p>
        </div>
      </div>

      <div v-else class="tab-panel" role="tabpanel">
        <div v-if="sessionStore.loading" class="state-panel">
          <div class="spinner-border text-sb-primary mb-3" role="status"></div>
          <p>Loading reports...</p>
        </div>

        <div v-else-if="sessionStore.error" class="state-panel state-panel-error">
          <i class="bi bi-exclamation-triangle"></i>
          <p>{{ sessionStore.error }}</p>
        </div>

        <div v-else-if="totalSessions" class="reports-grid">
          <article class="analytics-summary">
            <div class="summary-header">
              <span class="summary-icon">
                <i class="bi bi-activity"></i>
              </span>
              <div>
                <p class="panel-kicker">Performance</p>
                <h5>Session Mix</h5>
              </div>
            </div>

            <div class="status-bars">
              <div
                v-for="item in statusBreakdown"
                :key="item.label"
                class="status-bar-row"
              >
                <div class="status-bar-label">
                  <span>{{ item.label }}</span>
                  <strong>{{ item.count }}</strong>
                </div>
                <div class="status-track">
                  <span class="status-fill" :style="{ width: item.percent + '%' }"></span>
                </div>
              </div>
            </div>
          </article>

          <article class="analytics-summary">
            <div class="summary-header">
              <span class="summary-icon">
                <i class="bi bi-clipboard2-data"></i>
              </span>
              <div>
                <p class="panel-kicker">Snapshot</p>
                <h5>Tutor Summary</h5>
              </div>
            </div>

            <div class="summary-list">
              <div
                v-for="summary in reportSummaries"
                :key="summary.label"
                class="summary-row"
              >
                <span>{{ summary.label }}</span>
                <strong>{{ summary.value }}</strong>
              </div>
            </div>
          </article>
        </div>

        <div v-else class="state-panel">
          <i class="bi bi-bar-chart"></i>
          <p>No report data available yet.</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionsStore } from '@/stores/completedSessions'

const router = useRouter()
const sessionStore = useSessionsStore()
const currentFilter = ref('all')
const activeTab = ref('sessions')

const viewTabs = [
  { label: 'Sessions', value: 'sessions', icon: 'bi-calendar2-week' },
  { label: 'Reports', value: 'reports', icon: 'bi-bar-chart' },
]

const filters = computed(() => [
  {
    label: `All (${sessionStore.sessions.length})`,
    value: 'all',
  },
  {
    label: `Completed (${sessionStore.completedSessions.length})`,
    value: 'completed',
  },
  {
    label: `Upcoming (${sessionStore.upcomingSessions.length})`,
    value: 'upcoming',
  },
  {
    label: `Rejected (${sessionStore.rejectedSessions.length})`,
    value: 'rejected',
  },
])

onMounted(() => {
  sessionStore.fetchSessions()
})

const goToDetails = (sessionId) => {
  router.push(`/booking-details/${sessionId}`)
}

const totalSessions = computed(() => sessionStore.sessions.length)

const totalEarnings = computed(() =>
  sessionStore.completedSessions.reduce((sum, session) => sum + Number(session.earnings || 0), 0)
)

const averageRating = computed(() => {
  const ratedSessions = sessionStore.completedSessions.filter((session) => session.rating)

  if (!ratedSessions.length) {
    return 0
  }

  return (
    ratedSessions.reduce((sum, session) => sum + Number(session.rating), 0) /
    ratedSessions.length
  ).toFixed(1)
})

const totalHours = computed(() =>
  sessionStore.completedSessions.reduce((sum, session) => {
    if (session.duration_hours) {
      return sum + Number(session.duration_hours || 0)
    }

    const start = new Date(`1970-01-01T${session.startTime}`)
    const end = new Date(`1970-01-01T${session.endTime}`)
    const hours = (end - start) / (1000 * 60 * 60)

    if (!Number.isFinite(hours) || hours < 0) {
      return sum
    }

    return sum + hours
  }, 0)
)

const statCards = computed(() => [
  {
    label: 'Total Sessions',
    value: totalSessions.value,
    note: `${sessionStore.completedSessions.length} completed`,
    icon: 'bi-calendar-event',
    visual: 'ring',
    progress: getPercent(sessionStore.completedSessions.length),
  },
  {
    label: 'Total Earnings',
    value: `PHP ${totalEarnings.value.toLocaleString()}`,
    note: 'Completed sessions',
    icon: 'bi-wallet2',
    visual: 'bars',
    bars: [36, 56, 72, 92, 68, 44],
  },
  {
    label: 'Avg Rating',
    value: averageRating.value,
    note: 'Rated sessions',
    icon: 'bi-star',
    visual: 'ring',
    progress: Math.round((Number(averageRating.value) / 5) * 100),
  },
  {
    label: 'Hours Tutored',
    value: `${totalHours.value.toFixed(1)}h`,
    note: 'Completed time',
    icon: 'bi-clock-history',
    visual: 'bars',
    bars: [42, 48, 62, 78, 88, 58],
  },
])

const getPercent = (count) => {
  if (!totalSessions.value) {
    return 0
  }

  return Math.round((count / totalSessions.value) * 100)
}

const statusBreakdown = computed(() => [
  {
    label: 'Completed',
    count: sessionStore.completedSessions.length,
    percent: getPercent(sessionStore.completedSessions.length),
  },
  {
    label: 'Upcoming',
    count: sessionStore.upcomingSessions.length,
    percent: getPercent(sessionStore.upcomingSessions.length),
  },
  {
    label: 'Rejected',
    count: sessionStore.rejectedSessions.length,
    percent: getPercent(sessionStore.rejectedSessions.length),
  },
])

const reportSummaries = computed(() => [
  {
    label: 'Completion rate',
    value: `${getPercent(sessionStore.completedSessions.length)}%`,
  },
  {
    label: 'Average per hour',
    value: totalHours.value ? `PHP ${(totalEarnings.value / totalHours.value).toFixed(0)}` : 'PHP 0',
  },
  {
    label: 'Average per completed session',
    value: sessionStore.completedSessions.length
      ? `PHP ${(totalEarnings.value / sessionStore.completedSessions.length).toFixed(0)}`
      : 'PHP 0',
  },
  {
    label: 'Filtered sessions',
    value: filteredSessions.value.length,
  },
])

const filteredSessions = computed(() => {
  switch (currentFilter.value) {
    case 'completed':
      return sessionStore.completedSessions
    case 'upcoming':
      return sessionStore.upcomingSessions
    case 'rejected':
      return sessionStore.rejectedSessions
    default:
      return sessionStore.sessions
  }
})

const formatStatus = (status) => status

const getStatusClass = (status) => {
  switch (String(status || '').toLowerCase()) {
    case 'upcoming':
      return 'status-badge status-badge-upcoming'
    case 'ongoing':
      return 'status-badge status-badge-ongoing'
    case 'payment required':
    case 'awaiting verification':
      return 'status-badge status-badge-warning'
    case 'completed':
      return 'status-badge status-badge-completed'
    case 'rejected':
    case 'cancelled':
      return 'status-badge status-badge-danger'
    case 'pending':
      return 'status-badge status-badge-pending'
    default:
      return 'status-badge status-badge-pending'
  }
}
</script>

<style scoped>
.reports-content {
  --reports-glass: color-mix(in srgb, var(--sb-card-bg) 85%, transparent);
  --reports-glass-strong: color-mix(in srgb, var(--sb-card-bg) 92%, transparent);
  --reports-border: color-mix(in srgb, var(--sb-card-border) 82%, transparent);
  --reports-muted: var(--sb-text-muted);
  --reports-ink: var(--sb-text-main);
  color: var(--reports-ink);
  display: grid;
  gap: 1rem;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

.metric-card,
.session-row,
.analytics-summary {
  border: 1px solid var(--reports-border);
  background: var(--reports-glass-strong);
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.04);
}

.reports-panel {
  border: 1px solid var(--reports-border);
  background: var(--reports-glass);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.08);
}

.metric-card {
  min-height: 142px;
  border-radius: 24px;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  gap: 0.85rem;
  overflow: hidden;
  position: relative;
}

.metric-card::after {
  content: '';
  position: absolute;
  inset: auto -22px -36px auto;
  width: 96px;
  height: 96px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--sb-primary) 14%, transparent);
  pointer-events: none;
}

.metric-copy {
  display: grid;
  align-content: space-between;
  gap: 0.4rem;
  min-width: 0;
  position: relative;
  z-index: 1;
}

.metric-icon,
.session-icon,
.summary-icon {
  width: 36px;
  height: 36px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--sb-primary) 12%, transparent);
  border: 1px solid color-mix(in srgb, var(--sb-primary) 22%, transparent);
  color: var(--sb-primary);
}

.metric-label,
.metric-note,
.panel-kicker,
.session-meta-item span,
.summary-row span,
.status-bar-label span {
  color: var(--reports-muted);
}

.metric-label,
.panel-kicker,
.session-meta-item span {
  font-size: 0.74rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0;
}

.metric-value {
  font-size: clamp(1.55rem, 2vw, 2.15rem);
  line-height: 1;
  letter-spacing: 0;
  position: relative;
  z-index: 1;
  overflow-wrap: anywhere;
}

.metric-note {
  font-size: 0.82rem;
  position: relative;
  z-index: 1;
}

.metric-visual {
  width: 70px;
  min-width: 70px;
  align-self: center;
  display: flex;
  justify-content: center;
  position: relative;
  z-index: 1;
}

.metric-ring {
  width: 68px;
  height: 68px;
  transform: rotate(-90deg);
  filter: drop-shadow(0 0 8px color-mix(in srgb, var(--sb-primary) 24%, transparent));
}

.metric-ring-track,
.metric-ring-fill {
  fill: none;
  stroke-width: 7;
}

.metric-ring-track {
  stroke: color-mix(in srgb, var(--sb-primary) 12%, transparent);
}

.metric-ring-fill {
  --metric-circumference: 175.93;
  stroke: color-mix(in srgb, var(--sb-primary) 84%, white);
  stroke-linecap: round;
  stroke-dasharray: var(--metric-circumference);
  stroke-dashoffset: calc(var(--metric-circumference) - (var(--metric-circumference) * var(--metric-progress) / 100));
}

.metric-bars {
  width: 68px;
  height: 54px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 0.28rem;
}

.metric-bars span {
  width: 0.44rem;
  min-height: 20%;
  border-radius: 999px;
  background: linear-gradient(
    to top,
    color-mix(in srgb, var(--sb-primary) 20%, transparent),
    color-mix(in srgb, var(--sb-primary) 82%, white)
  );
  box-shadow: 0 0 10px color-mix(in srgb, var(--sb-primary) 16%, transparent);
}

.reports-panel {
  border-radius: 28px;
  padding: 1.25rem;
}

.reports-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 0.35rem 0.35rem 1.2rem;
}

.panel-kicker {
  margin: 0 0 0.35rem;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin: 0;
  font-weight: 800;
  letter-spacing: 0;
}

.panel-title i {
  color: var(--sb-primary);
}

.view-tabs,
.filter-bar {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  border: 1px solid var(--reports-border);
  background: color-mix(in srgb, var(--sb-bg) 62%, transparent);
  border-radius: 999px;
  padding: 0.35rem;
}

.view-tab,
.filter-tab,
.details-btn {
  border: 0;
  transition:
    transform var(--sb-t-quick, 120ms) var(--sb-spring-fast, ease),
    background-color var(--sb-t-normal, 250ms) var(--sb-spring, ease),
    color var(--sb-t-normal, 250ms) var(--sb-spring, ease),
    box-shadow var(--sb-t-normal, 250ms) var(--sb-spring, ease);
}

.view-tab,
.filter-tab {
  border-radius: 999px;
  color: var(--reports-muted);
  background: transparent;
  font-weight: 700;
  white-space: nowrap;
}

.view-tab {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.52rem 0.85rem;
}

.filter-tab {
  padding: 0.48rem 0.9rem;
  font-size: 0.88rem;
}

.view-tab-active,
.filter-tab-active {
  color: var(--reports-ink);
  background: var(--reports-glass-strong);
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.08);
}

.view-tab:active,
.filter-tab:active,
.details-btn:active {
  transform: scale(0.97);
}

.tab-panel {
  border-top: 1px solid var(--reports-border);
  padding-top: 1rem;
}

.sessions-toolbar {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 1rem;
  overflow-x: auto;
  padding-bottom: 0.15rem;
}

.session-list {
  display: grid;
  gap: 0.75rem;
}

.session-row {
  border-radius: 20px;
  padding: 1rem;
  display: grid;
  grid-template-columns: minmax(180px, 1.15fr) minmax(320px, 1.8fr) auto;
  align-items: center;
  gap: 1rem;
}

.session-subject-line {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  min-width: 0;
}

.session-subject-line h5,
.analytics-summary h5 {
  margin: 0;
  font-size: 1rem;
  font-weight: 800;
  letter-spacing: 0;
}

.session-subject-line p {
  margin: 0.2rem 0 0;
  color: var(--reports-muted);
  font-size: 0.9rem;
}

.session-meta-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.75rem;
}

.session-meta-item {
  min-width: 0;
}

.session-meta-item strong {
  display: block;
  margin-top: 0.2rem;
  font-size: 0.92rem;
  color: var(--reports-ink);
  overflow-wrap: anywhere;
}

.rating-value {
  color: #c49102 !important;
}

.rating-value i {
  margin-right: 0.25rem;
}

.session-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.65rem;
}

.status-badge {
  border: 1px solid transparent;
  font-weight: 800 !important;
}

.status-badge-completed,
.status-badge-upcoming,
.status-badge-ongoing {
  color: var(--sb-primary) !important;
  background: color-mix(in srgb, var(--sb-primary) 13%, transparent) !important;
  border-color: color-mix(in srgb, var(--sb-primary) 24%, transparent) !important;
}

.status-badge-warning {
  color: #9a6500 !important;
  background: rgba(255, 193, 7, 0.14) !important;
  border-color: rgba(255, 193, 7, 0.28) !important;
}

.status-badge-danger {
  color: var(--bs-danger, #dc3545) !important;
  background: rgba(220, 53, 69, 0.12) !important;
  border-color: rgba(220, 53, 69, 0.26) !important;
}

.status-badge-pending {
  color: var(--reports-muted) !important;
  background: color-mix(in srgb, var(--sb-card-border) 42%, transparent) !important;
  border-color: var(--reports-border) !important;
}

.details-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  border-radius: 999px;
  padding: 0.55rem 0.85rem;
  background: var(--sb-primary);
  color: var(--sb-primary-contrast, #fff);
  font-weight: 800;
  white-space: nowrap;
}

.details-btn:hover {
  background: var(--sb-primary-hover);
  color: var(--sb-primary-contrast, #fff);
}

.state-panel {
  min-height: 260px;
  border: 1px dashed var(--reports-border);
  border-radius: 22px;
  background: color-mix(in srgb, var(--sb-card-bg) 54%, transparent);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: var(--reports-muted);
  text-align: center;
}

.state-panel i {
  color: var(--sb-primary);
  font-size: 1.75rem;
  margin-bottom: 0.8rem;
}

.state-panel p {
  margin: 0;
  font-weight: 700;
}

.state-panel-error {
  color: var(--sb-danger-bs, #dc3545);
}

.state-panel-error i {
  color: var(--sb-danger-bs, #dc3545);
}

.reports-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.8fr);
  gap: 1rem;
}

.analytics-summary {
  border-radius: 22px;
  padding: 1rem;
}

.summary-header {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  margin-bottom: 1rem;
}

.status-bars,
.summary-list {
  display: grid;
  gap: 0.85rem;
}

.status-bar-label,
.summary-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.status-track {
  height: 0.55rem;
  border-radius: 999px;
  overflow: hidden;
  background: color-mix(in srgb, var(--sb-card-border) 70%, transparent);
}

.status-fill {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--sb-primary), color-mix(in srgb, var(--sb-primary) 64%, white));
}

.summary-row {
  border-bottom: 1px solid var(--reports-border);
  padding-bottom: 0.75rem;
}

.summary-row:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.summary-row strong {
  color: var(--reports-ink);
  text-align: right;
}

@media (max-width: 1199.98px) {
  .metric-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .session-row {
    grid-template-columns: 1fr;
  }

  .session-actions {
    justify-content: space-between;
  }
}

@media (max-width: 767.98px) {
  .metric-grid,
  .reports-grid,
  .session-meta-grid {
    grid-template-columns: 1fr;
  }

  .reports-panel {
    border-radius: 22px;
    padding: 1rem;
  }

  .reports-panel-header {
    align-items: stretch;
    flex-direction: column;
  }

  .view-tabs,
  .filter-bar {
    width: 100%;
    overflow-x: auto;
    justify-content: flex-start;
  }

  .session-actions {
    align-items: stretch;
    flex-direction: column;
  }

  .details-btn {
    justify-content: center;
  }

  .metric-card {
    min-height: 124px;
  }
}

@supports not (backdrop-filter: blur(18px)) {
  .metric-card,
  .reports-panel,
  .session-row,
  .analytics-summary {
    background: var(--sb-card-bg);
  }
}
</style>
