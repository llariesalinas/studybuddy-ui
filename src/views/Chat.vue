<template>
  <div class="chat-shell">
    <aside class="chat-sidebar">
      <div class="sidebar-header">
        <div>
          <h3>Messages</h3>
          <p>{{ chatStore.totalUnread }} unread</p>
        </div>
        <span class="connection-pill" :class="{ online: chatStore.isUpdatesConnected }">
          {{ chatStore.isUpdatesConnected ? 'Live' : 'Syncing' }}
        </span>
      </div>

      <div class="room-list">
        <button
          v-for="room in chatStore.sortedRooms"
          :key="room.id"
          type="button"
          class="room-item sb-interactive"
          :class="{ active: chatStore.currentRoom?.id === room.id }"
          @click="selectRoom(room)"
        >
          <span class="room-avatar">{{ getRoomInitials(room) }}</span>
          <span class="room-info">
            <span class="room-title-row">
              <span class="room-name">{{ chatStore.getRoomPartnerName(room) }}</span>
              <span
                v-if="room.unread_count"
                class="unread-badge"
                :class="{ 'pulse-once': pulsingRooms.has(room.id) }"
              >
                {{ room.unread_count }}
              </span>
            </span>
            <span class="last-message">
              {{ formatLastMessage(room.last_message) }}
            </span>
            <span
              v-if="room.current_booking"
              class="room-session-badge badge rounded-pill"
              :class="getSidebarChipClass(room.current_booking.status_intent)"
            >
              {{ room.current_booking.status }}
            </span>
          </span>
        </button>

        <div v-if="!chatStore.rooms.length" class="empty-rooms">
          <i class="bi bi-chat-dots"></i>
          <p>No conversations yet</p>
        </div>
      </div>
    </aside>

    <section class="chat-main">
      <Transition name="room-switch" mode="out-in">
        <div :key="chatStore.currentRoom?.id ?? 'empty'" class="chat-main-inner">
          <template v-if="chatStore.currentRoom">
            <div class="chat-workspace">
              <div class="chat-conversation">
                <ChatBanner
                  v-if="chatStore.currentRoom.current_booking"
                  :banner-context="chatStore.currentRoom.current_booking"
                  :is-tutor="isTutor"
                  @location-saved="handleLocationSaved"
                  @rate="openRatingModal"
                />

                <div class="chat-card">
                  <div class="message-list" ref="messageList">
                    <TransitionGroup :name="historyLoaded ? 'msg' : ''" tag="div" class="messages-group">
                      <div
                        v-for="item in groupedMessages"
                        :key="item.type === 'date-separator' ? item.key : item.id"
                        :class="
                          item.type === 'date-separator'
                            ? 'date-separator-row'
                            : [
                                'message-wrapper',
                                {
                                  'is-me': item.is_me,
                                  'is-system': item.message_type !== 'text',
                                  'is-pending': item.status === 'pending' || item.pending === true,
                                  'is-failed': item.failed === true,
                                },
                              ]
                        "
                      >
                        <template v-if="item.type === 'date-separator'">
                          <span class="date-separator-label">{{ item.label }}</span>
                        </template>

                        <template v-else>
                          <div v-if="item.message_type === 'booking_event'" class="system-event">
                            <i class="bi bi-calendar-check"></i>
                            <div>
                              <strong>{{ item.content }}</strong>
                              <BookingCard
                                v-if="item.metadata?.booking"
                                :booking="item.metadata.booking"
                                :is-tutor="isTutor"
                                compact
                                @location-saved="handleLocationSaved"
                              />
                            </div>
                          </div>

                          <template v-else>
                            <div v-if="!item.is_me" class="message-avatar-sm">
                              {{ getInitials(item.sender_name) }}
                            </div>
                            <div class="message-bubble-col">
                              <div
                                class="message-bubble"
                                :class="{
                                  'sb-pop-active': poppingMessages.has(item.id),
                                  'is-failed': item.failed === true,
                                }"
                              >
                                <div class="message-content">{{ item.content }}</div>
                              </div>
                              <div class="message-meta">
                                <span>{{ formatTime(item.created_at) }}</span>
                                <span v-if="item.pending" class="send-status">
                                  <span class="send-indicator-dot" aria-hidden="true"></span>
                                  Sending
                                </span>
                                <span v-else-if="item.failed" class="send-status failed">
                                  Failed
                                  <button
                                    type="button"
                                    class="retry-btn"
                                    @click="chatStore.retryMessage(item.temp_id)"
                                  >
                                    Retry
                                  </button>
                                </span>
                                <span v-else-if="item.is_me && item.is_read">Read</span>
                                <span v-else-if="item.is_me">Sent</span>
                              </div>
                            </div>
                          </template>
                        </template>
                      </div>
                    </TransitionGroup>

                    <div v-if="chatStore.activeTypingUsers.length" class="typing-indicator">
                      {{ typingLabel }}
                    </div>
                  </div>

                  <form
                    class="chat-input-area"
                    @submit.prevent="handleSend"
                    :class="{ 'sb-shake-active': composerShaking }"
                  >
                    <textarea
                      ref="messageInput"
                      v-model="newMessage"
                      placeholder="Type your message..."
                      class="message-input"
                      rows="1"
                      @input="handleComposerInput"
                      @keydown.enter="handleComposerEnter"
                    ></textarea>
                    <button
                      type="submit"
                      class="send-btn sb-btn"
                      :disabled="!newMessage.trim()"
                    >
                      <i class="bi bi-send-fill"></i>
                    </button>
                  </form>
                </div>
              </div>

              <aside class="chat-context-panel" aria-label="Conversation context">
                <div class="context-profile">
                  <div class="context-avatar">{{ getRoomInitials(chatStore.currentRoom) }}</div>
                  <h4>{{ chatStore.getRoomPartnerName(chatStore.currentRoom) }}</h4>
                  <p>{{ partnerSubtitle }}</p>
                </div>

                <div class="context-section">
                  <h5>Stats together</h5>
                  <div class="context-stat-grid">
                    <div class="context-stat-card">
                      <strong>{{ partnerContext.sessions_together || 0 }}</strong>
                      <span>Sessions</span>
                    </div>
                    <div class="context-stat-card">
                      <strong>{{ formattedFocusedHours }}</strong>
                      <span>Focused</span>
                    </div>
                  </div>
                </div>

                <div class="context-section">
                  <h5>Common Topics</h5>
                  <div v-if="partnerContext.topics?.length" class="topic-chip-list">
                    <span v-for="topic in partnerContext.topics" :key="topic" class="topic-chip">
                      {{ topic }}
                    </span>
                  </div>
                  <p v-else class="context-empty">No shared topics yet</p>
                </div>
              </aside>
            </div>
          </template>

          <div v-else class="no-chat-selected">
            <div class="empty-state">
              <i class="bi bi-chat-dots"></i>
              <p>Select a conversation to start chatting</p>
            </div>
          </div>
        </div>
      </Transition>
    </section>

    <RatingStackModal
      :open="ratingModalOpen"
      :sessions="sessionsStore.unratedCompletedSessions"
      @close="ratingModalOpen = false"
      @rated="ratingModalOpen = sessionsStore.unratedCompletedSessions.length > 0"
    />
  </div>
