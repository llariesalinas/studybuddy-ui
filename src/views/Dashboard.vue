<template>
  <div class="dashboard-page p-4">
    <div class="row g-4 mb-5">
      <div v-for="(stat, index) in stats" :key="index" class="col-md-3">
        <div class="card border-sb shadow-sm rounded-4 h-100 p-3 d-flex flex-row align-items-center stat-card">
          <div :class="[stat.bgClass, 'p-3 rounded-4 me-3']">
            <i :class="[stat.icon, 'text-sb-primary fs-3']"></i>
          </div>
          <div class="flex-grow-1">
            <h6 class="text-muted small fw-bold mb-1">{{ stat.label }}</h6>
            <Transition name="fade" mode="out-in">
              <h2 v-if="loading" class="fw-bold mb-0 placeholder-glow">
                <span class="placeholder col-6 rounded"></span>
              </h2>
              <h2 v-else class="fw-bold mb-0">{{ stat.count }}</h2>
            </Transition>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-4 align-items-stretch">
      <div class="col-xl-8">
        <div class="card border-0 shadow-sm rounded-4 weekly-board-card h-100">
          <div class="card-body p-4 p-xl-4 d-flex flex-column h-100">
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
                <div class="week-range-pill">
                  {{ formattedWeekRange }}
                </div>
                <button
                  type="button"
                  class="schedule-nav-btn"
                  :disabled="!canGoToNextWeek"
                  @click="goToNextWeek"
                  aria-label="Next week"
                >
                  <i class="bi bi-chevron-right"></i>
                </button>
                <button
                  v-if="nextSessionWeekOffset !== null && weekOffset !== nextSessionWeekOffset"
                  type="button"
                  class="btn btn-sm ms-1"
                  style="font-size: 0.75rem; color: var(--sb-primary); border: 1px solid var(--sb-primary); white-space: nowrap;"
                  @click="weekOffset = nextSessionWeekOffset"
                  aria-label="Jump to next session"
                >
                  <i class="bi bi-calendar2-event me-1"></i>Next session
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
                        @click="goToDetails(session.id)"
                      >
                        <p class="weekly-session-time mb-2">{{ formatSessionTime(session) }}</p>
                        <h6 class="weekly-session-title mb-1">{{ session.subject }}</h6>
                        <p class="weekly-session-tutor mb-2">{{ session.tutor }}</p>
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
        <div class="card border-sb shadow-sm rounded-4 recommendations-card h-100">
          <div class="card-body p-4 d-flex flex-column h-100">
            <div class="mb-3">
              <p class="weekly-board-kicker mb-2">Discover</p>
              <h4 class="fw-bold mb-1">Try out these tutors</h4>
              <p class="text-muted small mb-0">Browse recommended tutors without leaving your dashboard rhythm.</p>
            </div>

            <div class="flex-grow-1 d-flex flex-column overflow-hidden">
              <Transition name="fade" mode="out-in">
                <div v-if="loading" class="flex-grow-1 pe-2">
                  <div class="list-group list-group-flush placeholder-glow">
                    <div v-for="i in 6" :key="'skel-tutor-' + i" class="list-group-item d-flex justify-content-between align-items-center py-2">
                      <div class="w-75">
                        <h6 class="mb-1"><span class="placeholder col-8 rounded"></span></h6>
                        <p class="mb-0"><span class="placeholder col-5 rounded"></span></p>
                      </div>
                      <div class="w-25 text-end">
                        <span class="placeholder col-10 rounded"></span>
                      </div>
                    </div>
                  </div>
                </div>

                <div v-else class="d-flex flex-column h-100">
                  <div class="flex-grow-1 pe-2">
                    <div class="list-group list-group-flush">
                      <div v-if="pagedTutors.length === 0" class="text-muted small py-3">
                        No recommended tutors available at the moment.
                      </div>

                      <div
                        v-for="tutor in pagedTutors"
                        :key="tutor.id"
                        class="list-group-item d-flex justify-content-between align-items-center py-2 tutor-list-item"
                        @click="bookTutor(tutor.id)"
                      >
                        <div>
                          <h6 class="mb-1">{{ tutor.name }}</h6>
                          <p class="mb-0 text-muted small">Rating {{ tutor.rating || 'N/A' }} | {{ tutor.subjects?.join(', ') || 'Various Subjects' }}</p>
                        </div>
                        <div class="fw-bold text-sb-primary">PHP {{ tutor.hourlyRate || 0 }}/hr</div>
                      </div>
                    </div>
                  </div>

                  <div class="d-flex justify-content-between align-items-center mt-3 pt-2 border-top flex-shrink-0">
                    <button class="btn bg-sb-primary text-white btn-sm" @click="prevPage" :disabled="page === 1">Prev</button>
                    <span class="small text-muted">Page {{ page }} of {{ totalPages || 1 }}</span>
                    <button class="btn bg-sb-primary text-white btn-sm" @click="nextPage" :disabled="page >= totalPages">Next</button>
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSessionsStore } from '@/stores/completedSessions'

