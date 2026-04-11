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
            How was your session with {{ activeSession.tutor || 'your tutor' }}?
          </p>

          <div class="rating-stars">
            <button
              v-for="star in 5"
              :key="star"
              type="button"
              class="rating-star-btn"
              :class="{ active: currentRating >= star }"
              @click="currentRating = star"
            >
              <i class="bi" :class="currentRating >= star ? 'bi-star-fill' : 'bi-star'"></i>
            </button>
          </div>

          <textarea
            v-model="ratingComment"
            class="form-control rating-stack-textarea"
            rows="3"
            placeholder="Add an optional comment"
          ></textarea>
        </div>

        <div class="rating-stack-footer">
          <button
            type="button"
            class="btn btn-light"
            :disabled="activeIndex === 0"
            @click="goToPrevious"
          >
            Newer
          </button>

          <div class="rating-stack-actions">
            <button type="button" class="btn btn-outline-secondary" @click="goToNextOrClose">
              Skip for Now
            </button>
            <button
              type="button"
              class="btn bg-sb-primary text-white"
              :disabled="currentRating === 0 || isSubmitting"
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
import { computed, nextTick, ref, watch } from 'vue'
import { useSessionsStore } from '@/stores/completedSessions'

const props = defineProps({
  open: {
    type: Boolean,
    default: false
  },
  sessions: {
    type: Array,
    default: () => []
  },
  initialSessionId: {
    type: [String, Number],
    default: null
  }
})

const emit = defineEmits(['close', 'rated'])

const sessionsStore = useSessionsStore()
const activeIndex = ref(0)
const currentRating = ref(0)
const ratingComment = ref('')
const isSubmitting = ref(false)

const activeSession = computed(() => props.sessions[activeIndex.value] || null)

const resetDraft = () => {
  currentRating.value = 0
  ratingComment.value = ''
}

const setInitialIndex = () => {
  if (!props.sessions.length) {
    activeIndex.value = 0
    return
  }

  if (props.initialSessionId != null) {
    const matchedIndex = props.sessions.findIndex(
      session => String(session.id) === String(props.initialSessionId)
    )

    activeIndex.value = matchedIndex >= 0 ? matchedIndex : 0
    return
  }

  activeIndex.value = 0
}

const goToPrevious = () => {
  if (activeIndex.value === 0) {
    return
  }

  activeIndex.value -= 1
  resetDraft()
}

const goToNextOrClose = () => {
  if (activeIndex.value < props.sessions.length - 1) {
    activeIndex.value += 1
    resetDraft()
    return
  }

  emit('close')
}

const submitRating = async () => {
  if (!activeSession.value || !currentRating.value) {
    return
  }

  isSubmitting.value = true

  try {
    await sessionsStore.submitRating(
      activeSession.value.id,
      currentRating.value,
      ratingComment.value
    )

    emit('rated', activeSession.value.id)
    resetDraft()

    await nextTick()

    if (!props.sessions.length) {
      emit('close')
      return
    }

    activeIndex.value = Math.min(activeIndex.value, props.sessions.length - 1)

    if (!props.sessions[activeIndex.value]) {
      emit('close')
    }
  } catch (error) {
    console.error('Failed to submit rating:', error)
    alert(error.response?.data?.error || 'Failed to submit rating.')
  } finally {
    isSubmitting.value = false
  }
}

watch(
  () => [props.open, props.initialSessionId, props.sessions.length],
  ([open]) => {
    if (!open) {
      resetDraft()
      return
    }

    setInitialIndex()
    resetDraft()
  },
  { immediate: true }
)
</script>

<style scoped>
.rating-stack-shell {
  position: fixed;
  inset: 0;
  z-index: 1100;
  background: rgba(10, 25, 22, 0.45);
  display: grid;
  place-items: center;
  padding: 24px;
}

.rating-stack-modal {
  width: min(100%, 620px);
  max-height: min(90vh, 760px);
  overflow: auto;
  background: #ffffff;
  border-radius: 28px;
  box-shadow: 0 24px 80px rgba(15, 23, 42, 0.22);
  padding: 24px;
  display: grid;
  gap: 20px;
}

.rating-stack-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  gap: 16px;
}

.rating-stack-close {
  width: 42px;
  height: 42px;
  border: 0;
  border-radius: 50%;
  background: #f4f6f5;
  color: #344054;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  transition: background-color 150ms ease, color 150ms ease, transform 150ms ease;
}

.rating-stack-close:hover {
  background: #e7ece9;
  color: #101828;
  transform: scale(1.03);
}

.rating-stack-eyebrow {
  margin: 0 0 4px;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #8c3a32;
  font-weight: 700;
}

.rating-stack-title {
  margin: 0;
  font-weight: 700;
  color: #18332a;
}

.rating-stack-progress {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.rating-stack-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  background: #fde8e5;
  color: #b42318;
  font-weight: 700;
}

.rating-stack-count {
  color: #667085;
  font-weight: 600;
}

.rating-stack-card {
  border-radius: 24px;
  padding: 20px;
  background:
    radial-gradient(circle at top right, rgba(180, 35, 24, 0.08), transparent 30%),
    linear-gradient(180deg, #fffaf9 0%, #ffffff 100%);
  border: 1px solid #f2ddda;
  display: grid;
  gap: 18px;
}

.rating-stack-meta {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.rating-stack-subject {
  font-size: 1.15rem;
  font-weight: 700;
  color: #18332a;
}

.rating-stack-tutor,
.rating-stack-schedule {
  color: #667085;
}

.rating-stack-schedule {
  text-align: right;
  font-weight: 600;
}

.rating-stack-copy {
  margin: 0;
  color: #475467;
}

.rating-stars {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.rating-star-btn {
  width: 56px;
  height: 56px;
  border: 0;
  border-radius: 50%;
  background: #f5f7f6;
  color: #98a2b3;
  font-size: 1.6rem;
  transition: transform 150ms ease, background-color 150ms ease, color 150ms ease;
}

.rating-star-btn:hover,
.rating-star-btn.active {
  background: #fff3d6;
  color: #f59e0b;
  transform: translateY(-2px);
}

.rating-stack-textarea {
  border-radius: 16px;
}

.rating-stack-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.rating-stack-actions {
  display: flex;
  gap: 12px;
}

@media (max-width: 640px) {
  .rating-stack-modal {
    padding: 20px;
  }

  .rating-stack-meta,
  .rating-stack-footer {
    flex-direction: column;
    align-items: stretch;
  }

  .rating-stack-schedule {
    text-align: left;
  }

  .rating-stack-actions {
    width: 100%;
    justify-content: stretch;
  }

  .rating-stack-actions .btn,
  .rating-stack-footer > .btn {
    width: 100%;
  }
}
</style>
