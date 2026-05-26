<template>
  <div class="budget-range" :class="`budget-range-${variant}`">
    <div
      v-if="variant !== 'dropdown'"
      class="d-flex justify-content-between align-items-start gap-3 flex-wrap mb-3"
    >
      <div>
        <label class="form-label fw-semibold small mb-1">{{ label }}</label>
        <div class="small text-muted">Choose the minimum and maximum hourly rate.</div>
      </div>

      <div class="budget-pill">
        {{ summaryText }}
      </div>
    </div>

    <div v-else class="budget-summary-large">
      {{ summaryText }}
    </div>

    <div class="slider-shell">
      <div class="slider-track"></div>
      <div class="slider-fill" :style="fillStyle"></div>

      <input
        type="range"
        class="slider-thumb slider-thumb-min"
        :min="minLimit"
        :max="maxLimit"
        :step="step"
        :value="normalizedMinValue"
        @input="updateMinValue"
      />

      <input
        type="range"
        class="slider-thumb slider-thumb-max"
        :min="minLimit"
        :max="maxLimit"
        :step="step"
        :value="maxThumbDisplayValue"
        @input="updateMaxValue"
      />
    </div>

    <div class="d-flex justify-content-between text-muted small mt-2">
      <span>{{ currencyFormatter.format(minLimit) }}</span>
      <span>{{ currencyFormatter.format(maxLimit) }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: {
    type: String,
    default: 'Budget Range'
  },
  minValue: {
    type: Number,
    required: true
  },
  maxValue: {
    type: Number,
    required: true
  },
  minLimit: {
    type: Number,
    default: 100
  },
  maxLimit: {
    type: Number,
    default: 1000
  },
  step: {
    type: Number,
    default: 50
  },
  variant: {
    type: String,
    default: 'default'
  }
})

const emit = defineEmits(['update:minValue', 'update:maxValue'])

const currencyFormatter = new Intl.NumberFormat('en-PH', {
  style: 'currency',
  currency: 'PHP',
  maximumFractionDigits: 0
})

const clampValue = (value) => {
  const parsedValue = Number(value)

  if (Number.isNaN(parsedValue)) {
    return props.minLimit
  }

  return Math.min(props.maxLimit, Math.max(props.minLimit, parsedValue))
}

const normalizedMinValue = computed(() =>
  Math.min(clampValue(props.minValue), clampValue(props.maxValue))
)

const normalizedMaxValue = computed(() =>
  Math.max(clampValue(props.minValue), clampValue(props.maxValue))
)

const minPercentage = computed(() =>
  ((normalizedMinValue.value - props.minLimit) / (props.maxLimit - props.minLimit)) * 100
)

const maxPercentage = computed(() =>
  ((normalizedMaxValue.value - props.minLimit) / (props.maxLimit - props.minLimit)) * 100
)

const fillStyle = computed(() => ({
  left: `${minPercentage.value}%`,
  width: `${maxPercentage.value - minPercentage.value}%`
}))

const maxThumbDisplayValue = computed(() =>
  props.minLimit + props.maxLimit - normalizedMaxValue.value
)

const summaryText = computed(() => {
  const minLabel = currencyFormatter.format(normalizedMinValue.value)
  const maxLabel = normalizedMaxValue.value >= props.maxLimit
    ? `${currencyFormatter.format(normalizedMaxValue.value)}+`
    : currencyFormatter.format(normalizedMaxValue.value)

  return `${minLabel} - ${maxLabel}`
})

const updateMinValue = (event) => {
  const nextValue = Math.min(Number(event.target.value), normalizedMaxValue.value)
  emit('update:minValue', nextValue)
}

const updateMaxValue = (event) => {
  const rawValue = Number(event.target.value)
  const nextValue = Math.max(
    props.minLimit + props.maxLimit - rawValue,
    normalizedMinValue.value
  )
  emit('update:maxValue', nextValue)
}
</script>

<style scoped>
.budget-range {
  width: 100%;
}

.budget-range-dropdown {
  padding: 0.25rem 0.35rem 0.1rem;
  font-family: inherit;
}

.budget-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 180px;
  padding: 0.6rem 0.9rem;
  border-radius: 999px;
  background: rgba(0, 137, 90, 0.08);
  border: 1px solid rgba(0, 137, 90, 0.16);
  color: var(--sb-primary, #00895a);
  font-weight: 700;
  font-size: 0.95rem;
}

.budget-summary-large {
  text-align: center;
  color: var(--sb-text-main);
  font-size: clamp(1.7rem, 3vw, 2.2rem);
  font-weight: 700;
  letter-spacing: -0.03em;
  margin-bottom: 1.4rem;
}

.slider-shell {
  position: relative;
  height: 26px;
}

.slider-track,
.slider-fill {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  height: 8px;
  border-radius: 999px;
}

.slider-track {
  inset-inline: 0;
  background: var(--sb-card-border);
}

.slider-fill {
  background: linear-gradient(90deg, var(--sb-primary-dark), var(--sb-primary-mid));
}

.slider-thumb {
  position: absolute;
  inset-inline: 0;
  top: 0;
  width: 100%;
  height: 26px;
  margin: 0;
  appearance: none;
  background: transparent;
  pointer-events: none;
}

.slider-thumb::-webkit-slider-runnable-track {
  height: 8px;
  background: transparent;
}

.slider-thumb::-moz-range-track {
  height: 8px;
  background: transparent;
}

.slider-thumb::-webkit-slider-thumb {
  appearance: none;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 3px solid #ffffff;
  background: var(--sb-primary);
  box-shadow: 0 6px 16px rgba(0, 137, 90, 0.22);
  cursor: pointer;
  pointer-events: auto;
  margin-top: -7px;
}

.slider-thumb::-moz-range-thumb {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 3px solid #ffffff;
  background: var(--sb-primary);
  box-shadow: 0 6px 16px rgba(0, 137, 90, 0.22);
  cursor: pointer;
  pointer-events: auto;
}

.slider-thumb-min {
  z-index: 2;
}

.slider-thumb-max {
  z-index: 3;
  direction: rtl;
}

.budget-range-dropdown .slider-shell {
  height: 44px;
}

.budget-range-dropdown .slider-track,
.budget-range-dropdown .slider-fill {
  height: 6px;
}

.budget-range-dropdown .slider-track {
  background: var(--sb-card-border);
}

.budget-range-dropdown .slider-fill {
  background: linear-gradient(90deg, var(--sb-primary-dark), var(--sb-primary-mid));
}

.budget-range-dropdown .slider-thumb::-webkit-slider-thumb {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  border: 2px solid rgba(0, 137, 90, 0.28);
  background: #ffffff;
  box-shadow: 0 10px 22px rgba(10, 122, 81, 0.14);
  margin-top: -18px;
}

.budget-range-dropdown .slider-thumb::-moz-range-thumb {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  border: 2px solid rgba(0, 137, 90, 0.28);
  background: #ffffff;
  box-shadow: 0 10px 22px rgba(10, 122, 81, 0.14);
}
</style>
