<template>
  <div class="p-4">
    <div class="row g-4 mb-5">
      <div v-for="(stat, index) in stats" :key="index" class="col-md-3">
        <div class="card border-sb shadow-sm rounded-4 h-100 p-3 d-flex flex-row align-items-center">
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

    <div class="row g-4">
      <div class="col-md-8">
        <div class="card border-sb border-1 shadow-sm rounded-4" style="height: 520px;">
          <div class="card-body p-4 p-md-4 d-flex flex-column h-100 overflow-hidden">
            <header class="d-flex justify-content-between align-items-end mb-4 flex-shrink-0">
              <div>
                <h4 class="fw-bold mb-1 d-flex align-items-center">
                  <i class="bi bi-file-earmark-text text-sb-primary me-3"></i>This week's schedule
                </h4>
              </div>
              <div class="d-flex align-items-center gap-2">
                <button
                  type="button"
                  class="schedule-nav-btn"
                  :disabled="selectedDayIndex === 0"
                  @click="goToPreviousDay"
                  aria-label="Previous day"
                >
                  <i class="bi bi-chevron-left"></i>
                </button>
                <p class="text-muted mb-0 small schedule-date-label">{{ formattedSelectedDate }}</p>
                <button
                  type="button"
                  class="schedule-nav-btn"
                  :disabled="selectedDayIndex === 6"
                  @click="goToNextDay"
                  aria-label="Next day"
                >
                  <i class="bi bi-chevron-right"></i>
                </button>
              </div>
            </header>

            <Transition name="fade" mode="out-in">
              <div v-if="loading" class="flex-grow-1 w-100 placeholder-glow overflow-hidden">
                <div class="d-flex position-relative w-100 h-100">
                  <div class="d-flex flex-column text-end pe-3 border-end" style="width: 90px; justify-content: space-between;">
                    <div v-for="i in 4" :key="'skel-time-' + i" style="height: 80px;">
                      <span class="placeholder col-10 rounded"></span>
                    </div>
                  </div>
                  <div class="flex-grow-1 ms-3 position-relative">
                    <div v-for="i in 4" :key="'skel-line-' + i" class="border-bottom w-100 opacity-25" style="height: 80px;"></div>
                    <div class="position-absolute start-0 w-100 rounded-4 p-3 bg-secondary bg-opacity-10 border-start border-4 border-secondary" style="top: 30px; height: 90px;">
                      <span class="placeholder col-3 rounded mb-2"></span><br>
                      <span class="placeholder col-6 rounded"></span>
                    </div>
                    <div class="position-absolute start-0 w-100 rounded-4 p-3 bg-secondary bg-opacity-10 border-start border-4 border-secondary" style="top: 180px; height: 70px;">
                      <span class="placeholder col-2 rounded mb-2"></span><br>
                      <span class="placeholder col-5 rounded"></span>
                    </div>
                  </div>
                </div>
              </div>

              <div v-else class="flex-grow-1 overflow-auto pe-2 custom-scrollbar">
                <div class="d-flex position-relative mt-2 w-100" :style="{ minHeight: `${agendaRange.timeLabels.length * HOUR_ROW_HEIGHT}px` }">
                  <div
                    class="d-flex flex-column text-end pe-3 border-end text-muted small fw-bold text-uppercase"
                    style="width: 90px; justify-content: space-between; font-size: 0.7rem;"
                  >
                    <div v-for="hour in agendaRange.timeLabels" :key="hour" :style="{ height: `${HOUR_ROW_HEIGHT}px` }">
                      {{ formatHour(hour) }}
                    </div>
                  </div>

                  <div class="position-relative flex-grow-1 ms-3">
                    <div class="position-absolute w-100 h-100 d-flex flex-column justify-content-between pointer-events-none" style="z-index: 0;">
                      <div
                        v-for="hour in agendaRange.timeLabels"
                        :key="'line-' + hour"
                        class="border-bottom w-100 opacity-25"
                        :style="{ height: `${HOUR_ROW_HEIGHT}px` }"
                      ></div>
                    </div>

                    <div
                      v-for="session in selectedScheduleCards"
                      :key="session.id"
                      class="position-absolute border-start border-4 rounded-4 p-3 d-flex justify-content-between align-items-start shadow-sm session-card"
                      :class="getSessionCardClasses(session.status)"
                      :style="getSessionStyle(session)"
                      @click="goToDetails(session.id)"
                    >
                      <div class="flex-grow-1 min-w-0">
                        <div class="d-flex align-items-center gap-2 mb-1">
                          <span
                            v-if="session.status.toLowerCase() === 'ongoing'"
                            class="spinner-grow spinner-grow-sm text-warning"
                            style="width: 8px; height: 8px;"
                          ></span>
                          <span class="fw-bold text-uppercase session-card-label">{{ session.status }}</span>
                        </div>
                        <h6 class="fw-bold text-dark mb-1 session-card-title">{{ session.subject }}</h6>
                        <p class="text-muted small mb-0 session-card-meta">
                          {{ session.startTime }} - {{ session.endTime }} | {{ session.tutor }}
                        </p>
                      </div>

                      <i v-if="session.status.toLowerCase() === 'completed'" class="bi bi-check-circle-fill text-success fs-5 ms-2"></i>
                      <i v-else-if="session.status.toLowerCase() === 'ongoing'" class="bi bi-play-circle-fill text-warning fs-5 ms-2"></i>
                      <i v-else class="bi bi-calendar-event text-primary fs-5 ms-2"></i>
                    </div>

                    <div v-if="selectedScheduleCards.length === 0" class="h-100 d-flex align-items-center justify-content-center text-center text-muted small px-4">
                      No sessions scheduled for {{ selectedDayName.toLowerCase() }}.
                    </div>
                  </div>
                </div>
              </div>
            </Transition>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card border-sb shadow-sm rounded-4" style="height: 520px;">
          <div class="card-body p-4 d-flex flex-column" style="height: 100%;">
            <h4 class="fw-bold mb-3">Try out these tutors</h4>

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
                        class="list-group-item d-flex justify-content-between align-items-center py-2"
                        @click="bookTutor(tutor.id)"
                        style="cursor: pointer;"
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionsStore } from '@/stores/completedSessions'

