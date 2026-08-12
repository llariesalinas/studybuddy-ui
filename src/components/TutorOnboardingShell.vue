<template>
  <div class="onboarding-page">
    <nav class="navbar sb-surface py-3">
      <div class="container d-flex justify-content-between align-items-center">
        <span class="navbar-brand fw-bold fs-4 sb-text">StudyBuddy</span>
        <SbThemeToggle />
      </div>
    </nav>

    <main class="container py-5">
      <div class="row justify-content-center">
        <div class="col-lg-9">
          <div class="onboarding-shell">
            <aside class="onboarding-rail">
              <div
                v-for="(step, index) in STEPS"
                :key="step"
                class="rail-step"
                :class="{
                  'rail-step-active': index === currentStep - 1,
                  'rail-step-done': index < currentStep - 1,
                }"
              >
                <span class="rail-num">{{ index < currentStep - 1 ? '' : index + 1 }}</span>
                <span>{{ step }}</span>
              </div>
            </aside>

            <section class="onboarding-main sb-text">
              <slot />
            </section>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import SbThemeToggle from '@/components/SbThemeToggle.vue'

// This shell is specific to the tutor onboarding wizard (Preferences -> Subjects -> Verify),
// hence the fixed step labels rather than a generic `steps` prop -- see
// docs/plans/2026-08-12-tutor-onboarding-modality-rate-redesign.md for why it exists: the rail
// chrome was previously copy-pasted between TutorSubjectSetup.vue and TutorVerificationSetup.vue,
// and a third copy would have landed in TutorPreferenceSetup.vue.
const STEPS = ['Preferences', 'Subjects', 'Verify']

defineProps({
  // 1-indexed: 1 = Preferences, 2 = Subjects, 3 = Verify.
  currentStep: {
    type: Number,
    required: true,
  },
})
</script>

<style scoped>
.onboarding-page {
  min-height: 100vh;
  background: var(--sb-bg);
}

.onboarding-shell {
  display: flex;
  background: var(--sb-card-bg);
  border: 1px solid var(--sb-card-border);
  border-radius: 18px;
  box-shadow: 0 6px 20px var(--sb-shadow-soft);
  overflow: hidden;
}

.onboarding-rail {
  width: 160px;
  flex-shrink: 0;
  background: color-mix(in srgb, var(--sb-primary) 8%, var(--sb-card-bg));
  border-right: 1px solid var(--sb-card-border);
  padding: 28px 16px;
}

.rail-step {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 24px;
  font-size: 13px;
  color: var(--sb-text-muted);
}

.rail-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 1.5px solid var(--sb-card-border);
  background: var(--sb-card-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 11px;
  flex-shrink: 0;
}

.rail-step-active {
  color: var(--sb-text-main);
  font-weight: 700;
}

.rail-step-active .rail-num,
.rail-step-done .rail-num {
  background: var(--sb-primary);
  border-color: var(--sb-primary);
  color: var(--sb-primary-contrast);
}

.rail-step-done .rail-num::after {
  content: '\2713';
  color: var(--sb-primary-contrast);
  font-size: 12px;
}

.onboarding-main {
  flex: 1;
  min-width: 0;
  padding: 32px 32px 30px;
}

.onboarding-main :deep(h3) {
  font-weight: 800;
  margin: 0 0 0.2rem;
  font-size: 1.15rem;
}

.onboarding-main :deep(.muted) {
  color: var(--sb-text-muted);
  margin: 0 0 1.25rem;
  font-size: 0.92rem;
}

@media (max-width: 640px) {
  .onboarding-shell {
    flex-direction: column;
  }

  .onboarding-rail {
    width: 100%;
    display: flex;
    justify-content: space-between;
    padding: 16px 18px;
    border-right: 0;
    border-bottom: 1px solid var(--sb-card-border);
  }

  .rail-step {
    margin-bottom: 0;
    flex-direction: column;
    gap: 4px;
    font-size: 11px;
  }

  .onboarding-main {
    padding: 26px 20px;
  }
}
</style>
