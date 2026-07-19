<template>
  <button
    ref="triggerRef"
    type="button"
    class="subject-trigger"
    :aria-expanded="isOpen ? 'true' : 'false'"
    :aria-controls="dialogId"
    @click="openModal"
  >
    <span class="subject-trigger-text" :class="{ 'is-placeholder': !selectedSubject }">
      {{ selectedSubject?.subject_name || placeholder }}
    </span>
    <span v-if="selectedSubject?.category" class="subject-trigger-tag">
      {{ selectedSubject.category }}
    </span>
    <span class="subject-trigger-icon" aria-hidden="true">
      <i class="bi bi-chevron-down"></i>
    </span>
  </button>

  <Teleport to="body">
    <div v-if="isOpen" class="subject-backdrop" role="presentation" @click.self="closeModal">
      <section
        :id="dialogId"
        class="subject-dialog"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="titleId"
        @keydown.esc.prevent="closeModal"
      >
        <div class="subject-header">
          <h2 :id="titleId" class="subject-title">{{ title }}</h2>
          <button type="button" class="subject-icon-btn" aria-label="Close" @click="closeModal">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <label class="subject-search-wrap" :for="searchId">
          <span class="subject-search-icon" aria-hidden="true">
            <i class="bi bi-search"></i>
          </span>
          <input
            :id="searchId"
            ref="searchRef"
            v-model.trim="searchQuery"
            class="subject-search sb-field"
            type="text"
            placeholder="Search subjects"
            @keydown.down.prevent="focusRow(0)"
          />
        </label>

        <!-- Searching: flat result list overrides browsing -->
        <div
          v-if="searchQuery"
          ref="listRef"
          class="subject-results"
          role="listbox"
          :aria-labelledby="titleId"
          @keydown="handleListKeydown"
        >
          <template v-if="searchResults.length">
            <button
              v-for="subject in searchResults"
              :key="subject.subject_code"
              type="button"
              class="subject-row"
              :class="{ 'is-selected': isSelected(subject.subject_code) }"
              role="option"
              :aria-selected="isSelected(subject.subject_code) ? 'true' : 'false'"
              @click="choose(subject.subject_code)"
            >
              <span class="subject-row-copy">
                <span class="subject-row-name">{{ subject.subject_name }}</span>
                <span class="subject-row-meta">{{ subject.category }}</span>
              </span>
              <span v-if="subject.matchedViaKeyword" class="subject-via-badge">
                via "{{ searchQuery }}"
              </span>
              <span v-else-if="isSelected(subject.subject_code)" class="subject-check" aria-hidden="true">
                <i class="bi bi-check-circle-fill"></i>
              </span>
            </button>
          </template>
          <p v-else class="subject-empty">No matching subjects for "{{ searchQuery }}".</p>
        </div>

        <!-- Browsing: category pane + subject pane -->
        <div v-else ref="listRef" class="subject-panes" @keydown="handleListKeydown">
          <nav class="subject-cats" aria-label="Subject categories">
            <button
              v-for="category in categories"
              :key="category"
              type="button"
              class="subject-cat"
              :class="[categoryClass(category), { 'is-active': category === activeCategory }]"
              @click="activeCategory = category"
            >
              <span class="subject-cat-dot" aria-hidden="true"></span>
              <span class="subject-cat-name">{{ category }}</span>
              <span class="subject-cat-count">{{ subjectsFor(category).length }}</span>
            </button>
          </nav>
          <div class="subject-list" role="listbox" :aria-labelledby="titleId">
            <p class="subject-crumb">{{ activeCategory }}</p>
            <button
              v-for="subject in subjectsFor(activeCategory)"
              :key="subject.subject_code"
              type="button"
              class="subject-row"
              :class="{ 'is-selected': isSelected(subject.subject_code) }"
              role="option"
              :aria-selected="isSelected(subject.subject_code) ? 'true' : 'false'"
              @click="choose(subject.subject_code)"
            >
              <span class="subject-row-name">{{ subject.subject_name }}</span>
              <span v-if="isSelected(subject.subject_code)" class="subject-check" aria-hidden="true">
                <i class="bi bi-check-circle-fill"></i>
              </span>
            </button>
          </div>
        </div>
      </section>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { categoryClass, searchSubjects, subjectCategories } from '@/components/subjectPicker.shared'

const props = defineProps({
  subjects: { type: Array, required: true },
  modelValue: { type: Array, required: true },
  title: { type: String, default: 'Choose Subject' },
  placeholder: { type: String, default: 'Select subject' },
})
const emit = defineEmits(['update:modelValue'])

