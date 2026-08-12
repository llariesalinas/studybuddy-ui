<template>
  <div class="admin-support-container">
    <div class="card sb-card-surface border-1 shadow-sm rounded-4" style="height: 520px;">
      <div class="card-body p-4 p-md-5 d-flex flex-column overflow-hidden">
        <h4 class="fw-bold sb-text mb-4 d-flex align-items-center">
          <i class="bi bi-headset text-sb-primary me-3"></i> Tickets
        </h4>

        <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4">
          <div class="d-flex gap-2 mb-4 filter-bar p-2 rounded-3 d-inline-flex">
            <button
              v-for="status in statusTabs"
              :key="status"
              @click="filters.status = status"
              class="btn rounded-pill px-3 py-1 fw-semibold shadow-none sb-btn sb-pill filter-tab"
              :class="{ 'filter-tab-active': filters.status === status }"
              :aria-pressed="filters.status === status"
            >
              {{ status.replace('_', ' ') }} ({{ getCount(status) }})
            </button>
          </div>

          <div class="input-group" style="max-width: 300px;">
            <span class="input-group-text sb-input-addon border-end-0">
              <i class="bi bi-search"></i>
            </span>
            <input
              v-model="filters.search"
              type="text"
              class="form-control border-start-0 shadow-none sb-search-input sb-field"
              placeholder="Search subject or user..."
            />
          </div>
        </div>

        <div class="flex-grow-1 overflow-auto" style="min-height: 0;">
          <table class="table table-hover align-middle mb-0 sb-themed-table">
            <thead>
              <tr class="sb-muted small" style="border-bottom: 2px solid var(--sb-card-border);">
                <th class="ps-4 py-3">Reporter</th>
                <th class="py-3">Category</th>
                <th class="py-3">Subject</th>
                <th class="py-3">Opened</th>
                <th class="py-3">Assigned Agent</th>
                <th class="pe-4 py-3 text-end">Actions</th>
              </tr>
            </thead>

            <tbody>
              <tr v-if="loading">
                <td colspan="6" class="text-center py-5 sb-muted">
                  <div class="spinner-border text-primary mb-2" role="status"></div>
                  <div>Loading tickets...</div>
                </td>
              </tr>

              <tr
                v-else-if="filteredTickets.length > 0"
                v-for="ticket in filteredTickets"
                :key="ticket.id"
              >
                <td class="ps-4">
                  <div class="d-flex align-items-center">
                    <div class="avatar-sm bg-primary-subtle text-primary rounded-circle d-flex align-items-center justify-content-center fw-bold me-3">
                      {{ getInitials(ticket.user.name) }}
                    </div>
                    <div>
                      <p class="mb-0 fw-bold sb-text">{{ ticket.user.name }}</p>
                      <p class="small text-muted mb-0">{{ ticket.user.role }}</p>
                    </div>
                  </div>
                </td>
                <td>
                  <span class="badge rounded-pill px-3 py-2" :class="getCategoryTone(ticket.category)">
                    {{ getCategoryLabel(ticket.category) }}
                  </span>
                </td>
                <td style="max-width: 250px;">
                  <span class="fw-semibold sb-text d-block text-truncate">{{ ticket.subject }}</span>
                  <!-- The SuperAdmin Open tab holds both Open and Escalated, so it needs the status. -->
                  <span
                    v-if="isSuperAdminDesk"
                    class="d-inline-block mt-1"
                    :class="getStatusBadgeClass(ticket.status)"
                  >
                    {{ ticket.status.replace('_', ' ') }}
                  </span>
                </td>
                <td class="small text-muted">{{ formatDate(ticket.created_at) }}</td>
                <td class="small font-semibold">
                  <span v-if="ticket.assigned_agent" class="text-sb-primary">
                    <i class="bi bi-person-badge me-1"></i>{{ ticket.assigned_agent }}
                  </span>
                  <span v-else class="text-muted italic">Unassigned</span>
                </td>
                <td class="pe-4 text-end">
                  <button
                    type="button"
                    class="btn btn-sm btn-light rounded-circle sb-btn me-2"
                    aria-label="View Ticket"
                    @click.stop="openDetail(ticket)"
                  >
                    <i class="bi bi-eye"></i>
                  </button>
                  <button
                    v-if="canClaim(ticket)"
                    type="button"
                    class="btn btn-sm bg-sb-primary text-white sb-btn rounded-pill px-3"
                    :disabled="claimingId === ticket.id"
                    @click.stop="handleClaim(ticket)"
                  >
                    <span v-if="claimingId === ticket.id" class="spinner-border spinner-border-sm me-1"></span>
                    Claim
                  </button>
                  <button
                    v-else-if="canChat(ticket)"
                    type="button"
                    class="btn btn-sm btn-outline-primary sb-btn rounded-pill px-3"
                    @click.stop="goToChat(ticket)"
                  >
                    Chat
                  </button>
                  <button
                    v-if="canEscalate(ticket)"
                    type="button"
                    class="btn btn-sm btn-outline-warning sb-btn rounded-pill px-3 ms-2"
                    :disabled="escalatingId === ticket.id"
                    @click.stop="openEscalationModal(ticket)"
                  >
                    Escalate
                  </button>
                </td>
              </tr>

              <tr v-else>
                <td colspan="6" class="text-center py-4 sb-muted">
                  No support tickets found in this queue.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Ticket Detail Panel (Teleported) -->
    <Teleport to="body">
      <div
        v-if="selectedTicket"
        class="offcanvas offcanvas-end border-0 shadow"
        :class="{ show: selectedTicket }"
        tabindex="-1"
        style="width: 480px; visibility: visible;"
      >
        <div class="offcanvas-header bg-light">
          <h5 class="offcanvas-title fw-bold">Ticket Details</h5>
          <button
            type="button"
            class="btn-close shadow-none"
            @click="selectedTicket = null"
          ></button>
        </div>

        <div class="offcanvas-body">
          <div class="d-flex align-items-center mb-4">
            <div class="avatar-lg bg-primary-subtle text-primary rounded-circle d-flex align-items-center justify-content-center fw-bold me-3" style="width: 60px; height: 60px; font-size: 1.5rem;">
              {{ getInitials(selectedTicket.user.name) }}
            </div>
            <div>
              <h5 class="fw-bold mb-1 sb-text">{{ selectedTicket.user.name }}</h5>
              <p class="text-muted mb-0 small">
                {{ selectedTicket.user.role }} · Opened on {{ formatDateFull(selectedTicket.created_at) }}
              </p>
            </div>
          </div>

          <div class="card border-0 bg-light rounded-4 p-3 mb-4">
            <div class="row g-3">
              <div class="col-6">
                <span class="small text-muted d-block">TICKET ID</span>
                <strong class="font-monospace">#{{ selectedTicket.id }}</strong>
              </div>
              <div class="col-6">
                <span class="small text-muted d-block">STATUS</span>
                <span :class="getStatusBadgeClass(selectedTicket.status)">{{ selectedTicket.status }}</span>
              </div>
              <div class="col-6">
                <span class="small text-muted d-block">CATEGORY</span>
                <span class="badge rounded-pill px-2 py-1 small" :class="getCategoryTone(selectedTicket.category)">
                  {{ getCategoryLabel(selectedTicket.category) }}
                </span>
              </div>
              <div class="col-6" v-if="selectedTicket.assigned_agent">
                <span class="small text-muted d-block">ASSIGNED AGENT</span>
                <strong class="text-sb-primary">{{ selectedTicket.assigned_agent }}</strong>
              </div>
              <div class="col-6" v-if="selectedTicket.penalized_user">
                <span class="small text-muted d-block">PENALIZED USER</span>
                <strong class="sb-text">{{ selectedTicket.penalized_user.name }}</strong>
                <span class="small text-muted d-block">{{ selectedTicket.penalized_user.role }}</span>
              </div>
              <div class="col-6" v-if="selectedTicket.resolution_verdict">
                <span class="small text-muted d-block">VERDICT</span>
                <span
                  class="badge rounded-pill px-2 py-1 small"
                  :class="selectedTicket.resolution_verdict === 'counted'
                    ? 'bg-danger-subtle text-danger'
                    : 'bg-success-subtle text-success'"
                >
                  {{ selectedTicket.resolution_verdict === 'counted' ? 'Counted as strike' : 'Excused' }}
                </span>
              </div>
            </div>
          </div>

          <div class="mb-4">
            <span class="small text-muted fw-bold d-block mb-1">SUBJECT</span>
            <h6 class="fw-bold sb-text">{{ selectedTicket.subject }}</h6>
          </div>

          <div class="mb-4">
            <span class="small text-muted fw-bold d-block mb-1">DESCRIPTION</span>
            <div class="bg-light p-3 rounded-4 sb-text small whitespace-pre-wrap">
              {{ selectedTicket.description }}
            </div>
          </div>

          <div v-if="selectedTicket.escalation_reason" class="mb-4">
            <span class="small text-muted fw-bold d-block mb-1">ESCALATION REASON</span>
            <div class="bg-warning-subtle text-dark p-3 rounded-4 small whitespace-pre-wrap">
              {{ selectedTicket.escalation_reason }}
            </div>
            <p v-if="selectedTicket.escalated_by" class="small text-muted mt-2 mb-0">
              Escalated by {{ selectedTicket.escalated_by }}
            </p>
          </div>

          <div v-if="selectedTicket.booking_id || selectedTicket.transaction_id" class="card border-sb rounded-4 p-3 mb-4">
            <h6 class="fw-bold mb-2 small text-muted"><i class="bi bi-link-45deg me-1"></i>CONTEXT LINKS</h6>
            <div v-if="selectedTicket.booking_id" class="mb-2">
              <p class="small text-muted mb-0">Linked Booking</p>
              <p class="fw-semibold mb-0">
                Booking #{{ selectedTicket.booking_id }}
              </p>
            </div>
            <div v-if="selectedTicket.transaction_id">
              <p class="small text-muted mb-0">Linked Wallet Transaction</p>
              <p class="fw-semibold mb-0">
                Transaction #{{ selectedTicket.transaction_id }}
              </p>
            </div>
          </div>

          <div class="mt-auto pt-4 border-top">
            <button
              v-if="canClaim(selectedTicket)"
              type="button"
              class="btn bg-sb-primary text-white w-100 mb-2 rounded-pill py-2 sb-btn"
              :disabled="claimingId === selectedTicket.id"
              @click="handleClaim(selectedTicket)"
            >
              <span v-if="claimingId === selectedTicket.id" class="spinner-border spinner-border-sm me-2"></span>
              Claim Ticket & Enter Chat
            </button>
            <button
              v-if="canChat(selectedTicket)"
              type="button"
              class="btn btn-primary w-100 mb-2 rounded-pill py-2 sb-btn"
              @click="goToChat(selectedTicket)"
            >
              Open Ticket Chat
            </button>
            <button
              v-if="canEscalate(selectedTicket)"
              type="button"
              class="btn btn-outline-warning w-100 mb-2 rounded-pill py-2 sb-btn"
              :disabled="escalatingId === selectedTicket.id"
              @click="openEscalationModal(selectedTicket)"
            >
              Escalate to SuperAdmin
            </button>
            <button
              v-if="canResolve(selectedTicket)"
              type="button"
              class="btn btn-outline-danger w-100 rounded-pill py-2 sb-btn"
              :disabled="resolvingId === selectedTicket.id"
              @click="handleResolve(selectedTicket)"
            >
              <span v-if="resolvingId === selectedTicket.id" class="spinner-border spinner-border-sm me-2"></span>
              {{ isStrikeTicket(selectedTicket) ? 'Review Late Cancellation' : 'Mark Ticket as Resolved' }}
            </button>
          </div>
        </div>
      </div>
      <div
        v-if="selectedTicket"
        class="offcanvas-backdrop fade show"
        @click="selectedTicket = null"
      ></div>
    </Teleport>

    <Teleport to="body">
      <div
        v-if="ticketToEscalate"
        class="modal fade show d-block"
        tabindex="-1"
        role="dialog"
        aria-modal="true"
      >
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content border-0 shadow">
            <div class="modal-header border-0 pb-0">
              <h5 class="modal-title fw-bold sb-text">Escalate Ticket</h5>
              <button
                type="button"
                class="btn-close shadow-none"
                aria-label="Close"
                @click="closeEscalationModal"
              ></button>
            </div>
            <div class="modal-body">
              <p class="small text-muted mb-3">
                Ticket #{{ ticketToEscalate.id }} will move to the SuperAdmin support queue.
              </p>
              <label for="escalation-reason" class="form-label small fw-bold text-muted">
                REASON
              </label>
              <textarea
                id="escalation-reason"
                v-model="escalationReason"
                class="form-control sb-field shadow-none"
                rows="4"
                maxlength="500"
                placeholder="What needs SuperAdmin access or decision-making?"
              ></textarea>
              <p v-if="escalationError" class="text-danger small mt-2 mb-0">
                {{ escalationError }}
              </p>
            </div>
            <div class="modal-footer border-0 pt-0">
              <button
                type="button"
                class="btn btn-light rounded-pill px-4 sb-btn"
                @click="closeEscalationModal"
              >
                Cancel
              </button>
              <button
                type="button"
                class="btn btn-warning rounded-pill px-4 sb-btn"
                :disabled="escalatingId === ticketToEscalate.id"
                @click="handleEscalate"
              >
                <span v-if="escalatingId === ticketToEscalate.id" class="spinner-border spinner-border-sm me-2"></span>
                Escalate
              </button>
            </div>
          </div>
        </div>
      </div>
      <div
        v-if="ticketToEscalate"
        class="modal-backdrop fade show"
        @click="closeEscalationModal"
      ></div>
    </Teleport>

    <!-- Late Cancellation verdict. Two-step on `counted` because the verdict cannot be reversed. -->
    <Teleport to="body">
      <div
        v-if="ticketToJudge"
        class="modal fade show d-block"
        tabindex="-1"
        role="dialog"
        aria-modal="true"
        aria-labelledby="verdict-modal-title"
      >
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content border-0 shadow">
            <div class="modal-header border-0 pb-0">
              <h5 id="verdict-modal-title" class="modal-title fw-bold sb-text">
                {{ confirmingCounted ? 'Count this as a strike?' : 'Review Late Cancellation' }}
              </h5>
              <button
                type="button"
                class="btn-close shadow-none"
                aria-label="Close"
                @click="closeVerdictModal"
              ></button>
            </div>

            <div class="modal-body">
              <template v-if="!confirmingCounted">
                <p class="small text-muted mb-3">
                  Ticket #{{ ticketToJudge.id }} — a session was cancelled after the Grace Cutoff.
                </p>
                <div v-if="ticketToJudge.penalized_user" class="verdict-subject rounded-4 p-3 mb-3">
                  <span class="small text-muted d-block">CANCELLED BY</span>
                  <strong class="sb-text">{{ ticketToJudge.penalized_user.name }}</strong>
                  <span class="small text-muted">· {{ ticketToJudge.penalized_user.role }}</span>
                </div>
                <p class="small sb-text mb-0">
                  <strong>Excuse</strong> clears the strike from their record.
                  <strong>Count as strike</strong> keeps it against them for 14 days.
                </p>
              </template>

              <template v-else>
                <p class="sb-text mb-3">
                  This will count a strike against
                  <strong>{{ ticketToJudge.penalized_user?.name || 'this user' }}</strong>
                  for the next 14 days.
                </p>
                <div class="verdict-warning rounded-4 p-3 mb-0">
                  <p class="small fw-bold mb-1">
                    <i class="bi bi-exclamation-triangle-fill me-1"></i>
                    This is final and cannot be reversed.
                  </p>
                  <p
                    v-if="ticketToJudge.penalized_user?.role === 'Tutor'"
                    class="small mb-0"
                  >
                    It also deducts ₱50 from their wallet immediately.
                  </p>
                  <p v-else class="small mb-0">
                    At 3 active strikes they cannot book new sessions until one expires.
                  </p>
                </div>
              </template>

              <p v-if="verdictError" class="text-danger small mt-3 mb-0">
                {{ verdictError }}
              </p>
            </div>

            <div class="modal-footer border-0 pt-0">
              <template v-if="!confirmingCounted">
                <button
                  type="button"
                  class="btn btn-outline-success rounded-pill px-4 sb-btn"
                  :disabled="resolvingId === ticketToJudge.id"
                  @click="submitVerdict('excused')"
                >
                  <span v-if="resolvingId === ticketToJudge.id" class="spinner-border spinner-border-sm me-2"></span>
                  Excuse
                </button>
                <button
                  type="button"
                  class="btn btn-danger-soft px-4 sb-btn"
                  :disabled="resolvingId === ticketToJudge.id"
                  @click="submitVerdict('counted')"
                >
                  Count as strike
                </button>
              </template>

              <template v-else>
                <button
                  type="button"
                  class="btn btn-light rounded-pill px-4 sb-btn"
                  :disabled="resolvingId === ticketToJudge.id"
                  @click="confirmingCounted = false"
                >
                  Go back
                </button>
                <button
                  type="button"
                  class="btn btn-danger rounded-pill px-4 sb-btn"
                  :disabled="resolvingId === ticketToJudge.id"
                  @click="submitVerdict('counted')"
                >
                  <span v-if="resolvingId === ticketToJudge.id" class="spinner-border spinner-border-sm me-2"></span>
                  Confirm strike
                </button>
              </template>
            </div>
          </div>
        </div>
      </div>
      <div
        v-if="ticketToJudge"
        class="modal-backdrop fade show"
        @click="closeVerdictModal"
      ></div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api/api'
