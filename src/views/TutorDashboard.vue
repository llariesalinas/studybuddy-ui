<template>
  <div class="p-4">

    <div class="row g-4 mb-3">

      <div class="col-md-4">
        <div class="card border-sb rounded-4 p-4 shadow-sm h-100">
          <p class="text-muted small fw-bold mb-2">TOTAL SESSIONS</p>
          <Transition name="fade" mode="out-in">
            <h2 v-if="loading" class="fw-bold mb-0 placeholder-glow">
              <span class="placeholder col-5 rounded"></span>
            </h2>
            <h2 v-else class="fw-bold mb-0 text-dark">{{ totalSessions }}</h2>
          </Transition>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card border-sb rounded-4 p-4 shadow-sm h-100">
          <p class="text-muted small fw-bold mb-2">AVG RATING</p>
          <Transition name="fade" mode="out-in">
            <h2 v-if="loading" class="fw-bold mb-0 placeholder-glow">
              <span class="placeholder col-5 rounded"></span>
            </h2>
            <h2 v-else class="fw-bold mb-0 text-dark d-flex align-items-center">
              {{ avgRating }}
              <i class="bi bi-star-fill text-warning fs-4 ms-2"></i>
            </h2>
          </Transition>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card border-0 rounded-4 p-4 shadow-sm h-100" style="background-color: var(--sb-dark);">
          <p class="text-white-50 small fw-bold mb-2">EARNINGS</p>
          <Transition name="fade" mode="out-in">
            <h2 v-if="loading" class="fw-bold mb-0 placeholder-glow">
              <span class="placeholder col-5 rounded" style="background-color: rgba(255,255,255,0.25);"></span>
            </h2>
            <h2 v-else class="fw-bold text-white mb-0">₱{{ earnings }}</h2>
          </Transition>
        </div>
      </div>

    </div>

    <div class="row g-4 align-items-stretch">

      <div class="col-xl-8">
        <div class="card border-0 shadow-sm rounded-4 weekly-board-card h-100">
          <div class="card-body p-4 d-flex flex-column h-100">

            <header class="weekly-board-header d-flex flex-column flex-lg-row justify-content-between align-items-lg-center gap-3 mb-4">
              <div>
                <p class="weekly-board-kicker mb-2">Weekly Schedule</p>
                <h4 class="weekly-board-title mb-1">Your Sessions This Week</h4>
                <p class="weekly-board-subtitle mb-0">
                  Review your booked sessions across the week and open any session details in one click.
                </p>
              </div>
              <div class="d-flex align-items-center gap-2 align-self-start align-self-lg-auto weekly-board-nav">
                <button
                  type="button"
                  class="schedule-nav-btn"
                  :disabled="!canGoToPreviousWeek"
                  @click="goToPreviousWeek"
                  aria-label="Previous week"
                >
                  <i class="bi bi-chevron-left"></i>
                </button>
                <div class="week-range-pill">{{ formattedWeekRange }}</div>
                <button
                  type="button"
                  class="schedule-nav-btn"
                  :disabled="!canGoToNextWeek"
                  @click="goToNextWeek"
                  aria-label="Next week"
                >
                  <i class="bi bi-chevron-right"></i>
                </button>
              </div>
            </header>

            <Transition name="fade" mode="out-in">

              <div v-if="loading" class="weekly-board-skeleton flex-grow-1">
                <div class="weekly-grid">
                  <div v-for="i in 7" :key="'skeleton-day-' + i" class="day-column day-column-skeleton">
                    <div class="day-header">
                      <span class="placeholder col-5 rounded mb-2"></span>
                      <span class="placeholder col-7 rounded"></span>
                    </div>
                    <div class="day-body">
                      <div v-for="j in 2" :key="'skeleton-card-' + i + '-' + j" class="session-card-skeleton placeholder-glow">
                        <span class="placeholder col-4 rounded mb-2"></span>
                        <span class="placeholder col-8 rounded mb-2"></span>
                        <span class="placeholder col-6 rounded"></span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div v-else class="weekly-board-scroll custom-scrollbar flex-grow-1">
                <div class="weekly-grid">
                  <article
                    v-for="day in weekDays"
                    :key="day.key"
                    class="day-column"
                    :class="{ 'day-column-today': day.isToday }"
                  >
                    <div class="day-header">
                      <p class="day-name mb-1">{{ day.shortName }}</p>
                      <p class="day-date mb-0">{{ day.date.getDate() }}</p>
                    </div>

                    <div class="day-body">
                      <button
                        v-for="session in daySessionsMap[day.key]"
                        :key="session.id"
                        type="button"
                        class="weekly-session-card"
                        :class="getWeeklySessionCardClasses(session.status)"
                        :style="getSessionCardStyle(session)"
                        @click="goToBookingDetails(session.id)"
                      >
                        <p class="weekly-session-time mb-2">{{ formatSessionTime(session) }}</p>
                        <h6 class="weekly-session-title mb-1">{{ session.subject }}</h6>
                        <p class="weekly-session-tutor mb-2">{{ session.student || session.tuteeName || 'Student' }}</p>
                        <div class="d-flex align-items-center justify-content-between gap-2">
                          <span class="weekly-session-status">{{ session.status }}</span>
                          <span class="weekly-session-duration">{{ getSessionSlotSpan(session) }} slot{{ getSessionSlotSpan(session) === 1 ? '' : 's' }}</span>
                        </div>
                      </button>

                      <div v-if="!daySessionsMap[day.key]?.length" class="day-empty-state">
                        <i :class="getEmptyStateIcon(day.index)"></i>
                        <span>{{ getEmptyStateLabel(day.index) }}</span>
                      </div>
                    </div>
                  </article>
                </div>
              </div>
            </Transition>

          </div>
        </div>
      </div>

      <div class="col-xl-4">
        <div class="card border-sb shadow-sm rounded-4 h-100">
          <div class="card-body p-4 d-flex flex-column h-100">

            <div class="mb-3">
              <p class="weekly-board-kicker mb-2">Action Required</p>
              <h4 class="fw-bold mb-1">Pending Payments</h4>
              <p class="text-muted small mb-0">Sessions waiting on payment submission or your verification.</p>
            </div>

            <div class="flex-grow-1 d-flex flex-column overflow-hidden">
              <Transition name="fade" mode="out-in">

                <div v-if="loading" class="flex-grow-1">
                  <div class="d-flex flex-column gap-3 placeholder-glow">
                    <div v-for="i in 4" :key="'skel-pay-' + i" class="pending-payment-skeleton">
                      <span class="placeholder col-6 rounded mb-2 d-block"></span>
                      <span class="placeholder col-4 rounded mb-2 d-block"></span>
                      <span class="placeholder col-8 rounded d-block"></span>
                    </div>
                  </div>
                </div>

                <div v-else class="d-flex flex-column h-100">
                  <div class="flex-grow-1 overflow-auto pending-scroll custom-scrollbar">

                    <div v-if="pendingPaymentSessions.length === 0" class="text-center text-muted py-5">
                      <i class="bi bi-check-circle fs-2 mb-2 d-block text-success"></i>
                      <p class="small mb-0">No pending payments right now.</p>
                    </div>

                    <div
                      v-for="session in pendingPaymentSessions"
                      :key="session.id"
                      class="pending-payment-card mb-3"
                      :class="getPendingPaymentCardClass(session.status)"
                      @click="goToBookingDetails(session.id)"
                    >
                      <div class="d-flex justify-content-between align-items-start mb-1">
                        <h6 class="pending-payment-subject mb-0">{{ session.subject || 'General' }}</h6>
                        <span class="pending-payment-badge">{{ session.status }}</span>
                      </div>
                      <p class="pending-payment-student mb-1">{{ session.student || session.tuteeName || 'Student' }}</p>
                      <div class="d-flex align-items-center justify-content-between">
                        <p class="pending-payment-date mb-0">
                          <i class="bi bi-calendar3 me-1"></i>
                          {{ new Date(session.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) }}
                        </p>
                        <p class="pending-payment-time mb-0">
                          {{ formatSessionTime(session) }}
                        </p>
                      </div>
                    </div>

                  </div>

                  <div v-if="pendingPaymentSessions.length > 0" class="mt-3 pt-2 border-top flex-shrink-0">
                    <p class="text-muted small mb-0 text-center">
                      {{ pendingPaymentSessions.length }} session{{ pendingPaymentSessions.length === 1 ? '' : 's' }} awaiting action
                    </p>
                  </div>
                </div>

              </Transition>
            </div>

          </div>
        </div>
      </div>

    </div>
  </div>
