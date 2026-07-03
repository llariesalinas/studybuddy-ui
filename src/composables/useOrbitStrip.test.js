import { describe, expect, it } from 'vitest'
import {
  getOrbitPhase,
  getOrbitPresentation,
  normalizeOrbitSession,
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
})
