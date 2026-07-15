<template>
  <div class="p-1">

    <div class="d-flex mb-4 justify-content-between align-items-center">
        <div style="width: 200px;">
          <input
            type="date"
            v-model="selectedDate"
            class="form-control sb-field"
          />
        </div>
    </div>

    <div v-if="actionError" class="alert alert-danger rounded-4 border-0 mb-3">
      {{ actionError }}
    </div>

    <div v-if="filteredSessions.length === 0" class="text-center text-muted py-5">
        No pending session requests found.
    </div>
    
    <div v-else>
        <div
          v-for="session in filteredSessions"
          :key="session.id"
          class="card border mb-2 rounded-4 shadow-sm request-card"
          :class="{ 'request-card-attention': isHighlightedRequest(session.id) }"
          @mouseenter="clearHighlight(session.id)"
        >
          <div class="card-body py-3">
            
            <div class="row text-center">

              <div class="col-md mb-3 mb-md-0 d-flex flex-column">
                <small class="text-muted mb-2">Tutee</small>
                <div class="fw-semibold my-auto">{{ session.tuteeName }}</div>
              </div>

              <div class="col-md mb-3 mb-md-0 d-flex flex-column">
                <small class="text-muted mb-2">Subject</small>
                <div class="fw-semibold my-auto">{{ session.subject }}</div>
              </div>

              <div class="col-md mb-3 mb-md-0 d-flex flex-column">
                <small class="text-muted mb-2">Date</small>
                <div class="fw-semibold schedule-stack my-auto">
                  <div v-for="(block, index) in getTimeBlocks(session)" :key="`${session.id}-date-${block.date}-${index}`">
                    {{ formatDisplayDate(block.date) }}
                  </div>
                </div>
              </div>

              <div class="col-md mb-3 mb-md-0 d-flex flex-column">
                <small class="text-muted mb-2">Start Time</small>
                <div class="fw-semibold schedule-stack my-auto">
                  <div v-for="(block, index) in getTimeBlocks(session)" :key="`${session.id}-start-${block.startTime}-${index}`">
                    {{ formatDisplayTime(block.startTime) }}
                  </div>
                </div>
              </div>

              <div class="col-md mb-3 mb-md-0 d-flex flex-column">
                <small class="text-muted mb-2">End Time</small>
                <div class="fw-semibold schedule-stack my-auto">
                  <div v-for="(block, index) in getTimeBlocks(session)" :key="`${session.id}-end-${block.endTime}-${index}`">
                    {{ formatDisplayTime(block.endTime) }}
                  </div>
                </div>
              </div>

              <div class="col-md mb-3 mb-md-0 d-flex flex-column">
                <small class="text-muted mb-2">Location</small>
                <div class="my-auto">
                  <div v-if="session.session_mode === 'Online'" class="text-muted small">Online</div>
                  <div v-else class="d-flex align-items-center gap-2 justify-content-center">
                    <span :class="{ 'text-muted small': !session.preferred_location }">
                      {{ session.preferred_location || 'No location set' }}
                    </span>
                    
                    <button 
                      class="btn btn-sm btn-link p-0 text-decoration-none text-muted sb-btn" 
                      @click="openLocationModal(session)"
                      title="Edit location"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" class="bi bi-pencil-square" viewBox="0 0 16 16">
                        <path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/>
                        <path fill-rule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5v11z"/>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>

              <div class="col-md d-flex flex-column">
                <small class="text-muted mb-2 d-none d-md-block">Actions</small> <div class="d-flex gap-2 justify-content-center my-auto">
                  
                  <button 
                    class="btn btn-sm btn-outline-success rounded-circle d-flex align-items-center justify-content-center sb-btn" 
                    style="width: 42px; height: 42px;"
                    :disabled="tutorRenewalRequired || confirmingId === session.id" 
                    @click="confirmSession(session.id)"
                    :title="tutorRenewalRequired ? 'Renew your verification to confirm sessions' : 'Confirm Session'"
                    :aria-label="tutorRenewalRequired ? 'Renew your verification to confirm sessions' : 'Confirm Session'"
                  >
                    <span v-if="confirmingId === session.id" class="spinner-border spinner-border-sm" aria-hidden="true"></span>
                    <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-check-lg" viewBox="0 0 16 16">
                      <path d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425a.247.247 0 0 1 .02-.022Z"/>
                    </svg>
                  </button>

                  <button 
                    class="btn btn-sm btn-outline-danger rounded-circle d-flex align-items-center justify-content-center sb-btn" 
                    style="width: 42px; height: 42px;"
                    :disabled="rejectingId === session.id" 
                    @click="rejectSession(session.id)"
                    title="Reject Session"
                    aria-label="Reject Session"
                  >
                    <span v-if="rejectingId === session.id" class="spinner-border spinner-border-sm" aria-hidden="true"></span>
                    <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-x-lg" viewBox="0 0 16 16">
                      <path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8 2.146 2.854Z"/>
                    </svg>
                  </button>

                </div>
              </div>

            </div>
          </div>
        </div>
    </div>

    <Teleport to="body">
      <div ref="locationModalRef" class="modal fade" id="locationModal" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content rounded-4">
            
            <div class="modal-header border-0 pb-0">
              <h5 class="modal-title fw-bold">Edit Location</h5>
              <button type="button" class="btn-close" @click="closeLocationModal" aria-label="Close"></button>
            </div>
            
            <div class="modal-body text-muted">
              <p class="mb-3">
                Set location for session with <span class="fw-semibold text-dark">{{ activeSession?.tuteeName }}</span>
              </p>
              <input
                type="text"
                class="form-control shadow-none sb-field"
                v-model="tempLocation"
                @keyup.enter="saveLocation"
                @keyup.esc="closeLocationModal"
                placeholder="Enter location (e.g. Library, Cafe)"
              />
            </div>
            
            <div class="modal-footer border-0 pt-0">
              <button type="button" class="btn btn-light sb-btn" @click="closeLocationModal">Cancel</button>
              <button type="button" class="btn bg-sb-primary text-white sb-btn" @click="saveLocation">Save Location</button>
            </div>
            
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div
        v-if="sessionLoadLimitModalOpen"
        class="modal-backdrop show"
        style="display: block;"
        @click.self="closeSessionLoadLimitModal"
      >
        <div class="modal d-block" tabindex="-1" role="dialog" aria-modal="true">
          <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content rounded-4">
              <div class="modal-header border-0 pb-0">
                <div>
                  <h5 class="modal-title fw-bold">Accepted session limit reached</h5>
                  <p class="small text-muted mb-0">You need to clear some accepted sessions first.</p>
                </div>
                <button type="button" class="btn-close" @click="closeSessionLoadLimitModal" aria-label="Close"></button>
              </div>
              <div class="modal-body">
                <p class="mb-2">
                  You currently have <strong>{{ sessionLoadLimitModalLoad }}</strong>
                  accepted session group{{ sessionLoadLimitModalLoad === 1 ? '' : 's' }} out of
                  <strong>{{ sessionLoadLimitModalLimit }}</strong> allowed.
                </p>
                <p class="mb-0 text-muted">
                  Manage the sessions you already accepted, or open Help to send a support ticket to your institution admin if you need an exception.
                </p>
              </div>
              <div class="modal-footer border-0 pt-0">
                <button type="button" class="btn btn-light sb-btn" @click="closeSessionLoadLimitModal">Close</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, onBeforeUnmount, onMounted } from 'vue'
