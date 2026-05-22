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
          class="room-item"
          :class="{ active: chatStore.currentRoom?.id === room.id }"
          @click="selectRoom(room)"
        >
          <span class="room-avatar">{{ getRoomInitials(room) }}</span>
          <span class="room-info">
            <span class="room-title-row">
              <span class="room-name">{{ chatStore.getRoomPartnerName(room) }}</span>
              <span v-if="room.unread_count" class="unread-badge">{{ room.unread_count }}</span>
            </span>
            <span class="last-message">
              {{ formatLastMessage(room.last_message) }}
            </span>
            <span v-if="room.current_booking" class="room-session-chip">
              {{ room.current_booking.status }} session
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
      <template v-if="chatStore.currentRoom">
        <header class="chat-header">
          <div class="partner-info">
            <div class="partner-avatar">{{ getRoomInitials(chatStore.currentRoom) }}</div>
            <div>
              <h3>{{ chatStore.getRoomPartnerName(chatStore.currentRoom) }}</h3>
              <p :class="{ connected: chatStore.isConnected }">
                {{ chatStore.isConnected ? 'Connected' : 'Reconnecting...' }}
              </p>
            </div>
          </div>
        </header>

        <div class="message-list" ref="messageList">
          <BookingCard
            v-if="chatStore.currentRoom.current_booking"
            :booking="chatStore.currentRoom.current_booking"
            :is-tutor="isTutor"
            @location-saved="handleLocationSaved"
          />

          <div
            v-for="msg in chatStore.messages"
            :key="msg.id"
            class="message-wrapper"
            :class="{
              'is-me': msg.is_me,
              'is-system': msg.message_type !== 'text',
            }"
          >
            <div v-if="!msg.is_me && msg.message_type === 'text'" class="message-sender">
              {{ msg.sender_name }}
            </div>

            <div v-if="msg.message_type === 'booking_event'" class="system-event">
              <i class="bi bi-calendar-check"></i>
              <div>
                <strong>{{ msg.content }}</strong>
                <BookingCard
                  v-if="msg.metadata?.booking"
                  :booking="msg.metadata.booking"
                  :is-tutor="isTutor"
                  compact
                  @location-saved="handleLocationSaved"
                />
              </div>
            </div>

            <div v-else class="message-bubble">
              <div class="message-content">{{ msg.content }}</div>
              <div class="message-meta">
                <span>{{ formatTime(msg.created_at) }}</span>
                <span v-if="msg.pending">Sending</span>
                <span v-else-if="msg.is_me && msg.is_read">Read</span>
                <span v-else-if="msg.is_me">Sent</span>
              </div>
            </div>
          </div>

          <div v-if="chatStore.activeTypingUsers.length" class="typing-indicator">
            {{ typingLabel }}
          </div>
        </div>

        <form class="chat-input-area" @submit.prevent="handleSend" :class="{ 'sb-shake-active': composerShaking }">
          <input
            v-model="newMessage"
            type="text"
            :placeholder="chatStore.isConnected ? 'Type a message...' : 'Connecting...'"
            class="message-input"
            :disabled="!chatStore.isConnected"
            @input="chatStore.sendTyping(true)"
          />
          <button type="submit" class="send-btn sb-btn" :disabled="!newMessage.trim() || !chatStore.isConnected">
            <i class="bi bi-send-fill"></i>
          </button>
        </form>
      </template>

      <div v-else class="no-chat-selected">
        <div class="empty-state">
          <i class="bi bi-chat-dots"></i>
          <p>Select a conversation to start chatting</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, defineComponent, h, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useChatStore } from '@/stores/chat'
import { useAuthStore } from '@/stores/auth'

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
const route = useRoute()
const newMessage = ref('')
const messageList = ref(null)
const composerShaking = ref(false)

const isTutor = computed(() => {
  const role = authStore.user?.role || localStorage.getItem('user_role')
  return String(role || '').toLowerCase() === 'tutor'
})
const typingLabel = computed(() => {
  const names = chatStore.activeTypingUsers.map((user) => user.name).filter(Boolean)
  return `${names[0] || 'They'} ${names.length > 1 ? 'are' : 'is'} typing...`
})

const selectRoom = async (room) => {
  await chatStore.selectRoom(room)
  scrollToBottom()
}

function triggerShake() {
  composerShaking.value = true
  setTimeout(() => { composerShaking.value = false }, 420)
}