import { useToastStore } from '@/stores/toast'

const router = useRouter()
const route = useRoute()
const toastStore = useToastStore()

const tickets = ref([])
const loading = ref(true)
const claimingId = ref(null)
const resolvingId = ref(null)
const escalatingId = ref(null)
const selectedTicket = ref(null)
const ticketToEscalate = ref(null)
const escalationReason = ref('')
const escalationError = ref('')
const ticketToJudge = ref(null)
const verdictError = ref('')
const confirmingCounted = ref(false)
const isSuperAdminDesk = computed(() => route.path.startsWith('/superadmin'))
// A tab can cover more than one status. The SuperAdmin desk has no Escalated tab, so its Open tab
// carries both Open and Escalated; without that widening, escalated tickets are fetched from
// admin_list_tickets but unreachable. System-opened Late Cancellation tickets land in that queue as
// Open/unescalated, which is the other reason the desk needs an Open tab at all.
const TAB_STATUSES = {
  Open: ['Open'],
  In_Progress: ['In_Progress'],
  Resolved: ['Resolved'],
}
const SUPERADMIN_TAB_STATUSES = { ...TAB_STATUSES, Open: ['Open', 'Escalated'] }

const tabStatuses = computed(() => (
  isSuperAdminDesk.value ? SUPERADMIN_TAB_STATUSES : TAB_STATUSES
))
const statusTabs = computed(() => (
  isSuperAdminDesk.value ? ['Open', 'Resolved'] : ['Open', 'In_Progress', 'Resolved']
))
const statusesForTab = (tab) => tabStatuses.value[tab] ?? [tab]

