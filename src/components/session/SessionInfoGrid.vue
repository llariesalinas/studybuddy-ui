<template>
  <section class="session-card session-info-card">
    <h4>{{ title }}</h4>
    <div class="session-info-stream">
      <article
        v-for="item in items"
        :key="item.label"
        class="session-info-row"
      >
        <span class="session-info-label">{{ item.label }}</span>
        <div class="session-info-content">
          <strong>{{ item.value || 'N/A' }}</strong>
          <p v-if="item.hint">{{ item.hint }}</p>
          <div v-if="item.chips?.length" class="session-info-chips">
            <span
              v-for="chip in item.chips"
              :key="`${item.label}-${chip}`"
              class="session-info-chip"
            >
              {{ chip }}
            </span>
          </div>
        </div>
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
/* Surface styling comes from the glass-segment class passed in by the parent view. */
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

.session-info-stream {
  border-top: 1px solid var(--sb-card-border);
}

.session-info-row {
  display: grid;
  grid-template-columns: 120px minmax(0, 1fr);
  gap: 16px;
  align-items: start;
  min-width: 0;
  border-bottom: 1px solid var(--sb-card-border);
  padding: 18px 0;
  transition:
    background-color var(--sb-t-normal) var(--sb-spring),
    transform var(--sb-t-normal) var(--sb-spring);
}

.session-info-row:last-child {
  border-bottom: 0;
}

.session-info-row:hover {
  transform: translateX(3px);
}

.session-info-label {
  color: var(--sb-text-subtle);
  font-size: 0.68rem;
  font-weight: 850;
  letter-spacing: 0;
  text-transform: uppercase;
}

.session-info-content {
  display: grid;
  gap: 6px;
  min-width: 0;
}

.session-info-content strong {
  display: block;
  overflow-wrap: anywhere;
  color: var(--sb-text-dark);
  font-size: 1rem;
  font-weight: 850;
}

.session-info-content p {
  margin: 0;
  color: var(--sb-text-muted);
  font-size: 0.8rem;
  line-height: 1.45;
}

.session-info-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.session-info-chip {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--sb-card-bg) 70%, transparent);
  border: 1px solid color-mix(in srgb, var(--sb-card-border) 84%, transparent);
  color: var(--sb-text-main);
  font-size: 0.74rem;
  font-weight: 700;
}

@media (max-width: 575px) {
  .session-info-card {
    padding: 18px;
  }

  .session-info-row {
    grid-template-columns: 1fr;
    gap: 8px;
    padding: 16px 0;
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
