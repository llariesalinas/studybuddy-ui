<template>
  <Teleport to="body">
    <div v-if="open && activeSession" class="rating-stack-shell" @click.self="emit('close')">
      <div
        class="rating-stack-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="rating-stack-title"
      >
        <div class="rating-stack-header">
          <div>
            <p class="rating-stack-eyebrow">Unrated Sessions</p>
            <h5 id="rating-stack-title" class="rating-stack-title">Rate Your Recent Sessions</h5>
          </div>
          <button
            type="button"
            class="rating-stack-close"
            aria-label="Close popup"
            @click="emit('close')"
          >
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <div class="rating-stack-progress">
          <span class="rating-stack-badge">
            <i class="bi bi-exclamation-diamond-fill"></i>
            Unrated
          </span>
          <span class="rating-stack-count">{{ activeIndex + 1 }} of {{ sessions.length }}</span>
        </div>

        <div class="rating-stack-card">
          <div class="rating-stack-meta">
            <div>
              <div class="rating-stack-subject">{{ activeSession.subject || 'Session' }}</div>
              <div class="rating-stack-tutor">{{ activeSession.tutor || 'Tutor' }}</div>
            </div>
            <div class="rating-stack-schedule">
              <div>{{ activeSession.date || 'N/A' }}</div>
              <div>{{ activeSession.startTime }} - {{ activeSession.endTime }}</div>
            </div>
          </div>

          <p class="rating-stack-copy">
            How was your experience with <strong>{{ activeSession.tutor || 'your tutor' }}</strong>?
          </p>

          <div class="rating-sections">
            <div v-for="cat in ratingCategories" :key="cat.id" class="rating-category-item">
              <div class="rating-stars">
                <button
                  v-for="star in 5"
                  :key="star"
                  type="button"
                  class="rating-star-btn-sm sb-btn"
                  :class="{ active: ratings[cat.id] >= star }"
                  @click="ratings[cat.id] = star"
                >
                  <i class="bi" :class="ratings[cat.id] >= star ? 'bi-star-fill' : 'bi-star'"></i>
                </button>
              </div>
              <span class="rating-category-label" :class="{ 'text-dark': ratings[cat.id] > 0 }">
                {{ cat.label }}
              </span>
            </div>
          </div>

          <textarea
            v-model="ratingComment"
            class="form-control rating-stack-textarea"
            rows="2"
            placeholder="Additional feedback (optional)..."
          ></textarea>
        </div>

        <div class="rating-stack-footer">
          <button
            type="button"
            class="btn btn-light sb-btn"
            :disabled="activeIndex === 0"
            @click="goToPrevious"
          >
            Previous
          </button>

          <div class="rating-stack-actions">
            <button type="button" class="btn btn-outline-secondary sb-btn" @click="goToNextOrClose">
              Skip
            </button>
            <button
              type="button"
              class="btn bg-sb-primary text-white sb-btn"
              :disabled="!isFormValid || isSubmitting"
              @click="submitRating"
            >
              {{ isSubmitting ? 'Submitting...' : 'Submit Rating' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, nextTick, ref, watch, onUnmounted } from 'vue'
import { useSessionsStore } from '@/stores/completedSessions'
import { useToastStore } from '@/stores/toast'

const props = defineProps({
  open: { type: Boolean, default: false },
  sessions: { type: Array, default: () => [] },
  initialSessionId: { type: [String, Number], default: null }
})

const emit = defineEmits(['close', 'rated'])
const sessionsStore = useSessionsStore()
const toastStore = useToastStore()

const activeIndex = ref(0)
const ratingComment = ref('')
const isSubmitting = ref(false)

const ratingCategories = [
  { id: 'preparation', label: 'Preparation' },
  { id: 'clarity', label: 'Clarity' },
  { id: 'punctuality', label: 'Punctuality' },
  { id: 'overall', label: 'Overall Experience'}
]

const ratings = ref(
  ratingCategories.reduce((acc, cat) => ({ ...acc, [cat.id]: 0 }), {})
)

const activeSession = computed(() => props.sessions[activeIndex.value] || null)

const isFormValid = computed(() => {
  return ratingCategories.every(cat => ratings.value[cat.id] > 0)
})

const resetDraft = () => {
  Object.keys(ratings.value).forEach(key => (ratings.value[key] = 0))
  ratingComment.value = ''
}

const setInitialIndex = () => {
  if (!props.sessions.length) return
  if (props.initialSessionId != null) {
    const idx = props.sessions.findIndex(s => String(s.id) === String(props.initialSessionId))
    activeIndex.value = idx >= 0 ? idx : 0
  } else {
    activeIndex.value = 0
  }
}

const goToPrevious = () => {
  if (activeIndex.value > 0) {
    activeIndex.value--
    resetDraft()
  }
}

const goToNextOrClose = () => {
  if (activeIndex.value < props.sessions.length - 1) {
    activeIndex.value++
    resetDraft()
  } else {
    emit('close')
  }
}

const submitRating = async () => {
  if (!activeSession.value || !isFormValid.value) return
  isSubmitting.value = true

  try {
    await sessionsStore.submitRating(
      activeSession.value.id,
      { ...ratings.value },
      ratingComment.value
    )

    emit('rated', activeSession.value.id)
    resetDraft()
    await nextTick()

    if (!props.sessions.length || activeIndex.value >= props.sessions.length) {
      emit('close')
    }
  } catch (error) {
    console.error('Failed to submit rating:', error)
    toastStore.push('Failed to submit rating.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

watch(
  () => [props.open, props.initialSessionId, props.sessions.length],
  ([open]) => {
    if (!open) {
      document.body.style.overflow = '' 
      resetDraft()
      return
    }
    
    document.body.style.overflow = 'hidden' 
    setInitialIndex()
    resetDraft()
  },
  { immediate: true }
)

onUnmounted(() => {
  document.body.style.overflow = ''
})
</script>

<style scoped>
.rating-stack-shell {
  position: fixed;
  inset: 0;
  z-index: 1100;
  background: rgba(10, 25, 22, 0.5);
  display: grid;
  place-items: center;
  padding: 20px;
}

.rating-stack-modal {
  width: min(100%, 540px);
  max-height: 98vh; 
  overflow-y: auto;
  background: #ffffff;
  border-radius: 24px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.rating-stack-header { display: flex; justify-content: space-between; align-items: flex-start; }
.rating-stack-close { 
  width: 36px; height: 36px; border: 0; border-radius: 50%; 
  background: #f4f6f8; color: #667085; transition: 0.2s;
}
.rating-stack-close:hover { background: #e4e7ec; color: #101828; }
.rating-stack-eyebrow { font-size: 11px; font-weight: 800; color: #b42318; text-transform: uppercase; margin-bottom: 4px; letter-spacing: 0.5px; }
.rating-stack-title { font-weight: 700; color: #101828; margin: 0; }

.rating-stack-progress { display: flex; justify-content: space-between; align-items: center; }
.rating-stack-badge { background: #fef3f2; color: #b42318; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 700; display: flex; gap: 6px; }
.rating-stack-count { font-size: 13px; font-weight: 600; color: #667085; }

.rating-stack-card { 
  background: linear-gradient(180deg, #fffaf9 0%, #ffffff 100%);
  border: 1px solid #f2f4f7; border-radius: 20px; padding: 20px;
}
.rating-stack-meta { display: flex; justify-content: space-between; margin-bottom: 16px; border-bottom: 1px solid #f2f4f7; padding-bottom: 12px; }
.rating-stack-subject { font-weight: 700; color: #101828; font-size: 16px; }
.rating-stack-tutor { color: #667085; font-size: 14px; }
.rating-stack-schedule { text-align: right; color: #667085; font-size: 12px; font-weight: 500; }

.rating-stack-copy { font-size: 14px; color: #475467; text-align: center; margin-bottom: 16px; }

.rating-sections {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px 12px;
  margin-bottom: 20px;
}

.rating-category-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.rating-stars { display: flex; gap: 6px; }

.rating-star-btn-sm {
  width: 36px;
  height: 36px;
  border: 0;
  border-radius: 50%; 
  background: #f4f6f8;
  color: #8c9bb0;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.1s ease, color 0.2s;
  cursor: pointer;
}

.rating-star-btn-sm:hover { transform: scale(1.1); }
.rating-star-btn-sm.active { color: #fdb022; }

.rating-category-label {
  font-size: 12px; font-weight: bold; color: #98a2b3;
  transition: color 0.2s;
}

.text-dark { color: #344054 !important; }

.rating-stack-textarea { 
  border-radius: 12px; border: 1px solid #d0d5dd; font-size: 14px; 
}

.rating-stack-footer { display: flex; justify-content: space-between; align-items: center; padding-top: 8px; }
.rating-stack-actions { display: flex; gap: 10px; }

.btn { font-weight: 600; border-radius: 10px; padding: 8px 16px; }

@media (max-width: 480px) {
  .rating-sections { grid-template-columns: 1fr; }
  .rating-stack-footer { flex-direction: column; gap: 12px; }
  .rating-stack-actions { width: 100%; }
  .rating-stack-actions .btn { flex: 1; }
  .rating-stack-footer > .btn { width: 100%; order: 2; }
}
</style>