const filters = reactive({
  status: 'Open',
  search: ''
})

const fetchTickets = async () => {
  try {
    loading.value = true
    const response = await api.get('admin/support/tickets/')
    tickets.value = response.data
  } catch (error) {
    console.error('Failed to fetch support tickets:', error)
    toastStore.push('Failed to load support tickets.', 'error')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchTickets()
})

watch(isSuperAdminDesk, () => {
  filters.status = 'Open'
  selectedTicket.value = null
  ticketToEscalate.value = null
  closeVerdictModal()
})

const getCount = (tab) => {
  const statuses = statusesForTab(tab)
  return tickets.value.filter((t) => statuses.includes(t.status)).length
}

const filteredTickets = computed(() => {
  const statuses = statusesForTab(filters.status)
  return tickets.value.filter((ticket) => {
    const matchesStatus = statuses.includes(ticket.status)
    const search = filters.search.toLowerCase()
    const matchesSearch =
      !search ||
      ticket.subject.toLowerCase().includes(search) ||
      ticket.description.toLowerCase().includes(search) ||
      ticket.user.name.toLowerCase().includes(search)

    return matchesStatus && matchesSearch
  })
})

const openDetail = (ticket) => {
  selectedTicket.value = ticket
}

const canClaim = (ticket) => {
  if (isSuperAdminDesk.value) {
    return ticket.status === 'Escalated' && !ticket.assigned_agent_id
  }
  return ticket.status === 'Open'
}

