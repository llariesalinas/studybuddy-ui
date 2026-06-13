<template>
  <div class="dashboard-shell">
    <div class="dashboard-content">
      <section class="metrics-grid" aria-label="Session summary">
        <article
          v-for="(stat, index) in stats"
          :key="index"
          class="glass-panel metric-card"
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
                    <article
                      v-for="session in daySessionsMap[day.key]"
                      :key="session.id"
                      class="weekly-session-card sb-interactive"
                      :class="[
                        getWeeklySessionCardClasses(session.status),
                        { 'weekly-session-card-dismissible': canDismissDashboardPill(session) }
                      ]"
                      role="button"
                      tabindex="0"
                      :aria-label="getSessionCardAriaLabel(session)"
                      @click="goToDetails(session.id)"
                      @keydown.enter.prevent="goToDetails(session.id)"
                      @keydown.space.prevent="goToDetails(session.id)"
                    >
                      <p class="weekly-session-time">{{ formatSessionTime(session) }}</p>
                      <p class="weekly-session-tutor">{{ session.tutor }}</p>

                      <div class="weekly-session-popout">
                        <p class="weekly-session-popout-time">{{ formatSessionTime(session) }}</p>
                        <h3 class="weekly-session-title">{{ session.subject }}</h3>
                        <div class="weekly-session-detail-grid">
                          <span class="weekly-session-detail-row">
                            <strong>Tutor</strong>
                            <span>{{ session.tutor }}</span>
                          </span>
                          <span class="weekly-session-detail-row">
                            <strong>Slots</strong>
                            <span>{{ getSessionSlotLabel(session) }}</span>
                          </span>
                          <span class="weekly-session-detail-row">
                            <strong>Mode</strong>
                            <span>{{ session.session_mode || 'Online' }}</span>
                          </span>
                          <span class="weekly-session-detail-row">
                            <strong>Location</strong>
                            <span>{{ getSessionLocationLabel(session) }}</span>
                          </span>
                        </div>
                        <span class="weekly-session-status" :title="session.status">{{ session.status }}</span>

                        <button
                          v-if="canDismissDashboardPill(session)"
                          type="button"
                          class="weekly-session-dismiss-btn sb-btn"
                          :aria-label="`Remove ${session.status} schedule pill for ${session.subject}`"
                          @click.stop="openDismissPillDialog(session)"
                        >
                          <i class="bi bi-trash3" aria-hidden="true"></i>
                          <span>Remove schedule pill</span>
                        </button>
                      </div>
                    </article>

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
              <p class="panel-subtitle">Recommended for your courses.</p>
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
                  <div v-if="featuredTutors.length === 0" class="recommendation-empty">
                    No recommended tutors available at the moment.
                  </div>

                  <button
                    v-for="tutor in featuredTutors"
                    :key="tutor.id"
                    type="button"
                    class="tutor-list-item sb-interactive"
                    @click="bookTutor(tutor.id)"
                  >
                    <span class="tutor-avatar" aria-hidden="true">{{ getTutorInitials(tutor) }}</span>
                    <span class="tutor-copy">
                      <span class="tutor-name">{{ tutor.name }}</span>
                      <span class="tutor-meta" :title="getTutorMetaTitle(tutor)">
                        <span class="tutor-rating">
                          <i class="bi bi-star-fill" aria-hidden="true"></i>
                          {{ getTutorRatingLabel(tutor) }}
                        </span>
                        <span class="tutor-meta-dot" aria-hidden="true">•</span>
                        <span class="tutor-subject">{{ getTutorPrimarySubject(tutor) }}</span>
                      </span>
                    </span>
                    <span class="tutor-rate">
                      <span>PHP</span>
                      <strong>{{ tutor.hourlyRate || 0 }}/hr</strong>
                    </span>
                  </button>
                </div>

                <div v-if="hasMoreRecommendations" class="recommendation-more">
                  <button type="button" class="recommendation-more-btn sb-btn" @click="viewMoreTutors">
                    View More Recommendations
                  </button>
                </div>
              </div>
            </Transition>
          </div>
        </aside>
      </section>
    </div>

    <Teleport to="body">
      <Transition name="fade">
        <div
          v-if="dismissDialogSession"
          class="dashboard-modal-backdrop"
          @click.self="closeDismissPillDialog"
        >
          <section
            class="dashboard-confirm-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="dismiss-pill-title"
          >
            <div class="dashboard-confirm-icon" aria-hidden="true">
              <i class="bi bi-trash3"></i>
            </div>
            <div class="dashboard-confirm-copy">
              <h2 id="dismiss-pill-title">Remove schedule pill?</h2>
              <p>
                This hides the {{ dismissDialogSession.status }} pill from your dashboard only.
                Session history and details stay available.
              </p>
              <p v-if="dismissPillError" class="dashboard-confirm-error">{{ dismissPillError }}</p>
            </div>
            <div class="dashboard-confirm-actions">
              <button
                type="button"
                class="dashboard-confirm-secondary sb-btn"
                :disabled="dismissPillPending"
                @click="closeDismissPillDialog"
              >
                Cancel
              </button>
              <button
                type="button"
                class="dashboard-confirm-danger sb-btn"
                :disabled="dismissPillPending"
                @click="confirmDismissDashboardPill"
              >
                {{ dismissPillPending ? 'Removing...' : 'Remove pill' }}
              </button>
            </div>
          </section>
        </div>
      </Transition>
    </Teleport>
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
const dismissDialogSession = ref(null)
const dismissPillPending = ref(false)
const dismissPillError = ref('')

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
        && !session.dashboard_hidden_by_current_user
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

