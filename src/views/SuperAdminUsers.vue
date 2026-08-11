<template>
  <div class="superadmin-users">
    <header class="users-header">
      <div>
        <p class="eyebrow">Directory</p>
        <h1>All Users</h1>
      </div>
      <div class="header-actions">
        <input
          v-model="filters.search"
          type="text"
          class="search-input sb-field"
          placeholder="Search name or email"
        >
        <button type="button" class="export-button" :disabled="!filteredUsers.length" @click="openExportModal">
          <i class="bi bi-download"></i>
          Export CSV
        </button>
      </div>
    </header>

    <SbExportModal
      :open="isExportOpen"
      title="Export users"
      :items="exportColumnGroups"
      :scope-line="exportScopeLine"
      :combined-file-label="USERS_FILE_LABEL"
      @confirm="exportUsers"
      @close="isExportOpen = false"
    />

    <section class="filter-row" aria-label="User filters">
      <SbSelectModal
        v-model="filters.role"
        :options="roleFilterOptions"
        title="Filter Role"
        placeholder="All roles"
        :searchable="false"
        clearable
        clear-label="All roles"
        trigger-class="filter-trigger"
      />
      <SbSelectModal
        v-model="filters.institution"
        :options="institutionFilterOptions"
        title="Filter Institution"
        placeholder="All institutions"
        searchable
        clearable
        clear-label="All institutions"
        trigger-class="filter-trigger"
      />
      <SbSelectModal
        v-model="filters.status"
        :options="statusFilterOptions"
        title="Filter Status"
        placeholder="All statuses"
        :searchable="false"
        clearable
        clear-label="All statuses"
        trigger-class="filter-trigger"
      />
    </section>

    <section class="users-table-panel">
      <Transition name="fade" mode="out-in">
        <div v-if="store.loading.users && !store.users.length" class="table-responsive">
          <table class="table align-middle mb-0">
            <thead>
              <tr>
                <th>User</th>
                <th>Role</th>
                <th>Institution</th>
                <th>Status</th>
                <th>Joined</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>
            <tbody class="placeholder-glow">
              <tr v-for="i in 7" :key="`user-sk-${i}`">
                <td><span class="placeholder col-7 rounded"></span></td>
                <td><span class="placeholder col-4 rounded"></span></td>
                <td><span class="placeholder col-8 rounded"></span></td>
                <td><span class="placeholder col-5 rounded"></span></td>
                <td><span class="placeholder col-6 rounded"></span></td>
                <td class="text-end"><span class="placeholder col-5 rounded"></span></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead>
              <tr>
                <th>User</th>
                <th>Role</th>
                <th>Institution</th>
                <th>Status</th>
                <th>Joined</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in filteredUsers" :key="user.id">
                <td>
                  <div class="user-cell">
                    <div class="avatar-sm">
                      <img v-if="user.profile_picture_url" :src="user.profile_picture_url" alt="">
                      <span v-else>{{ getInitials(user) }}</span>
                    </div>
                    <div>
                      <p>{{ user.full_name }}</p>
                      <span>{{ user.email }}</span>
                    </div>
                  </div>
                </td>
                <td><span :class="getRoleBadgeClass(user.role)">{{ user.role }}</span></td>
                <td>{{ user.institution_name || 'Unassigned' }}</td>
                <td>
                  <span :class="user.is_suspended ? 'status-badge is-danger' : 'status-badge is-success'">
                    {{ user.is_suspended ? 'Suspended' : 'Active' }}
                  </span>
                </td>
                <td>{{ formatDate(user.created_at) }}</td>
                <td class="text-end">
                  <button type="button" class="icon-action" aria-label="View user details" @click="openDetail(user)">
                    <i class="bi bi-eye"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>

          <div v-if="!filteredUsers.length" class="empty-state">
            <i class="bi bi-people"></i>
            <p>No users found matching your filters.</p>
          </div>
        </div>
      </Transition>
    </section>

    <SuperAdminUserModal
      v-if="selectedUser"
      :user="selectedUser"
      :institutions="store.institutions"
      @close="selectedUser = null"
      @updated="handleUserUpdated"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import SbExportModal from '@/components/SbExportModal.vue'
import SbSelectModal from '@/components/SbSelectModal.vue'
import SuperAdminUserModal from '@/components/SuperAdminUserModal.vue'
import { useHaptics } from '@/composables/useHaptics'
import { useSuperAdminStore } from '@/stores/superadmin'
import { useToastStore } from '@/stores/toast'
import { USERS_FILE_LABEL, USER_COLUMN_GROUPS } from '@/constants/superadminExports'

const store = useSuperAdminStore()
const toastStore = useToastStore()
const { vibrate, patterns } = useHaptics()

const selectedUser = ref(null)
const filters = reactive({ search: '', role: '', institution: '', status: '' })
const isExportOpen = ref(false)

const exportColumnGroups = USER_COLUMN_GROUPS

const roleFilterOptions = [
  { label: 'All roles', value: '' },
  { label: 'Tutee', value: 'Tutee' },
  { label: 'Tutor', value: 'Tutor' },
  { label: 'Admin', value: 'Admin' },
  { label: 'SuperAdmin', value: 'SuperAdmin' },
]

const statusFilterOptions = [
  { label: 'All statuses', value: '' },
  { label: 'Active', value: 'Active' },
  { label: 'Suspended', value: 'Suspended' },
]

const institutionFilterOptions = computed(() => [
  { label: 'All institutions', value: '' },
  ...store.institutions.map((institution) => ({
    label: institution.institution_name,
    value: institution.id,
    description: institution.school_email_domain,
  })),
])

