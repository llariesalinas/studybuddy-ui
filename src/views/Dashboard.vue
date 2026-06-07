<template>
  <div class="dashboard-shell">
    <div class="dashboard-content">
      <section class="metrics-grid" aria-label="Session summary">
        <article
          v-for="(stat, index) in stats"
          :key="index"
          class="glass-panel metric-card sb-stagger-item"
          :style="{ animationDelay: `${index * 0.07}s` }"
        >
          <span class="metric-icon">
            <i :class="['bi', stat.icon]"></i>
          </span>
          <div class="metric-copy">
            <p class="metric-label">{{ stat.label }}</p>
            <Transition name="fade" mode="out-in">
              <span v-if="loading" class="metric-value placeholder-glow">
                <span class="placeholder col-6 rounded"></span>
              </span>
              <span v-else class="metric-value">{{ stat.count }}</span>
            </Transition>
          </div>
        </article>
      </section>

      <section class="dashboard-grid">
        <article class="glass-panel weekly-panel">
          <header class="panel-header weekly-board-header">
            <div class="panel-heading">
              <p class="panel-kicker">Weekly Schedule</p>
              <h2 class="panel-title">Your Sessions This Week</h2>
              <p class="panel-subtitle">
                Review your booked sessions across the week and open any session details in one click.
              </p>
            </div>

            <div class="weekly-board-nav" aria-label="Week navigation">
              <button
                type="button"
                class="schedule-nav-btn sb-btn"
                :disabled="!canGoToPreviousWeek"
                @click="goToPreviousWeek"
                aria-label="Previous week"
              >
                <i class="bi bi-chevron-left"></i>
              </button>
              <button
                type="button"
                class="week-range-pill sb-btn"
                :class="{ 'week-range-pill-current': isViewingCurrentWeek }"
                :aria-label="weekRangeAriaLabel"
                :aria-current="isViewingCurrentWeek ? 'date' : undefined"
                @click="goToCurrentWeek"
              >
                {{ formattedWeekRange }}
              </button>
              <button
                type="button"
                class="schedule-nav-btn sb-btn"
                :disabled="!canGoToNextWeek"
                @click="goToNextWeek"
                aria-label="Next week"
              >
                <i class="bi bi-chevron-right"></i>
              </button>
            </div>
          </header>

          <Transition name="fade" mode="out-in">
            <div v-if="loading" class="weekly-board-skeleton">
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

            <div v-else class="weekly-board-scroll custom-scrollbar">
              <div class="weekly-grid">
                <article
                  v-for="day in weekDays"
                  :key="day.key"
                  class="day-column"
                  :class="{ 'day-column-today': day.isToday }"
                >
                  <div class="day-header">
                    <p class="day-name">{{ day.shortName }}</p>
                    <p class="day-date">{{ day.date.getDate() }}</p>
                  </div>

                  <div class="day-body">
                    <button
                      v-for="session in daySessionsMap[day.key]"
                      :key="session.id"
                      type="button"
                      class="weekly-session-card sb-interactive"
                      :class="getWeeklySessionCardClasses(session.status)"
                      @click="goToDetails(session.id)"
                    >
                      <p class="weekly-session-time">{{ formatSessionTime(session) }}</p>
                      <h3 class="weekly-session-title">{{ session.subject }}</h3>
                      <p class="weekly-session-tutor">{{ session.tutor }}</p>
                      <div class="weekly-session-meta">
                        <span class="weekly-session-status">{{ session.status }}</span>
                        <span class="weekly-session-duration">
                          {{ getSessionSlotSpan(session) }} slot{{ getSessionSlotSpan(session) === 1 ? '' : 's' }}
                        </span>
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
        </article>

        <aside class="glass-panel recommendation-panel">
          <header class="panel-header recommendation-header">
            <div class="panel-heading">
              <p class="panel-kicker">Discover</p>
              <h2 class="panel-title">Try out these tutors</h2>
              <p class="panel-subtitle">Browse recommended tutors without leaving your dashboard rhythm.</p>
            </div>
          </header>

          <div class="recommendation-body">
            <Transition name="fade" mode="out-in">
              <div v-if="loading" class="recommendation-skeleton placeholder-glow">
                <div v-for="i in 5" :key="'skel-tutor-' + i" class="recommendation-skeleton-row">
                  <div class="skeleton-copy">
                    <span class="placeholder col-8 rounded"></span>
                    <span class="placeholder col-5 rounded"></span>
                  </div>
                  <span class="placeholder col-3 rounded"></span>
                </div>
              </div>

              <div v-else class="recommendation-list-wrap">
                <div class="recommendation-list">
                  <div v-if="pagedTutors.length === 0" class="recommendation-empty">
                    No recommended tutors available at the moment.
                  </div>

                  <button
                    v-for="tutor in pagedTutors"
                    :key="tutor.id"
                    type="button"
                    class="tutor-list-item sb-interactive"
                    @click="bookTutor(tutor.id)"
                  >
                    <span class="tutor-copy">
                      <span class="tutor-name">{{ tutor.name }}</span>
                      <span class="tutor-meta" :title="getTutorMetaTitle(tutor)">
                        {{ formatTutorMeta(tutor) }}
                      </span>
                    </span>
                    <span class="tutor-rate">PHP {{ tutor.hourlyRate || 0 }}/hr</span>
                  </button>
                </div>

                <div v-if="totalPages > 1" class="recommendation-pagination">
                  <button class="pagination-btn sb-btn" @click="prevPage" :disabled="page === 1">Prev</button>
                  <span class="pagination-label">Page {{ page }} of {{ totalPages || 1 }}</span>
                  <button class="pagination-btn sb-btn" @click="nextPage" :disabled="page >= totalPages">Next</button>
                </div>
              </div>
            </Transition>
          </div>
        </aside>
      </section>
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

