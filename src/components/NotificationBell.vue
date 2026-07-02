<template>
  <div ref="wrapperRef" class="notification-wrapper">
    <button type="button" class="notification-trigger sb-btn" @click="toggleDropdown">
      <i class="bi bi-bell fs-5"></i>
      <span v-if="notificationsStore.unreadCount" class="notification-badge">
        {{ notificationsStore.unreadCount }}
      </span>
    </button>

    <div v-if="isOpen" class="notification-dropdown">
      <div class="notification-header">
        <div>
          <p class="notification-eyebrow mb-1">Updates</p>
          <strong class="notification-title">Notifications</strong>
        </div>
        <span class="notification-count">{{ notificationsStore.unreadCount }}</span>
      </div>

      <div v-if="!notificationsStore.notifications.length" class="notification-empty">
        <div class="notification-empty-icon">
          <i class="bi bi-bell-slash"></i>
        </div>
        <div class="notification-empty-title">You're all caught up</div>
        <div class="notification-empty-copy">Unread booking and payment updates will appear here.</div>
      </div>

      <div v-else class="notification-list">
        <button
          v-for="notification in notificationsStore.notifications"
          :key="notification.id"
          type="button"
          class="notification-item sb-btn"
          :class="{ 'notification-item-read': notification.is_read }"
          @click="markAsRead(notification.id)"
        >
          <div class="notification-dot" :class="{ 'notification-dot-read': notification.is_read }"></div>
          <div class="notification-copy">
            <div class="notification-message">{{ notification.message }}</div>
            <div class="notification-time">
              {{ formatTimestamp(notification.created_at) }}
              <span v-if="notification.is_read" class="notification-read-label">Read</span>
            </div>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useNotificationsStore } from '@/stores/notifications'
import { NOTIFICATION_POLL_INTERVAL_MS } from '../config.js'

const notificationsStore = useNotificationsStore()
const isOpen = ref(false)
const wrapperRef = ref(null)
let refreshIntervalId = null
let errorTicksRemaining = 0
let consecutiveErrors = 0

const toggleDropdown = async () => {
  isOpen.value = !isOpen.value

  if (isOpen.value) {
    await notificationsStore.fetchNotifications()
  }
}

const markAsRead = async (notificationId) => {
  await notificationsStore.markAsRead(notificationId)
}

const formatTimestamp = (value) => {
  if (!value) {
    return ''
  }

  return new Intl.DateTimeFormat('en-PH', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(new Date(value))
}

const handleClickOutside = (event) => {
  if (!wrapperRef.value?.contains(event.target)) {
    isOpen.value = false
  }
}

const handleVisibilityChange = async () => {
  if (!document.hidden) {
    await notificationsStore.fetchNotifications()
  }
}

onMounted(() => {
  window.addEventListener('click', handleClickOutside)
  document.addEventListener('visibilitychange', handleVisibilityChange)
  notificationsStore.fetchNotifications()
  refreshIntervalId = window.setInterval(async () => {
    if (document.hidden) return
    if (errorTicksRemaining > 0) {
      errorTicksRemaining--
      return
    }
    const success = await notificationsStore.fetchNotifications()
    if (success) {
      consecutiveErrors = 0
      errorTicksRemaining = 0
    } else {
      consecutiveErrors++
      errorTicksRemaining = Math.min(2 ** (consecutiveErrors - 1), 8)
    }
  }, NOTIFICATION_POLL_INTERVAL_MS)
})

onBeforeUnmount(() => {
  window.removeEventListener('click', handleClickOutside)
  document.removeEventListener('visibilitychange', handleVisibilityChange)

  if (refreshIntervalId) {
    window.clearInterval(refreshIntervalId)
  }
})
</script>

<style scoped>
.notification-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.notification-trigger {
  position: relative;
  border: 1px solid #dbe4dd;
  background: #ffffff;
  border-radius: 16px;
  width: 52px;
  height: 52px;
  color: #153326;
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.06);
  transition: transform var(--sb-t-normal) var(--sb-spring);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.notification-trigger:hover {
  transform: translateY(-1px);
  border-color: #b9cfbf;
  box-shadow: 0 16px 28px rgba(15, 23, 42, 0.09);
}

.notification-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  min-width: 22px;
  height: 22px;
  border-radius: 999px;
  background: #dc2626;
  color: #ffffff;
  font-size: 0.72rem;
  font-weight: 700;
  display: grid;
  place-items: center;
  padding: 0 6px;
}

.notification-dropdown {
  position: absolute;
  top: calc(100% + 14px);
  right: 0;
  left: auto;
  width: min(360px, calc(100vw - 48px));
  background: #ffffff;
  border: 1px solid #dbe4dd;
  border-radius: 22px;
  overflow: hidden;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.16);
  z-index: 1040;
}

.notification-header {
  padding: 16px 18px;
  border-bottom: 1px solid #edf2ee;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(180deg, #f8fcfa 0%, #ffffff 100%);
}

.notification-eyebrow {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #6b7b73;
}

.notification-title {
  font-size: 1rem;
  color: #13261d;
}

.notification-count {
  min-width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: #e8f5ee;
  color: #0e7a53;
  font-size: 0.82rem;
  font-weight: 700;
}

.notification-list {
  max-height: 360px;
  overflow-y: auto;
}

.notification-item {
  width: 100%;
  border: 0;
  background: #ffffff;
  text-align: left;
  padding: 16px 18px;
  border-bottom: 1px solid #eef2f7;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  transition: none;
}

.notification-item:hover {
  background: #f8fcfa;
}

.notification-item-read {
  background: #fbfcfb;
}

.notification-item:last-child {
  border-bottom: 0;
}

.notification-dot {
  width: 10px;
  height: 10px;
  margin-top: 6px;
  border-radius: 999px;
  background: #0e9f6e;
  flex-shrink: 0;
}

.notification-copy {
  min-width: 0;
}

.notification-message {
  font-size: 0.94rem;
  line-height: 1.45;
  color: #1f2937;
  white-space: normal;
}

.notification-item-read .notification-message {
  color: #69767b;
}

.notification-time {
  font-size: 0.78rem;
  color: #6b7280;
  margin-top: 6px;
}

.notification-read-label {
  margin-left: 8px;
  padding: 2px 8px;
  border-radius: 999px;
  background: #eef2f0;
  color: #64706a;
  font-size: 0.7rem;
  font-weight: 700;
}

.notification-dot-read {
  background: #c5d1ca;
}

.notification-empty {
  padding: 28px 22px 30px;
  color: #6b7280;
  text-align: center;
}

.notification-empty-icon {
  width: 52px;
  height: 52px;
  margin: 0 auto 14px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  background: #f2f7f4;
  color: #62806f;
  font-size: 1.3rem;
}

.notification-empty-title {
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 6px;
}

.notification-empty-copy {
  font-size: 0.88rem;
  line-height: 1.5;
}

@media (max-width: 1024px) {
  .notification-dropdown {
    left: auto;
    right: 0;
    width: min(320px, calc(100vw - 32px));
  }
}
</style>
