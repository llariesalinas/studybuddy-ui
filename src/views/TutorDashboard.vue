<template>
  <div class="tutor-dashboard">
    <section class="metric-grid" aria-label="Tutor dashboard metrics">
      <article
        v-for="metric in dashboardMetrics"
        :key="metric.label"
        class="metric-card"
      >
        <div class="metric-copy">
          <span class="metric-icon" :class="`metric-icon-${metric.tone}`">
            <i :class="['bi', metric.icon]"></i>
          </span>
          <span class="metric-label">{{ metric.label }}</span>
          <strong class="metric-value">{{ metric.value }}</strong>
          <span class="metric-note">{{ metric.note }}</span>
        </div>

        <div class="metric-visual" :class="`metric-visual-${metric.visual}`" aria-hidden="true">
          <svg v-if="metric.visual === 'ring'" class="metric-ring" viewBox="0 0 72 72">
            <circle class="metric-ring-track" cx="36" cy="36" r="28"></circle>
            <circle
              class="metric-ring-fill"
              cx="36"
              cy="36"
              r="28"
              :style="{ '--metric-progress': metric.progress }"
            ></circle>
          </svg>

          <div v-else class="metric-bars">
            <span
              v-for="(height, index) in metric.bars"
              :key="`${metric.label}-${height}-${index}`"
              :style="{ height: height + '%' }"
            ></span>
          </div>
        </div>
      </article>
    </section>

    <section class="bookings-panel">
      <header class="panel-header">
        <div>
          <p class="panel-kicker">Tutor Workspace</p>
          <h4 class="panel-title">
            <i class="bi bi-calendar2-week"></i>
            Upcoming Bookings
          </h4>
        </div>

        <span class="booking-count">
          <i class="bi bi-clock-history"></i>
          {{ upcomingBookings.length }} upcoming
        </span>
      </header>

      <div v-if="isLoading" class="state-panel">
        <div class="spinner-border text-sb-primary mb-3" role="status"></div>
        <p>Loading dashboard...</p>
      </div>

      <div v-else-if="errorMessage" class="state-panel state-panel-error">
        <i class="bi bi-exclamation-triangle"></i>
        <p>{{ errorMessage }}</p>
        <button type="button" class="retry-btn sb-btn" @click="loadTutorDashboard">
          <i class="bi bi-arrow-clockwise"></i>
          Retry
        </button>
      </div>

      <div v-else-if="upcomingBookings.length" class="booking-list">
        <article
          v-for="booking in upcomingBookings"
          :key="getBookingId(booking)"
          class="booking-card"
        >
          <div class="booking-main">
            <span class="booking-avatar">
              <i class="bi bi-person"></i>
            </span>

            <div class="booking-title-group">
              <h5>{{ getBookingStudent(booking) }}</h5>
              <span class="subject-pill">{{ getBookingSubject(booking) }}</span>
            </div>
          </div>

          <div class="booking-meta-grid">
            <div class="booking-meta-item">
              <span>Date</span>
              <strong>{{ formatDate(booking.date) }}</strong>
            </div>

            <div class="booking-meta-item">
              <span>Time</span>
              <strong>{{ formatBookingTime(booking) }}</strong>
            </div>

            <div class="booking-meta-item">
              <span>Status</span>
              <strong>
                <span class="status-badge" :class="getStatusClass(booking.status)">
                  {{ booking.status || 'Pending' }}
                </span>
              </strong>
            </div>
          </div>

          <button
            type="button"
            class="details-btn sb-btn"
            @click="goToBookingDetails(getBookingId(booking))"
          >
            <span>Details</span>
            <i class="bi bi-arrow-right"></i>
          </button>
        </article>
      </div>

      <div v-else class="state-panel">
        <i class="bi bi-calendar2-plus"></i>
        <p>No upcoming sessions yet.</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSessionsStore } from '@/stores/completedSessions'
import api from '@/services/api/api'

const router = useRouter()
const route = useRoute()
const sessionsStore = useSessionsStore()

const totalSessions = ref(0)
const avgRating = ref(0)
const earnings = ref(0)
const upcomingBookings = ref([])
const isLoading = ref(false)
const errorMessage = ref('')

const nextBooking = computed(() => upcomingBookings.value[0] || null)

