<template>
  <section class="taxonomy-picker">
    <div class="search-wrap">
      <i class="bi bi-search search-icon" aria-hidden="true"></i>
      <input
        v-model.trim="searchQuery"
        type="text"
        class="search-input"
        :placeholder="searchPlaceholder"
        :aria-label="searchPlaceholder"
      />
      <button
        v-if="searchQuery"
        type="button"
        class="search-clear"
        aria-label="Clear search"
        @click="searchQuery = ''"
      >
        <i class="bi bi-x-lg" aria-hidden="true"></i>
      </button>
    </div>

    <!-- Focused category header: back control + identity. Shared by browse and in-category search. -->
    <template v-if="activeCategory">
      <button type="button" class="back-pill" @click="activeCategory = ''">
        <i class="bi bi-arrow-left" aria-hidden="true"></i> All categories
      </button>
      <div class="head-rule"></div>
      <h4 class="category-title" :class="categoryClass(activeCategory)">
        <span class="category-dot"></span>{{ activeCategory }}
      </h4>
    </template>

    <!-- Top-level search: narrowed category cards as a jump-in shortcut. -->
    <template v-else-if="searchQuery && searchResults.length">
      <span class="count-line">
        {{ searchResults.length }} {{ searchResults.length === 1 ? 'result' : 'results' }}
        for &ldquo;{{ searchQuery }}&rdquo; in {{ matchedCategories.length }}
        {{ matchedCategories.length === 1 ? 'category' : 'categories' }}
      </span>
      <p class="section-label">Jump to a category</p>
      <div class="category-grid jump-grid">
        <button
          v-for="entry in matchedCategories"
          :key="entry.category"
          type="button"
          class="category-card compact"
          :class="categoryClass(entry.category)"
          @click="activeCategory = entry.category"
        >
          <strong>{{ entry.category }}</strong>
          <small class="card-hit">{{ entry.count }} {{ entry.count === 1 ? 'match' : 'matches' }}</small>
        </button>
      </div>
      <p class="section-label">Matching subjects</p>
    </template>

    <span v-if="countLine" class="count-line">{{ countLine }}</span>

    <!-- Search results: descriptive rows (name, category, description, keyword badge). -->
    <template v-if="searchQuery">
      <div v-if="scopedResults.length" class="result-rows">
        <button
          v-for="subject in scopedResults"
          :key="subject.subject_code"
          type="button"
          class="result-row"
          :class="{ selected: modelValue.includes(subject.subject_code), blocked: isBlocked(subject.subject_code) }"
          :disabled="isBlocked(subject.subject_code)"
          :title="isBlocked(subject.subject_code) ? limitMessage : undefined"
          @click="toggle(subject.subject_code)"
        >
          <span class="left">
            <span class="name">{{ subject.subject_name }}</span>
            <span v-if="!activeCategory" class="meta" :class="categoryClass(subject.category)">
              <span class="category-dot"></span>{{ subject.category }}
            </span>
            <span v-if="subject.description" class="desc">
              <template v-for="(segment, i) in highlightSegments(subject.description, searchQuery)" :key="i">
                <strong v-if="segment.match">{{ segment.text }}</strong>
                <template v-else>{{ segment.text }}</template>
              </template>
            </span>
          </span>
          <span v-if="modelValue.includes(subject.subject_code)" class="check">&#10003; Added</span>
        </button>
      </div>
      <div v-else class="empty-state">
        <p>No matching subjects{{ activeCategory ? ` in ${activeCategory}` : '' }} for &ldquo;{{ searchQuery }}&rdquo;.</p>
        <button v-if="allowPropose && !outsideMatchCount" type="button" class="propose-cta" @click="emit('propose', searchQuery)">
          Can't find it? Propose it &rarr;
        </button>
      </div>

      <p v-if="outsideMatchCount" class="hint-line">
        {{ outsideMatchCount }} more {{ outsideMatchCount === 1 ? 'match' : 'matches' }} in other categories &mdash;
        <button type="button" class="hint-link" @click="activeCategory = ''">search all categories</button>
      </p>
    </template>

    <!-- Browsing a focused category: compact chips. -->
    <div v-else-if="activeCategory" class="chips">
      <button
        v-for="subject in subjectsFor(activeCategory)"
        :key="subject.subject_code"
        type="button"
        class="subject-chip"
        :class="{ selected: modelValue.includes(subject.subject_code), blocked: isBlocked(subject.subject_code) }"
        :disabled="isBlocked(subject.subject_code)"
        :title="isBlocked(subject.subject_code) ? limitMessage : (subject.description || undefined)"
        @click="toggle(subject.subject_code)"
      >
        {{ subject.subject_name }}
      </button>
    </div>

    <!-- Top level: the category grid. -->
    <div v-else class="category-grid">
      <button
        v-for="category in categories"
        :key="category"
        type="button"
        class="category-card"
        :class="categoryClass(category)"
        @click="activeCategory = category"
      >
        <span class="monogram" aria-hidden="true">{{ category[0] }}</span>
        <strong>{{ category }}</strong>
        <small>{{ subjectsFor(category).length }} subjects</small>
        <span v-if="selectedFor(category)" class="card-selected">{{ selectedFor(category) }}</span>
      </button>
    </div>

    <p v-if="isAtLimit" class="limit-line">
      <i class="bi bi-info-circle-fill"></i>
      {{ limitMessage }}
    </p>

    <div v-if="selectedSubjects.length" class="selection-tray">
      <span :class="{ 'tray-count-full': isAtLimit }">
        Selected {{ modelValue.length }}<span v-if="maxSelection">/{{ maxSelection }}</span>
      </span>
      <button
        v-for="subject in selectedSubjects"
        :key="subject.subject_code"
        type="button"
        class="subject-chip selected"
        @click="toggle(subject.subject_code)"
      >
        {{ subject.subject_name }} &times;
      </button>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import {
  categoryClass,
  highlightSegments,
  searchSubjects,
  subjectCategories,
} from '@/components/subjectPicker.shared'

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

