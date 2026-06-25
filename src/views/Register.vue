<template>
  <AuthShell>
    <template #icon>
      <i class="bi bi-book"></i>
    </template>
    <template #title>Create Account</template>
    <template #subtitle>Join the StudyBuddy network</template>

    <div v-if="generalError" class="sb-auth-alert">{{ generalError }}</div>

    <form @submit.prevent="handleRegister">
      <div class="sb-auth-field">
        <label class="sb-auth-label">First Name</label>
        <input
          type="text"
          v-model="store.newUserFname"
          class="sb-auth-input sb-field"
          placeholder="Juan"
          required
        />
      </div>

      <div class="sb-auth-field">
        <label class="sb-auth-label">Middle Name</label>
        <input
          type="text"
          v-model="store.newUserMname"
          class="sb-auth-input sb-field"
          placeholder="Optional"
        />
      </div>

      <div class="sb-auth-field">
        <label class="sb-auth-label">Last Name</label>
        <input
          type="text"
          v-model="store.newUserLname"
          class="sb-auth-input sb-field"
          placeholder="Dela Cruz"
          required
        />
      </div>

      <div class="sb-auth-field">
        <label class="sb-auth-label">University Email</label>
        <input
          type="email"
          v-model="store.newUserEmail"
          class="sb-auth-input sb-field"
          placeholder="you@university.edu"
          required
        />
        <div v-if="emailError" class="sb-auth-field-error">{{ emailError }}</div>
      </div>

      <div class="sb-auth-field">
        <label class="sb-auth-label">Institution</label>
        <SbSelectModal
          v-model="store.selectedInstitutionId"
          :options="institutionOptions"
          title="Institution"
          placeholder="Select your institution"
          searchable
          trigger-class="sb-auth-select"
        />
        <div v-if="selectedInstitutionDomain" class="sb-auth-helper">
          Allowed email domain: {{ selectedInstitutionDomain }}
        </div>
        <div v-if="institutionError" class="sb-auth-field-error">{{ institutionError }}</div>
      </div>

      <div class="sb-auth-field">
        <label class="sb-auth-label">Password</label>
        <input
          type="password"
          v-model="store.newUserPassword"
          class="sb-auth-input sb-field"
          placeholder="••••••••"
          required
        />
      </div>

      <div class="sb-auth-field">
        <label class="sb-auth-label">I want to</label>
        <SbSelectModal
          v-model="store.newUserType"
          :options="roleOptions"
          title="I want to"
          placeholder="Select your role"
          trigger-class="sb-auth-select"
        />
      </div>

      <button type="submit" class="sb-btn-pill sb-auth-submit sb-btn sb-elevated sb-elevated--brand" :disabled="isSubmitting">
        <span v-if="isSubmitting" class="sb-spinner" aria-hidden="true"></span>
        {{ isSubmitting ? 'Processing...' : 'Create Account' }}
      </button>
    </form>
  </AuthShell>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useRegistrationInfoStore } from '@/stores/registrationinfo'
import api from '@/services/api/api'
import { useCatalogStore } from '@/stores/catalog'
import AuthShell from '@/components/AuthShell.vue'
import SbSelectModal from '@/components/SbSelectModal.vue'

const router = useRouter()
const store = useRegistrationInfoStore()
const catalogStore = useCatalogStore()

const isSubmitting = ref(false)
const institutions = ref([])

const generalError = ref('')
const emailError = ref('')
const institutionError = ref('')

const roleOptions = [
  { label: 'Find a Tutor (Student)', value: 'Tutee' },
  { label: 'Become a Tutor', value: 'Tutor' },
]

const institutionOptions = computed(() =>
  institutions.value.map((institution) => ({
    label: `${institution.institution_name} (${institution.school_email_domain})`,
    value: String(institution.id),
  }))
)

const selectedInstitution = computed(() => {
  return (
    institutions.value.find(
      (institution) => String(institution.id) === String(store.selectedInstitutionId),
    ) || null
  )
})

