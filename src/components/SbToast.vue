<template>
  <Teleport to="body">
    <div class="sb-toast-stack">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toastStore.toasts"
          :key="toast.id"
          class="sb-toast"
          :class="`sb-toast--${toast.type}`"
          role="alert"
          aria-live="polite"
          @click="toastStore.dismiss(toast.id)"
        >
          <span class="sb-toast-dot"></span>
          <span class="sb-toast-message">{{ toast.message }}</span>
          <button
            v-if="toast.action"
            type="button"
            class="sb-toast-action"
            @click.stop="runAction(toast)"
          >
            {{ toast.action.label }}
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { useToastStore } from '@/stores/toast'
const toastStore = useToastStore()

const runAction = (toast) => {
  toastStore.dismiss(toast.id)
  toast.action?.handler?.()
}
</script>

<style scoped>
.sb-toast-stack {
  position: fixed;
  top: 20px;
  right: 24px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
}

.sb-toast {
  background: var(--sb-dark);
  color: #ffffff;
  border-radius: 12px;
  padding: 12px 18px;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.22);
  cursor: pointer;
  pointer-events: auto;
  max-width: 320px;
}

.sb-toast-message { flex: 1; }

.sb-toast-action {
  background: rgba(255, 255, 255, 0.16);
  border: none;
  color: inherit;
  border-radius: 999px;
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  flex-shrink: 0;
}

.sb-toast-action:hover { background: rgba(255, 255, 255, 0.26); }

.sb-toast--error   { background: #7f1d1d; }
.sb-toast--warning { background: #78350f; }

.sb-toast-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--sb-primary);
  flex-shrink: 0;
}
.sb-toast--error .sb-toast-dot   { background: #fca5a5; }
.sb-toast--warning .sb-toast-dot { background: #fcd34d; }

/* TransitionGroup hooks — sb-toast-in keyframe is defined globally in App.vue */
.toast-enter-active {
  animation: sb-toast-in var(--sb-t-normal) var(--sb-spring) both;
}
.toast-leave-active {
  transition: opacity var(--sb-t-quick) ease, transform var(--sb-t-quick) ease;
}
.toast-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