const canChat = (ticket) => {
  return ticket.status === 'In_Progress' || (isSuperAdminDesk.value && ticket.status === 'Escalated' && ticket.assigned_agent_id)
}

const canEscalate = (ticket) => {
  return !isSuperAdminDesk.value && ticket.status === 'In_Progress'
}

const isStrikeTicket = (ticket) => ticket?.category === 'Late_Cancellation'

const canResolve = (ticket) => {
  if (ticket.status === 'Resolved') return false
  // A strike ticket needs a verdict, and admin_resolve_ticket only accepts one from a SuperAdmin.
  if (isStrikeTicket(ticket)) return isSuperAdminDesk.value
  if (ticket.status === 'Escalated') return isSuperAdminDesk.value
  return !isSuperAdminDesk.value
}

const handleClaim = async (ticket) => {
  claimingId.value = ticket.id
  try {
    await api.post(`admin/support/tickets/${ticket.id}/claim/`)
    toastStore.push('Ticket claimed successfully. Entering chatroom.')
    selectedTicket.value = null
    await fetchTickets()
    router.push(`/chat?room=${ticket.chatroom_id}`)
  } catch (error) {
    console.error('Failed to claim support ticket:', error)
    const errorMessage = error.response?.data?.error || 'Unable to claim ticket. Please try again.'
    toastStore.push(errorMessage, 'error')
  } finally {
    claimingId.value = null
  }
}