</template>

<script setup>
import { computed, defineComponent, h, nextTick, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useChatStore } from '@/stores/chat'
import { useAuthStore } from '@/stores/auth'
import { useSessionsStore } from '@/stores/completedSessions'
import { CHAT_SHAKE_MS, CHAT_POP_MS, CHAT_PULSE_MS } from '../config.js'
import ChatBanner from '@/components/ChatBanner.vue'
import RatingStackModal from '@/components/RatingStackModal.vue'

const BookingCard = defineComponent({
  props: {
    booking: {
      type: Object,
      required: true,
    },
    isTutor: {
      type: Boolean,
      default: false,
    },
    compact: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['location-saved'],
  setup(props, { emit }) {
    const chatStore = useChatStore()
    const editing = ref(false)
    const location = ref(props.booking.preferred_location || '')
    const saving = ref(false)
    const error = ref('')

    watch(() => props.booking.preferred_location, (value) => {
      location.value = value || ''
    })

    const canEditLocation = computed(() => {
      return props.isTutor
        && props.booking.session_mode === 'F2F'
        && props.booking.status === 'Pending'
        && props.booking.booking_request_id
    })

    const detailsTarget = computed(() => {
      return props.isTutor ? props.booking.detail_url : props.booking.tutee_detail_url
    })

    const saveLocation = async () => {
      const nextLocation = location.value.trim()
      if (!nextLocation) {
        error.value = 'Location is required.'
        return
      }

      saving.value = true
      error.value = ''

      try {
        await chatStore.updatePendingLocation(props.booking.booking_request_id, nextLocation)
        editing.value = false
        emit('location-saved')
      } catch (saveError) {
        error.value = saveError.response?.data?.error || 'Could not update location.'
      } finally {
        saving.value = false
      }
    }

    return () => h('article', {
      class: ['booking-card', { compact: props.compact }],
    }, [
      h('div', { class: 'booking-card-header' }, [
        h('div', [
          h('span', { class: 'booking-eyebrow' }, props.booking.status),
          h('h4', props.booking.subject || 'Study session'),
        ]),
        h('span', { class: 'mode-pill' }, props.booking.session_mode),
      ]),
      h('div', { class: 'booking-grid' }, [
        h('span', [h('i', { class: 'bi bi-calendar3' }), props.booking.date]),
        h('span', [h('i', { class: 'bi bi-clock' }), `${props.booking.startTime} - ${props.booking.endTime}`]),
        h('span', [h('i', { class: 'bi bi-hourglass-split' }), `${props.booking.duration_hours}h`]),
        props.booking.session_mode === 'F2F'
          ? h('span', [h('i', { class: 'bi bi-geo-alt' }), props.booking.preferred_location || 'No location'])
          : null,
      ]),
      canEditLocation.value
        ? h('div', { class: 'location-editor' }, [
          editing.value
            ? h('div', { class: 'location-edit-row' }, [
              h('input', {
                value: location.value,
                disabled: saving.value,
                onInput: (event) => {
                  location.value = event.target.value
                },
              }),
              h('button', {
                type: 'button',
                disabled: saving.value,
                onClick: saveLocation,
              }, saving.value ? 'Saving' : 'Save'),
            ])
            : h('button', {
              type: 'button',
              class: 'text-action',
              onClick: () => {
                editing.value = true
              },
            }, 'Edit location'),
          error.value ? h('p', { class: 'location-error' }, error.value) : null,
        ])
        : null,
      detailsTarget.value
        ? h(RouterLink, { to: detailsTarget.value, class: 'details-link' }, () => 'View session details')
        : null,
    ])
  },
})

const chatStore = useChatStore()
const authStore = useAuthStore()
const sessionsStore = useSessionsStore()
const route = useRoute()
const newMessage = ref('')
const messageList = ref(null)
const messageInput = ref(null)
const ratingModalOpen = ref(false)
const composerShaking = ref(false)
const historyLoaded = ref(false)
const poppingMessages = reactive(new Set())
const pulsingRooms = reactive(new Set())

const isTutor = computed(() => {
  const role = authStore.user?.role || localStorage.getItem('user_role')
  return String(role || '').toLowerCase() === 'tutor'
})

async function openRatingModal() {
  if (!sessionsStore.sessions.length) {
    await sessionsStore.fetchSessions()
  }

  ratingModalOpen.value = true
}

const typingLabel = computed(() => {
  const names = chatStore.activeTypingUsers.map((user) => user.name).filter(Boolean)
  return `${names[0] || 'They'} ${names.length > 1 ? 'are' : 'is'} typing...`
})

const partnerContext = computed(() => chatStore.currentRoom?.partner_context || {})
const partnerSubtitle = computed(() => (isTutor.value ? 'Tutee' : 'Tutor'))
const formattedFocusedHours = computed(() => {
  const hours = Number(partnerContext.value.focused_hours || 0)
  if (Number.isInteger(hours)) return `${hours}h`
  return `${hours.toFixed(1)}h`
})

const getSidebarChipClass = (intent) => {
  const map = {
    pending: 'bg-warning text-dark',
    pending_location: 'bg-warning text-dark',
    confirmed: 'bg-primary text-white',
    ongoing: 'bg-info text-dark',
    payment_required: 'bg-warning text-dark',
    awaiting_payment: 'bg-info text-dark',
    review_pending: 'bg-info text-dark',
    rejected: 'bg-danger text-white',
    cancelled: 'bg-danger text-white',
  }
  return map[intent] ?? 'bg-secondary text-white'
}

const selectRoom = async (room) => {
  await chatStore.selectRoom(room)
  scrollToBottom()
}

function triggerShake() {
  composerShaking.value = true
  setTimeout(() => { composerShaking.value = false }, CHAT_SHAKE_MS)
}

function handleSend() {
  if (!newMessage.value.trim()) {
    triggerShake()
    return
  }
  chatStore.sendMessage(newMessage.value.trim())
  newMessage.value = ''
  resizeComposer()
}

function resizeComposer() {
  nextTick(() => {
    if (!messageInput.value) return
    messageInput.value.style.height = 'auto'
    messageInput.value.style.height = `${Math.min(messageInput.value.scrollHeight, 132)}px`
  })
}

function handleComposerInput() {
  chatStore.sendTyping(true)
  resizeComposer()
}

function handleComposerEnter(event) {
  if (event.shiftKey) return
  event.preventDefault()
  handleSend()
}

const handleLocationSaved = async () => {
  if (!chatStore.currentRoom) return
  await chatStore.fetchRooms()
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messageList.value) {
      messageList.value.scrollTop = messageList.value.scrollHeight
    }
  })
}

