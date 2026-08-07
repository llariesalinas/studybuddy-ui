<template>
  <div class="tutor-dashboard">
    <div v-if="isHiddenByLoadLimit" class="alert alert-warning" role="status">
      You are hidden from tutor search because you reached your Accepted Session Load Limit.
      Complete or cancel an upcoming session to become visible again.
    </div>

    <section class="metric-strip" aria-label="Tutor dashboard metrics">
      <div class="metric-cell">
        <span class="metric-label">Wallet Balance</span>
        <strong class="metric-value">{{ formatCurrency(walletBalance) }}</strong>
      </div>
      <div class="metric-cell">
        <span class="metric-label">Avg Rating</span>
        <strong class="metric-value">{{ formatRating(avgRating) }} <small>/ 5.0</small></strong>
      </div>
      <div class="metric-cell" :class="{ 'metric-cell-capacity': isHiddenByLoadLimit }">
        <span class="metric-label">Accepted Sessions</span>
        <strong class="metric-value" :class="{ 'metric-value-capacity': isHiddenByLoadLimit }">
          {{ acceptedSessionLoad }} <small>/ {{ sessionLoadLimit }}</small>
        </strong>
        <span v-if="isHiddenByLoadLimit" class="capacity-note">At capacity</span>
      </div>
    </section>

    <section
      class="dashboard-layout"
      :class="{ 'dashboard-layout-with-rail': hasAttentionBookings }"
    >
      <main class="schedule-column">
        <header class="panel-header">
          <h2>Full Schedule</h2>
          <span>{{ scheduleBookings.length }} committed</span>
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

        <div v-else-if="!upcomingBookings.length" class="empty-hero">
          <h3>No sessions yet</h3>
          <p>
            Tutees find you through your subjects and availability. Make sure both are set so you
            show up in search.
          </p>
          <button type="button" class="availability-btn sb-btn" @click="goToAvailability">
            Check my availability
          </button>
        </div>

        <template v-else>
          <div v-if="currentPageGroups.length" class="schedule-groups">
            <section v-for="group in currentPageGroups" :key="group.date" class="schedule-group">
              <header class="date-header">
                <span>
                  {{ formatScheduleDate(group.date) }}
                  <em v-if="getDateAccent(group.date)"> · {{ getDateAccent(group.date) }}</em>
                </span>
                <span>{{ formatSessionCount(group.bookings.length) }}</span>
              </header>

              <article
                v-for="booking in group.bookings"
                :key="getBookingId(booking)"
                class="schedule-row"
              >
                <strong class="schedule-time">{{ formatBookingStartTime(booking) }}</strong>
                <div class="schedule-details">
                  <strong>{{ getBookingStudent(booking) }}</strong>
                  <span>{{ getBookingSubject(booking) }} · {{ formatDuration(booking) }}</span>
                </div>
                <span class="status-badge" :class="getStatusClass(booking.status)">
                  {{ booking.status || 'Pending' }}
                </span>
                <button
                  type="button"
                  class="view-btn sb-btn"
                  @click="goToBookingDetails(getBookingId(booking))"
                >
                  View
                </button>
              </article>
            </section>
          </div>

          <div v-if="schedulePages.length" class="pager">
            <span>Showing {{ rangeStart }}-{{ rangeEnd }} of {{ scheduleBookings.length }}</span>
            <nav aria-label="Schedule pages">
              <button
                type="button"
                class="page-btn"
                :disabled="currentPage === 1"
                aria-label="Previous page"
                @click="currentPage -= 1"
              >
                ‹
              </button>
              <button
                v-for="page in schedulePages.length"
                :key="page"
                type="button"
                class="page-btn"
                :class="{ 'page-btn-current': currentPage === page }"
                :aria-current="currentPage === page ? 'page' : undefined"
                @click="currentPage = page"
              >
                {{ page }}
              </button>
              <button
                type="button"
                class="page-btn"
                :disabled="currentPage === schedulePages.length"
                aria-label="Next page"
                @click="currentPage += 1"
              >
                ›
              </button>
            </nav>
          </div>
        </template>
      </main>

      <aside v-if="hasAttentionBookings" class="attention-rail">
        <header class="panel-header">
          <h2>Needs Attention</h2>
          <span>{{ attentionBookings.requests.length + attentionBookings.payments.length }}</span>
        </header>

        <div class="attention-panel">
          <section v-if="attentionBookings.requests.length">
            <header class="attention-section-header">
              <span>Requests</span>
              <span>{{ attentionBookings.requests.length }}</span>
            </header>
            <article
              v-for="booking in attentionBookings.requests"
              :key="getBookingId(booking)"
              class="attention-row"
            >
              <strong>{{ getBookingStudent(booking) }}</strong>
              <span class="attention-subject">{{ getBookingSubject(booking) }}</span>
              <span class="attention-when">{{ formatAttentionTime(booking) }}</span>
              <div>
                <span class="status-badge" :class="getStatusClass(booking.status)">
                  {{ booking.status || 'Pending' }}
                </span>
                <button
                  type="button"
                  class="view-btn sb-btn"
                  @click="goToBookingDetails(getBookingId(booking))"
                >
                  View
                </button>
              </div>
            </article>
          </section>

          <section v-if="attentionBookings.payments.length">
            <header class="attention-section-header">
              <span>Payments</span>
              <span>{{ attentionBookings.payments.length }}</span>
            </header>
            <article
              v-for="booking in attentionBookings.payments"
              :key="getBookingId(booking)"
              class="attention-row"
            >
              <strong>{{ getBookingStudent(booking) }}</strong>
              <span class="attention-subject">{{ getBookingSubject(booking) }}</span>
              <span class="attention-when">{{ formatAttentionTime(booking) }}</span>
              <div>
                <span class="status-badge" :class="getStatusClass(booking.status)">
                  {{ booking.status || 'Pending' }}
                </span>
                <button
                  type="button"
                  class="view-btn sb-btn"
                  @click="goToBookingDetails(getBookingId(booking))"
                >
                  View
                </button>
              </div>
            </article>
          </section>
        </div>
      </aside>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSessionsStore } from '@/stores/completedSessions'
