<template>
    <div class="card sb-card-surface border-1 shadow-sm rounded-4" style="height: 520px;">
        <div class="card-body p-4 p-md-5 d-flex flex-column overflow-hidden">
            <h4 class="fw-bold sb-text mb-4 d-flex align-items-center">
                <i class="bi bi-file-earmark-text text-sb-primary me-3"></i>Sessions
            </h4>

            <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4">
                <div class="d-flex gap-2 mb-4 filter-bar p-2 rounded-3 d-inline-flex">
                    <button
                        v-for="filter in filters"
                        :key="filter.value"
                        @click="currentFilter = filter.value"
                        class="btn rounded-pill px-3 py-1 fw-semibold shadow-none sb-btn sb-pill filter-tab"
                        :class="{ 'filter-tab-active': currentFilter === filter.value }"
                        :aria-pressed="currentFilter === filter.value"
                    >
                        {{ filter.label }}
                    </button>
                </div>

                <div class="input-group" style="max-width: 300px;">
                    <span class="input-group-text sb-input-addon border-end-0">
                        <i class="bi bi-search"></i>
                    </span>
                    <input
                        v-model="searchQuery"
                        type="text"
                      class="form-control border-start-0 shadow-none sb-search-input sb-field"
                        placeholder="Search tutor or subject..."
                    >
                </div>
            </div>

            <div class="flex-grow-1 overflow-auto" style="min-height: 0;">
                <table class="table table-hover align-middle mb-0 sb-themed-table">
                    <thead>
                        <tr class="sb-muted small" style="border-bottom: 2px solid var(--sb-card-border);">
                            <th>Tutor</th>
                            <th>Subject</th>
                            <th>Date</th>
                            <th>Time</th>
                            <th>Status</th>
                            <th>Rating</th>
                            <th></th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr v-if="sessionsStore.loading">
                            <td colspan="7" class="text-center py-5 sb-muted">
                                <div class="spinner-border text-primary mb-2" role="status"></div>
                                <div>Loading sessions...</div>
                            </td>
                        </tr>

                        <tr v-else-if="sessionsStore.error">
                            <td colspan="7" class="text-center py-4 text-danger">
                                {{ sessionsStore.error }}
                            </td>
                        </tr>

                        <tr
                            v-else-if="filteredSessions.length > 0"
                            v-for="session in filteredSessions"
                            :key="session.id"
                            @click="goToDetails(session.id)"
                            class="clickable-row sb-interactive"
                        >
                            <td>{{ session.tutor || 'TBD' }}</td>
                            <td>{{ session.subject }}</td>
                            <td>{{ session.date }}</td>
                            <td>{{ session.startTime }} - {{ session.endTime }}</td>

                            <td>
                                <span class="badge rounded-pill px-3 py-1" :class="getStatusClass(session.status)">
                                    {{ session.status }}
                                </span>
                            </td>

                            <td>
                                <span v-if="session.rating" class="text-warning fw-bold small">
                                    <i class="bi bi-star-fill me-1"></i>{{ session.rating }}
                                </span>
                                <span v-else class="badge rounded-pill text-bg-danger-subtle text-danger-emphasis border border-danger-subtle">
                                    Unrated
                                </span>
                            </td>

                            <td></td>
                        </tr>

                        <tr v-else>
                            <td colspan="7" class="text-center py-4 sb-muted">
                                No sessions found.
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionsStore } from '@/stores/completedSessions.js'
import { isHiddenFromTutee } from '@/constants/tuteeSessionVisibility.js'

const router = useRouter()
const sessionsStore = useSessionsStore()

const currentFilter = ref('upcoming')
const searchQuery = ref('')

onMounted(() => {
    sessionsStore.fetchSessions()
})

const filters = [
    { label: 'All', value: 'all' },
    { label: 'Cancelled', value: 'cancelled' },
    { label: 'Upcoming', value: 'upcoming' },
    { label: 'Ongoing', value: 'ongoing' },
    { label: 'Completed', value: 'completed' }
]

const filteredSessions = computed(() => {
    // Pending and Rejected are filtered off the base list, not just missing a tab, so they stay out
    // of "All" too. The store still holds them -- it is shared with the tutor side.
    let filteredList = sessionsStore.sessions.filter((session) => !isHiddenFromTutee(session))

    if (currentFilter.value !== 'all') {
        filteredList = filteredList.filter((session) => {
            const backendStatus = String(session.status || '').toLowerCase()
            return backendStatus === currentFilter.value
        })
    }

    if (searchQuery.value.trim() !== '') {
        const query = searchQuery.value.toLowerCase()
        filteredList = filteredList.filter((session) => {
            const tutorName = String(session.tutor || '').toLowerCase()
            const subject = String(session.subject || '').toLowerCase()

            return tutorName.includes(query) || subject.includes(query)
        })
    }

    return filteredList
})

const getStatusClass = (status) => {
    switch (String(status || '').toLowerCase()) {
        case 'pending location':
            return 'bg-warning text-dark'
        case 'cancelled':
            return 'bg-danger text-white'
        case 'upcoming':
            return 'bg-primary text-white'
        case 'ongoing':
            return 'bg-info text-white'
        case 'payment required':
            return 'bg-warning-subtle text-dark'
        case 'awaiting verification':
        case 'review pending':
            return 'bg-info text-dark'
        case 'completed':
            return 'bg-success text-white'
        default:
            return 'bg-secondary text-white'
    }
}

const goToDetails = (id) => router.push(`/tuteeSessionDetails/${id}`)
</script>

<style scoped>
.clickable-row {
    cursor: pointer;
}

.clickable-row:hover {
    background-color: color-mix(in srgb, var(--sb-primary) 8%, transparent);
}

.filter-bar {
    background: var(--sb-bg);
    border: 1px solid var(--sb-card-border);
}

.filter-tab {
  position: relative;
  color: var(--sb-text-muted);
}

.filter-tab-active {
  background: var(--sb-card-bg);
  color: var(--sb-text-main);
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}
.sb-input-addon,
.sb-search-input {
    background: var(--sb-card-bg);
    border-color: var(--sb-card-border);
    color: var(--sb-text-main);
}

.sb-input-addon {
    color: var(--sb-text-muted);
}

.sb-themed-table {
    --bs-table-bg: transparent;
    --bs-table-color: var(--sb-text-main);
    --bs-table-border-color: var(--sb-card-border);
    --bs-table-hover-bg: color-mix(in srgb, var(--sb-primary) 7%, transparent);
    --bs-table-hover-color: var(--sb-text-main);
}

thead th {
    position: sticky;
    top: 0;
    background-color: var(--sb-card-bg);
    z-index: 2;
    box-shadow: inset 0 -2px 0 var(--sb-card-border, #dee2e6);
}
</style>
