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
          <section class="info-card profile-card shadow-sm position-relative">
            <div class="profile-actions">
              <button class="action-btn" aria-label="Favorite" @click="toggleFavorite">
                <i class="bi" :class="isFavorite ? 'bi-heart-fill text-danger' : 'bi-heart'"></i>
              </button>
              <button class="action-btn" aria-label="Message">
                <i class="bi bi-chat-dots"></i>
              </button>
            </div>

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
                  :key="index"
                  class="subject-accordion-item"
                >
                  <button
                    type="button"
                    class="subject-accordion-header"
                    @click="toggleSubject(index)"
                  >
                    <span>{{ subject }}</span>
                    <i class="bi" :class="expandedSubjects.includes(index) ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
                  </button>

                  <div
                    class="subject-accordion-collapse"
                    :class="{ 'is-expanded': expandedSubjects.includes(index) }"
                  >
                    <div class="subject-accordion-body">
                      <div class="subject-accordion-content">
                        Comprehensive sessions focusing on {{ subject }}. Tailored exactly to your pace and learning style to help you achieve your goals.
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <hr class="my-4" style="border-color: #edf1ef;" />
              <p class="policy-note">Free cancellation up to 24 hours before the session.</p>

              <button
                type="button"
                class="btn confirm-booking-btn w-100"
                :disabled="selectedSlots.length === 0 || isSubmittingBooking"
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
const isSubmittingBooking = ref(false)
const expandedSubjects = ref([])
const isFavorite = ref(false)

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
})

const tutorProfile = computed(() => ({
  name: tutorDetails.value.name || 'Tutor Name',
  hourlyRate: Number(tutorDetails.value.hourly_rate) || 0,
  rating: Number(tutorDetails.value.rating) || 4.7,
  sessionCount: Number(tutorDetails.value.total_sessions) || 124,
  subjects: tutorDetails.value.subjects?.length
    ? tutorDetails.value.subjects
    : ['Computer Science', 'Beginner Friendly', 'Web Development'],
  bio: tutorDetails.value.bio || 'This tutor brings patient, step-by-step guidance for learners building confidence in technical subjects. Additional bio content can easily extend here to test the scrollbar constraint and ensure it is functioning correctly. We are dedicated to providing excellent learning experiences for all ages.',
}))

const tutorInitials = computed(() => {
  const parts = tutorProfile.value.name.split(' ').filter(Boolean)
  return parts.slice(0, 2).map(part => part[0]).join('').toUpperCase() || 'SB'
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

const toggleFavorite = async () => {
  isFavorite.value = !isFavorite.value

  try {
    if (isFavorite.value) {
      await api.post('favorites/add/', { tutor_id: tutorID })
    } else {
      await api.delete(`favorites/remove/${tutorID}/`)
    }
  } catch (error) {
    isFavorite.value = !isFavorite.value
    console.error('Failed to toggle favorite status', error)
    alert('Could not update favorite status. Please try again.')
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
  if (day.is_past) return 'day-availability-bar-past'
  if (day.has_available) return 'day-availability-bar-available'
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
    isFavorite.value = response.data.is_favorite ?? false
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

function toggleSlot(day, week, slot) {
  if (slot.is_booked || day.is_past || !day.in_month) return

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

const confirmBooking = async () => {
  if (selectedSlots.value.length === 0) {
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
      payment_method: 1
    })

    alert('Booking Confirmed!')
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
  transition: all 150ms ease;
}

.action-btn:hover {
  background: #f3f7f5;
  color: #0a7a51;
}

.action-btn:hover .text-danger {
  color: #dc3545 !important;
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
  transition: background-color 150ms ease;
  cursor: pointer;
}

.subject-accordion-header:hover {
  background: #f3f7f5;
}

.subject-accordion-collapse {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 250ms ease-in-out;
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
