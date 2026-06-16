<template>
  <div class="admin-users p-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3 class="mb-0">User Management</h3>
      <div class="d-flex gap-2">
        <input v-model="filters.search" type="text" class="form-control form-control-sm rounded-pill px-3" placeholder="Search by name or email..." style="width: 250px;">
        <select v-model="filters.role" class="form-select form-select-sm rounded-pill" style="width: 120px;">
          <option value="">All Roles</option>
          <option value="Tutee">Tutee</option>
          <option value="Tutor">Tutor</option>
        </select>
        <select v-model="filters.status" class="form-select form-select-sm rounded-pill" style="width: 120px;">
          <option value="">All Status</option>
          <option value="Active">Active</option>
          <option value="Suspended">Suspended</option>
        </select>
      </div>
    </div>

    <div class="card border-0 shadow-sm rounded-4 overflow-hidden">
      <Transition name="fade" mode="out-in">
        <div v-if="store.loading.users && !store.users.length" class="table-responsive">
          <table class="table align-middle mb-0">
            <thead class="bg-light">
              <tr>
                <th class="ps-4 py-3">User</th>
                <th class="py-3">Role</th>
                <th class="py-3">Institution</th>
                <th class="py-3">Status</th>
                <th class="py-3">Joined</th>
                <th class="pe-4 py-3 text-end">Actions</th>
              </tr>
            </thead>
            <tbody class="placeholder-glow">
              <tr v-for="i in 5" :key="'user-skeleton-' + i">
                <td class="ps-4">
                  <div class="d-flex align-items-center">
                    <div class="placeholder rounded-circle me-3" style="width: 32px; height: 32px;"></div>
                    <div class="flex-grow-1">
                      <p class="placeholder col-6 rounded mb-1"></p>
                      <p class="placeholder col-4 rounded mb-0 small"></p>
                    </div>
                  </div>
                </td>
                <td><span class="placeholder col-4 rounded"></span></td>
                <td><span class="placeholder col-8 rounded"></span></td>
                <td><span class="placeholder col-5 rounded-pill"></span></td>
                <td><span class="placeholder col-6 rounded small"></span></td>
                <td class="pe-4 text-end">
                  <span class="placeholder col-6 rounded"></span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="bg-light">
              <tr>
                <th class="ps-4 py-3">User</th>
                <th class="py-3">Role</th>
                <th class="py-3">Institution</th>
                <th class="py-3">Status</th>
                <th class="py-3">Joined</th>
                <th class="pe-4 py-3 text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in filteredUsers" :key="user.id">
                <td class="ps-4">
                  <div class="d-flex align-items-center">
                    <div class="avatar-sm bg-primary-subtle text-primary rounded-circle d-flex align-items-center justify-content-center fw-bold me-3">
                      {{ user.fname[0] }}{{ user.lname[0] }}
                    </div>
                    <div>
                      <p class="mb-0 fw-bold">{{ user.full_name }}</p>
                      <p class="small text-muted mb-0">{{ user.email }}</p>
                    </div>
                  </div>
                </td>
                <td>
                  <span :class="getRoleBadgeClass(user.role)">{{ user.role }}</span>
                </td>
                <td class="small">{{ user.institution_name || 'N/A' }}</td>
                <td>
                  <span v-if="user.is_suspended" class="badge bg-danger-subtle text-danger rounded-pill px-3">Suspended</span>
                  <span v-else class="badge bg-success-subtle text-success rounded-pill px-3">Active</span>
                </td>
                <td class="small text-muted">{{ formatDate(user.created_at) }}</td>
                <td class="pe-4 text-end">
                  <button @click="openDetail(user)" class="btn btn-sm btn-light rounded-circle sb-btn">
                    <i class="bi bi-eye"></i></button>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-if="!store.users.length" class="text-center py-5">
            <p class="text-muted">No users found matching your filters.</p>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Detail Side Panel -->
    <div class="offcanvas offcanvas-end border-0 shadow" :class="{ show: selectedUser }" tabindex="-1" style="width: 450px;">
      <div class="offcanvas-header bg-light">
        <h5 class="offcanvas-title fw-bold">User Details</h5>
        <button @click="selectedUser = null" type="button" class="btn-close shadow-none"></button>
      </div>
      <div v-if="selectedUser" class="offcanvas-body">
        <div class="text-center mb-4">
          <div class="avatar-lg bg-primary-subtle text-primary rounded-circle d-flex align-items-center justify-content-center fw-bold mx-auto mb-3" style="width: 80px; height: 80px; font-size: 2rem;">
            {{ selectedUser.fname[0] }}{{ selectedUser.lname[0] }}
          </div>
          <h4 class="fw-bold mb-1">{{ selectedUser.full_name }}</h4>
          <p class="text-muted mb-3">{{ selectedUser.email }}</p>
          <div class="d-flex justify-content-center gap-2">
            <span :class="getRoleBadgeClass(selectedUser.role)">{{ selectedUser.role }}</span>
            <span v-if="selectedUser.is_suspended" class="badge bg-danger rounded-pill px-3">Suspended</span>
          </div>
        </div>

        <div class="card border-0 bg-light rounded-4 p-3 mb-4">
          <h6 class="fw-bold mb-3 small text-muted">PROFILE INFORMATION</h6>
          <div class="mb-2">
            <p class="small text-muted mb-0">Institution</p>
            <p class="fw-semibold">{{ selectedUser.institution_name || 'N/A' }}</p>
          </div>
          <div class="mb-2">
            <p class="small text-muted mb-0">Registration Date</p>
            <p class="fw-semibold">{{ formatDateFull(selectedUser.created_at) }}</p>
          </div>
          <div>
            <p class="small text-muted mb-0">Profile Status</p>
            <p :class="selectedUser.profile_completed ? 'text-success' : 'text-warning'" class="fw-semibold mb-0">
              {{ selectedUser.profile_completed ? 'Completed' : 'Incomplete' }}
            </p>
          </div>
        </div>

        <div v-if="selectedUser.role === 'Tutor'" class="card border-0 bg-light rounded-4 p-3">
          <h6 class="fw-bold mb-3 small text-muted">TUTOR DATA</h6>
          <div class="mb-2">
            <p class="small text-muted mb-0">Wallet Balance</p>
            <p class="fw-bold text-success fs-5">₱{{ selectedUser.wallet_balance?.toLocaleString() || '0.00' }}</p>
          </div>
          <div class="mb-0">
            <p class="small text-muted mb-0">Standard Commission</p>
            <p class="fw-semibold mb-0">10% (Platform Fixed)</p>
          </div>
        </div>

        <div class="mt-4 pt-4 border-top">
          <button 
            @click="toggleSuspension(selectedUser)" 
            :disabled="suspending"
            class="btn w-100 mb-2 rounded-pill py-2 sb-btn" 
            :class="selectedUser.is_suspended ? 'btn-success' : 'btn-outline-danger'"
          >
            <span v-if="suspending" class="spinner-border spinner-border-sm me-2"></span>
            {{ suspending ? 'Updating...' : selectedUser.is_suspended ? 'Reactivate Account' : 'Suspend Account' }}
          </button>
        </div>
      </div>
    </div>
    <div v-if="selectedUser" @click="selectedUser = null" class="offcanvas-backdrop fade show"></div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import { useAdminStore } from '@/stores/admin';