// At the cap, adding is refused. Surfaced as a disabled state on every unselected option rather
// than left as a silent no-op, so the picker explains itself instead of appearing broken.
const isAtLimit = computed(
  () => Boolean(props.maxSelection) && props.modelValue.length >= props.maxSelection,
)
const isBlocked = (code) => isAtLimit.value && !props.modelValue.includes(code)
const limitMessage = computed(
  () => `You've reached the ${props.maxSelection}-subject limit. Remove one to add another.`,
)

function toggle(code) { if (props.modelValue.includes(code)) emit('update:modelValue', props.modelValue.filter((value) => value !== code)); else if (!props.maxSelection || props.modelValue.length < props.maxSelection) emit('update:modelValue', [...props.modelValue, code]) }

const searchPlaceholder = computed(() =>
  activeCategory.value ? `Search in ${activeCategory.value}` : 'Search subjects',
)

const searchResults = computed(() => searchSubjects(props.subjects, searchQuery.value))

// Search inside a focused category stays scoped to it; matches elsewhere are offered as a hint.
const scopedResults = computed(() =>
  activeCategory.value
    ? searchResults.value.filter((subject) => subject.category === activeCategory.value)
    : searchResults.value,
)
const outsideMatchCount = computed(() =>
  activeCategory.value ? searchResults.value.length - scopedResults.value.length : 0,
)

// Categories containing at least one match, in catalog order, for the top-level jump band.
const matchedCategories = computed(() => {
  const counts = new Map()
  searchResults.value.forEach((subject) => counts.set(subject.category, (counts.get(subject.category) || 0) + 1))
  return categories.value
    .filter((category) => counts.has(category))
    .map((category) => ({ category, count: counts.get(category) }))
})

const countLine = computed(() => {
  if (!activeCategory.value) return ''
  const total = subjectsFor(activeCategory.value).length
  if (searchQuery.value) return `${scopedResults.value.length} of ${total} match “${searchQuery.value}”`
  const selected = selectedFor(activeCategory.value)
  return `${total} subjects${selected ? ` · ${selected} selected` : ''}`
})
</script>

<style scoped>
.taxonomy-picker { --cat: var(--sb-primary); }
.search-wrap { position: relative; margin-bottom: 14px; }
.search-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--sb-text-muted); font-size: .82rem; line-height: 1; }
.search-input { width: 100%; padding: 10px 32px 10px 34px; border: 1.5px solid var(--sb-card-border); border-radius: 10px; font-size: .9rem; background: var(--sb-bg); color: var(--sb-text-main); font-family: inherit; box-sizing: border-box; }
.search-input:focus { border-color: var(--sb-primary); background: var(--sb-card-bg); outline: none; }
.search-clear { position: absolute; right: 9px; top: 50%; transform: translateY(-50%); border: 0; background: transparent; color: var(--sb-text-muted); font-size: .8rem; line-height: 1; padding: 4px; }

/* Focused-category header. The back control is a bordered pill so it never reads as a heading. */
.back-pill { display: inline-flex; align-items: center; gap: 7px; border: 1px solid var(--sb-card-border); background: var(--sb-card-bg); color: var(--sb-text-main); border-radius: 999px; padding: 7px 14px 7px 11px; font-size: .8rem; font-weight: 600; font-family: inherit; }
.back-pill:hover { border-color: var(--sb-primary); color: var(--sb-primary); }
.head-rule { height: 1px; background: var(--sb-card-border); margin: 12px 0 14px; }
.category-title { display: flex; align-items: center; gap: 9px; font-size: 1rem; font-weight: 750; color: var(--sb-text-main); margin: 0 0 4px; }
.category-dot { width: 9px; height: 9px; border-radius: 50%; background: var(--cat); flex: none; }
.category-title .category-dot { width: 10px; height: 10px; }
.count-line { display: block; font-size: .75rem; color: var(--sb-text-muted); margin-bottom: 13px; }
.section-label { font-size: .68rem; text-transform: uppercase; letter-spacing: .06em; font-weight: 700; color: var(--sb-text-muted); margin: 0 0 8px; }