</template>


<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api/api'

const router = useRouter()

const loading = ref(false)
const totalSessions = ref(0)
const avgRating = ref(0)
const earnings = ref(0)
const allBookings = ref([])
const weekOffset = ref(0)


const loadTutorDashboard = async () => {
  loading.value = true

  try {
    const response = await api.get('tutor-dashboard/')
    totalSessions.value = response.data.total_sessions
    avgRating.value = response.data.rating_average
    earnings.value = response.data.total_earnings
    allBookings.value = response.data.upcoming_bookings || []
  } catch (error) {
    console.error('Failed to load tutor dashboard:', error)
  } finally {
    loading.value = false
  }
}

onMounted(loadTutorDashboard)

const padNumber = (value) => String(value).padStart(2, '0')

const parseTimeToMinutes = (timeStr = '00:00') => {
  const [hours = 0, minutes = 0] = String(timeStr).split(':').map(Number)
  return (hours * 60) + minutes
}

const getStartOfWeek = (date) => {
  const start = new Date(date)
  const day = start.getDay()
  const diff = day === 0 ? -6 : 1 - day
  start.setHours(0, 0, 0, 0)
  start.setDate(start.getDate() + diff)
  return start
}

const addDays = (date, days) => {
  const next = new Date(date)
  next.setDate(next.getDate() + days)
  return next
}