const getRoomInitials = (room) => {
  const name = chatStore.getRoomPartnerName(room)
  return name.split(' ').filter(Boolean).map((part) => part[0]).join('').slice(0, 2).toUpperCase()
}

const formatLastMessage = (message) => {
  if (!message) return 'No messages yet'
  if (message.message_type === 'booking_event') return message.content
  return message.content
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)

  if (Number.isNaN(date.getTime())) {
    return ''
  }

  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function getDateLabel(timestamp) {
  const date = new Date(timestamp)

  if (Number.isNaN(date.getTime())) {
    return ''
  }

  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  if (date.toDateString() === today.toDateString()) return 'TODAY'
  if (date.toDateString() === yesterday.toDateString()) return 'YESTERDAY'

  return date.toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  })
}

const groupedMessages = computed(() => {
  const result = []
  let lastLabel = null

  for (const msg of chatStore.messages) {
    const label = getDateLabel(msg.created_at)

    if (label && label !== lastLabel) {
      result.push({ type: 'date-separator', label, key: `sep-${label}` })
      lastLabel = label
    }

    result.push(msg)
  }

  return result
})

function getInitials(name) {
  return String(name || '')
    .split(' ')
    .filter(Boolean)
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
}

watch(() => chatStore.messages.length, scrollToBottom)