const HOUR_ROW_HEIGHT = 80
const MIN_SESSION_CARD_HEIGHT = 76

const router = useRouter()
const sessionsStore = useSessionsStore()
const loading = ref(false)
const selectedDayIndex = ref(0)

onMounted(async () => {
  loading.value = true

  await Promise.all([
    sessionsStore.fetchSessions(),
    sessionsStore.fetchRecommendations()
  ])

  loading.value = false
})

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

const getDateKey = (date) => `${date.getFullYear()}-${padNumber(date.getMonth() + 1)}-${padNumber(date.getDate())}`

const now = new Date()
const startOfWeek = getStartOfWeek(now)
selectedDayIndex.value = Math.max(0, Math.min(6, (now.getDay() + 6) % 7))

const weekDays = computed(() =>
  Array.from({ length: 7 }, (_, index) => {
    const date = new Date(startOfWeek)
    date.setDate(startOfWeek.getDate() + index)

    return {
      index,
      date,
      key: getDateKey(date),
      dayName: date.toLocaleDateString('en-US', { weekday: 'long' }),
      label: date.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })
    }
  })
)

const selectedWeekDay = computed(() => weekDays.value[selectedDayIndex.value] || weekDays.value[0])
const selectedDateKey = computed(() => selectedWeekDay.value?.key || '')
const selectedDayName = computed(() => selectedWeekDay.value?.dayName || 'Today')
const formattedSelectedDate = computed(() => selectedWeekDay.value?.label || '')

const selectedDaySessions = computed(() => {
  const allSessions = sessionsStore.sessions || []

  return allSessions
    .filter((session) => session.date === selectedDateKey.value && !['pending', 'cancelled', 'rejected'].includes(session?.status?.toLowerCase()))
    .sort((left, right) => {
      const startDifference = parseTimeToMinutes(left.startTime) - parseTimeToMinutes(right.startTime)

      if (startDifference !== 0) {
        return startDifference
      }

      return parseTimeToMinutes(left.endTime) - parseTimeToMinutes(right.endTime)
    })
})

