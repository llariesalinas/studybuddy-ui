import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import api from '@/services/api/api'

export const useNotificationsStore = defineStore('notifications', () => {
  const notifications = ref([])
  const loading = ref(false)

  const unreadCount = computed(() =>
    notifications.value.filter((notification) => !notification.is_read).length
  )

  const fetchNotifications = async () => {
    loading.value = true

    try {
      const response = await api.get('/notifications/')
      notifications.value = response.data
    } catch (error) {
      console.error('Failed to load notifications:', error)
    } finally {
      loading.value = false
    }
  }

  const markAsRead = async (notificationId) => {
    await api.post(`/notifications/${notificationId}/read/`)
    notifications.value = notifications.value.map((notification) =>
      notification.id === notificationId
        ? { ...notification, is_read: true }
        : notification
    )
  }

  return {
    notifications,
    loading,
    unreadCount,
    fetchNotifications,
    markAsRead,
  }
})
