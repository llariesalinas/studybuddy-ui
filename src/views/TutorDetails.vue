<template>
  <div class="booking-page py-4">
    <div class="container">
      <div class="mb-4">
        <button class="back-link" type="button" @click="backButton">
          <i class="bi bi-arrow-left"></i>
          Back
        </button>
      </div>

      <div class="booking-layout">
        <div class="left-column">
          <section class="info-card profile-card shadow-sm">
            <div class="profile-header">
              <div class="avatar-fallback">{{ tutorInitials }}</div>

              <div class="profile-copy">
                <div class="name-row">
                  <h1 class="profile-name">{{ tutorProfile.name }}</h1>
                  <span class="verified-badge">
                    <i class="bi bi-patch-check-fill"></i>
                    Verified
                  </span>
                </div>

                <div class="rating-row">
                  <span class="stars" aria-hidden="true">
                    <i
                      v-for="star in 5"
                      :key="star"
                      class="bi"
                      :class="star <= filledStars ? 'bi-star-fill' : 'bi-star'"
                    ></i>
                  </span>
                  <span class="rating-score">{{ tutorProfile.rating.toFixed(1) }}</span>
                  <span class="session-count">{{ tutorProfile.sessionCount }} sessions</span>
                </div>

                <p class="hourly-rate">{{ currencyFormatter.format(tutorProfile.hourlyRate) }}/hr</p>

                <div class="subject-pills">
                  <span
                    v-for="subject in tutorProfile.subjects"
                    :key="subject"
                    class="subject-pill"
                  >
                    {{ subject }}
                  </span>
                </div>
              </div>
            </div>

            <div class="profile-meta">
              <div>
                <h2 class="section-title">About the Tutor</h2>
                <p class="bio-copy">{{ tutorProfile.bio }}</p>
              </div>

              <p v-if="tutorProfile.responseTimeLabel" class="meta-line">
                <i class="bi bi-clock-history"></i>
                Typically replies {{ tutorProfile.responseTimeLabel }}
              </p>

              <div v-if="tutorProfile.pinnedReview" class="pinned-review">
                <div class="pinned-review-header">
                  <span class="pinned-review-badge">Pinned Review</span>
                  <span class="pinned-review-rating">
                    <i class="bi bi-star-fill"></i>
                    {{ tutorProfile.pinnedReview.rating_score }}
                  </span>
                </div>

                <blockquote class="review-quote">
                  "{{ tutorProfile.pinnedReview.comment }}"
                </blockquote>

                <p class="review-author">- {{ tutorProfile.pinnedReview.student_name }}</p>
              </div>
            </div>
          </section>

          <section class="info-card schedule-card shadow-sm">
            <div class="schedule-header">
              <div>
                <h2 class="schedule-title">{{ tutorProfile.name }}'s Schedule</h2>
                <p class="schedule-subtitle">Pick one or more slots within the same week.</p>
              </div>

              <div class="availability-legend">
                <span class="legend-pill legend-pill-available">Available</span>
                <span class="legend-pill legend-pill-selected">Selected</span>
              </div>
            </div>

            <div v-if="currentWeek" class="week-shell">
              <div class="week-toolbar">
                <div class="week-nav">
                  <button
                    type="button"
                    class="week-nav-btn"
                    :disabled="!canGoPrevious"
                    @click="navigateWeek(-1)"
                  >
                    <i class="bi bi-chevron-left"></i>
                  </button>
                  <button
                    type="button"
                    class="week-nav-btn"
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
                    'day-column-outside': !day.in_month,
                    'day-column-past': day.is_past
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
                      class="slot-link"
                      :class="{ selected: isSlotSelected(day, slot) }"
                      :disabled="slot.is_booked || day.is_past || !day.in_month"
                      @click="toggleSlot(day, currentWeek, slot)"
                    >
                      {{ formatTime(day.date, slot.time_slot) }}
                    </button>

                    <div v-if="!day.slots.length" class="empty-day">No slots</div>
                  </div>
                </article>
              </div>

              <div class="schedule-actions">
                <button
                  v-if="hasHiddenSlots"
                  type="button"
                  class="btn btn-outline-success px-4 rounded-3 fw-semibold"
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
              <h2 class="sidebar-title">Booking Summary</h2>

              <div class="summary-rows">
                <div class="summary-row">
                  <span class="summary-label">Hours</span>
                  <span class="summary-value">{{ paymentSummary.hours }}</span>
                </div>
                <div class="summary-row">
                  <span class="summary-label">Subject</span>
                  <span class="summary-value">{{ paymentSummary.subject }}</span>
                </div>
                <div class="summary-row">
                  <span class="summary-label">Tutor</span>
                  <span class="summary-value">{{ paymentSummary.tutor }}</span>
                </div>
                <div class="summary-row summary-total">
                  <span class="summary-label">Total</span>
                  <span class="summary-value">{{ paymentSummary.total }}</span>
                </div>
              </div>
            </section>

            <section class="info-card shadow-sm">
              <h2 class="sidebar-title">Booking Note</h2>

              <div class="payment-method-grid">
                <button
                  v-for="method in paymentMethods"
                  :key="method.id"
                  type="button"
                  class="payment-method-card"
                  :class="{ selected: paymentStore.selectedMethod === method.id }"
                  @click="chooseMethod(method.id)"
                >
                  <i :class="['bi', method.icon, 'payment-method-icon']"></i>
                  <span>{{ method.label }}</span>
                </button>
              </div>

              <p class="payment-feedback">{{ paymentFeedback }}</p>
              <p class="policy-note">Free cancellation up to 24 hours before the session.</p>

              <button
                type="button"
                class="btn confirm-booking-btn"
                :disabled="!canConfirmBooking || isSubmittingBooking"
                @click="confirmBooking"
              >
                {{ isSubmittingBooking ? 'Confirming...' : 'Confirm Booking' }}
              </button>
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
import { usePaymentStore } from '@/stores/tuteePaymentDetails'
import api from '@/services/api/api'