const router = useRouter()
const route = useRoute()
const sessionsStore = useSessionsStore()
const loading = ref(false)
const weekOffset = ref(0)

const getSessionDateKey = (session) => {
  const rawDate = session?.date

  if (!rawDate) {
    return ''
  }

  const rawString = String(rawDate)

  if (/^\d{4}-\d{2}-\d{2}$/.test(rawString)) {
    return rawString
  }

  const parsedDate = new Date(rawString)

  if (Number.isNaN(parsedDate.getTime())) {
    return rawString.slice(0, 10)
  }

  return getDateKey(parsedDate)
}

const hasVisibleWeekSessions = () => {
  const startKey = getDateKey(visibleStartOfWeek.value)
  const endKey = getDateKey(visibleEndOfWeek.value)

  return (sessionsStore.sessions || []).some((session) => {
    const normalizedStatus = String(session?.status || '').toLowerCase()
    const sessionDateKey = getSessionDateKey(session)

    return (
      sessionDateKey >= startKey
      && sessionDateKey <= endKey
      && !['cancelled', 'rejected'].includes(normalizedStatus)
    )
  })
}

const ensureWeekContainsSessions = () => {
  if (nextSessionWeekOffset.value === null) {
    return
  }

  if (!hasVisibleWeekSessions()) {
    weekOffset.value = nextSessionWeekOffset.value
  }
}

const refreshDashboard = async () => {
  loading.value = true

  await Promise.all([
    sessionsStore.fetchSessions(),
    sessionsStore.fetchRecommendations()
  ])

  loading.value = false

  ensureWeekContainsSessions()
}

onMounted(refreshDashboard)

watch(
  () => route.query.refresh,
  () => {
    refreshDashboard()
  }
)

watch(
  () => sessionsStore.sessions,
  () => {
    ensureWeekContainsSessions()
  }
)

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

const getEndOfMonth = (date) => {
  return new Date(date.getFullYear(), date.getMonth() + 1, 0)
}

const getDateKey = (date) => `${date.getFullYear()}-${padNumber(date.getMonth() + 1)}-${padNumber(date.getDate())}`

const today = new Date()
const monthStart = new Date(today.getFullYear(), today.getMonth(), 1)
const monthEnd = new Date(today.getFullYear(), today.getMonth() + 3, 0)
const baseStartOfWeek = getStartOfWeek(today)
const minVisibleWeekStart = getStartOfWeek(monthStart)
const maxVisibleWeekStart = getStartOfWeek(monthEnd)
const MS_PER_WEEK = 7 * 24 * 60 * 60 * 1000
const minWeekOffset = Math.round((minVisibleWeekStart.getTime() - baseStartOfWeek.getTime()) / MS_PER_WEEK)
const maxWeekOffset = Math.round((maxVisibleWeekStart.getTime() - baseStartOfWeek.getTime()) / MS_PER_WEEK)

const nextSessionWeekOffset = computed(() => {
  const upcoming = sessionsStore.upcomingSessions
  if (!upcoming || upcoming.length === 0) return null
  const nearestDate = new Date(upcoming[0].date)
  const nearestWeekStart = getStartOfWeek(nearestDate)
  const offset = Math.round((nearestWeekStart.getTime() - baseStartOfWeek.getTime()) / MS_PER_WEEK)
  return Math.min(Math.max(offset, minWeekOffset), maxWeekOffset)
})

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
      headerLabel: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
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

const visibleSessions = computed(() => {
  const startKey = getDateKey(visibleStartOfWeek.value)
  const endKey = getDateKey(visibleEndOfWeek.value)
  const allSessions = (sessionsStore.sessions || []).map((session) => ({
    ...session,
    dateKey: getSessionDateKey(session)
  }))

  return allSessions
    .filter((session) => {
      return (
        session.dateKey >= startKey
        && session.dateKey <= endKey
      )
    })
    .sort((left, right) => {
      if (left.dateKey !== right.dateKey) {
        return new Date(left.dateKey) - new Date(right.dateKey)
      }

      const startDifference = parseTimeToMinutes(left.startTime) - parseTimeToMinutes(right.startTime)

      if (startDifference !== 0) {
        return startDifference
      }

      return parseTimeToMinutes(left.endTime) - parseTimeToMinutes(right.endTime)
    })
})