const openEscalationModal = (ticket) => {
  ticketToEscalate.value = ticket
  escalationReason.value = ''
  escalationError.value = ''
}

const closeEscalationModal = () => {
  ticketToEscalate.value = null
  escalationReason.value = ''
  escalationError.value = ''
}

const handleEscalate = async () => {
  const ticket = ticketToEscalate.value
  const reason = escalationReason.value.trim()
  if (!ticket) return
  if (!reason) {
    escalationError.value = 'Add a short reason before escalating.'
    return
  }

  escalatingId.value = ticket.id
  escalationError.value = ''
  try {
    await api.post(`admin/support/tickets/${ticket.id}/escalate/`, { reason })
    toastStore.push('Ticket escalated to SuperAdmin support.')
    selectedTicket.value = null
    closeEscalationModal()
    await fetchTickets()
  } catch (error) {
    console.error('Failed to escalate support ticket:', error)
    escalationError.value = error.response?.data?.error || 'Unable to escalate ticket.'
  } finally {
    escalatingId.value = null
  }
}

const openVerdictModal = (ticket) => {
  ticketToJudge.value = ticket
  confirmingCounted.value = false
  verdictError.value = ''
}

const closeVerdictModal = () => {
  ticketToJudge.value = null
  confirmingCounted.value = false
  verdictError.value = ''
}