const filteredUsers = computed(() => {
  return store.users.filter((user) => {
    const search = filters.search.toLowerCase()
    const matchesSearch = !search ||
      user.full_name?.toLowerCase().includes(search) ||
      user.email?.toLowerCase().includes(search)
    const matchesRole = !filters.role || user.role === filters.role
    const matchesInstitution = !filters.institution ||
      String(user.institution || '') === String(filters.institution)
    const matchesStatus = !filters.status ||
      (filters.status === 'Active' && !user.is_suspended) ||
      (filters.status === 'Suspended' && user.is_suspended)
    return matchesSearch && matchesRole && matchesInstitution && matchesStatus
  })
})

// Spells out exactly which rows the export will contain, so "42 of 310" is never a surprise.
const exportScopeLine = computed(() => {
  const institution = institutionFilterOptions.value.find(
    (option) => String(option.value) === String(filters.institution),
  )
  const activeFilters = [
    filters.role,
    institution && filters.institution ? institution.label : '',
    filters.status,
    filters.search ? `"${filters.search}"` : '',
  ].filter(Boolean)

  const count = `${filteredUsers.value.length} of ${store.users.length} users`
  return activeFilters.length ? `${count} · ${activeFilters.join(' · ')}` : count
})

onMounted(() => {
  store.fetchUsers({}, true)
  store.fetchInstitutions()
})

function openDetail(user) {
  selectedUser.value = user
  vibrate(patterns.light)
}

function handleUserUpdated(updatedUser) {
  selectedUser.value = updatedUser
}

function openExportModal() {
  vibrate(patterns.light)
  isExportOpen.value = true
}

function exportUsers({ ids, filename }) {
  isExportOpen.value = false
  try {
    store.exportUsersCsv(filteredUsers.value, ids, filename)
  } catch {
    toastStore.push('Failed to export CSV.', 'error')
  }
}

function getInitials(user) {
  return `${user.fname?.[0] || ''}${user.lname?.[0] || ''}` || 'SB'
}

function getRoleBadgeClass(role) {
  switch (role) {
    case 'SuperAdmin':
      return 'role-badge is-super'
    case 'Admin':
      return 'role-badge is-admin'
    case 'Tutor':
      return 'role-badge is-tutor'
    default:
      return 'role-badge is-tutee'
  }
}

function formatDate(value) {
  if (!value) return 'N/A'
  return new Date(value).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from,
.fade-leave-to { opacity: 0; }

.superadmin-users {
  min-height: 100%;
  padding: 24px;
  color: var(--sb-text-main);
}

.users-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 18px;
  margin-bottom: 16px;
}

.eyebrow {
  color: var(--sb-text-muted);
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  margin: 0 0 4px;
}

h1 {
  font-size: 30px;
  font-weight: 800;
  line-height: 1.15;
  margin: 0;
}

h2 {
  font-size: 18px;
  font-weight: 800;
  margin: 0;
}

.header-actions,
.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.search-input {
  width: min(280px, 100%);
  border: 1px solid var(--sb-card-border);
  border-radius: 999px;
  padding: 9px 16px;
  outline: 0;
}

.search-input:focus {
  border-color: var(--sb-primary);
  box-shadow: 0 0 0 3px rgba(0, 137, 90, 0.12);
}

.export-button {
  border: 0;
  border-radius: 999px;
  background: var(--sb-primary);
  color: #fff;
  font-size: 13px;
  font-weight: 800;
  padding: 9px 15px;
  display: inline-flex;
  align-items: center;
  gap: 7px;
}

.filter-row {
  margin-bottom: 16px;
}

:deep(.filter-trigger) {
  min-width: 170px;
  border-radius: 999px;
}

.users-table-panel {
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid var(--sb-card-border);
  border-radius: 18px;
  box-shadow: 0 12px 32px rgba(10, 25, 22, 0.06);
}

.users-table-panel {
  overflow: hidden;
}

.table thead th {
  color: var(--sb-text-muted);
  font-size: 12px;
  text-transform: uppercase;
  border: 0;
  padding: 14px 20px;
}

.table tbody td {
  border-color: var(--sb-card-border);
  padding: 16px 20px;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 220px;
}

.avatar-sm {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #edf6f1;
  color: var(--sb-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 800;
  overflow: hidden;
  flex: 0 0 auto;
}

.avatar-sm img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-cell p {
  margin: 0;
  font-weight: 800;
}

.user-cell span,
.table tbody td {
  color: var(--sb-text-muted);
}

.role-badge,
.status-badge {
  border-radius: 999px;
  padding: 5px 12px;
  font-size: 12px;
  font-weight: 800;
  white-space: nowrap;
}

.role-badge.is-super { background: #111827; color: #fff; }
.role-badge.is-admin { background: #f5f3ff; color: #5b21b6; }
.role-badge.is-tutor { background: #edf6f1; color: var(--sb-primary); }
.role-badge.is-tutee { background: #eff6ff; color: #1d4ed8; }
.status-badge.is-success { background: #ecfdf5; color: #047857; }
.status-badge.is-danger { background: #fef2f2; color: #991b1b; }

.icon-action {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  border: 1px solid var(--sb-card-border);
  background: #fff;
  color: var(--sb-text-main);
}

.export-button:disabled {
  opacity: 0.65;
}

.empty-state {
  text-align: center;
  color: var(--sb-text-muted);
  padding: 42px 16px;
}

.empty-state i {
  display: block;
  font-size: 36px;
  color: var(--sb-primary);
  margin-bottom: 8px;
}

@media (max-width: 980px) {
  .users-header {
    grid-template-columns: 1fr;
    display: grid;
  }

  .header-actions {
    width: 100%;
  }

  .search-input {
    width: 100%;
  }
}

@media (max-width: 640px) {
  .superadmin-users {
    padding: 16px;
  }

  .filter-row :deep(.filter-trigger),
  .export-button {
    width: 100%;
  }
}
</style>