const getSessionDurationLabel = (session) => {
  const minutes = getSessionDurationMinutes(session)

  if (minutes < 60) {
    return `${minutes} mins`
  }

  const hours = minutes / 60
  return `${Number.isInteger(hours) ? hours : hours.toFixed(1)} hr${hours === 1 ? '' : 's'}`
}

const getSessionSlotLabel = (session) => {
  const slots = getSessionSlotSpan(session)
  return `${slots} slot${slots === 1 ? '' : 's'} / ${getSessionDurationLabel(session)}`
}

const getSessionLocationLabel = (session) => (
  session?.preferred_location
  || (session?.session_mode === 'F2F' ? 'No location set' : 'Online')
)

const getSessionCardAriaLabel = (session) => (
  `${formatSessionTime(session)} with ${session.tutor}. ${session.subject}. ${session.status}. Click for full session information.`
)

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

const canDismissDashboardPill = (session) => {
  const status = String(session?.status || '').toLowerCase()
  return ['rejected', 'cancelled'].includes(status) && !session?.dashboard_hidden_by_current_user
}

const openDismissPillDialog = (session) => {
  dismissDialogSession.value = session
  dismissPillError.value = ''
}

const closeDismissPillDialog = () => {
  if (dismissPillPending.value) {
    return
  }

  dismissDialogSession.value = null
  dismissPillError.value = ''
}

const confirmDismissDashboardPill = async () => {
  if (!dismissDialogSession.value) {
    return
  }

  dismissPillPending.value = true
  dismissPillError.value = ''

  try {
    await sessionsStore.dismissDashboardPill(dismissDialogSession.value.id)
    dismissDialogSession.value = null
  } catch (error) {
    console.error('Failed to remove dashboard pill:', error)
    dismissPillError.value = 'Could not remove this pill right now. Please try again.'
  } finally {
    dismissPillPending.value = false
  }
}

const getTutorSubjects = (tutor) => (
  Array.isArray(tutor?.subjects)
    ? tutor.subjects.filter(Boolean)
    : []
)

const getTutorInitials = (tutor) => {
  const name = String(tutor?.name || 'Tutor').trim()
  const parts = name.split(/\s+/).filter(Boolean)

  return parts
    .slice(0, 2)
    .map((part) => part.charAt(0).toUpperCase())
    .join('') || 'T'
}

