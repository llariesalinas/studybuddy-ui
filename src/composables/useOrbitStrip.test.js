import { describe, expect, it } from 'vitest'
import {
  getOrbitPhase,
  getOrbitPresentation,
  normalizeOrbitSession,
  ORBIT_HANDOFF_CAP_MS,
} from './useOrbitStrip'

const NOW = new Date('2026-07-03T05:48:00.000Z')

describe('useOrbitStrip helpers', () => {
  it('normalizes list and detail payload shapes', () => {
    expect(
      normalizeOrbitSession({
        id: 42,
        status: 'Upcoming',
        date: '2026-07-03',
        startTime: '14:00',
        endTime: '15:00',
        subject: 'Calculus',
        tutor: 'Maria Cruz',
      }),
    ).toMatchObject({
      id: 42,
      status: 'Upcoming',
      startTime: '14:00',
      tutorName: 'Maria Cruz',
    })

    expect(
      normalizeOrbitSession({
        id: 43,
        tutor: { name: 'Leo Santos' },
        session: {
          status: 'Payment Required',
          date: '2026-07-03',
          start_time: '13:00',
          end_time: '14:00',
          subject: 'Physics',
        },
      }),
    ).toMatchObject({
      id: 43,
      status: 'Payment Required',
      endTime: '14:00',
      subject: 'Physics',
      tutorName: 'Leo Santos',
    })
  })

  it('shows upcoming only inside the 15 minute countdown window', () => {
    const session = {
      status: 'Upcoming',
      date: '2026-07-03',
      startTime: '14:00',
      endTime: '15:00',
    }

    expect(getOrbitPhase(session, NOW)).toBe('upcoming')
    expect(getOrbitPhase(session, new Date('2026-07-03T05:30:00.000Z'))).toBe(null)
  })

  it('uses real time for live and status for handoff', () => {
    expect(
      getOrbitPhase(
        {
          status: 'Upcoming',
          date: '2026-07-03',
          startTime: '13:00',
          endTime: '14:00',
        },
        NOW,
      ),
    ).toBe('live')

    expect(
      getOrbitPhase(
        {
          status: 'Awaiting Verification',
          date: '2026-07-02',
          startTime: '13:00',
          endTime: '14:00',
        },
        NOW,
      ),
    ).toBe('handoff')
  })

  it('calculates presentation timer, progress, and up next hint', () => {
    const presentation = getOrbitPresentation({
      session: {
        id: 42,
        status: 'Upcoming',
        date: '2026-07-03',
        startTime: '14:00',
        endTime: '15:00',
        subject: 'Calculus',
        tutor: 'Maria',
      },
      nextSession: {
        status: 'Payment Required',
        date: '2026-07-03',
        startTime: '12:00',
        endTime: '13:00',
        subject: 'Physics',
        tutor: 'Leo',
      },
      nextState: 'handoff',
      now: NOW,
    })

    expect(presentation.hasOrbit).toBe(true)
    expect(presentation.stateLabel).toBe('Starting soon')
    expect(presentation.timerText).toBe('Starts in 12:00')
    expect(presentation.progress).toBe(20)
    expect(presentation.zone).toBe(1)
    expect(presentation.upNextHint).toContain('Up next: Payment handoff - Physics')
  })

  it('caps the handoff elapsed text at the same window as the progress bar', () => {
    // Regression: timerText used to keep counting the raw elapsed time
    // forever (e.g. "410:31:35 ago") even though progress was already
    // clamped to 100% past the 24h handoff cap.
    const farPastEnd = new Date(NOW.getTime() - (ORBIT_HANDOFF_CAP_MS * 5))

    const staleHandoff = getOrbitPresentation({
      session: {
        id: 99,
        status: 'Payment Required',
        date: farPastEnd.toISOString().slice(0, 10),
        startTime: '13:00',
        endTime: '13:30',
      },
      now: NOW,
    })

    expect(staleHandoff.progress).toBe(100)
    expect(staleHandoff.timerText).toBe('Ended over 24:00:00 ago')
    expect(staleHandoff.timerText).not.toMatch(/^Ended \d{3,}:/)
  })
})
