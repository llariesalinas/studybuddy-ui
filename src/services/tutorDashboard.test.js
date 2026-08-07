import { describe, expect, it } from 'vitest'
import { dayPackedPages, groupByDate, splitBookingsByAttention } from './tutorDashboard'

describe('splitBookingsByAttention', () => {
  it('routes requests, payment actions, and scheduled bookings by their specified statuses', () => {
    const pending = { id: 'pending', raw_status: 'PeNdInG', status: 'Upcoming' }
    const paymentRequired = {
      id: 'payment-required',
      raw_status: 'Confirmed',
      status: 'payment required',
    }
    const awaitingVerification = {
      id: 'awaiting-verification',
      raw_status: 'awaiting payment verification',
      status: 'Awaiting Verification',
    }
    const upcoming = { id: 'upcoming', raw_status: 'Confirmed', status: 'Upcoming' }

    expect(
      splitBookingsByAttention([pending, paymentRequired, awaitingVerification, upcoming]),
    ).toEqual({
      requests: [pending],
      payments: [paymentRequired, awaitingVerification],
      schedule: [paymentRequired, awaitingVerification, upcoming],
    })
  })

  it('keeps bookings without raw_status in the schedule', () => {
    const booking = { id: 'fallback', status: 'Upcoming' }

    expect(splitBookingsByAttention([booking])).toEqual({
      requests: [],
      payments: [],
      schedule: [booking],
    })
  })
})

describe('groupByDate', () => {
  it('orders days and bookings by their date and start time', () => {
    const early = { id: 'early', date: '2026-08-05', startTime: '09:00' }
    const later = { id: 'later', date: '2026-08-05', startTime: '15:00' }
    const nextDay = { id: 'next-day', date: '2026-08-06', startTime: '10:00' }

    expect(groupByDate([later, nextDay, early])).toEqual([
      { date: '2026-08-05', bookings: [early, later] },
      { date: '2026-08-06', bookings: [nextDay] },
    ])
  })
})

describe('dayPackedPages', () => {
  it('packs whole days toward the target and breaks before one that would exceed it', () => {
    const monday = { date: '2026-08-03', bookings: [{}, {}, {}] }
    const tuesday = { date: '2026-08-04', bookings: [{}, {}] }
    const wednesday = { date: '2026-08-05', bookings: [{}, {}] }

    expect(dayPackedPages([monday, tuesday, wednesday])).toEqual([[monday, tuesday], [wednesday]])
  })

  it('keeps an oversized day whole and emits an empty input as no pages', () => {
    const oversizedDay = { date: '2026-08-05', bookings: [{}, {}, {}, {}, {}, {}, {}] }
    const followingDay = { date: '2026-08-06', bookings: [{}] }

    expect(dayPackedPages([oversizedDay, followingDay])).toEqual([[oversizedDay], [followingDay]])
    expect(dayPackedPages([])).toEqual([])
  })
})
