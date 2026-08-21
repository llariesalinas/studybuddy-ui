<template>
  <div class="booking-page py-4">
    <div class="container">
      <div class="mb-4">
        <button class="back-link sb-btn" type="button" @click="backButton">
          <i class="bi bi-arrow-left"></i>
          Back
        </button>
      </div>

      <div class="booking-layout">
        <div class="left-column">
          <section class="info-card profile-card shadow-sm position-relative">
            <div class="profile-actions">
              <button class="action-btn sb-btn" aria-label="Message" @click="openChat">
                <i class="bi bi-chat-dots"></i>
              </button>
            </div>

            <div class="profile-header">
              <div class="avatar-shell">
                <img
                  v-if="tutorProfile.profilePictureUrl && !avatarLoadError"
                  :src="tutorProfile.profilePictureUrl"
                  class="avatar-img"
                  alt="Tutor profile photo"
                  @error="avatarLoadError = true"
                >
                <div v-else class="avatar-fallback">{{ tutorInitials }}</div>
              </div>

              <div class="profile-copy">
                <div class="name-row">
                  <h1 class="profile-name">{{ tutorProfile.name }}</h1>
                  <span v-if="tutorProfile.isVerified" class="verified-badge">
                    <i class="bi bi-patch-check-fill"></i>
                    Verified
                  </span>
                  <span v-if="tutorProfile.institutionName" class="institution-badge">
                    <i class="bi bi-mortarboard-fill"></i>
                    {{ tutorProfile.institutionName }}
                  </span>
                </div>

                <div class="bio-container">
                  <h2 class="section-title">About the Tutor</h2>
                  <p class="bio-copy">{{ tutorProfile.bio }}</p>
                </div>
              </div>
            </div>
          </section>

          <section class="info-card schedule-card shadow-sm">
            <div class="schedule-header">
              <div>
                <h2 class="schedule-title">{{ tutorProfile.name }}'s Schedule</h2>
                <p class="schedule-subtitle">Pick one or more slots on the same day.</p>
              </div>

              <div class="availability-legend">
                <span class="legend-pill legend-pill-available">Available</span>
                <span class="legend-pill legend-pill-blocked">Blocked</span>
                <span class="legend-pill legend-pill-selected">Selected</span>
              </div>
            </div>

            <div v-if="currentWeek" class="week-shell">
              <div class="week-toolbar">
                <div class="week-nav">
                  <button
                    type="button"
                    class="week-nav-btn sb-btn"
                    :disabled="!canGoPrevious"
                    @click="navigateWeek(-1)"
                  >
                    <i class="bi bi-chevron-left"></i>
                  </button>
                  <button
                    type="button"
                    class="week-nav-btn sb-btn"
                    :disabled="!canGoNext"
                    @click="navigateWeek(1)"
                  >
                    <i class="bi bi-chevron-right"></i>
                  </button>
                </div>

                <p class="week-range mb-0">{{ currentWeekLabel }}</p>
              </div>

              <div class="week-columns">
                <article
                  v-for="day in currentWeek.days"
                  :key="day.date"
                  class="day-column"
                  :class="{
                    'day-column-today': isToday(day.date),
                    'day-column-outside': !day.in_month,
                    'day-column-past': day.is_past,
                    'day-column-blocked': day.is_blocked
                  }"
                >
                  <div class="day-heading">
                    <div class="day-name">{{ formatShortDay(day.name) }}</div>
                    <div class="day-date">{{ formatDayHeaderDate(day.date) }}</div>
                  </div>

                  <div class="day-availability-bar" :class="availabilityBarClass(day)"></div>

                  <div class="day-slots">
                    <button
                      v-for="slot in displayedSlots(day)"
                      :key="`${day.date}-${slot.id}-${slot.time_slot}`"
                      type="button"
                      class="slot-link sb-btn"
                      :class="{
                        selected: isSlotSelected(day, slot),
                        'range-held': isSlotHeldBySelection(day, slot),
                        blocked: slot.is_overridden || day.is_blocked
                      }"
                      :disabled="slot.is_booked || day.is_past || !day.in_month || isSlotHeldBySelection(day, slot)"
                      @click="toggleSlot(day, currentWeek, slot)"
                    >
                      {{ formatSlotRange(day.date, slot.time_slot) }}
                    </button>

                    <div
                      v-if="!day.slots.length"
                      class="empty-day"
                      :class="{ 'empty-day-blocked': day.is_blocked }"
                    >
                      {{ day.is_blocked ? 'Blocked' : 'No slots' }}
                    </div>
                  </div>
                </article>
              </div>

              <div class="schedule-actions">
                <button
                  v-if="hasHiddenSlots"
                  type="button"
                  class="btn btn-outline-success px-4 rounded-3 fw-semibold sb-btn"
                  @click="showFullSchedule = true"
                >
                  View full schedule
                </button>
              </div>
            </div>

            <div v-else class="empty-schedule">No schedule available.</div>
          </section>
        </div>

        <aside class="right-column">
          <div class="sticky-sidebar">
            <section class="info-card shadow-sm">
              <h2 class="sidebar-title">Tutor Stats</h2>

              <div class="summary-rows">
                <div class="summary-row">
                  <span class="summary-label">Hourly Rate</span>
                  <span class="summary-value text-success fw-bold">
                    {{ currencyFormatter.format(tutorProfile.hourlyRate) }}/hr
                  </span>
                </div>
                <div class="summary-row">
                  <span class="summary-label">Rating</span>
                  <span class="summary-value align-items-center d-flex gap-1">
                    <i class="bi bi-star-fill text-warning"></i>
                    {{ tutorProfile.rating.toFixed(1) }}
                  </span>
                </div>
                <div class="summary-row">
                  <span class="summary-label">Total Sessions</span>
                  <span class="summary-value">{{ tutorProfile.sessionCount }}</span>
                </div>
              </div>
            </section>

            <section class="info-card shadow-sm">
              <h2 class="sidebar-title mb-3">Subjects Taught</h2>

              <div class="subjects-accordion">
                <div
                  v-for="(subject, index) in tutorProfile.subjects"
                  :key="subject.subject_code || index"
                  class="subject-accordion-item"
                >
                  <button
                    type="button"
                    class="subject-accordion-header sb-btn"
                    @click="toggleSubject(index)"
                  >
                    <span>{{ subject.subject_name }}</span>
                    <i class="bi" :class="expandedSubjects.includes(index) ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
                  </button>

                  <div
                    class="subject-accordion-collapse"
                    :class="{ 'is-expanded': expandedSubjects.includes(index) }"
                  >
                    <div class="subject-accordion-body">
                      <div class="subject-accordion-content">
                        {{ subject.description || `Comprehensive sessions focusing on ${subject.subject_name}. Tailored exactly to your pace and learning style to help you achieve your goals.` }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="isFaceToFace" class="mb-4">
                <label class="form-label fw-bold small text-muted">Preferred Location</label>
                <input
                  type="text"
                  v-model="bookedSessionStore.bookedSessionLocation"
                  class="form-control border-sb shadow-none py-2 rounded-3 sb-field"
                  placeholder="e.g. Library Room 3"
                  required
                />
              </div>

              <hr class="my-4" style="border-color: #edf1ef;" />

              <div class="cost-counter" :class="{ 'cost-counter-active': selectedSessionCount > 0 }">
                <div class="cost-counter-header">Estimated Total</div>
                <div class="cost-counter-amount">{{ formattedEstimatedCost }}</div>
                <div v-if="sessionTimeRangeLabel" class="cost-counter-session">
                  Session: {{ sessionTimeRangeLabel }}
                </div>
                <div class="cost-counter-meta">
                  {{ selectedSessionCount }} slot{{ selectedSessionCount === 1 ? '' : 's' }}
                  ({{ selectedSessionHours }} hour{{ selectedSessionHours === 1 ? '' : 's' }})
                </div>
              </div>

              <p class="policy-note">Free cancellation up to 24 hours before the session.</p>

              <button
                type="button"
                class="btn confirm-booking-btn w-100 sb-btn"
                :disabled="isConfirmBookingDisabled"
                @click="confirmBooking"
              >
                {{ confirmBookingButtonLabel }}
              </button>

              <p v-if="isTuteeStrikeBlocked" class="strike-booking-note">
                You have {{ profileStore.strikeCap }} late-cancellation strikes. Booking reopens
                {{ strikeExpiryLabel }}.
              </p>

              <router-link
                v-else-if="isTuteeBookingBlocked"
                to="/application-status"
                class="verify-booking-link"
              >
                Verify your account to book
              </router-link>
            </section>
          </div>
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useBookingPrefsStore } from '@/stores/selectedSessions'
import { useBookedSessionStore } from '@/stores/bookedSessionDetails'
import { useInitialBookingPrefsStore } from '@/stores/initialbookingprefs'
import { useFindTutorsStore } from '@/stores/findTutors'
import { usePaymentStore } from '@/stores/tuteePaymentDetails'
import { useChatStore } from '@/stores/chat'
import { useProfileStore } from '@/stores/profile'
import { useToastStore } from '@/stores/toast'
import { needsTuteeBookingBlock, needsTuteeStrikeBlock } from '@/services/tutorApplicationState'
import { formatCutoffLabel } from '@/composables/useCancellationWindow'
import api from '@/services/api/api'

