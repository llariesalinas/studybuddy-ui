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
  width: 76px;
  height: 38px;
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
  width: 76px;
  height: 38px;
  overflow: hidden;
  border: 1px solid #7dbcea;
  border-radius: 999px;
  background:
    radial-gradient(circle at 22% 22%, rgba(255, 255, 255, 0.85) 0 6px, transparent 7px),
    linear-gradient(180deg, #72c7ff 0%, #b8e6ff 100%);
  box-shadow:
    inset 0 1px 3px rgba(255, 255, 255, 0.7),
    inset 0 -8px 14px rgba(255, 255, 255, 0.22),
    0 8px 20px rgba(20, 92, 145, 0.16);
  transition:
    border-color 0.26s ease,
    background 0.26s ease,
    box-shadow 0.26s ease;
}

.sb-theme-toggle__thumb {
  position: absolute;
  top: 4px;
  left: 4px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #ffd75e;
  box-shadow:
    0 0 0 5px rgba(255, 222, 110, 0.24),
    0 3px 8px rgba(166, 106, 18, 0.24);
  transition:
    transform 0.28s cubic-bezier(0.2, 0.8, 0.2, 1),
    background 0.26s ease,
    box-shadow 0.26s ease;
}

.sb-theme-toggle__sun,
.sb-theme-toggle__moon {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  transition:
    opacity 0.22s ease,
    transform 0.28s ease;
}

.sb-theme-toggle__sun {
  opacity: 1;
  background:
    radial-gradient(circle, #fff4a8 0 16%, transparent 17%),
    conic-gradient(
      from 0deg,
      transparent 0deg 18deg,
      rgba(255, 249, 186, 0.9) 18deg 30deg,
      transparent 30deg 62deg,
      rgba(255, 249, 186, 0.9) 62deg 74deg,
      transparent 74deg 106deg,
      rgba(255, 249, 186, 0.9) 106deg 118deg,
      transparent 118deg 150deg,
      rgba(255, 249, 186, 0.9) 150deg 162deg,
      transparent 162deg 194deg,
      rgba(255, 249, 186, 0.9) 194deg 206deg,
      transparent 206deg 238deg,
      rgba(255, 249, 186, 0.9) 238deg 250deg,
      transparent 250deg 282deg,
      rgba(255, 249, 186, 0.9) 282deg 294deg,
      transparent 294deg 326deg,
      rgba(255, 249, 186, 0.9) 326deg 338deg,
      transparent 338deg 360deg
    );
}

.sb-theme-toggle__moon {
  opacity: 0;
  transform: rotate(-18deg) scale(0.7);
  background: #f6f0ca;
}

.sb-theme-toggle__moon::after {
  position: absolute;
  top: 1px;
  left: 9px;
  width: 25px;
  height: 25px;
  border-radius: 50%;
  background: #142847;
  content: '';
}

.sb-theme-toggle__cloud {
  position: absolute;
  right: 9px;
  bottom: 6px;
  width: 30px;
  height: 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 14px 3px 0 rgba(255, 255, 255, 0.48);
  transition:
    opacity 0.22s ease,
    transform 0.28s ease;
}

.sb-theme-toggle__cloud-puff {
  position: absolute;
  bottom: 5px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.94);
}

.sb-theme-toggle__cloud-puff--one {
  left: 4px;
  width: 13px;
  height: 13px;
}

.sb-theme-toggle__cloud-puff--two {
  left: 13px;
  width: 16px;
  height: 16px;
}

.sb-theme-toggle__cloud-puff--three {
  right: -4px;
  width: 11px;
  height: 11px;
}

.sb-theme-toggle__stars {
  position: absolute;
  inset: 0;
  opacity: 0;
  transform: translateY(4px);
  transition:
    opacity 0.22s ease,
    transform 0.28s ease;
}

.sb-theme-toggle__star {
  position: absolute;
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: #fff8c6;
  box-shadow: 0 0 6px rgba(255, 248, 198, 0.8);
}

.sb-theme-toggle__star--one {
  top: 9px;
  left: 14px;
}

.sb-theme-toggle__star--two {
  top: 20px;
  left: 25px;
  width: 2px;
  height: 2px;
}

.sb-theme-toggle__star--three {
  top: 12px;
  right: 18px;
  width: 2px;
  height: 2px;
}

.sb-theme-toggle__input:checked + .sb-theme-toggle__track {
  border-color: #213b65;
  background:
    radial-gradient(circle at 18% 28%, rgba(255, 255, 255, 0.12) 0 2px, transparent 3px),
    linear-gradient(180deg, #172b50 0%, #0c1730 100%);
  box-shadow:
    inset 0 1px 3px rgba(255, 255, 255, 0.14),
    inset 0 -8px 14px rgba(0, 0, 0, 0.18),
    0 8px 20px rgba(6, 18, 38, 0.22);
}

.sb-theme-toggle__input:checked + .sb-theme-toggle__track .sb-theme-toggle__thumb {
  transform: translateX(38px);
  background: #f6f0ca;
  box-shadow:
    0 0 0 5px rgba(246, 240, 202, 0.13),
    0 3px 8px rgba(0, 0, 0, 0.28);
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
  transform: translateX(38px) scale(0.94);
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