import { useWalletStore } from '@/stores/wallet'
import api from '@/services/api/api'
import { dayPackedPages, groupByDate, splitBookingsByAttention } from '@/services/tutorDashboard'

const router = useRouter()
const route = useRoute()
const sessionsStore = useSessionsStore()
const walletStore = useWalletStore()

const avgRating = ref(0)
const acceptedSessionLoad = ref(0)
const sessionLoadLimit = ref(10)
const upcomingBookings = ref([])
const isLoading = ref(false)
const errorMessage = ref('')
const currentPage = ref(1)

const walletBalance = computed(() => Number(walletStore.balance || 0))
const isHiddenByLoadLimit = computed(() => acceptedSessionLoad.value >= sessionLoadLimit.value)
const attentionBookings = computed(() => splitBookingsByAttention(upcomingBookings.value))
const scheduleBookings = computed(() => attentionBookings.value.schedule)
const schedulePages = computed(() => dayPackedPages(groupByDate(scheduleBookings.value)))
const currentPageGroups = computed(() => schedulePages.value[currentPage.value - 1] || [])
const hasAttentionBookings = computed(
  () => attentionBookings.value.requests.length + attentionBookings.value.payments.length > 0,
)
const rangeStart = computed(() => {
  if (!currentPageGroups.value.length) {
    return 0
  }

  return (
    schedulePages.value
      .slice(0, currentPage.value - 1)
      .flat()
      .reduce((count, group) => count + group.bookings.length, 0) + 1
  )
})
const rangeEnd = computed(
  () =>
    rangeStart.value +
    currentPageGroups.value.reduce((count, group) => count + group.bookings.length, 0) -
    1,
)