const router = useRouter()
const route = useRoute()

const bookingPrefsStore = useBookingPrefsStore()
const bookedSessionStore = useBookedSessionStore()
const initialBookingStore = useInitialBookingPrefsStore()
const findTutorsStore = useFindTutorsStore()
const paymentStore = usePaymentStore()
const chatStore = useChatStore()
const profileStore = useProfileStore()
const toastStore = useToastStore()

const tutorID = route.params.id
const monthOffset = ref(0)
const weekIndex = ref(0)
const selectedSlots = ref([])
const monthAvailability = ref(null)
const showFullSchedule = ref(false)
const isSubmittingBooking = ref(false)
const avatarLoadError = ref(false)
const expandedSubjects = ref([])

const openChat = async () => {
  try {
    const room = await chatStore.startInquiry(tutorID)
    router.push({ name: 'chat', query: { room: room.id } })
  } catch (error) {
    console.error('Failed to open chat:', error)
  }
}

const currencyFormatter = new Intl.NumberFormat('en-PH', {
  style: 'currency',
  currency: 'PHP'
})

const tutorDetails = ref({
  profile_id: null,
  name: '',
  subjects: [],
  rating: 4.7,
  bio: '',
  profile_picture_url: '',
  hourly_rate: 0,
  total_sessions: 124,
  response_time_label: '',
  pinned_review_id: null,
  pinned_review: null
})

