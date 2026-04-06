const IDLE_LOGOUT_MS = 10 * 60 * 1000

const ACTIVITY_EVENTS = [
  'mousemove',
  'mousedown',
  'keydown',
  'scroll',
  'touchstart',
  'click'
]

let idleTimeoutId = null
let timeoutCallback = null
let listenersAttached = false

const clearIdleTimeout = () => {
  if (idleTimeoutId !== null && typeof window !== 'undefined') {
    window.clearTimeout(idleTimeoutId)
    idleTimeoutId = null
  }
}

const resetIdleTimer = () => {
  if (typeof window === 'undefined' || !timeoutCallback) {
    return
  }

  clearIdleTimeout()

  idleTimeoutId = window.setTimeout(() => {
    timeoutCallback?.()
  }, IDLE_LOGOUT_MS)
}

const handleUserActivity = () => {
  resetIdleTimer()
}

const attachActivityListeners = () => {
  if (typeof window === 'undefined' || listenersAttached) {
    return
  }

  ACTIVITY_EVENTS.forEach((eventName) => {
    window.addEventListener(eventName, handleUserActivity, true)
  })

  listenersAttached = true
}

const detachActivityListeners = () => {
  if (typeof window === 'undefined' || !listenersAttached) {
    return
  }

  ACTIVITY_EVENTS.forEach((eventName) => {
    window.removeEventListener(eventName, handleUserActivity, true)
  })

  listenersAttached = false
}

export const startIdleSessionTracking = (onTimeout) => {
  timeoutCallback = onTimeout

  attachActivityListeners()
  resetIdleTimer()
}

export const stopIdleSessionTracking = () => {
  clearIdleTimeout()
  detachActivityListeners()
  timeoutCallback = null
}

export { IDLE_LOGOUT_MS }
