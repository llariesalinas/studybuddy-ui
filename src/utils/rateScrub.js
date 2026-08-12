// Pure math for the tutor onboarding hourly-rate field's click-drag "scrub" gesture
// (see docs/plans/2026-08-12-tutor-onboarding-modality-rate-redesign.md). Kept separate
// from TutorPreferenceSetup.vue so the drag arithmetic is unit-testable without mounting
// the component or simulating mouse events.

// How much the rate changes per pixel of horizontal drag.
export const PHP_PER_PIXEL = 1

// A tutor's hourly rate can't be negative.
export const MIN_HOURLY_RATE = 0

export const computeScrubbedRate = (startValue, deltaX) => {
  return Math.max(MIN_HOURLY_RATE, Math.round(startValue + deltaX * PHP_PER_PIXEL))
}