const visibleWeeks = computed(() => monthAvailability.value?.weeks || [])
const firstBookableWeekIndex = computed(() => getInitialWeekIndex(visibleWeeks.value))
const currentWeek = computed(() => visibleWeeks.value[weekIndex.value] || null)

const canGoPrevious = computed(() => {
  if (monthOffset.value > 0) return true
  return weekIndex.value > firstBookableWeekIndex.value
})

const canGoNext = computed(() => visibleWeeks.value.length > 0)

const hasHiddenSlots = computed(() => {
  if (showFullSchedule.value || !currentWeek.value) return false
  return currentWeek.value.days.some(day => day.slots.length > 8)
})

const currentWeekLabel = computed(() => {
  if (!currentWeek.value) return ''

  const start = new Date(currentWeek.value.week_start)
  const end = new Date(currentWeek.value.week_end)
  const startMonth = start.toLocaleDateString([], { month: 'short' })
  const endMonth = end.toLocaleDateString([], { month: 'short' })
  const year = end.getFullYear()

  if (startMonth === endMonth) {
    return `${startMonth} ${start.getDate()}-${end.getDate()}, ${year}`
  }
  return `${startMonth} ${start.getDate()} - ${endMonth} ${end.getDate()}, ${year}`
})

const tutorProfile = computed(() => ({
  name: tutorDetails.value.name || 'Tutor Name',
  profilePictureUrl: tutorDetails.value.profile_picture_url || '',
  isVerified: Boolean(tutorDetails.value.is_verified),
  institutionName: tutorDetails.value.institutionName || '',
  hourlyRate: Number(tutorDetails.value.hourly_rate) || 0,
  rating: Number(tutorDetails.value.rating) || 4.7,
  sessionCount: Number(tutorDetails.value.total_sessions) || 124,
  subjects: tutorDetails.value.subjects?.length
    ? tutorDetails.value.subjects
    : [
        {
          subject_code: 'fallback-1',
          subject_name: 'Computer Science',
          description: ''
        },
        {
          subject_code: 'fallback-2',
          subject_name: 'Beginner Friendly',
          description: ''
        },
        {
          subject_code: 'fallback-3',
          subject_name: 'Web Development',
          description: ''
        }
      ],
  bio: tutorDetails.value.bio || 'This tutor brings patient, step-by-step guidance for learners building confidence in technical subjects. Additional bio content can easily extend here to test the scrollbar constraint and ensure it is functioning correctly. We are dedicated to providing excellent learning experiences for all ages.',
}))

const tutorInitials = computed(() => {
  const parts = String(tutorProfile.value.name || '')
    .trim()
    .split(/\s+/)
    .filter(Boolean)

  return parts.slice(0, 2).map(part => part[0]).join('').toUpperCase() || 'SB'
})

const isFaceToFace = computed(() => {
  const mode = bookingPrefsStore.selectedMode || initialBookingStore.selectedMode || 'Online'
  return mode === 'Face-to-face' || mode === 'F2F'
})