const dashboardMetrics = computed(() => [
  {
    label: 'Total Sessions',
    value: totalSessions.value,
    note: 'All tutor sessions',
    icon: 'bi-calendar-event',
    tone: 'green',
    visual: 'ring',
    progress: Math.min(Number(totalSessions.value || 0) * 10, 100),
  },
  {
    label: 'Avg Rating',
    value: formatRating(avgRating.value),
    note: Number(avgRating.value || 0) ? 'Out of 5.0' : 'No ratings yet',
    icon: 'bi-star',
    tone: 'gold',
    visual: 'ring',
    progress: Math.round((Number(avgRating.value || 0) / 5) * 100),
  },
  {
    label: 'Earnings',
    value: formatCurrency(earnings.value),
    note: 'Total earnings',
    icon: 'bi-wallet2',
    tone: 'green',
    visual: 'bars',
    bars: [34, 52, 72, 92, 64, 44],
  },
  {
    label: 'Next Session',
    value: nextBooking.value ? formatDate(nextBooking.value.date, 'short') : 'None',
    note: nextBooking.value
      ? `${getBookingSubject(nextBooking.value)} with ${getBookingStudent(nextBooking.value)}`
      : `${upcomingBookings.value.length} upcoming bookings`,
    icon: 'bi-clock-history',
    tone: 'blue',
    visual: 'bars',
    bars: upcomingBookings.value.length ? [42, 58, 76, 88, 70, 50] : [22, 22, 22, 22, 22, 22],
  },
])

const goToBookingDetails = (id) => {
  router.push({
    name: 'booking-details',
    params: { id },
  })
}

const loadTutorDashboard = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const [_, response] = await Promise.all([
      sessionsStore.fetchSessions(),
      api.get('tutor-dashboard/'),
    ])

    totalSessions.value = response.data.total_sessions
    avgRating.value = response.data.rating_average
    earnings.value = response.data.total_earnings

    const apiBookings = response.data.upcoming_bookings || []
    const fallbackBookings = sessionsStore.upcomingSessions || []

    // Prefer dashboard payload, but fall back to the shared bookings list if empty.
    upcomingBookings.value = apiBookings.length ? apiBookings : fallbackBookings
  } catch (error) {
    console.error('Failed to load tutor dashboard:', error)
    errorMessage.value = 'Unable to load dashboard data right now.'
  } finally {
    isLoading.value = false
  }
}

const getBookingStudent = (booking) =>
  booking?.student || booking?.tuteeName || booking?.tutee || booking?.student_name || 'Student TBD'

const getBookingSubject = (booking) => booking?.subject || booking?.course || 'General'

const getBookingId = (booking) =>
  booking?.id || booking?.booking_id || booking?.booking_request_id || booking?.session_group_id

const formatCurrency = (value) => {
  const amount = Number(value || 0)

  if (!Number.isFinite(amount)) {
    return 'PHP 0'
  }

  return `PHP ${amount.toLocaleString('en-US', { maximumFractionDigits: 0 })}`
}

const formatRating = (value) => {
  const rating = Number(value || 0)

  if (!Number.isFinite(rating) || rating <= 0) {
    return '0.0'
  }

  return rating.toFixed(1)
}

const formatDate = (value, style = 'long') => {
  if (!value) {
    return 'Date TBD'
  }

  const normalized = String(value)
  const date = new Date(/^\d{4}-\d{2}-\d{2}$/.test(normalized) ? `${normalized}T00:00:00` : normalized)

  if (Number.isNaN(date.getTime())) {
    return 'Date TBD'
  }

  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: style === 'short' ? undefined : 'numeric',
  }).format(date)
}

const formatClock = (value) => {
  if (!value) {
    return ''
  }

  const normalized = String(value).trim()
  const timeOnly = normalized.match(/^(\d{1,2}):(\d{2})(?::\d{2})?$/)
  const date = timeOnly ? new Date(`1970-01-01T${normalized}`) : new Date(normalized)

  if (Number.isNaN(date.getTime())) {
    return normalized
  }

  return new Intl.DateTimeFormat('en-US', {
    hour: 'numeric',
    minute: '2-digit',
  }).format(date)
}

const formatBookingTime = (booking) => {
  const start = booking?.startTime || booking?.start_time || booking?.time_start || booking?.start
  const end = booking?.endTime || booking?.end_time || booking?.time_end || booking?.end
  const time = booking?.time || booking?.schedule_time

  if (start && end) {
    return `${formatClock(start)} - ${formatClock(end)}`
  }

  if (start || time) {
    return formatClock(start || time)
  }

  return 'Time TBD'
}