const getTutorRatingLabel = (tutor) => tutor?.rating || 'N/A'

const getTutorPrimarySubject = (tutor) => getTutorSubjects(tutor)[0] || 'Various subjects'


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

const featuredTutorLimit = 5

const featuredTutors = computed(() => {
  const tutors = sessionsStore.recommendedTutors || []
  return tutors.slice(0, featuredTutorLimit)
})

const hasMoreRecommendations = computed(() => (
  (sessionsStore.recommendedTutors?.length || 0) > featuredTutorLimit
))

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

const viewMoreTutors = () => router.push({ name: 'tutors' })
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
  min-height: 0;
  overflow: visible;
  padding: 0;
  color: var(--sb-ink);
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: transparent;
}

.dashboard-content {
  position: relative;
  z-index: 1;
  display: grid;
  gap: 1rem;
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
}

.glass-panel {
  border: 1px solid var(--sb-card-border);
  border-radius: 18px;
  background: color-mix(in srgb, var(--sb-card-bg) 96%, var(--sb-bg));
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-height: 86px;
  padding: 0.85rem;
}

.metric-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  flex: 0 0 auto;
  border-radius: 14px;
  background: rgba(0, 137, 90, 0.1);
  color: var(--sb-primary);
  font-size: 1.18rem;
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
  min-height: 1.7rem;
  color: var(--sb-ink);
  font-size: 1.55rem;
  font-weight: 850;
  line-height: 1;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(300px, 0.34fr);
  gap: 1rem;
  align-items: stretch;
}

.weekly-panel,
.recommendation-panel {
  display: flex;
  flex-direction: column;
  height: clamp(460px, calc(100vh - 230px), 600px);
  min-height: 0;
  padding: 1rem;
  overflow: hidden;
}

.weekly-panel {
  overflow: visible;
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.9rem;
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
  font-size: 1.18rem;
  font-weight: 850;
  letter-spacing: 0;
}

.panel-subtitle {
  max-width: 620px;
  margin: 0.2rem 0 0;
  color: var(--sb-muted);
  font-size: 0.82rem;
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
  min-height: 0;
  overflow: visible;
  padding-bottom: 0;
}

.weekly-board-skeleton {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.weekly-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 0.5rem;
  min-width: 0;
  align-items: start;
}

.day-column {
  display: grid;
  grid-template-rows: auto 1fr;
  min-height: 320px;
  min-width: 0;
  border: 1px solid var(--sb-card-border);
  border-radius: 20px;
  background: transparent;
  overflow: visible;
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
  padding: 0.65rem 0.45rem;
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
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  padding: 0.5rem;
  min-height: 0;
  overflow: visible;
  min-width: 0;
  background: color-mix(in srgb, var(--sb-bg) 76%, var(--sb-card-bg));
}

.weekly-session-card {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  width: 100%;
  height: 58px;
  min-height: 58px;
  max-height: 58px;
  border: 1px solid transparent;
  border-radius: 14px;
  padding: 0.56rem;
  text-align: left;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, background-color 0.18s ease;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
  min-width: 0;
  overflow: visible;
  cursor: pointer;
}

.weekly-session-card:hover {
  z-index: 10;
  box-shadow: 0 0 0 1px rgba(0, 137, 90, 0.18),
              0 3px 8px rgba(15, 23, 42, 0.05);
}

.weekly-session-card:focus-visible {
  outline: 2px solid color-mix(in srgb, var(--sb-primary) 72%, white);
  outline-offset: 2px;
}

.weekly-session-card-dismissible .weekly-session-time {
  padding-right: 0;
}