const effectiveSelectedSlots = computed(() => {
  if (!currentWeek.value) {
    return selectedSlots.value
  }

  const expandedSlots = []

  currentWeek.value.days.forEach((day) => {
    const explicitDaySelections = selectedSlots.value
      .filter(selected => selected.session_date === day.date)
      .sort((left, right) => left.time_slot.localeCompare(right.time_slot))

    if (!explicitDaySelections.length) {
      return
    }

    const selectableDaySlots = [...day.slots]
      .filter(slot => !slot.is_booked)
      .sort((left, right) => left.time_slot.localeCompare(right.time_slot))

    selectableDaySlots.forEach((slot) => {
      const matchingSelection = explicitDaySelections.find(
        selected => selected.availability_id === slot.id
      )

      if (matchingSelection) {
        expandedSlots.push(matchingSelection)
        return
      }

      const previousExplicit = [...explicitDaySelections]
        .reverse()
        .find(selected => selected.time_slot < slot.time_slot)
      const nextExplicit = explicitDaySelections.find(selected => selected.time_slot > slot.time_slot)

      if (!previousExplicit || !nextExplicit) {
        return
      }

      const slotsBetween = selectableDaySlots.filter(
        candidate => candidate.time_slot > previousExplicit.time_slot && candidate.time_slot < nextExplicit.time_slot
      )

      const isContinuousRange = slotsBetween.every((candidate, index) => {
        const previousTime = index === 0 ? previousExplicit.time_slot : slotsBetween[index - 1].time_slot
        return addOneHour(previousTime) === candidate.time_slot
      }) && addOneHour(slotsBetween.at(-1)?.time_slot || previousExplicit.time_slot) === nextExplicit.time_slot

      if (!isContinuousRange) {
        return
      }

      expandedSlots.push({
        availability_id: slot.id,
        session_date: day.date,
        session_mode: bookingPrefsStore.selectedMode || initialBookingStore.selectedMode || 'Online',
        time_slot: slot.time_slot,
        week_start: currentWeek.value.week_start
      })
    })
  })

  return expandedSlots.sort((left, right) => {
    const dateComparison = left.session_date.localeCompare(right.session_date)
    if (dateComparison !== 0) return dateComparison
    return left.time_slot.localeCompare(right.time_slot)
  })
})

const SESSION_SLOT_HOURS = 1.0

const selectedSessionCount = computed(() => effectiveSelectedSlots.value.length)

const selectedSessionHours = computed(() => selectedSessionCount.value * SESSION_SLOT_HOURS)

const estimatedCost = computed(() => selectedSessionHours.value * tutorProfile.value.hourlyRate)

const formattedEstimatedCost = computed(() => currencyFormatter.format(estimatedCost.value))

const sessionTimeRangeLabel = computed(() => {
  if (!effectiveSelectedSlots.value.length) return ''

  const first = effectiveSelectedSlots.value[0]
  const last = effectiveSelectedSlots.value[effectiveSelectedSlots.value.length - 1]

  return formatTimeRangeLabel(first.session_date, first.time_slot, addOneHour(last.time_slot))
})

const tuteeVerificationSnapshot = computed(() => ({
  application_status: profileStore.applicationStatus || null,
  document_renewal_status: profileStore.renewalStatus || null,
  tutee_verification_enforced: profileStore.tuteeVerificationEnforced,
  strike_blocked: profileStore.strikeBlocked,
  strike_expires_at: profileStore.strikeExpiresAt,
}))

const isTuteeStrikeBlocked = computed(() =>
  profileStore.loaded && needsTuteeStrikeBlock(tuteeVerificationSnapshot.value)
)

const strikeExpiryLabel = computed(() => {
  const expiresAt = profileStore.strikeExpiresAt

  if (!expiresAt) {
    return 'once a strike expires'
  }

  return `on ${formatCutoffLabel(new Date(expiresAt))}`
})

const isTuteeBookingBlocked = computed(() =>
  profileStore.loaded && needsTuteeBookingBlock(tuteeVerificationSnapshot.value)
)

const isConfirmBookingDisabled = computed(() =>
  isTuteeBookingBlocked.value || selectedSlots.value.length === 0 || isSubmittingBooking.value
)

const confirmBookingButtonLabel = computed(() => {
  // Strike first: it's the cause the tutee can't fix by verifying.
  if (isTuteeStrikeBlocked.value) {
    return 'Booking paused'
  }

  if (isTuteeBookingBlocked.value) {
    return 'Verify to book'
  }

  if (isSubmittingBooking.value) {
    return 'Confirming...'
  }

  if (selectedSlots.value.length === 0) {
    return 'Select a slot first'
  }

  return 'Confirm Booking'
})

const backButton = () => {
  router.back()
}

const toggleSubject = (index) => {
  if (expandedSubjects.value.includes(index)) {
    expandedSubjects.value = expandedSubjects.value.filter(i => i !== index)
  } else {
    expandedSubjects.value.push(index)
  }
}

function createLocalDate(dateString, timeString) {
  return new Date(`${dateString}T${timeString}:00`)
}