const goToBookingDetails = (id) => {
  router.push({
    name: 'booking-details',
    params: { id },
  })
}

const goToAvailability = () => router.push({ name: 'tch-availability' })

const loadTutorDashboard = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const walletLoad = walletStore.fetchWallet()
    const [, response] = await Promise.all([
      sessionsStore.fetchSessions(),
      api.get('tutor-dashboard/'),
    ])
    await walletLoad.catch(() => {})

    avgRating.value = response.data.rating_average
    acceptedSessionLoad.value = response.data.accepted_session_load ?? 0
    sessionLoadLimit.value = response.data.session_load_limit ?? 10

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

  return Number.isFinite(amount)
    ? `PHP ${amount.toLocaleString('en-US', { maximumFractionDigits: 0 })}`
    : 'PHP 0'
}

const formatRating = (value) => {
  const rating = Number(value || 0)

  return Number.isFinite(rating) && rating > 0 ? rating.toFixed(1) : '0.0'
}

const formatDate = (value, options) => {
  const normalized = String(value || '')
  const date = new Date(
    /^\d{4}-\d{2}-\d{2}$/.test(normalized) ? `${normalized}T00:00:00` : normalized,
  )

  if (Number.isNaN(date.getTime())) {
    return 'Date TBD'
  }

  return new Intl.DateTimeFormat('en-US', options).format(date)
}

const formatScheduleDate = (value) =>
  formatDate(value, { weekday: 'short', month: 'short', day: 'numeric' })

const formatClock = (value) => {
  if (!value) {
    return 'Time TBD'
  }

  const normalized = String(value).trim()
  const timeOnly = normalized.match(/^(\d{1,2}):(\d{2})(?::\d{2})?$/)
  const date = timeOnly ? new Date(`1970-01-01T${normalized}`) : new Date(normalized)

  return Number.isNaN(date.getTime())
    ? normalized
    : new Intl.DateTimeFormat('en-US', { hour: 'numeric', minute: '2-digit' }).format(date)
}

const getBookingStart = (booking) =>
  booking?.startTime ||
  booking?.start_time ||
  booking?.time_start ||
  booking?.start ||
  booking?.time

const formatBookingStartTime = (booking) => formatClock(getBookingStart(booking))

const formatDuration = (booking) => {
  const hours = Number(booking?.duration_hours)

  return Number.isFinite(hours) && hours > 0
    ? `${hours} ${hours === 1 ? 'hr' : 'hrs'}`
    : 'Duration TBD'
}

const formatSessionCount = (count) => `${count} ${count === 1 ? 'session' : 'sessions'}`

const formatAttentionTime = (booking) =>
  `${formatDate(booking?.date, { month: 'short', day: 'numeric' })}, ${formatBookingStartTime(booking)}`

// Built from local date parts on purpose: toISOString() converts to UTC, which would
// mislabel Today/Tomorrow for every Manila morning before 08:00 (UTC+8).
const toLocalDateKey = (date) => {
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')

  return `${date.getFullYear()}-${month}-${day}`
}