const mergeSessionsForDisplay = (sessions = []) => {
  const mergedSessions = []

  sessions.forEach((session) => {
    const previousSession = mergedSessions.at(-1)

    if (!previousSession) {
      mergedSessions.push({ ...session })
      return
    }

    const previousDateKey = previousSession.dateKey || previousSession.date
    const nextDateKey = session.dateKey || session.date
    const sameDay = previousDateKey === nextDateKey
    const previousEndsAt = parseTimeToMinutes(previousSession.endTime)
    const nextStartsAt = parseTimeToMinutes(session.startTime)
    const isContinuous = previousEndsAt === nextStartsAt
    const sameGroup = previousSession.session_group_id && previousSession.session_group_id === session.session_group_id
    const sameSessionMeta = (
      previousSession.subject === session.subject
      && previousSession.tutor === session.tutor
      && String(previousSession.status || '').toLowerCase() === String(session.status || '').toLowerCase()
    )

    if (sameDay && isContinuous && (sameGroup || sameSessionMeta)) {
      previousSession.endTime = session.endTime
      previousSession.duration_hours = (previousSession.duration_hours || 0) + (session.duration_hours || 0)
      return
    }

    mergedSessions.push({ ...session })
  })

  return mergedSessions
}

const daySessionsMap = computed(() => {
  const groupedSessions = {}

  weekDays.value.forEach((day) => {
    groupedSessions[day.key] = []
  })

  mergeSessionsForDisplay(visibleSessions.value).forEach((session) => {
    const sessionDateKey = session.dateKey || session.date
    if (groupedSessions[sessionDateKey]) {
      groupedSessions[sessionDateKey].push(session)
    }
  })

  return groupedSessions
})

const formatDisplayTime = (timeStr = '00:00') => {
  const [hours = 0, minutes = 0] = String(timeStr).split(':').map(Number)
  const suffix = hours >= 12 ? 'PM' : 'AM'
  const hour = hours % 12 || 12
  return `${hour}:${String(minutes).padStart(2, '0')} ${suffix}`
}

const formatSessionTime = (session) => `${formatDisplayTime(session.startTime)} - ${formatDisplayTime(session.endTime)}`

const getSessionDurationMinutes = (session) => {
  const duration = parseTimeToMinutes(session.endTime) - parseTimeToMinutes(session.startTime)
  return duration > 0 ? duration : 30
}

const getSessionSlotSpan = (session) => Math.max(1, Math.ceil(getSessionDurationMinutes(session) / 30))

const getSessionCardStyle = (session) => ({
  minHeight: `${Math.max(74, getSessionSlotSpan(session) * 42)}px`
})

const getEmptyStateLabel = (dayIndex) => {
  if (dayIndex === 5) {
    return 'No Sessions'
  }

  if (dayIndex === 6) {
    return 'Open Day'
  }

  return 'No sessions'
}

const getEmptyStateIcon = (dayIndex) => {
  if (dayIndex === 5) {
    return 'bi bi-moon-stars'
  }

  if (dayIndex === 6) {
    return 'bi bi-book'
  }

  return 'bi bi-calendar2-x'
}

const getWeeklySessionCardClasses = (status) => {
  const s = String(status || '').toLowerCase()
  if (s === 'pending')               return 'weekly-session-card-pending'
  if (s === 'upcoming')              return 'weekly-session-card-upcoming'
  if (s === 'ongoing')               return 'weekly-session-card-ongoing'
  if (s === 'awaiting verification') return 'weekly-session-card-verification'
  if (s === 'payment required')      return 'weekly-session-card-payment-required'
  if (s === 'completed')             return 'weekly-session-card-completed'
  if (s === 'rejected')              return 'weekly-session-card-rejected'
  if (s === 'cancelled')             return 'weekly-session-card-cancelled'
  return 'weekly-session-card-upcoming'
}

const goToPreviousWeek = () => {
  if (canGoToPreviousWeek.value) {
    weekOffset.value -= 1
  }
}

const goToNextWeek = () => {
  if (canGoToNextWeek.value) {
    weekOffset.value += 1
  }
}

const stats = computed(() => [
  { label: 'Pending', count: sessionsStore.requestedSessions?.length || 0, icon: 'bi-clock', bgClass: 'bg-warning bg-opacity-10' },
  { label: 'Upcoming', count: sessionsStore.upcomingSessions?.length || 0, icon: 'bi-calendar-event', bgClass: 'bg-info bg-opacity-10' },
  { label: 'Ongoing', count: sessionsStore.ongoingSessions?.length || 0, icon: 'bi-play-circle', bgClass: 'bg-primary bg-opacity-10' },
  { label: 'Completed', count: sessionsStore.completedSessions?.length || 0, icon: 'bi-check-square', bgClass: 'bg-success bg-opacity-10' }
])

const page = ref(1)
const pageSize = 6

const totalPages = computed(() => {
  const total = sessionsStore.recommendedTutors?.length || 0
  return Math.ceil(total / pageSize) || 1
})