.weekly-session-popout {
  position: absolute;
  left: 50%;
  top: calc(100% + 0.45rem);
  z-index: 20;
  width: min(240px, calc(100vw - 40px));
  border: 1px solid var(--sb-card-border);
  border-radius: 14px;
  background: var(--sb-card-bg);
  box-shadow: 0 18px 48px rgba(15, 23, 42, 0.16);
  padding: 0.75rem;
  opacity: 0;
  visibility: hidden;
  transform: translate(-50%, -4px) scale(0.98);
  transition:
    opacity 0.18s ease 0.2s,
    transform 0.18s ease 0.2s,
    visibility 0s linear 0.38s;
}

.weekly-session-card:hover .weekly-session-popout,
.weekly-session-card:focus-within .weekly-session-popout,
.weekly-session-card:focus-visible .weekly-session-popout {
  opacity: 1;
  visibility: visible;
  transform: translate(-50%, 0) scale(1);
  transition-delay: 0s;
}

.weekly-session-popout::before {
  content: "";
  position: absolute;
  left: 50%;
  top: -7px;
  width: 12px;
  height: 12px;
  border-left: 1px solid var(--sb-card-border);
  border-top: 1px solid var(--sb-card-border);
  background: var(--sb-card-bg);
  transform: translateX(-50%) rotate(45deg);
}

.day-column:nth-child(n + 6) .weekly-session-popout {
  right: 0;
  left: auto;
  transform: translateY(-4px) scale(0.98);
}

.day-column:nth-child(n + 6) .weekly-session-card:hover .weekly-session-popout,
.day-column:nth-child(n + 6) .weekly-session-card:focus-within .weekly-session-popout,
.day-column:nth-child(n + 6) .weekly-session-card:focus-visible .weekly-session-popout {
  transform: translateY(0) scale(1);
}

.day-column:nth-child(n + 6) .weekly-session-popout::before {
  right: 1rem;
  left: auto;
  transform: rotate(45deg);
}

.weekly-session-popout-time {
  margin: 0 0 0.25rem;
  color: #006c49;
  font-size: 0.62rem;
  font-weight: 900;
  letter-spacing: 0;
  text-transform: uppercase;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.weekly-session-detail-grid {
  display: grid;
  gap: 0.38rem;
}

.weekly-session-detail-row {
  display: flex;
  justify-content: space-between;
  gap: 0.65rem;
  min-width: 0;
  color: var(--sb-muted);
  font-size: 0.68rem;
  line-height: 1.25;
}

.weekly-session-detail-row strong {
  flex: 0 0 auto;
  color: var(--sb-ink);
  font-size: 0.6rem;
  font-weight: 850;
  text-transform: uppercase;
}

.weekly-session-detail-row span {
  min-width: 0;
  text-align: right;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.weekly-session-popout .weekly-session-dismiss-btn {
  position: static;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  width: 100%;
  min-height: 30px;
  margin-top: 0.65rem;
  border: 1px solid #dc2626;
  border-radius: 999px;
  background: transparent;
  color: #b91c1c;
  padding: 0.3rem 0.55rem;
  font-size: 0.68rem;
  font-weight: 850;
  line-height: 1;
  transition: opacity 0.15s ease, transform 0.15s ease, background-color 0.15s ease;
}

.weekly-session-popout .weekly-session-status {
  flex: 0 0 auto;
  max-width: 100%;
  margin-top: 0.5rem;
  padding: 0.16rem 0.5rem;
  font-size: 0.6rem;
}

.weekly-session-dismiss-btn:hover,
.weekly-session-dismiss-btn:focus-visible {
  background: #fee2e2;
  color: #991b1b;
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
  flex: 1 1 auto;
  min-width: 0;
  max-width: min(100%, 58px);
  min-height: 20px;
  padding: 0.08rem 0.36rem;
  border-radius: 999px;
  background: var(--sb-bg);
  font-size: 0.54rem;
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
  -webkit-line-clamp: 2;
  margin: 0 0 0.2rem;
  font-size: 0.68rem;
  font-weight: 800;
  line-height: 1.25;
  color: var(--sb-ink);
  overflow: hidden;
  word-break: break-word;
}

.weekly-session-time {
  margin: 0 0 0.32rem;
  font-size: 0.58rem;
  font-weight: 800;
  color: #006c49;
  letter-spacing: 0;
  text-transform: uppercase;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.weekly-session-tutor {
  margin: 0 0 0.36rem;
  font-size: 0.62rem;
  color: var(--sb-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.weekly-session-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.25rem;
  min-width: 0;
  margin-top: auto;
  width: 100%;
}

.weekly-session-duration {
  font-size: 0.54rem;
  font-weight: 700;
  color: var(--sb-muted);
  flex: 0 0 auto;
  white-space: nowrap;
}

.dashboard-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1080;
  display: grid;
  place-items: center;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.36);
  backdrop-filter: blur(8px);
}

.dashboard-confirm-modal {
  width: min(100%, 390px);
  border: 1px solid var(--sb-card-border);
  border-radius: 18px;
  background: var(--sb-card-bg);
  color: var(--sb-ink);
  box-shadow: 0 24px 64px rgba(15, 23, 42, 0.22);
  padding: 1.15rem;
}

.dashboard-confirm-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.35rem;
  height: 2.35rem;
  border-radius: 999px;
  background: #fee2e2;
  color: #b91c1c;
  margin-bottom: 0.85rem;
}

.dashboard-confirm-copy h2 {
  margin: 0 0 0.45rem;
  color: var(--sb-ink);
  font-size: 1.05rem;
  font-weight: 850;
  letter-spacing: 0;
}

.dashboard-confirm-copy p {
  margin: 0;
  color: var(--sb-muted);
  font-size: 0.88rem;
  line-height: 1.45;
}

.dashboard-confirm-error {
  margin-top: 0.65rem !important;
  color: #b91c1c !important;
  font-weight: 750;
}

.dashboard-confirm-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.65rem;
  margin-top: 1rem;
}

