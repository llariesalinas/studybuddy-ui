<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="sb-export-backdrop"
      role="presentation"
      @click.self="close"
    >
      <section
        ref="dialogRef"
        class="sb-export-dialog"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="titleId"
        @keydown="handleDialogKeydown"
      >
        <header class="sb-export-header">
          <div>
            <h2 :id="titleId" class="sb-export-title">{{ title }}</h2>
            <p v-if="scopeLine" class="sb-export-scope">
              <span class="sb-export-dot" aria-hidden="true"></span>
              {{ scopeLine }}
            </p>
          </div>
          <button type="button" class="sb-export-icon-btn" aria-label="Close" @click="close">
            <i class="bi bi-x-lg"></i>
          </button>
        </header>

        <div class="sb-export-split">
          <div
            class="sb-export-list"
            role="group"
            :aria-labelledby="titleId"
          >
            <label
              v-for="item in items"
              :key="item.id"
              class="sb-export-row"
              :class="{ 'is-checked': isChecked(item.id) }"
            >
              <input
                ref="itemInputs"
                type="checkbox"
                class="sb-export-checkbox"
                :checked="isChecked(item.id)"
                @change="toggle(item.id)"
              >
              <span class="sb-export-row-label">{{ item.label }}</span>
            </label>
          </div>

          <aside class="sb-export-preview" aria-live="polite">
            <h3 class="sb-export-preview-title">You will get</h3>
            <ul v-if="selectedItems.length" class="sb-export-manifest">
              <li v-for="item in selectedItems" :key="item.id">{{ item.label }}</li>
            </ul>
            <p v-else class="sb-export-manifest-empty">Nothing selected</p>
            <p class="sb-export-filename">{{ previewFilename || '—' }}</p>
          </aside>
        </div>

        <footer class="sb-export-footer">
          <button type="button" class="sb-export-linkbtn" @click="toggleAll">
            {{ allChecked ? 'Clear all' : 'Select all' }}
          </button>
          <div class="sb-export-actions">
            <button type="button" class="sb-export-btn is-ghost" @click="close">Cancel</button>
            <button
              type="button"
              class="sb-export-btn is-primary"
              :disabled="!selectedIds.length || busy"
              @click="confirm"
            >
              <i class="bi bi-download" aria-hidden="true"></i>
              {{ exportLabel }}
            </button>
          </div>
        </footer>
      </section>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { exportFilename } from '../utils/csv.js'

const props = defineProps({
  open: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    required: true
  },
  // [{ id, label, fileLabel }] -- fileLabel names the file when this is the only ticked item.
  items: {
    type: Array,
    default: () => []
  },
  scopeLine: {
    type: String,
    default: ''
  },
  // Filename stem used whenever two or more items are ticked.
  combinedFileLabel: {
    type: String,
    default: 'report'
  },
  // Extension the download will carry. The analytics report is an xlsx workbook built server-side;
  // the user directory is still a csv built in the browser.
  fileExtension: {
    type: String,
    default: 'csv'
  },
  busy: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['confirm', 'close'])

const componentId = `sb-export-${Math.random().toString(36).slice(2, 10)}`
const titleId = `${componentId}-title`

const dialogRef = ref(null)
const itemInputs = ref([])
// Seeded here as well as in the open watcher, so a modal mounted with open already true still
// starts fully ticked rather than with an empty, un-exportable selection.
const selectedIds = ref(props.open ? props.items.map(item => item.id) : [])
const previousBodyOverflow = ref('')
const previouslyFocused = ref(null)

const selectedItems = computed(() =>
  props.items.filter(item => selectedIds.value.includes(item.id))
)

const allChecked = computed(
  () => props.items.length > 0 && selectedIds.value.length === props.items.length
)

// A single ticked item names the file after itself, so a folder of exports stays self-describing.
const previewFilename = computed(() => {
  if (!selectedItems.value.length) return ''

  const label = selectedItems.value.length === 1
    ? selectedItems.value[0].fileLabel || selectedItems.value[0].id
    : props.combinedFileLabel

  return exportFilename(label, props.fileExtension)
})

const exportLabel = computed(() =>
  selectedIds.value.length ? `Export ${selectedIds.value.length}` : 'Export'
)

// Opens with everything ticked, so confirming without touching anything reproduces the previous
// all-in-one output and the modal only ever narrows what you get.
watch(
  () => props.open,
  async isOpen => {
    if (isOpen) {
      previouslyFocused.value = document.activeElement
      selectedIds.value = props.items.map(item => item.id)
      lockBodyScroll()
      await nextTick()
      itemInputs.value[0]?.focus()
      return
    }

    unlockBodyScroll()
    await nextTick()
    previouslyFocused.value?.focus?.()
  }
)

onBeforeUnmount(() => {
  unlockBodyScroll()
})

function isChecked(id) {
  return selectedIds.value.includes(id)
}

function toggle(id) {
  selectedIds.value = isChecked(id)
    ? selectedIds.value.filter(value => value !== id)
    : [...selectedIds.value, id]
}

function toggleAll() {
  selectedIds.value = allChecked.value ? [] : props.items.map(item => item.id)
}