const agendaRange = computed(() => {
  if (selectedDaySessions.value.length === 0) {
    return { start: 9, end: 17, timeLabels: [9, 10, 11, 12, 13, 14, 15, 16, 17] }
  }

  const hours = selectedDaySessions.value.flatMap((session) => [
    Math.floor(parseTimeToMinutes(session.startTime) / 60),
    Math.ceil(parseTimeToMinutes(session.endTime) / 60)
  ])

  const start = Math.max(0, Math.min(...hours) - 1)
  const end = Math.min(23, Math.max(...hours) + 1)
  const timeLabels = []

  for (let hour = start; hour <= end; hour += 1) {
    timeLabels.push(hour)
  }

  return { start, end, timeLabels }
})

const formatHour = (hourValue) => {
  const suffix = hourValue >= 12 ? 'PM' : 'AM'
  const hour = hourValue % 12 || 12
  return `${String(hour).padStart(2, '0')}:00 ${suffix}`
}

const selectedScheduleCards = computed(() => {
  const laneEndTimes = []

  const cards = selectedDaySessions.value.map((session) => {
    const sessionStartMins = parseTimeToMinutes(session.startTime)
    const sessionEndMins = parseTimeToMinutes(session.endTime)

    let lane = laneEndTimes.findIndex((endTime) => endTime <= sessionStartMins)

    if (lane === -1) {
      lane = laneEndTimes.length
      laneEndTimes.push(sessionEndMins)
    } else {
      laneEndTimes[lane] = sessionEndMins
    }

    return {
      ...session,
      lane,
      top: ((sessionStartMins - (agendaRange.value.start * 60)) / 60) * HOUR_ROW_HEIGHT,
      height: Math.max(((sessionEndMins - sessionStartMins) / 60) * HOUR_ROW_HEIGHT, MIN_SESSION_CARD_HEIGHT),
    }
  })

  return cards.map((card) => {
    const overlappingCards = cards.filter((otherCard) =>
      parseTimeToMinutes(otherCard.startTime) < parseTimeToMinutes(card.endTime)
      && parseTimeToMinutes(otherCard.endTime) > parseTimeToMinutes(card.startTime)
    )

    return {
      ...card,
      laneCount: Math.max(...overlappingCards.map((otherCard) => otherCard.lane + 1), 1),
    }
  })
})

const getSessionCardClasses = (status) => {
  const normalizedStatus = String(status || '').toLowerCase()

  if (normalizedStatus === 'completed') {
    return 'bg-success bg-opacity-10 border-success'
  }

  if (normalizedStatus === 'ongoing') {
    return 'bg-warning bg-opacity-10 border-warning'
  }

  if (normalizedStatus === 'awaiting verification' || normalizedStatus === 'payment required') {
    return 'bg-secondary bg-opacity-10 border-secondary'
  }

  return 'bg-info bg-opacity-10 border-primary'
}

const getSessionStyle = (session) => {
  const gap = 12
  const width = `calc((100% - ${(session.laneCount - 1) * gap}px) / ${session.laneCount})`
  const left = `calc((${width} + ${gap}px) * ${session.lane})`

  return {
    top: `${session.top}px`,
    left,
    width,
    height: `${session.height}px`
  }
}

const goToPreviousDay = () => {
  if (selectedDayIndex.value > 0) {
    selectedDayIndex.value -= 1
  }
}

const goToNextDay = () => {
  if (selectedDayIndex.value < 6) {
    selectedDayIndex.value += 1
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

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 10px;
}

.schedule-nav-btn {
  width: 34px;
  height: 34px;
  border: 1px solid #dbe6e1;
  border-radius: 999px;
  background: #ffffff;
  color: #0a7a51;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.schedule-nav-btn:hover:not(:disabled) {
  background: #edf7f2;
  border-color: #b8ddcc;
  box-shadow: 0 6px 14px rgba(0, 137, 90, 0.12);
}

.schedule-nav-btn:disabled {
  color: #9aa7b3;
  background: #f8faf9;
  cursor: not-allowed;
}

.schedule-date-label {
  min-width: 160px;
  text-align: center;
}

.session-card {
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  overflow: hidden;
}

.session-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.08) !important;
}

.session-card-label {
  font-size: 0.65rem;
  letter-spacing: 1px;
}

.session-card-title,
.session-card-meta {
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