.dashboard-confirm-secondary,
.dashboard-confirm-danger {
  min-height: 36px;
  border-radius: 999px;
  padding: 0.48rem 0.85rem;
  font-size: 0.82rem;
  font-weight: 800;
}

.dashboard-confirm-secondary {
  border: 1px solid var(--sb-card-border);
  background: var(--sb-card-bg);
  color: var(--sb-muted);
}

.dashboard-confirm-danger {
  border: 1px solid #dc2626;
  background: #dc2626;
  color: #fff;
}

.dashboard-confirm-secondary:disabled,
.dashboard-confirm-danger:disabled {
  opacity: 0.68;
  cursor: not-allowed;
}

:global([data-sb-theme="dark"]) .weekly-session-dismiss-btn {
  border-color: rgba(248, 113, 113, 0.35);
  background: rgba(15, 23, 42, 0.72);
  color: #fecaca;
}

:global([data-sb-theme="dark"]) .weekly-session-popout {
  background: #0b241c;
  border-color: #1d4537;
  box-shadow: 0 20px 54px rgba(2, 18, 13, 0.34);
}

:global([data-sb-theme="dark"]) .weekly-session-popout::before {
  background: #0b241c;
  border-color: #1d4537;
}

:global([data-sb-theme="dark"]) .weekly-session-popout-time {
  color: #8ee4bf;
}

:global([data-sb-theme="dark"]) .weekly-session-detail-row {
  color: #a8bbb3;
}

:global([data-sb-theme="dark"]) .weekly-session-detail-row strong {
  color: #f3f7f5;
}

:global([data-sb-theme="dark"]) .weekly-session-dismiss-btn:hover,
:global([data-sb-theme="dark"]) .weekly-session-dismiss-btn:focus-visible {
  background: rgba(127, 29, 29, 0.78);
  color: #fff;
}

:global([data-sb-theme="dark"]) .dashboard-modal-backdrop {
  background: rgba(2, 6, 23, 0.58);
}

