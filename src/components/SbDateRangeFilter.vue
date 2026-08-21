<template>
  <div class="sb-range-filter">
    <div class="sb-range-presets" :aria-label="ariaLabel" role="group">
      <button
        v-for="preset in presets"
        :key="preset.value"
        type="button"
        class="sb-range-preset"
        :class="{ active: modelValue === preset.value }"
        :aria-pressed="modelValue === preset.value"
        @click="$emit('update:modelValue', preset.value)"
      >
        {{ preset.label }}
      </button>
    </div>

    <div v-if="modelValue === customValue" class="sb-range-dates">
      <label>
        From
        <input
          :value="dateFrom"
          type="date"
          :max="dateTo || maxDate"
          @change="$emit('update:dateFrom', $event.target.value)"
        >
      </label>
      <label>
        To
        <input
          :value="dateTo"
          type="date"
          :min="dateFrom || undefined"
          :max="maxDate"
          @change="$emit('update:dateTo', $event.target.value)"
        >
      </label>
      <button
        type="button"
        class="sb-range-apply"
        :disabled="!canApply"
        @click="$emit('apply')"
      >
        Apply
      </button>
    </div>
  </div>
</template>

<script setup>
// Preset pills plus an explicit From/To range, extracted from the booking-history filter that was
// written inline in SuperAdminUserModal.vue so the Reports pages could reuse it rather than grow
// a second copy.
//
// Deliberately presentational: it owns no date maths and no fetching. The two callers mean
// different things by their presets (day counts in the user modal, period tokens in Reports), so
// resolving a preset into an actual window stays with the caller.
import { computed } from 'vue'
import { todayKey } from '@/utils/time'

const props = defineProps({
  // The selected preset's value.
  modelValue: { type: String, default: '' },
  // [{ label, value }] — the pills to show.
  presets: { type: Array, required: true },
  // Which preset value reveals the From/To inputs.
  customValue: { type: String, default: 'custom' },
  dateFrom: { type: String, default: '' },
  dateTo: { type: String, default: '' },
  ariaLabel: { type: String, default: 'Date range' },
})

defineEmits(['update:modelValue', 'update:dateFrom', 'update:dateTo', 'apply'])

// Local-time 'YYYY-MM-DD' (see utils/time.js) — never toISOString(), which would offer tomorrow
// as a selectable day for users in Manila.
const maxDate = todayKey()

// Apply stays disabled rather than letting an inverted range reach the server, so the guard is
// visible before the request instead of arriving as an error toast after it.
const canApply = computed(
  () => Boolean(props.dateFrom) && Boolean(props.dateTo) && props.dateFrom <= props.dateTo,
)
</script>

<style scoped>
.sb-range-filter {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.sb-range-presets {
  display: inline-flex;
  border: 1px solid var(--sb-card-border);
  border-radius: 999px;
  background: var(--sb-card-bg);
  padding: 3px;
  gap: 2px;
}

.sb-range-preset {
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: var(--sb-text-muted);
  font-size: 12px;
  font-weight: 700;
  padding: 6px 12px;
  cursor: pointer;
}

.sb-range-preset.active {
  background: var(--sb-primary);
  color: #fff;
}

.sb-range-dates {
  display: flex;
  align-items: end;
  flex-wrap: wrap;
  gap: 10px;
}

.sb-range-dates label {
  display: grid;
  gap: 4px;
  color: var(--sb-text-muted);
  font-size: 11px;
  font-weight: 700;
}

.sb-range-dates input {
  border: 1px solid var(--sb-card-border);
  border-radius: 9px;
  padding: 8px;
  background: var(--sb-card-bg);
  color: var(--sb-text-main);
  font: inherit;
}

.sb-range-apply {
  border: 1px solid var(--sb-card-border);
  border-radius: 9px;
  background: var(--sb-card-bg);
  color: var(--sb-text-main);
  font-size: 12px;
  font-weight: 700;
  padding: 8px 14px;
  cursor: pointer;
}

.sb-range-apply:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
