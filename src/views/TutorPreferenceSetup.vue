<template>
  <div class="min-vh-100 py-5 tutor-setup-page">
    <div class="container-fluid px-4 mb-3 d-flex justify-content-between align-items-center">
      <span class="fw-bold sb-text">StudyBuddy</span>
      <SbThemeToggle />
    </div>

    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-7 col-lg-6">
          <div class="card border-0 sb-card-surface sb-text shadow-sm rounded-4">
            <div class="card-body p-4 p-md-5">
              <div class="text-center mb-4">
                <h3 class="fw-bold sb-text">Tutor Profile Setup</h3>
                <p class="sb-muted">Set your teaching preferences to start matching.</p>
              </div>

              <form @submit.prevent="handleCompleteSetup">
                <div class="mb-4">
                  <label class="form-label fw-bold small sb-muted">TEACHING LEVEL</label>
                  <SbSelectModal
                    v-model="form.teaching_level"
                    :options="teachingLevelOptions"
                    title="Teaching Level"
                    placeholder="Select level"
                    trigger-class="form-select border-sb shadow-none"
                  />
                </div>

                <div class="mb-4">
                  <label class="form-label fw-bold small sb-muted d-block">MODALITY</label>
                  <div class="modality-pill-group">
                    <button
                      type="button"
                      class="modality-pill sb-btn sb-pill"
                      :class="{ 'modality-pill-active': form.can_online }"
                      :aria-pressed="form.can_online"
                      @click="form.can_online = !form.can_online"
                    >
                      <span class="modality-pill-icon"><i class="bi bi-camera-video-fill"></i></span>
                      <span>Online</span>
                    </button>
                    <button
                      type="button"
                      class="modality-pill sb-btn sb-pill"
                      :class="{ 'modality-pill-active': form.can_f2f }"
                      :aria-pressed="form.can_f2f"
                      @click="form.can_f2f = !form.can_f2f"
                    >
                      <span class="modality-pill-icon"><i class="bi bi-geo-alt-fill"></i></span>
                      <span>Face-to-Face</span>
                    </button>
                  </div>
                </div>

                <div class="mb-4">
                  <label class="form-label fw-bold small sb-muted" for="hourly-rate-input">HOURLY RATE (PHP)</label>
                  <div
                    class="rate-scrub-shell"
                    :class="{ 'is-scrubbing': isScrubbingRate }"
                    @mousedown="startRateScrub"
                  >
                    <span class="rate-prefix">PHP</span>
                    <input
                      id="hourly-rate-input"
                      type="text"
                      inputmode="numeric"
                      class="rate-scrub-input"
                      v-model="form.hourly_rate"
                      placeholder="0.00"
                      required
                      @mousedown.stop
                      @input="sanitizeRateInput"
                    >
                    <span class="rate-scrub-hint">drag &harr; or type</span>
                  </div>
                </div>

                <div class="form-check mb-5">
                  <input class="form-check-input" type="checkbox" v-model="commissionTermsAccepted" id="commission-terms">
                  <label class="form-check-label small sb-muted" for="commission-terms">
                    I understand StudyBuddy deducts a {{ commissionRatePercent }}% platform fee from
                    each completed session's payout.
                  </label>
                </div>

                <button type="submit" class="btn bg-sb-primary text-white w-100 py-3 rounded-3 fw-bold shadow-sm sb-btn" :disabled="!commissionTermsAccepted">
                  Complete Profile
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useProfileStore } from '@/stores/profile'
import { useToastStore } from '@/stores/toast'
import api from '@/services/api/api'
import { PLATFORM_COMMISSION_RATE_PERCENT } from '@/config'
import { computeScrubbedRate, MIN_HOURLY_RATE } from '@/utils/rateScrub'
import SbThemeToggle from '@/components/SbThemeToggle.vue'
import SbSelectModal from '@/components/SbSelectModal.vue'

const router = useRouter()
const profileStore = useProfileStore()
const toastStore = useToastStore()

const commissionRatePercent = PLATFORM_COMMISSION_RATE_PERCENT

const form = ref({
  teaching_level: '',
  can_online: true,
  can_f2f: false,
  hourly_rate: null
})

// Pre-checked once accepted (see profileStore.checkProfileStatus) so a returning tutor editing
// their profile isn't asked to re-acknowledge every time — see ADR-0010.
const commissionTermsAccepted = ref(profileStore.commissionTermsAccepted)

const teachingLevelOptions = [
  { label: 'Elementary', value: 'Elementary' },
  { label: 'High School', value: 'High School' },
  { label: 'College', value: 'College' },
]

/* HOURLY RATE — click-drag "scrub" gesture, layered on top of normal typing.
   Clicking the input itself (stopped via @mousedown.stop in the template) focuses it for
   typing; a mousedown anywhere else on the shell starts a drag that adjusts the rate by
   computeScrubbedRate's 1-PHP-per-pixel math (src/utils/rateScrub.js). */
const isScrubbingRate = ref(false)
let scrubStartX = 0
let scrubStartValue = 0

const startRateScrub = (event) => {
  isScrubbingRate.value = true
  scrubStartX = event.clientX
  scrubStartValue = Number(form.value.hourly_rate) || 0
  document.addEventListener('mousemove', onRateScrub)
  document.addEventListener('mouseup', endRateScrub)
}

const onRateScrub = (event) => {
  if (!isScrubbingRate.value) return
  const deltaX = event.clientX - scrubStartX
  form.value.hourly_rate = computeScrubbedRate(scrubStartValue, deltaX)
}