:global([data-sb-theme="dark"]) .dashboard-confirm-icon {
  background: rgba(127, 29, 29, 0.42);
  color: #fecaca;
}

:global([data-sb-theme="dark"]) .dashboard-confirm-error {
  color: #fca5a5 !important;
}


.day-empty-state {
  width: 100%;
  min-height: 82px;
  flex-grow: 1;
  border: 1px dashed var(--sb-card-border);
  border-radius: 14px;
  background: color-mix(in srgb, var(--sb-card-bg) 72%, transparent);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.38rem;
  padding: 0.55rem;
  text-align: center;
  color: var(--sb-muted);
  font-size: 0.58rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0;
}

.day-empty-state i {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.2rem;
  height: 1.2rem;
  font-size: 1rem;
  line-height: 1;
}

.day-empty-state span {
  display: block;
  max-width: 100%;
  line-height: 1.25;
}

.session-card-skeleton {
  width: 100%;
  padding: 0.75rem;
  border-radius: 16px;
  background: var(--sb-card-bg);
  box-shadow: 0 8px 20px rgba(19, 41, 34, 0.04);
}

.recommendation-header {
  margin-bottom: 0.8rem;
}

.recommendation-panel {
  --recommendation-panel-bg: color-mix(in srgb, var(--sb-card-bg) 96%, var(--sb-bg));
  --recommendation-panel-border: var(--sb-card-border);
  --recommendation-card-bg: color-mix(in srgb, var(--sb-card-bg) 84%, transparent);
  --recommendation-card-border: color-mix(in srgb, var(--sb-card-border) 88%, var(--sb-primary));
  --recommendation-card-hover: color-mix(in srgb, var(--sb-card-bg) 94%, var(--sb-primary));
  --recommendation-title: var(--sb-ink);
  --recommendation-muted: var(--sb-muted);
  --recommendation-rate: var(--sb-primary);
  --recommendation-avatar-bg: var(--sb-green-tint);
  --recommendation-avatar-border: color-mix(in srgb, var(--sb-primary) 50%, var(--sb-card-border));
  --recommendation-divider: color-mix(in srgb, var(--sb-card-border) 92%, transparent);
  background: var(--recommendation-panel-bg);
  border-color: var(--recommendation-panel-border);
}

:global([data-sb-theme="dark"]) .recommendation-panel {
  --recommendation-panel-bg: #09231c;
  --recommendation-panel-border: #1f4d3c;
  --recommendation-card-bg: #172d25;
  --recommendation-card-border: #1f3b32;
  --recommendation-card-hover: #1b3a30;
  --recommendation-title: #f3f7f5;
  --recommendation-muted: #a7bbb3;
  --recommendation-rate: #a8e5cd;
  --recommendation-avatar-bg: #0b1815;
  --recommendation-avatar-border: #75b59c;
  --recommendation-divider: #1a332b;
  box-shadow: 0 12px 28px rgba(2, 18, 13, 0.2);
}

:global([data-sb-theme="dark"]) .recommendation-panel .panel-kicker {
  color: #789189;
}

:global([data-sb-theme="dark"]) .recommendation-panel .panel-title {
  color: var(--recommendation-title);
}

:global([data-sb-theme="dark"]) .recommendation-panel .panel-subtitle {
  color: #b6c8c0;
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
  gap: 0.5rem;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding-right: 0.1rem;
  scrollbar-gutter: stable;
  contain: paint;
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
  display: grid;
  grid-template-columns: 38px minmax(0, 1fr) minmax(54px, auto);
  align-items: center;
  gap: 0.55rem;
  width: 100%;
  height: 72px;
  min-height: 72px;
  max-height: 72px;
  border: 1px solid var(--recommendation-card-border);
  border-radius: 20px;
  background: var(--recommendation-card-bg);
  color: inherit;
  padding: 0.65rem;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.18s ease, background-color 0.18s ease, transform 0.18s ease;
}

