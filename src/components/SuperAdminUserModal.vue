<template>
  <Teleport to="body">
    <div class="superadmin-modal-backdrop" role="presentation" @click.self="close">
      <section class="superadmin-user-modal" role="dialog" aria-modal="true" aria-labelledby="superadmin-user-title">
        <header class="modal-topbar">
          <div class="user-identity">
            <div class="user-avatar">
              <img v-if="user?.profile_picture_url" :src="user.profile_picture_url" alt="">
              <span v-else>{{ initials }}</span>
            </div>
            <div>
              <p class="eyebrow mb-1">User details</p>
              <h2 id="superadmin-user-title">{{ user?.full_name || 'StudyBuddy user' }}</h2>
              <p class="user-email">{{ user?.email }}</p>
            </div>
          </div>
          <button type="button" class="icon-button" aria-label="Close" @click="close">
            <i class="bi bi-x-lg"></i>
          </button>
        </header>

        <div class="status-row">
          <span :class="roleBadgeClass">{{ user?.role }}</span>
          <span :class="user?.is_suspended ? 'status-badge is-danger' : 'status-badge is-success'">
            {{ user?.is_suspended ? 'Suspended' : 'Active' }}
          </span>
          <span v-if="user?.is_domain_exempt" class="status-badge is-info">Domain exempt</span>
        </div>

        <nav class="tab-row" role="tablist" aria-label="User detail tabs">
          <button
            type="button"
            class="tab-button sb-pill"
            :class="{ active: activeTab === 'profile' }"
            role="tab"
            :aria-selected="activeTab === 'profile'"
            @click="switchTab('profile')"
          >
            Profile
          </button>
          <button
            v-if="user?.role === 'Tutor'"
            type="button"
            class="tab-button sb-pill"
            :class="{ active: activeTab === 'schedule' }"
            role="tab"
            :aria-selected="activeTab === 'schedule'"
            @click="switchTab('schedule')"
          >
            Schedule
          </button>
          <button
            type="button"
            class="tab-button sb-pill"
            :class="{ active: activeTab === 'bookings' }"
            role="tab"
            :aria-selected="activeTab === 'bookings'"
            @click="switchTab('bookings')"
          >
            Bookings
          </button>
          <button
            type="button"
            class="tab-button sb-pill"
            :class="{ active: activeTab === 'actions' }"
            role="tab"
            :aria-selected="activeTab === 'actions'"
            @click="switchTab('actions')"
          >
            Actions
          </button>
        </nav>

        <div v-if="activeTab === 'profile'" class="modal-section">
          <div class="section-heading first-heading">
            <h3>Profile overview</h3>
            <button
              v-if="hasDetailStats"
              type="button"
              class="secondary-action compact"
              :disabled="exporting"
              @click="exportStats"
            >
              Export CSV
            </button>
          </div>
          <dl class="detail-grid">
            <div>
              <dt>Institution</dt>
              <dd>{{ user?.institution_name || 'Unassigned' }}</dd>
            </div>
            <div>
              <dt>Joined</dt>
              <dd>{{ formatDateFull(user?.created_at) }}</dd>
            </div>
            <div>
              <dt>Profile status</dt>
              <dd>{{ user?.profile_completed ? 'Completed' : 'Incomplete' }}</dd>
            </div>
            <div>
              <dt>Domain exemption</dt>
              <dd>{{ user?.is_domain_exempt ? 'Granted' : 'Not granted' }}</dd>
            </div>
            <div v-if="user?.role === 'Tutor'">
              <dt>Wallet balance</dt>
              <dd>PHP {{ formatMoney(user?.wallet_balance || 0) }}</dd>
            </div>
            <div v-if="user?.role === 'Tutor'">
              <dt>Completed sessions</dt>
              <dd>{{ user?.tutor_sessions_completed || 0 }}</dd>
            </div>
            <div v-if="user?.role === 'Tutor'">
              <dt>Average rating</dt>
              <dd>{{ Number(user?.tutor_avg_rating || 0).toFixed(1) }}</dd>
            </div>
          </dl>

          <div v-if="hasDetailStats" class="profile-stats">
            <p v-if="statsLoading" class="empty-state">Loading profile statistics...</p>
            <template v-else-if="userStats">
              <template v-if="user?.role === 'Tutor'">
                <div class="section-heading"><h3>Rating breakdown</h3></div>
                <article class="stats-card rating-card">
                  <div v-for="score in ratingScores" :key="score" class="rating-row">
                    <span>{{ score }} star</span>
                    <span class="rating-track" aria-hidden="true">
                      <span :style="{ width: ratingPercentage(score) + '%' }"></span>
                    </span>
                    <strong>{{ userStats.rating_distribution?.[score] || 0 }}</strong>
                  </div>
                </article>

                <div class="section-heading"><h3>Recent reviews</h3></div>
                <article class="stats-card review-list">
                  <div v-for="(review, index) in userStats.recent_reviews" :key="index" class="review-row">
                    <div><strong>{{ review.reviewer_name }}</strong><span>{{ review.score }} star</span></div>
                    <p>{{ review.comment || 'No written comment.' }}</p>
                  </div>
                  <p v-if="!userStats.recent_reviews?.length" class="empty-state">No reviews yet.</p>
                </article>
              </template>

              <div class="section-heading">
                <h3>{{ user?.role === 'Tutor' ? 'Subjects taught' : 'Subjects learned' }}</h3>
              </div>
              <article class="stats-card chip-list">
                <span v-for="subject in userStats.subjects" :key="subject.name" class="subject-chip">
                  {{ subject.name }}
                  <small v-if="subject.expertise_level != null">Level {{ subject.expertise_level }}</small>
                </span>
                <p v-if="!userStats.subjects?.length" class="empty-state">No subjects recorded.</p>
              </article>

              <div class="section-heading"><h3>Cancellations</h3></div>
              <article class="stats-card cancellation-grid">
                <div><strong>{{ userStats.cancellations.by_user }}</strong><span>By user</span></div>
                <div><strong>{{ userStats.cancellations.by_counterpart }}</strong><span>By counterpart</span></div>
                <div :class="{ 'is-blocked': userStats.cancellations.strike_blocked }">
                  <strong>
                    {{ userStats.cancellations.active_strikes ?? 0 }}<span class="of-cap">/{{ userStats.cancellations.strike_cap ?? 3 }}</span>
                  </strong>
                  <span>
                    Active strikes
                    <small>last {{ userStats.cancellations.strike_window_days ?? 14 }} days</small>
                  </span>
                </div>
              </article>

              <div class="section-heading">
                <h3>Most frequent {{ user?.role === 'Tutor' ? 'students' : 'tutors' }}</h3>
              </div>
              <article class="stats-card counterpart-list">
                <div v-for="counterpart in userStats.top_counterparts" :key="counterpart.name">
                  <strong>{{ counterpart.name }}</strong>
                  <span>{{ counterpart.session_count }} sessions</span>
                </div>
                <p v-if="!userStats.top_counterparts?.length" class="empty-state">No bookings recorded.</p>
              </article>
            </template>
          </div>
        </div>

        <div v-else-if="activeTab === 'schedule'" class="modal-section">
          <div class="section-heading first-heading">
            <h3>Weekly availability</h3>
            <button type="button" class="secondary-action compact" :disabled="exporting" @click="exportAvailability">
              Export CSV
            </button>
          </div>
          <p v-if="availabilityLoading" class="empty-state">Loading schedule...</p>
          <template v-else>
            <div class="schedule-legend" aria-label="Schedule state legend">
              <span><i class="legend-swatch is-open"></i>Open</span>
              <span><i class="legend-swatch is-booked"></i>Booked</span>
              <span><i class="legend-swatch is-inactive"></i>Inactive</span>
            </div>
            <div v-if="availabilityData?.length" class="schedule-grid">
              <span class="schedule-corner"></span>
              <strong v-for="day in scheduleDays" :key="day.value">{{ day.label }}</strong>
              <template v-for="timeSlot in scheduleTimes" :key="timeSlot">
                <span class="schedule-time">{{ formatTime(timeSlot) }}</span>
                <template v-for="day in scheduleDays" :key="`${day.value}-${timeSlot}`">
                  <button
                    v-if="scheduleSlot(day.value, timeSlot)"
                    type="button"
                    class="schedule-cell"
                    :class="`is-${scheduleSlot(day.value, timeSlot).state}`"
                    :aria-label="`${day.label} ${formatTime(timeSlot)}: ${scheduleSlot(day.value, timeSlot).state}`"
                    :disabled="scheduleSlot(day.value, timeSlot).state !== 'booked'"
                    @click="jumpToBooking(scheduleSlot(day.value, timeSlot).booking_id)"
                  >
                    <i v-if="scheduleSlot(day.value, timeSlot).state === 'booked'" class="bi bi-check-lg"></i>
                  </button>
                  <span v-else class="schedule-cell is-empty"></span>
                </template>
              </template>
            </div>
            <p v-else class="empty-state">No weekly availability recorded.</p>
            <p class="schedule-help">Click a booked cell to jump to it in Bookings.</p>
          </template>
        </div>

        <div v-else-if="activeTab === 'bookings'" class="modal-section">
          <div class="section-heading first-heading">
            <h3>Booking history</h3>
            <button type="button" class="secondary-action compact" :disabled="exporting" @click="exportBookings">
              Export CSV
            </button>
          </div>
          <SbDateRangeFilter
            v-model:date-from="customDateFrom"
            v-model:date-to="customDateTo"
            :model-value="bookingFilter"
            :presets="bookingPresets"
            aria-label="Booking date filters"
            class="booking-range-filter"
            @update:model-value="setBookingPreset"
            @apply="applyCustomDates"
          />
          <p v-if="bookingsLoading" class="empty-state">Loading bookings...</p>
          <div v-else class="booking-table-wrap">
            <table class="booking-table">
              <thead>
                <tr>
                  <th>Date</th><th>Time</th><th>Subject</th><th>Tutor</th><th>Tutee</th><th>Mode</th><th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="booking in bookingsData?.results"
                  :key="booking.id"
                  :ref="(element) => setBookingRowRef(booking.id, element)"
                  :class="{ 'is-highlighted': highlightedBookingId === booking.id }"
                >
                  <td>{{ formatDateShort(booking.date) }}</td>
                  <td>{{ formatTime(booking.time) }}</td>
                  <td>{{ booking.subject }}</td>
                  <td>{{ booking.tutor_name }}</td>
                  <td>{{ booking.tutee_name }}</td>
                  <td>{{ booking.mode }}</td>
                  <td><span class="booking-status">{{ booking.status }}</span></td>
                </tr>
                <tr v-if="!bookingsData?.results?.length"><td colspan="7" class="empty-state">No bookings found.</td></tr>
              </tbody>
            </table>
          </div>
          <div v-if="bookingsData?.total" class="pagination-row">
            <span>Page {{ bookingsData.page }} of {{ bookingPageCount }}</span>
            <div>
              <button type="button" class="secondary-action compact" :disabled="bookingsData.page <= 1" @click="changeBookingPage(-1)">Previous</button>
              <button type="button" class="secondary-action compact" :disabled="bookingsData.page >= bookingPageCount" @click="changeBookingPage(1)">Next</button>
            </div>
          </div>
        </div>

        <div v-else-if="activeTab === 'actions'" class="modal-section">
          <div class="action-grid">
            <label class="action-field">
              <span>Role</span>
              <SbSelectModal
                v-model="draftRole"
                :options="roleOptions"
                title="Change Role"
                placeholder="Choose role"
                :searchable="false"
              />
            </label>

            <label class="action-field">
              <span>Institution</span>
              <SbSelectModal
                v-model="draftInstitution"
                :options="institutionOptions"
                title="Change Institution"
                placeholder="Choose institution"
                searchable
                clearable
                clear-label="No institution"
              />
            </label>
          </div>

          <div class="action-stack">
            <button
              type="button"
              class="secondary-action"
              :disabled="busy || user?.is_domain_exempt"
              @click="grantDomainExemption"
            >
              <i class="bi bi-shield-check"></i>
              {{ user?.is_domain_exempt ? 'Domain exemption granted' : 'Grant domain exemption' }}
            </button>

            <div class="danger-action">
              <template v-if="suspendConfirm">
                <p>Confirm {{ user?.is_suspended ? 'reactivation' : 'suspension' }} for this account?</p>
                <div class="confirm-row">
                  <button type="button" class="danger-confirm" :disabled="busy" @click="confirmSuspension">
                    {{ user?.is_suspended ? 'Reactivate' : 'Suspend' }}
                  </button>
                  <button type="button" class="secondary-action compact" :disabled="busy" @click="suspendConfirm = false">
                    Cancel
                  </button>
                </div>
              </template>
              <button v-else type="button" class="danger-outline" :disabled="busy" @click="requestSuspension">
                <i class="bi" :class="user?.is_suspended ? 'bi-arrow-counterclockwise' : 'bi-pause-circle'"></i>
                {{ user?.is_suspended ? 'Reactivate account' : 'Suspend account' }}
              </button>
            </div>

            <div v-if="user?.role === 'Tutor' || user?.role === 'Tutee'" class="dev-tools-action">
              <span class="dev-tools-label">Verification dev tools</span>
              <div class="dev-tools-grid">
                <button type="button" class="secondary-action compact" :disabled="busy" @click="sendDevAction('send_received')">
                  Send received email
                </button>
                <button type="button" class="secondary-action compact" :disabled="busy" @click="sendDevAction('send_approved')">
                  Send approved email
                </button>
                <button type="button" class="secondary-action compact" :disabled="busy" @click="sendDevAction('send_rejected')">
                  Send rejected email
                </button>
                <button type="button" class="secondary-action compact" :disabled="busy" @click="sendDevAction('send_reminder_7day')">
                  Send 7-day reminder
                </button>
                <button type="button" class="secondary-action compact" :disabled="busy" @click="sendDevAction('send_reminder_1day')">
                  Send 1-day reminder
                </button>
                <button type="button" class="secondary-action compact" :disabled="busy" @click="sendDevAction('force_expire')">
                  Force-expire renewal
                </button>
              </div>
            </div>
          </div>
        </div>

        <footer class="modal-footer-actions">
          <button type="button" class="secondary-action compact" :disabled="busy" @click="close">Close</button>
          <button type="button" class="primary-action" :disabled="busy || !hasDirtyFields" @click="saveChanges">
            <span v-if="busy" class="spinner-border spinner-border-sm me-2" role="status"></span>
            Save changes
          </button>
        </footer>
      </section>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import SbDateRangeFilter from '@/components/SbDateRangeFilter.vue'
