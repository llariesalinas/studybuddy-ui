export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/'
export const API_PROXY_TARGET = import.meta.env.VITE_API_PROXY_TARGET || ''

// Client-safe publishable key for logo.dev (see ADR-0002) -- not a secret, but kept out
// of source so it can vary by environment / be omitted in local dev.
export const LOGO_DEV_TOKEN = import.meta.env.VITE_LOGO_DEV_TOKEN || ''

// Demo Basic Auth credentials, sent on the X-Demo-Auth header (not Authorization,
// which is reserved for JWT Bearer tokens -- see ADR-0005). Empty/unset outside
// the demo deployment, so this is a no-op for local dev and real production.
export const DEMO_BASIC_AUTH_USER = import.meta.env.VITE_DEMO_BASIC_AUTH_USER || ''
export const DEMO_BASIC_AUTH_PASSWORD = import.meta.env.VITE_DEMO_BASIC_AUTH_PASSWORD || ''

// Shows the dev booking/wallet panels (force a session's live phase, mark ready-for-payment,
// credit/debit a tutor wallet) outside of `import.meta.env.DEV`. Mirrors the backend's
// BOOKING_DEV_TOOLS_ENABLED flag -- only meaningful on the demo deployment, where it's set to
// 'true' so the panel is reachable despite being a production build.
export const BOOKING_DEV_TOOLS_ENABLED = import.meta.env.VITE_BOOKING_DEV_TOOLS_ENABLED === 'true'

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

// Recommender display — must match the backend's HYBRID_SCORE_PRECISION and
// UPCOMING_WEEK_DAYS (backend/studybuddy/recommender/hybrid.py, workload.py), so
// scores that read as tied on screen are the ones the Tie Breaker actually tied.
export const HYBRID_SCORE_PRECISION = 3
export const UPCOMING_WEEK_DAYS = 7