const getEndOfMonth = (date) => new Date(date.getFullYear(), date.getMonth() + 1, 0)

const getDateKey = (date) =>
  `${date.getFullYear()}-${padNumber(date.getMonth() + 1)}-${padNumber(date.getDate())}`

const today = new Date()
const monthStart = new Date(today.getFullYear(), today.getMonth(), 1)
const monthEnd = getEndOfMonth(today)
const baseStartOfWeek = getStartOfWeek(today)
const minVisibleWeekStart = getStartOfWeek(monthStart)
const maxVisibleWeekStart = getStartOfWeek(monthEnd)
const MS_PER_WEEK = 7 * 24 * 60 * 60 * 1000
const minWeekOffset = Math.round((minVisibleWeekStart.getTime() - baseStartOfWeek.getTime()) / MS_PER_WEEK)
const maxWeekOffset = Math.round((maxVisibleWeekStart.getTime() - baseStartOfWeek.getTime()) / MS_PER_WEEK)

const visibleStartOfWeek = computed(() => addDays(baseStartOfWeek, weekOffset.value * 7))
const visibleEndOfWeek = computed(() => addDays(visibleStartOfWeek.value, 6))
const canGoToPreviousWeek = computed(() => weekOffset.value > minWeekOffset)
const canGoToNextWeek = computed(() => weekOffset.value < maxWeekOffset)

const weekDays = computed(() =>
  Array.from({ length: 7 }, (_, index) => {
    const date = addDays(visibleStartOfWeek.value, index)
    return {
      index,
      date,
      key: getDateKey(date),
      isToday: getDateKey(date) === getDateKey(today),
      shortName: date.toLocaleDateString('en-US', { weekday: 'short' }),
    }
  })
)

const formattedWeekRange = computed(() => {
  const start = visibleStartOfWeek.value
  const end = visibleEndOfWeek.value
  const startMonth = start.toLocaleDateString('en-US', { month: 'short' })
  const endMonth = end.toLocaleDateString('en-US', { month: 'short' })
  const year = end.getFullYear()
  if (startMonth === endMonth) {
    return `${startMonth} ${start.getDate()} - ${end.getDate()}, ${year}`
  }
  return `${startMonth} ${start.getDate()} - ${endMonth} ${end.getDate()}, ${year}`
})

