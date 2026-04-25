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
        let baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/'
        if (!baseUrl.endsWith('/')) baseUrl += '/'
        return baseUrl.replace(/^http/, 'ws').replace('/api/', '/ws/chat/')
    })

    async function fetchRooms() {
        try {
            const response = await api.get('chat/rooms/')
            rooms.value = response.data
            console.log('Fetched rooms:', rooms.value.length)
        } catch (error) {
            console.error('Error fetching chat rooms:', error)
        }
    }

    async function fetchHistory(roomId) {
        try {
            messages.value = [] // Clear current messages while loading
            const response = await api.get(`chat/rooms/${roomId}/history/`)
            messages.value = response.data
            console.log('Fetched history:', messages.value.length, 'messages')
        } catch (error) {
            console.error('Error fetching message history:', error)
        }
    }

    async function startInquiry(tutorProfileId) {
        try {
            const response = await api.post(`chat/start/${tutorProfileId}/`)
            const room = response.data
            // Refresh rooms list to include the new one
            await fetchRooms()
            currentRoom.value = room
            return room
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

        // Ensure we have a token
        const token = authStore.token
        if (!token) {
            console.error('No token found for WebSocket connection')
            return
        }

        const url = `${wsUrl.value}${roomId}/?token=${token}`
        console.log('Connecting to WebSocket:', url)
        socket.value = new WebSocket(url)

        socket.value.onopen = () => {
            console.log('WebSocket connected')
            isConnected.value = true
        }

        socket.value.onmessage = (event) => {
            const data = JSON.parse(event.data)
            
            // Identifying if the message is mine using both possible ID types
            const senderUserId = Number(data.sender_id)
            const senderProfileId = Number(data.sender_profile_id)
            
            const myUserId = Number(authStore.user?.id || localStorage.getItem('user_id'))
            const myProfileId = Number(authStore.user?.profile_id || localStorage.getItem('profile_id'))
            
            const isMyMessage = (senderUserId === myUserId) || (senderProfileId === myProfileId)

            console.log('Received message:', data, 'isMyMessage:', isMyMessage)

            if (isMyMessage) {
                // Replace the matching optimistic message with server-confirmed data
                // We match by content and pending status
                const pendingIdx = messages.value.findIndex(
                    m => m.pending && m.content === data.message
                )
                if (pendingIdx !== -1) {
                    messages.value[pendingIdx] = {
                        ...messages.value[pendingIdx],
                        id: data.id || messages.value[pendingIdx].id,
                        created_at: data.created_at,
                        pending: false
                    }
                    return
                }
            }

            // If we're here, it's either someone else's message OR a message we sent 
            // from another tab/connection that wasn't in our local optimistic state.
            messages.value.push({
                id: data.id || Date.now(),
                content: data.message,
                sender_name: data.sender_name,
                sender: data.sender_id,
                created_at: data.created_at,
                is_me: isMyMessage
            })
        }

        socket.value.onclose = (event) => {
            isConnected.value = false
            console.log('WebSocket disconnected', event.code, event.reason)
            if (!intentionalDisconnect.value && currentRoom.value?.id === roomId) {
                console.log('Reconnecting in 3s...')
                setTimeout(() => connectToRoom(roomId), 3000)
            }
        }

        socket.value.onerror = (error) => {
            console.error('WebSocket error:', error)
        }
    }

    function sendMessage(content) {
        if (!socket.value || !isConnected.value) {
            console.error('Cannot send message: WebSocket not connected')
            return
        }

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