import SbSelectModal from '@/components/SbSelectModal.vue'
import { getDateKey } from '@/utils/time'
import { useHaptics } from '@/composables/useHaptics'
import { useSuperAdminStore } from '@/stores/superadmin'
import { useToastStore } from '@/stores/toast'

const props = defineProps({
  user: {
    type: Object,
    required: true,
  },
  institutions: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['close', 'updated'])

const store = useSuperAdminStore()
const toastStore = useToastStore()
const { vibrate, patterns } = useHaptics()

const activeTab = ref('profile')
const busy = ref(false)
const suspendConfirm = ref(false)
const draftRole = ref('')
const draftInstitution = ref('')
const userStats = ref(null)
const statsLoaded = ref(false)
const statsLoading = ref(false)
const availabilityData = ref(null)
const availabilityLoaded = ref(false)
const availabilityLoading = ref(false)
const bookingsData = ref(null)
const bookingsLoaded = ref(false)
const bookingsLoading = ref(false)
const bookingPage = ref(1)
const bookingFilter = ref('all')
const bookingDateFrom = ref(null)
const bookingDateTo = ref(null)
const customDateFrom = ref('')
const customDateTo = ref('')
const highlightedBookingId = ref(null)
const bookingRowRefs = new Map()

const ratingScores = [5, 4, 3, 2, 1]
const scheduleDays = [
  { value: 'Mon', label: 'Mon' },
  { value: 'Tue', label: 'Tue' },
  { value: 'Wed', label: 'Wed' },
  { value: 'Thu', label: 'Thu' },
  { value: 'Fri', label: 'Fri' },
  { value: 'Sat', label: 'Sat' },
  { value: 'Sun', label: 'Sun' },
]
const bookingPresets = [
  { value: 'all', label: 'All time' },
  { value: '7', label: 'Last 7 days' },
  { value: '30', label: 'Last 30 days' },
  { value: '90', label: 'Last 90 days' },
  { value: 'custom', label: 'Custom' },
]

const roleOptions = [
  { label: 'Tutee', value: 'Tutee' },
  { label: 'Tutor', value: 'Tutor' },
  { label: 'Admin', value: 'Admin' },
  { label: 'SuperAdmin', value: 'SuperAdmin' },
]

const institutionOptions = computed(() => [
  { label: 'No institution', value: '' },
  ...props.institutions.map((institution) => ({
    label: institution.institution_name,
    value: institution.id,
    description: institution.school_email_domain,
  })),
])

const initials = computed(() => {
  const first = props.user?.fname?.[0] || ''
  const last = props.user?.lname?.[0] || ''
  return `${first}${last}` || 'SB'
})

const roleBadgeClass = computed(() => {
  switch (props.user?.role) {
    case 'SuperAdmin':
      return 'role-badge is-super'
    case 'Admin':
      return 'role-badge is-admin'
    case 'Tutor':
      return 'role-badge is-tutor'
    default:
      return 'role-badge is-tutee'
  }
})

const hasDirtyFields = computed(() =>
  draftRole.value !== props.user?.role ||
  String(draftInstitution.value || '') !== String(props.user?.institution || '')
)

const hasDetailStats = computed(() => ['Tutor', 'Tutee'].includes(props.user?.role))
const exporting = computed(() => store.loading.userExport)
const ratingTotal = computed(() =>
  Object.values(userStats.value?.rating_distribution || {}).reduce(
    (total, count) => total + Number(count),
    0,
  ),
)
const scheduleTimes = computed(() =>
  [...new Set((availabilityData.value || []).map((slot) => slot.time_slot))].sort(),
)
const scheduleSlotMap = computed(() =>
  new Map(
    (availabilityData.value || []).map((slot) => [`${slot.day}-${slot.time_slot}`, slot]),
  ),
)
const bookingPageCount = computed(() =>
  Math.max(1, Math.ceil((bookingsData.value?.total || 0) / (bookingsData.value?.page_size || 10))),
)

watch(
  () => props.user?.id,
  () => {
    const user = props.user
    draftRole.value = user?.role || ''
    draftInstitution.value = user?.institution || ''
    activeTab.value = 'profile'
    suspendConfirm.value = false
    userStats.value = null
    statsLoaded.value = false
    availabilityData.value = null
    availabilityLoaded.value = false
    bookingsData.value = null
    bookingsLoaded.value = false
    bookingPage.value = 1
    bookingFilter.value = 'all'
    bookingDateFrom.value = null
    bookingDateTo.value = null
    customDateFrom.value = ''
    customDateTo.value = ''
    highlightedBookingId.value = null
    bookingRowRefs.clear()
    vibrate(patterns.light)
    if (hasDetailStats.value) loadStats()
  },
  { immediate: true }
)

async function switchTab(tab) {
  activeTab.value = tab
  suspendConfirm.value = false
  vibrate(patterns.light)
  if (tab === 'profile') await loadStats()
  if (tab === 'schedule') await loadAvailability()
  if (tab === 'bookings') await loadBookings()
}

async function loadStats() {
  if (!props.user || !hasDetailStats.value || statsLoaded.value || statsLoading.value) return
  const userId = props.user.id
  statsLoading.value = true
  try {
    const data = await store.fetchUserStats(userId)
    if (props.user?.id === userId) {
      userStats.value = data
      statsLoaded.value = true
    }
  } catch (error) {
    toastStore.push(error.response?.data?.error || 'Failed to load user statistics.', 'error')
  } finally {
    statsLoading.value = false
  }
}

async function loadAvailability() {
  if (!props.user || availabilityLoaded.value || availabilityLoading.value) return
  const userId = props.user.id
  availabilityLoading.value = true
  try {
    const data = await store.fetchUserAvailability(userId)
    if (props.user?.id === userId) {
      availabilityData.value = data
      availabilityLoaded.value = true
    }
  } catch (error) {
    toastStore.push(error.response?.data?.error || 'Failed to load tutor availability.', 'error')
  } finally {
    availabilityLoading.value = false
  }
}

async function loadBookings(force = false, page = bookingPage.value) {
  if (!props.user || (!force && bookingsLoaded.value) || bookingsLoading.value) return
  const userId = props.user.id
  bookingsLoading.value = true
  bookingRowRefs.clear()
  try {
    const data = await store.fetchUserBookings(userId, {
      page,
      dateFrom: bookingDateFrom.value,
      dateTo: bookingDateTo.value,
    })
    if (props.user?.id === userId) {
      bookingsData.value = data
      bookingPage.value = page
      bookingsLoaded.value = true
    }
  } catch (error) {
    toastStore.push(error.response?.data?.error || 'Failed to load booking history.', 'error')
  } finally {
    bookingsLoading.value = false
  }
}

function ratingPercentage(score) {
  if (!ratingTotal.value) return 0
  return (Number(userStats.value?.rating_distribution?.[score] || 0) / ratingTotal.value) * 100
}

function scheduleSlot(day, timeSlot) {
  return scheduleSlotMap.value.get(`${day}-${timeSlot}`)
}

async function setBookingPreset(preset) {
  bookingFilter.value = preset
  highlightedBookingId.value = null
  if (preset === 'custom') return

  bookingDateTo.value = null
  bookingDateFrom.value = null
  if (preset !== 'all') {
    const today = new Date()
    const start = new Date(today)
    start.setDate(start.getDate() - Number(preset) + 1)
    bookingDateFrom.value = getDateKey(start)
    bookingDateTo.value = getDateKey(today)
  }
  bookingPage.value = 1
  await loadBookings(true, 1)
}

async function applyCustomDates() {
  if (customDateFrom.value && customDateTo.value && customDateFrom.value > customDateTo.value) {
    toastStore.push('The start date must be on or before the end date.', 'error')
    return
  }
  bookingDateFrom.value = customDateFrom.value || null
  bookingDateTo.value = customDateTo.value || null
  bookingPage.value = 1
  highlightedBookingId.value = null
  await loadBookings(true, 1)
}

async function changeBookingPage(direction) {
  const nextPage = bookingPage.value + direction
  if (nextPage < 1 || nextPage > bookingPageCount.value) return
  highlightedBookingId.value = null
  await loadBookings(true, nextPage)
}

function setBookingRowRef(bookingId, element) {
  if (element) bookingRowRefs.set(bookingId, element)
  else bookingRowRefs.delete(bookingId)
}

async function jumpToBooking(bookingId) {
  if (!bookingId) return
  activeTab.value = 'bookings'
  bookingFilter.value = 'all'
  bookingDateFrom.value = null
  bookingDateTo.value = null
  highlightedBookingId.value = bookingId

  await loadBookings(true, 1)
  let page = 1
  const pageCount = bookingPageCount.value
  while (!bookingsData.value?.results?.some((booking) => booking.id === bookingId) && page < pageCount) {
    page += 1
    await loadBookings(true, page)
  }
  await nextTick()
  bookingRowRefs.get(bookingId)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

async function exportStats() {
  try {
    await store.exportUserStatsCsv(props.user.id)
  } catch {
    toastStore.push('Failed to export profile statistics.', 'error')
  }
}

async function exportAvailability() {
  try {
    await store.exportUserAvailabilityCsv(props.user.id)
  } catch {
    toastStore.push('Failed to export tutor availability.', 'error')
  }
}

async function exportBookings() {
  try {
    await store.exportUserBookingsCsv(props.user.id, {
      dateFrom: bookingDateFrom.value,
      dateTo: bookingDateTo.value,
    })
  } catch {
    toastStore.push('Failed to export booking history.', 'error')
  }
}

function formatTime(timeString) {
  if (!timeString) return ''
  return new Intl.DateTimeFormat('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  }).format(new Date(`1970-01-01T${timeString}:00`))
}

function formatDateShort(dateString) {
  if (!dateString) return ''
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date(`${dateString}T00:00:00`))
}

function close() {
  vibrate(patterns.light)
  emit('close')
}

async function saveChanges() {
  if (!props.user || !hasDirtyFields.value) return

  busy.value = true
  vibrate(patterns.medium)

  try {
    let updated = props.user
    if (draftRole.value !== props.user.role) {
      updated = await store.updateUserRole(props.user.id, draftRole.value)
    }
    if (String(draftInstitution.value || '') !== String(updated.institution || '')) {
      updated = await store.updateUserInstitution(props.user.id, draftInstitution.value || null)
    }
    toastStore.push('User updated successfully.')
    emit('updated', updated)
  } catch {
    toastStore.push('Failed to update user.', 'error')
  } finally {
    busy.value = false
  }
}

async function grantDomainExemption() {
  if (!props.user || props.user.is_domain_exempt) return

  busy.value = true
  vibrate(patterns.medium)

  try {
    const updated = await store.toggleDomainExemption(props.user.id, true)
    toastStore.push('Domain exemption granted.')
    emit('updated', updated)
  } catch {
    toastStore.push('Failed to grant domain exemption.', 'error')
  } finally {
    busy.value = false
  }
}

function requestSuspension() {
  suspendConfirm.value = true
  vibrate(patterns.light)
}

async function confirmSuspension() {
  if (!props.user) return

  busy.value = true
  vibrate(patterns.celebratory)

  try {
    const updated = await store.updateUserStatus(props.user.id, !props.user.is_suspended)
    toastStore.push(updated.is_suspended ? 'User suspended.' : 'User reactivated.')
    suspendConfirm.value = false
    emit('updated', updated)
  } catch {
    toastStore.push('Failed to update user status.', 'error')
  } finally {
    busy.value = false
  }
}

async function sendDevAction(action) {
  if (!props.user) return

  busy.value = true
  try {
    await store.sendVerificationDevAction(props.user.id, action)
    toastStore.push(`'${action}' triggered.`)
  } catch (err) {
    toastStore.push(err.response?.data?.error || 'Dev action failed.', 'error')
  } finally {
    busy.value = false
  }
}

function formatDateFull(value) {
  if (!value) return 'N/A'
  return new Date(value).toLocaleString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function formatMoney(value) {
  return Number(value || 0).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}
</script>

<style scoped>
.superadmin-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1080;
  background: rgba(10, 25, 22, 0.42);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.superadmin-user-modal {
  width: min(760px, 100%);
  max-height: min(760px, calc(100vh - 48px));
  overflow: auto;
  background: var(--sb-card-bg, #fff);
  color: var(--sb-text-main, #163127);
  border: 1px solid var(--sb-card-border, #e4e8e6);
  border-radius: 18px;
  box-shadow: 0 24px 80px rgba(10, 25, 22, 0.22);
}

.modal-topbar,
.modal-footer-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 22px 24px;
}

.modal-topbar {
  border-bottom: 1px solid var(--sb-card-border, #e4e8e6);
}

.user-identity {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}

.user-avatar {
  width: 58px;
  height: 58px;
  border-radius: 50%;
  background: var(--sb-primary, #00895a);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
  flex: 0 0 auto;
  overflow: hidden;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.eyebrow {
  color: var(--sb-text-muted, #6b7280);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
}

h2 {
  font-size: 24px;
  line-height: 1.2;
  font-weight: 700;
  margin: 0;
}

.user-email {
  color: var(--sb-text-muted, #6b7280);
  margin: 3px 0 0;
  word-break: break-word;
}

.icon-button {
  width: 38px;
  height: 38px;
  border-radius: 999px;
  border: 1px solid var(--sb-card-border, #e4e8e6);
  background: #fff;
  color: var(--sb-text-main, #163127);
}

.status-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 18px 24px 0;
}

.role-badge,
.status-badge {
  border-radius: 999px;
  padding: 5px 12px;
  font-size: 12px;
  font-weight: 700;
}

.role-badge.is-super { background: #111827; color: #fff; }
.role-badge.is-admin { background: #f5f3ff; color: #5b21b6; }
.role-badge.is-tutor { background: #edf6f1; color: var(--sb-primary, #00895a); }
.role-badge.is-tutee { background: #eff6ff; color: #1d4ed8; }
.status-badge.is-success { background: #ecfdf5; color: #047857; }
.status-badge.is-danger { background: #fef2f2; color: #991b1b; }
.status-badge.is-info { background: #eff6ff; color: #1d4ed8; }

.tab-row {
  display: flex;
  gap: 6px;
  padding: 18px 24px 0;
}

.tab-button {
  border: 1px solid var(--sb-card-border, #e4e8e6);
  background: #fff;
  color: var(--sb-text-muted, #6b7280);
  border-radius: 999px;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 700;
}

.tab-button.active {
  background: var(--sb-primary, #00895a);
  border-color: var(--sb-primary, #00895a);
  color: #fff;
}

.modal-section {
  padding: 22px 24px;
}

.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 24px 0 10px;
}

.section-heading.first-heading {
  margin-top: 0;
}

.section-heading h3 {
  margin: 0;
  color: var(--sb-text-main);
  font-size: 14px;
  font-weight: 800;
}

.profile-stats {
  margin-top: 24px;
}

.stats-card {
  border: 1px solid var(--sb-card-border);
  border-radius: 14px;
  padding: 16px;
  background: var(--sb-card-bg);
}

.rating-card,
.review-list,
.counterpart-list {
  display: grid;
  gap: 12px;
}

.rating-row {
  display: grid;
  grid-template-columns: 52px 1fr 28px;
  align-items: center;
  gap: 10px;
  color: var(--sb-text-muted);
  font-size: 12px;
}

.rating-row strong {
  color: var(--sb-text-main);
  text-align: right;
}

.rating-track {
  height: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: color-mix(in srgb, var(--sb-card-border) 75%, transparent);
}

.rating-track span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--sb-primary);
}

.review-row + .review-row,
.counterpart-list div + div {
  border-top: 1px solid var(--sb-card-border);
  padding-top: 12px;
}

.review-row div,
.counterpart-list div {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.review-row span,
.counterpart-list span {
  color: var(--sb-text-muted);
  font-size: 12px;
}

.review-row p {
  margin: 6px 0 0;
  color: var(--sb-text-muted);
  font-size: 13px;
}

.chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.subject-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  border: 1px solid color-mix(in srgb, var(--sb-primary) 25%, var(--sb-card-border));
  border-radius: 999px;
  padding: 6px 10px;
  background: color-mix(in srgb, var(--sb-primary) 8%, var(--sb-card-bg));
  color: var(--sb-primary);
  font-size: 12px;
  font-weight: 700;
}

.subject-chip small {
  color: var(--sb-text-muted);
}

.cancellation-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.cancellation-grid div {
  display: grid;
  gap: 2px;
  text-align: center;
}

.cancellation-grid strong {
  color: var(--sb-text-main);
  font-size: 24px;
}

.cancellation-grid span {
  color: var(--sb-text-muted);
  font-size: 12px;
}

.cancellation-grid small {
  display: block;
  font-size: 11px;
  opacity: 0.75;
}

/* The cap is what matters at a glance -- a user sitting at 3/3 is blocked from booking right now. */
.cancellation-grid .is-blocked strong {
  color: var(--sb-danger);
}

.cancellation-grid .of-cap {
  color: var(--sb-text-muted);
  font-size: 15px;
  font-weight: 700;
}

.empty-state {
  margin: 0;
  padding: 16px;
  color: var(--sb-text-muted);
  text-align: center;
}

.schedule-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-bottom: 14px;
  color: var(--sb-text-muted);
  font-size: 12px;
}

.legend-swatch {
  display: inline-block;
  width: 10px;
  height: 10px;
  margin-right: 5px;
  border-radius: 3px;
  vertical-align: -1px;
}

.legend-swatch.is-open,
.schedule-cell.is-open {
  border-color: color-mix(in srgb, var(--sb-primary) 35%, var(--sb-card-border));
  background: color-mix(in srgb, var(--sb-primary) 10%, var(--sb-card-bg));
}

.legend-swatch.is-booked,
.schedule-cell.is-booked {
  border-color: var(--sb-primary);
  background: var(--sb-primary);
  color: var(--sb-card-bg);
}

.legend-swatch.is-inactive,
.schedule-cell.is-inactive {
  border-color: var(--sb-card-border);
  background: color-mix(in srgb, var(--sb-card-border) 55%, var(--sb-card-bg));
}

.schedule-grid {
  display: grid;
  grid-template-columns: 64px repeat(7, minmax(50px, 1fr));
  gap: 5px;
  min-width: 520px;
  overflow-x: auto;
  align-items: center;
}

.schedule-grid > strong,
.schedule-time {
  color: var(--sb-text-muted);
  font-size: 11px;
  text-align: center;
}

.schedule-cell {
  min-height: 34px;
  border: 1px solid var(--sb-card-border);
  border-radius: 7px;
}

.schedule-cell:disabled {
  cursor: default;
}

.schedule-cell.is-empty {
  background: transparent;
  border-style: dashed;
  opacity: 0.45;
}

.schedule-help {
  margin: 10px 0 0;
  color: var(--sb-text-muted);
  font-size: 12px;
}

.booking-table-wrap {
  overflow-x: auto;
  border: 1px solid var(--sb-card-border);
  border-radius: 12px;
}

.booking-table {
  width: 100%;
  min-width: 820px;
  border-collapse: collapse;
  font-size: 12px;
}

.booking-table th,
.booking-table td {
  padding: 11px 10px;
  border-bottom: 1px solid var(--sb-card-border);
  text-align: left;
  white-space: nowrap;
}

.booking-table th {
  color: var(--sb-text-muted);
  font-size: 10px;
  text-transform: uppercase;
}

.booking-table tbody tr:last-child td {
  border-bottom: 0;
}

.booking-table tr.is-highlighted {
  background: color-mix(in srgb, var(--sb-primary) 13%, var(--sb-card-bg));
  outline: 2px solid var(--sb-primary);
  outline-offset: -2px;
}

.booking-status {
  display: inline-flex;
  border-radius: 999px;
  padding: 4px 8px;
  background: color-mix(in srgb, var(--sb-primary) 8%, var(--sb-card-bg));
  color: var(--sb-text-main);
  font-weight: 700;
}

.pagination-row,
.pagination-row div {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-row {
  justify-content: space-between;
  margin-top: 14px;
  color: var(--sb-text-muted);
  font-size: 12px;
}

.detail-grid,
.action-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.detail-grid div,
.action-field {
  border: 1px solid var(--sb-card-border, #e4e8e6);
  border-radius: 14px;
  padding: 14px;
  background: color-mix(in srgb, var(--sb-primary, #00895a) 3%, #fff);
}

dt,
.action-field span {
  color: var(--sb-text-muted, #6b7280);
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  margin-bottom: 6px;
}

dd {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
}

.action-field {
  display: grid;
  gap: 8px;
}

.action-stack {
  display: grid;
  gap: 12px;
  margin-top: 16px;
}

.primary-action,
.secondary-action,
.danger-outline,
.danger-confirm {
  border-radius: 999px;
  border: 1px solid transparent;
  padding: 10px 18px;
  font-size: 14px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.primary-action {
  background: var(--sb-primary, #00895a);
  color: #fff;
}

.primary-action:disabled,
.secondary-action:disabled,
.danger-outline:disabled {
  opacity: 0.62;
  cursor: not-allowed;
}

.secondary-action {
  background: #fff;
  border-color: var(--sb-card-border, #e4e8e6);
  color: var(--sb-text-main, #163127);
}

.secondary-action.compact {
  padding-inline: 16px;
}

.danger-outline {
  background: #fff;
  border-color: #fecaca;
  color: #991b1b;
}

.danger-action {
  border: 1px solid #fecaca;
  border-radius: 14px;
  background: #fef2f2;
  padding: 14px;
}

.danger-action p {
  margin: 0 0 12px;
  color: #991b1b;
  font-weight: 700;
}

.danger-confirm {
  background: #ef4444;
  color: #fff;
}

.confirm-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.dev-tools-action {
  border: 1px solid var(--sb-card-border, #e4e8e6);
  border-radius: 14px;
  background: var(--sb-surface-variant, #f8f9fa);
  padding: 14px;
}

.dev-tools-label {
  display: block;
  margin: 0 0 12px;
  color: var(--sb-text-muted, #5b6660);
  font-weight: 700;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.dev-tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px;
}

.modal-footer-actions {
  border-top: 1px solid var(--sb-card-border, #e4e8e6);
}

@media (max-width: 640px) {
  .superadmin-modal-backdrop {
    align-items: stretch;
    padding: 12px;
  }

  .modal-topbar,
  .modal-footer-actions,
  .user-identity {
    align-items: flex-start;
  }

  .modal-footer-actions,
  .detail-grid,
  .action-grid {
    grid-template-columns: 1fr;
  }

  .modal-footer-actions {
    display: grid;
  }
}
</style>