const normalizeStatus = (status) => String(status || '').toLowerCase()

const visibleSessions = computed(() => {
  const startKey = getDateKey(visibleStartOfWeek.value)
  const endKey = getDateKey(visibleEndOfWeek.value)

  return allBookings.value
    .filter((session) => {
      const status = normalizeStatus(session.status)
      return (
        session.date >= startKey &&
        session.date <= endKey &&
        !['pending', 'cancelled', 'rejected'].includes(status)
      )
    })
    .sort((a, b) => {
      if (a.date !== b.date) return new Date(a.date) - new Date(b.date)
      const diff = parseTimeToMinutes(a.startTime) - parseTimeToMinutes(b.startTime)
      if (diff !== 0) return diff
      return parseTimeToMinutes(a.endTime) - parseTimeToMinutes(b.endTime)
    })
})

const mergeSessionsForDisplay = (sessions = []) => {
  const merged = []

  sessions.forEach((session) => {
    const prev = merged.at(-1)

    if (!prev) {
      merged.push({ ...session })
      return
    }

    const sameDay = prev.date === session.date
    const prevEndsAt = parseTimeToMinutes(prev.endTime)
    const nextStartsAt = parseTimeToMinutes(session.startTime)
    const isContinuous = prevEndsAt === nextStartsAt
    const sameGroup = prev.session_group_id && prev.session_group_id === session.session_group_id
    const sameMeta =
      prev.subject === session.subject &&
      (prev.student || prev.tuteeName) === (session.student || session.tuteeName) &&
      normalizeStatus(prev.status) === normalizeStatus(session.status)

    if (sameDay && isContinuous && (sameGroup || sameMeta)) {
      prev.endTime = session.endTime
      prev.duration_hours = (prev.duration_hours || 0) + (session.duration_hours || 0)
      return
    }

    merged.push({ ...session })
  })

  return merged
}

const daySessionsMap = computed(() => {
  const map = {}
  weekDays.value.forEach((day) => { map[day.key] = [] })
  mergeSessionsForDisplay(visibleSessions.value).forEach((session) => {
    if (map[session.date]) {
      map[session.date].push(session)
    }
  })
  return map
})

const pendingPaymentSessions = computed(() =>
  allBookings.value
    .filter((session) => {
      const status = normalizeStatus(session.status)
      return status === 'payment required' || status === 'awaiting verification'
    })
    .sort((a, b) => new Date(a.date) - new Date(b.date))
)

const formatDisplayTime = (timeStr = '00:00') => {
  const [hours = 0, minutes = 0] = String(timeStr).split(':').map(Number)
  const suffix = hours >= 12 ? 'PM' : 'AM'
  const hour = hours % 12 || 12
  return `${hour}:${String(minutes).padStart(2, '0')} ${suffix}`
}

const formatSessionTime = (session) =>
  `${formatDisplayTime(session.startTime)} - ${formatDisplayTime(session.endTime)}`

const getSessionDurationMinutes = (session) => {
  const duration = parseTimeToMinutes(session.endTime) - parseTimeToMinutes(session.startTime)
  return duration > 0 ? duration : 30
}

const getSessionSlotSpan = (session) => Math.max(1, Math.ceil(getSessionDurationMinutes(session) / 30))

const getSessionCardStyle = (session) => ({
  minHeight: `${Math.max(74, getSessionSlotSpan(session) * 42)}px`
})

const getWeeklySessionCardClasses = (status) => {
  const s = normalizeStatus(status)
  if (s === 'completed') return 'weekly-session-card-completed'
  if (s === 'ongoing') return 'weekly-session-card-ongoing'
  if (s === 'awaiting verification' || s === 'payment required') return 'weekly-session-card-verification'
  return 'weekly-session-card-upcoming'
}