const getStatusClass = (status) => {
  switch (String(status || '').toLowerCase()) {
    case 'upcoming':
    case 'confirmed':
      return 'status-badge-upcoming'
    case 'ongoing':
      return 'status-badge-ongoing'
    case 'payment required':
    case 'awaiting verification':
    case 'awaiting payment verification':
      return 'status-badge-warning'
    case 'completed':
      return 'status-badge-completed'
    case 'rejected':
    case 'cancelled':
      return 'status-badge-danger'
    case 'pending':
    default:
      return 'status-badge-pending'
  }
}

onMounted(loadTutorDashboard)

watch(
  () => route.query.refresh,
  () => {
    loadTutorDashboard()
  }
)
</script>

<style scoped>
.tutor-dashboard {
  --dashboard-glass: color-mix(in srgb, var(--sb-card-bg) 85%, transparent);
  --dashboard-glass-strong: color-mix(in srgb, var(--sb-card-bg) 92%, transparent);
  --dashboard-border: color-mix(in srgb, var(--sb-card-border) 82%, transparent);
  --dashboard-muted: var(--sb-text-muted);
  --dashboard-ink: var(--sb-text-main);
  color: var(--dashboard-ink);
  display: grid;
  gap: 1rem;
  position: relative;
}

.tutor-dashboard::before {
  content: '';
  position: absolute;
  inset: -1rem -0.75rem auto auto;
  width: min(360px, 48vw);
  height: 220px;
  border-radius: 999px;
  background:
    radial-gradient(circle at 30% 35%, color-mix(in srgb, var(--sb-primary) 14%, transparent), transparent 58%),
    radial-gradient(circle at 72% 48%, rgba(56, 189, 248, 0.1), transparent 56%);
  filter: blur(40px);
  opacity: 0.55;
  pointer-events: none;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
  position: relative;
  z-index: 1;
}

.metric-card,
.booking-card {
  border: 1px solid var(--dashboard-border);
  background: var(--dashboard-glass-strong);
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.04);
}

.bookings-panel {
  border: 1px solid var(--dashboard-border);
  background: var(--dashboard-glass);
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
  inset: auto -24px -40px auto;
  width: 98px;
  height: 98px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--sb-primary) 12%, transparent);
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
.booking-avatar {
  width: 36px;
  height: 36px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--sb-primary) 12%, transparent);
  border: 1px solid color-mix(in srgb, var(--sb-primary) 22%, transparent);
  color: var(--sb-primary);
  flex: 0 0 auto;
}

.metric-icon-gold {
  background: rgba(255, 193, 7, 0.14);
  border-color: rgba(255, 193, 7, 0.28);
  color: #a66d00;
}

.metric-icon-blue {
  background: rgba(56, 189, 248, 0.12);
  border-color: rgba(56, 189, 248, 0.24);
  color: #087da4;
}

.metric-label,
.metric-note,
.panel-kicker,
.booking-meta-item span {
  color: var(--dashboard-muted);
}

.metric-label,
.panel-kicker,
.booking-meta-item span {
  font-size: 0.74rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0;
}

.metric-value {
  font-size: clamp(1.45rem, 1.9vw, 2.05rem);
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
  overflow-wrap: anywhere;
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
  filter: drop-shadow(0 0 8px color-mix(in srgb, var(--sb-primary) 20%, transparent));
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
    color-mix(in srgb, var(--sb-primary) 18%, transparent),
    color-mix(in srgb, var(--sb-primary) 76%, white)
  );
  box-shadow: 0 0 10px color-mix(in srgb, var(--sb-primary) 14%, transparent);
}

.bookings-panel {
  border-radius: 28px;
  padding: 1.25rem;
  position: relative;
  z-index: 1;
}