function handleSend() {
  if (!newMessage.value.trim()) {
    triggerShake()
    return
  }
  chatStore.sendMessage(newMessage.value.trim())
  newMessage.value = ''
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

watch(() => chatStore.messages.length, scrollToBottom)

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

.sidebar-header h3,
.chat-header h3 {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
  color: #163127;
}

.sidebar-header p,
.chat-header p {
  margin: 4px 0 0;
  font-size: 12px;
  color: #6c757d;
}

.connection-pill,
.mode-pill,
.room-session-chip {
  border-radius: 999px;
  background: #f1f3f5;
  color: #495057;
  font-size: 11px;
  font-weight: 700;
  padding: 4px 9px;
}

.connection-pill.online,
.connected {
  color: #00895a;
}

.room-list {
  flex: 1;
  overflow-y: auto;
}

.room-item {
  width: 100%;
  border: 0;
  border-bottom: 1px solid #f1f3f5;
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

.room-avatar,
.partner-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: #00895a;
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
.room-session-chip {
  display: block;
}

.room-name {
  min-width: 0;
  flex: 1;
  color: #163127;
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.last-message {
  color: #6c757d;
  font-size: 13px;
  margin-top: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.room-session-chip {
  width: fit-content;
  margin-top: 7px;
  background: #f8f9fa;
}

.unread-badge {
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 999px;
  background: #00895a;
  color: #ffffff;
  font-size: 11px;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.chat-main {
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: #fcfdfc;
}

.chat-header {
  background: #ffffff;
  border-bottom: 1px solid #eeeeee;
  padding: 16px 20px;
}

.partner-info {
  display: flex;
  gap: 12px;
  align-items: center;
}

.message-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: stretch;
  gap: 14px;
  overscroll-behavior: contain;
}

.message-wrapper {
  display: flex;
  flex-direction: column;
  max-width: 72%;
  align-self: flex-start;
}

.message-wrapper.is-me {
  align-self: flex-end;
  align-items: flex-end;
}

.message-wrapper.is-system {
  max-width: 100%;
  align-self: stretch;
}

.message-sender {
  color: #6c757d;
  font-size: 12px;
  margin: 0 0 3px 4px;
}

.message-bubble {
  background: #ffffff;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 11px 13px;
  width: fit-content;
  max-width: 100%;
}

.is-me .message-bubble {
  background: #00895a;
  border-color: #00895a;
  color: #ffffff;
}

.message-content {
  word-break: break-word;
}

.message-meta {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 5px;
  font-size: 11px;
  opacity: 0.75;
}

.system-event {
  display: flex;
  gap: 10px;
  background: #f8f9fa;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 12px;
  color: #163127;
}

.system-event > i {
  color: #00895a;
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
  color: #163127;
}

.booking-eyebrow {
  font-size: 11px;
  font-weight: 800;
  color: #00895a;
  text-transform: uppercase;
}

.booking-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px 14px;
}

.booking-grid span {
  color: #495057;
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
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 10px 12px;
  min-width: 0;
}

.location-edit-row input {
  flex: 1;
}

.location-edit-row button,
.text-action {
  border: 0;
  background: #00895a;
  color: #ffffff;
  border-radius: 8px;
  padding: 9px 12px;
  font-weight: 700;
}

.text-action {
  background: transparent;
  color: #00895a;
  padding: 0;
}

.location-error {
  color: #dc3545;
  font-size: 12px;
  margin: 6px 0 0;
}

.details-link {
  color: #00895a;
  display: inline-block;
  font-size: 13px;
  font-weight: 700;
  text-decoration: none;
}

.typing-indicator {
  color: #6c757d;
  font-size: 13px;
  padding-left: 4px;
}

.chat-input-area {
  flex: 0 0 auto;
  border-top: 1px solid #eeeeee;
  background: #ffffff;
  padding: 16px 20px;
  display: flex;
  gap: 10px;
}

.message-input {
  flex: 1;
}

.message-input:disabled {
  background: #f8f9fa;
  cursor: not-allowed;
}

.send-btn {
  border: 0;
  border-radius: 50%;
  width: 44px;
  height: 44px;
  background: #00895a;
  color: #ffffff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.send-btn:disabled {
  opacity: 0.55;
}

.no-chat-selected,
.empty-rooms {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
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
  }

  .message-wrapper {
    max-width: 88%;
  }

  .booking-grid {
    grid-template-columns: 1fr;
  }
}

.sb-shake-active {
  animation: sb-shake 400ms ease both;
}
</style>
