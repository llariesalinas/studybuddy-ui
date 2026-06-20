import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const { useSessionsStore } = await import('./completedSessions')
const { useActiveSessionStore } = await import('./activeSession')

describe('active session store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    window.localStorage.clear()
  })

  it('recognizes a forced live booking from refreshed session payloads', () => {
    const sessionsStore = useSessionsStore()
    const activeSession = useActiveSessionStore()

    activeSession.currentTime = new Date('2026-06-15T10:30:00')
    sessionsStore.sessions = [
      {
        id: 42,
        status: 'Ongoing',
        date: '2026-06-15',
        startTime: '10:00',
        endTime: '11:00',
        subject: 'Dev QA',
      },
    ]
    activeSession.activeDetail = {
      id: 42,
      session: {
        raw_status: 'Confirmed',
        session_mode: 'F2F',
        date: '2026-06-15',
        start_time: '10:00',
        end_time: '11:00',
        preferred_location: 'Library',
      },
      check_ins: {
        venue_confirm: null,
        midpoint_checkin: null,
      },
    }

    expect(activeSession.activeBooking.id).toBe(42)
    expect(activeSession.sessionPhase).toBe('midpoint')
    expect(activeSession.dueCheckIn).toBe('venue')
  })
})
