<template>
  <section class="session-card session-info-card">
    <h4>{{ title }}</h4>
    <div class="session-info-grid">
      <article
        v-for="(item, index) in items"
        :key="item.label"
        class="session-info-tile"
        :class="`session-info-tile-${index % 6}`"
      >
        <span>{{ item.label }}</span>
        <strong>{{ item.value || 'N/A' }}</strong>
      </article>
    </div>
  </section>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: 'Session information',
  },
  items: {
    type: Array,
    default: () => [],
  },
})
</script>

<style scoped>
.session-card {
  border: 1px solid color-mix(in srgb, var(--sb-card-border) 70%, transparent);
  border-radius: 18px;
  background: color-mix(in srgb, var(--sb-card-bg) 88%, transparent);
  box-shadow: 0 14px 36px var(--sb-shadow-soft);
  backdrop-filter: blur(10px);
  transition:
    transform var(--sb-t-normal) var(--sb-spring),
    box-shadow var(--sb-t-normal) var(--sb-spring),
    border-color var(--sb-t-normal) var(--sb-spring),
    background-color var(--sb-t-normal) var(--sb-spring);
}

.session-card:hover {
  border-color: color-mix(in srgb, var(--sb-primary) 22%, var(--sb-card-border));
  background: color-mix(in srgb, var(--sb-card-bg) 94%, transparent);
  box-shadow: 0 22px 54px color-mix(in srgb, var(--sb-shadow-soft) 74%, rgba(15, 23, 42, 0.12));
  transform: translateY(-3px);
}

.session-info-card {
  padding: 24px;
}

.session-info-card h4 {
  margin: 0 0 24px;
  color: var(--sb-text-main);
  font-size: 1.15rem;
  font-weight: 800;
  letter-spacing: 0;
}

.session-info-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 22px;
}

.session-info-tile {
  position: relative;
  display: grid;
  align-content: center;
  min-height: 48px;
  min-width: 0;
  overflow: hidden;
  border-radius: 13px;
  background: transparent;
  padding: 4px 11px 4px 20px;
  transition:
    background-color var(--sb-t-normal) var(--sb-spring),
    transform var(--sb-t-normal) var(--sb-spring);
}

.session-info-tile:hover {
  background: color-mix(in srgb, var(--sb-card-bg) 56%, transparent);
  transform: translateX(3px);
}

.session-info-tile::before {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  width: 4px;
  border-radius: 999px;
  content: '';
}

.session-info-tile-0::before {
  background: var(--sb-primary);
}

.session-info-tile-1::before {
  background: var(--sb-pop-yellow);
}

.session-info-tile-2::before {
  background: var(--sb-pop-pink);
}

.session-info-tile-3::before {
  background: var(--sb-pop-orange);
}

.session-info-tile-4::before {
  background: var(--sb-aurora-violet);
}

.session-info-tile-5::before {
  background: var(--sb-primary-mid);
}

.session-info-tile span {
  display: block;
  margin-bottom: 4px;
  color: var(--sb-text-subtle);
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}

.session-info-tile strong {
  display: block;
  overflow-wrap: anywhere;
  color: var(--sb-text-dark);
  font-size: 0.98rem;
  font-weight: 800;
}

@media (max-width: 575px) {
  .session-info-card {
    padding: 18px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .session-card,
  .session-info-tile {
    transition: none;
  }

  .session-card:hover,
  .session-info-tile:hover {
    transform: none;
  }
}
</style>
