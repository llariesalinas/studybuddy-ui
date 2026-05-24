export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/'

// Derive WebSocket server root from API_BASE_URL at runtime
export function wsServerRoot() {
  if (typeof window !== 'undefined') return window.location.host
  return new URL(API_BASE_URL).host
}

// Auth
export const ACCESS_REFRESH_INTERVAL_MS = 4 * 60 * 1000   // 4 min
export const IDLE_LOGOUT_MS             = 10 * 60 * 1000  // 10 min

// Polling
export const SESSION_POLL_INTERVAL_MS      = 15_000
export const NOTIFICATION_POLL_INTERVAL_MS = 15_000

// Chat / WebSocket
export const WS_RECONNECT_DELAY_MS  = 3_000
export const TYPING_CLEAR_MS        = 3_500
export const TYPING_DEBOUNCE_MS     = 1_800
export const WS_RECONNECT_CAP_MS    = 6_000

// UI animations
export const CHAT_SHAKE_MS = 420
export const CHAT_POP_MS   = 600
export const CHAT_PULSE_MS = 600