const refreshDashboard = async () => {
  loading.value = true

  await Promise.all([
    sessionsStore.fetchSessions(),
    sessionsStore.fetchRecommendations()
  ])

  loading.value = false
}

onMounted(refreshDashboard)

watch(
  () => route.query.refresh,
  () => {
    refreshDashboard()
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

const visibleStartOfWeek = computed(() => addDays(baseStartOfWeek, weekOffset.value * 7))
const visibleEndOfWeek = computed(() => addDays(visibleStartOfWeek.value, 6))
const canGoToPreviousWeek = computed(() => weekOffset.value > minWeekOffset)
const canGoToNextWeek = computed(() => weekOffset.value < maxWeekOffset)
const isViewingCurrentWeek = computed(() => weekOffset.value === 0)

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

const weekRangeAriaLabel = computed(() => {
  if (isViewingCurrentWeek.value) {
    return `Current week, ${formattedWeekRange.value}`
  }

  return `Viewing week, ${formattedWeekRange.value}. Click to return to the current week.`
})

const goToCurrentWeek = () => {
  weekOffset.value = 0
}

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

const getTutorSubjects = (tutor) => (
  Array.isArray(tutor?.subjects)
    ? tutor.subjects.filter(Boolean)
    : []
)

const getTutorRatingLabel = (tutor) => tutor?.rating || 'N/A'

const formatTutorMeta = (tutor) => {
  const subjects = getTutorSubjects(tutor)
  const visibleSubjects = subjects.slice(0, 2).join(', ') || 'Various subjects'
  const remainingSubjects = subjects.length > 2 ? ` - +${subjects.length - 2} more` : ''

  return `Rating ${getTutorRatingLabel(tutor)} - ${visibleSubjects}${remainingSubjects}`
}

const getTutorMetaTitle = (tutor) => {
  const subjects = getTutorSubjects(tutor)
  const subjectList = subjects.length ? subjects.join(', ') : 'Various subjects'

  return `Rating ${getTutorRatingLabel(tutor)} - ${subjectList}`
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
const pageSize = 5

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
  transition: opacity 0.24s var(--sb-spring, cubic-bezier(0.16, 1, 0.3, 1));
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.dashboard-shell {
  --sb-primary: #00895a;
  --sb-primary-hover: #00704a;
  --sb-dark: #0a1916;
  --sb-ink: var(--sb-text-main);
  --sb-muted: var(--sb-text-muted);
  --sb-divider: var(--sb-card-border);
  --sb-green-tint: #edf7f3;
  --sb-green-border: #b8dece;
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  padding: 2rem;
  color: var(--sb-ink);
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: transparent;
}

.dashboard-content {
  position: relative;
  z-index: 1;
  display: grid;
  gap: 1.25rem;
  max-width: 1320px;
  margin: 0 auto;
}

.glass-panel {
  border: 1px solid var(--sb-card-border);
  border-radius: 24px;
  background: color-mix(in srgb, var(--sb-card-bg) 88%, transparent);
  box-shadow: 0 24px 70px rgba(15, 23, 42, 0.1);
  backdrop-filter: blur(24px);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  min-height: 104px;
  padding: 1rem;
}

.metric-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  flex: 0 0 auto;
  border-radius: 18px;
  background: rgba(0, 137, 90, 0.1);
  color: var(--sb-primary);
  font-size: 1.35rem;
}

.metric-copy {
  display: grid;
  gap: 0.15rem;
  min-width: 0;
}

.metric-label {
  margin: 0;
  color: var(--sb-muted);
  font-size: 0.75rem;
  font-weight: 850;
  text-transform: uppercase;
  letter-spacing: 0;
}

.metric-value {
  display: block;
  min-height: 2rem;
  color: var(--sb-ink);
  font-size: 1.85rem;
  font-weight: 850;
  line-height: 1;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(340px, 0.38fr);
  gap: 1.25rem;
  align-items: stretch;
}

.weekly-panel,
.recommendation-panel {
  display: flex;
  flex-direction: column;
  min-height: 560px;
  padding: 1.35rem;
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.2rem;
}

.panel-heading {
  min-width: 0;
}

.panel-kicker {
  margin: 0 0 0.35rem;
  color: var(--sb-muted);
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0;
}

.panel-title {
  margin: 0;
  color: var(--sb-ink);
  font-size: 1.4rem;
  font-weight: 850;
  letter-spacing: 0;
}

.panel-subtitle {
  max-width: 620px;
  margin: 0.3rem 0 0;
  color: var(--sb-muted);
  font-size: 0.9rem;
  line-height: 1.45;
}

.weekly-board-header {
  flex-wrap: wrap;
}

.weekly-board-nav {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  flex: 0 0 auto;
  border: 1px solid var(--sb-card-border);
  border-radius: 999px;
  background: var(--sb-bg);
  padding: 0.32rem;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.9);
}

.week-range-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 180px;
  min-height: 38px;
  padding: 0.45rem 0.85rem;
  border: 1px solid transparent;
  border-radius: 999px;
  background: var(--sb-card-bg);
  color: var(--sb-ink);
  font-family: inherit;
  font-size: 0.8rem;
  font-weight: 850;
  text-align: center;
  white-space: nowrap;
  user-select: none;
  box-shadow: 0 1px 2px rgba(17, 24, 39, 0.06);
  transition: border-color var(--sb-t-normal) var(--sb-spring),
              box-shadow var(--sb-t-normal) var(--sb-spring),
              color var(--sb-t-normal) var(--sb-spring);
}