function formatTime(dateString, time) {
  const slotDate = createLocalDate(dateString, time)
  return new Intl.DateTimeFormat('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  }).format(slotDate)
}

function formatTimeWithoutPeriod(dateString, time) {
  return formatTime(dateString, time).replace(/\s?[AP]M$/i, '')
}

function getTimePeriod(time) {
  const [hours] = time.split(':').map(Number)
  return hours >= 12 ? 'PM' : 'AM'
}

function formatTimeRangeLabel(dateString, startTime, endTime) {
  if (getTimePeriod(startTime) !== getTimePeriod(endTime)) {
    return `${formatTime(dateString, startTime)} - ${formatTime(dateString, endTime)}`
  }

  return `${formatTimeWithoutPeriod(dateString, startTime)} - ${formatTime(dateString, endTime)}`
}

function formatSlotRange(dateString, time) {
  return formatTimeRangeLabel(dateString, time, addOneHour(time))
}

function formatShortDay(dayName) {
  return dayName.slice(0, 3)
}

function formatDayHeaderDate(dateString) {
  return new Date(dateString).getDate()
}

function getDateKey(date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function isToday(dateString) {
  return dateString === getDateKey(new Date())
}

function addOneHour(timeString) {
  const [hours, minutes] = timeString.split(':').map(Number)
  const totalMinutes = (hours * 60) + minutes + 60
  const normalizedHours = Math.floor(totalMinutes / 60) % 24
  const normalizedMinutes = totalMinutes % 60

  return `${String(normalizedHours).padStart(2, '0')}:${String(normalizedMinutes).padStart(2, '0')}`
}

function displayedSlots(day) {
  if (showFullSchedule.value) {
    return day.slots
  }
  return day.slots.slice(0, 8)
}

function availabilityBarClass(day) {
  if (day.is_past) return 'day-availability-bar-past'
  if (day.is_blocked) return 'day-availability-bar-blocked'
  if (day.has_available) return 'day-availability-bar-available'
  return 'day-availability-bar-unavailable'
}

const getTutorDetails = async () => {
  try {
    const response = await api.get(`tutors/${tutorID}/`)
    avatarLoadError.value = false
    tutorDetails.value = {
      profile_id: response.data.profile_id,
      name: [response.data.fname, response.data.lname].filter(Boolean).join(' '),
      institutionName: response.data.institution_name || '',
      subjects: Array.isArray(response.data.subjects) ? response.data.subjects : [],
      rating: response.data.rating_average ?? 4.7,
      bio: response.data.bio,
      profile_picture_url: response.data.profile_picture_url || '',
      hourly_rate: response.data.hourly_rate ?? 0,
      total_sessions: response.data.total_sessions ?? 124,
      response_time_label: response.data.response_time_label || '',
      is_verified: Boolean(response.data.is_verified),
      pinned_review_id: response.data.pinned_review_id ?? null,
      pinned_review: response.data.pinned_review ?? null
    }
  } catch (error) {
    console.error('Failed to load tutor details.', error)
  }
}

function getInitialWeekIndex(weeks) {
  if (!weeks.length) return 0

  const today = new Date()
  const todayString = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
  const matchingWeekIndex = weeks.findIndex(
    week => todayString >= week.week_start && todayString <= week.week_end
  )

  return matchingWeekIndex >= 0 ? matchingWeekIndex : 0
}

const getTutorSchedule = async () => {
  try {
    const response = await api.get(`tutors/${route.params.id}/availability/`, {
      params: { month_offset: monthOffset.value }
    })

    monthAvailability.value = response.data
    weekIndex.value = getInitialWeekIndex(response.data.weeks || [])
    selectedSlots.value = []
    showFullSchedule.value = false
  } catch (error) {
    console.error('Failed to load tutor schedule.', error)
  }
}

async function navigateWeek(direction) {
  if (direction < 0) {
    const minimumWeekIndex = monthOffset.value === 0 ? firstBookableWeekIndex.value : 0

    if (weekIndex.value > minimumWeekIndex) {
      weekIndex.value -= 1
      selectedSlots.value = []
      showFullSchedule.value = false
      return
    }

    if (monthOffset.value === 0) return

    monthOffset.value -= 1
    await getTutorSchedule()

    if (monthOffset.value > 0) {
      weekIndex.value = Math.max(visibleWeeks.value.length - 1, 0)
    }
    return
  }

  if (weekIndex.value < visibleWeeks.value.length - 1) {
    weekIndex.value += 1
    selectedSlots.value = []
    showFullSchedule.value = false
    return
  }

  monthOffset.value += 1
  await getTutorSchedule()
  weekIndex.value = 0
}

function isSlotSelected(day, slot) {
  return selectedSlots.value.some(
    selected => selected.availability_id === slot.id && selected.session_date === day.date
  )
}

function isSlotHeldBySelection(day, slot) {
  if (isSlotSelected(day, slot)) {
    return false
  }

  return effectiveSelectedSlots.value.some(
    selected => selected.availability_id === slot.id && selected.session_date === day.date
  )
}

function canExpandSelectionWithinDay(day, explicitSelections) {
  if (explicitSelections.length <= 1) {
    return true
  }

  const orderedSelections = [...explicitSelections].sort((left, right) => left.time_slot.localeCompare(right.time_slot))
  const availableSlots = [...day.slots]
    .filter(slot => !slot.is_booked)
    .sort((left, right) => left.time_slot.localeCompare(right.time_slot))

  for (let index = 0; index < orderedSelections.length - 1; index += 1) {
    const currentSelection = orderedSelections[index]
    const nextSelection = orderedSelections[index + 1]

    let expectedTime = addOneHour(currentSelection.time_slot)

    while (expectedTime < nextSelection.time_slot) {
      const hasIntermediateSlot = availableSlots.some(slot => slot.time_slot === expectedTime)

      if (!hasIntermediateSlot) {
        return false
      }

      expectedTime = addOneHour(expectedTime)
    }
  }

  return true
}

function toggleSlot(day, week, slot) {
  if (slot.is_booked || day.is_past || !day.in_month || isSlotHeldBySelection(day, slot)) return

  const slotWithDate = {
    availability_id: slot.id,
    session_date: day.date,
    session_mode: bookingPrefsStore.selectedMode || initialBookingStore.selectedMode || 'Online',
    time_slot: slot.time_slot,
    week_start: week.week_start
  }

  const exists = selectedSlots.value.some(
    selected => selected.availability_id === slot.id && selected.session_date === day.date
  )

  if (exists) {
    selectedSlots.value = selectedSlots.value.filter(
      selected => !(selected.availability_id === slot.id && selected.session_date === day.date)
    )
    return
  }

  if (selectedSlots.value.length > 0 && selectedSlots.value[0].week_start !== week.week_start) {
    toastStore.push('You can book multiple slots only within the same week.', 'warning')
    return
  }

  if (selectedSlots.value.length > 0 && selectedSlots.value[0].session_date !== day.date) {
    toastStore.push('You can only book multiple sessions on the same day.', 'warning')
    return
  }

  const nextSelections = [...selectedSlots.value, slotWithDate]
  const daySelections = nextSelections.filter(selected => selected.session_date === day.date)

  if (!canExpandSelectionWithinDay(day, daySelections)) {
    toastStore.push('The selected range includes unavailable in-between time slots.', 'warning')
    return
  }

  selectedSlots.value = nextSelections
}

const confirmBooking = async () => {
  if (isTuteeBookingBlocked.value || selectedSlots.value.length === 0) {
    return
  }

  isSubmittingBooking.value = true

  try {
    bookedSessionStore.bookedSessions = [...effectiveSelectedSlots.value]
    bookedSessionStore.bookedSessionTutorName = tutorProfile.value.name
    bookedSessionStore.bookedSessionTutorID = tutorID
    bookedSessionStore.bookedSessionSub = bookedSessionStore.bookedSessionSub || initialBookingStore.selectedSubject
    bookedSessionStore.bookedSessionMode = bookedSessionStore.bookedSessionMode || initialBookingStore.selectedMode

    const response = await api.post('bookings/confirm/', {
      tutor_id: tutorID,
      slots: effectiveSelectedSlots.value,
      preferred_location: bookedSessionStore.bookedSessionLocation,
      subject: bookedSessionStore.bookedSessionSub
    })

    const confirmation = response.data
    const destination = confirmation.meeting_link || confirmation.preferred_location
    const cancellationCopy = confirmation.is_born_late
      ? 'This booking has no penalty-free cancellation window.'
      : `Cancel without a strike before ${new Date(confirmation.cancellation_deadline).toLocaleString()}.`
    toastStore.push(`Booking confirmed. ${destination ? `Session details: ${destination}. ` : ''}${cancellationCopy}`)
    initialBookingStore.$reset()
    findTutorsStore.reset()
    selectedSlots.value = []

    router.push({
      name: 'dashboard',
      query: { refresh: Date.now() }
    })
  } catch (error) {
    console.error('Payment error:', error.response?.data || error)
    toastStore.push(error.response?.data?.error || 'Something went wrong.', 'error')
  } finally {
    isSubmittingBooking.value = false
  }
}

onMounted(async () => {
  paymentStore.reset()
  bookedSessionStore.bookedSessionLocation = findTutorsStore.filters.location || ''
  await Promise.all([
    getTutorDetails(),
    getTutorSchedule()
  ])
})
</script>

<style scoped>
.booking-page {
  min-height: 100vh;
  background: #f8f9fa;
}

.booking-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) minmax(320px, 0.9fr);
  gap: 24px;
  align-items: start;
}

