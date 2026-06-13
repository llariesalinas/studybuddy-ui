<template>
  <div class="superadmin-dashboard p-4">
    <!-- Error Alert -->
    <div v-if="store.error.stats" class="alert alert-danger border-0 shadow-sm rounded-4 mb-4 d-flex align-items-center">
      <i class="bi bi-exclamation-triangle-fill fs-4 me-3"></i>
      <div>
        <p class="mb-0 fw-bold">Failed to load platform data</p>
        <p class="small mb-0">{{ store.error.stats }}</p>
      </div>
      <button @click="store.fetchStats(true)" class="btn btn-sm btn-danger ms-auto rounded-pill px-3 sb-btn">Retry</button>
    </div>

    <!-- Health Widgets -->
    <div class="row g-4 mb-5">
      <div class="col-md-3">
        <div class="card border-0 sb-card-surface shadow-sm rounded-4 p-3 h-100">
          <div class="d-flex align-items-center mb-2">
            <div class="icon-box bg-primary-subtle text-primary rounded-3 me-3 p-2">
              <i class="bi bi-people-fill fs-4"></i>
            </div>
            <p class="sb-muted small fw-bold mb-0">TOTAL USERS</p>
          </div>
          <Transition name="fade" mode="out-in">
            <div v-if="store.loading.stats" class="placeholder-glow">
              <h2 class="placeholder col-6 rounded mb-2"></h2>
              <p class="placeholder col-8 rounded mb-0"></p>
            </div>
            <div v-else>
              <h2 class="fw-bold mb-0">{{ (store.stats?.total_tutors || 0) + (store.stats?.total_tutees || 0) }}</h2>
              <p class="small sb-muted mb-0">
                <span class="text-primary fw-bold">{{ store.stats?.total_tutors }}</span> tutors /
                <span class="text-info fw-bold">{{ store.stats?.total_tutees }}</span> tutees
              </p>
            </div>
          </Transition>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-0 sb-card-surface shadow-sm rounded-4 p-3 h-100">
          <div class="d-flex align-items-center mb-2">
            <div class="icon-box bg-info-subtle text-info rounded-3 me-3 p-2">
              <i class="bi bi-building fs-4"></i>
            </div>
            <p class="sb-muted small fw-bold mb-0">INSTITUTIONS</p>
          </div>
          <Transition name="fade" mode="out-in">
            <div v-if="store.loading.institutionPerformance" class="placeholder-glow">
              <h2 class="placeholder col-4 rounded mb-2"></h2>
              <p class="placeholder col-9 rounded mb-0"></p>
            </div>
            <div v-else>
              <h2 class="fw-bold mb-0">{{ store.institutionPerformance.length }}</h2>
              <p class="small sb-muted mb-0">Active partner institutions</p>
            </div>
          </Transition>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-0 sb-card-surface shadow-sm rounded-4 p-3 h-100">
          <div class="d-flex align-items-center mb-2">
            <div class="icon-box bg-success-subtle text-success rounded-3 me-3 p-2">
              <i class="bi bi-calendar-check fs-4"></i>
            </div>
            <p class="sb-muted small fw-bold mb-0">SESSIONS TODAY</p>
          </div>
          <Transition name="fade" mode="out-in">
            <div v-if="store.loading.stats" class="placeholder-glow">
              <h2 class="placeholder col-4 rounded mb-2"></h2>
              <p class="placeholder col-9 rounded mb-0"></p>
            </div>
            <div v-else>
              <h2 class="fw-bold mb-0">{{ store.stats?.active_sessions_today }}</h2>
              <p class="small sb-muted mb-0">Currently active confirmed sessions</p>
            </div>
          </Transition>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-0 sb-card-surface shadow-sm rounded-4 p-3 h-100">
          <div class="d-flex align-items-center mb-2">
            <div class="icon-box bg-warning-subtle text-warning rounded-3 me-3 p-2">
              <i class="bi bi-wallet2 fs-4"></i>
            </div>
            <p class="sb-muted small fw-bold mb-0">COMMISSIONS (MTD)</p>
          </div>
          <Transition name="fade" mode="out-in">
            <div v-if="store.loading.stats" class="placeholder-glow">
              <h2 class="placeholder col-7 rounded mb-2"></h2>
              <p class="placeholder col-8 rounded mb-0"></p>
            </div>
            <div v-else>
              <h2 class="fw-bold mb-0">₱{{ store.stats?.commissions_this_month?.toLocaleString() }}</h2>
              <p class="small sb-muted mb-0">Total platform fees this month</p>
            </div>
          </Transition>
        </div>
      </div>
    </div>

    <div class="row g-4 mb-5">
      <!-- Activity Feed -->
      <div class="col-lg-8">
        <div class="card border-0 sb-card-surface shadow-sm rounded-4 p-4 h-100">
          <h5 class="fw-bold sb-text mb-4">Recent Platform Activity</h5>
          <Transition name="fade" mode="out-in">
            <div v-if="store.loading.stats" class="activity-timeline placeholder-glow">
              <div v-for="i in 5" :key="'activity-skeleton-' + i" class="activity-item d-flex mb-4">
                <div class="activity-icon me-3 mt-1">
                  <div class="placeholder rounded-circle" style="width: 20px; height: 20px;"></div>
                </div>
                <div class="activity-content flex-grow-1">
                  <p class="placeholder col-8 rounded mb-1"></p>
                  <p class="placeholder col-4 rounded small mb-0"></p>
                </div>
              </div>
            </div>
            <div v-else-if="store.stats?.recent_activity?.length" class="activity-timeline">
              <div v-for="act in store.stats.recent_activity" :key="act.id" class="activity-item d-flex mb-4">
                <div class="activity-icon me-3 mt-1">
                  <i :class="getActivityIcon(act.activity_type)" class="fs-5"></i>
                </div>
                <div class="activity-content">
                  <p class="mb-1 fw-semibold sb-text">{{ act.message }}</p>
                  <p class="small sb-muted mb-0">{{ formatDate(act.created_at) }}</p>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-5 sb-muted">
              <i class="bi bi-activity fs-1 mb-2 d-block"></i>
              <p>No recent activity detected.</p>
            </div>
          </Transition>
        </div>
      </div>

      <!-- Quick Actions + Institution Performance Summary -->
      <div class="col-lg-4">
        <div class="card border-0 sb-card-surface shadow-sm rounded-4 p-4 mb-4">
          <h5 class="fw-bold sb-text mb-4">Quick Actions</h5>
          <div class="d-grid gap-3">
            <router-link to="/superadmin/institutions" class="btn action-surface border-0 text-start rounded-3 p-3 shadow-none position-relative sb-btn">
              <div class="d-flex align-items-center">
                <i class="bi bi-building fs-4 me-3 text-primary"></i>
                <div>
                  <p class="fw-bold mb-0">Manage Institutions</p>
                  <p class="small sb-muted mb-0">Add, toggle, and configure partners</p>
                </div>
              </div>
            </router-link>

            <router-link to="/superadmin/users" class="btn action-surface border-0 text-start rounded-3 p-3 shadow-none sb-btn">
              <div class="d-flex align-items-center">
                <i class="bi bi-shield-lock fs-4 me-3 text-warning"></i>
                <div>
                  <p class="fw-bold mb-0">All Users</p>
                  <p class="small sb-muted mb-0">View and manage every platform user</p>
                </div>
              </div>
            </router-link>

            <router-link to="/superadmin/reports" class="btn action-surface border-0 text-start rounded-3 p-3 shadow-none sb-btn">
              <div class="d-flex align-items-center">
                <i class="bi bi-bar-chart-line fs-4 me-3 text-info"></i>
                <div>
                  <p class="fw-bold mb-0">Platform Reports</p>
                  <p class="small sb-muted mb-0">Cross-institution analytics</p>
                </div>
              </div>
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Institution Performance Table -->
    <div class="card border-0 sb-card-surface shadow-sm rounded-4 overflow-hidden">
      <div class="p-4 border-bottom d-flex justify-content-between align-items-center" style="border-color: var(--sb-card-border) !important;">
        <h5 class="fw-bold sb-text mb-0">Institution Performance Overview</h5>
        <router-link to="/superadmin/reports" class="btn btn-sm btn-light rounded-pill px-3 sb-btn">
          Full Reports <i class="bi bi-arrow-right ms-1"></i>
        </router-link>
      </div>
      <div class="table-responsive">
        <table class="table align-middle mb-0">
          <thead>
            <tr>
              <th class="ps-4 py-3 border-0 bg-transparent text-uppercase small fw-bold sb-muted">Institution</th>
              <th class="py-3 border-0 bg-transparent text-uppercase small fw-bold sb-muted text-center">Tutors</th>
              <th class="py-3 border-0 bg-transparent text-uppercase small fw-bold sb-muted text-center">Tutees</th>
              <th class="py-3 border-0 bg-transparent text-uppercase small fw-bold sb-muted text-center">Completed</th>
              <th class="py-3 border-0 bg-transparent text-uppercase small fw-bold sb-muted text-center">Avg Rating</th>
              <th class="pe-4 py-3 border-0 bg-transparent text-uppercase small fw-bold sb-muted text-end">Commission</th>
            </tr>
          </thead>
          <tbody>
            <template v-if="store.loading.institutionPerformance">
              <tr v-for="i in 4" :key="'perf-sk-' + i" class="placeholder-glow">
                <td class="ps-4"><span class="placeholder col-8 rounded"></span></td>
                <td class="text-center"><span class="placeholder col-4 rounded"></span></td>
                <td class="text-center"><span class="placeholder col-4 rounded"></span></td>
                <td class="text-center"><span class="placeholder col-4 rounded"></span></td>
                <td class="text-center"><span class="placeholder col-5 rounded"></span></td>
                <td class="pe-4 text-end"><span class="placeholder col-6 rounded"></span></td>
              </tr>
            </template>
            <template v-else-if="store.institutionPerformance.length">
              <tr v-for="inst in store.institutionPerformance" :key="inst.id">
                <td class="ps-4 fw-bold sb-text">{{ inst.institution_name }}</td>
                <td class="text-center">{{ inst.tutors }}</td>
                <td class="text-center">{{ inst.tutees }}</td>
                <td class="text-center">
                  <span class="badge bg-success-subtle text-success rounded-pill px-3">{{ inst.sessions }}</span>
                </td>
                <td class="text-center">
                  <span class="text-warning fw-bold">
                    <i class="bi bi-star-fill me-1"></i>{{ inst.avg_rating > 0 ? inst.avg_rating.toFixed(1) : '—' }}
                  </span>
                </td>
                <td class="pe-4 text-end fw-bold">₱{{ inst.revenue.toLocaleString(undefined, { minimumFractionDigits: 2 }) }}</td>
              </tr>
            </template>
            <template v-else>
              <tr>
                <td colspan="6" class="text-center py-5 sb-muted">
                  <i class="bi bi-building fs-1 d-block mb-2"></i>No institution data available.
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useSuperAdminStore } from '@/stores/superadmin'