import { useSessionsStore } from '@/stores/completedSessions'
import { useProfileStore } from '@/stores/profile'
import api from '@/services/api/api'
import * as bootstrap from 'bootstrap'
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()
const confirmingId = ref(null)
const rejectingId = ref(null)
const sessionStore = useSessionsStore()
const profileStore = useProfileStore()
const highlightedRequestIds = ref([])
const selectedDate = ref('')
const actionError = ref('')
const sessionLoadLimitModalOpen = ref(false)
const sessionLoadLimitModalLoad = ref(0)
const sessionLoadLimitModalLimit = ref(10)
const tutorRenewalRequired = computed(() => Boolean(profileStore.tutorRenewalRequired))

// Modal Refs
const locationModalRef = ref(null)
const activeSession = ref(null)
const tempLocation = ref('')

const resetLocationModal = () => {
  activeSession.value = null
  tempLocation.value = ''
}

onMounted(async () => {
  await sessionStore.fetchSessions()
  highlightedRequestIds.value = [...sessionStore.unseenPendingRequestIds]
  sessionStore.markPendingRequestsSeen()

  locationModalRef.value?.addEventListener('hidden.bs.modal', resetLocationModal)
})

onBeforeUnmount(() => {
  if (locationModalRef.value) {
    const modalInstance = bootstrap.Modal.getInstance(locationModalRef.value)
    modalInstance?.hide()
    modalInstance?.dispose()
    locationModalRef.value.removeEventListener('hidden.bs.modal', resetLocationModal)
  }
})