.tutor-list-item:hover {
  border-color: color-mix(in srgb, var(--sb-primary) 30%, var(--sb-card-border));
  background: var(--recommendation-card-hover);
}

.tutor-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 2px solid var(--recommendation-avatar-border);
  border-radius: 50%;
  background: var(--recommendation-avatar-bg);
  color: var(--recommendation-rate);
  font-size: 0.7rem;
  font-weight: 900;
  line-height: 1;
  flex: 0 0 auto;
}

.tutor-copy {
  display: grid;
  gap: 0.18rem;
  min-width: 0;
  overflow: hidden;
}

.tutor-name {
  display: block;
  color: var(--recommendation-title);
  font-size: 0.88rem;
  font-weight: 850;
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tutor-meta {
  display: flex;
  align-items: center;
  gap: 0.24rem;
  min-width: 0;
  color: var(--recommendation-muted);
  font-size: 0.66rem;
  font-weight: 750;
  line-height: 1.25;
  overflow: hidden;
}

.tutor-rating {
  display: inline-flex;
  align-items: center;
  gap: 0.16rem;
  flex: 0 0 auto;
  color: #d99912;
  font-weight: 900;
  white-space: nowrap;
}

:global([data-sb-theme="dark"]) .tutor-rating {
  color: #ffc84d;
}

.tutor-rating i {
  font-size: 0.64rem;
  line-height: 1;
}

.tutor-meta-dot {
  color: var(--recommendation-muted);
  flex: 0 0 auto;
  opacity: 0.9;
}

.tutor-subject {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tutor-rate {
  display: grid;
  align-content: center;
  justify-items: end;
  flex: 0 0 auto;
  gap: 0.12rem;
  color: var(--recommendation-rate);
  font-weight: 900;
  min-width: 54px;
  white-space: nowrap;
}

.tutor-rate span {
  font-size: 0.64rem;
  line-height: 1;
}

.tutor-rate strong {
  font-size: 0.8rem;
  line-height: 1.15;
}

.recommendation-more {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  margin-top: 0.55rem;
  padding-top: 0.55rem;
  border-top: 1px solid var(--recommendation-divider);
}

.recommendation-more-btn {
  border: 0;
  background: transparent;
  color: var(--recommendation-muted);
  padding: 0.25rem 0;
  font-size: 0.8rem;
  font-weight: 850;
  text-align: center;
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

  .weekly-panel,
  .recommendation-panel {
    height: auto;
    max-height: none;
  }

  .weekly-grid {
    grid-template-columns: repeat(7, minmax(0, 1fr));
    min-width: 0;
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
    padding: 0;
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
    grid-template-columns: repeat(7, minmax(0, 1fr));
    min-width: 0;
  }

  .weekly-board-nav,
  .recommendation-more {
    width: 100%;
  }

  .week-range-pill {
    flex: 1;
    min-width: 0;
  }

  .tutor-list-item {
    grid-template-columns: 38px minmax(0, 1fr) minmax(54px, auto);
    height: 72px;
    min-height: 72px;
    max-height: 72px;
    padding: 0.65rem;
  }

  .recommendation-more-btn {
    width: 100%;
  }
}

/* Remove Animations and Hover Effects for Tutee Dashboard */

/* 1. Remove hover effects from interactive elements */
.week-range-pill:hover,
.schedule-nav-btn:hover:not(:disabled),
.weekly-session-card:hover,
.tutor-list-item:hover {
  transform: none !important;
  box-shadow: 0 1px 2px rgba(17, 24, 39, 0.06) !important; /* Restore base shadow, no hover shadow */
  background-color: inherit !important;
  border-color: inherit !important;
  color: inherit !important;
}

/* 2. Remove animations from elements */
.week-range-pill-current {
  animation: none !important;
}

.weekly-session-card {
  transition: none !important;
}

/* 3. Remove stagger animation from metric cards */
.metric-card {
  animation: none !important;
}
</style>
