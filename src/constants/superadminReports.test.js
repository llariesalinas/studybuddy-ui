import { describe, expect, it } from 'vitest'
import {
  REPORT_DETAIL_DATASETS,
  REPORT_PERIOD_CUSTOM,
  SORT_ASCENDING,
  SORT_DESCENDING,
  reportPeriodScopeLabel,
  sortReportRows,
} from './superadminReports.js'

const names = (rows) => rows.map((row) => row.name)

describe('sortReportRows', () => {
  const tutors = [
    { name: 'Brenda', rating: 3.54 },
    { name: 'Unrated', rating: null },
    { name: 'Sarah', rating: 4.67 },
    { name: 'Matthew', rating: 3.67 },
  ]

  it('sorts numbers descending by default', () => {
    expect(names(sortReportRows(tutors, 'rating'))).toEqual([
      'Sarah',
      'Matthew',
      'Brenda',
      'Unrated',
    ])
  })

  it('keeps blanks last when ascending, so the worst rated leads rather than the unrated', () => {
    expect(names(sortReportRows(tutors, 'rating', SORT_ASCENDING))).toEqual([
      'Brenda',
      'Matthew',
      'Sarah',
      'Unrated',
    ])
  })

  it('does not treat a missing rating as zero', () => {
    const rows = [{ name: 'Unrated', rating: null }, { name: 'OneStar', rating: 1 }]

    expect(names(sortReportRows(rows, 'rating', SORT_ASCENDING))).toEqual(['OneStar', 'Unrated'])
  })

  it('sorts strings alphabetically rather than by subtraction', () => {
    expect(names(sortReportRows(tutors, 'name', SORT_ASCENDING))).toEqual([
      'Brenda',
      'Matthew',
      'Sarah',
      'Unrated',
    ])
  })

  it('leaves the source array untouched', () => {
    const original = [...tutors]
    sortReportRows(tutors, 'rating')

    expect(tutors).toEqual(original)
  })

  it('treats an empty string as missing, not as the alphabetically smallest name', () => {
    const rows = [{ name: '' }, { name: 'Adam' }]

    expect(names(sortReportRows(rows, 'name', SORT_ASCENDING))).toEqual(['Adam', ''])
  })
})

describe('REPORT_DETAIL_DATASETS', () => {
  it('derives each subject share from the rows on the page', () => {
    const rows = REPORT_DETAIL_DATASETS.subjects.rows({
      subject_popularity: [
        { subject_name: 'Python', booking_count: 30 },
        { subject_name: 'Java', booking_count: 10 },
      ],
    })

    expect(rows.map((row) => row.share)).toEqual([0.75, 0.25])
  })

  it('does not divide by zero when nothing was booked', () => {
    const rows = REPORT_DETAIL_DATASETS.subjects.rows({
      subject_popularity: [{ subject_name: 'Python', booking_count: 0 }],
    })

    expect(rows[0].share).toBe(0)
  })

  it('survives a missing payload rather than throwing on first paint', () => {
    expect(REPORT_DETAIL_DATASETS.tutors.rows(null)).toEqual([])
    expect(REPORT_DETAIL_DATASETS.subjects.rows(undefined)).toEqual([])
  })

  it('names neither page in a way that claims completeness', () => {
    // The analytics queryset is booking-driven, so anyone idle in the window is absent. See
    // CONTEXT.md -- "All tutors" would be a lie, and this guards against it creeping back.
    const titles = Object.values(REPORT_DETAIL_DATASETS).map((entry) => entry.title)

    titles.forEach((title) => expect(title.toLowerCase()).not.toContain('all '))
  })
})

describe('reportPeriodScopeLabel', () => {
  it('spells out the terse toggle labels', () => {
    expect(reportPeriodScopeLabel('3m')).toBe('Last 3 months')
    expect(reportPeriodScopeLabel('all')).toBe('All time')
  })

  it('falls back to the raw value for an unknown period', () => {
    expect(reportPeriodScopeLabel('nonsense')).toBe('nonsense')
  })

  // "Custom range" alone would not say what the figures beneath it cover.
  it('spells out a custom window as its actual endpoints', () => {
    expect(reportPeriodScopeLabel(REPORT_PERIOD_CUSTOM, '2026-04-01', '2026-06-30')).toBe(
      'Apr 1, 2026 – Jun 30, 2026',
    )
  })

  it('renders the endpoints in local time, not shifted by UTC parsing', () => {
    // `new Date('2026-04-01')` is UTC midnight, which prints as Mar 31 west of UTC.
    expect(reportPeriodScopeLabel(REPORT_PERIOD_CUSTOM, '2026-04-01', '2026-04-01')).toContain(
      'Apr 1, 2026',
    )
  })

  it('falls back to a generic label until both endpoints are chosen', () => {
    expect(reportPeriodScopeLabel(REPORT_PERIOD_CUSTOM, '2026-04-01', '')).toBe('Custom range')
    expect(reportPeriodScopeLabel(REPORT_PERIOD_CUSTOM)).toBe('Custom range')
  })
})

describe('sort direction constants', () => {
  it('are distinct', () => {
    expect(SORT_ASCENDING).not.toBe(SORT_DESCENDING)
  })
})
