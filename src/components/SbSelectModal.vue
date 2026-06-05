<template>
  <button
    ref="triggerRef"
    type="button"
    class="sb-select-trigger"
    :class="triggerClass"
    :aria-expanded="isOpen ? 'true' : 'false'"
    :aria-controls="dialogId"
    @click="openModal"
  >
    <span class="sb-select-trigger-text" :class="{ 'is-placeholder': !selectedOption }">
      {{ selectedOption?.label || placeholder }}
    </span>
    <span class="sb-select-trigger-icon" aria-hidden="true">
      <i class="bi bi-chevron-down"></i>
    </span>
  </button>

  <Teleport to="body">
    <div
      v-if="isOpen"
      class="sb-select-backdrop"
      role="presentation"
      @click.self="closeModal"
    >
      <section
        :id="dialogId"
        ref="dialogRef"
        class="sb-select-dialog"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="titleId"
        @keydown="handleDialogKeydown"
      >
        <div class="sb-select-header">
          <h2 :id="titleId" class="sb-select-title">{{ title }}</h2>
          <button type="button" class="sb-select-icon-btn" aria-label="Close" @click="closeModal">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <label v-if="searchable" class="sb-select-search-wrap" :for="searchId">
          <span class="sb-select-search-icon" aria-hidden="true">
            <i class="bi bi-search"></i>
          </span>
          <input
            :id="searchId"
            ref="searchRef"
            v-model.trim="searchQuery"
            class="sb-select-search"
            type="text"
            :placeholder="searchPlaceholder || `Search ${title.toLowerCase()}`"
            :aria-controls="listboxId"
            @keydown.down.prevent="focusOption(0)"
          >
        </label>

        <button
          v-if="clearable && hasSelection"
          type="button"
          class="sb-select-clear"
          @click="selectValue(clearValue)"
        >
          <i class="bi bi-x-circle" aria-hidden="true"></i>
          {{ clearLabel }}
        </button>

        <div
          :id="listboxId"
          ref="listboxRef"
          class="sb-select-list"
          role="listbox"
          :aria-labelledby="titleId"
          :aria-activedescendant="activeOptionId"
          tabindex="-1"
          @keydown="handleListboxKeydown"
        >
          <template v-if="filteredGroups.length">
            <section
              v-for="group in filteredGroups"
              :key="group.label"
              class="sb-select-group"
            >
              <p v-if="group.label" class="sb-select-group-label">{{ group.label }}</p>
              <button
                v-for="option in group.options"
                :id="getOptionId(option)"
                :key="String(option.value)"
                :ref="el => setOptionRef(el, option)"
                type="button"
                class="sb-select-option"
                :class="{ 'is-selected': isSelected(option.value) }"
                role="option"
                :aria-selected="isSelected(option.value) ? 'true' : 'false'"
                @click="selectValue(option.value)"
              >
                <span class="sb-select-option-copy">
                  <span class="sb-select-option-label">{{ option.label }}</span>
                  <span v-if="option.description" class="sb-select-option-description">
                    {{ option.description }}
                  </span>
                </span>
                <span class="sb-select-check" aria-hidden="true">
                  <i class="bi" :class="isSelected(option.value) ? 'bi-check-circle-fill' : 'bi-circle'"></i>
                </span>
              </button>
            </section>
          </template>
          <p v-else class="sb-select-empty">{{ emptyMessage }}</p>
        </div>
      </section>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: null
  },
  options: {
    type: Array,
    default: () => []
  },
  groups: {
    type: Array,
    default: () => []
  },
  title: {
    type: String,
    default: 'Select an option'
  },
  placeholder: {
    type: String,
    default: 'Select an option'
  },
  searchable: {
    type: Boolean,
    default: true
  },
  clearable: {
    type: Boolean,
    default: false
  },
  clearLabel: {
    type: String,
    default: 'Clear selection'
  },
  clearValue: {
    type: [String, Number, null],
    default: ''
  },
  searchPlaceholder: {
    type: String,
    default: ''
  },
  emptyMessage: {
    type: String,
    default: 'No options found.'
  },
  triggerClass: {
    type: [String, Array, Object],
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])

const componentId = `sb-select-${Math.random().toString(36).slice(2, 10)}`
const dialogId = `${componentId}-dialog`
const titleId = `${componentId}-title`
const searchId = `${componentId}-search`
const listboxId = `${componentId}-listbox`

const isOpen = ref(false)
const searchQuery = ref('')
const activeIndex = ref(0)
const previousBodyOverflow = ref('')
const triggerRef = ref(null)
const dialogRef = ref(null)
const searchRef = ref(null)
const listboxRef = ref(null)
const optionRefs = ref(new Map())

