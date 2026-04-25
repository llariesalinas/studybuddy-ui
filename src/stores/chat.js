import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api/api'
import { useAuthStore } from './auth'

export const useChatStore = defineStore('chat', () => {
    const authStore = useAuthStore()
    const rooms = ref([])
    const currentRoom = ref(null)
    const messages = ref([])
    const socket = ref(null)
    const isConnected = ref(false)
    const intentionalDisconnect = ref(false)

    const wsUrl = computed(() => {
        const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/'
        return baseUrl.replace(/^http/, 'ws').replace('/api/', '/ws/chat/')
    })

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
            const response = await api.get(`chat/rooms/${roomId}/history/`)
            messages.value = response.data
        } catch (error) {
            console.error('Error fetching message history:', error)
        }
    }

    async function startInquiry(tutorProfileId) {
        try {
            const response = await api.post(`chat/start/${tutorProfileId}/`)
            return response.data
        } catch (error) {
            console.error('Error starting inquiry chat:', error)
            throw error
        }
    }

    function connectToRoom(roomId) {
        if (socket.value) {
            socket.value.close()
        }
        intentionalDisconnect.value = false

        const url = `${wsUrl.value}${roomId}/?token=${authStore.token}`
        socket.value = new WebSocket(url)

        socket.value.onopen = () => {
            isConnected.value = true
        }

        socket.value.onmessage = (event) => {
            const data = JSON.parse(event.data)
            const isMyMessage = data.sender_id === authStore.user?.id

            if (isMyMessage) {
                // Replace the matching optimistic message with server-confirmed data
                const pendingIdx = messages.value.findIndex(
                    m => m.pending && m.content === data.message
                )
                if (pendingIdx !== -1) {
                    messages.value[pendingIdx] = {
                        ...messages.value[pendingIdx],
                        created_at: data.created_at,
                        pending: false
                    }
                    return
                }
            }

            messages.value.push({
                id: Date.now(),
                content: data.message,
                sender_name: data.sender_name,
                sender: data.sender_id,
                created_at: data.created_at,
                is_me: isMyMessage
            })
        }

        socket.value.onclose = () => {
            isConnected.value = false
            if (!intentionalDisconnect.value && currentRoom.value?.id === roomId) {
                setTimeout(() => connectToRoom(roomId), 3000)
            }
        }

        socket.value.onerror = (error) => {
            console.error('WebSocket error:', error)
        }
    }

    function sendMessage(content) {
        if (!socket.value || !isConnected.value) return

        // Optimistic update — show immediately, replace on server echo
        messages.value.push({
            id: `temp_${Date.now()}`,
            content,
            sender: authStore.user?.id,
            created_at: new Date().toISOString(),
            is_me: true,
            pending: true
        })

        socket.value.send(JSON.stringify({ message: content }))
    }

    function disconnect() {
        intentionalDisconnect.value = true
        if (socket.value) {
            socket.value.close()
            socket.value = null
        }
        isConnected.value = false
        messages.value = []
        currentRoom.value = null
    }

    return {
        rooms,
        currentRoom,
        messages,
        isConnected,
        fetchRooms,
        fetchHistory,
        startInquiry,
        connectToRoom,
        sendMessage,
        disconnect
    }
})