const getPendingPaymentCardClass = (status) => {
  const s = normalizeStatus(status)
  return s === 'awaiting verification' ? 'pending-payment-card-verification' : 'pending-payment-card-payment'
}

const getEmptyStateLabel = (dayIndex) => {
  if (dayIndex === 5) return 'No Sessions'
  if (dayIndex === 6) return 'Open Day'
  return 'No sessions'
}

const getEmptyStateIcon = (dayIndex) => {
  if (dayIndex === 5) return 'bi bi-moon-stars'
  if (dayIndex === 6) return 'bi bi-book'
  return 'bi bi-calendar2-x'
}

// ─── Navigation ───────────────────────────────────────────────────────────────

const goToPreviousWeek = () => { if (canGoToPreviousWeek.value) weekOffset.value -= 1 }
const goToNextWeek = () => { if (canGoToNextWeek.value) weekOffset.value += 1 }

const goToBookingDetails = (id) => router.push({ name: 'booking-details', params: { id } })
</script>


<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease-in-out;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.weekly-board-card {
  min-height: 500px;
  background: #ffffff;
}

.weekly-board-kicker {
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #6b7d74;
}

.weekly-board-title {
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: #111827;
}

.weekly-board-subtitle {
  color: #6b7280;
  font-size: 0.9rem;
}

.weekly-board-header {
  padding-bottom: 0.5rem;
}

.weekly-board-nav {
  background: #f2f4f6;
  border-radius: 999px;
  padding: 0.3rem;
}

.week-range-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 180px;
  min-height: 38px;
  padding: 0.45rem 0.85rem;
  border-radius: 999px;
  background: #ffffff;
  color: #111827;
  font-size: 0.8rem;
  font-weight: 700;
  text-align: center;
  box-shadow: 0 1px 2px rgba(17, 24, 39, 0.06);
}

.schedule-nav-btn {
  width: 38px;
  height: 38px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: #4b5563;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease, box-shadow 0.2s ease;
}

.schedule-nav-btn:hover:not(:disabled) {
  background: #ffffff;
  color: #111827;
  box-shadow: 0 1px 2px rgba(17, 24, 39, 0.08);
}

.schedule-nav-btn:disabled {
  color: #9aa7b3;
  background: #f8faf9;
  cursor: not-allowed;
}

.custom-scrollbar::-webkit-scrollbar { height: 8px; width: 6px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #d6e2dd; border-radius: 999px; }

.weekly-board-scroll {
  overflow-x: auto;
  overflow-y: hidden;
  padding-bottom: 4px;
}

.weekly-board-skeleton { overflow: hidden; }

.weekly-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 8px;
  min-width: 0;
  align-items: start;
}

.day-column {
  display: grid;
  grid-template-rows: auto 1fr;
  min-height: 380px;
  min-width: 0;
  border-radius: 18px;
  background: transparent;
  overflow: hidden;
}

