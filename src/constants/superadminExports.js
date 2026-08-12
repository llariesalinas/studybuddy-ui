// Definitions for the two SuperAdmin exports that go through SbExportModal.
//
// Each entry is one tickable item in the modal: `label` is what the admin reads and what the
// preview manifest lists, `fileLabel` names the downloaded file when that item is the only one
// ticked, and `id` is the wire value.

import { getDateKey } from '../utils/time.js'

// Section slugs must match the keys AdminAnalyticsExportView writes, since they are sent verbatim
// as the `sections` query param.
export const REPORT_SECTIONS = [
  { id: 'summary', label: 'Summary', fileLabel: 'summary' },
  { id: 'sessions_over_time', label: 'Sessions Over Time', fileLabel: 'sessions' },
  { id: 'top_tutors', label: 'Top Tutors', fileLabel: 'top-tutors' },
  { id: 'subject_popularity', label: 'Subject Popularity', fileLabel: 'subjects' },
  { id: 'transactions', label: 'Booking Transactions', fileLabel: 'transactions' },
]

export const REPORT_COMBINED_FILE_LABEL = 'report'
export const USERS_FILE_LABEL = 'users'

const yesNo = (value) => (value ? 'Yes' : 'No')

// Dates go through getDateKey so a Manila-evening signup is not stamped with the next UTC day.
const dateOnly = (value) => {
  if (!value) return ''
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? '' : getDateKey(parsed)
}

// Column groups for the user directory export. Fields come from AdminUserSerializer; tutor-only
// values are blank for tutees rather than zero, so an empty cell reads as "not applicable".
export const USER_COLUMN_GROUPS = [
  {
    id: 'identity',
    label: 'Identity',
    fileLabel: 'users-identity',
    columns: [
      { header: 'Name', value: (user) => user.full_name },
      { header: 'Email', value: (user) => user.email },
      { header: 'Role', value: (user) => user.role },
    ],
  },
  {
    id: 'institution_status',
    label: 'Institution & Status',
    fileLabel: 'users-status',
    columns: [
      { header: 'Institution', value: (user) => user.institution_name || 'Unassigned' },
      { header: 'Status', value: (user) => (user.is_suspended ? 'Suspended' : 'Active') },
      { header: 'Profile Completed', value: (user) => yesNo(user.profile_completed) },
      { header: 'Domain Exempt', value: (user) => yesNo(user.is_domain_exempt) },
      { header: 'Joined', value: (user) => dateOnly(user.created_at) },
    ],
  },
  {
    id: 'tutor_metrics',
    label: 'Tutor Metrics',
    fileLabel: 'users-tutor-metrics',
    columns: [
      { header: 'Sessions Completed', value: (user) => tutorValue(user, 'tutor_sessions_completed') },
      { header: 'Average Rating', value: (user) => tutorValue(user, 'tutor_avg_rating') },
      { header: 'Session Load Limit', value: (user) => tutorValue(user, 'tutor_session_load_limit') },
      { header: 'Accepted Session Load', value: (user) => tutorValue(user, 'tutor_accepted_session_load') },
      { header: 'Session Load Remaining', value: (user) => tutorValue(user, 'tutor_session_load_remaining') },
    ],
  },
  {
    id: 'wallet',
    label: 'Wallet',
    fileLabel: 'users-wallet',
    columns: [
      { header: 'Wallet Balance', value: (user) => tutorValue(user, 'wallet_balance') },
    ],
  },
]

function tutorValue(user, field) {
  if (user.role !== 'Tutor') return ''
  const value = user[field]
  return value === null || value === undefined ? '' : value
}
