<template>
  <label class="sb-theme-toggle" aria-label="Toggle light/dark theme">
    <input
      type="checkbox"
      class="sb-theme-toggle__input"
      :checked="themeStore.theme === 'dark'"
      @change="themeStore.toggleTheme()"
    />

    <span class="sb-theme-toggle__track" aria-hidden="true">
      <span class="sb-theme-toggle__stars">
        <span class="sb-theme-toggle__star sb-theme-toggle__star--one"></span>
        <span class="sb-theme-toggle__star sb-theme-toggle__star--two"></span>
        <span class="sb-theme-toggle__star sb-theme-toggle__star--three"></span>
      </span>

      <span class="sb-theme-toggle__cloud">
        <span class="sb-theme-toggle__cloud-puff sb-theme-toggle__cloud-puff--one"></span>
        <span class="sb-theme-toggle__cloud-puff sb-theme-toggle__cloud-puff--two"></span>
        <span class="sb-theme-toggle__cloud-puff sb-theme-toggle__cloud-puff--three"></span>
      </span>

      <span class="sb-theme-toggle__thumb">
        <span class="sb-theme-toggle__sun"></span>
        <span class="sb-theme-toggle__moon"></span>
      </span>
    </span>

    <span class="sb-theme-toggle__label">
      {{ themeStore.theme === 'dark' ? 'Dark mode' : 'Light mode' }}
    </span>
  </label>
</template>

<script setup>
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()
</script>

<style scoped>
.sb-theme-toggle {
  position: relative;
  display: inline-grid;
  width: 58px;
  height: 30px;
  flex: 0 0 auto;
  place-items: center;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.sb-theme-toggle__input {
  position: absolute;
  inset: 0;
  z-index: 2;
  width: 100%;
  height: 100%;
  margin: 0;
  cursor: pointer;
  opacity: 0;
}

.sb-theme-toggle__track {
  position: relative;
  display: block;
  width: 58px;
  height: 30px;
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--sb-card-border) 72%, var(--sb-primary));
  border-radius: 999px;
  background:
    radial-gradient(circle at 22% 24%, rgba(255, 255, 255, 0.68) 0 4px, transparent 5px),
    linear-gradient(180deg, #cbe8eb 0%, #e8f5ef 100%);
  box-shadow:
    inset 0 1px 2px rgba(255, 255, 255, 0.62),
    0 4px 12px rgba(10, 25, 22, 0.1);
  transition: none;
}

.sb-theme-toggle__thumb {
  position: absolute;
  top: 4px;
  left: 4px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #f0c85a;
  box-shadow:
    0 0 0 3px rgba(240, 200, 90, 0.14),
    0 2px 6px rgba(88, 62, 15, 0.16);
  transition: transform var(--sb-t-normal) var(--sb-spring);
}

.sb-theme-toggle__sun,
.sb-theme-toggle__moon {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  transition:
    opacity var(--sb-t-normal) var(--sb-spring),
    transform var(--sb-t-normal) var(--sb-spring);
}

.sb-theme-toggle__sun {
  opacity: 1;
  background:
    radial-gradient(circle, #fff1a4 0 15%, transparent 16%),
    conic-gradient(
      from 0deg,
      transparent 0deg 18deg,
      rgba(255, 246, 170, 0.72) 18deg 30deg,
      transparent 30deg 62deg,
      rgba(255, 246, 170, 0.72) 62deg 74deg,
      transparent 74deg 106deg,
      rgba(255, 246, 170, 0.72) 106deg 118deg,
      transparent 118deg 150deg,
      rgba(255, 246, 170, 0.72) 150deg 162deg,
      transparent 162deg 194deg,
      rgba(255, 246, 170, 0.72) 194deg 206deg,
      transparent 206deg 238deg,
      rgba(255, 246, 170, 0.72) 238deg 250deg,
      transparent 250deg 282deg,
      rgba(255, 246, 170, 0.72) 282deg 294deg,
      transparent 294deg 326deg,
      rgba(255, 246, 170, 0.72) 326deg 338deg,
      transparent 338deg 360deg
    );
}

.sb-theme-toggle__moon {
  opacity: 0;
  transform: rotate(-18deg) scale(0.7);
  background: #d8e2dc;
}

.sb-theme-toggle__moon::after {
  position: absolute;
  top: 0;
  left: 7px;
  width: 19px;
  height: 22px;
  border-radius: 50%;
  background: #17251f;
  content: '';
}

.sb-theme-toggle__cloud {
  position: absolute;
  right: 7px;
  bottom: 5px;
  width: 22px;
  height: 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 10px 2px 0 rgba(255, 255, 255, 0.36);
  transition:
    opacity var(--sb-t-normal) var(--sb-spring),
    transform var(--sb-t-normal) var(--sb-spring);
}

.sb-theme-toggle__cloud-puff {
  position: absolute;
  bottom: 5px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.94);
}