function confirm() {
  if (!selectedIds.value.length) return

  // Emitted in the order the items were declared, which is the order they are written to the file.
  emit('confirm', {
    ids: selectedItems.value.map(item => item.id),
    filename: previewFilename.value
  })
}

function close() {
  emit('close')
}

function handleDialogKeydown(event) {
  if (event.key === 'Escape') {
    event.preventDefault()
    close()
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
.sb-export-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1060;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.25rem;
  background: rgba(7, 19, 16, 0.48);
}

.sb-export-dialog {
  display: grid;
  width: min(620px, 100%);
  max-height: calc(100vh - 2.5rem);
  border: 1px solid color-mix(in srgb, var(--sb-card-border) 78%, transparent);
  border-radius: 20px;
  background: color-mix(in srgb, var(--sb-card-bg) 94%, transparent);
  color: var(--sb-text-main);
  box-shadow: 0 30px 80px rgba(7, 19, 16, 0.28);
  overflow: hidden;
}

.sb-export-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.15rem 1.25rem 0.85rem;
}

.sb-export-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
}

.sb-export-scope {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin: 0.35rem 0 0;
  font-size: 0.78rem;
  color: var(--sb-text-muted);
}

.sb-export-dot {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: var(--sb-primary);
  flex: none;
}

.sb-export-icon-btn {
  border: 0;
  background: transparent;
  color: var(--sb-text-muted);
  padding: 0.25rem;
  line-height: 1;
  cursor: pointer;
}

.sb-export-split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 0;
  overflow: hidden;
}

.sb-export-list {
  padding: 0.25rem 0.85rem 0.75rem 1.25rem;
  overflow-y: auto;
}

.sb-export-row {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.55rem 0.4rem;
  border-radius: 11px;
  cursor: pointer;
}

.sb-export-row + .sb-export-row {
  border-top: 1px solid color-mix(in srgb, var(--sb-card-border) 45%, transparent);
}

.sb-export-row.is-checked {
  background: color-mix(in srgb, var(--sb-primary) 6%, transparent);
}

.sb-export-checkbox {
  width: 18px;
  height: 18px;
  flex: none;
  accent-color: var(--sb-primary);
  cursor: pointer;
}

.sb-export-row-label {
  font-size: 0.85rem;
  font-weight: 600;
}

.sb-export-preview {
  border-left: 1px solid color-mix(in srgb, var(--sb-card-border) 60%, transparent);
  background: color-mix(in srgb, var(--sb-primary) 4%, transparent);
  padding: 0.9rem 1rem;
  overflow-y: auto;
}

.sb-export-preview-title {
  margin: 0 0 0.5rem;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--sb-text-muted);
}

.sb-export-manifest {
  list-style: none;
  margin: 0;
  padding: 0;
}

.sb-export-manifest li {
  position: relative;
  padding: 0.35rem 0 0.35rem 1rem;
  font-size: 0.78rem;
  border-bottom: 1px dashed color-mix(in srgb, var(--sb-card-border) 60%, transparent);
}

.sb-export-manifest li:last-child {
  border-bottom: 0;
}

.sb-export-manifest li::before {
  content: '';
  position: absolute;
  left: 2px;
  top: 0.78rem;
  width: 5px;
  height: 5px;
  border-radius: 999px;
  background: var(--sb-primary);
}

.sb-export-manifest-empty {
  margin: 0;
  font-size: 0.78rem;
  font-style: italic;
  color: var(--sb-text-muted);
}

.sb-export-filename {
  margin: 0.7rem 0 0;
  padding-top: 0.6rem;
  border-top: 1px solid color-mix(in srgb, var(--sb-card-border) 60%, transparent);
  font-family: var(--sb-font-mono);
  font-size: 0.72rem;
  color: var(--sb-text-muted);
  word-break: break-all;
}

.sb-export-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.85rem 1.25rem;
  border-top: 1px solid color-mix(in srgb, var(--sb-card-border) 60%, transparent);
}

.sb-export-linkbtn {
  border: 0;
  background: none;
  padding: 0;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--sb-primary);
  cursor: pointer;
}

.sb-export-actions {
  display: flex;
  gap: 0.5rem;
}

/* Mirrors .export-button / .refresh-button on SuperAdminReports.vue, which are scoped there. */
.sb-export-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  border: 0;
  border-radius: 999px;
  padding: 9px 16px;
  font-size: 13px;
  font-weight: 800;
  background: var(--sb-primary);
  color: #fff;
  cursor: pointer;
}

.sb-export-btn.is-ghost {
  background: transparent;
  border: 1px solid var(--sb-card-border);
  color: var(--sb-text-main);
}

.sb-export-btn:disabled {
  background: color-mix(in srgb, var(--sb-text-muted) 22%, transparent);
  color: var(--sb-text-muted);
  cursor: not-allowed;
}

@media (max-width: 560px) {
  .sb-export-backdrop {
    align-items: flex-end;
    padding: 0.75rem;
  }

  .sb-export-dialog {
    border-radius: 18px;
    max-height: calc(100vh - 1.5rem);
  }

  .sb-export-split {
    grid-template-columns: 1fr;
  }

  .sb-export-preview {
    border-left: 0;
    border-top: 1px solid color-mix(in srgb, var(--sb-card-border) 60%, transparent);
  }
}
</style>