const pagedTutors = computed(() => {
  const tutors = sessionsStore.recommendedTutors || []
  const start = (page.value - 1) * pageSize
  return tutors.slice(start, start + pageSize)
})

const nextPage = () => {
  if (page.value < totalPages.value) {
    page.value += 1
  }
}

const prevPage = () => {
  if (page.value > 1) {
    page.value -= 1
  }
}

const goToDetails = (id) => {
  router.push({
    name: 'tuteeSessionDetails',
    params: { id }
  })
}

const bookTutor = (id) => router.push({
  name: 'tutor-details',
  params: { id }
})
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

.dashboard-page {
  color: #163127;
}

.stat-card,
.recommendations-card,
.weekly-board-card {
  background:
    radial-gradient(circle at top right, rgba(111, 251, 190, 0.12), transparent 32%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), #ffffff);
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
  transition: background-color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
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

.custom-scrollbar::-webkit-scrollbar {
  height: 8px;
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #d6e2dd;
  border-radius: 999px;
}

.weekly-board-scroll {
  overflow-x: auto;
  overflow-y: hidden;
  padding-bottom: 4px;
}

.weekly-board-skeleton {
  overflow: hidden;
}

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

.day-column:nth-child(odd) .day-body {
  background: rgba(242, 244, 246, 0.42);
}

.day-column:nth-child(even) .day-body {
  background: #f2f4f6;
}

.day-column-today {
  border-radius: 18px;
}

.day-column-today .day-date {
  color: #0f172a;
}

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
  transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
  box-shadow: 0 1px 2px rgba(17, 24, 39, 0.08);
  min-width: 0;
  overflow: hidden;
}

.weekly-session-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 24px rgba(17, 24, 39, 0.08);
}

.weekly-session-card-upcoming {
  background: #f8fbff;
  border-left: 4px solid #0dcaf0;
}

.weekly-session-card-ongoing {
  background: #f5f9ff;
  border-left: 4px solid #0d6efd;
}

.weekly-session-card-completed {
  background: #f2fbf5;
  border-left: 4px solid #198754;
}

.weekly-session-card-verification {
  background: #fff7ed;
  border-left: 4px solid #f97316;
}

.weekly-session-card-pending {
  background: #fffbeb;
  border-left: 4px solid #fbbf24;
}

.weekly-session-card-payment-required {
  background: #fff1f2;
  border-left: 4px solid #ef4444;
}

.weekly-session-card-rejected {
  background: #fef2f2;
  border-left: 4px solid #dc2626;
}

.weekly-session-card-cancelled {
  background: #f9fafb;
  border-left: 4px solid #9ca3af;
}

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

.weekly-session-card-upcoming .weekly-session-status {
  background: rgba(13, 202, 240, 0.12);
  color: #087990;
}

.weekly-session-card-ongoing .weekly-session-status {
  background: rgba(13, 110, 253, 0.12);
  color: #0a58ca;
}

.weekly-session-card-completed .weekly-session-status {
  background: rgba(25, 135, 84, 0.12);
  color: #146c43;
}

.weekly-session-card-verification .weekly-session-status {
  background: rgba(249, 115, 22, 0.15);
  color: #c2410c;
}

.weekly-session-card-pending .weekly-session-status {
  background: rgba(251, 191, 36, 0.18);
  color: #92400e;
}

.weekly-session-card-payment-required .weekly-session-status {
  background: rgba(239, 68, 68, 0.12);
  color: #b91c1c;
}

.weekly-session-card-rejected .weekly-session-status {
  background: rgba(220, 38, 38, 0.12);
  color: #991b1b;
}

.weekly-session-card-cancelled .weekly-session-status {
  background: rgba(156, 163, 175, 0.18);
  color: #6b7280;
}

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

.day-empty-state i {
  font-size: 1rem;
}

.session-card-skeleton {
  width: 100%;
  padding: 0.75rem;
  border-radius: 16px;
  background: #ffffff;
  box-shadow: 0 8px 20px rgba(19, 41, 34, 0.04);
}

.tutor-list-item {
  cursor: pointer;
}

@media (max-width: 1199px) {
  .weekly-grid {
    grid-template-columns: repeat(7, minmax(118px, 1fr));
    min-width: 860px;
  }
}

@media (max-width: 991px) {
  .week-range-pill {
    min-width: 160px;
  }
}

@media (max-width: 767px) {
  .dashboard-page {
    padding-left: 0 !important;
    padding-right: 0 !important;
  }

  .weekly-grid {
    grid-template-columns: repeat(7, minmax(150px, 1fr));
    min-width: 1080px;
  }

  .weekly-board-header {
    align-items: flex-start !important;
  }
}
</style>
