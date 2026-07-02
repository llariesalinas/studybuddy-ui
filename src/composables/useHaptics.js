export const HAPTIC_PATTERNS = {
  light: 12,
  medium: 30,
  celebratory: [18, 40, 18, 40, 60],
}

export function useHaptics() {
  const vibrate = (pattern = HAPTIC_PATTERNS.light) => {
    if (typeof navigator === 'undefined' || typeof navigator.vibrate !== 'function') {
      return false
    }

    try {
      return navigator.vibrate(pattern)
    } catch {
      return false
    }
  }

  return {
    vibrate,
    patterns: HAPTIC_PATTERNS,
  }
}