.left-column {
  display: grid;
  gap: 24px;
}

.right-column {
  min-width: 0;
  align-self: start;
  position: sticky;
  top: 24px;
}

.sticky-sidebar {
  display: grid;
  gap: 20px;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 0;
  background: transparent;
  color: #315447;
  font-weight: 600;
  padding: 0;
}

.info-card {
  background: #ffffff;
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}

.profile-card {
  display: grid;
  gap: 24px;
}

.profile-actions {
  position: absolute;
  top: 24px;
  right: 24px;
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background: #ffffff;
  color: #315447;
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: transform var(--sb-t-normal) var(--sb-spring);
}

.action-btn:hover {
  background: #f3f7f5;
  color: #0a7a51;
}

.profile-header {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 20px;
  align-items: start;
}

.avatar-shell,
.avatar-img,
.avatar-fallback {
  width: 88px;
  height: 88px;
  border-radius: 50%;
}

.avatar-shell {
  overflow: hidden;
  flex: 0 0 auto;
}

.avatar-img {
  display: block;
  object-fit: cover;
}

.avatar-fallback {
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #0a7a51, #15a36a);
  color: #ffffff;
  font-size: 1.7rem;
  font-weight: 700;
}

.profile-copy {
  display: grid;
  gap: 14px;
  margin-top: 10px;
}

