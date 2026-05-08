<template>
  <div class="p-1">

    <div class="d-flex mb-4 justify-content-between align-items-center">
        <div style="width: 200px;">
          <input
            type="date"
            v-model="selectedDate"
            class="form-control"
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
                      class="btn btn-sm btn-link p-0 text-decoration-none text-muted" 
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
                    class="btn btn-sm btn-outline-success rounded-circle d-flex align-items-center justify-content-center" 
                    style="width: 42px; height: 42px;"
                    :disabled="confirmingId === session.id" 
                    @click="confirmSession(session.id)"
                    title="Confirm Session"
                    aria-label="Confirm Session"
                  >
                    <span v-if="confirmingId === session.id" class="spinner-border spinner-border-sm" aria-hidden="true"></span>
                    <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-check-lg" viewBox="0 0 16 16">
                      <path d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425a.247.247 0 0 1 .02-.022Z"/>
                    </svg>
                  </button>

                  <button 
                    class="btn btn-sm btn-outline-danger rounded-circle d-flex align-items-center justify-content-center" 
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
              class="form-control shadow-none"
              v-model="tempLocation"
              @keyup.enter="saveLocation"
              @keyup.esc="closeLocationModal"
              placeholder="Enter location (e.g. Library, Cafe)"
            />
          </div>
          
          <div class="modal-footer border-0 pt-0">
            <button type="button" class="btn btn-light" @click="closeLocationModal">Cancel</button>
            <button type="button" class="btn bg-sb-primary text-white" @click="saveLocation">Save Location</button>
          </div>
          
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSessionsStore } from '@/stores/completedSessions'
import api from '@/services/api/api'
import * as bootstrap from 'bootstrap'

const confirmingId = ref(null)
const rejectingId = ref(null)
const sessionStore = useSessionsStore()
const highlightedRequestIds = ref([])
const selectedDate = ref('')
const actionError = ref('')

// Modal Refs
const locationModalRef = ref(null)
const activeSession = ref(null)
const tempLocation = ref('')

onMounted(async () => {
  await sessionStore.fetchSessions()
  highlightedRequestIds.value = [...sessionStore.unseenPendingRequestIds]
  sessionStore.markPendingRequestsSeen()
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
  
  activeSession.value = null
  tempLocation.value = ''
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
    alert(err.response?.data?.error || 'Failed to save location. Please try again.')
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
  confirmingId.value = id
  actionError.value = ''

  try {
    await sessionStore.approveSession(id)
  } catch (error) {
    actionError.value =
      error.response?.data?.error || 'Unable to confirm this session. Please refresh and try again.'

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
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease, background-color 180ms ease;
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