const normalizedGroups = computed(() => {
  const groups = props.groups
    .filter(group => Array.isArray(group.options) && group.options.length)
    .map(group => ({
      label: group.label || '',
      options: normalizeOptions(group.options)
    }))

  if (props.options.length) {
    groups.push({
      label: '',
      options: normalizeOptions(props.options)
    })
  }

  return groups
})

const flatOptions = computed(() =>
  normalizedGroups.value.flatMap(group => group.options)
)

const selectedOption = computed(() =>
  flatOptions.value.find(option => option.value === props.modelValue)
)

const hasSelection = computed(() => props.modelValue !== null && props.modelValue !== '')

const filteredGroups = computed(() => {
  const query = searchQuery.value.toLowerCase()

  return normalizedGroups.value
    .map(group => ({
      ...group,
      options: group.options.filter(option => {
        if (!query) {
          return true
        }

        return [option.label, option.description, String(option.value)]
          .filter(Boolean)
          .some(value => value.toLowerCase().includes(query))
      })
    }))
    .filter(group => group.options.length)
})

const visibleOptions = computed(() =>
  filteredGroups.value.flatMap(group => group.options)
)

const activeOptionId = computed(() => {
  const option = visibleOptions.value[activeIndex.value]
  return option ? getOptionId(option) : undefined
})

watch(isOpen, async value => {
  if (value) {
    lockBodyScroll()
    optionRefs.value = new Map()
    activeIndex.value = getSelectedVisibleIndex()
    await nextTick()
    focusInitialElement()
    return
  }

  unlockBodyScroll()
  searchQuery.value = ''
  await nextTick()
  triggerRef.value?.focus()
})

watch(searchQuery, async () => {
  activeIndex.value = 0
  await nextTick()
})

onBeforeUnmount(() => {
  unlockBodyScroll()
})

function normalizeOptions(options) {
  return options
    .filter(option => option && Object.prototype.hasOwnProperty.call(option, 'value'))
    .map(option => ({
      label: String(option.label ?? option.value),
      value: option.value,
      description: option.description || ''
    }))
}

function openModal() {
  isOpen.value = true
}

function closeModal() {
  isOpen.value = false
}

function selectValue(value) {
  emit('update:modelValue', value)
  closeModal()
}

function isSelected(value) {
  return value === props.modelValue
}

function getOptionId(option) {
  return `${componentId}-option-${String(option.value).replace(/[^a-zA-Z0-9_-]/g, '-')}`
}

function setOptionRef(el, option) {
  if (el) {
    optionRefs.value.set(option.value, el)
  }
}

function getSelectedVisibleIndex() {
  const index = visibleOptions.value.findIndex(option => option.value === props.modelValue)
  return index >= 0 ? index : 0
}

function focusInitialElement() {
  if (props.searchable) {
    searchRef.value?.focus()
    return
  }

  focusOption(activeIndex.value)
}

function focusOption(index) {
  if (!visibleOptions.value.length) {
    listboxRef.value?.focus()
    return
  }

  activeIndex.value = Math.max(0, Math.min(index, visibleOptions.value.length - 1))
  const option = visibleOptions.value[activeIndex.value]
  optionRefs.value.get(option.value)?.focus()
}

function handleDialogKeydown(event) {
  if (event.key === 'Escape') {
    event.preventDefault()
    closeModal()
  }
}

function handleListboxKeydown(event) {
  if (event.key === 'ArrowDown') {
    event.preventDefault()
    focusOption(activeIndex.value + 1)
  }

  if (event.key === 'ArrowUp') {
    event.preventDefault()
    focusOption(activeIndex.value - 1)
  }

  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    const option = visibleOptions.value[activeIndex.value]

    if (option) {
      selectValue(option.value)
    }
  }
}

function lockBodyScroll() {
  previousBodyOverflow.value = document.body.style.overflow
  document.body.style.overflow = 'hidden'
}

function unlockBodyScroll() {
  if (document.body.style.overflow === 'hidden') {
    document.body.style.overflow = previousBodyOverflow.value
  }
}
</script>

<style scoped>
.sb-select-trigger {
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  width: 100%;
  min-height: 44px;
  border: 1px solid var(--sb-card-border);
  border-radius: 14px;
  background: color-mix(in srgb, var(--sb-card-bg) 86%, transparent);
  color: var(--sb-text-main);
  padding: 0.7rem 0.85rem;
  font: inherit;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, background-color 0.18s ease;
}

.sb-select-trigger:hover,
.sb-select-trigger:focus-visible {
  border-color: var(--sb-primary);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--sb-primary) 12%, transparent);
  outline: none;
}

