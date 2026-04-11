<template>
  <div class="p-1">

    <div class="d-flex mb-4 justify-content-between align-items-center">
        <div>
        <div class="d-flex align-items-center gap-2 flex-wrap">
          <h2 class="fw-bold mb-1">Requested Sessions</h2>
          <span v-if="sessionStore.hasNewPendingRequests" class="request-alert-dot" aria-label="New requests available"></span>
        </div>
        <p class="text-muted mb-0">
            Manage pending session requests.
        </p>
        </div>

        <div style="width: 200px;">
          <input
            type="date"
            v-model="selectedDate"
            class="form-control"
          />
        </div>
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

            <div class="row align-items-center text-center text-md-start">

              <div class="col-md">
                <small class="text-muted">Tutee</small>
                <div class="fw-semibold">
                  {{ session.tuteeName }}
                </div>
              </div>

              <div class="col-md">
                <small class="text-muted">Subject</small>
                <div class="fw-semibold">
                  {{ session.subject }}
                </div>
              </div>

              <div class="col-md">
                <small class="text-muted">Date</small>
                <div class="fw-semibold schedule-stack">
                  <div
                    v-for="(block, index) in getTimeBlocks(session)"
                    :key="`${session.id}-date-${block.date}-${index}`"
                  >
                    {{ formatDisplayDate(block.date) }}
                  </div>
                </div>
              </div>

              <div class="col-md">
                <small class="text-muted">Start Time</small>
                <div class="fw-semibold schedule-stack">
                  <div
                    v-for="(block, index) in getTimeBlocks(session)"
                    :key="`${session.id}-start-${block.startTime}-${index}`"
                  >
                    {{ formatDisplayTime(block.startTime) }}
                  </div>
                </div>
              </div>

              <div class="col-md">
                <small class="text-muted">End Time</small>
                <div class="fw-semibold schedule-stack">
                  <div
                    v-for="(block, index) in getTimeBlocks(session)"
                    :key="`${session.id}-end-${block.endTime}-${index}`"
                  >
                    {{ formatDisplayTime(block.endTime) }}
                  </div>
                </div>
              </div>

              <div class="col-md text-md-end mt-3 mt-md-0">
                <div class="d-grid gap-2">

                <button
                  class="btn btn-sm btn-success"
                  :disabled="confirmingId === session.id"
                  @click="confirmSession(session.id)"
                >
                  {{ confirmingId === session.id ? "Confirming..." : "Confirm" }}
                </button>

                  <button
                    class="btn btn-sm btn-danger"
                    :disabled="rejectingId === session.id"
                    @click="rejectSession(session.id)"
                  >
                    {{ rejectingId === session.id ? "Rejecting..." : "Reject" }}
                  </button>

                </div>
              </div>

            </div>

          </div>
        </div>
        
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSessionsStore } from '@/stores/completedSessions'

const confirmingId = ref(null)
const rejectingId = ref(null)
const sessionStore = useSessionsStore()
const highlightedRequestIds = ref([])

const selectedDate = ref('')

onMounted(async () => {
  await sessionStore.fetchSessions()
  highlightedRequestIds.value = [...sessionStore.unseenPendingRequestIds]
  sessionStore.markPendingRequestsSeen()
})

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
  if (!dateValue) {
    return 'N/A'
  }

  const displayDate = new Date(`${dateValue}T00:00:00`)

  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  }).format(displayDate)
}

const formatDisplayTime = (timeValue) => {
  if (!timeValue) {
    return 'N/A'
  }

  const [hours = 0, minutes = 0] = String(timeValue)
    .split(':')
    .map(part => Number.parseInt(part, 10) || 0)

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
  await sessionStore.approveSession(id)
  confirmingId.value = null
}

const rejectSession = async (id) => {
  rejectingId.value = id
  await sessionStore.rejectSession(id)
  rejectingId.value = null
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
