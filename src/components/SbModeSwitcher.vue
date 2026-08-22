<template>
  <template v-if="isSwitchable">

    <div
      class="sb-mode"
      :class="{ 'sb-mode--collapsed': isCollapsed }"
      role="radiogroup"
      :aria-label="GROUP_LABEL"
      :aria-busy="isSwitching"
      data-test="mode-switch"
      @keydown="onGroupKeydown"
    >
      <button
        v-for="(mode, index) in MODES"
        :key="mode"
        :ref="(el) => setCellRef(el, index)"
        type="button"
        role="radio"
        class="sb-mode-cell"
        :class="{ 'sb-mode-cell--on': mode === role }"
        :aria-checked="mode === role"
        :tabindex="index === focusedIndex ? 0 : -1"
        :title="MODE_LABELS[mode]"
        :aria-label="MODE_LABELS[mode]"
        :data-test="`mode-switch-${mode}`"
        @click="onSelect(mode)"
        @focus="focusedIndex = index"
      >
        <span aria-hidden="true">
          {{ isCollapsed ? MODE_ABBREVIATIONS[mode] : MODE_LABELS[mode] }}
        </span>
      </button>
    </div>


    <!-- The selected cell tracks the committed role, so the busy state has nowhere visible to -->
    <!-- live; announce it instead of dropping focus by disabling the cell the user is on. -->
    <span class="visually-hidden" role="status" data-test="mode-switch-status">
      {{ isSwitching ? `Switching to ${targetLabel} mode` : '' }}
    </span>

    <!-- `data-sb-owned` keeps clearBootstrapModalState() from ripping out a backdrop Vue renders. -->
    <Teleport to="body">
      <div v-if="showSetupModal" class="modal-backdrop fade show" data-sb-owned @click="closeModal"></div>

      <div
        v-if="showSetupModal"
        ref="dialogEl"
        class="modal show"
        tabindex="-1"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="SETUP_TITLE_ID"
        style="display: block;"
        @click.self="closeModal"
        @keydown.tab.prevent="onDialogTab"
      >
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content rounded-4">
            <div class="modal-header border-0">
              <h5 :id="SETUP_TITLE_ID" class="modal-title fw-bold">No {{ targetLabel }} account yet</h5>
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
                ref="confirmEl"
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
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProfileStore } from '@/stores/profile'
import { useSidebarStore } from '@/stores/sidebar'
import { useToastStore } from '@/stores/toast'

const router = useRouter()
const authStore = useAuthStore()
const profileStore = useProfileStore()
const sidebarStore = useSidebarStore()
const toastStore = useToastStore()

const MODES = ['tutee', 'tutor']
const MODE_LABELS = { tutor: 'Tutor', tutee: 'Tutee' }
const MODE_HOME = { tutor: '/tch-dashboard', tutee: '/dashboard' }
// Shown only on the 76px rail, where the full label cannot fit. The accessible name and the
// tooltip both keep the real word, so the abbreviation is never the only thing carrying meaning.
const MODE_ABBREVIATIONS = { tutor: 'TR', tutee: 'TE' }
const GROUP_LABEL = 'Account mode'
const SETUP_TITLE_ID = 'sb-mode-setup-title'
const PREVIOUS_KEYS = ['ArrowLeft', 'ArrowUp']
const NEXT_KEYS = ['ArrowRight', 'ArrowDown']

const showSetupModal = ref(false)
const isSwitching = ref(false)
const cellRefs = ref([])
const dialogEl = ref(null)
const confirmEl = ref(null)
const returnFocusEl = ref(null)

const role = computed(() => authStore.user?.role?.toLowerCase() || null)

// SuperAdmins are excluded outright: get_login_profile_for_user force-resets staff back to
// SuperAdmin on every login, so a switched admin would be flipped back mid-session.
const isSwitchable = computed(() => role.value === 'tutor' || role.value === 'tutee')

const isCollapsed = computed(() => sidebarStore.collapsed)

