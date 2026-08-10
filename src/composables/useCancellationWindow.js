// Grace Cutoff helpers for the session/booking detail screens.
//
// The backend is the authority: `cancel_booking` never rejects on time, it cancels and -- when
// the request lands inside the cutoff -- opens a Late Cancellation SupportTicket against whoever
// cancelled (backend/studybuddy/views.py). So this module never gates the button; it only tells
// the views which consequence to describe.
//
// The cutoff is anchored to Manila via parseSessionDateTime, matching the backend's
// timezone.get_current_timezone(), so a device on another timezone classifies identically.

import { computed, onBeforeUnmount, ref, unref } from 'vue'

import { GRACE_CUTOFF_HOURS } from '@/config'
import { parseSessionDateTime } from '@/composables/useSessionClock'

const MINUTE_MS = 60 * 1000
const GRACE_CUTOFF_MS = GRACE_CUTOFF_HOURS * 60 * MINUTE_MS

// Upcoming sessions don't need second-level precision -- a minute of drift on either side of the
// cutoff is invisible, and the server re-decides on submit anyway.
const TICK_MS = MINUTE_MS

// Exported so anything else showing a Grace-Cutoff-shaped instant (a strike expiry, say) formats
// it the same way and in the same timezone.
export const formatCutoffLabel = (date) => {
  if (!date) {
    return ''
  }

  return new Intl.DateTimeFormat(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    timeZone: 'Asia/Manila',
  }).format(date)
}

export const getGraceCutoff = (dateValue, startTimeValue) => {
  const startAt = parseSessionDateTime(dateValue, startTimeValue)

  if (!startAt) {
    return null
  }

  return new Date(startAt.getTime() - GRACE_CUTOFF_MS)
}

export const getCancellationWindowState = ({ date, startTime, now = new Date() }) => {
  const cutoffAt = getGraceCutoff(date, startTime)

  return {
    cutoffAt,
    // `>=` mirrors the backend's is_late_cancellation comparison, so the boundary instant lands
    // on the same side on both ends. An unparseable session falls back to the penalty-free copy
    // rather than warning about a strike we can't actually predict.
    isLate: Boolean(cutoffAt) && now.getTime() >= cutoffAt.getTime(),
    cutoffLabel: formatCutoffLabel(cutoffAt),
  }
}

export function useCancellationWindow({ date, startTime }) {
  const now = ref(new Date())

  // useSessionClock's ticker deliberately only runs while a session is live, so it stays frozen
  // for the Upcoming sessions this cutoff applies to -- hence a separate, much slower one here.
  const intervalId =
    typeof window === 'undefined'
      ? null
      : window.setInterval(() => {
          now.value = new Date()
        }, TICK_MS)

  const handleVisibilityChange = () => {
    now.value = new Date()
  }

  if (typeof document !== 'undefined') {
    document.addEventListener('visibilitychange', handleVisibilityChange)
  }

  onBeforeUnmount(() => {
    if (intervalId) {
      window.clearInterval(intervalId)
    }

    if (typeof document !== 'undefined') {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  })

  const state = computed(() =>
    getCancellationWindowState({
      date: unref(date),
      startTime: unref(startTime),
      now: now.value,
    }),
  )

  return {
    cutoffAt: computed(() => state.value.cutoffAt),
    isLate: computed(() => state.value.isLate),
    cutoffLabel: computed(() => state.value.cutoffLabel),
  }
}
