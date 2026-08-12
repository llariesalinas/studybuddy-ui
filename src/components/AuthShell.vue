<template>
  <div class="sb-auth-page">
    <a class="sb-auth-brand" :href="backTo" @click.prevent="router.push(backTo)">
      <span class="sb-brand-mark" aria-hidden="true">
        <img src="@/assets/logos/studybuddy-logo.svg" alt="" class="sb-brand-mark-logo" />
      </span>
      <span>StudyBuddy</span>
      <span class="sb-auth-back">{{ backLabel }}</span>
    </a>

    <div class="sb-auth-theme-toggle">
      <SbThemeToggle />
    </div>

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
import SbThemeToggle from '@/components/SbThemeToggle.vue'

defineProps({
  backTo: { type: String, default: '/' },
  backLabel: { type: String, default: '← Back to home' },
})

const router = useRouter()
</script>

<style scoped>
.sb-auth-page {
  --sb-parchment: var(--sb-bg);
  --sb-ink: var(--sb-text-main);
  --sb-muted: var(--sb-text-muted);
  --sb-auth-card-bg: var(--sb-card-bg);
  --sb-auth-card-border: var(--sb-card-border);
  --sb-green-tint: #edf7f3;
  --sb-green-border: #b8dece;

  min-height: 100vh;
  position: relative;
  background: transparent;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 16px 48px;
  font-family: var(--sb-font-base);
  box-sizing: border-box;
}

.sb-auth-theme-toggle {
  position: absolute;
  top: 24px;
  right: 24px;
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
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sb-brand-mark-logo {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.sb-auth-back {
  color: var(--sb-muted);
  font-weight: 400;
  font-size: 13px;
}

.sb-auth-card {
  background: var(--sb-auth-card-bg);
  border: 1px solid var(--sb-auth-card-border);
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

  .sb-auth-theme-toggle {
    top: 16px;
    right: 12px;
  }
}
</style>
