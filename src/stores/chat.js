import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api/api'
import { useAuthStore } from './auth'
import {
  API_BASE_URL,
  wsServerRoot,
  WS_RECONNECT_DELAY_MS,
  TYPING_CLEAR_MS,
  TYPING_DEBOUNCE_MS,
  POPUP_DISMISS_MS,
} from '../config.js'

export const useChatStore = defineStore('chat', () => {
  const authStore = useAuthStore()

  const rooms = ref([])
  const currentRoom = ref(null)
  const messages = ref([])
  const socket = ref(null)
  const updatesSocket = ref(null)
  const isConnected = ref(false)
  const isUpdatesConnected = ref(false)
  const intentionalDisconnect = ref(false)
  const intentionalUpdatesDisconnect = ref(false)
  const typingUsers = ref({})
  const recentPopup = ref(null)

  let reconnectTimer = null
  let updatesReconnectTimer = null
  let typingTimer = null
  const typingClearTimers = new Map()

  const wsRoot = computed(() => {
    let baseUrl = API_BASE_URL
    if (!baseUrl.endsWith('/')) baseUrl += '/'

    if (baseUrl.startsWith('http')) {
      const apiUrl = new URL(baseUrl)
      const scheme = apiUrl.protocol === 'https:' ? 'wss' : 'ws'
      return `${scheme}://${apiUrl.host}/ws/chat/`
    }

    const serverRoot = wsServerRoot()
    const scheme =
      typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'wss' : 'ws'
    return `${scheme}://${serverRoot}/ws/chat/`
  })

  const totalUnread = computed(() => {
    return rooms.value.reduce((total, room) => total + Number(room.unread_count || 0), 0)
  })

  const activeTypingUsers = computed(() => {
    const roomId = currentRoom.value?.id
    if (!roomId) return []
    return Object.values(typingUsers.value[roomId] || {})
  })

  const sortedRooms = computed(() => {
    return [...rooms.value].sort((a, b) => {
      const aTime = new Date(a.updated_at || a.last_message?.created_at || a.created_at || 0).getTime()
      const bTime = new Date(b.updated_at || b.last_message?.created_at || b.created_at || 0).getTime()
      return bTime - aTime
    })
  })

  const myUserId = () => Number(authStore.user?.id || localStorage.getItem('user_id'))
  const myProfileId = () => Number(authStore.user?.profile_id || localStorage.getItem('profile_id'))

  const isMine = (payload) => {
    const senderUserId = Number(payload?.sender_id ?? payload?.sender)
    const senderProfileId = Number(payload?.sender_profile_id)
    return senderUserId === myUserId() || senderProfileId === myProfileId()
  }

  const withMeFlag = (message) => ({
    ...message,
    is_me: message.is_me ?? isMine(message),
  })

  const upsertRoom = (room, { preserveUnread = false } = {}) => {
    if (!room?.id) return

    const existingIndex = rooms.value.findIndex((existing) => existing.id === room.id)
    if (existingIndex === -1) {
      rooms.value.unshift(room)
    } else {
      const existingRoom = rooms.value[existingIndex]
      const nextRoom = { ...room }

      if (
        preserveUnread
        && currentRoom.value?.id !== room.id
        && Number(existingRoom.unread_count || 0) > Number(nextRoom.unread_count || 0)
      ) {
        nextRoom.unread_count = existingRoom.unread_count
      }

      rooms.value[existingIndex] = {
        ...existingRoom,
        ...nextRoom,
      }
    }

    if (currentRoom.value?.id === room.id) {
      currentRoom.value = {
        ...currentRoom.value,
        ...rooms.value.find((existing) => existing.id === room.id),
      }
    }
  }

  const applyMessageToRoom = (roomId, message, previousUnread = null) => {
    const room = rooms.value.find((candidate) => candidate.id === roomId)
    if (!room) return

    room.last_message = message
    room.updated_at = message.created_at

    if (!message.is_me && currentRoom.value?.id !== roomId) {
      room.unread_count = Number(previousUnread ?? room.unread_count ?? 0) + 1
      recentPopup.value = {
        roomId,
        partnerName: getRoomPartnerName(room),
        content: message.content,
      }
      window.setTimeout(() => {
        if (recentPopup.value?.roomId === roomId) {
          recentPopup.value = null
        }
      }, POPUP_DISMISS_MS)
    }
  }

  const addOrReplaceMessage = (incoming) => {
    const message = withMeFlag(incoming)
    const pendingIndex = message.temp_id
      ? messages.value.findIndex((candidate) => candidate.pending && candidate.temp_id === message.temp_id)
      : messages.value.findIndex(
        (candidate) => candidate.pending && candidate.content === message.content && message.is_me
      )

    if (pendingIndex !== -1) {
      messages.value[pendingIndex] = {
        ...messages.value[pendingIndex],
        ...message,
        pending: false,
        failed: false,
      }
      return
    }

    if (message.id && messages.value.some((candidate) => candidate.id === message.id && !candidate.pending)) {
      messages.value = messages.value.map((candidate) => (
        candidate.id === message.id ? { ...candidate, ...message } : candidate
      ))
      return
    }

    messages.value.push(message)
  }

  async function fetchRooms() {
    try {
      const response = await api.get('chat/rooms/')
      rooms.value = response.data
    } catch (error) {
      console.error('Error fetching chat rooms:', error)
    }
  }

  async function fetchHistory(roomId) {
    try {
      messages.value = []
      const response = await api.get(`chat/rooms/${roomId}/history/`)
      messages.value = response.data.map(withMeFlag)
    } catch (error) {
      console.error('Error fetching message history:', error)
    }
  }

  async function startInquiry(tutorProfileId) {
    const response = await api.post(`chat/start/${tutorProfileId}/`)
    const room = response.data
    upsertRoom(room)
    currentRoom.value = room
    return room
  }

  async function selectRoom(room) {
    currentRoom.value = room
    upsertRoom({ ...room, unread_count: 0 })
    await fetchHistory(room.id)
    connectToRoom(room.id)
    await markRoomRead(room.id)
  }

  async function markRoomRead(roomId = currentRoom.value?.id) {
    if (!roomId) return

    try {
      await api.post(`chat/rooms/${roomId}/read/`)
      upsertRoom({ id: roomId, unread_count: 0 })
      if (socket.value?.readyState === WebSocket.OPEN) {
        socket.value.send(JSON.stringify({ type: 'read' }))
      }
    } catch (error) {
      console.error('Error marking chat room read:', error)
    }
  }

  function connectUpdates() {
    const token = authStore.token || localStorage.getItem('access_token')
    if (!token || updatesSocket.value || !authStore.isAuthenticated) return

    intentionalUpdatesDisconnect.value = false
    updatesSocket.value = new WebSocket(`${wsRoot.value}updates/?token=${encodeURIComponent(token)}`)

    updatesSocket.value.onopen = () => {
      isUpdatesConnected.value = true
      if (updatesReconnectTimer) {
        window.clearTimeout(updatesReconnectTimer)
        updatesReconnectTimer = null
      }
    }

    updatesSocket.value.onmessage = (event) => {
      handleEvent(JSON.parse(event.data), false)
    }

    updatesSocket.value.onclose = () => {
      isUpdatesConnected.value = false
      updatesSocket.value = null
      if (!intentionalUpdatesDisconnect.value && authStore.isAuthenticated) {
        updatesReconnectTimer = window.setTimeout(connectUpdates, WS_RECONNECT_DELAY_MS)
      }
    }

    updatesSocket.value.onerror = (error) => {
      console.error('Chat updates WebSocket error:', error)
    }
  }

  function connectToRoom(roomId) {
    if (socket.value) {
      socket.value.close()
      socket.value = null
    }

    const token = authStore.token || localStorage.getItem('access_token')
    if (!token) return

    intentionalDisconnect.value = false
    socket.value = new WebSocket(`${wsRoot.value}${roomId}/?token=${encodeURIComponent(token)}`)

    socket.value.onopen = () => {
      isConnected.value = true
      if (reconnectTimer) {
        window.clearTimeout(reconnectTimer)
        reconnectTimer = null
      }
      markRoomRead(roomId)
    }

    socket.value.onmessage = (event) => {
      handleEvent(JSON.parse(event.data), true)
    }

    socket.value.onclose = () => {
      isConnected.value = false
      socket.value = null
      if (!intentionalDisconnect.value && currentRoom.value?.id === roomId) {
        reconnectTimer = window.setTimeout(() => connectToRoom(roomId), WS_RECONNECT_DELAY_MS)
      }
    }

    socket.value.onerror = (error) => {
      console.error('Chat room WebSocket error:', error)
    }
  }

  function handleEvent(event, fromActiveRoom) {
    if (!event?.type) return

    if (event.type === 'message') {
      const message = withMeFlag(event.message)
      const previousUnread = Number(
        rooms.value.find((candidate) => candidate.id === event.room_id)?.unread_count || 0
      )
      if (event.room) upsertRoom(event.room, { preserveUnread: true })
      applyMessageToRoom(event.room_id, message, previousUnread)

      if (currentRoom.value?.id === event.room_id) {
        addOrReplaceMessage(message)
        if (!message.is_me) markRoomRead(event.room_id)
      }

      return
    }

    if (event.type === 'room_updated' || event.type === 'booking_context_updated') {
      upsertRoom(event.room, { preserveUnread: true })
      return
    }

    if (event.type === 'typing') {
      if (isMine(event) || currentRoom.value?.id !== event.room_id) return
      setTypingUser(event)
      return
    }

    if (event.type === 'read_receipt') {
      if (Number(event.reader_id) !== myUserId() && currentRoom.value?.id === event.room_id) {
        messages.value = messages.value.map((message) => (
          message.is_me ? { ...message, is_read: true } : message
        ))
      } else {
        upsertRoom({ id: event.room_id, unread_count: 0 })
      }

      if (!fromActiveRoom) fetchRooms()
    }
  }

  function setTypingUser(event) {
    const roomTyping = {
      ...typingUsers.value[event.room_id],
      [event.sender_id]: {
        id: event.sender_id,
        name: event.sender_name,
      },
    }

    if (!event.is_typing) {
      delete roomTyping[event.sender_id]
    }

    typingUsers.value = {
      ...typingUsers.value,
      [event.room_id]: roomTyping,
    }

    const key = `${event.room_id}:${event.sender_id}`
    if (typingClearTimers.has(key)) {
      window.clearTimeout(typingClearTimers.get(key))
    }

    if (event.is_typing) {
      typingClearTimers.set(key, window.setTimeout(() => {
        const current = { ...typingUsers.value[event.room_id] }
        delete current[event.sender_id]
        typingUsers.value = {
          ...typingUsers.value,
          [event.room_id]: current,
        }
        typingClearTimers.delete(key)
      }, TYPING_CLEAR_MS))
    }
  }

  function sendMessage(content) {
    const trimmed = String(content || '').trim()
    if (!trimmed || !currentRoom.value?.id) return Promise.resolve()
    const tempId = `temp_${Date.now()}_${Math.random().toString(36).slice(2)}`

    const optimisticMessage = {
      id: tempId,
      temp_id: tempId,
      room: currentRoom.value?.id,
      content: trimmed,
      sender: myUserId(),
      sender_id: myUserId(),
      created_at: new Date().toISOString(),
      message_type: 'text',
      metadata: {},
      is_me: true,
      pending: true,
      failed: false,
    }

    messages.value.push(optimisticMessage)

    if (socket.value?.readyState === WebSocket.OPEN && isConnected.value) {
      try {
        socket.value.send(JSON.stringify({ type: 'message', message: trimmed, temp_id: tempId }))
        sendTyping(false)
        return Promise.resolve()
      } catch (error) {
        console.error('WebSocket send failed, falling back to REST:', error)
      }
    }

    sendTyping(false)
    return sendViaRest(currentRoom.value.id, trimmed, tempId)
  }

  async function sendViaRest(roomId, content, tempId) {
    try {
      const response = await api.post(`chat/rooms/${roomId}/messages/`, {
        message: content,
        temp_id: tempId,
      })
      const savedMessage = withMeFlag(response.data.message)
      const index = messages.value.findIndex((message) => message.temp_id === tempId)

      if (index !== -1) {
        messages.value[index] = {
          ...savedMessage,
          temp_id: tempId,
          pending: false,
          failed: false,
        }
      } else {
        addOrReplaceMessage(savedMessage)
      }

      if (response.data.room) {
        upsertRoom(response.data.room)
      }
    } catch (error) {
      const index = messages.value.findIndex((message) => message.temp_id === tempId)
      if (index !== -1) {
        messages.value[index] = {
          ...messages.value[index],
          pending: false,
          failed: true,
        }
      }
      console.error('REST chat send failed:', error)
    }
  }

  function retryMessage(tempId) {
    const message = messages.value.find((candidate) => candidate.temp_id === tempId && candidate.failed)
    if (!message || !currentRoom.value?.id) return Promise.resolve()

    messages.value = messages.value.map((candidate) => (
      candidate.temp_id === tempId
        ? { ...candidate, pending: true, failed: false }
        : candidate
    ))

    return sendViaRest(currentRoom.value.id, message.content, tempId)
  }

  function sendTyping(isTyping = true) {
    if (!socket.value || !isConnected.value) return

    socket.value.send(JSON.stringify({ type: 'typing', is_typing: isTyping }))

    if (typingTimer) window.clearTimeout(typingTimer)
    if (isTyping) {
      typingTimer = window.setTimeout(() => sendTyping(false), TYPING_DEBOUNCE_MS)
    }
  }

  async function updatePendingLocation(bookingRequestId, preferredLocation) {
    const response = await api.patch(`bookings/${bookingRequestId}/location/`, {
      preferred_location: preferredLocation,
    })
    await fetchRooms()
    return response.data
  }

  function getRoomPartnerName(room) {
    const role = authStore.user?.role || localStorage.getItem('user_role')
    return String(role).toLowerCase() === 'tutor' ? room.tutee_name : room.tutor_name
  }

  function disconnectRoom() {
    intentionalDisconnect.value = true
    if (reconnectTimer) window.clearTimeout(reconnectTimer)
    if (socket.value) {
      socket.value.close()
      socket.value = null
    }
    isConnected.value = false
    messages.value = []
    currentRoom.value = null
  }

  function disconnectAll() {
    disconnectRoom()
    intentionalUpdatesDisconnect.value = true
    if (updatesReconnectTimer) window.clearTimeout(updatesReconnectTimer)
    if (updatesSocket.value) {
      updatesSocket.value.close()
      updatesSocket.value = null
    }
    isUpdatesConnected.value = false
    rooms.value = []
    recentPopup.value = null
  }

  return {
    rooms,
    sortedRooms,
    currentRoom,
    messages,
    isConnected,
    isUpdatesConnected,
    activeTypingUsers,
    totalUnread,
    recentPopup,
    fetchRooms,
    fetchHistory,
    startInquiry,
    selectRoom,
    markRoomRead,
    connectUpdates,
    connectToRoom,
    sendMessage,
    retryMessage,
    sendTyping,
    updatePendingLocation,
    getRoomPartnerName,
    disconnectRoom,
    disconnectAll,
  }
})
