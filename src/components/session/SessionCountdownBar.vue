<template>
  <section
    v-if="presentation?.hasOrbit"
    class="session-countdown"
    :class="`is-${presentation.state}`"
    role="status"
    aria-live="polite"
  >
    <div class="session-countdown-copy">
      <span class="session-countdown-pill">
        <span></span>
        {{ presentation.stateLabel }}
      </span>
      <h4>{{ presentation.primaryText }}</h4>
      <p>{{ presentation.timerText }}</p>
    </div>

    <div class="session-countdown-map">
      <div
        class="session-countdown-orbit"
        :style="{ '--orbit-progress': `${presentation.progress}%` }"
        :aria-label="`${presentation.zoneLabel}, ${presentation.timerText}`"
      >
        <span
          v-for="zone in 4"
          :key="zone"
          class="session-countdown-zone"
          :class="{ active: presentation.zone >= zone }"
        >
          <i>{{ zone }}</i>
        </span>
        <span class="session-countdown-fill"></span>
        <span class="session-countdown-bead"></span>
      </div>
      <div class="session-countdown-meta">
        <span>Window progress</span>
        <strong>{{ presentation.progress }}%</strong>
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  presentation: {
    type: Object,
    required: true,
  },
})
</script>

<style scoped>
.session-countdown {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 0.56fr) minmax(280px, 0.44fr);
  gap: 24px;
  overflow: hidden;
  padding: 24px 28px;
  border-top: 1px solid rgba(255, 255, 255, 0.14);
  background:
    radial-gradient(circle at 12% 18%, rgba(51, 213, 166, 0.32), transparent 32%),
    radial-gradient(circle at 88% 86%, rgba(255, 204, 111, 0.2), transparent 32%),
    linear-gradient(135deg, #061814, #10342c 58%, #1b2621);
  color: #ffffff;
}

.session-countdown::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.08), transparent),
    repeating-linear-gradient(
      90deg,
      rgba(255, 255, 255, 0.06) 0,
      rgba(255, 255, 255, 0.06) 1px,
      transparent 1px,
      transparent 80px
    );
  opacity: 0.45;
  pointer-events: none;
}

.session-countdown-copy,
.session-countdown-map {
  position: relative;
  z-index: 1;
  min-width: 0;
}

.session-countdown-pill {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  width: max-content;
  max-width: 100%;
  margin-bottom: 12px;
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  color: #dbfff3;
  padding: 5px 11px;
  font-size: 12px;
  font-weight: 800;
}

.session-countdown-pill span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #52efbf;
  box-shadow: 0 0 14px rgba(82, 239, 191, 0.82);
}

.session-countdown h4 {
  margin: 0;
  color: #ffffff;
  font-size: 1.08rem;
  font-weight: 900;
  line-height: 1.25;
  letter-spacing: 0;
}

.session-countdown p {
  margin: 6px 0 0;
  color: rgba(255, 255, 255, 0.76);
  font-size: 0.88rem;
}

.session-countdown-map {
  display: grid;
  align-content: center;
  gap: 12px;
}

.session-countdown-orbit {
  position: relative;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
  min-height: 44px;
  align-items: center;
}

.session-countdown-zone {
  position: relative;
  height: 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.14);
}

.session-countdown-zone.active {
  background: rgba(109, 255, 214, 0.46);
}

.session-countdown-zone i {
  position: absolute;
  top: 16px;
  left: 50%;
  color: rgba(255, 255, 255, 0.56);
  font-size: 10px;
  font-style: normal;
  font-weight: 800;
  transform: translateX(-50%);
}

.session-countdown-fill {
  position: absolute;
  left: 0;
  top: 50%;
  width: var(--orbit-progress);
  max-width: 100%;
  height: 3px;
  border-radius: 999px;
  background: linear-gradient(90deg, #55efc2, #f8d27a);
  transform: translateY(-50%);
}

.session-countdown-bead {
  position: absolute;
  left: var(--orbit-progress);
  top: 50%;
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  background: #fbfffd;
  box-shadow:
    0 0 0 7px rgba(85, 239, 194, 0.17),
    0 0 22px rgba(248, 210, 122, 0.58);
  transform: translate(-50%, -50%);
}

.session-countdown-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: rgba(255, 255, 255, 0.66);
  font-size: 0.78rem;
}

.session-countdown-meta strong {
  color: #ffffff;
  font-size: 0.86rem;
}

@media (max-width: 760px) {
  .session-countdown {
    grid-template-columns: 1fr;
    gap: 18px;
    padding: 22px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .session-countdown,
  .session-countdown::before {
    transition: none;
  }
}
</style>