const submitVerdict = async (verdict) => {
  const ticket = ticketToJudge.value
  if (!ticket) return

  // Counting a strike is final and deducts from a tutor's wallet, so it goes through a second
  // step. Excusing is the relieving verdict and needs no guard.
  if (verdict === 'counted' && !confirmingCounted.value) {
    confirmingCounted.value = true
    return
  }

  resolvingId.value = ticket.id
  verdictError.value = ''
  try {
    await api.post(`admin/support/tickets/${ticket.id}/resolve/`, { verdict })
    toastStore.push(
      verdict === 'counted'
        ? 'Late cancellation counted as a strike.'
        : 'Late cancellation excused. No strike recorded.',
    )
    selectedTicket.value = null
    closeVerdictModal()
    await fetchTickets()
  } catch (error) {
    console.error('Failed to resolve support ticket:', error)
    verdictError.value = error.response?.data?.error || 'Unable to resolve ticket.'
  } finally {
    resolvingId.value = null
  }
}

const handleResolve = async (ticket) => {
  if (isStrikeTicket(ticket)) {
    openVerdictModal(ticket)
    return
  }

  if (!confirm('Are you sure you want to mark this ticket as Resolved? The chat conversation will be closed.')) {
    return
  }

  resolvingId.value = ticket.id
  try {
    await api.post(`admin/support/tickets/${ticket.id}/resolve/`)
    toastStore.push('Support ticket resolved successfully.')
    selectedTicket.value = null
    await fetchTickets()
  } catch (error) {
    console.error('Failed to resolve support ticket:', error)
    toastStore.push('Unable to resolve ticket.', 'error')
  } finally {
    resolvingId.value = null
  }
}

