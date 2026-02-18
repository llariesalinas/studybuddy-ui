<template>
  <div class="find-tutors-content">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">Find Tutors</h2>
      <p class="text-muted">Browse peer tutors matched to your learning needs.</p>
    </div>

    <div class="row mb-4 g-3">
      <div class="col-md-9">
        <div class="input-group shadow-sm border-sb rounded-3 overflow-hidden">
          <span class="input-group-text bg-white border-0 ps-3">
            <i class="bi bi-search text-muted"></i>
          </span>
          <input type="text" class="form-control border-0 py-2 shadow-none" placeholder="Search by name or subject...">
        </div>
      </div>
      <div class="col-md-3">
        <div class="input-group shadow-sm border-sb rounded-3 overflow-hidden">
          <span class="input-group-text bg-white border-0 ps-3">
            <i class="bi bi-funnel text-muted"></i>
          </span>
          <select class="form-select border-0 py-2 shadow-none text-muted">
            <option selected>All Subjects</option>
            <option value="1">Mathematics</option>
            <option value="2">Sciences</option>
            <option value="3">Humanities</option>
          </select>
        </div>
      </div>
    </div>

    <div class="row g-4">
      
      <div class="col-md-6 col-xl-4">
        <div class="card border-sb shadow-sm h-100 rounded-4 p-2">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <div class="d-flex align-items-center gap-3">
                <div class="rounded-circle bg-success bg-opacity-25 text-sb-primary d-flex justify-content-center align-items-center fw-bold" style="width: 48px; height: 48px;">
                  MS
                </div>
                <div>
                  <h6 class="fw-bold mb-0">Maria Santos</h6>
                  <small class="text-muted" style="font-size: 0.8rem;">3rd Year · Mathematics</small>
                </div>
              </div>
              <div class="d-flex align-items-center text-warning fw-bold">
                <i class="bi bi-star-fill me-1 small"></i> 4.9
              </div>
            </div>

            <p class="text-muted small mb-3" style="min-height: 40px;">
              3rd year Mathematics major passionate about making complex concepts accessible.
            </p>

            <div class="d-flex flex-wrap gap-2 mb-4">
              <span class="badge bg-light text-dark border fw-normal px-2 py-1">Calculus</span>
              <span class="badge bg-light text-dark border fw-normal px-2 py-1">Linear Algebra</span>
              <span class="badge bg-light text-dark border fw-normal px-2 py-1">Statistics</span>
            </div>

            <hr class="border-sb">
            <div class="d-flex justify-content-between align-items-center mt-3">
              <div>
                <span class="fw-bold">₱150</span><span class="text-muted small">/hr</span>
                <span class="text-muted small ms-2">· 87 sessions</span>
              </div>
              <button class="btn bg-sb-primary text-white px-3 py-1 rounded-3 small fw-semibold shadow-sm">
                Book Session
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-6 col-xl-4">
        <div class="card border-sb shadow-sm h-100 rounded-4 p-2">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <div class="d-flex align-items-center gap-3">
                <div class="rounded-circle bg-success bg-opacity-25 text-sb-primary d-flex justify-content-center align-items-center fw-bold" style="width: 48px; height: 48px;">
                  JR
                </div>
                <div>
                  <h6 class="fw-bold mb-0">James Reyes</h6>
                  <small class="text-muted" style="font-size: 0.8rem;">4th Year · Engineering</small>
                </div>
              </div>
              <div class="d-flex align-items-center text-warning fw-bold">
                <i class="bi bi-star-fill me-1 small"></i> 4.7
              </div>
            </div>
            <p class="text-muted small mb-3" style="min-height: 40px;">
              Engineering student who loves breaking down science problems step by step.
            </p>
            <div class="d-flex flex-wrap gap-2 mb-4">
              <span class="badge bg-light text-dark border fw-normal px-2 py-1">Physics</span>
              <span class="badge bg-light text-dark border fw-normal px-2 py-1">Chemistry</span>
              <span class="badge bg-light text-dark border fw-normal px-2 py-1">Thermodynamics</span>
            </div>
            <hr class="border-sb">
            <div class="d-flex justify-content-between align-items-center mt-3">
              <div>
                <span class="fw-bold">₱140</span><span class="text-muted small">/hr</span>
                <span class="text-muted small ms-2">· 52 sessions</span>
              </div>
              <button class="btn bg-sb-primary text-white px-3 py-1 rounded-3 small fw-semibold shadow-sm">
                Book Session
              </button>
            </div>
          </div>
        </div>
      </div>

      </div>
  </div>
</template>

<style scoped>
/* Minor tweaks to ensure inputs match your Figma styling */
.form-control:focus, .form-select:focus {
  border-color: transparent;
  box-shadow: none;
}
</style>