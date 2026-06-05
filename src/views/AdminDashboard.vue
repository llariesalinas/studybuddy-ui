<template>
  <div class="admin-dashboard p-4">
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

      <div class="col-md-3">
        <div class="card border-0 sb-card-surface shadow-sm rounded-4 p-3 h-100">
          <div class="d-flex align-items-center mb-2">
            <div class="icon-box bg-danger-subtle text-danger rounded-3 me-3 p-2">
              <i class="bi bi-exclamation-triangle fs-4"></i>
            </div>
            <p class="sb-muted small fw-bold mb-0">PENDING ACTIONS</p>
          </div>
          <Transition name="fade" mode="out-in">
            <div v-if="store.loading.stats" class="placeholder-glow">
              <h2 class="placeholder col-5 rounded mb-2 text-danger"></h2>
              <p class="placeholder col-10 rounded mb-0"></p>
            </div>
            <div v-else>
              <h2 class="fw-bold mb-0 text-danger">{{ store.stats?.failed_withdrawals || 0 }}</h2>
              <p class="small sb-muted mb-0">Failed cash-outs needing attention</p>
            </div>
          </Transition>
        </div>
      </div>
    </div>

    <div class="row g-4">
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

      <!-- Quick Actions -->
      <div class="col-lg-4">
        <div class="card border-0 sb-card-surface shadow-sm rounded-4 p-4 mb-4">
          <h5 class="fw-bold sb-text mb-4">Quick Actions</h5>
          <div class="d-grid gap-3">
            <router-link to="/admin/institutions" class="btn action-surface border-0 text-start rounded-3 p-3 shadow-none position-relative sb-btn">
              <div class="d-flex align-items-center">
                <i class="bi bi-building fs-4 me-3 text-primary"></i>
                <div>
                  <p class="fw-bold mb-0">Manage Institutions</p>
                  <p class="small sb-muted mb-0">Toggle partner status and domains</p>
                </div>
              </div>
            </router-link>

            <router-link to="/admin/withdrawals" class="btn action-surface border-0 text-start rounded-3 p-3 shadow-none position-relative sb-btn">
              <div class="d-flex align-items-center">
                <i class="bi bi-cash-stack fs-4 me-3 text-success"></i>
                <div>
                  <p class="fw-bold mb-0">Audit Cash Outs</p>
                  <p class="small sb-muted mb-0">Review provider payouts and exceptions</p>
                </div>
              </div>
              <span v-if="store.stats?.failed_withdrawals" class="badge bg-danger rounded-pill position-absolute top-0 end-0 translate-middle-y mt-3 me-3">
                {{ store.stats.failed_withdrawals }}
              </span>
            </router-link>

            <router-link to="/admin/users" class="btn action-surface border-0 text-start rounded-3 p-3 shadow-none sb-btn">
              <div class="d-flex align-items-center">
                <i class="bi bi-shield-lock fs-4 me-3 text-warning"></i>
                <div>
                  <p class="fw-bold mb-0">User Management</p>
                  <p class="small sb-muted mb-0">Suspend or reactivate platform accounts</p>
                </div>
              </div>
            </router-link>

            <router-link to="/admin/support" class="btn action-surface border-0 text-start rounded-3 p-3 shadow-none sb-btn">
              <div class="d-flex align-items-center">
                <i class="bi bi-headset fs-4 me-3 text-info"></i>
                <div>
                  <p class="fw-bold mb-0">Support Desk</p>
                  <p class="small sb-muted mb-0">Claim and resolve user support tickets</p>
                </div>
              </div>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useAdminStore } from '@/stores/admin';

const store = useAdminStore()

onMounted(() => {
  store.fetchStats(true)
})

const getActivityIcon = (type) => {
  switch (type) {
    case 'registration': return 'bi bi-person-plus text-primary';
    case 'booking_completed': return 'bi bi-check-circle text-success';
    case 'institution_added': return 'bi bi-building-add text-info';
    case 'withdrawal_failed': return 'bi bi-exclamation-octagon text-danger';
    case 'withdrawal_processed': return 'bi bi-cash text-success';
    case 'admin_action': return 'bi bi-shield-check text-warning';
    default: return 'bi bi-dot text-secondary';
  }
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleString('en-US', { 
    month: 'short', 
    day: 'numeric', 
    hour: 'numeric', 
    minute: '2-digit' 
  })
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.admin-dashboard {
  color: var(--sb-text-main);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.icon-box {
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.activity-item {
  position: relative;
}

.activity-timeline .activity-item:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 10px;
  top: 35px;
  bottom: -20px;
  width: 2px;
  background-color: var(--sb-bg);
}

.activity-icon {
  width: 20px;
  z-index: 1;
  background: var(--sb-card-bg);
}

.action-surface {
  background-color: var(--sb-bg);
  color: var(--sb-text-main);
}

.action-surface:hover {
  background-color: color-mix(in srgb, var(--sb-primary) 8%, var(--sb-bg)) !important;
  color: var(--sb-text-main);
  transform: translateY(-2px);
  transition: all 0.2s ease;
}
</style>