const targetRole = computed(() => (role.value === 'tutor' ? 'tutee' : 'tutor'))
const targetLabel = computed(() => MODE_LABELS[targetRole.value] || '')
const currentLabel = computed(() => MODE_LABELS[role.value] || '')

const focusedIndex = ref(Math.max(MODES.indexOf(role.value), 0))

const isProvisioned = computed(() =>
  targetRole.value === 'tutor' ? profileStore.canTutor : profileStore.canTutee
)

// Both applications collect the same two documents, so an approved one carries across.
const verificationCarriesOver = computed(() => profileStore.applicationStatus === 'approved')

const setCellRef = (el, index) => {
  cellRefs.value[index] = el
}

// Arrow keys move focus without selecting. The standard radiogroup would switch mode on every
// arrow press; switching navigates the whole app, so activation stays on Space/Enter and click.
const onGroupKeydown = (event) => {
  const step = NEXT_KEYS.includes(event.key) ? 1 : PREVIOUS_KEYS.includes(event.key) ? -1 : 0
  if (!step) return

  event.preventDefault()
  focusedIndex.value = (focusedIndex.value + step + MODES.length) % MODES.length
  cellRefs.value[focusedIndex.value]?.focus()
}

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

const onSelect = (mode) => {
  if (isSwitching.value || mode === role.value) return

  if (!isProvisioned.value) {
    returnFocusEl.value = cellRefs.value[MODES.indexOf(mode)] || null
    showSetupModal.value = true
    return
  }

  switchTo(mode)
}

const confirmSetup = async () => {
  await switchTo(targetRole.value)
  closeModal()
}

const focusableInDialog = () =>
  Array.from(dialogEl.value?.querySelectorAll('button:not([disabled])') || [])

const onDialogTab = (event) => {
  const focusable = focusableInDialog()
  if (!focusable.length) return

  const current = focusable.indexOf(document.activeElement)
  const step = event.shiftKey ? -1 : 1
  const next = (current + step + focusable.length) % focusable.length
  focusable[next].focus()
}

const onDocumentKeydown = (event) => {
  if (event.key === 'Escape' && !isSwitching.value) closeModal()
}

watch(showSetupModal, async (open) => {
  if (open) {
    document.addEventListener('keydown', onDocumentKeydown)
    await nextTick()
    confirmEl.value?.focus()
    return
  }

  document.removeEventListener('keydown', onDocumentKeydown)
  returnFocusEl.value?.focus()
  returnFocusEl.value = null
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', onDocumentKeydown)
})
</script>

<style scoped>
/* This component owns every class it renders. It previously borrowed .sb-item / .sb-chip from
   AppSidebar's scoped block, which never applied: a multi-root fragment does not inherit the
   parent's scope id, so the control rendered as an unstyled user-agent button. */
.sb-mode {
  display: flex;
  gap: 2px;
  margin: 0 0.1rem;
  padding: 3px;
  border: 1px solid var(--sb-card-border);
  border-radius: 999px;
  background: var(--sb-bg);
}

.sb-mode[aria-busy='true'] {
  opacity: 0.6;
  pointer-events: none;
}

.sb-mode-cell {
  flex: 1;
  min-width: 0;
  padding: 0.32rem 0.2rem;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: var(--sb-text-muted);
  font-family: inherit;
  font-size: 0.8rem;
  font-weight: 700;
  text-align: center;
  cursor: pointer;
  transition: background-color var(--sb-t-normal) var(--sb-spring),
              color var(--sb-t-normal) var(--sb-spring);
}

.sb-mode-cell:hover:not(.sb-mode-cell--on) {
  color: var(--sb-text-main);
}

.sb-mode-cell--on {
  background: var(--sb-primary);
  color: #fff;
  cursor: default;
}

.sb-mode-cell span {
  display: block;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.sb-mode--collapsed {
  flex-direction: column;
  border-radius: 14px;
}

.sb-mode--collapsed .sb-mode-cell {
  padding: 0.3rem 0.1rem;
  border-radius: 10px;
  font-size: 0.68rem;
}
</style>