watch(
  () => chatStore.currentRoom?.id,
  () => {
    historyLoaded.value = false
  },
)

watch(
  () => chatStore.messages.length,
  (len) => {
    if (len > 0 && !historyLoaded.value) {
      nextTick(() => {
        historyLoaded.value = true
      })
    }
  },
)

watch(
  () => chatStore.messages.map((message) => message.is_read),
  (newVals, oldVals) => {
    if (!oldVals) return

    newVals.forEach((isRead, index) => {
      const msg = chatStore.messages[index]

      if (isRead && oldVals[index] === false && msg?.id) {
        poppingMessages.add(msg.id)
        setTimeout(() => poppingMessages.delete(msg.id), CHAT_POP_MS)
      }
    })
  },
)

watch(
  () => chatStore.sortedRooms.map((room) => ({
    id: room.id,
    unread: Number(room.unread_count || 0),
  })),
  (newVals, oldVals) => {
    if (!oldVals) return

    const previousUnreadByRoom = new Map(oldVals.map((room) => [room.id, room.unread]))

    newVals.forEach((room) => {
      const previousUnread = previousUnreadByRoom.get(room.id)

      if (previousUnread !== undefined && room.unread > previousUnread) {
        pulsingRooms.add(room.id)
        setTimeout(() => pulsingRooms.delete(room.id), CHAT_PULSE_MS)
      }
    })
  },
  { deep: true },
)