const openLocationModal = (session) => {
  activeSession.value = session
  tempLocation.value = session.preferred_location || ''
  
  if (locationModalRef.value) {
    const modalInstance = bootstrap.Modal.getOrCreateInstance(locationModalRef.value)
    modalInstance.show()
  }
}

const closeLocationModal = () => {
  if (locationModalRef.value) {
    const modalInstance = bootstrap.Modal.getInstance(locationModalRef.value)
    modalInstance?.hide()
  }
}

const closeSessionLoadLimitModal = () => {
  sessionLoadLimitModalOpen.value = false
}

const saveLocation = async () => {
  if (!activeSession.value) return;

  const session = activeSession.value;
  const id = session.booking_request_id || session.id;

  try {
    await api.patch(`/bookings/${id}/location/`, { preferred_location: tempLocation.value })
    
    session.preferred_location = tempLocation.value
    
    closeLocationModal() 
  } catch (err) {
    console.error('Failed to update location', err)
    toastStore.push(err.response?.data?.error || 'Failed to save location. Please try again.', 'error')
  }
}

const isHighlightedRequest = (sessionId) =>
  highlightedRequestIds.value.includes(String(sessionId))

const clearHighlight = (sessionId) => {
  highlightedRequestIds.value = highlightedRequestIds.value.filter(id => id !== String(sessionId))
}

const getTimeBlocks = (session) => {
  if (Array.isArray(session.timeBlocks) && session.timeBlocks.length > 0) {
    return session.timeBlocks
  }

  return [{
    date: session.date,
    startTime: session.startTime,
    endTime: session.endTime
  }]
}

const formatDisplayDate = (dateValue) => {
  if (!dateValue) return 'N/A'
  const displayDate = new Date(`${dateValue}T00:00:00`)
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  }).format(displayDate)
}

const formatDisplayTime = (timeValue) => {
  if (!timeValue) return 'N/A'
  const [hours = 0, minutes = 0] = String(timeValue).split(':').map(part => Number.parseInt(part, 10) || 0)
  const displayDate = new Date()
  displayDate.setHours(hours, minutes, 0, 0)

  return new Intl.DateTimeFormat('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  }).format(displayDate)
}

const confirmSession = async (id) => {
  if (tutorRenewalRequired.value) {
    return
  }

  confirmingId.value = id
  actionError.value = ''
  closeSessionLoadLimitModal()

  try {
    await sessionStore.approveSession(id)
  } catch (error) {
    const errorCode = error.response?.data?.code
    if (errorCode === 'session_load_limit_reached') {
      sessionLoadLimitModalLoad.value = Number(error.response?.data?.accepted_session_load || 0)
      sessionLoadLimitModalLimit.value = Number(error.response?.data?.session_load_limit || 10)
      sessionLoadLimitModalOpen.value = true
      actionError.value = ''
    } else {
      actionError.value =
        error.response?.data?.error || 'Unable to confirm this session. Please refresh and try again.'
    }

    await sessionStore.fetchSessions()
  } finally {
    confirmingId.value = null
  }
}

const rejectSession = async (id) => {
  rejectingId.value = id
  actionError.value = ''

  try {
    await sessionStore.rejectSession(id)
  } catch (error) {
    actionError.value =
      error.response?.data?.error || 'Unable to reject this session. Please refresh and try again.'

    await sessionStore.fetchSessions()
  } finally {
    rejectingId.value = null
  }
}

const filteredSessions = computed(() => {
  let sessions = sessionStore.requestedSessions

  if (selectedDate.value) {
    sessions = sessions.filter(session =>
      getTimeBlocks(session).some(block => block.date === selectedDate.value)
    )
  }

  return sessions
})
</script>

<style scoped>
.request-alert-dot {
  display: inline-flex;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #dc2626;
  box-shadow: 0 0 0 4px rgba(220, 38, 38, 0.14);
  flex-shrink: 0;
}

.request-card {
  transition: transform var(--sb-t-normal) var(--sb-spring);
}

.schedule-stack {
  display: grid;
  gap: 0.2rem;
}

.request-card-attention {
  border-color: rgba(0, 137, 90, 0.32) !important;
  box-shadow: 0 0 0 4px rgba(0, 137, 90, 0.14), 0 12px 24px rgba(0, 137, 90, 0.08);
}

.request-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12);
}

.request-card-attention:hover {
  border-color: var(--sb-card-border, #eaeaea) !important;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12);
}

</style>
