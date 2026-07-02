<template>
  <div class="sb-step-bar" :aria-label="`Step ${current} of ${total}`">
    <div class="sb-step-bar-labels">
      <span class="sb-step-label">Step {{ current }} of {{ total }}</span>
      <span class="sb-step-label sb-step-label--right">{{ Math.round((current / total) * 100) }}%</span>
    </div>
    <div class="sb-step-track">
      <div class="sb-step-fill" :style="{ transform: `scaleX(${current / total})` }"></div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  current: { type: Number, required: true },
  total:   { type: Number, required: true },
})
</script>

<style scoped>
.sb-step-bar { width: 100%; }

.sb-step-bar-labels {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.sb-step-label {
  font-size: 12px;
  font-weight: 700;
  color: var(--sb-text-secondary, #475569);
}

.sb-step-track {
  height: 6px;
  background: rgba(0, 137, 90, 0.15);
  border-radius: 999px;
  overflow: hidden;
}

.sb-step-fill {
  width: 100%;
  height: 100%;
  background: var(--sb-primary);
  border-radius: 999px;
  transform-origin: left center;
  transition: transform var(--sb-t-normal) var(--sb-spring);
}
</style>
