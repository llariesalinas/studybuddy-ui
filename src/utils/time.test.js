import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import {
  currentComparableMinutes,
  formatDurationLabel,
  formatTimeLabel,
  formatTimeRangeLabel,
  isPastDate,
  isPastTimeForDate,
  padNumber,
  timeToMinutes,
  todayKey,
} from './time'

describe('padNumber', () => {
  it('pads single digits to two characters', () => {
    expect(padNumber(5)).toBe('05')
    expect(padNumber(0)).toBe('00')
  })

  it('leaves two-digit values alone', () => {
    expect(padNumber(12)).toBe('12')
  })
})

describe('timeToMinutes', () => {
  it('converts an HH:mm string to minutes since midnight', () => {
    expect(timeToMinutes('00:00')).toBe(0)
    expect(timeToMinutes('09:30')).toBe(570)
    expect(timeToMinutes('23:00')).toBe(1380)
  })

  it('treats missing values as midnight, matching the behavior it replaces', () => {
    expect(timeToMinutes(null)).toBe(0)
    expect(timeToMinutes(undefined)).toBe(0)
    expect(timeToMinutes('')).toBe(0)
  })
})

describe('formatTimeLabel', () => {
  it('renders 12-hour labels with a period suffix', () => {
    expect(formatTimeLabel('09:00')).toBe('9:00 AM')
    expect(formatTimeLabel('13:00')).toBe('1:00 PM')
  })

  it('renders both noon and midnight as 12', () => {
    expect(formatTimeLabel('00:00')).toBe('12:00 AM')
    expect(formatTimeLabel('12:00')).toBe('12:00 PM')
  })

  it('returns an empty string for a missing time', () => {
    expect(formatTimeLabel(null)).toBe('')
  })
})

describe('formatTimeRangeLabel', () => {
  it('collapses the period when both bounds share one', () => {
    expect(formatTimeRangeLabel('09:00', '11:00')).toBe('9:00 - 11:00 AM')
  })

  it('keeps both periods when the range crosses noon', () => {
    expect(formatTimeRangeLabel('11:00', '13:00')).toBe('11:00 AM - 1:00 PM')
  })

  it('returns an empty string unless both bounds are present', () => {
    expect(formatTimeRangeLabel('09:00', null)).toBe('')
    expect(formatTimeRangeLabel(null, '11:00')).toBe('')
    expect(formatTimeRangeLabel(null, null)).toBe('')
  })
})

describe('formatDurationLabel', () => {
  it('singularizes a one-hour range', () => {
    expect(formatDurationLabel('09:00', '10:00')).toBe('1 hr')
  })

  it('pluralizes longer ranges', () => {
    expect(formatDurationLabel('09:00', '11:00')).toBe('2 hrs')
  })

  it('returns an empty string for an incomplete or inverted range', () => {
    expect(formatDurationLabel('09:00', null)).toBe('')
    expect(formatDurationLabel('11:00', '09:00')).toBe('')
    expect(formatDurationLabel('09:00', '09:00')).toBe('')
  })
})

describe('date and time comparisons against now', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    // 2026-08-07 14:30:00 local time
    vi.setSystemTime(new Date(2026, 7, 7, 14, 30, 0))
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('builds todayKey from local date parts, not UTC', () => {
    expect(todayKey()).toBe('2026-08-07')
  })

  it('reports current minutes since midnight', () => {
    expect(currentComparableMinutes()).toBe(14 * 60 + 30)
  })

  it('rounds the current minute up when seconds have elapsed', () => {
    vi.setSystemTime(new Date(2026, 7, 7, 14, 30, 42))
    expect(currentComparableMinutes()).toBe(14 * 60 + 31)
  })

  it('detects past dates', () => {
    expect(isPastDate('2026-08-06')).toBe(true)
    expect(isPastDate('2026-08-07')).toBe(false)
    expect(isPastDate('2026-08-08')).toBe(false)
  })

  it('treats a missing date as not past', () => {
    expect(isPastDate(null)).toBe(false)
    expect(isPastDate('')).toBe(false)
  })

  it('flags times already gone today', () => {
    expect(isPastTimeForDate('2026-08-07', '09:00')).toBe(true)
    expect(isPastTimeForDate('2026-08-07', '15:00')).toBe(false)
  })

  it('never flags times on a future date', () => {
    expect(isPastTimeForDate('2026-08-08', '09:00')).toBe(false)
  })

  it('needs both a date and a time to flag anything', () => {
    expect(isPastTimeForDate('2026-08-07', null)).toBe(false)
    expect(isPastTimeForDate(null, '09:00')).toBe(false)
  })
})
