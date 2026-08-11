// Configuration for the SuperAdmin report drill-down pages, one entry per dataset.
//
// Kept beside superadminExports.js and shaped the same way on purpose: the detail view renders
// whatever these entries describe rather than hard-coding a table per dataset, so adding a third
// drill-down is a new entry plus a route, not a new component.

// Row scope understood by AdminAnalyticsView. `full` returns every ranked row; omitting the param
// leaves the endpoint on its truncated dashboard default.
export const ANALYTICS_VIEW_FULL = 'full'

// How many rows each ranked card shows on the dashboard. The server truncates independently -- this
// exists so the cards do not additionally slice at a magic number of their own.
export const REPORT_CARD_ROW_LIMIT = 5

// Column value types the detail view knows how to format and align.
export const REPORT_COLUMN_TEXT = 'text'
export const REPORT_COLUMN_NUMBER = 'number'
export const REPORT_COLUMN_RATING = 'rating'
export const REPORT_COLUMN_MONEY = 'money'
export const REPORT_COLUMN_PERCENT = 'percent'

export const SORT_ASCENDING = 'asc'
export const SORT_DESCENDING = 'desc'

// The reporting window, shared by the dashboard and both drill-down pages so a period cannot mean
// one thing on one screen and something else on the next. `label` is the terse toggle text;
// `scopeLabel` is the spelled-out form for subtitles and the export scope line, where "3M" would
// read as jargon.
export const REPORT_PERIOD_OPTIONS = [
  { label: '7D', value: '7d', scopeLabel: 'Last 7 days' },
  { label: '30D', value: '30d', scopeLabel: 'Last 30 days' },
  { label: '3M', value: '3m', scopeLabel: 'Last 3 months' },
  { label: 'All', value: 'all', scopeLabel: 'All time' },
]

export const REPORT_DEFAULT_PERIOD = '30d'

export const ALL_INSTITUTIONS_LABEL = 'All institutions'

const isMissing = (value) => value === null || value === undefined || value === ''

// Sorts a copy of `rows`, with blanks last in *both* directions.
//
// Treating a missing value as 0 would rank an unrated tutor below a genuine one-star tutor, which
// is a stronger claim than the data supports: "not rated" and "rated badly" are different facts.
// Ascending therefore shows the worst rated first, not the unrated.
export const sortReportRows = (rows, key, direction = SORT_DESCENDING) => {
  const factor = direction === SORT_ASCENDING ? 1 : -1
  return [...rows].sort((left, right) => {
    const a = left[key]
    const b = right[key]
    if (isMissing(a) && isMissing(b)) return 0
    if (isMissing(a)) return 1
    if (isMissing(b)) return -1
    if (typeof a === 'string' || typeof b === 'string') {
      return String(a).localeCompare(String(b)) * factor
    }
    return (a - b) * factor
  })
}

export const reportPeriodScopeLabel = (value) =>
  REPORT_PERIOD_OPTIONS.find((option) => option.value === value)?.scopeLabel || value

// Both pages are titled for what the query actually returns. The analytics queryset is
// booking-driven, so a tutor or subject with no completed session in the window is absent
// entirely -- neither page may claim to list "all" of anything. See CONTEXT.md.
export const REPORT_DETAIL_DATASETS = {
  tutors: {
    slug: 'tutors',
    routeName: 'superadmin-report-tutors',
    eyebrow: 'Tutors',
    title: 'Tutor performance',
    // Reads as "159 tutors with sessions", stating the population rather than implying a roster.
    countNoun: 'tutors with sessions',
    totalKey: 'tutor_total',
    exportSection: 'top_tutors',
    // Matches the fileLabel REPORT_SECTIONS uses for this section, so a workbook exported from the
    // detail page is named the same as the equivalent tick in the dashboard's export modal.
    exportFileLabel: 'top-tutors',
    searchPlaceholder: 'Search tutor',
    searchKey: 'name',
    emptyMessage: 'No tutor completed a session in this period.',
    defaultSort: { key: 'sessions', direction: SORT_DESCENDING },
    rows: (payload) =>
      (payload?.top_tutors || []).map((row) => ({
        name: row.name,
        sessions: row.sessions,
        rating: row.rating,
        earnings: row.earnings,
      })),
    columns: [
      { key: 'name', header: 'Tutor', type: REPORT_COLUMN_TEXT },
      { key: 'sessions', header: 'Sessions', type: REPORT_COLUMN_NUMBER },
      { key: 'rating', header: 'Rating', type: REPORT_COLUMN_RATING },
      { key: 'earnings', header: 'Earnings', type: REPORT_COLUMN_MONEY },
    ],
  },
  subjects: {
    slug: 'subjects',
    routeName: 'superadmin-report-subjects',
    eyebrow: 'Demand',
    title: 'Subject popularity',
    countNoun: 'subjects with bookings',
    totalKey: 'subject_total',
    exportSection: 'subject_popularity',
    exportFileLabel: 'subjects',
    searchPlaceholder: 'Search subject',
    searchKey: 'subject_name',
    emptyMessage: 'No subject was booked in this period.',
    defaultSort: { key: 'booking_count', direction: SORT_DESCENDING },
    // Share is derived here rather than fetched: the percentages are of the rows on this page, and
    // computing them from the payload keeps them consistent with the list even when it is filtered
    // server-side by institution.
    rows: (payload) => {
      const raw = payload?.subject_popularity || []
      const total = raw.reduce((sum, item) => sum + (item.booking_count || 0), 0)
      return raw.map((item) => ({
        subject_name: item.subject_name,
        booking_count: item.booking_count,
        share: total ? item.booking_count / total : 0,
      }))
    },
    columns: [
      { key: 'subject_name', header: 'Subject', type: REPORT_COLUMN_TEXT },
      { key: 'booking_count', header: 'Bookings', type: REPORT_COLUMN_NUMBER },
      { key: 'share', header: 'Share', type: REPORT_COLUMN_PERCENT },
    ],
  },
}