watch(
  () => route.query.room,
  async (roomId) => {
    const numericRoomId = Number(roomId)

    if (!numericRoomId || chatStore.currentRoom?.id === numericRoomId) {
      return
    }

    const room = chatStore.rooms.find((candidate) => candidate.id === numericRoomId)
    if (room) {
      await selectRoom(room)
    }
  }
)

onMounted(async () => {
  await chatStore.fetchRooms()
  chatStore.connectUpdates()

  const roomId = Number(route.query.room)
  const initialRoom = roomId
    ? chatStore.rooms.find((candidate) => candidate.id === roomId)
    : chatStore.sortedRooms[0]

  if (initialRoom) {
    await selectRoom(initialRoom)
  }
})

onUnmounted(() => {
  chatStore.disconnectRoom()
})
</script>

<style scoped>
.chat-shell {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  flex: 1;
  min-height: 0;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  overflow: hidden;
}

.chat-sidebar {
  border-right: 1px solid #eeeeee;
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
}

.sidebar-header {
  padding: 18px;
  border-bottom: 1px solid #eeeeee;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.sidebar-header h3 {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
  color: var(--sb-text-main);
}

.sidebar-header p {
  margin: 4px 0 0;
  font-size: 12px;
  color: var(--sb-text-secondary);
}

.connection-pill,
.mode-pill,
.room-session-badge {
  border-radius: 999px;
  background: #f1f3f5;
  color: var(--sb-text-secondary);
  font-size: 11px;
  font-weight: 700;
  padding: 4px 9px;
}

.connection-pill.online {
  color: var(--sb-primary);
}

.room-list {
  flex: 1;
  overflow-y: auto;
}

.room-item {
  width: 100%;
  border: 0;
  border-bottom: 1px solid #f1f3f5;
  border-left: 3px solid transparent;
  background: #fff;
  display: flex;
  gap: 12px;
  padding: 14px 18px;
  text-align: left;
  cursor: pointer;
}

.room-item:hover,
.room-item.active {
  background: #edf7f3;
}

.room-item.active {
  border-left-color: var(--sb-primary);
}

.room-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: var(--sb-primary);
  color: #ffffff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 800;
  flex: 0 0 auto;
}

.room-info {
  min-width: 0;
  flex: 1;
}

.room-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.room-name,
.last-message,
.room-session-badge {
  display: block;
}