.week-range-pill:hover {
  border-color: rgba(0, 137, 90, 0.24);
  color: var(--sb-primary);
  box-shadow: 0 0 0 3px rgba(0, 137, 90, 0.08),
              0 1px 2px rgba(17, 24, 39, 0.06);
}

.week-range-pill-current {
  color: var(--sb-primary);
  border: 1px solid rgba(0, 137, 90, 0.42);
  box-shadow: 0 0 0 3px rgba(0, 137, 90, 0.1),
              0 1px 2px rgba(17, 24, 39, 0.06);
  animation: current-week-ring 2.4s var(--sb-spring) infinite;
}

@keyframes current-week-ring {
  0% {
    box-shadow: 0 0 0 0 rgba(0, 137, 90, 0.2),
                0 1px 2px rgba(17, 24, 39, 0.06);
  }
  60% {
    box-shadow: 0 0 0 6px rgba(0, 137, 90, 0),
                0 1px 2px rgba(17, 24, 39, 0.06);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(0, 137, 90, 0),
                0 1px 2px rgba(17, 24, 39, 0.06);
  }
}

.schedule-nav-btn {
  width: 38px;
  height: 38px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: var(--sb-muted);
  transition: background-color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.schedule-nav-btn:hover:not(:disabled) {
  background: var(--sb-card-bg);
  color: var(--sb-ink);
  box-shadow: 0 1px 2px rgba(17, 24, 39, 0.08);
}

.schedule-nav-btn:disabled {
  color: var(--sb-text-subtle);
  background: var(--sb-bg);
  cursor: not-allowed;
}

.custom-scrollbar::-webkit-scrollbar {
  height: 8px;
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: var(--sb-card-border);
  border-radius: 999px;
}

.weekly-board-scroll {
  flex: 1;
  overflow-x: auto;
  overflow-y: hidden;
  padding-bottom: 4px;
}

.weekly-board-skeleton {
  flex: 1;
  overflow: hidden;
}

.weekly-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 0.7rem;
  min-width: 0;
  align-items: start;
}