/* Category grid */
.category-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.jump-grid { margin-bottom: 16px; }
.category-card { position: relative; overflow: hidden; min-height: 112px; padding: 16px; text-align: left; border: 1px solid color-mix(in srgb, var(--cat) 30%, var(--sb-card-border)); border-radius: 16px; background: linear-gradient(135deg, color-mix(in srgb, var(--cat) 12%, var(--sb-card-bg)), var(--sb-card-bg) 65%); color: var(--sb-text-main); }
.category-card:hover { border-color: var(--cat); }
.category-card strong, .category-card small { display: block; position: relative; }
.category-card strong { font-size: .86rem; }
.category-card small { font-size: .72rem; color: var(--sb-text-muted); margin-top: 4px; }
.monogram { position: absolute; right: -8px; bottom: -35px; font: 700 6rem Georgia, serif; line-height: 1; color: color-mix(in srgb, var(--cat) 20%, transparent); }
/* Search band reuses the card language at a lower weight so results stay the focus. */
.category-card.compact { min-height: 0; padding: 12px 14px; border-radius: 13px; }
.category-card.compact strong { font-size: .81rem; }
.card-hit { color: var(--sb-primary) !important; font-weight: 700; }
.card-selected { position: absolute; top: 11px; right: 11px; z-index: 2; font-size: .64rem; font-weight: 700; background: var(--sb-primary); color: var(--sb-primary-contrast); border-radius: 999px; padding: 1px 7px; }

/* Chips: browsing. No per-chip category dot -- the heading already declares the category. */
.chips { margin-top: 2px; }
.subject-chip { display: inline-flex; align-items: center; gap: 6px; border: 1px solid var(--sb-card-border); background: var(--sb-card-bg); color: var(--sb-text-main); border-radius: 999px; padding: 7px 13px; margin: 0 7px 8px 0; font-size: .84rem; }
.subject-chip:hover { border-color: var(--sb-primary); }
.subject-chip.selected { border-color: var(--sb-primary); background: var(--sb-primary-light); font-weight: 650; }
.subject-chip.selected::before { content: "\2713"; color: var(--sb-primary); font-weight: 800; font-size: .78rem; }

/* Rows: searching. Kept descriptive so near-identical subject names stay distinguishable. */
.result-rows { border: 1px solid var(--sb-card-border); border-radius: 12px; overflow: hidden; }
.result-row { width: 100%; display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; padding: 11px 14px; border: 0; border-bottom: 1px solid var(--sb-card-border); background: var(--sb-card-bg); color: var(--sb-text-main); text-align: left; }
.result-row:last-child { border-bottom: 0; }
.result-row:hover { background: color-mix(in srgb, var(--sb-primary) 6%, var(--sb-card-bg)); }
.result-row.selected { background: color-mix(in srgb, var(--sb-primary) 10%, var(--sb-card-bg)); }
.result-row .left { display: flex; flex-direction: column; gap: 2px; }
.result-row .name { font-weight: 680; font-size: .87rem; }
.result-row .meta { display: flex; align-items: center; gap: 6px; font-size: .73rem; color: var(--sb-text-muted); }
.result-row .desc { font-size: .74rem; color: var(--sb-text-muted); line-height: 1.4; }
.result-row .check { color: var(--sb-primary); font-weight: 750; font-size: .78rem; white-space: nowrap; }

.empty-state { padding: 22px 16px; text-align: center; border: 1px solid var(--sb-card-border); border-radius: 12px; }
.empty-state p { color: var(--sb-text-muted); font-size: .85rem; margin: 0 0 10px; }
.propose-cta { border: 0; background: transparent; color: var(--sb-primary); font-weight: 700; font-size: .85rem; }
.hint-line { font-size: .77rem; color: var(--sb-text-muted); margin: 12px 0 0; }
.hint-link { border: 0; background: transparent; color: var(--sb-primary); font-weight: 650; font-size: .77rem; padding: 0; font-family: inherit; }
.hint-link:hover { text-decoration: underline; }

.selection-tray { border-top: 1px dashed var(--sb-border-light); margin-top: 16px; padding-top: 12px; }
.selection-tray > span { font-size: .8rem; color: var(--sb-text-muted); margin-right: 8px; }
.tray-count-full { color: var(--sb-primary); font-weight: 700; }

/* A blocked option is still readable -- it is a subject the tutor could pick after freeing a
   slot, not an invalid one. */
.subject-chip.blocked, .result-row.blocked { opacity: .45; cursor: not-allowed; }
.limit-line {
  display: flex; align-items: center; gap: .5rem;
  margin: 12px 0 0; padding: .55rem .8rem; border-radius: 12px;
  border: 1px solid color-mix(in srgb, var(--sb-primary) 30%, transparent);
  background: color-mix(in srgb, var(--sb-primary) 8%, transparent);
  font-size: .82rem; color: var(--sb-text-main);
}

.cat-math { --cat: var(--sb-primary); }.cat-science { --cat: var(--sb-secondary-blue); }.cat-tech { --cat: var(--sb-aurora-violet); }.cat-business { --cat: var(--sb-pop-yellow-deep); }.cat-humanities { --cat: var(--sb-pop-orange-deep); }.cat-arts { --cat: var(--sb-pop-pink-deep); }
@media (max-width: 640px) { .category-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
</style>