.room-name {
  min-width: 0;
  flex: 1;
  color: var(--sb-text-main);
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.last-message {
  color: var(--sb-text-secondary);
  font-size: 13px;
  margin-top: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.room-session-badge {
  width: fit-content;
  margin-top: 7px;
}

.unread-badge {
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 999px;
  background: var(--sb-primary);
  color: #ffffff;
  font-size: 11px;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.pulse-once {
  animation: sb-pulse-dot 600ms ease forwards;
  border-radius: 50%;
}

.chat-main {
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background:
    linear-gradient(135deg, rgba(248, 250, 252, 0.96), rgba(237, 247, 243, 0.9)),
    #f8fafc;
  padding: 20px;
}

.chat-main-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.chat-workspace {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 20px;
  height: 100%;
  min-height: 0;
}

.chat-conversation {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
  min-height: 0;
}

.room-switch-enter-active {
  transition:
    opacity var(--sb-t-normal) var(--sb-spring),
    transform var(--sb-t-normal) var(--sb-spring);
}

.room-switch-enter-from {
  opacity: 0;
  transform: translateX(16px);
}

.room-switch-leave-active {
  transition: opacity 150ms ease;
}

.room-switch-leave-to {
  opacity: 0;
}

.message-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 28px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: stretch;
  gap: 18px;
  overscroll-behavior: contain;
}

.chat-card {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.58);
  border: 1px solid rgba(255, 255, 255, 0.88);
  border-radius: 28px;
  box-shadow: 0 20px 60px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(24px);
}

.message-wrapper {
  display: flex;
  flex-direction: row;
  gap: 12px;
  max-width: 80%;
  align-self: flex-start;
  align-items: flex-end;
}

.message-wrapper.is-me {
  flex-direction: column;
  align-self: flex-end;
  align-items: flex-end;
}

.message-wrapper.is-system {
  max-width: 100%;
  align-self: stretch;
}

.msg-enter-active {
  animation: sb-bubble-in var(--sb-t-normal) var(--sb-spring) both;
}

.messages-group {
  display: contents;
}

.is-pending .message-bubble {
  opacity: 0.55;
}

.message-bubble.is-failed {
  border-color: rgba(220, 53, 69, 0.65);
  opacity: 0.72;
}

.is-pending .send-indicator-dot {
  animation: sb-pulse-dot 1s ease infinite;
  border-radius: 50%;
}

.date-separator-row {
  display: flex;
  align-items: center;
  align-self: stretch;
  justify-content: center;
  margin: 8px 0 4px;
  max-width: 100%;
}

.date-separator-label {
  background: rgba(255, 255, 255, 0.58);
  border: 1px solid rgba(255, 255, 255, 0.75);
  border-radius: 999px;
  color: rgba(71, 85, 105, 0.68);
  font-size: 11px;
  font-weight: 700;
  padding: 5px 12px;
  text-transform: uppercase;
}

.message-avatar-sm {
  align-self: flex-end;
  background: #39b8fd;
  border-radius: 50%;
  color: #ffffff;
  display: inline-flex;
  flex-shrink: 0;
  font-size: 11px;
  font-weight: 800;
  height: 32px;
  align-items: center;
  justify-content: center;
  width: 32px;
}

.message-bubble-col {
  display: flex;
  flex-direction: column;
  gap: 5px;
  max-width: 100%;
  min-width: 0;
}

.message-bubble {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: 18px;
  border-top-left-radius: 4px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
  padding: 12px 18px;
  width: fit-content;
  max-width: 100%;
}

.is-me .message-bubble {
  background: #8cf8bf;
  border-color: rgba(255, 255, 255, 0.5);
  border-top-left-radius: 18px;
  border-top-right-radius: 4px;
  color: #002112;
}

.message-content {
  word-break: break-word;
}

.message-meta {
  display: flex;
  justify-content: flex-start;
  gap: 8px;
  padding: 0 10px;
  font-size: 11px;
  color: var(--sb-text-secondary);
}

.is-me .message-meta {
  justify-content: flex-end;
}

.send-status {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.send-status.failed {
  color: var(--sb-danger-bs);
  font-weight: 700;
}

.retry-btn {
  background: transparent;
  border: 1px solid currentColor;
  border-radius: 999px;
  color: inherit;
  cursor: pointer;
  font-size: 10px;
  font-weight: 800;
  line-height: 1;
  padding: 3px 7px;
}

.retry-btn:hover {
  opacity: 0.78;
}

.send-indicator-dot {
  width: 6px;
  height: 6px;
  background: currentColor;
  display: inline-block;
}

.sb-pop-active {
  animation: sb-pop 300ms var(--sb-spring-fast) both;
  display: inline-block;
}

.system-event {
  display: flex;
  gap: 10px;
  background: #f8f9fa;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 12px;
  color: var(--sb-text-main);
}

.system-event > i {
  color: var(--sb-primary);
}

.booking-card {
  background: #ffffff;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 14px;
  width: 100%;
}

.booking-card.compact {
  margin-top: 10px;
}

.booking-card-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.booking-card h4 {
  font-size: 16px;
  font-weight: 800;
  margin: 2px 0 0;
  color: var(--sb-text-main);
}

.booking-eyebrow {
  font-size: 11px;
  font-weight: 800;
  color: var(--sb-primary);
  text-transform: uppercase;
}

.booking-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px 14px;
}

.booking-grid span {
  color: var(--sb-text-secondary);
  font-size: 13px;
  display: flex;
  gap: 7px;
  align-items: center;
}

.location-editor,
.details-link {
  margin-top: 12px;
}

.location-edit-row {
  display: flex;
  gap: 8px;
}

.location-edit-row input,
.message-input {
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(222, 226, 230, 0.82);
  border-radius: 18px;
  padding: 12px 16px;
  min-width: 0;
}

.location-edit-row input {
  flex: 1;
}

.location-edit-row button,
.text-action {
  border: 0;
  background: var(--sb-primary);
  color: #ffffff;
  border-radius: 8px;
  padding: 9px 12px;
  font-weight: 700;
}

.text-action {
  background: transparent;
  color: var(--sb-primary);
  padding: 0;
}

.location-error {
  color: var(--sb-danger-bs);
  font-size: 12px;
  margin: 6px 0 0;
}

.details-link {
  color: var(--sb-primary);
  display: inline-block;
  font-size: 13px;
  font-weight: 700;
  text-decoration: none;
}

.typing-indicator {
  color: var(--sb-text-secondary);
  font-size: 13px;
  padding-left: 4px;
}

.chat-input-area {
  flex: 0 0 auto;
  border-top: 1px solid rgba(255, 255, 255, 0.7);
  background: rgba(255, 255, 255, 0.42);
  padding: 18px 20px;
  display: flex;
  align-items: flex-end;
  gap: 14px;
}

.message-input {
  flex: 1;
  max-height: 132px;
  overflow-y: auto;
  resize: none;
}

.message-input:disabled {
  background: rgba(248, 249, 250, 0.72);
  cursor: not-allowed;
}

.send-btn {
  border: 0;
  border-radius: 14px;
  width: 48px;
  height: 48px;
  background: var(--sb-primary);
  color: #ffffff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.send-btn:disabled {
  opacity: 0.55;
}

.chat-context-panel {
  display: flex;
  flex-direction: column;
  gap: 22px;
  min-height: 0;
  overflow-y: auto;
  background: rgba(255, 255, 255, 0.52);
  border: 1px solid rgba(255, 255, 255, 0.82);
  border-radius: 28px;
  box-shadow: 0 20px 60px rgba(15, 23, 42, 0.07);
  backdrop-filter: blur(24px);
  padding: 24px;
}

.context-profile {
  border-bottom: 1px solid rgba(255, 255, 255, 0.72);
  padding-bottom: 22px;
  text-align: center;
}

.context-avatar {
  align-items: center;
  background: #39b8fd;
  border-radius: 24px;
  color: #ffffff;
  display: inline-flex;
  font-size: 28px;
  font-weight: 800;
  height: 88px;
  justify-content: center;
  margin-bottom: 14px;
  width: 88px;
}

.context-profile h4 {
  color: var(--sb-text-main);
  font-size: 22px;
  font-weight: 800;
  margin: 0;
}

.context-profile p,
.context-empty {
  color: var(--sb-text-secondary);
  font-size: 13px;
  margin: 4px 0 0;
}

.context-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.context-section h5 {
  color: var(--sb-text-secondary);
  font-size: 11px;
  font-weight: 800;
  margin: 0;
  text-transform: uppercase;
}

.context-stat-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.context-stat-card {
  background: rgba(255, 255, 255, 0.52);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 18px;
  padding: 14px 10px;
  text-align: center;
}

.context-stat-card strong {
  color: var(--sb-primary);
  display: block;
  font-size: 24px;
  line-height: 1.1;
}

.context-stat-card span {
  color: var(--sb-text-secondary);
  font-size: 11px;
}

.topic-chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.topic-chip {
  background: rgba(255, 255, 255, 0.62);
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 999px;
  color: var(--sb-text-main);
  font-size: 12px;
  font-weight: 700;
  padding: 7px 11px;
}

.no-chat-selected,
.empty-rooms {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--sb-text-secondary);
  text-align: center;
}

.empty-state i,
.empty-rooms i {
  display: block;
  font-size: 44px;
  margin-bottom: 10px;
}

@media (max-width: 900px) {
  .chat-shell {
    grid-template-columns: 1fr;
    grid-template-rows: auto minmax(0, 1fr);
    height: 100%;
    min-height: 0;
  }

  .chat-sidebar {
    max-height: 310px;
    border-right: 0;
    border-bottom: 1px solid #eeeeee;
  }

  .chat-main {
    min-height: 560px;
    padding: 12px;
  }

  .chat-workspace {
    grid-template-columns: 1fr;
  }

  .chat-context-panel {
    display: none;
  }

  .message-wrapper {
    max-width: 88%;
  }

  .message-list {
    padding: 20px;
  }

  .booking-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1180px) {
  .chat-workspace {
    grid-template-columns: 1fr;
  }

  .chat-context-panel {
    display: none;
  }
}

.sb-shake-active {
  animation: sb-shake 400ms ease both;
}
</style>
