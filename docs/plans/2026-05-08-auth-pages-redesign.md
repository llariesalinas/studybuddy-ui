# Auth Pages Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign Login.vue and Register.vue to match the LandingPage design system — parchment background, white auth card, green-only accents, scoped CSS, no Bootstrap layout/form classes.

**Architecture:** Extract a shared `AuthShell.vue` component that owns the parchment page, brand/back link, and white card chrome. Login and Register slot their form content into it. All styles are scoped per file; tokens are re-declared locally (same pattern as LandingPage.vue).

**Tech Stack:** Vue 3 Composition API, Vue Router, Pinia, Bootstrap Icons (glyphs only — no Bootstrap layout classes), scoped CSS with sb-* tokens.

---

## File Map

| Action | File | Responsibility |
|--------|------|----------------|
| Create | `src/components/AuthShell.vue` | Parchment page, brand/back link, white card, named slots for icon / title / subtitle / default |
| Modify | `src/views/Login.vue` | Uses AuthShell; sb-auth-* form classes; preserves login logic + role redirect |
| Modify | `src/views/Register.vue` | Uses AuthShell; sb-auth-* form classes; preserves all registration logic |

---

## Task 1: Create AuthShell.vue

**Files:**
- Create: `src/components/AuthShell.vue`

- [ ] **Step 1: Create the file with this exact content**

```vue
<template>
  <div class="sb-auth-page">
    <a class="sb-auth-brand" href="/" @click.prevent="router.push('/')">
      <span class="sb-brand-mark" aria-hidden="true">S</span>
      <span>StudyBuddy</span>
      <span class="sb-auth-back">← Back to home</span>
    </a>

    <div class="sb-auth-card">
      <div class="sb-auth-icon-badge">
        <slot name="icon" />
      </div>
      <h2 class="sb-auth-title">
        <slot name="title" />
      </h2>
      <p class="sb-auth-subtitle">
        <slot name="subtitle" />
      </p>
      <slot />
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<style scoped>
.sb-auth-page {
  --sb-primary: #00895a;
  --sb-primary-hover: #00704a;
  --sb-parchment: #f5f5f7;
  --sb-ink: #1d1d1f;
  --sb-muted: #6e6e73;
  --sb-green-tint: #edf7f3;
  --sb-green-border: #b8dece;

  min-height: 100vh;
  background: var(--sb-parchment);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 16px 48px;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  box-sizing: border-box;
}

.sb-auth-page *,
.sb-auth-page *::before,
.sb-auth-page *::after {
  box-sizing: border-box;
}

.sb-auth-brand {
  align-self: flex-start;
  display: inline-flex;
  align-items: center;
  gap: 9px;
  color: var(--sb-ink);
  font-size: 14px;
  font-weight: 700;
  text-decoration: none;
  margin-bottom: 32px;
}

.sb-auth-brand:hover .sb-auth-back {
  text-decoration: underline;
}

.sb-brand-mark {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--sb-primary);
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  flex-shrink: 0;
}

.sb-auth-back {
  color: var(--sb-muted);
  font-weight: 400;
  font-size: 13px;
}

.sb-auth-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 18px;
  padding: 36px 32px;
  width: 100%;
  max-width: 440px;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.06);
}

.sb-auth-icon-badge {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: var(--sb-green-tint);
  border: 1px solid var(--sb-green-border);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  font-size: 20px;
  color: var(--sb-primary);
}

.sb-auth-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--sb-ink);
  margin: 0 0 6px;
}

.sb-auth-subtitle {
  font-size: 14px;
  color: var(--sb-muted);
  margin: 0 0 24px;
}

@media (max-width: 768px) {
  .sb-auth-page {
    padding: 16px 12px 32px;
  }

  .sb-auth-card {
    padding: 24px 20px;
  }
}
</style>
```

- [ ] **Step 2: Verify the file was created**

```bash
ls src/components/AuthShell.vue
```

Expected: file exists, no error.

- [ ] **Step 3: Lint the new file**

```bash
npx oxlint src/components/AuthShell.vue
npx eslint src/components/AuthShell.vue
```

Expected: no errors.

- [ ] **Step 4: Commit**

```bash
git add src/components/AuthShell.vue
git commit -m "feat: add AuthShell shared auth page component"
```

---

## Task 2: Rewrite Login.vue

**Files:**
- Modify: `src/views/Login.vue`

The goal is to replace the Bootstrap template and add scoped sb-auth-* CSS. The `<script setup>` logic stays — only the template and styles change. Remove the `console.log` statements while here.

- [ ] **Step 1: Replace the full contents of `src/views/Login.vue`**