const endRateScrub = () => {
  isScrubbingRate.value = false
  document.removeEventListener('mousemove', onRateScrub)
  document.removeEventListener('mouseup', endRateScrub)
}

// Typing bypasses the scrub math, so strip anything that isn't a digit or a single
// decimal point (the field is text, not number, to keep the drag gesture usable).
const sanitizeRateInput = (event) => {
  const sanitized = event.target.value
    .replace(/[^\d.]/g, '')
    .replace(/(\..*)\./g, '$1')
  form.value.hourly_rate = sanitized
}

onBeforeUnmount(() => {
  document.removeEventListener('mousemove', onRateScrub)
  document.removeEventListener('mouseup', endRateScrub)
})


/* LOAD EXISTING TUTOR DATA */
onMounted(async () => {

  try {

    const response = await api.get('/tutor-dashboard/')

    const tutor = response.data

    form.value.teaching_level = tutor.teaching_level
    form.value.can_online = tutor.can_online
    form.value.can_f2f = tutor.can_f2f
    form.value.hourly_rate = tutor.hourly_rate

  } catch {

    console.log("New tutor setup")

  }

})


/* SUBMIT PROFILE SETUP */
const handleCompleteSetup = async () => {

  if (!form.value.teaching_level) {
    toastStore.push("Please select your teaching level.", 'warning')
    return
  }

  const parsedRate = Number(form.value.hourly_rate)

  if (!form.value.hourly_rate || Number.isNaN(parsedRate) || parsedRate <= MIN_HOURLY_RATE) {
    toastStore.push("Please enter a valid hourly rate.", 'warning')
    return
  }

  if (!commissionTermsAccepted.value) {
    toastStore.push("Please acknowledge the platform commission before continuing.", 'warning')
    return
  }

  try {

    await api.post('/tutor/setup/', {
      ...form.value,
      hourly_rate: parsedRate,
      commission_terms_accepted: commissionTermsAccepted.value,
    })

    // update profile guard state
    profileStore.profileCompleted = true
    profileStore.commissionTermsAccepted = true

    router.push({ name: 'tutor-subjects-setup' })

  } catch (error) {

    console.error("Failed to save tutor profile", error)
    toastStore.push("Could not save tutor profile.", 'error')

  }

}
</script>

<style scoped>
.tutor-setup-page {
  background-color: var(--sb-bg);
}

/* Modality pills — same visual language as InitialBooking.vue's "Preferred Mode"
   picker (.mode-button), but multi-select: can_online / can_f2f stay independent
   booleans since a tutor may support both at once. Motion tokens only, no new
   easing/keyframes, per docs/specs/2026-06-21-feel-haptics-unification-design.md. */
.modality-pill-group {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

/* .sb-btn / .sb-pill (main.css) already supply hover-lift, press-scale, and the
   prefers-reduced-motion guard — this block only adds the layout/color local
   overrides, mirroring InitialBooking.vue's .mode-button (same house pattern,
   applied here as multi-select instead of single-select). */
.modality-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 44px;
  border: 1px solid var(--sb-card-border);
  border-radius: 14px;
  background: var(--sb-card-bg);
  color: var(--sb-text-main);
  padding: 9px 10px;
  font-size: 14px;
  font-weight: 700;
  line-height: 1.2;
}

.modality-pill:hover,
.modality-pill:focus-visible {
  border-color: var(--sb-primary);
  box-shadow: var(--sb-halo);
  outline: none;
}

.modality-pill-active {
  border-color: var(--sb-primary);
  background: color-mix(in srgb, var(--sb-primary) 12%, var(--sb-card-bg));
  color: var(--sb-primary);
}

.modality-pill-icon {
  display: inline-flex;
  flex: 0 0 auto;
}

/* Hourly rate — typable + click-drag "scrub" field (see src/utils/rateScrub.js for the
   drag math). .sb-field's canonical immediate focus snap is reproduced here via
   :focus-within since focus lands on the inner <input>, not this wrapping shell. */
.rate-scrub-shell {
  position: relative;
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  border: 1.5px solid var(--sb-card-border);
  border-radius: 0.6rem;
  padding: 0.65rem 0.9rem;
  background: var(--sb-card-bg);
  transition: none;
}

/* Dragging only exists for mouse/trackpad input — on touch, the shell is just a normal
   text field, so don't show a drag cursor or hint that touch users can't act on. */
@media (hover: hover) and (pointer: fine) {
  .rate-scrub-shell {
    cursor: ew-resize;
  }
}

.rate-scrub-shell:focus-within,
.rate-scrub-shell.is-scrubbing {
  border-color: var(--sb-primary);
  box-shadow: var(--sb-halo);
}

.rate-prefix {
  color: var(--sb-text-muted);
  font-weight: 700;
  font-size: 0.95rem;
  pointer-events: none;
}

.rate-scrub-input {
  flex: 1 1 auto;
  min-width: 0;
  border: none;
  background: transparent;
  outline: none;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--sb-text-main);
  cursor: text;
  padding: 0;
}

.rate-scrub-hint {
  display: none;
  font-size: 0.65rem;
  color: var(--sb-text-muted);
  opacity: 0.7;
  pointer-events: none;
  white-space: nowrap;
}

@media (hover: hover) and (pointer: fine) {
  .rate-scrub-hint {
    display: inline;
  }
}
</style>