const componentId = `subject-picker-${Math.random().toString(36).slice(2, 10)}`
const dialogId = `${componentId}-dialog`
const titleId = `${componentId}-title`
const searchId = `${componentId}-search`

const isOpen = ref(false)
const searchQuery = ref('')
const activeCategory = ref('')
const previousBodyOverflow = ref('')
const triggerRef = ref(null)
const searchRef = ref(null)
const listRef = ref(null)

const categories = computed(() => subjectCategories(props.subjects))
const searchResults = computed(() => searchSubjects(props.subjects, searchQuery.value))
const selectedSubject = computed(() =>
  props.subjects.find((subject) => props.modelValue.includes(subject.subject_code)),
)

const subjectsFor = (category) =>
  props.subjects.filter((subject) => subject.category === category)

const isSelected = (code) => props.modelValue.includes(code)

function openModal() {
  isOpen.value = true
}

function closeModal() {
  isOpen.value = false
}

function choose(code) {
  // Single-select: always replace the selection and close, so the trigger reflects the pick.
  emit('update:modelValue', [code])
  closeModal()
}

// Roving focus over the visible option rows (search results or category subjects),
// mirroring SbSelectModal's arrow-key navigation.
function visibleRows() {
  return [...(listRef.value?.querySelectorAll('.subject-row') || [])]
}

function focusRow(index) {
  const rows = visibleRows()
  if (!rows.length) return
  rows[Math.max(0, Math.min(index, rows.length - 1))].focus()
}

function handleListKeydown(event) {
  const rows = visibleRows()
  const current = rows.indexOf(document.activeElement)

  if (event.key === 'ArrowDown') {
    event.preventDefault()
    focusRow(current + 1)
  }

  if (event.key === 'ArrowUp') {
    event.preventDefault()
    if (current <= 0) {
      searchRef.value?.focus()
      return
    }
    focusRow(current - 1)
  }
}

watch(isOpen, async (value) => {
  if (value) {
    previousBodyOverflow.value = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    if (!activeCategory.value || !categories.value.includes(activeCategory.value)) {
      activeCategory.value = selectedSubject.value?.category || categories.value[0] || ''
    }
    await nextTick()
    searchRef.value?.focus()
    return
  }

  if (document.body.style.overflow === 'hidden') {
    document.body.style.overflow = previousBodyOverflow.value
  }
  searchQuery.value = ''
  await nextTick()
  triggerRef.value?.focus()
})

onBeforeUnmount(() => {
  if (document.body.style.overflow === 'hidden') {
    document.body.style.overflow = previousBodyOverflow.value
  }
})
</script>

<style scoped>
.subject-trigger {
  --cat: var(--sb-primary);
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.6rem;
  width: 100%;
  min-height: 42px;
  border: 1px solid var(--sb-card-border);
  border-radius: 10px;
  background: var(--sb-card-bg);
  color: var(--sb-text-main);
  padding: 0.55rem 0.75rem;
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.subject-trigger:hover,
.subject-trigger:focus-visible {
  border-color: var(--sb-primary);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--sb-primary) 12%, transparent);
  outline: none;
}

.subject-trigger-text {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.subject-trigger-text.is-placeholder {
  color: var(--sb-text-muted);
  font-weight: 400;
}

.subject-trigger-tag {
  flex: 0 0 auto;
  max-width: 45%;
  overflow: hidden;
  border-radius: 999px;
  background: var(--sb-primary-light);
  color: var(--sb-primary);
  padding: 2px 10px;
  font-size: 0.68rem;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.subject-trigger-icon {
  color: var(--sb-primary);
  flex: 0 0 auto;
}

.subject-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1060;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.25rem;
  background: rgba(7, 19, 16, 0.48);
}

.subject-dialog {
  display: grid;
  gap: 0.85rem;
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

.subject-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.subject-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 850;
}

.subject-icon-btn {
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

.subject-search-wrap {
  position: relative;
  display: grid;
}

.subject-search-icon {
  position: absolute;
  left: 0.85rem;
  top: 50%;
  color: var(--sb-text-muted);
  transform: translateY(-50%);
}

.subject-search {
  width: 100%;
  border: 1px solid var(--sb-card-border);
  border-radius: 12px;
  background: color-mix(in srgb, var(--sb-card-bg) 82%, transparent);
  color: var(--sb-text-main);
  padding: 0.6rem 0.9rem 0.6rem 2.35rem;
  font: inherit;
  outline: none;
}

.subject-search:focus {
  border-color: var(--sb-primary);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--sb-primary) 12%, transparent);
}

