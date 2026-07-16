<template>
  <section class="taxonomy-picker">
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

const props = defineProps({
  subjects: { type: Array, required: true },
  modelValue: { type: Array, required: true },
  maxSelection: { type: Number, default: null },
})
const emit = defineEmits(['update:modelValue'])
const activeCategory = ref('')
const categories = computed(() => [...new Set(props.subjects.map((subject) => subject.category).filter(Boolean))])
const selectedSubjects = computed(() => props.subjects.filter((subject) => props.modelValue.includes(subject.subject_code)))
const subjectsFor = (category) => props.subjects.filter((subject) => subject.category === category)
const selectedFor = (category) => subjectsFor(category).filter((subject) => props.modelValue.includes(subject.subject_code)).length
const categoryClass = (category) => ({ 'cat-math': category === 'Mathematics & Data Sciences', 'cat-science': category === 'Natural Sciences', 'cat-tech': category === 'Technology & Computer Science', 'cat-business': category === 'Business, Finance & Economics', 'cat-humanities': category === 'Humanities & Social Sciences', 'cat-arts': category === 'Hobbies & Arts' })
function toggle(code) { if (props.modelValue.includes(code)) emit('update:modelValue', props.modelValue.filter((value) => value !== code)); else if (!props.maxSelection || props.modelValue.length < props.maxSelection) emit('update:modelValue', [...props.modelValue, code]) }
</script>

<style scoped>
.taxonomy-picker { --cat: var(--sb-primary); }
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
