export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/'
export const API_PROXY_TARGET = import.meta.env.VITE_API_PROXY_TARGET || ''

// Derive WebSocket server root from API_BASE_URL at runtime
export function wsServerRoot() {
  const fallbackOrigin =
    typeof window !== 'undefined' ? window.location.origin : 'http://127.0.0.1'
  const websocketSource = API_BASE_URL.startsWith('http') ? API_BASE_URL : API_PROXY_TARGET

  return new URL(websocketSource || fallbackOrigin, fallbackOrigin).host
}

export function wsServerProtocol() {
  const fallbackOrigin =
    typeof window !== 'undefined' ? window.location.origin : 'http://127.0.0.1'
  const websocketSource = API_BASE_URL.startsWith('http') ? API_BASE_URL : API_PROXY_TARGET
  const protocol = new URL(websocketSource || fallbackOrigin, fallbackOrigin).protocol

  return protocol === 'https:' ? 'wss' : 'ws'
}

// Auth
export const ACCESS_REFRESH_INTERVAL_MS = 4 * 60 * 1000   // 4 min
export const IDLE_LOGOUT_MS             = 10 * 60 * 1000  // 10 min
export const MAX_DOCUMENT_UPLOAD_SIZE_BYTES = 5 * 1024 * 1024 // 5 MB; keep in sync with backend

// Polling
export const SESSION_POLL_INTERVAL_MS      = 60_000
export const NOTIFICATION_POLL_INTERVAL_MS = 60_000

// Chat / WebSocket
export const WS_RECONNECT_DELAY_MS  = 3_000
export const TYPING_CLEAR_MS        = 3_500
export const TYPING_DEBOUNCE_MS     = 1_800
export const WS_RECONNECT_CAP_MS    = 6_000
export const POPUP_DISMISS_MS       = 6_000  // how long the new-message toast stays visible
export const CHAT_ROOMS_CACHE_TTL_MS   = 30_000
export const CHAT_HISTORY_CACHE_TTL_MS = 10 * 60 * 1000

// Frontend API cache
export const CATALOG_CACHE_TTL_MS = 60 * 60 * 1000
export const PARTNER_INSTITUTIONS_CACHE_TTL_MS = 15 * 60 * 1000
export const PAYMENT_METHODS_CACHE_TTL_MS = 10 * 60 * 1000
export const RECEIVING_INSTITUTIONS_CACHE_TTL_MS = 12 * 60 * 60 * 1000

// UI animations
export const CHAT_SHAKE_MS = 420
export const CHAT_POP_MS   = 600
export const CHAT_PULSE_MS = 600
