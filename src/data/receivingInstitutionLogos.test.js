import { describe, expect, it } from 'vitest'
import { getReceivingInstitutionLogoUrl } from './receivingInstitutionLogos'

describe('getReceivingInstitutionLogoUrl', () => {
  it('returns a logo.dev URL for a mapped institution', () => {
    expect(getReceivingInstitutionLogoUrl({ name: 'GCash' })).toBe('https://img.logo.dev/gcash.com')
  })

  it('is case- and whitespace-insensitive when matching the institution name', () => {
    expect(getReceivingInstitutionLogoUrl({ name: '  BDO Unibank, Inc.  ' })).toBe(
      'https://img.logo.dev/bdo.com.ph'
    )
  })

  it('appends a publishable token when provided', () => {
    expect(getReceivingInstitutionLogoUrl({ name: 'GCash' }, 'pk_test_123')).toBe(
      'https://img.logo.dev/gcash.com?token=pk_test_123'
    )
  })

  it('returns null for an institution with no domain mapping', () => {
    expect(getReceivingInstitutionLogoUrl({ name: 'Some Unmapped Rural Bank' })).toBeNull()
  })

  it('returns null when no institution is given', () => {
    expect(getReceivingInstitutionLogoUrl(null)).toBeNull()
  })
})
