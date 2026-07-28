<template>
  <section class="taxonomy-picker">
    <div class="search-wrap">
      <span class="search-icon" aria-hidden="true">&#128269;</span>
      <input
        v-model.trim="searchQuery"
        type="text"
        class="search-input"
        placeholder="Search subjects"
        aria-label="Search subjects"
      />
    </div>

    <div v-if="searchQuery">
      <div v-if="searchResults.length" class="dropdown-preview">
        <button
          v-for="subject in searchResults"
          :key="subject.subject_code"
          type="button"
          class="dropdown-row"
          :class="{ selected: modelValue.includes(subject.subject_code) }"
          @click="toggle(subject.subject_code)"
        >
          <span class="left">
            <span class="name">{{ subject.subject_name }}</span>
            <span class="meta">{{ subject.category }}</span>
          </span>
          <span v-if="modelValue.includes(subject.subject_code)" class="check">&#10003; Added</span>
          <span v-else-if="subject.matchedViaKeyword" class="via-badge">via "{{ searchQuery }}"</span>
        </button>
      </div>
      <div v-else class="dropdown-preview">
        <div class="empty-state">
          <p>No matching subjects{{ searchQuery ? ` for "${searchQuery}"` : '' }}.</p>
          <button v-if="allowPropose" type="button" class="propose-cta" @click="emit('propose', searchQuery)">
            Can't find it? Propose it &rarr;
          </button>
        </div>
      </div>
    </div>

    <template v-else>
      <div v-if="!activeCategory" class="category-grid">
        <button
          v-for="category in categories"
          :key="category"
          type="button"
          class="category-card"
          :class="categoryClass(category)"
          @click="activeCategory = category"
        >
          <span class="monogram">{{ category[0] }}</span>
          <strong>{{ category }}</strong>
          <small>{{ subjectsFor(category).length }} subjects<span v-if="selectedFor(category)"> · {{ selectedFor(category) }} selected</span></small>
        </button>
      </div>
      <div v-else class="drill-pane" :class="categoryClass(activeCategory)">
        <button type="button" class="back" @click="activeCategory = ''">All categories</button>
        <span class="breadcrumb">/ {{ activeCategory }}</span>
        <div class="chips">
          <button
            v-for="subject in subjectsFor(activeCategory)"
            :key="subject.subject_code"
            type="button"
            class="subject-chip"
            :class="{ selected: modelValue.includes(subject.subject_code) }"
            @click="toggle(subject.subject_code)"
          >
            <span class="dot"></span>{{ subject.subject_name }}
          </button>
        </div>
      </div>
    </template>

    <div v-if="selectedSubjects.length" class="selection-tray">
      <span>Selected {{ modelValue.length }}<span v-if="maxSelection">/{{ maxSelection }}</span></span>
      <button
        v-for="subject in selectedSubjects"
        :key="subject.subject_code"
        type="button"
        class="subject-chip selected"
        :class="categoryClass(subject.category)"
        @click="toggle(subject.subject_code)"
      >
        <span class="dot"></span>{{ subject.subject_name }} ×
      </button>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { categoryClass, searchSubjects, subjectCategories } from '@/components/subjectPicker.shared'

