<template>
  <template v-if="isSwitchable">
    <button
      type="button"
      class="sb-item sb-item-btn"
      data-test="mode-switch"
      :title="switchLabel"
      :aria-label="switchLabel"
      :disabled="isSwitching"
      @click="onSwitchClick"
    >
      <span class="sb-chip"><i class="bi bi-arrow-left-right"></i></span>
      <span class="sb-item-label">{{ isSwitching ? 'Switching...' : switchLabel }}</span>
    </button>

    <!-- `data-sb-owned` keeps clearBootstrapModalState() from ripping out a backdrop Vue renders. -->
    <Teleport to="body">
      <div v-if="showSetupModal" class="modal-backdrop fade show" data-sb-owned @click="closeModal"></div>

      <div
        v-if="showSetupModal"
        class="modal show"
        tabindex="-1"
        role="dialog"
        aria-modal="true"
        style="display: block;"
        @click.self="closeModal"
      >
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content rounded-4">
            <div class="modal-header border-0">
              <h5 class="modal-title fw-bold">No {{ targetLabel }} account yet</h5>
              <button type="button" class="btn-close" aria-label="Close" @click="closeModal"></button>
            </div>

            <div class="modal-body sb-muted">
              You currently don't have a {{ targetLabel }} account. Setting one up takes a few
              steps, and you can switch back any time &mdash; your existing
              {{ currentLabel }} account stays exactly as it is.
              <p v-if="verificationCarriesOver" class="mb-0 mt-3">
                Your documents are already verified, so you won't need to upload them again.
              </p>
            </div>

            <div class="modal-footer border-0">
              <button class="btn btn-light sb-btn" :disabled="isSwitching" @click="closeModal">
                Not now
              </button>
              <button
                class="btn bg-sb-primary text-white sb-btn sb-elevated sb-elevated--brand"
                :disabled="isSwitching"
                @click="confirmSetup"
              >
                Set up {{ targetLabel }} account
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </template>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProfileStore } from '@/stores/profile'
import { useToastStore } from '@/stores/toast'

const router = useRouter()
const authStore = useAuthStore()
const profileStore = useProfileStore()
const toastStore = useToastStore()

const MODE_LABELS = { tutor: 'Tutor', tutee: 'Tutee' }
const MODE_HOME = { tutor: '/tch-dashboard', tutee: '/dashboard' }

const showSetupModal = ref(false)
const isSwitching = ref(false)

const role = computed(() => authStore.user?.role?.toLowerCase() || null)

// SuperAdmins are excluded outright: get_login_profile_for_user force-resets staff back to
// SuperAdmin on every login, so a switched admin would be flipped back mid-session.
const isSwitchable = computed(() => role.value === 'tutor' || role.value === 'tutee')

const targetRole = computed(() => (role.value === 'tutor' ? 'tutee' : 'tutor'))
const targetLabel = computed(() => MODE_LABELS[targetRole.value] || '')
const currentLabel = computed(() => MODE_LABELS[role.value] || '')
const switchLabel = computed(() => `Switch to ${targetLabel.value}`)

const isProvisioned = computed(() =>
  targetRole.value === 'tutor' ? profileStore.canTutor : profileStore.canTutee
)

// Both applications collect the same two documents, so an approved one carries across.
const verificationCarriesOver = computed(() => profileStore.applicationStatus === 'approved')

const closeModal = () => {
  showSetupModal.value = false
}

const switchTo = async (mode) => {
  isSwitching.value = true

  try {
    await authStore.switchMode(mode)
    await profileStore.checkProfileStatus()
    // Push the mode's home and let the router guards take it from there -- an unprovisioned mode
    // is redirected into its own onboarding by the same gates that handle a fresh account.
    await router.push(MODE_HOME[mode])
  } catch (error) {
    console.error('Mode switch failed:', error)
    toastStore.push('Could not switch modes. Please try again.', 'error')
  } finally {
    isSwitching.value = false
  }
}

const onSwitchClick = () => {
  if (!isProvisioned.value) {
    showSetupModal.value = true
    return
  }

  switchTo(targetRole.value)
}

const confirmSetup = async () => {
  const mode = targetRole.value
  await switchTo(mode)
  closeModal()
}
</script>
