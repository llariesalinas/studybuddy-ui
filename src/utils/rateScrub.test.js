import { describe, expect, it } from 'vitest'
import { computeScrubbedRate } from './rateScrub'

describe('computeScrubbedRate', () => {
  it('adds one PHP per pixel of rightward drag', () => {
    expect(computeScrubbedRate(250, 50)).toBe(300)
  })

  it('subtracts one PHP per pixel of leftward drag', () => {
    expect(computeScrubbedRate(250, -50)).toBe(200)
  })

  it('rounds fractional drag deltas to the nearest whole PHP', () => {
    expect(computeScrubbedRate(250, 10.6)).toBe(261)
    expect(computeScrubbedRate(250, 10.4)).toBe(260)
  })

  it('clamps at zero instead of going negative', () => {
    expect(computeScrubbedRate(10, -500)).toBe(0)
  })

  it('is a no-op for zero delta', () => {
    expect(computeScrubbedRate(250, 0)).toBe(250)
  })
})