.name-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.profile-name {
  font-size: 2rem;
  font-weight: 700;
  color: #163127;
  margin: 0;
}

.verified-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 999px;
  background: #e8f7f1;
  color: #0a7a51;
  font-size: 0.85rem;
  font-weight: 600;
}

.institution-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 999px;
  background: var(--sb-bg, #f8f9fa);
  border: 1px solid var(--sb-card-border, #eaeaea);
  color: var(--sb-text-secondary, #495057);
  font-size: 0.85rem;
  font-weight: 600;
}

.bio-container {
  max-height: 96px;
  overflow-y: auto;
  padding-right: 8px;
}

.bio-container::-webkit-scrollbar {
  width: 6px;
}

.bio-container::-webkit-scrollbar-track {
  background: transparent;
}

.bio-container::-webkit-scrollbar-thumb {
  background: #dbe6e1;
  border-radius: 10px;
}

.bio-container::-webkit-scrollbar-thumb:hover {
  background: #c4d4cc;
}

.section-title {
  font-size: 1rem;
  font-weight: 700;
  color: #163127;
  margin-bottom: 6px;
}

.bio-copy {
  margin: 0;
  color: #53665e;
  line-height: 1.6;
}

.schedule-card {
  display: grid;
  gap: 24px;
}

.schedule-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.schedule-title,
.sidebar-title {
  margin: 0 0 4px;
  font-size: 1.15rem;
  font-weight: 700;
  color: #163127;
}

.schedule-subtitle {
  margin: 0;
  color: #6d8178;
}

.week-shell {
  display: grid;
  gap: 24px;
}

.week-toolbar {
  display: grid;
  grid-template-columns: auto 1fr;
  align-items: center;
  gap: 16px;
}

.week-nav {
  display: flex;
  gap: 10px;
}

.week-nav-btn {
  width: 42px;
  height: 42px;
  border: 0;
  border-radius: 14px;
  background: #edf6f1;
  color: #0a7a51;
  transition: transform var(--sb-t-normal) var(--sb-spring);
}

.week-nav-btn:hover:not(:disabled) {
  background: #dff1e8;
  transform: translateY(-1px);
  box-shadow: 0 8px 16px rgba(0, 137, 90, 0.12);
}

.week-nav-btn:disabled {
  background: #f3f4f6;
  color: #94a3b8;
  cursor: not-allowed;
}

.week-range {
  margin: 0;
  text-align: center;
  font-size: 1.2rem;
  font-weight: 700;
  color: #163127;
}

.week-columns {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 16px;
}

.day-column {
  min-width: 0;
  position: relative;
  display: grid;
  grid-template-rows: auto auto 1fr;
  gap: 8px;
  align-content: start;
}

.day-column-outside {
  opacity: 0.45;
}

.day-column-past {
  opacity: 0.7;
}

.day-column-blocked .day-name,
.day-column-blocked .day-date {
  color: #a16207;
}

.day-column-today {
  isolation: isolate;
}

.day-column-today::before {
  content: '';
  position: absolute;
  inset: -8px;
  background: linear-gradient(180deg, rgba(0, 137, 90, 0.08), rgba(0, 137, 90, 0.03));
  border-radius: 20px;
  box-shadow: 0 0 0 1px rgba(0, 137, 90, 0.14), 0 0 24px rgba(0, 137, 90, 0.18);
  z-index: -1;
  pointer-events: none;
}

.day-column-today .day-name {
  color: #0a7a51;
}

.day-column-today .day-date {
  color: #0a7a51;
  text-shadow: 0 0 10px rgba(0, 137, 90, 0.2);
}

.day-column-blocked .day-heading {
  background: linear-gradient(180deg, rgba(250, 204, 21, 0.12), transparent);
  border-radius: 12px;
}

.day-heading {
  display: grid;
  gap: 0;
  justify-items: center;
  text-align: center;
  padding-bottom: 2px;
}

.day-name {
  color: #687684;
  font-size: 0.9rem;
  font-weight: 600;
}

.day-date {
  color: #163127;
  font-size: 1.15rem;
  font-weight: 700;
  line-height: 1;
}

.day-availability-bar {
  height: 3px;
  border-radius: 999px;
  background: #d7e1dc;
}

.day-availability-bar-available {
  background: #00895a;
}

.day-availability-bar-blocked {
  background: #eab308;
}

.day-availability-bar-unavailable {
  background: #d3dbe0;
}

.day-availability-bar-past {
  background: #c7cfd6;
}

.day-slots {
  display: grid;
  gap: 10px;
  align-content: start;
}

.slot-link {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #dbe6e1;
  border-radius: 14px;
  background: #ffffff;
  color: #163127;
  font-size: 0.82rem;
  line-height: 1.25;
  font-weight: 600;
  text-align: left;
  cursor: pointer;
  transition: transform var(--sb-t-normal) var(--sb-spring);
}

.slot-link:hover:not(:disabled) {
  color: #0a7a51;
  background: #edf7f2;
  border-color: #cfe6da;
}

.slot-link:disabled {
  color: #a0acb8;
  background: #f8faf9;
  border-color: #eef2ef;
  cursor: not-allowed;
}

.slot-link.blocked,
.slot-link.blocked:disabled {
  color: #a16207;
  background: #fef9c3;
  border-color: #f4d96b;
}

.slot-link.selected {
  color: #ffffff;
  background: #00895a;
  border-color: #00895a;
  box-shadow: 0 8px 18px rgba(0, 137, 90, 0.18);
  transform: translateY(-1px);
}

.slot-link.range-held,
.slot-link.range-held:disabled {
  color: #94a3b8;
  background: #f1f5f9;
  border-color: #dbe4ee;
  cursor: not-allowed;
}

.empty-day {
  color: #9aa7b3;
  font-size: 0.9rem;
}

.empty-day-blocked {
  color: #a16207;
  font-weight: 700;
}

.schedule-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
}

.availability-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.legend-pill {
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
}

.legend-pill-available {
  background: #e8f7f1;
  color: #00895a;
}

.legend-pill-blocked {
  background: #fef3c7;
  color: #a16207;
  border: 1px solid rgba(234, 179, 8, 0.35);
}

.legend-pill-selected {
  background: rgba(0, 137, 90, 0.12);
  color: #00895a;
  border: 1px solid rgba(0, 137, 90, 0.2);
}

.empty-schedule {
  color: #7a8f86;
  text-align: center;
  padding: 32px 0;
}

.summary-rows {
  display: grid;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 14px 0;
  border-bottom: 1px solid #edf1ef;
}

.summary-row:last-child {
  border-bottom: 0;
}

.summary-label {
  color: #6c8077;
}

.summary-value {
  color: #163127;
  font-weight: 600;
  text-align: right;
}

.subjects-accordion {
  display: grid;
  gap: 10px;
}

.subject-accordion-item {
  border: 1px solid #e5ebe8;
  border-radius: 12px;
  overflow: hidden;
}

.subject-accordion-header {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  background: #fcfdfc;
  border: 0;
  color: #315447;
  font-weight: 600;
  text-align: left;
  transition: none;
  cursor: pointer;
}

.subject-accordion-header:hover {
  background: #f3f7f5;
}

.subject-accordion-collapse {
  display: grid;
  grid-template-rows: 0fr;
  transition: none;
}

.subject-accordion-collapse.is-expanded {
  grid-template-rows: 1fr;
}

.subject-accordion-body {
  overflow: hidden;
  background: #ffffff;
}

.subject-accordion-content {
  padding: 14px 16px;
  color: #6c8077;
  font-size: 0.92rem;
  border-top: 1px solid #e5ebe8;
  line-height: 1.6;
}

.cost-counter {
  border: 1px solid #dce9e2;
  border-radius: 12px;
  padding: 12px 14px;
  margin-bottom: 14px;
  background: #f7fbf9;
}

.cost-counter-active {
  border-color: #8cc9b2;
  background: #eef8f3;
}

.cost-counter-header {
  color: #4f685d;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.cost-counter-amount {
  color: #0e4d35;
  font-size: 1.25rem;
  font-weight: 800;
  line-height: 1.2;
  margin-top: 3px;
}

.cost-counter-session {
  color: #0e4d35;
  font-size: 0.86rem;
  font-weight: 600;
  margin-top: 6px;
}

.cost-counter-meta {
  color: #587266;
  font-size: 0.86rem;
  margin-top: 4px;
}

.policy-note {
  margin-bottom: 16px;
  color: #6c8077;
  font-size: 0.92rem;
  text-align: center;
}

.confirm-booking-btn {
  background: #00895a;
  color: #ffffff;
  border: 0;
  border-radius: 14px;
  padding: 12px 18px;
  font-weight: 700;
  display: block;
  margin: 0 auto;
}

.confirm-booking-btn:disabled {
  background: #b8c5bf;
  color: #f8faf9;
}

.verify-booking-link {
  display: inline-flex;
  justify-content: center;
  margin-top: 0.85rem;
  color: #0a7a51;
  font-size: 0.92rem;
  font-weight: 700;
  text-decoration: none;
}

.verify-booking-link:hover {
  text-decoration: underline;
}

.strike-booking-note {
  margin: 0.85rem 0 0;
  color: var(--sb-danger);
  font-size: 0.88rem;
  font-weight: 600;
  line-height: 1.45;
  text-align: center;
}

@media (max-width: 1199px) {
  .booking-layout {
    grid-template-columns: 1fr;
  }
  .right-column {
    position: static;
  }
}

@media (max-width: 991px) {
  .week-toolbar {
    grid-template-columns: 1fr;
    justify-items: start;
  }
  .week-range {
    text-align: left;
  }
}

@media (max-width: 768px) {
  .week-columns {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .profile-header {
    grid-template-columns: 1fr;
  }
}
</style>