const getDateAccent = (value) => {
  const normalized = String(value || '')
  const today = new Date()
  const tomorrow = new Date(today)
  tomorrow.setDate(today.getDate() + 1)

  if (normalized === toLocalDateKey(today)) {
    return 'Today'
  }

  return normalized === toLocalDateKey(tomorrow) ? 'Tomorrow' : ''
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

watch(schedulePages, (pages) => {
  currentPage.value = Math.min(Math.max(currentPage.value, 1), Math.max(pages.length, 1))
})

onMounted(loadTutorDashboard)

watch(
  () => route.query.refresh,
  () => {
    loadTutorDashboard()
  },
)
</script>

<style scoped>
.tutor-dashboard {
  --dashboard-border: color-mix(in srgb, var(--sb-card-border) 82%, transparent);
  --dashboard-muted: var(--sb-text-muted);
  --dashboard-ink: var(--sb-text-main);
  color: var(--dashboard-ink);
  display: grid;
  gap: 1rem;
}

.metric-strip,
.schedule-column,
.attention-panel {
  border: 1px solid var(--dashboard-border);
  background: var(--sb-card-bg);
}

.metric-strip {
  display: flex;
  border-radius: 0.75rem;
  overflow: hidden;
}

.metric-cell {
  flex: 1;
  min-width: 0;
  padding: 0.7rem 0.9rem;
  border-right: 1px solid var(--dashboard-border);
}

.metric-cell:last-child {
  border-right: 0;
}

.metric-cell-capacity {
  background: color-mix(in srgb, var(--bs-warning) 10%, var(--sb-card-bg));
}

.metric-label,
.capacity-note,
.panel-header span,
.date-header,
.pager,
.attention-when {
  color: var(--dashboard-muted);
  font-size: 0.72rem;
  font-weight: 800;
}

.metric-label,
.capacity-note,
.attention-section-header {
  display: block;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.metric-value {
  display: block;
  margin-top: 0.2rem;
  font-size: 1.25rem;
  line-height: 1.1;
}

.metric-value small {
  color: var(--dashboard-muted);
  font-size: 0.78rem;
  font-weight: 700;
}

.metric-value-capacity,
.capacity-note,
.attention-section-header {
  color: var(--bs-warning-text-emphasis);
}

.capacity-note {
  margin-top: 0.18rem;
}

.dashboard-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.875rem;
  align-items: start;
}

.dashboard-layout-with-rail {
  grid-template-columns: 1fr 300px;
}

.schedule-column,
.attention-panel {
  border-radius: 0.75rem;
  overflow: hidden;
}

.schedule-column {
  padding: 1rem;
}

.panel-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.65rem;
}

.panel-header h2 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 800;
}

.attention-rail .panel-header h2 {
  color: var(--bs-warning-text-emphasis);
}

.schedule-groups {
  border: 1px solid var(--dashboard-border);
  border-radius: 0.75rem;
  overflow: hidden;
}

.schedule-group + .schedule-group .date-header {
  border-top: 1px solid var(--dashboard-border);
}

.date-header,
.attention-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.45rem 0.75rem;
  background: color-mix(in srgb, var(--sb-primary) 5%, var(--sb-card-bg));
}

.date-header em {
  color: var(--sb-primary);
  font-style: normal;
}

.schedule-row {
  display: grid;
  grid-template-columns: 70px minmax(0, 1fr) 122px auto;
  align-items: center;
  gap: 0.625rem;
  padding: 0.65rem 0.75rem;
  border-top: 1px solid var(--dashboard-border);
}

.schedule-group .date-header + .schedule-row {
  border-top: 0;
}

.schedule-time,
.schedule-details strong,
.attention-row > strong {
  font-size: 0.78rem;
}

.schedule-details {
  min-width: 0;
}

.schedule-details strong,
.schedule-details span,
.attention-row > strong,
.attention-subject,
.attention-when {
  display: block;
}

.schedule-details span,
.attention-subject {
  margin-top: 0.18rem;
  color: var(--sb-primary);
  font-size: 0.72rem;
  font-weight: 700;
  overflow-wrap: anywhere;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  border: 1px solid transparent;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 800;
  line-height: 1.2;
  padding: 0.3rem 0.55rem;
}

.status-badge-completed,
.status-badge-upcoming,
.status-badge-ongoing {
  color: var(--sb-primary);
  background: color-mix(in srgb, var(--sb-primary) 13%, transparent);
  border-color: color-mix(in srgb, var(--sb-primary) 24%, transparent);
}

.status-badge-warning {
  color: var(--bs-warning-text-emphasis);
  background: color-mix(in srgb, var(--bs-warning) 14%, transparent);
  border-color: color-mix(in srgb, var(--bs-warning) 28%, transparent);
}

