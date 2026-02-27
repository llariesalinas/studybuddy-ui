<template>
  <div class="p-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="fw-bold text-dark">Teaching Hub</h2>
      <router-link to="/tch-availability" class="btn bg-sb-primary text-white rounded-3 px-4 fw-semibold shadow-sm">
        Set Schedule
      </router-link>
    </div>

    <div class="row g-4 mb-4">
      <div class="col-md-4">
        <div class="card border-sb rounded-4 p-4 shadow-sm h-100">
          <p class="text-muted small fw-bold mb-2">TOTAL SESSIONS</p>
          <h2 class="fw-bold mb-0 text-dark">{{ totalSessions }}</h2>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card border-sb rounded-4 p-4 shadow-sm h-100">
          <p class="text-muted small fw-bold mb-2">AVG RATING</p>
          <h2 class="fw-bold mb-0 text-dark d-flex align-items-center">
            {{ avgRating }} <i class="bi bi-star-fill text-warning fs-4 ms-2"></i>
          </h2>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card border-0 rounded-4 p-4 shadow-sm h-100" style="background-color: var(--sb-dark);">
          <p class="text-white-50 small fw-bold mb-2">EARNINGS</p>
          <h2 class="fw-bold text-white mb-0">₱{{ earnings }}</h2>
        </div>
      </div>
    </div>

    <div class="card border-sb rounded-4 shadow-sm">
      <div class="card-body p-4">
        <h6 class="fw-bold text-dark mb-4">Upcoming Bookings</h6>
        <div class="table-responsive">
          <table class="table align-middle mb-0">
            <thead>
              <tr class="small fw-bold text-muted">
                <th class="border-bottom-0 pb-3">STUDENT</th>
                <th class="border-bottom-0 pb-3">SUBJECT</th>
                <th class="border-bottom-0 pb-3">DATE</th>
                <th class="border-bottom-0 pb-3">STATUS</th>
              </tr>
            </thead>
            <tbody>
            <tr v-for="booking in upcomingBookings" :key="booking.date">
    <td class="py-3 text-dark">{{ booking.student }}</td>
    <td class="py-3">
      <span class="badge bg-light text-dark border border-sb px-2 py-1">
        —
      </span>
    </td>
    <td class="py-3 text-dark">{{ booking.date }}</td>
    <td class="py-3">
      <span class="badge bg-success bg-opacity-10 text-success border border-success px-3 py-1 rounded-pill">
        {{ booking.status }}
      </span>
    </td>
  </tr>
</tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

