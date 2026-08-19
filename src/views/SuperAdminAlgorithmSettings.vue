<script setup>
// Admin-tunable recommender weights. Values are raw and relative: the backend
// normalises each group at score time, so the percentage shown here is derived,
// never stored. See docs/plans/2026-08-19-dynamic-algorithm-weights.md and the
// chosen design at docs/mockups/2026-08-19-dynamic-algorithm-weights.html.
import { computed, onMounted, ref, watch } from 'vue'
import SbSelectModal from '@/components/SbSelectModal.vue'
import {
  getAlgorithmWeights,
  previewAlgorithmWeights,
  updateAlgorithmWeights
} from '@/services/api/algorithmWeights'
import { searchAlgorithmDemoTutees } from '@/services/api/algorithmDemo'

// Coarse enough to land on defensible round numbers, fine enough to express a
// real change. Sliders are in whole percent; the backend stores the raw value.
const SLIDER_STEP = 5
const SLIDER_MAX = 100
const HYBRID_GROUP = 'hybrid'
const PREVIEW_DEBOUNCE_MS = 350
// Narrower than this and the segment cannot hold its own label legibly.
const MIN_LABELLED_SHARE = 0.09

// The stacked bar is one quantity split up, not six unrelated categories, so the
// segments are a single-hue ramp mixed from the brand token rather than six
// hand-picked colours. Mixing keeps every shade derived from --sb-primary, so a
// brand change carries through and no hex literal is needed.
const SEGMENT_MIX_START = 100
const SEGMENT_MIX_STEP = 13
// Below this mix the segment is pale enough that dark text reads better on it.
const SEGMENT_DARK_TEXT_BELOW_MIX = 60

const groups = ref([])
const saved = ref({})
const previewEnabled = ref(false)
const loading = ref(true)
const saving = ref(false)
const errorMessage = ref('')

const tutees = ref([])
const selectedTuteeId = ref('')
const previewRows = ref([])
const previewLoading = ref(false)
const previewMessage = ref('')
const baselineOrder = ref([])

let previewTimer = null

const tuteeOptions = computed(() =>
  tutees.value.map((tutee) => ({
    value: tutee.id,
    label: tutee.name
  }))
)

const isDirty = computed(() =>
  groups.value.some((group) =>
    group.weights.some((weight) => weight.value !== saved.value[`${group.group}.${weight.key}`])
  )
)

function groupTotal(group) {
  return group.weights.reduce((sum, entry) => sum + entry.value, 0)
}

// Mirrors the server's normalize_group so the bar and the percentages track the
// sliders without a round trip. The server remains authoritative: what it
// returns after a save replaces whatever was shown here.
function shareOf(group, weight) {
  const total = groupTotal(group)
  return total > 0 ? weight.value / total : 0
}

function asPercent(value) {
  return `${Math.round(value * 100)}%`
}

function rawTotal(group) {
  return groupTotal(group).toFixed(2)
}

function segmentMix(index) {
  return Math.max(SEGMENT_MIX_START - index * SEGMENT_MIX_STEP, SEGMENT_MIX_STEP)
}

function segmentColor(index) {
  return `color-mix(in srgb, var(--sb-primary) ${segmentMix(index)}%, var(--sb-primary-contrast))`
}

function segmentTextColor(index) {
  return segmentMix(index) < SEGMENT_DARK_TEXT_BELOW_MIX
    ? 'var(--sb-text-main)'
    : 'var(--sb-primary-contrast)'
}

// The hybrid blend has exactly two members, so one handle says it all: moving it
// sets both sides. Any other group gets a slider per member.
function isBlend(group) {
  return group.group === HYBRID_GROUP && group.weights.length === 2
}

function onBlendInput(group, percent) {
  const value = Number(percent)
  group.weights[0].value = value / SLIDER_MAX
  group.weights[1].value = (SLIDER_MAX - value) / SLIDER_MAX
  schedulePreview()
}

function onWeightInput(weight, percent) {
  weight.value = Number(percent) / SLIDER_MAX
  schedulePreview()
}

function resetGroup(group) {
  group.weights.forEach((weight) => {
    weight.value = weight.default
  })
  schedulePreview()
}

function applyResponse(data) {
  groups.value = data.groups.map((group) => ({
    ...group,
    weights: group.weights.map((weight) => ({ ...weight }))
  }))
  previewEnabled.value = data.preview_enabled
  saved.value = {}
  groups.value.forEach((group) => {
    group.weights.forEach((weight) => {
      saved.value[`${group.group}.${weight.key}`] = weight.value
    })
  })
}