.status-badge-danger {
  color: var(--sb-danger-bs);
  background: color-mix(in srgb, var(--sb-danger-bs) 12%, transparent);
  border-color: color-mix(in srgb, var(--sb-danger-bs) 26%, transparent);
}

.status-badge-pending {
  color: var(--dashboard-muted);
  background: color-mix(in srgb, var(--sb-card-border) 42%, transparent);
  border-color: var(--dashboard-border);
}

.view-btn,
.page-btn,
.availability-btn,
.retry-btn {
  border: 1px solid var(--dashboard-border);
  border-radius: 0.45rem;
  background: var(--sb-card-bg);
  color: var(--dashboard-ink);
  font-size: 0.72rem;
  font-weight: 800;
  padding: 0.3rem 0.55rem;
}

.availability-btn,
.retry-btn,
.page-btn-current {
  border-color: var(--sb-primary);
  background: var(--sb-primary);
  color: var(--sb-primary-contrast);
}

.pager {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding-top: 0.7rem;
}

.pager nav {
  display: flex;
  gap: 0.3rem;
}

.page-btn {
  min-width: 1.65rem;
  height: 1.65rem;
  padding: 0;
}

.page-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.attention-panel {
  border-color: color-mix(in srgb, var(--bs-warning) 35%, var(--dashboard-border));
}

.attention-section-header {
  background: color-mix(in srgb, var(--bs-warning) 8%, var(--sb-card-bg));
  border-bottom: 1px solid color-mix(in srgb, var(--bs-warning) 25%, var(--dashboard-border));
  font-size: 0.68rem;
}

.attention-row {
  padding: 0.7rem 0.75rem;
  border-bottom: 1px solid color-mix(in srgb, var(--bs-warning) 20%, var(--dashboard-border));
}

.attention-row:last-child {
  border-bottom: 0;
}

.attention-when {
  margin-top: 0.22rem;
}

.attention-row > div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-top: 0.55rem;
}

.state-panel,
.empty-hero {
  min-height: 240px;
  border: 1px dashed var(--dashboard-border);
  border-radius: 0.75rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: var(--dashboard-muted);
  text-align: center;
}

.state-panel p,
.empty-hero h3,
.empty-hero p {
  margin: 0;
}

.empty-hero h3 {
  color: var(--dashboard-ink);
  font-size: 1rem;
}

.empty-hero p {
  max-width: 31rem;
  margin-top: 0.45rem;
  font-size: 0.82rem;
  line-height: 1.5;
}

.availability-btn,
.retry-btn {
  margin-top: 1rem;
  border-radius: 999px;
  padding: 0.5rem 0.85rem;
}

.state-panel-error {
  color: var(--sb-danger-bs);
}

@media (max-width: 899.98px) {
  .dashboard-layout-with-rail {
    grid-template-columns: 1fr;
  }

  .attention-rail {
    order: -1;
  }

  .schedule-row {
    grid-template-columns: 70px minmax(0, 1fr) auto;
  }

  .schedule-row .status-badge {
    grid-column: 2;
  }

  .schedule-row .view-btn {
    grid-column: 3;
    grid-row: 1 / span 2;
  }
}

@media (max-width: 599.98px) {
  .metric-cell {
    padding: 0.65rem 0.55rem;
  }

  .metric-value {
    font-size: 1rem;
  }

  .schedule-column {
    padding: 0.75rem;
  }

  .schedule-row {
    grid-template-columns: 1fr auto;
  }

  .schedule-time {
    grid-column: 1;
  }

  .schedule-details {
    grid-column: 1;
  }

  .schedule-row .status-badge {
    grid-column: 1;
  }

  .schedule-row .view-btn {
    grid-column: 2;
    grid-row: 1 / span 3;
  }

  .pager {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