const router = useRouter()
const route = useRoute()

const bookingPrefsStore = useBookingPrefsStore()
const bookedSessionStore = useBookedSessionStore()
const initialBookingStore = useInitialBookingPrefsStore()
const paymentStore = usePaymentStore()

const tutorID = route.params.id
const monthOffset = ref(0)
const weekIndex = ref(0)
const selectedSlots = ref([])
const monthAvailability = ref(null)
const showFullSchedule = ref(false)
const paymentMethods = ref([])
const isSubmittingBooking = ref(false)

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
  if (monthOffset.value > 0) {
    return true
  }

  return weekIndex.value > firstBookableWeekIndex.value
})
const canGoNext = computed(() => visibleWeeks.value.length > 0)
const hasHiddenSlots = computed(() => {
  if (showFullSchedule.value || !currentWeek.value) {
    return false
  }

  return currentWeek.value.days.some(day => day.slots.length > 8)
})
const currentWeekLabel = computed(() => {
  if (!currentWeek.value) {
    return ''
  }

  const start = new Date(currentWeek.value.week_start)
  const end = new Date(currentWeek.value.week_end)
  const startMonth = start.toLocaleDateString([], { month: 'short' })
  const endMonth = end.toLocaleDateString([], { month: 'short' })
  const year = end.getFullYear()

  if (startMonth === endMonth) {
    return `${startMonth} ${start.getDate()}-${end.getDate()}, ${year}`
  }
})
const tutorProfile = computed(() => ({
  name: tutorDetails.value.name || 'Tutor Name',
  hourlyRate: Number(tutorDetails.value.hourly_rate) || 0,
  rating: Number(tutorDetails.value.rating) || 4.7,
  sessionCount: Number(tutorDetails.value.total_sessions) || 124,
  subjects: tutorDetails.value.subjects?.length
    ? tutorDetails.value.subjects
    : ['Computer Science', 'Beginner Friendly'],
  bio: tutorDetails.value.bio || 'This tutor brings patient, step-by-step guidance for learners building confidence in technical subjects.',
  responseTimeLabel: tutorDetails.value.response_time_label || '',
  pinnedReview: tutorDetails.value.pinned_review
}))
const tutorInitials = computed(() => {
  const parts = tutorProfile.value.name.split(' ').filter(Boolean)
  return parts.slice(0, 2).map(part => part[0]).join('').toUpperCase() || 'SB'
})
const filledStars = computed(() => Math.round(tutorProfile.value.rating))
const paymentSummary = computed(() => {
  const hours = selectedSlots.value.length
  const total = tutorProfile.value.hourlyRate * hours

  return {
    hours,
    total: currencyFormatter.format(total),
    subject: bookedSessionStore.bookedSessionSub || initialBookingStore.selectedSubject || 'Selected sessions',
    tutor: tutorProfile.value.name
  }
})
const paymentFeedback = computed(() => 'Payment is submitted after the session during completion.')
const canConfirmBooking = computed(() => selectedSlots.value.length > 0)

