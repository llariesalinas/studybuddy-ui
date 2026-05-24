<template>
  <div class="admin-reports p-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3>Platform Analytics</h3>
      <button
        @click="store.fetchAnalytics(true)"
        :disabled="store.loading.analytics"
        class="btn bg-sb-primary text-white btn-sm rounded-pill ms-auto"
      >
        <span v-if="store.loading.analytics" class="spinner-border spinner-border-sm me-1" role="status"></span>
        <i v-else class="bi bi-arrow-clockwise me-1"></i>
        {{ store.loading.analytics ? 'Loading...' : 'Refresh Data' }}
      </button>
    </div>

    <!-- Revenue Breakdown Cards -->
    <div class="row g-4 mb-5">
      <div class="col-md-4">
        <div class="card border-0 shadow-sm rounded-4 p-4 h-100 bg-sb-primary text-white">
          <p class="small fw-bold mb-2 opacity-75">GROSS REVENUE (ALL TIME)</p>
          <Transition name="fade" mode="out-in">
            <div v-if="store.loading.analytics" class="placeholder-glow">
              <h2 class="placeholder col-8 rounded mb-2 bg-white opacity-25"></h2>
              <p class="placeholder col-10 rounded mb-0 bg-white opacity-25"></p>
            </div>
            <div v-else>
              <h2 class="fw-bold mb-0">₱{{ store.analytics?.revenue_summary?.gross?.toLocaleString() }}</h2>
              <div class="mt-3 pt-3 border-top border-white-50">
                <p class="small mb-0 opacity-75">Total volume of all paid sessions</p>
              </div>
            </div>
          </Transition>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card border-0 shadow-sm rounded-4 p-4 h-100">
          <p class="text-muted small fw-bold mb-2">PLATFORM COMMISSIONS</p>
          <Transition name="fade" mode="out-in">
            <div v-if="store.loading.analytics" class="placeholder-glow">
              <h2 class="placeholder col-7 rounded mb-2"></h2>
              <p class="placeholder col-9 rounded mb-0"></p>
            </div>
            <div v-else>
              <h2 class="fw-bold mb-0 text-dark">₱{{ store.analytics?.revenue_summary?.commissions?.toLocaleString() }}</h2>
              <div class="mt-3 pt-3 border-top border-light">
                <p class="small text-muted mb-0">Net earnings from the 10% platform fee</p>
              </div>
            </div>
          </Transition>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card border-0 shadow-sm rounded-4 p-4 h-100">
          <p class="text-muted small fw-bold mb-2">TUTOR PAYOUTS</p>
          <Transition name="fade" mode="out-in">
            <div v-if="store.loading.analytics" class="placeholder-glow">
              <h2 class="placeholder col-7 rounded mb-2"></h2>
              <p class="placeholder col-9 rounded mb-0"></p>
            </div>
            <div v-else>
              <h2 class="fw-bold mb-0 text-dark">₱{{ store.analytics?.revenue_summary?.payouts?.toLocaleString() }}</h2>
              <div class="mt-3 pt-3 border-top border-light">
                <p class="small text-muted mb-0">Total amount distributed to tutors</p>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </div>

    <!-- Sessions Over Time -->
    <div class="card border-0 shadow-sm rounded-4 p-4 mb-5">
      <h5 class="fw-bold mb-4">Sessions Completed (Last 30 Days)</h5>
      <Transition name="fade" mode="out-in">
        <div v-if="store.loading.analytics" class="placeholder-glow">
          <div class="d-flex align-items-end gap-1" style="height: 200px;">
            <div
              v-for="i in 30" :key="'bar-sk-' + i"
              class="placeholder flex-grow-1 rounded-top-2"
              :style="{ height: `${20 + Math.abs(Math.sin(i) * 70)}%` }"
            ></div>
          </div>
          <div class="d-flex justify-content-between mt-3">
            <span class="placeholder col-2 rounded"></span>
            <span class="placeholder col-2 rounded"></span>
            <span class="placeholder col-2 rounded"></span>
          </div>
        </div>
        <div v-else>
          <div class="d-flex align-items-end gap-1" style="height: 200px;">
            <div
              v-for="(val, idx) in store.analytics?.sessions_over_time?.data"
              :key="idx"
              class="flex-grow-1 bg-primary-subtle rounded-top-2 position-relative bar-hover"
              :style="{ height: `${(val / maxSessions) * 100}%` }"
            >
              <div class="bar-tooltip position-absolute top-0 start-50 translate-middle-x bg-dark text-white small px-2 py-1 rounded-2 shadow-sm" style="margin-top: -35px;">
                {{ val }}
              </div>
            </div>
          </div>
          <div class="d-flex justify-content-between mt-3 text-muted small">
            <span>{{ store.analytics?.sessions_over_time?.labels[0] }}</span>
            <span>{{ store.analytics?.sessions_over_time?.labels[14] }}</span>
            <span>{{ store.analytics?.sessions_over_time?.labels[29] }}</span>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Top Tutors Table -->
    <div class="card border-0 shadow-sm rounded-4 overflow-hidden">
      <div class="p-4 border-bottom bg-white">
        <h5 class="fw-bold mb-0">Top Performing Tutors</h5>
      </div>
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="bg-light">
            <tr>
              <th class="ps-4 py-3">Tutor Name</th>
              <th class="py-3">Sessions Completed</th>
              <th class="py-3">Avg Rating</th>
              <th class="pe-4 py-3 text-end">Rank</th>
            </tr>
          </thead>
          <tbody>
            <!-- Skeleton rows — no Transition wrapper -->
            <template v-if="store.loading.analytics">
              <tr v-for="i in 5" :key="'tutor-sk-' + i" class="placeholder-glow">
                <td class="ps-4"><span class="placeholder col-7 rounded"></span></td>
                <td>
                  <div class="d-flex align-items-center gap-3">
                    <span class="placeholder rounded flex-grow-1" style="max-width: 150px; height: 6px;"></span>
                    <span class="placeholder col-1 rounded"></span>
                  </div>
                </td>
                <td><span class="placeholder col-4 rounded"></span></td>
                <td class="pe-4 text-end">
                  <span class="placeholder rounded-circle" style="width: 32px; height: 32px; display: inline-block;"></span>
                </td>
              </tr>
            </template>

            <!-- Real rows -->
            <template v-else>
              <tr v-for="(t, idx) in store.analytics?.top_tutors" :key="idx">
                <td class="ps-4 fw-bold text-dark">{{ t.name }}</td>
                <td>
                  <div class="d-flex align-items-center">
                    <div class="flex-grow-1 progress me-3" style="height: 6px; max-width: 150px;">
                      <div class="progress-bar bg-success" :style="{ width: `${(t.sessions / topSessionCount) * 100}%` }"></div>
                    </div>
                    <span class="small fw-bold">{{ t.sessions }}</span>
                  </div>
                </td>
                <td>
                  <span class="text-warning fw-bold">
                    <i class="bi bi-star-fill me-1"></i>{{ t.rating.toFixed(1) }}
                  </span>
                </td>
                <td class="pe-4 text-end">
                  <span class="badge rounded-circle bg-light text-dark p-2 border"
                    style="width: 32px; height: 32px; display: inline-flex; align-items: center; justify-content: center;">
                    #{{ idx + 1 }}
                  </span>
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
import { onMounted, computed } from 'vue';
import { useAdminStore } from '@/stores/admin';

const store = useAdminStore()

onMounted(() => {
  store.fetchAnalytics()
})

const maxSessions = computed(() => {
  if (!store.analytics?.sessions_over_time?.data?.length) return 1
  return Math.max(...store.analytics.sessions_over_time.data, 5)
})

const topSessionCount = computed(() => {
  if (!store.analytics?.top_tutors?.length) return 1
  return Math.max(...store.analytics.top_tutors.map(t => t.sessions), 1)
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}


.bar-hover:hover {
  background-color: var(--sb-primary) !important;
}

.bar-tooltip {
  display: none;
  z-index: 10;
  white-space: nowrap;
}

.bar-hover:hover .bar-tooltip {
  display: block;
}

.progress { background-color: #f0f0f0; }
</style>