.subject-results,
.subject-panes {
  min-height: 240px;
  max-height: min(420px, 55vh);
  overflow: auto;
}

.subject-panes {
  display: flex;
  gap: 0;
  border-top: 1px solid var(--sb-card-border);
  overflow: hidden;
}

.subject-cats {
  flex: 0 0 160px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 0.6rem 0.5rem 0.6rem 0;
  border-right: 1px solid var(--sb-card-border);
  overflow-y: auto;
}

.subject-cat {
  --cat: var(--sb-primary);
  display: flex;
  align-items: center;
  gap: 0.45rem;
  border: 0;
  border-radius: 9px;
  background: transparent;
  color: var(--sb-text-muted);
  padding: 0.5rem 0.55rem;
  font-size: 0.78rem;
  font-weight: 600;
  text-align: left;
  cursor: pointer;
}

.subject-cat:hover {
  background: color-mix(in srgb, var(--cat) 7%, transparent);
}

.subject-cat.is-active {
  background: color-mix(in srgb, var(--cat) 12%, var(--sb-card-bg));
  color: var(--sb-text-main);
  font-weight: 700;
}

.subject-cat-dot {
  flex: 0 0 auto;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--cat);
}

.subject-cat-name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.subject-cat-count {
  flex: 0 0 auto;
  color: var(--sb-text-muted);
  font-size: 0.68rem;
}

.subject-list {
  flex: 1;
  min-width: 0;
  padding: 0.6rem 0 0.6rem 0.6rem;
  overflow-y: auto;
}

.subject-crumb {
  margin: 0 0 0.35rem;
  padding: 0 0.55rem;
  color: var(--sb-text-muted);
  font-size: 0.66rem;
  font-weight: 800;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.subject-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  width: 100%;
  border: 0;
  border-radius: 9px;
  background: transparent;
  color: var(--sb-text-main);
  padding: 0.55rem 0.65rem;
  font: inherit;
  font-size: 0.9rem;
  text-align: left;
  cursor: pointer;
}

.subject-row:hover,
.subject-row:focus-visible {
  background: var(--sb-primary-light);
  outline: none;
}

.subject-row.is-selected {
  background: var(--sb-primary-light);
  color: var(--sb-primary);
  font-weight: 700;
}

.subject-row-copy {
  display: grid;
  gap: 1px;
  min-width: 0;
}

.subject-row-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.subject-row-meta {
  color: var(--sb-text-muted);
  font-size: 0.72rem;
}

.subject-via-badge {
  flex: 0 0 auto;
  border-radius: 999px;
  background: color-mix(in srgb, var(--sb-pop-yellow-deep) 15%, var(--sb-card-bg));
  color: var(--sb-warning-text);
  padding: 2px 8px;
  font-size: 0.66rem;
  white-space: nowrap;
}

.subject-check {
  color: var(--sb-primary);
  flex: 0 0 auto;
}

.subject-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 120px;
  margin: 0;
  color: var(--sb-text-muted);
  font-weight: 750;
}

.cat-math { --cat: var(--sb-primary); }
.cat-science { --cat: var(--sb-secondary-blue); }
.cat-tech { --cat: var(--sb-aurora-violet); }
.cat-business { --cat: var(--sb-pop-yellow-deep); }
.cat-humanities { --cat: var(--sb-pop-orange-deep); }
.cat-arts { --cat: var(--sb-pop-pink-deep); }

@media (max-width: 640px) {
  .subject-backdrop {
    align-items: flex-end;
    padding: 0.75rem;
  }

  .subject-dialog {
    border-radius: 18px;
    max-height: calc(100vh - 1.5rem);
  }

  /* Sidebar collapses to a horizontal pill row */
  .subject-panes {
    flex-direction: column;
  }

  .subject-cats {
    flex: 0 0 auto;
    flex-direction: row;
    gap: 0.35rem;
    padding: 0.6rem 0 0.35rem;
    border-right: 0;
    border-bottom: 1px solid var(--sb-card-border);
    overflow-x: auto;
    overflow-y: hidden;
  }

  .subject-cat {
    flex: 0 0 auto;
    border: 1px solid var(--sb-card-border);
    border-radius: 999px;
    padding: 0.3rem 0.7rem;
    font-size: 0.72rem;
    white-space: nowrap;
  }

  .subject-cat.is-active {
    border-color: var(--cat);
  }

  .subject-cat-count {
    display: none;
  }

  .subject-list {
    padding-left: 0;
  }
}
</style>
