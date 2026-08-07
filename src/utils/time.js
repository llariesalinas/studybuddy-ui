// Shared time helpers for the booking search filters.
//
// These were previously copy-pasted across InitialBooking.vue, FindTutors.vue, and
// BookingTimePicker.vue. Times are handled as plain 'HH:mm' strings and dates as 'YYYY-MM-DD'
// keys built from *local* date parts -- never via toISOString(), which would shift the day for
// anyone east of UTC (the app's users are in Manila, UTC+8).

export const padNumber = (value) => String(value).padStart(2, '0')

export const timeToMinutes = (time) => {
  const [hours = 0, minutes = 0] = String(time || '00:00')
    .split(':')
    .map(Number)

  return hours * 60 + minutes
}

export const getDateKey = (date) => {
  return `${date.getFullYear()}-${padNumber(date.getMonth() + 1)}-${padNumber(date.getDate())}`
}

export const todayKey = () => getDateKey(new Date())

// The current minute, rounded up when any seconds have elapsed, so a slot starting at the
// current minute counts as already gone.
export const currentComparableMinutes = () => {
  const now = new Date()
  return now.getHours() * 60 + now.getMinutes() + (now.getSeconds() > 0 ? 1 : 0)
}

const formatTimeParts = (time) => {
  const totalMinutes = timeToMinutes(time)
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60

  return {
    clock: `${hours % 12 || 12}:${padNumber(minutes)}`,
    period: hours >= 12 ? 'PM' : 'AM',
  }
}

export const formatTimeLabel = (time) => {
  if (!time) {
    return ''
  }

  const { clock, period } = formatTimeParts(time)
  return `${clock} ${period}`
}

// Drops the redundant period from the start when both bounds share one:
// '9:00 - 11:00 AM' rather than '9:00 AM - 11:00 AM'.
export const formatTimeRangeLabel = (startTime, endTime) => {
  if (!startTime || !endTime) {
    return ''
  }

  const start = formatTimeParts(startTime)
  const end = formatTimeParts(endTime)

  if (start.period === end.period) {
    return `${start.clock} - ${end.clock} ${end.period}`
  }

  return `${start.clock} ${start.period} - ${end.clock} ${end.period}`
}

export const formatDurationLabel = (startTime, endTime) => {
  if (!startTime || !endTime) {
    return ''
  }

  const minutes = timeToMinutes(endTime) - timeToMinutes(startTime)

  if (minutes <= 0) {
    return ''
  }

  const hours = minutes / 60
  const rounded = Number.isInteger(hours) ? hours : Number(hours.toFixed(1))

  return `${rounded} ${rounded === 1 ? 'hr' : 'hrs'}`
}

export const isPastDate = (date) => Boolean(date) && date < todayKey()

export const isPastTimeForDate = (date, time) => {
  return (
    Boolean(date && time) && date === todayKey() && timeToMinutes(time) < currentComparableMinutes()
  )
}