.day-column {
  display: grid;
  grid-template-rows: auto 1fr;
  min-height: 380px;
  min-width: 0;
  border: 1px solid var(--sb-card-border);
  border-radius: 20px;
  background: transparent;
  overflow: hidden;
}

.day-column-today {
  border-color: rgba(0, 137, 90, 0.42);
  box-shadow: 0 0 0 3px rgba(0, 137, 90, 0.08);
}

.day-column-today .day-header {
  background: rgba(0, 137, 90, 0.1);
}

.day-column-today .day-name,
.day-column-today .day-date {
  color: var(--sb-primary);
}

.day-header {
  padding: 0.75rem 0.65rem;
  background: var(--sb-bg);
  text-align: center;
}

.day-name {
  margin: 0 0 0.25rem;
  font-size: 0.62rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0;
  color: var(--sb-muted);
}

.day-date {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 850;
  color: var(--sb-ink);
  line-height: 1;
}

.day-body {
  display: grid;
  align-content: start;
  gap: 0.55rem;
  padding: 0.65rem;
  min-height: 332px;
  overflow-y: auto;
  overflow-x: hidden;
  min-width: 0;
  background: color-mix(in srgb, var(--sb-bg) 76%, var(--sb-card-bg));
}

.weekly-session-card {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 150px;
  min-height: 150px;
  max-height: 150px;
  border: 1px solid transparent;
  border-radius: 16px;
  padding: 0.75rem;
  text-align: left;
  transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
  min-width: 0;
  overflow: hidden;
}

.weekly-session-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 24px rgba(17, 24, 39, 0.08);
}

.weekly-session-card-upcoming {
  background: #f8fbff;
  border-left: 4px solid #0ea5e9;
}

.weekly-session-card-ongoing {
  background: #f5f9ff;
  border-left: 4px solid #0d6efd;
}

