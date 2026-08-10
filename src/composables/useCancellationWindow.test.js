import { describe, expect, it } from 'vitest'
import { getCancellationWindowState, getGraceCutoff } from './useCancellationWindow'

// The session starts 2026-06-15 14:00 Manila == 06:00Z, so the 12-hour Grace Cutoff lands on
// 2026-06-15 02:00 Manila == 2026-06-14T18:00:00Z.
const SESSION_DATE = '2026-06-15'
const SESSION_START = '14:00'
const CUTOFF_ISO = '2026-06-14T18:00:00.000Z'

describe('getGraceCutoff', () => {
  it('subtracts the Grace Cutoff from the Manila-anchored session start', () => {
    expect(getGraceCutoff(SESSION_DATE, SESSION_START).toISOString()).toBe(CUTOFF_ISO)
  })

  it('returns null when the date or start time is missing', () => {
    expect(getGraceCutoff('', SESSION_START)).toBeNull()
    expect(getGraceCutoff(SESSION_DATE, '')).toBeNull()
    expect(getGraceCutoff('not-a-date', SESSION_START)).toBeNull()
  })
})

describe('getCancellationWindowState', () => {
  const stateAt = (nowIso) =>
    getCancellationWindowState({
      date: SESSION_DATE,
      startTime: SESSION_START,
      now: new Date(nowIso),
    })

  it('is not late a minute before the cutoff', () => {
    expect(stateAt('2026-06-14T17:59:00.000Z').isLate).toBe(false)
  })

  // The backend compares with `>=`, so the boundary instant must classify as late on both ends.
  it('is late exactly at the cutoff', () => {
    expect(stateAt(CUTOFF_ISO).isLate).toBe(true)
  })

  it('is late after the cutoff', () => {
    expect(stateAt('2026-06-15T05:00:00.000Z').isLate).toBe(true)
  })

  it('falls back to a non-late, unlabelled state when the session is unparseable', () => {
    const state = getCancellationWindowState({
      date: null,
      startTime: null,
      now: new Date(CUTOFF_ISO),
    })

    expect(state.cutoffAt).toBeNull()
    expect(state.isLate).toBe(false)
    expect(state.cutoffLabel).toBe('')
  })

  it('labels the cutoff in Manila time regardless of the host timezone', () => {
    const { cutoffLabel } = stateAt('2026-06-14T00:00:00.000Z')

    expect(cutoffLabel).toContain('2')
    expect(cutoffLabel).toContain('AM')
    expect(cutoffLabel).toContain('Jun 15')
  })
})