function pendingGroups() {
  return groups.value.reduce((payload, group) => {
    payload[group.group] = group.weights.reduce((entries, weight) => {
      entries[weight.key] = weight.value
      return entries
    }, {})
    return payload
  }, {})
}

function savedGroups() {
  return groups.value.reduce((payload, group) => {
    payload[group.group] = group.weights.reduce((entries, weight) => {
      entries[weight.key] = saved.value[`${group.group}.${weight.key}`]
      return entries
    }, {})
    return payload
  }, {})
}

async function loadPreview() {
  if (!previewEnabled.value || !selectedTuteeId.value) return

  previewLoading.value = true
  previewMessage.value = ''

  try {
    const { data } = await previewAlgorithmWeights(selectedTuteeId.value, pendingGroups())
    previewRows.value = data.rows || []

    if (!previewRows.value.length) {
      previewMessage.value =
        data.reason === 'no_preferences'
          ? 'This tutee has no subject preferences yet, so there is nothing to rank.'
          : 'No candidate tutors match this tutee.'
    }

  } catch {
    previewMessage.value = 'Could not run the preview.'
  } finally {
    previewLoading.value = false
  }
}

// The movement markers answer "what would saving this change?", so the baseline
// is the ranking under the SAVED weights - not under whatever is on the sliders
// when a tutee happens to be picked. Loading it separately keeps that true even
// if the admin drags first and chooses a tutee second.
async function loadBaseline() {
  if (!previewEnabled.value || !selectedTuteeId.value) return

  try {
    const { data } = await previewAlgorithmWeights(selectedTuteeId.value, savedGroups())
    baselineOrder.value = (data.rows || []).map((row) => row.tutor_id)
  } catch {
    baselineOrder.value = []
  }
}

function schedulePreview() {
  if (!previewEnabled.value) return
  clearTimeout(previewTimer)
  previewTimer = setTimeout(loadPreview, PREVIEW_DEBOUNCE_MS)
}

// How far a tutor moved from where it sat when this tutee was first previewed,
// so the effect of a weight change is visible rather than merely implied.
function movement(row, index) {
  const was = baselineOrder.value.indexOf(row.tutor_id)
  return was === -1 ? 0 : was - index
}

async function save() {
  saving.value = true
  errorMessage.value = ''

  try {
    const { data } = await updateAlgorithmWeights(pendingGroups())
    applyResponse(data)
    await loadBaseline()
  } catch (err) {
    errorMessage.value = err.response?.data?.error || 'Could not save the weights.'
  } finally {
    saving.value = false
  }
}

watch(selectedTuteeId, async () => {
  baselineOrder.value = []
  previewRows.value = []
  await loadBaseline()
  loadPreview()
})