```vue
<template>
  <AuthShell>
    <template #icon>
      <i class="bi bi-box-arrow-in-right"></i>
    </template>
    <template #title>Welcome Back</template>
    <template #subtitle>Log in to your StudyBuddy account</template>

    <div v-if="loginError" class="sb-auth-alert">{{ loginError }}</div>

    <form @submit.prevent="handleLogin">
      <div class="sb-auth-field">
        <label class="sb-auth-label">University Email</label>
        <input
          type="email"
          v-model="email"
          class="sb-auth-input"
          placeholder="you@university.edu"
          required
        />
      </div>

      <div class="sb-auth-field">
        <div class="sb-auth-label-row">
          <label class="sb-auth-label">Password</label>
          <a href="#" class="sb-auth-link sb-auth-link-sm">Forgot?</a>
        </div>
        <input
          type="password"
          v-model="password"
          class="sb-auth-input"
          placeholder="••••••••"
          required
        />
      </div>

      <button type="submit" class="sb-btn-pill sb-auth-submit" :disabled="isSubmitting">
        <span v-if="isSubmitting" class="sb-spinner" aria-hidden="true"></span>
        {{ isSubmitting ? 'Signing In...' : 'Sign In' }}
      </button>
    </form>

    <p class="sb-auth-footer-text">
      No account?
      <router-link to="/register" class="sb-auth-link">Create one</router-link>
    </p>
  </AuthShell>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AuthShell from '@/components/AuthShell.vue'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const isSubmitting = ref(false)
const loginError = ref('')

const handleLogin = async () => {
  isSubmitting.value = true
  loginError.value = ''

  try {
    const role = await authStore.login({ email: email.value, password: password.value })
    const normalizedRole = role?.toLowerCase()

    if (normalizedRole === 'tutor') router.push('/tch-dashboard')
    else if (normalizedRole === 'tutee') router.push('/dashboard')
    else router.push('/')
  } catch (error) {
    loginError.value =
      error.response?.data?.error || 'Login failed. Please check your credentials.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.sb-auth-field {
  margin-bottom: 16px;
}

.sb-auth-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 6px;
}

.sb-auth-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.sb-auth-label-row .sb-auth-label {
  margin-bottom: 0;
}

.sb-auth-input {
  width: 100%;
  padding: 10px 14px;
  font-size: 14px;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  background: #fff;
  color: #1d1d1f;
  outline: none;
  transition:
    border-color 0.15s ease,
    box-shadow 0.15s ease;
}

.sb-auth-input:focus {
  border-color: #00895a;
  box-shadow: 0 0 0 3px rgba(0, 137, 90, 0.12);
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

.sb-btn-pill {
  background: #00895a;
  color: #fff;
  padding: 11px 28px;
  border-radius: 9999px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition:
    background 0.15s ease,
    transform 0.15s ease;
}

.sb-btn-pill:hover:not(:disabled) {
  background: #00704a;
}

.sb-btn-pill:active:not(:disabled) {
  transform: scale(0.95);
}

.sb-btn-pill:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.sb-auth-submit {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  margin-bottom: 20px;
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

.sb-auth-link {
  color: #00895a;
  font-weight: 600;
  text-decoration: none;
}

.sb-auth-link:hover {
  text-decoration: underline;
}

.sb-auth-link-sm {
  font-size: 13px;
  font-weight: 500;
}

.sb-auth-footer-text {
  text-align: center;
  font-size: 13px;
  color: #6e6e73;
  margin: 0;
}
</style>
```

- [ ] **Step 2: Lint**

```bash
npx oxlint src/views/Login.vue
npx eslint src/views/Login.vue
```

Expected: no errors.

- [ ] **Step 3: Manually verify in browser**

Run `npm run dev`, go to `http://localhost:5173/login` and check:
- Parchment background is visible
- "← Back to home" link appears top-left
- Clicking it routes to `/`
- White card is centered with green icon badge, "Welcome Back" title
- Form fields have green focus ring
- Submitting with wrong credentials shows red alert block
- Submitting correctly routes tutor → `/tch-dashboard`, tutee → `/dashboard`
- On mobile (resize to <768px): card fills width, brand link stays visible

- [ ] **Step 4: Commit**

```bash
git add src/views/Login.vue
git commit -m "feat: redesign Login.vue with AuthShell and sb-auth styles"
```

---

## Task 3: Rewrite Register.vue

**Files:**
- Modify: `src/views/Register.vue`

Same approach as Login — replace template and styles, preserve all script logic unchanged.

- [ ] **Step 1: Replace the full contents of `src/views/Register.vue`**

