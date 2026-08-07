const normalizedStatus = (value) =>
  String(value || '')
    .trim()
    .toLowerCase()

export const splitBookingsByAttention = (bookings) => {
  const requests = []
  const payments = []
  const schedule = []

  bookings.forEach((booking) => {
    const rawStatus = normalizedStatus(booking?.raw_status)
    const status = normalizedStatus(booking?.status)

    if (rawStatus === 'pending') {
      requests.push(booking)
      return
    }

    if (status === 'payment required' || rawStatus === 'awaiting payment verification') {
      payments.push(booking)
    }

    schedule.push(booking)
  })

  return { requests, payments, schedule }
}

export const groupByDate = (bookings) => {
  const groupedBookings = new Map()

  bookings.forEach((booking) => {
    const date = booking?.date || ''
    const dayBookings = groupedBookings.get(date) || []

    dayBookings.push(booking)
    groupedBookings.set(date, dayBookings)
  })

  return [...groupedBookings.entries()]
    .sort(([firstDate], [secondDate]) => firstDate.localeCompare(secondDate))
    .map(([date, dayBookings]) => ({
      date,
      bookings: [...dayBookings].sort((firstBooking, secondBooking) =>
        String(firstBooking?.startTime || '').localeCompare(String(secondBooking?.startTime || '')),
      ),
    }))
}

export const dayPackedPages = (dayGroups, target = 6) => {
  const pages = []
  let page = []
  let bookingCount = 0

  dayGroups.forEach((dayGroup) => {
    const dayBookingCount = dayGroup.bookings.length

    if (page.length && bookingCount + dayBookingCount > target) {
      pages.push(page)
      page = []
      bookingCount = 0
    }

    page.push(dayGroup)
    bookingCount += dayBookingCount
  })

  if (page.length) {
    pages.push(page)
  }

  return pages
}
