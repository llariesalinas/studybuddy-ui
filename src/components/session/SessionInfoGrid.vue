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
  border: 0;
  border-radius: 0;
  background: transparent;
}

.session-card:hover {
  transform: none;
}

.session-info-card {
  padding: 28px;
}

.session-info-card h4 {
  margin: 0 0 20px;
  color: var(--sb-text-main);
  font-size: 1.08rem;
  font-weight: 850;
  letter-spacing: 0;
}

.session-info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  border-top: 1px solid var(--sb-card-border);
}

.session-info-tile {
  position: relative;
  display: grid;
  align-content: center;
  min-height: 92px;
  min-width: 0;
  overflow: hidden;
  border-right: 1px solid var(--sb-card-border);
  border-bottom: 1px solid var(--sb-card-border);
  border-radius: 0;
  background: transparent;
  padding: 18px 18px 18px 22px;
  transition:
    background-color var(--sb-t-normal) var(--sb-spring),
    transform var(--sb-t-normal) var(--sb-spring);
}

.session-info-tile:nth-child(2n) {
  border-right: 0;
}

.session-info-tile:nth-last-child(-n + 2) {
  border-bottom: 0;
}

.session-info-tile:hover {
  background: color-mix(in srgb, var(--sb-primary) 5%, transparent);
  transform: translateX(3px);
}

.session-info-tile::before {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  width: 4px;
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
  font-weight: 850;
  letter-spacing: 0;
  text-transform: uppercase;
}

.session-info-tile strong {
  display: block;
  overflow-wrap: anywhere;
  color: var(--sb-text-dark);
  font-size: 1rem;
  font-weight: 850;
}

@media (max-width: 575px) {
  .session-info-card {
    padding: 18px;
  }

  .session-info-grid {
    grid-template-columns: 1fr;
  }

  .session-info-tile,
  .session-info-tile:nth-child(2n),
  .session-info-tile:nth-last-child(-n + 2) {
    min-height: 76px;
    border-right: 0;
    border-bottom: 1px solid var(--sb-card-border);
  }

  .session-info-tile:last-child {
    border-bottom: 0;
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