.panel-header {
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

.booking-count {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  border: 1px solid var(--dashboard-border);
  background: var(--dashboard-glass-strong);
  border-radius: 999px;
  color: var(--dashboard-muted);
  font-size: 0.88rem;
  font-weight: 800;
  padding: 0.55rem 0.85rem;
  white-space: nowrap;
}

.booking-count i {
  color: var(--sb-primary);
}

.booking-list {
  border-top: 1px solid var(--dashboard-border);
  display: grid;
  gap: 0.75rem;
  padding-top: 1rem;
}

.booking-card {
  border-radius: 20px;
  padding: 1rem;
  display: grid;
  grid-template-columns: minmax(180px, 1.1fr) minmax(320px, 1.6fr) auto;
  align-items: center;
  gap: 1rem;
}

.booking-main {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  min-width: 0;
}

.booking-title-group {
  min-width: 0;
}

.booking-title-group h5 {
  margin: 0;
  font-size: 1rem;
  font-weight: 800;
  letter-spacing: 0;
  overflow-wrap: anywhere;
}

.subject-pill {
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  margin-top: 0.38rem;
  border: 1px solid color-mix(in srgb, var(--sb-primary) 24%, transparent);
  border-radius: 999px;
  background: color-mix(in srgb, var(--sb-primary) 11%, transparent);
  color: var(--sb-primary);
  font-size: 0.78rem;
  font-weight: 800;
  padding: 0.28rem 0.62rem;
  overflow-wrap: anywhere;
}

.booking-meta-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
}

.booking-meta-item {
  min-width: 0;
}

.booking-meta-item strong {
  display: block;
  margin-top: 0.24rem;
  color: var(--dashboard-ink);
  font-size: 0.92rem;
  overflow-wrap: anywhere;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  border: 1px solid transparent;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 800;
  line-height: 1.2;
  padding: 0.32rem 0.65rem;
}

.status-badge-completed,
.status-badge-upcoming,
.status-badge-ongoing {
  color: var(--sb-primary);
  background: color-mix(in srgb, var(--sb-primary) 13%, transparent);
  border-color: color-mix(in srgb, var(--sb-primary) 24%, transparent);
}

.status-badge-warning {
  color: #9a6500;
  background: rgba(255, 193, 7, 0.14);
  border-color: rgba(255, 193, 7, 0.28);
}

.status-badge-danger {
  color: var(--bs-danger, #dc3545);
  background: rgba(220, 53, 69, 0.12);
  border-color: rgba(220, 53, 69, 0.26);
}

.status-badge-pending {
  color: var(--dashboard-muted);
  background: color-mix(in srgb, var(--sb-card-border) 42%, transparent);
  border-color: var(--dashboard-border);
}

.details-btn,
.retry-btn {
  border: 0;
  transition:
    transform var(--sb-t-quick, 120ms) var(--sb-spring-fast, ease),
    background-color var(--sb-t-normal, 250ms) var(--sb-spring, ease),
    color var(--sb-t-normal, 250ms) var(--sb-spring, ease),
    box-shadow var(--sb-t-normal, 250ms) var(--sb-spring, ease);
}

.details-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  border-radius: 999px;
  padding: 0.55rem 0.85rem;
  background: var(--sb-primary);
  color: var(--sb-primary-contrast, #fff);
  font-weight: 800;
  white-space: nowrap;
}

.details-btn:hover,
.retry-btn:hover {
  background: var(--sb-primary-hover);
  color: var(--sb-primary-contrast, #fff);
}

.details-btn:active,
.retry-btn:active {
  transform: scale(0.97);
}

.state-panel {
  min-height: 260px;
  border: 1px dashed var(--dashboard-border);
  border-radius: 22px;
  background: color-mix(in srgb, var(--sb-card-bg) 54%, transparent);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: var(--dashboard-muted);
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

.retry-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  border-radius: 999px;
  background: var(--sb-primary);
  color: var(--sb-primary-contrast, #fff);
  font-weight: 800;
  margin-top: 1rem;
  padding: 0.55rem 0.9rem;
}

.retry-btn i {
  color: currentColor;
  font-size: 1rem;
  margin: 0;
}

@media (max-width: 1199.98px) {
  .metric-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .booking-card {
    grid-template-columns: 1fr;
  }

  .details-btn {
    width: 100%;
  }
}

@media (max-width: 767.98px) {
  .metric-grid,
  .booking-meta-grid {
    grid-template-columns: 1fr;
  }

  .bookings-panel {
    border-radius: 22px;
    padding: 1rem;
  }

  .panel-header {
    align-items: stretch;
    flex-direction: column;
  }

  .booking-count {
    justify-content: center;
    width: 100%;
  }

  .metric-card {
    min-height: 124px;
  }
}

@supports not (backdrop-filter: blur(18px)) {
  .metric-card,
  .bookings-panel,
  .booking-card {
    background: var(--sb-card-bg);
  }
}
</style>