onMounted(async () => {
  try {
    const { data } = await getAlgorithmWeights()
    applyResponse(data)

    if (previewEnabled.value) {
      const response = await searchAlgorithmDemoTutees('')
      tutees.value = response.data.tutees
    }
  } catch {
    errorMessage.value = 'Could not load the algorithm weights.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="algorithm-settings-page">
    <p class="eyebrow">Recommender</p>
    <h1>Algorithm Settings</h1>
    <p class="subtitle">
      Tune how tutor recommendations are ranked. Changes apply to every recommendation
      platform-wide once saved.
    </p>

    <p v-if="loading" class="empty-state">Loading…</p>

    <template v-else>
      <p v-if="errorMessage" class="error-banner">{{ errorMessage }}</p>

      <section v-for="group in groups" :key="group.group" class="sb-card group-card">
        <h2>{{ group.label }}</h2>
        <p class="group-help">{{ group.description }}</p>

        <div class="stack-bar">
          <div
            v-for="(weight, index) in group.weights"
            :key="weight.key"
            class="stack-segment"
            :style="{
              width: `${shareOf(group, weight) * 100}%`,
              background: segmentColor(index),
              color: segmentTextColor(index)
            }"
          >
            <span v-if="shareOf(group, weight) > MIN_LABELLED_SHARE">
              {{ weight.label }} {{ asPercent(shareOf(group, weight)) }}
            </span>
          </div>
        </div>

        <!-- Two-member group: one handle sets both sides. -->
        <div v-if="isBlend(group)" class="blend">
          <input
            class="weight-slider"
            type="range"
            min="0"
            :max="SLIDER_MAX"
            :step="SLIDER_STEP"
            :value="Math.round(shareOf(group, group.weights[0]) * SLIDER_MAX)"
            :aria-label="`${group.weights[0].label} share`"
            @input="onBlendInput(group, $event.target.value)"
          />
          <div class="blend-ends">
            <span>All {{ group.weights[1].label.toLowerCase() }}</span>
            <span>All {{ group.weights[0].label.toLowerCase() }}</span>
          </div>
          <div class="blend-readout">
            <div v-for="weight in group.weights" :key="weight.key">
              <span class="readout-key">{{ weight.label }}</span>
              <span class="readout-value">{{ shareOf(group, weight).toFixed(2) }}</span>
            </div>
          </div>
        </div>

        <div v-else class="weight-rows">
          <div v-for="weight in group.weights" :key="weight.key" class="weight-row">
            <div class="weight-name">
              {{ weight.label }}
              <small>{{ weight.description }}</small>
            </div>
            <input
              class="weight-slider"
              type="range"
              min="0"
              :max="SLIDER_MAX"
              :step="SLIDER_STEP"
              :value="Math.round(weight.value * SLIDER_MAX)"
              :aria-label="`${weight.label} weight`"
              @input="onWeightInput(weight, $event.target.value)"
            />
            <div class="weight-share">
              {{ asPercent(shareOf(group, weight)) }}
              <small>share</small>
            </div>
          </div>
        </div>

        <div class="group-footer">
          <span>
            Raw total <strong>{{ rawTotal(group) }}</strong> — normalised to 100% at score time
          </span>
          <button type="button" class="reset-btn" @click="resetGroup(group)">
            Reset to defaults
          </button>
        </div>
      </section>

      <section class="sb-card group-card">
        <h2>Preview</h2>
        <p class="group-help">
          Recomputed from both groups above. Nothing is saved until you press Save.
        </p>

        <div class="preview-split">
          <div>
            <template v-if="previewEnabled">
              <label class="field-label">Preview against tutee</label>
              <SbSelectModal
                v-model="selectedTuteeId"
                :options="tuteeOptions"
                title="Select tutee"
                placeholder="Choose a tutee"
                searchable
              />
            </template>
            <p v-else class="gated-note">
              The ranked preview is part of the staff algorithm tools and is switched off on this
              backend. The weight controls above still apply platform-wide.
            </p>
          </div>

          <div>
            <label class="field-label">Ranked tutors</label>
            <p v-if="previewLoading" class="empty-state small">Scoring…</p>
            <p v-else-if="previewMessage" class="empty-state small">{{ previewMessage }}</p>
            <p v-else-if="!previewRows.length" class="empty-state small">
              Select a tutee to see how these weights rank their tutors.
            </p>
            <ul v-else class="rank-list">
              <li
                v-for="(row, index) in previewRows"
                :key="row.tutor_id"
                :class="{ moved: movement(row, index) !== 0 }"
              >
                <span class="rank-pos">{{ index + 1 }}</span>
                <span class="rank-name">{{ row.name }}</span>
                <span class="rank-score">{{ row.hybrid_score.toFixed(3) }}</span>
                <span
                  class="rank-delta"
                  :class="{
                    up: movement(row, index) > 0,
                    down: movement(row, index) < 0
                  }"
                >
                  {{
                    movement(row, index) > 0
                      ? `+${movement(row, index)}`
                      : movement(row, index) < 0
                        ? movement(row, index)
                        : '–'
                  }}
                </span>
              </li>
            </ul>
          </div>
        </div>

        <div class="save-footer">
          <span class="audit">
            <template v-for="group in groups" :key="group.group">
              <template v-if="group.updated_by">
                {{ group.label }} last changed by {{ group.updated_by }}.
              </template>
            </template>
          </span>
          <div class="save-actions">
            <span v-if="isDirty" class="unsaved">Unsaved changes</span>
            <button
              type="button"
              class="sb-btn-pill"
              :disabled="!isDirty || saving"
              @click="save"
            >
              {{ saving ? 'Saving…' : 'Save' }}
            </button>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.algorithm-settings-page {
  max-width: 1180px;
  margin: 0 auto;
  padding: 24px;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 11px;
  font-weight: 700;
  color: var(--sb-primary);
  margin: 0 0 4px;
}

h1 {
  font-size: 24px;
  margin: 0 0 4px;
  font-weight: 700;
}

.subtitle {
  color: var(--sb-text-muted);
  font-size: 13px;
  margin: 0 0 20px;
}

.error-banner {
  background: color-mix(in srgb, var(--sb-warning-bg) 14%, var(--sb-card-bg));
  border: 1px solid color-mix(in srgb, var(--sb-warning-bg) 42%, var(--sb-card-bg));
  color: var(--sb-warning-text);
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 13px;
  margin-bottom: 16px;
}

.sb-card {
  background: var(--sb-card-bg);
  border: 1px solid var(--sb-card-border);
  border-radius: 18px;
  padding: 28px;
}

.group-card {
  margin-bottom: 20px;
}

.group-card h2 {
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 3px;
}

.group-help {
  font-size: 12px;
  color: var(--sb-text-muted);
  margin: 0 0 16px;
}

.stack-bar {
  display: flex;
  height: 32px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--sb-card-border);
  margin-bottom: 14px;
}

