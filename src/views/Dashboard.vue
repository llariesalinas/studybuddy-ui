<template>
  <div class="dashboard-content">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">Welcome back, Student!</h2>
      <p class="text-muted">Here's your tutoring overview for today.</p>
    </div>

    <div class="row g-4 mb-5">
      <div class="col-md-3">
        <div class="card border-sb border-1 shadow-sm h-100 rounded-4">
          <div class="card-body d-flex align-items-center">
            <div class="rounded p-3 bg-success bg-opacity-10 me-3">
              <i class="bi bi-calendar-event text-sb-primary fs-5"></i>
            </div>
            <div>
              <p class="text-muted small mb-0">Upcoming Sessions</p>
              <h3 class="fw-bold mb-0">2</h3>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-sb border-1 shadow-sm h-100 rounded-4">
          <div class="card-body d-flex align-items-center">
            <div class="rounded p-3 bg-success bg-opacity-10 me-3">
              <i class="bi bi-book text-sb-primary fs-5"></i>
            </div>
            <div>
              <p class="text-muted small mb-0">Completed Sessions</p>
              <h3 class="fw-bold mb-0">3</h3>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-sb border-1 shadow-sm h-100 rounded-4">
          <div class="card-body d-flex align-items-center">
            <div class="rounded p-3 bg-warning bg-opacity-10 me-3">
              <i class="bi bi-star text-warning fs-5"></i>
            </div>
            <div>
              <p class="text-muted small mb-0">Average Rating</p>
              <h3 class="fw-bold mb-0">4.7</h3>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-sb border-1 shadow-sm h-100 rounded-4">
          <div class="card-body d-flex align-items-center">
            <div class="rounded p-3 bg-info bg-opacity-10 me-3">
              <i class="bi bi-graph-up-arrow text-info fs-5"></i>
            </div>
            <div>
              <p class="text-muted small mb-0">Total Earnings</p>
              <h3 class="fw-bold mb-0">₱495</h3>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-md-6">
        <div class="card border-sb border-1 shadow-sm rounded-4">
          <div class="card-body p-4">
            <h5 class="fw-bold mb-4 d-flex align-items-center">
              <i class="bi bi-clock text-sb-primary me-2"></i> Upcoming Sessions
            </h5>

            <div
              class="d-flex justify-content-between align-items-center border border-sb rounded-3 p-3 mb-3"
            >
              <div>
                <h6 class="fw-bold mb-1">Calculus</h6>
                <small class="text-muted">with Maria Santos</small>
              </div>
              <div class="text-end">
                <h6 class="fw-bold mb-1">2026-02-20</h6>
                <small class="text-muted">10:00 AM</small>
              </div>
            </div>

            <div
              class="d-flex justify-content-between align-items-center border border-sb rounded-3 p-3"
            >
              <div>
                <h6 class="fw-bold mb-1">Data Structures</h6>
                <small class="text-muted">with Carlos Tan</small>
              </div>
              <div class="text-end">
                <h6 class="fw-bold mb-1">2026-02-18</h6>
                <small class="text-muted">2:00 PM</small>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-6">
        <div class="card border-sb border-1 shadow-sm rounded-4 h-100">
          <div class="card-body p-4">
            <h5 class="fw-bold mb-4 d-flex align-items-center">
              <i class="bi bi-star text-warning me-2"></i> Recent Sessions
            </h5>

            <div
              class="d-flex justify-content-between align-items-center border border-sb rounded-3 p-3 mb-3"
            >
              <div>
                <h6 class="fw-bold mb-1">Academic Writing</h6>
                <small class="text-muted">Anna Cruz</small>
              </div>
              <div class="d-flex gap-2">
                <span class="badge bg-light text-dark border"
                  ><i class="bi bi-star-fill text-dark small me-1"></i>5</span
                >
                <span class="badge bg-light text-dark border">₱130</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
