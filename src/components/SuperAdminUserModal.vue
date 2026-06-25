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
        </div>

        <div v-else class="modal-section">
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
import { computed, ref, watch } from 'vue'
import SbSelectModal from '@/components/SbSelectModal.vue'
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

watch(
  () => props.user,
  (user) => {
    draftRole.value = user?.role || ''
    draftInstitution.value = user?.institution || ''
    activeTab.value = 'profile'
    suspendConfirm.value = false
    vibrate(patterns.light)
  },
  { immediate: true }
)

function switchTab(tab) {
  activeTab.value = tab
  suspendConfirm.value = false
  vibrate(patterns.light)
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