```vue
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
          class="sb-auth-input"
          placeholder="Juan"
          required
        />
      </div>

      <div class="sb-auth-field">
        <label class="sb-auth-label">Middle Name</label>
        <input
          type="text"
          v-model="store.newUserMname"
          class="sb-auth-input"
          placeholder="Optional"
        />
      </div>

      <div class="sb-auth-field">
        <label class="sb-auth-label">Last Name</label>
        <input
          type="text"
          v-model="store.newUserLname"
          class="sb-auth-input"
          placeholder="Dela Cruz"
          required
        />
      </div>

      <div class="sb-auth-field">
        <label class="sb-auth-label">University Email</label>
        <input
          type="email"
          v-model="store.newUserEmail"
          class="sb-auth-input"
          placeholder="you@university.edu"
          required
        />
        <div v-if="emailError" class="sb-auth-field-error">{{ emailError }}</div>
      </div>

      <div class="sb-auth-field">
        <label class="sb-auth-label">Institution</label>
        <select v-model="store.selectedInstitutionId" class="sb-auth-select" required>
          <option value="" disabled>Select your institution</option>
          <option
            v-for="institution in institutions"
            :key="institution.id"
            :value="String(institution.id)"
          >
            {{ institution.institution_name }} ({{ institution.school_email_domain }})
          </option>
        </select>
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
          class="sb-auth-input"
          placeholder="••••••••"
          required
        />
      </div>

      <div class="sb-auth-field">
        <label class="sb-auth-label">I want to</label>
        <select v-model="store.newUserType" class="sb-auth-select" required>
          <option value="" disabled selected>Select your role</option>
          <option value="Tutee">Find a Tutor (Student)</option>
          <option value="Tutor">Become a Tutor</option>
        </select>
      </div>

      <button type="submit" class="sb-btn-pill sb-auth-submit" :disabled="isSubmitting">
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
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api/api'
import AuthShell from '@/components/AuthShell.vue'

const router = useRouter()
const store = useRegistrationInfoStore()
const authStore = useAuthStore()

const isSubmitting = ref(false)
const institutions = ref([])

const generalError = ref('')
const emailError = ref('')
const institutionError = ref('')

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
    const response = await api.get('partner-institutions/')
    institutions.value = response.data
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
    !store.newUserPassword ||
    !store.selectedInstitutionId
  ) {
    generalError.value = 'Please fill in all required fields.'
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

    await authStore.login({
      email: store.newUserEmail,
      password: store.newUserPassword,
    })

    if (role === 'Tutor') router.push('/tutor-setup')
    else router.push('/preferencesetup')
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
  color: #1d1d1f;
  margin-bottom: 6px;
}

.sb-auth-input,
.sb-auth-select {
  width: 100%;
  padding: 10px 14px;
  font-size: 14px;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  background: #fff;
  color: #1d1d1f;
  outline: none;
  transition:
    border-color 0.15s ease,
    box-shadow 0.15s ease;
  appearance: none;
}

.sb-auth-input:focus,
.sb-auth-select:focus {
  border-color: #00895a;
  box-shadow: 0 0 0 3px rgba(0, 137, 90, 0.12);
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
  color: #6e6e73;
  font-size: 12px;
  margin-top: 4px;
}

.sb-btn-pill {
  background: #00895a;
  color: #fff;
  padding: 11px 28px;
  border-radius: 9999px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition:
    background 0.15s ease,
    transform 0.15s ease;
}

.sb-btn-pill:hover:not(:disabled) {
  background: #00704a;
}

.sb-btn-pill:active:not(:disabled) {
  transform: scale(0.95);
}

.sb-btn-pill:disabled {
  opacity: 0.65;
  cursor: not-allowed;
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
```

- [ ] **Step 2: Lint**

```bash
npx oxlint src/views/Register.vue
npx eslint src/views/Register.vue
```

Expected: no errors.

- [ ] **Step 3: Manually verify in browser**

Go to `http://localhost:5173/register` and check:
- Parchment background visible
- "← Back to home" link routes to `/`
- White card is centered, green book icon badge, "Create Account" title
- Institutions dropdown loads correctly from the backend
- Allowed email domain helper text appears when an institution is selected
- Email/institution field-level errors appear in red below the field (not in a top-level alert)
- Submitting with missing fields shows top-level general error
- Successful registration routes Tutor → `/tutor-setup`, Tutee → `/preferencesetup`
- On mobile: card fills width, all fields accessible

- [ ] **Step 4: Commit**

```bash
git add src/views/Register.vue
git commit -m "feat: redesign Register.vue with AuthShell and sb-auth styles"
```

---

## Task 4: Final Build Verification

- [ ] **Step 1: Run full lint pass on all three files**

```bash
npx oxlint src/components/AuthShell.vue src/views/Login.vue src/views/Register.vue
npx eslint src/components/AuthShell.vue src/views/Login.vue src/views/Register.vue
npx prettier --check src/components/AuthShell.vue src/views/Login.vue src/views/Register.vue
```

Expected: no errors or warnings.

- [ ] **Step 2: Production build**

```bash
npm run build
```

Expected: build completes with no errors. Warnings about chunk size are fine.

- [ ] **Step 3: Commit if prettier auto-fixed anything**

Only needed if prettier `--check` reported diffs and you ran `--write` to fix:

```bash
git add src/components/AuthShell.vue src/views/Login.vue src/views/Register.vue
git commit -m "style: prettier format auth files"
```