const goToChat = (ticket) => {
  selectedTicket.value = null
  router.push(`/chat?room=${ticket.chatroom_id}`)
}

const getInitials = (name) => {
  return String(name || '')
    .split(' ')
    .filter(Boolean)
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
}

const getCategoryLabel = (cat) => {
  const map = {
    Payment: 'Payment Issue',
    Booking: 'Booking/No-show',
    Technical: 'Technical Problem',
    Dispute: 'Dispute',
    Other: 'Other'
  }
  return map[cat] || cat
}

const getCategoryTone = (cat) => {
  switch (cat) {
    case 'Payment': return 'bg-success-subtle text-success';
    case 'Booking': return 'bg-primary-subtle text-primary';
    case 'Technical': return 'bg-info-subtle text-info';
    case 'Dispute': return 'bg-danger-subtle text-danger';
    default: return 'bg-secondary-subtle text-dark';
  }
}

const getStatusBadgeClass = (status) => {
  switch (status) {
    case 'Open': return 'badge bg-warning text-dark px-3 rounded-pill';
    case 'In_Progress': return 'badge bg-primary text-white px-3 rounded-pill';
    case 'Escalated': return 'badge bg-warning-subtle text-dark px-3 rounded-pill';
    default: return 'badge bg-success text-white px-3 rounded-pill';
  }
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const formatDateFull = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.verdict-subject {
  background: var(--sb-bg);
  border: 1px solid var(--sb-card-border);
}

.verdict-warning {
  border: 1px solid color-mix(in srgb, var(--sb-danger) 30%, transparent);
  background: color-mix(in srgb, var(--sb-danger) 12%, transparent);
  color: var(--sb-danger);
}

.filter-bar {
    background: var(--sb-bg);
    border: 1px solid var(--sb-card-border);
}

.filter-tab {
  position: relative;
  color: var(--sb-text-muted);
}

.filter-tab-active {
  background: var(--sb-card-bg);
  color: var(--sb-text-main);
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}
.sb-input-addon,
.sb-search-input {
    background: var(--sb-card-bg);
    border-color: var(--sb-card-border);
    color: var(--sb-text-main);
}

.sb-input-addon {
    color: var(--sb-text-muted);
}

.sb-themed-table {
    --bs-table-bg: transparent;
    --bs-table-color: var(--sb-text-main);
    --bs-table-border-color: var(--sb-card-border);
    --bs-table-hover-bg: color-mix(in srgb, var(--sb-primary) 7%, transparent);
    --bs-table-hover-color: var(--sb-text-main);
}

thead th {
    position: sticky;
    top: 0;
    background-color: var(--sb-card-bg);
    z-index: 2;
    box-shadow: inset 0 -2px 0 var(--sb-card-border, #dee2e6);
}

.avatar-sm {
  width: 32px;
  height: 32px;
  font-size: 0.8rem;
}

.avatar-lg {
    width: 60px;
    height: 60px;
}

.whitespace-pre-wrap {
  white-space: pre-wrap;
}
</style>