import { useToastStore } from '@/stores/toast'

const store = useAdminStore()
const toastStore = useToastStore()
const selectedUser = ref(null)

const filters = reactive({
  search: '',
  role: '',
  status: ''
})

onMounted(() => {
  store.fetchUsers({})
})

const filteredUsers = computed(() => {
  return store.users.filter(user => {
    const search = filters.search.toLowerCase()
    const matchesSearch = !search ||
      user.full_name.toLowerCase().includes(search) ||
      user.email.toLowerCase().includes(search)

    const matchesRole = !filters.role || user.role === filters.role
    const matchesStatus = !filters.status ||
      (filters.status === 'Active' && !user.is_suspended) ||
      (filters.status === 'Suspended' && user.is_suspended)

    return matchesSearch && matchesRole && matchesStatus
  })
})

const getRoleBadgeClass = (role) => {
  switch (role) {
    case 'Admin': return 'badge bg-dark rounded-pill px-3';
    case 'Tutor': return 'badge bg-primary rounded-pill px-3';
    default: return 'badge bg-info-subtle text-info rounded-pill px-3';
  }
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const formatDateFull = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleString('en-US', { month: 'long', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' })
}

const openDetail = (user) => {
  selectedUser.value = user
}

const suspending = ref(false)

const toggleSuspension = async (user) => {
  const action = user.is_suspended ? 'reactivate' : 'suspend'
  if (confirm(`Are you sure you want to ${action} ${user.full_name}?`)) {
    suspending.value = true
    try {
      await store.updateUserStatus(user.id, !user.is_suspended)
      // No manual patch needed — store mutation is reactive
    } catch {
      toastStore.push('Failed to update user status.', 'error')
    } finally {
      suspending.value = false
    }
  }
}

const deleteUser = async (user) => {
  if (confirm(`CRITICAL ACTION: Are you sure you want to PERMANENTLY DELETE ${user.full_name}? This cannot be undone.`)) {
    try {
      await store.deleteUser(user.id)
      selectedUser.value = null
    } catch {
      toastStore.push('Failed to delete user.', 'error')
    }
  }
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.avatar-sm { width: 32px; height: 32px; font-size: 0.8rem; }
.admin-users .table thead th { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: none; }
.admin-users .table tbody td { border-bottom: 1px solid #f8f9fa; }
.dropdown-item:active { background-color: var(--sb-primary); }
</style>