const selectedInstitutionDomain = computed(() => {
  return selectedInstitution.value?.school_email_domain || ''
})

const emailDomainMatchesInstitution = computed(() => {
  if (!store.newUserEmail || !selectedInstitutionDomain.value) return true
  const parts = store.newUserEmail.split('@')
  if (parts.length !== 2) return false
  return parts[1].trim().toLowerCase() === selectedInstitutionDomain.value.toLowerCase()
})

const loadInstitutions = async () => {
  try {
    institutions.value = await catalogStore.fetchPartnerInstitutions()
  } catch (error) {
    console.error('Failed to load partner institutions:', error)
    generalError.value = 'Unable to load partner institutions right now. Please try again later.'
  }
}

const handleRegister = async () => {
  generalError.value = ''
  emailError.value = ''
  institutionError.value = ''

  if (
    !store.newUserFname ||
    !store.newUserLname ||
    !store.newUserEmail ||
    !store.newUserPassword
  ) {
    generalError.value = 'Please fill in all required fields.'
    return
  }

  if (!store.selectedInstitutionId) {
    institutionError.value = 'Please select your institution.'
    return
  }

  if (!store.newUserType) {
    generalError.value = 'Please select your role.'
    return
  }

  if (!emailDomainMatchesInstitution.value) {
    institutionError.value =
      'Your email domain does not match the selected institution. Please check and try again.'
    return
  }

  isSubmitting.value = true

  try {
    const role = store.newUserType

    await api.post('register/', {
      fname: store.newUserFname,
      mname: store.newUserMname,
      lname: store.newUserLname,
      email: store.newUserEmail,
      password: store.newUserPassword,
      role: role,
      institution_id: store.selectedInstitutionId,
    })

    router.push({
      name: 'login',
      query: {
        registered: 'success',
        email: store.newUserEmail,
      },
    })
  } catch (error) {
    console.error('Registration Error:', error)

    if (error.response) {
      const data = error.response.data
      const message = data.error || data.detail || 'Registration failed. Please try again.'

      if (message.toLowerCase().includes('email')) emailError.value = message
      else if (message.toLowerCase().includes('institution')) institutionError.value = message
      else generalError.value = message
    } else if (error.request) {
      generalError.value = 'Server not responding. Please try again later.'
    } else {
      generalError.value = 'An unexpected error occurred.'
    }
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  loadInstitutions()
})
</script>

<style scoped>
.sb-auth-field {
  margin-bottom: 16px;
}

.sb-auth-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--sb-text-main);
  margin-bottom: 6px;
}

.sb-auth-input,
.sb-auth-select {
  width: 100%;
  padding: 10px 14px;
  font-size: 14px;
  border: 1px solid var(--sb-card-border);
  border-radius: 12px;
  background: var(--sb-surface);
  color: var(--sb-text-main);
  outline: none;
  transition: none;
  appearance: none;
}

.sb-auth-input:focus,
.sb-auth-select:focus {
  border-color: #00895a;
  box-shadow: 0 0 0 3px rgba(0, 137, 90, 0.12);
}

.sb-auth-input::placeholder {
  color: var(--sb-text-muted);
  opacity: 0.78;
}

.sb-auth-alert {
  background: #fff5f5;
  border: 1px solid #fecaca;
  color: #b91c1c;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 13px;
  margin-bottom: 18px;
}

.sb-auth-field-error {
  color: #b91c1c;
  font-size: 12px;
  margin-top: 4px;
}

.sb-auth-helper {
  color: var(--sb-text-muted);
  font-size: 12px;
  margin-top: 4px;
}

.sb-btn-pill {
  background: var(--sb-primary);
  color: var(--sb-primary-contrast);
  padding: 11px 28px;
  border-radius: 9999px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: transform var(--sb-t-normal) var(--sb-spring);
}

.sb-btn-pill:hover:not(:disabled) {
  background: var(--sb-primary-hover);
}

.sb-auth-submit {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.sb-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: sb-spin 0.7s linear infinite;
  flex-shrink: 0;
}

@keyframes sb-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
