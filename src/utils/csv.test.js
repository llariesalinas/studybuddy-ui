import { describe, expect, it } from 'vitest'
import { buildCsv, escapeCsvValue, exportFilename } from './csv.js'
import { todayKey } from './time.js'

describe('escapeCsvValue', () => {
  it('returns an empty string for null and undefined', () => {
    expect(escapeCsvValue(null)).toBe('')
    expect(escapeCsvValue(undefined)).toBe('')
  })

  it('leaves plain values untouched', () => {
    expect(escapeCsvValue('Juan Dela Cruz')).toBe('Juan Dela Cruz')
    expect(escapeCsvValue(42)).toBe('42')
    expect(escapeCsvValue(0)).toBe('0')
  })

  it('quotes values containing a comma, a quote, or a newline', () => {
    expect(escapeCsvValue('Cruz, Juan')).toBe('"Cruz, Juan"')
    expect(escapeCsvValue('He said "hi"')).toBe('"He said ""hi"""')
    expect(escapeCsvValue('line one\nline two')).toBe('"line one\nline two"')
  })

  it('neutralises values a spreadsheet would read as a formula', () => {
    expect(escapeCsvValue('=1+1')).toBe("'=1+1")
    expect(escapeCsvValue('@handle')).toBe("'@handle")
    expect(escapeCsvValue('-5')).toBe("'-5")
  })
})

describe('buildCsv', () => {
  it('joins cells with commas and rows with CRLF', () => {
    const csv = buildCsv([
      ['Name', 'Role'],
      ['Ana', 'Tutor'],
      ['Cruz, Juan', 'Tutee'],
    ])

    expect(csv).toBe('Name,Role\r\nAna,Tutor\r\n"Cruz, Juan",Tutee')
  })

  it('returns an empty string for no rows', () => {
    expect(buildCsv([])).toBe('')
  })
})

describe('exportFilename', () => {
  it('stamps the local date, not the UTC one', () => {
    expect(exportFilename('users')).toBe(`studybuddy-users-${todayKey()}.csv`)
  })

  it('takes an extension, so the analytics workbook is not named .csv', () => {
    expect(exportFilename('report', 'xlsx')).toBe(`studybuddy-report-${todayKey()}.xlsx`)
  })
})