const store = useSuperAdminStore()

onMounted(() => {
  store.fetchStats(true)
  store.fetchInstitutionPerformance(true)
})

const getActivityIcon = (type) => {
  switch (type) {
    case 'registration': return 'bi bi-person-plus text-primary'
    case 'booking_completed': return 'bi bi-check-circle text-success'
    case 'institution_added': return 'bi bi-building-add text-info'
    case 'withdrawal_failed': return 'bi bi-exclamation-octagon text-danger'
    case 'withdrawal_processed': return 'bi bi-cash text-success'
    case 'admin_action': return 'bi bi-shield-check text-warning'
    default: return 'bi bi-dot text-secondary'
  }
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.superadmin-dashboard { color: var(--sb-text-main); }

.icon-box {
  width: 42px; height: 42px;
  display: flex; align-items: center; justify-content: center;
}

.activity-item { position: relative; }
.activity-timeline .activity-item:not(:last-child)::after {
  content: ''; position: absolute;
  left: 10px; top: 35px; bottom: -20px;
  width: 2px; background-color: var(--sb-bg);
}
.activity-icon { width: 20px; z-index: 1; background: var(--sb-card-bg); }

.action-surface { background-color: var(--sb-bg); color: var(--sb-text-main); }
.action-surface:hover {
  background-color: color-mix(in srgb, var(--sb-primary) 8%, var(--sb-bg)) !important;
  color: var(--sb-text-main); transform: translateY(-2px); transition: all 0.2s ease;
}

.table thead th { font-size: 0.75rem; letter-spacing: 0.05em; border-bottom: none; }
</style>
