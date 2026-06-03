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
              v-for="status in ['Open', 'In_Progress', 'Resolved']"
              :key="status"
              @click="filters.status = status"
              class="btn rounded-pill px-3 py-1 fw-semibold shadow-none sb-btn filter-tab"
              :class="{ 'filter-tab-active': filters.status === status }"
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
              class="form-control border-start-0 shadow-none sb-search-input"
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
                <td class="fw-semibold sb-text text-truncate" style="max-width: 250px;">
                  {{ ticket.subject }}
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
                    v-if="ticket.status === 'Open'"
                    type="button"
                    class="btn btn-sm bg-sb-primary text-white sb-btn rounded-pill px-3"
                    :disabled="claimingId === ticket.id"
                    @click.stop="handleClaim(ticket)"
                  >
                    <span v-if="claimingId === ticket.id" class="spinner-border spinner-border-sm me-1"></span>
                    Claim
                  </button>
                  <button
                    v-else-if="ticket.status === 'In_Progress'"
                    type="button"
                    class="btn btn-sm btn-outline-primary sb-btn rounded-pill px-3"
                    @click.stop="goToChat(ticket)"
                  >
                    Chat
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
              v-if="selectedTicket.status === 'Open'"
              type="button"
              class="btn bg-sb-primary text-white w-100 mb-2 rounded-pill py-2 sb-btn"
              :disabled="claimingId === selectedTicket.id"
              @click="handleClaim(selectedTicket)"
            >
              <span v-if="claimingId === selectedTicket.id" class="spinner-border spinner-border-sm me-2"></span>
              Claim Ticket & Enter Chat
            </button>
            <button
              v-if="selectedTicket.status === 'In_Progress'"
              type="button"
              class="btn btn-primary w-100 mb-2 rounded-pill py-2 sb-btn"
              @click="goToChat(selectedTicket)"
            >
              Open Ticket Chat
            </button>
            <button
              v-if="selectedTicket.status !== 'Resolved'"
              type="button"
              class="btn btn-outline-danger w-100 rounded-pill py-2 sb-btn"
              :disabled="resolvingId === selectedTicket.id"
              @click="handleResolve(selectedTicket)"
            >
              <span v-if="resolvingId === selectedTicket.id" class="spinner-border spinner-border-sm me-2"></span>
              Mark Ticket as Resolved
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
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api/api'
import { useToastStore } from '@/stores/toast'

const router = useRouter()
const toastStore = useToastStore()

const tickets = ref([])
const loading = ref(true)
const claimingId = ref(null)
const resolvingId = ref(null)
const selectedTicket = ref(null)

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

const getCount = (status) => tickets.value.filter((t) => t.status === status).length

const filteredTickets = computed(() => {
  return tickets.value.filter((ticket) => {
    const matchesStatus = ticket.status === filters.status
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

const handleResolve = async (ticket) => {
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
.filter-tab-active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 12px;
  right: 12px;
  height: 2px;
  background: var(--sb-primary);
  border-radius: 999px;
  transform-origin: left center;
  animation: sb-tab-indicator var(--sb-t-normal) var(--sb-spring) both;
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