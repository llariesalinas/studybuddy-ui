// Shared helpers for building and downloading CSV files in the browser.
//
// The SuperAdmin exports come from two places: the analytics report is rendered server-side and
// streamed back as a blob, while the user directory is built here from data the store already
// holds. Both end up going through downloadCsv() so the download mechanics live in one place.
//
// Date stamps use todayKey() rather than toISOString(), which would name a file with yesterday's
// date for anyone east of UTC (the app's users are in Manila, UTC+8).

import { todayKey } from './time.js'

const CSV_MIME_TYPE = 'text/csv'
const FIELDS_NEEDING_QUOTES = /[",\r\n]/

// Excel and Sheets treat a leading =, +, - or @ as the start of a formula, so a display name like
// "=cmd" would execute on open. Prefixing with a single quote keeps the value readable as text.
const FORMULA_PREFIXES = ['=', '+', '-', '@']

export const escapeCsvValue = (value) => {
  if (value === null || value === undefined) return ''

  let text = String(value)
  if (FORMULA_PREFIXES.includes(text[0])) text = `'${text}`
  if (!FIELDS_NEEDING_QUOTES.test(text)) return text

  return `"${text.replace(/"/g, '""')}"`
}

export const buildCsv = (rows) =>
  rows.map((row) => row.map(escapeCsvValue).join(',')).join('\r\n')

export const downloadCsv = (filename, contents) => {
  const blob = contents instanceof Blob ? contents : new Blob([contents], { type: CSV_MIME_TYPE })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')

  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

// studybuddy-<label>-YYYY-MM-DD.<ext>. Callers pass the single selected item's slug when exactly
// one is selected, so a folder of exports stays self-describing. The analytics report comes back
// from the server as an xlsx workbook; the user directory is still built here as csv.
export const exportFilename = (label, extension = 'csv') =>
  `studybuddy-${label}-${todayKey()}.${extension}`
