<template>
  <TutorOnboardingShell :current-step="3">
    <h3>Last step: verification</h3>
    <p class="muted">Upload your documents now, or finish later.</p>

    <div class="why-strip">
      <i class="bi bi-info-circle" aria-hidden="true"></i>
      <span
        ><strong>Verified tutors appear in tutee search.</strong> Until an admin approves your
        documents, tutees can't find or book you — but you can still use the rest of the
        app.</span
      >
    </div>

    <label class="field-label" for="school-id">School ID</label>
    <label class="upload-row" for="school-id">
      <i class="bi bi-file-earmark-arrow-up" aria-hidden="true"></i>
      <span>{{ schoolId?.name || 'Click to upload' }}</span>
    </label>
    <input
      id="school-id"
      class="visually-hidden"
      type="file"
      accept="image/*"
      @change="handleFileChange($event, 'schoolId')"
    />

    <label class="field-label" for="enrollment-proof">Enrollment proof</label>
    <label class="upload-row" for="enrollment-proof">
      <i class="bi bi-file-earmark-arrow-up" aria-hidden="true"></i>
      <span>{{ enrollmentProof?.name || 'Click to upload' }}</span>
    </label>
    <input
      id="enrollment-proof"
      class="visually-hidden"
      type="file"
      accept="image/*,.pdf"
      @change="handleFileChange($event, 'enrollmentProof')"
    />

    <div class="stack-actions">
      <button
        type="button"
        class="btn-primary-pill sb-btn"
        :disabled="isSubmitting"
        @click="submitVerification"
      >
        {{ isSubmitting ? 'Submitting...' : 'Submit & Finish Onboarding' }}
      </button>
      <div class="step-nav-row">
        <button
          type="button"
          class="btn-outline-pill sb-btn"
          :disabled="isSubmitting"
          @click="goBackToSubjects"
        >
          &larr; Back
        </button>
        <button
          type="button"
          class="btn-outline-pill sb-btn"
          :disabled="isSubmitting"
          @click="skipVerification"
        >
          Skip for Now
        </button>
      </div>
    </div>
  </TutorOnboardingShell>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import TutorOnboardingShell from '@/components/TutorOnboardingShell.vue'
import { useProfileStore } from '@/stores/profile'
import { useToastStore } from '@/stores/toast'
import { skipTutorVerification, submitTutorVerification } from '@/services/tutorOnboarding'
import { MAX_DOCUMENT_UPLOAD_SIZE_BYTES } from '@/config'

const router = useRouter()
const profileStore = useProfileStore()
const toastStore = useToastStore()
const schoolId = ref(null)
const enrollmentProof = ref(null)
const isSubmitting = ref(false)

const handleFileChange = (event, type) => {
  const file = event.target.files[0]
  if (!file) return

  if (file.size > MAX_DOCUMENT_UPLOAD_SIZE_BYTES) {
    toastStore.push(`"${file.name}" is too large. Each file must be under 5 MB.`, 'warning')
    event.target.value = ''
    return
  }

  if (type === 'schoolId') schoolId.value = file
  else enrollmentProof.value = file
}

const finishOnboarding = async (payload) => {
  profileStore.applicationStatus = payload.application_status || null
  profileStore.tutorOnboardingSkippedAt = payload.tutor_onboarding_skipped_at || null
  profileStore.tutorOnboardingComplete = true
  await router.push({ name: 'tch-dashboard' })
}

const submitVerification = async () => {
  if (!schoolId.value || !enrollmentProof.value) {
    toastStore.push('Please upload both your School ID and enrollment proof.', 'warning')
    return
  }

  isSubmitting.value = true
  try {
    const formData = new FormData()
    formData.append('school_id', schoolId.value)
    formData.append('enrollment_proof', enrollmentProof.value)
    const application = await submitTutorVerification(formData, {
      resubmit: profileStore.applicationStatus === 'rejected',
    })
    await finishOnboarding({ ...application, application_status: 'pending' })
  } catch (error) {
    toastStore.push(error.response?.data?.error || 'Could not submit your documents.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

const skipVerification = async () => {
  isSubmitting.value = true
  try {
    const onboardingState = await skipTutorVerification()
    await finishOnboarding(onboardingState)
  } catch (error) {
    toastStore.push(error.response?.data?.error || 'Could not skip verification.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

const goBackToSubjects = () => {
  router.push({ name: 'tutor-subjects-setup' })
}
</script>

<style scoped>
.why-strip {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  background: color-mix(in srgb, var(--sb-primary) 6%, var(--sb-card-bg));
  border: 1px solid var(--sb-card-border);
  border-radius: 12px;
  padding: 12px 14px;
  margin-bottom: 18px;
  font-size: 0.83rem;
  color: var(--sb-text-muted);
}
.why-strip i {
  color: var(--sb-primary);
  margin-top: 2px;
}
.why-strip strong {
  color: var(--sb-text-main);
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
.upload-row {
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1.5px dashed var(--sb-card-border);
  border-radius: 12px;
  padding: 14px 16px;
  margin-bottom: 14px;
  font-size: 0.88rem;
  color: var(--sb-text-muted);
  cursor: pointer;
  overflow-wrap: anywhere;
}
.upload-row:hover {
  border-color: var(--sb-primary);
}
.upload-row i {
  color: var(--sb-primary);
  font-size: 1.2rem;
}
.stack-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 20px;
}
.step-nav-row {
  display: flex;
  gap: 10px;
}
.step-nav-row .btn-outline-pill {
  width: auto;
  flex: 1;
}
.btn-primary-pill,
.btn-outline-pill {
  width: 100%;
  border-radius: 999px;
  padding: 11px 24px;
  font-weight: 700;
  font-size: 13.5px;
}
.btn-primary-pill {
  background: var(--sb-primary);
  color: var(--sb-primary-contrast);
  border: 0;
}
.btn-primary-pill:hover {
  background: var(--sb-primary-hover);
}
.btn-outline-pill {
  background: transparent;
  border: 1px solid var(--sb-card-border);
  color: var(--sb-text-main);
}
.btn-outline-pill:hover {
  border-color: var(--sb-primary);
  color: var(--sb-primary);
}
</style>