.weekly-session-card-completed {
  background: #f2fbf5;
  border-left: 4px solid var(--sb-primary);
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
  min-width: 0;
  max-width: 100%;
  min-height: 22px;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
  background: var(--sb-bg);
  font-size: 0.58rem;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
  color: var(--sb-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  margin: 0 0 0.25rem;
  font-size: 0.72rem;
  font-weight: 800;
  line-height: 1.3;
  color: var(--sb-ink);
  overflow: hidden;
  word-break: break-word;
}

.weekly-session-time {
  margin: 0 0 0.45rem;
  font-size: 0.62rem;
  font-weight: 800;
  color: #006c49;
  letter-spacing: 0;
  text-transform: uppercase;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.weekly-session-tutor {
  margin: 0 0 0.55rem;
  font-size: 0.66rem;
  color: var(--sb-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.weekly-session-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  min-width: 0;
  margin-top: auto;
}

.weekly-session-duration {
  font-size: 0.58rem;
  font-weight: 700;
  color: var(--sb-muted);
  flex-shrink: 0;
  white-space: nowrap;
}


.day-empty-state {
  min-height: 110px;
  border: 1px dashed var(--sb-card-border);
  border-radius: 16px;
  background: color-mix(in srgb, var(--sb-card-bg) 72%, transparent);
  display: grid;
  place-items: center;
  gap: 0.45rem;
  padding: 0.75rem;
  text-align: center;
  color: var(--sb-muted);
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0;
}

.day-empty-state i {
  font-size: 1rem;
}

.session-card-skeleton {
  width: 100%;
  padding: 0.75rem;
  border-radius: 16px;
  background: var(--sb-card-bg);
  box-shadow: 0 8px 20px rgba(19, 41, 34, 0.04);
}

.recommendation-panel {
  min-height: 560px;
}

.recommendation-header {
  margin-bottom: 1rem;
}

.recommendation-body,
.recommendation-list-wrap {
  display: flex;
  flex: 1;
  min-height: 0;
  flex-direction: column;
}

.recommendation-list {
  display: grid;
  gap: 0.65rem;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding-right: 0.15rem;
}

.recommendation-empty {
  display: grid;
  min-height: 160px;
  place-items: center;
  border: 1px dashed var(--sb-card-border);
  border-radius: 18px;
  background: color-mix(in srgb, var(--sb-card-bg) 72%, transparent);
  color: var(--sb-muted);
  padding: 1rem;
  text-align: center;
  font-size: 0.9rem;
  font-weight: 700;
}

.tutor-list-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.9rem;
  width: 100%;
  height: 96px;
  min-height: 96px;
  max-height: 96px;
  border: 1px solid var(--sb-card-border);
  border-radius: 18px;
  background: color-mix(in srgb, var(--sb-card-bg) 78%, transparent);
  color: inherit;
  padding: 0.85rem;
  text-align: left;
  cursor: pointer;
}

.tutor-copy {
  display: grid;
  gap: 0.25rem;
  min-width: 0;
  overflow: hidden;
}

.tutor-name {
  display: block;
  color: var(--sb-ink);
  font-size: 0.96rem;
  font-weight: 850;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tutor-meta {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  color: var(--sb-muted);
  font-size: 0.78rem;
  font-weight: 650;
  line-height: 1.35;
  overflow: hidden;
}

.tutor-rate {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  min-height: 34px;
  border: 1px solid rgba(0, 137, 90, 0.24);
  border-radius: 999px;
  background: rgba(0, 137, 90, 0.09);
  color: #07543a;
  padding: 0.35rem 0.65rem;
  font-size: 0.78rem;
  font-weight: 850;
  min-width: 96px;
  white-space: nowrap;
}

.recommendation-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex: 0 0 auto;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--sb-card-border);
}

.pagination-btn {
  min-height: 36px;
  border: 0;
  border-radius: 999px;
  background: var(--sb-primary);
  color: #fff;
  padding: 0.5rem 0.85rem;
  font-size: 0.8rem;
  font-weight: 850;
}

.pagination-btn:disabled {
  background: var(--sb-card-border);
  color: var(--sb-muted);
  cursor: not-allowed;
}

.pagination-label {
  color: var(--sb-muted);
  font-size: 0.82rem;
  font-weight: 750;
}

.recommendation-skeleton {
  display: grid;
  gap: 0.65rem;
}

.recommendation-skeleton-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  min-height: 76px;
  border-radius: 18px;
  background: color-mix(in srgb, var(--sb-card-bg) 78%, transparent);
  padding: 0.85rem;
}

.skeleton-copy {
  display: grid;
  gap: 0.5rem;
  width: 70%;
}

@media (max-width: 1199px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .weekly-grid {
    grid-template-columns: repeat(7, minmax(118px, 1fr));
    min-width: 860px;
  }
}

@media (max-width: 991px) {
  .metrics-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .panel-header {
    flex-direction: column;
  }

  .week-range-pill {
    min-width: 160px;
  }
}

@media (max-width: 767px) {
  .dashboard-shell {
    padding: 1rem;
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .glass-panel {
    border-radius: 18px;
  }

  .weekly-panel,
  .recommendation-panel {
    padding: 1rem;
  }

  .weekly-grid {
    grid-template-columns: repeat(7, minmax(150px, 1fr));
    min-width: 1080px;
  }

  .weekly-board-nav,
  .recommendation-pagination {
    width: 100%;
  }

  .week-range-pill {
    flex: 1;
    min-width: 0;
  }

  .tutor-list-item {
    align-items: flex-start;
    flex-direction: column;
    height: 132px;
    min-height: 132px;
    max-height: 132px;
  }

  .tutor-rate,
  .pagination-btn {
    width: 100%;
  }
}
</style>
