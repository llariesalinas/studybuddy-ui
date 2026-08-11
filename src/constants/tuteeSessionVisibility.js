// Statuses the tutee's own session surfaces no longer show. The API keeps sending them -- Pending
// and Rejected are stored Booking.STATUS_CHOICES values that get_display_status passes through
// verbatim -- so every tutee-facing list has to filter them out rather than assume they never
// arrive. Keyed on the display `status` field; the tutor side reads `raw_status` instead.
export const TUTEE_HIDDEN_SESSION_STATUSES = ['pending', 'rejected']

export const isHiddenFromTutee = (session) =>
  TUTEE_HIDDEN_SESSION_STATUSES.includes(String(session?.status || '').toLowerCase())