.sb-theme-toggle__cloud-puff--one {
  left: 3px;
  width: 9px;
  height: 9px;
}

.sb-theme-toggle__cloud-puff--two {
  left: 9px;
  width: 12px;
  height: 12px;
}

.sb-theme-toggle__cloud-puff--three {
  right: -3px;
  width: 8px;
  height: 8px;
}

.sb-theme-toggle__stars {
  position: absolute;
  inset: 0;
  opacity: 0;
  transform: translateY(4px);
  transition:
    opacity var(--sb-t-normal) var(--sb-spring),
    transform var(--sb-t-normal) var(--sb-spring);
}

.sb-theme-toggle__star {
  position: absolute;
  width: 2px;
  height: 2px;
  border-radius: 50%;
  background: #e8f1ed;
  box-shadow: 0 0 4px rgba(232, 241, 237, 0.62);
}

.sb-theme-toggle__star--one {
  top: 8px;
  left: 12px;
}

.sb-theme-toggle__star--two {
  top: 18px;
  left: 20px;
  width: 2px;
  height: 2px;
}

.sb-theme-toggle__star--three {
  top: 10px;
  right: 14px;
  width: 2px;
  height: 2px;
}

.sb-theme-toggle__input:checked + .sb-theme-toggle__track {
  border-color: color-mix(in srgb, var(--sb-card-border) 76%, var(--sb-primary));
  background:
    radial-gradient(circle at 18% 28%, rgba(255, 255, 255, 0.08) 0 2px, transparent 3px),
    linear-gradient(180deg, #20372d 0%, #101d19 100%);
  box-shadow:
    inset 0 1px 2px rgba(255, 255, 255, 0.1),
    0 4px 12px rgba(6, 18, 16, 0.18);
}

.sb-theme-toggle__input:checked + .sb-theme-toggle__track .sb-theme-toggle__thumb {
  transform: translateX(28px);
  background: #d8e2dc;
  box-shadow:
    0 0 0 3px rgba(216, 226, 220, 0.1),
    0 2px 6px rgba(0, 0, 0, 0.2);
}

.sb-theme-toggle__input:checked + .sb-theme-toggle__track .sb-theme-toggle__sun {
  opacity: 0;
  transform: rotate(35deg) scale(0.65);
}

.sb-theme-toggle__input:checked + .sb-theme-toggle__track .sb-theme-toggle__moon {
  opacity: 1;
  transform: rotate(0deg) scale(1);
}

.sb-theme-toggle__input:checked + .sb-theme-toggle__track .sb-theme-toggle__cloud {
  opacity: 0;
  transform: translateX(12px) translateY(5px);
}

.sb-theme-toggle__input:checked + .sb-theme-toggle__track .sb-theme-toggle__stars {
  opacity: 1;
  transform: translateY(0);
}

.sb-theme-toggle__input:focus-visible + .sb-theme-toggle__track {
  outline: 3px solid rgba(76, 150, 255, 0.5);
  outline-offset: 3px;
}

.sb-theme-toggle__input:active + .sb-theme-toggle__track .sb-theme-toggle__thumb {
  transform: scale(0.94);
}

.sb-theme-toggle__input:checked:active + .sb-theme-toggle__track .sb-theme-toggle__thumb {
  transform: translateX(28px) scale(0.94);
}

.sb-theme-toggle__label {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  overflow: hidden;
  border: 0;
  clip: rect(0, 0, 0, 0);
  clip-path: inset(50%);
  white-space: nowrap;
}

@media (prefers-reduced-motion: reduce) {
  .sb-theme-toggle__track,
  .sb-theme-toggle__thumb,
  .sb-theme-toggle__sun,
  .sb-theme-toggle__moon,
  .sb-theme-toggle__cloud,
  .sb-theme-toggle__stars {
    transition-duration: 1ms;
    transition-timing-function: linear;
  }
}
</style>