.day-column:nth-child(odd) .day-body  { background: rgba(242, 244, 246, 0.42); }
.day-column:nth-child(even) .day-body { background: #f2f4f6; }

.day-column-today .day-date { color: #0f172a; }

.day-header {
  padding: 0 0.3rem 0.65rem;
  background: transparent;
  text-align: center;
}

.day-name {
  font-size: 0.62rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  color: #8a9099;
}

.day-date {
  font-size: 1.1rem;
  font-weight: 800;
  color: #111827;
  line-height: 1;
}

.day-body {
  display: grid;
  align-content: start;
  gap: 0.55rem;
  padding: 0.55rem;
  border-radius: 14px;
  min-height: 332px;
  overflow-y: auto;
  overflow-x: hidden;
  min-width: 0;
}

.weekly-session-card {
  width: 100%;
  border: 0;
  border-radius: 12px;
  padding: 0.7rem 0.65rem;
  text-align: left;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 1px 2px rgba(17, 24, 39, 0.08);
  min-width: 0;
  overflow: hidden;
}

.weekly-session-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 24px rgba(17, 24, 39, 0.08);
}

.weekly-session-card-upcoming     { background: #f8fbff; border-left: 4px solid #0dcaf0; }
.weekly-session-card-ongoing      { background: #f5f9ff; border-left: 4px solid #0d6efd; }
.weekly-session-card-completed    { background: #f2fbf5; border-left: 4px solid #198754; }
.weekly-session-card-verification { background: #fff9ef; border-left: 4px solid #ffc107; }

.weekly-session-status {
  display: inline-flex;
  align-items: center;
  min-height: 22px;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
  background: #f3f4f6;
  font-size: 0.58rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #4b5563;
}

.weekly-session-card-upcoming .weekly-session-status     { background: rgba(13, 202, 240, 0.12); color: #087990; }
.weekly-session-card-ongoing .weekly-session-status      { background: rgba(13, 110, 253, 0.12); color: #0a58ca; }
.weekly-session-card-completed .weekly-session-status    { background: rgba(25, 135, 84, 0.12);  color: #146c43; }
.weekly-session-card-verification .weekly-session-status { background: rgba(255, 193, 7, 0.18);  color: #997404; }

.weekly-session-title {
  font-size: 0.72rem;
  font-weight: 800;
  line-height: 1.3;
  color: #111827;
  word-break: break-word;
}

.weekly-session-time {
  font-size: 0.62rem;
  font-weight: 800;
  color: #006c49;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.weekly-session-tutor {
  font-size: 0.66rem;
  color: #6b7280;
  word-break: break-word;
  overflow-wrap: anywhere;
}

.weekly-session-duration {
  font-size: 0.58rem;
  font-weight: 700;
  color: #6b7280;
  flex-shrink: 0;
  white-space: nowrap;
}

.day-empty-state {
  min-height: 110px;
  border: 1px dashed #d2d7de;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.72);
  display: grid;
  place-items: center;
  gap: 0.45rem;
  padding: 0.75rem;
  text-align: center;
  color: #8a9099;
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.day-empty-state i { font-size: 1rem; }

.session-card-skeleton {
  width: 100%;
  padding: 0.75rem;
  border-radius: 16px;
  background: #ffffff;
  box-shadow: 0 8px 20px rgba(19, 41, 34, 0.04);
}

.pending-scroll {
  max-height: 420px;
}

.pending-payment-card {
  border-radius: 14px;
  padding: 0.85rem 1rem;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 1px 3px rgba(17, 24, 39, 0.07);
}

.pending-payment-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(17, 24, 39, 0.09);
}

.pending-payment-card-payment     { background: #fff9ef; border-left: 4px solid #ffc107; }
.pending-payment-card-verification { background: #f0f7ff; border-left: 4px solid #0d6efd; }

.pending-payment-subject {
  font-size: 0.82rem;
  font-weight: 800;
  color: #111827;
}

.pending-payment-student {
  font-size: 0.72rem;
  color: #6b7280;
  margin-bottom: 0.4rem;
}

.pending-payment-date,
.pending-payment-time {
  font-size: 0.65rem;
  font-weight: 700;
  color: #6b7280;
}

.pending-payment-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.1rem 0.5rem;
  border-radius: 999px;
  font-size: 0.58rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  white-space: nowrap;
  background: rgba(255, 193, 7, 0.18);
  color: #997404;
}

.pending-payment-card-verification .pending-payment-badge {
  background: rgba(13, 110, 253, 0.12);
  color: #0a58ca;
}

.pending-payment-skeleton {
  padding: 0.85rem 1rem;
  border-radius: 14px;
  background: #f9fafb;
  border-left: 4px solid #e5e7eb;
}

@media (max-width: 1199px) {
  .weekly-grid {
    grid-template-columns: repeat(7, minmax(118px, 1fr));
    min-width: 860px;
  }
}

@media (max-width: 991px) {
  .week-range-pill { min-width: 160px; }
}

@media (max-width: 767px) {
  .weekly-grid {
    grid-template-columns: repeat(7, minmax(150px, 1fr));
    min-width: 1080px;
  }

  .weekly-board-header { align-items: flex-start !important; }
}
</style>