import { describe, expect, it } from 'vitest'
import { getSessionClockState, parseSessionDateTime } from './useSessionClock'

describe('useSessionClock helpers', () => {
  it('parses session date and time in Manila time', () => {
    const parsed = parseSessionDateTime('2026-06-15', '14:00')

    expect(parsed.toISOString()).toBe('2026-06-15T06:00:00.000Z')
  })

  it('clamps elapsed and progress before the session starts', () => {
    const state = getSessionClockState({
      date: '2026-06-15',
      startTime: '14:00',
      endTime: '15:30',
      now: new Date('2026-06-15T05:30:00.000Z'),
    })

    expect(state.elapsedSeconds).toBe(0)
    expect(state.minutesLeft).toBe(120)
    expect(state.progress).toBe(0)
    expect(state.formattedElapsed).toBe('00:00:00')
  })

  it('calculates elapsed, minutes left, and progress during a session', () => {
    const state = getSessionClockState({
      date: '2026-06-15',
      startTime: '14:00',
      endTime: '15:30',
      now: new Date('2026-06-15T06:45:30.000Z'),
    })

    expect(state.elapsedSeconds).toBe(2730)
    expect(state.minutesLeft).toBe(45)
    expect(state.progress).toBe(50.6)
    expect(state.formattedElapsed).toBe('00:45:30')
  })

  it('clamps progress after the session ends', () => {
    const state = getSessionClockState({
      date: '2026-06-15',
      startTime: '14:00',
      endTime: '15:30',
      now: new Date('2026-06-15T08:10:00.000Z'),
    })

    expect(state.elapsedSeconds).toBe(5400)
    expect(state.minutesLeft).toBe(0)
    expect(state.progress).toBe(100)
    expect(state.formattedElapsed).toBe('01:30:00')
  })
})