const backButton = () => {
  router.back()
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

function formatShortDay(dayName) {
  return dayName.slice(0, 3)
}

function formatDayHeaderDate(dateString) {
  return new Date(dateString).getDate()
}

function displayedSlots(day) {
  if (showFullSchedule.value) {
    return day.slots
  }

  return day.slots.slice(0, 8)
}

function availabilityBarClass(day) {
  if (day.is_past) {
    return 'day-availability-bar-past'
  }

  if (day.has_available) {
    return 'day-availability-bar-available'
  }

  return 'day-availability-bar-unavailable'
}

const getTutorDetails = async () => {
  try {
    const response = await api.get(`tutors/${tutorID}/`)

    tutorDetails.value = {
      profile_id: response.data.profile_id,
      name: `${response.data.fname} ${response.data.lname}`,
      subjects: response.data.subjects,
      rating: response.data.rating_average ?? 4.7,
      bio: response.data.bio,
      hourly_rate: response.data.hourly_rate ?? 350,
      total_sessions: response.data.total_sessions ?? 124,
      response_time_label: response.data.response_time_label || '',
      pinned_review_id: response.data.pinned_review_id ?? null,
      pinned_review: response.data.pinned_review ?? null
    }
  } catch (error) {
    console.error('Failed to load tutor details.', error)
  }
}

const getPaymentMethods = async () => {
  try {
    const methodsRes = await api.get('payment-methods/')
    let onlinePaymentAdded = false

    paymentMethods.value = methodsRes.data.reduce((methods, method) => {
      if (method.name === 'Cash') {
        methods.push({
          id: method.id,
          label: 'Cash',
          icon: 'bi-cash-coin'
        })
        return methods
      }

      if ((method.name === 'GCash' || method.name === 'Bank Transfer') && !onlinePaymentAdded) {
        methods.push({
          id: method.id,
          label: 'Online Payment',
          icon: 'bi-credit-card'
        })
        onlinePaymentAdded = true
      }

      return methods
    }, [])
  } catch (error) {
    console.error('Failed to load payment methods.', error)
  }
}

function getInitialWeekIndex(weeks) {
  if (!weeks.length) {
    return 0
  }

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
      params: {
        month_offset: monthOffset.value
      }
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

    if (monthOffset.value === 0) {
      return
    }

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

function toggleSlot(day, week, slot) {
  if (slot.is_booked || day.is_past || !day.in_month) {
    return
  }

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
    alert('You can book multiple slots only within the same week.')
    return
  }

  selectedSlots.value.push(slotWithDate)
}

const chooseMethod = (methodId) => {
  paymentStore.selectedMethod = methodId
}

const confirmBooking = async () => {
  if (!canConfirmBooking.value) {
    return
  }

  isSubmittingBooking.value = true

  try {
    bookedSessionStore.bookedSessions = [...selectedSlots.value]
    bookedSessionStore.bookedSessionTutorName = tutorProfile.value.name
    bookedSessionStore.bookedSessionTutorID = tutorID
    bookedSessionStore.bookedSessionSub = bookedSessionStore.bookedSessionSub || initialBookingStore.selectedSubject
    bookedSessionStore.bookedSessionMode = bookedSessionStore.bookedSessionMode || initialBookingStore.selectedMode

    await api.post('bookings/confirm/', {
      tutor_id: tutorID,
      slots: selectedSlots.value,
    })

    alert('Booking Confirmed!')
    paymentStore.reset()
    bookedSessionStore.resetStore()
    selectedSlots.value = []

    router.push({
      name: 'dashboard',
      query: { refresh: Date.now() }
    })
  } catch (error) {
    console.error('Payment error:', error.response?.data || error)
    alert(error.response?.data?.error || 'Something went wrong.')
  } finally {
    isSubmittingBooking.value = false
  }
}

onMounted(async () => {
  paymentStore.reset()
  await Promise.all([
    getTutorDetails(),
    getTutorSchedule(),
    getPaymentMethods()
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

.profile-header {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 20px;
  align-items: start;
}

.avatar-fallback {
  width: 88px;
  height: 88px;
  border-radius: 50%;
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

.rating-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  color: #51685e;
}

.stars {
  display: inline-flex;
  gap: 4px;
  color: #ffb703;
}

.rating-score {
  font-weight: 700;
  color: #163127;
}

.session-count {
  color: #6d8178;
}

.hourly-rate {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 700;
  color: #0a7a51;
}

.subject-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.subject-pill {
  padding: 8px 12px;
  border-radius: 999px;
  background: #f3f7f5;
  color: #315447;
  font-size: 0.9rem;
  font-weight: 600;
}

.profile-meta {
  display: grid;
  gap: 16px;
}

.section-title {
  font-size: 1rem;
  font-weight: 700;
  color: #163127;
  margin-bottom: 8px;
}

.bio-copy,
.review-quote {
  margin: 0;
  color: #53665e;
  line-height: 1.7;
}

.meta-line {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  color: #315447;
  font-weight: 600;
}

.review-quote {
  padding-left: 16px;
  border-left: 3px solid #d3ebe0;
  font-style: italic;
}

.pinned-review {
  display: grid;
  gap: 10px;
  padding: 16px;
  border-radius: 16px;
  background: #f6fbf8;
  border: 1px solid #e1efe7;
}

.pinned-review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.pinned-review-badge,
.pinned-review-rating {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  font-weight: 700;
}

.pinned-review-badge {
  color: #0a7a51;
}

.pinned-review-rating {
  color: #c98300;
}

.review-author {
  margin: 0;
  color: #315447;
  font-weight: 600;
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
  transition: background-color 150ms ease, transform 150ms ease, box-shadow 150ms ease;
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
  font-weight: 600;
  text-align: left;
  cursor: pointer;
  transition: background-color 150ms ease, color 150ms ease, border-color 150ms ease, box-shadow 150ms ease, transform 150ms ease;
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

.slot-link.selected {
  color: #ffffff;
  background: #00895a;
  border-color: #00895a;
  box-shadow: 0 8px 18px rgba(0, 137, 90, 0.18);
  transform: translateY(-1px);
}

.empty-day {
  color: #9aa7b3;
  font-size: 0.9rem;
}

.schedule-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
}

.confirm-booking-btn {
  background: #00895a;
  color: #ffffff;
  border: 0;
  border-radius: 14px;
  padding: 12px 18px;
  font-weight: 700;
}

.confirm-booking-btn:disabled {
  background: #b8c5bf;
  color: #f8faf9;
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

.legend-pill-selected {
  background: rgba(0, 137, 90, 0.12);
  color: #00895a;
  border: 1px solid rgba(0, 137, 90, 0.2);
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

.summary-total .summary-label,
.summary-total .summary-value {
  font-size: 1.05rem;
  font-weight: 700;
}

.payment-method-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(132px, 132px));
  justify-content: center;
  gap: 12px;
  margin-bottom: 14px;
}

.payment-method-card {
  display: grid;
  justify-items: center;
  text-align: center;
  gap: 10px;
  padding: 16px 10px;
  border: 1px solid #e5ebe8;
  border-radius: 16px;
  background: #ffffff;
  color: #315447;
  transition: background-color 150ms ease, border-color 150ms ease, color 150ms ease, box-shadow 150ms ease;
}

.payment-method-card:hover {
  background: #f4f7f6;
}

.payment-method-card.selected {
  border-color: #00895a;
  color: #00895a;
  box-shadow: 0 10px 20px rgba(0, 137, 90, 0.12);
}

.payment-method-icon {
  font-size: 1.4rem;
}

.payment-feedback {
  color: #6c8077;
  margin-bottom: 12px;
  text-align: center;
}

.policy-note {
  margin-bottom: 16px;
  color: #6c8077;
  font-size: 0.92rem;
  text-align: center;
}

.confirm-booking-btn {
  display: block;
  margin: 0 auto;
}

.empty-schedule {
  color: #7a8f86;
  text-align: center;
  padding: 32px 0;
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

  .payment-method-grid {
    grid-template-columns: 1fr;
    justify-content: stretch;
  }

  .profile-header {
    grid-template-columns: 1fr;
  }
}
</style>