.stack-segment {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  transition: width 0.12s ease;
}

.weight-slider {
  width: 100%;
  accent-color: var(--sb-primary);
}

.blend-ends {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--sb-text-muted);
  margin: 4px 0 14px;
}

.blend-readout {
  display: flex;
  gap: 26px;
}

.readout-key {
  display: block;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--sb-text-muted);
  font-weight: 700;
}

.readout-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: var(--sb-primary);
}

.weight-row {
  display: grid;
  grid-template-columns: 150px 1fr 78px;
  align-items: center;
  gap: 12px;
  padding: 7px 0;
  border-bottom: 1px solid var(--sb-card-border);
}

.weight-row:last-child {
  border-bottom: none;
}

.weight-name {
  font-size: 13px;
  font-weight: 600;
}

.weight-name small {
  display: block;
  font-weight: 400;
  color: var(--sb-text-muted);
  font-size: 11px;
}

.weight-share {
  text-align: right;
  font-variant-numeric: tabular-nums;
  font-weight: 700;
  font-size: 15px;
  color: var(--sb-primary);
}

.weight-share small {
  display: block;
  font-weight: 600;
  color: var(--sb-text-muted);
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.group-footer,
.save-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  border-top: 1px solid var(--sb-card-border);
  margin-top: 14px;
  padding-top: 13px;
  font-size: 12px;
  color: var(--sb-text-muted);
}

/* The documented filled pill (.claude/skills/shadcn-components.md). */
.sb-btn-pill {
  background: var(--sb-primary);
  color: var(--sb-primary-contrast);
  padding: 11px 28px;
  border-radius: 9999px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  transition:
    background 0.15s ease,
    transform 0.15s ease;
  cursor: pointer;
}

.sb-btn-pill:hover:not(:disabled) {
  background: var(--sb-primary-hover);
}

.sb-btn-pill:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

/* Secondary, per-group action: deliberately not a pill, so the single filled
   pill on the page is unambiguously Save. */
.reset-btn {
  border-radius: 9999px;
  border: 1px solid var(--sb-card-border);
  background: transparent;
  color: var(--sb-text-muted);
  font-size: 13px;
  font-weight: 600;
  padding: 8px 18px;
  cursor: pointer;
}

.preview-split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 22px;
}

@media (max-width: 860px) {
  .preview-split {
    grid-template-columns: 1fr;
  }

  .weight-row {
    grid-template-columns: 120px 1fr 66px;
  }
}

.field-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--sb-text-muted);
  margin-bottom: 6px;
}

.gated-note {
  font-size: 12px;
  color: var(--sb-text-muted);
  background: var(--sb-card-border);
  border-radius: 9px;
  padding: 12px 14px;
  margin: 0;
}

.rank-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.rank-list li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border: 1px solid var(--sb-card-border);
  border-radius: 9px;
  margin-bottom: 6px;
  font-size: 13px;
}

.rank-list li.moved {
  border-color: var(--sb-primary);
}

.rank-pos {
  width: 21px;
  height: 21px;
  border-radius: 50%;
  background: var(--sb-card-border);
  color: var(--sb-text-muted);
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex: none;
}

.rank-name {
  flex: 1;
  font-weight: 600;
}

.rank-score {
  font-variant-numeric: tabular-nums;
  color: var(--sb-text-muted);
  font-size: 12px;
}

.rank-delta {
  width: 30px;
  text-align: right;
  font-size: 11px;
  font-weight: 700;
  color: var(--sb-text-muted);
}

.rank-delta.up {
  color: var(--sb-primary);
}

.rank-delta.down {
  color: var(--sb-danger);
}

.save-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.unsaved {
  font-size: 12px;
  font-weight: 700;
  color: var(--sb-warning-text);
}

.empty-state {
  color: var(--sb-text-muted);
  font-size: 14px;
  text-align: center;
  padding: 60px 0;
}

.empty-state.small {
  padding: 20px 0;
  font-size: 13px;
}
</style>
