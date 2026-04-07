<template>
  <div class="p-1">

    <div class="d-flex mb-4 justify-content-between align-items-center">
        <div>
        <h2 class="fw-bold mb-1">Requested Sessions</h2>
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
                <div class="fw-semibold">
                  {{ session.date }}
                </div>
              </div>

              <div class="col-md">
                <small class="text-muted">Start Time</small>
                <div class="fw-semibold">
                  {{ session.startTime }}
                </div>
              </div>

              <div class="col-md">
                <small class="text-muted">End Time</small>
                <div class="fw-semibold">
                  {{ session.endTime }}
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

const selectedDate = ref('')

onMounted(() => {
  sessionStore.fetchSessions()
})

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
      session.date === selectedDate.value
    )
  }

  return sessions
})
</script>

<style scoped>
.session-card {
  cursor: pointer;
  transition: all 0.2s ease;
}

.session-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(0,0,0,0.08);
}
</style>
