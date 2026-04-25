<template>
  <div class="chat-container">
    <div class="chat-sidebar">
      <div class="sidebar-header">
        <h3>Messages</h3>
      </div>
      <div class="room-list">
        <div 
          v-for="room in chatStore.rooms" 
          :key="room.id" 
          class="room-item"
          :class="{ active: chatStore.currentRoom?.id === room.id }"
          @click="selectRoom(room)"
        >
          <div class="room-avatar">
            {{ getRoomInitials(room) }}
          </div>
          <div class="room-info">
            <div class="room-name">{{ getRoomPartnerName(room) }}</div>
            <div class="last-message" v-if="room.last_message">
              {{ room.last_message.content }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-main">
      <template v-if="chatStore.currentRoom">
        <div class="chat-header">
          <div class="partner-info">
            <div class="partner-avatar">{{ getRoomInitials(chatStore.currentRoom) }}</div>
            <div class="partner-name">{{ getRoomPartnerName(chatStore.currentRoom) }}</div>
          </div>
        </div>

        <div class="message-list" ref="messageList">
          <div 
            v-for="msg in chatStore.messages" 
            :key="msg.id" 
            class="message-wrapper"
            :class="{ 'is-me': msg.is_me }"
          >
            <div class="message-bubble">
              <div class="message-content">{{ msg.content }}</div>
              <div class="message-time">{{ formatTime(msg.created_at) }}</div>
            </div>
          </div>
        </div>

        <div class="chat-input-area">
          <form @submit.prevent="handleSend" class="input-form">
            <input 
              v-model="newMessage" 
              type="text" 
              placeholder="Type a message..." 
              class="form-control"
            />
            <button type="submit" class="send-btn" :disabled="!newMessage.trim()">
              <i class="bi bi-send-fill"></i>
            </button>
          </form>
        </div>
      </template>
      <div v-else class="no-chat-selected">
        <div class="empty-state">
          <i class="bi bi-chat-dots"></i>
          <p>Select a conversation to start chatting</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useAuthStore } from '@/stores/auth'
import { useRoute } from 'vue-router'

const chatStore = useChatStore()
const authStore = useAuthStore()
const route = useRoute()
const newMessage = ref('')
const messageList = ref(null)

const selectRoom = async (room) => {
  chatStore.currentRoom = room
  await chatStore.fetchHistory(room.id)
  chatStore.connectToRoom(room.id)
  scrollToBottom()
}

const handleSend = () => {
  if (!newMessage.value.trim()) return
  chatStore.sendMessage(newMessage.value)
  newMessage.value = ''
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messageList.value) {
      messageList.value.scrollTop = messageList.value.scrollHeight
    }
  })
}

const getRoomPartnerName = (room) => {
  const isTutor = authStore.user?.role === 'Tutor'
  return isTutor ? room.tutee_name : room.tutor_name
}

const getRoomInitials = (room) => {
  const name = getRoomPartnerName(room)
  return name.split(' ').filter(Boolean).map(n => n[0]).join('').toUpperCase()
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

watch(() => chatStore.messages.length, () => {
  scrollToBottom()
})

onMounted(async () => {
  await chatStore.fetchRooms()
  
  // If we came from a specific room or tutor inquiry
  const roomId = route.query.room
  if (roomId) {
    const room = chatStore.rooms.find(r => r.id === parseInt(roomId))
    if (room) {
      selectRoom(room)
    }
  }
})

onUnmounted(() => {
  chatStore.disconnect()
})
</script>

<style scoped>
.chat-container {
  display: flex;
  height: calc(100vh - 100px);
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  margin: 20px;
}

.chat-sidebar {
  width: 300px;
  border-right: 1px solid #eee;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.room-list {
  flex: 1;
  overflow-y: auto;
}

.room-item {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  cursor: pointer;
  transition: background 0.2s;
  gap: 12px;
}

.room-item:hover {
  background: #f8f9fa;
}

.room-item.active {
  background: #e8f7f1;
}

.room-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #00895a;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.room-info {
  flex: 1;
  overflow: hidden;
}

.room-name {
  font-weight: 600;
  color: #163127;
}

.last-message {
  font-size: 0.85rem;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fcfdfc;
}

.chat-header {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  background: #fff;
}

.partner-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.partner-avatar {
  width: 35px;
  height: 35px;
  border-radius: 50%;
  background: #00895a;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  font-weight: bold;
}

.partner-name {
  font-weight: 600;
  color: #163127;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message-wrapper {
  display: flex;
  flex-direction: column;
  max-width: 70%;
}

.message-wrapper.is-me {
  align-self: flex-end;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 18px;
  background: #fff;
  border: 1px solid #eee;
  position: relative;
}

.is-me .message-bubble {
  background: #00895a;
  color: white;
  border: none;
}

.message-time {
  font-size: 0.7rem;
  margin-top: 4px;
  opacity: 0.7;
  text-align: right;
}

.chat-input-area {
  padding: 20px;
  background: #fff;
  border-top: 1px solid #eee;
}

.input-form {
  display: flex;
  gap: 10px;
}

.send-btn {
  background: #00895a;
  color: white;
  border: none;
  width: 45px;
  height: 45px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
}

.no-chat-selected {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
}

.empty-state {
  text-align: center;
}

.empty-state i {
  font-size: 4rem;
  margin-bottom: 1rem;
  display: block;
}
</style>
