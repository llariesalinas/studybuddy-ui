<template>
  <TutorOnboardingShell :current-step="1">
    <h3>Tutor profile setup</h3>
    <p class="muted">Set your teaching preferences to start matching.</p>

    <form @submit.prevent="handleCompleteSetup">
      <div class="field-block">
        <label class="field-label">Teaching Level</label>
        <SbSelectModal
          v-model="form.teaching_level"
          :options="teachingLevelOptions"
          title="Teaching Level"
          placeholder="Select level"
          trigger-class="form-select border-sb shadow-none"
        />
      </div>

      <div class="field-block">
        <label class="field-label">Modality</label>
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

      <div class="field-block">
        <label class="field-label" for="hourly-rate-input">Hourly Rate (PHP)</label>
        <div class="rate-input-shell">
          <span class="rate-prefix">PHP</span>
          <input
            id="hourly-rate-input"
            type="text"
            inputmode="numeric"
            class="rate-input"
            v-model="form.hourly_rate"
            placeholder="0.00"
            required
            @input="sanitizeRateInput"
          >
        </div>
      </div>

      <div class="commission-row">
        <input class="form-check-input" type="checkbox" v-model="commissionTermsAccepted" id="commission-terms">
        <label class="form-check-label" for="commission-terms">
          I understand StudyBuddy deducts a {{ commissionRatePercent }}% platform fee from
          each completed session's payout.
        </label>
      </div>

      <button type="submit" class="btn-primary-pill sb-btn" :disabled="!commissionTermsAccepted">
        Continue to Subjects
      </button>
    </form>
  </TutorOnboardingShell>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProfileStore } from '@/stores/profile'
import { useToastStore } from '@/stores/toast'
import api from '@/services/api/api'
import { PLATFORM_COMMISSION_RATE_PERCENT } from '@/config'
import SbSelectModal from '@/components/SbSelectModal.vue'
import TutorOnboardingShell from '@/components/TutorOnboardingShell.vue'

const router = useRouter()
const profileStore = useProfileStore()
const toastStore = useToastStore()

const commissionRatePercent = PLATFORM_COMMISSION_RATE_PERCENT

// A tutor's hourly rate can't be negative.
const MIN_HOURLY_RATE = 0

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

// The field is text (not number) so it can carry the PHP prefix inline; strip anything
// that isn't a digit or a single decimal point as the tutor types.
const sanitizeRateInput = (event) => {
  const sanitized = event.target.value
    .replace(/[^\d.]/g, '')
    .replace(/(\..*)\./g, '$1')
  form.value.hourly_rate = sanitized
}


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
.field-block {
  margin-bottom: 1.25rem;
}

.field-label {
  display: block;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--sb-text-muted);
  margin-bottom: 8px;
}

.commission-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin: 0 0 1.5rem;
  font-size: 0.82rem;
  color: var(--sb-text-muted);
}

.commission-row .form-check-input {
  margin-top: 3px;
  flex-shrink: 0;
}

.btn-primary-pill {
  width: 100%;
  border: 0;
  border-radius: 999px;
  padding: 11px 24px;
  font-weight: 700;
  font-size: 13.5px;
  background: var(--sb-primary);
  color: var(--sb-primary-contrast);
}

.btn-primary-pill:hover:not(:disabled) {
  background: var(--sb-primary-hover);
}

.btn-primary-pill:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

/* Hourly rate — plain typable field with an inline PHP prefix. .sb-field's canonical
   immediate focus snap is reproduced here via :focus-within since focus lands on the
   inner <input>, not this wrapping shell. */
.rate-input-shell {
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

.rate-input-shell:focus-within {
  border-color: var(--sb-primary);
  box-shadow: var(--sb-halo);
}

.rate-prefix {
  color: var(--sb-text-muted);
  font-weight: 700;
  font-size: 0.95rem;
  pointer-events: none;
}

.rate-input {
  flex: 1 1 auto;
  min-width: 0;
  border: none;
  background: transparent;
  outline: none;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--sb-text-main);
  padding: 0;
}
</style>