.sb-select-trigger-text {
  min-width: 0;
  overflow: hidden;
  color: var(--sb-text-main);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sb-select-trigger-text.is-placeholder {
  color: var(--sb-text-muted);
}

.sb-select-trigger-icon {
  color: var(--sb-primary);
  flex: 0 0 auto;
}

.sb-select-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1060;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.25rem;
  background: rgba(7, 19, 16, 0.48);
  backdrop-filter: blur(8px);
}

.sb-select-dialog {
  display: grid;
  gap: 1rem;
  width: min(560px, 100%);
  max-height: calc(100vh - 2.5rem);
  border: 1px solid color-mix(in srgb, var(--sb-card-border) 78%, transparent);
  border-radius: 20px;
  background: color-mix(in srgb, var(--sb-card-bg) 94%, transparent);
  color: var(--sb-text-main);
  box-shadow: 0 30px 80px rgba(7, 19, 16, 0.28);
  padding: 1rem;
  overflow: hidden;
}

.sb-select-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.sb-select-title {
  margin: 0;
  color: var(--sb-text-main);
  font-size: 1.1rem;
  font-weight: 850;
  letter-spacing: 0;
}

.sb-select-icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border: 0;
  border-radius: 999px;
  background: color-mix(in srgb, var(--sb-card-border) 44%, transparent);
  color: var(--sb-text-main);
  cursor: pointer;
}

.sb-select-search-wrap {
  position: relative;
  display: grid;
}

.sb-select-search-icon {
  position: absolute;
  left: 0.85rem;
  top: 50%;
  color: var(--sb-text-muted);
  transform: translateY(-50%);
}

.sb-select-search {
  width: 100%;
  border: 1px solid var(--sb-card-border);
  border-radius: 14px;
  background: color-mix(in srgb, var(--sb-card-bg) 82%, transparent);
  color: var(--sb-text-main);
  padding: 0.72rem 0.9rem 0.72rem 2.35rem;
  font: inherit;
  outline: none;
}

.sb-select-search:focus {
  border-color: var(--sb-primary);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--sb-primary) 12%, transparent);
}

.sb-select-clear {
  justify-self: start;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  border: 0;
  background: transparent;
  color: var(--sb-primary);
  padding: 0.2rem 0;
  font-weight: 800;
  cursor: pointer;
}

.sb-select-list {
  display: grid;
  gap: 0.75rem;
  max-height: min(420px, 58vh);
  overflow: auto;
  padding-right: 0.15rem;
  outline: none;
}

.sb-select-group {
  display: grid;
  gap: 0.4rem;
}

.sb-select-group-label {
  position: sticky;
  top: 0;
  z-index: 1;
  margin: 0;
  border: 1px solid color-mix(in srgb, var(--sb-card-border) 78%, transparent);
  border-radius: 999px;
  background: color-mix(in srgb, var(--sb-card-bg) 92%, transparent);
  color: var(--sb-text-muted);
  padding: 0.35rem 0.65rem;
  font-size: 0.72rem;
  font-weight: 850;
  letter-spacing: 0;
  text-transform: uppercase;
}

.sb-select-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  width: 100%;
  border: 1px solid var(--sb-card-border);
  border-radius: 14px;
  background: color-mix(in srgb, var(--sb-card-bg) 82%, transparent);
  color: var(--sb-text-main);
  padding: 0.78rem 0.9rem;
  font: inherit;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, background-color 0.18s ease;
}

.sb-select-option:hover,
.sb-select-option:focus-visible,
.sb-select-option.is-selected {
  border-color: var(--sb-primary);
  background: color-mix(in srgb, var(--sb-primary) 11%, var(--sb-card-bg));
  box-shadow: 0 12px 28px color-mix(in srgb, var(--sb-primary) 13%, transparent);
  outline: none;
}

.sb-select-option-copy {
  display: grid;
  gap: 0.15rem;
  min-width: 0;
}

.sb-select-option-label {
  color: var(--sb-text-main);
  font-weight: 850;
}

.sb-select-option-description {
  color: var(--sb-text-muted);
  font-size: 0.84rem;
  line-height: 1.35;
}

.sb-select-check {
  color: var(--sb-primary);
  flex: 0 0 auto;
}

.sb-select-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 120px;
  margin: 0;
  color: var(--sb-text-muted);
  font-weight: 750;
}

@media (max-width: 640px) {
  .sb-select-backdrop {
    align-items: flex-end;
    padding: 0.75rem;
  }

  .sb-select-dialog {
    border-radius: 18px;
    max-height: calc(100vh - 1.5rem);
  }
}
</style>