const props = defineProps({
  subjects: { type: Array, required: true },
  modelValue: { type: Array, required: true },
  maxSelection: { type: Number, default: null },
  allowPropose: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue', 'propose'])
const activeCategory = ref('')
const searchQuery = ref('')
const categories = computed(() => subjectCategories(props.subjects))
const selectedSubjects = computed(() => props.subjects.filter((subject) => props.modelValue.includes(subject.subject_code)))
const subjectsFor = (category) => props.subjects.filter((subject) => subject.category === category)
const selectedFor = (category) => subjectsFor(category).filter((subject) => props.modelValue.includes(subject.subject_code)).length
function toggle(code) { if (props.modelValue.includes(code)) emit('update:modelValue', props.modelValue.filter((value) => value !== code)); else if (!props.maxSelection || props.modelValue.length < props.maxSelection) emit('update:modelValue', [...props.modelValue, code]) }

const searchResults = computed(() => searchSubjects(props.subjects, searchQuery.value))
</script>

<style scoped>
.taxonomy-picker { --cat: var(--sb-primary); }
.search-wrap { position: relative; margin-bottom: 14px; }
.search-icon { position: absolute; left: 11px; top: 50%; transform: translateY(-50%); color: var(--sb-text-muted); font-size: .85rem; }
.search-input { width: 100%; padding: 10px 12px 10px 34px; border: 1.5px solid var(--sb-card-border); border-radius: 10px; font-size: .9rem; background: var(--sb-bg); color: var(--sb-text-main); font-family: inherit; box-sizing: border-box; }
.search-input:focus { border-color: var(--sb-primary); outline: none; }
.dropdown-preview { border: 1px solid var(--sb-card-border); border-radius: 10px; overflow: hidden; }
.dropdown-row { width: 100%; display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; border: 0; border-bottom: 1px solid var(--sb-card-border); background: var(--sb-card-bg); color: var(--sb-text-main); font-size: .85rem; text-align: left; }
.dropdown-row:last-child { border-bottom: 0; }
.dropdown-row:hover { background: color-mix(in srgb, var(--sb-primary) 6%, var(--sb-card-bg)); }
.dropdown-row.selected { background: color-mix(in srgb, var(--sb-primary) 10%, var(--sb-card-bg)); font-weight: 600; }
.dropdown-row .left { display: flex; flex-direction: column; gap: 2px; }
.dropdown-row .name { font-weight: 600; }
.dropdown-row .meta { font-size: .74rem; color: var(--sb-text-muted); }
.dropdown-row .via-badge { font-size: .68rem; padding: 2px 7px; border-radius: 999px; background: color-mix(in srgb, var(--sb-pop-yellow-deep) 15%, var(--sb-card-bg)); color: var(--sb-warning-text); white-space: nowrap; }
.dropdown-row .check { color: var(--sb-primary); font-weight: 700; font-size: .78rem; white-space: nowrap; }
.empty-state { padding: 22px 16px; text-align: center; }
.empty-state p { color: var(--sb-text-muted); font-size: .85rem; margin: 0 0 10px; }
.propose-cta { border: 0; background: transparent; color: var(--sb-primary); font-weight: 700; font-size: .85rem; }
.category-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
.category-card, .subject-chip, .back { border: 1px solid var(--sb-card-border); background: var(--sb-card-bg); color: var(--sb-text-main); }
.category-card { position: relative; overflow: hidden; min-height: 112px; padding: 16px; text-align: left; border-color: color-mix(in srgb, var(--cat) 30%, var(--sb-card-border)); background: linear-gradient(135deg, color-mix(in srgb, var(--cat) 12%, var(--sb-card-bg)), var(--sb-card-bg) 65%); border-radius: 16px; }
.category-card strong, .category-card small { display: block; position: relative; }
.category-card small, .breadcrumb, .selection-tray > span { color: var(--sb-text-muted); margin-top: 4px; }
.monogram { position: absolute; right: -8px; bottom: -35px; font: 700 6rem Georgia, serif; color: color-mix(in srgb, var(--cat) 20%, transparent); }
.drill-pane { border: 1px solid var(--sb-card-border); border-left: 4px solid var(--cat); border-radius: 14px; padding: 18px; }
.back { border: 0; color: var(--sb-primary); font-weight: 600; }.breadcrumb { margin-left: 8px; }.chips { margin-top: 14px; }
.subject-chip { border-radius: 999px; padding: 7px 12px; margin: 0 7px 7px 0; font-size: .85rem; }
.subject-chip.selected { border-color: var(--cat); background: color-mix(in srgb, var(--cat) 12%, var(--sb-card-bg)); font-weight: 600; }
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; background: var(--cat); }
.selection-tray { border-top: 1px dashed var(--sb-border-light); margin-top: 14px; padding-top: 12px; }.selection-tray > span { font-size: .8rem; margin-right: 8px; }
.cat-math { --cat: var(--sb-primary); }.cat-science { --cat: var(--sb-secondary-blue); }.cat-tech { --cat: var(--sb-aurora-violet); }.cat-business { --cat: var(--sb-pop-yellow-deep); }.cat-humanities { --cat: var(--sb-pop-orange-deep); }.cat-arts { --cat: var(--sb-pop-pink-deep); }
@media (max-width: 640px) { .category-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
</style>
