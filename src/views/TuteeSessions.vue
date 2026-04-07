<template>
    <div class="card border-sb border-1 shadow-sm rounded-4" style="height: 520px;">
        <div class="card-body p-4 p-md-5 d-flex flex-column overflow-hidden">
            <h4 class="fw-bold mb-4 d-flex align-items-center">
                <i class="bi bi-file-earmark-text text-sb-primary me-3"></i>Sessions
            </h4>

            <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4">
                <div class="d-flex gap-2 mb-4 bg-light p-2 rounded-3 d-inline-flex border border-sb">
                    <button v-for="filter in filters" :key="filter.value" @click="currentFilter = filter.value"
                        class="btn rounded-pill px-3 py-1 fw-semibold text-muted shadow-none"
                        :class="currentFilter === filter.value ? 'bg-white text-dark shadow-sm' : 'btn-light'">
                        {{ filter.label }}
                    </button>
                </div>

                <div class="input-group" style="max-width: 300px;">
                    <span class="input-group-text bg-white border-end-0 border-sb text-muted">
                        <i class="bi bi-search"></i>
                    </span>
                    <input type="text" class="form-control border-start-0 shadow-none" v-model="searchQuery" placeholder="Search tutor or subject...">
                </div>
            </div>
            

            <div class="flex-grow-1 overflow-auto" style="min-height: 0;">
                <table class="table table-hover align-middle mb-0">
                    <thead>
                        <tr class="text-muted small" style="border-bottom: 2px solid var(--sb-card-border);">
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
                            <td colspan="7" class="text-center py-5 text-muted">
                                <div class="spinner-border text-primary mb-2" role="status"></div>
                                <div>Loading sessions...</div>
                            </td>
                        </tr>

                        <tr v-else-if="sessionsStore.error">
                            <td colspan="7" class="text-center py-4 text-danger">
                                {{ sessionsStore.error }}
                            </td>
                        </tr>

                        <tr v-else-if="filteredSessions.length > 0" v-for="session in filteredSessions" :key="session.id" @click="goToDetails(session.id)"
                            class="clickable-row">
                            <td>{{ session.tutor || 'TBD' }}</td>
                            <td>{{ session.subject }}</td>
                            <td>{{ session.date }}</td>
                            <td>{{ session.startTime }} - {{ session.endTime }}</td>

                            <td>
                                <span class="badge rounded-pill px-3 py-1" :class="getStatusClass(session.status)">
                                    {{ session.status?.toLowerCase() === 'confirmed' ? 'Upcoming' : session.status }}
                                </span>
                            </td>

                            <td>
                                <span v-if="session.rating" class="text-warning fw-bold small">
                                    ⭐ {{ session.rating }}
                                </span>
                                <span v-else class="text-muted">—</span>
                            </td>

                            <td>
                                <button v-if="session.status?.toLowerCase() === 'ongoing'" class="btn btn-sm btn-success"
                                    data-bs-toggle="modal" data-bs-target="#confirmationModal"
                                    @click.stop="prepareConfirmation(session)">
                                    Confirm
                                </button>
                            </td>
                        </tr>

                        <tr v-else>
                            <td colspan="7" class="text-center py-4 text-muted">
                                No sessions found.
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <div class="modal fade" id="confirmationModal" tabindex="-1" aria-labelledby="confirmationModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content rounded-4">
                <div class="modal-header border-0">
                    <h5 class="modal-title fw-bold" id="confirmationModalLabel">Confirm Session</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>

                <div class="modal-body border-0 text-center py-4">
                    <h5 class="fw-bold mb-1">Rate your session</h5>
                    <p class="text-muted mb-4">
                        How was your {{ selectedSession?.subject }} session with {{ selectedSession?.tutor || 'your tutor' }}?
                    </p>
                    
                    <div class="d-flex justify-content-center gap-2 mb-2 text-warning fs-1">
                        <i v-for="star in 5" :key="star"
                            class="bi transition-all"
                            :class="currentRating >= star ? 'bi-star-fill text-warning' : 'bi-star text-muted'"
                            @click="currentRating = star"
                            style="cursor: pointer; transition: 0.2s;">
                        </i>
                    </div>
                    
                    <div class="small text-muted fw-semibold" style="height: 20px;">
                        <span v-if="currentRating === 1">Needs Improvement</span>
                        <span v-if="currentRating === 2">Fair</span>
                        <span v-if="currentRating === 3">Good</span>
                        <span v-if="currentRating === 4">Great!</span>
                        <span v-if="currentRating === 5">Excellent!</span>
                    </div>
                </div>

                <div class="modal-footer border-0">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn bg-sb-primary text-white" 
                        :disabled="currentRating === 0 || isSubmitting"
                        @click="executeConfirmation">
                        
                        <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        
                        {{ isSubmitting ? 'Submitting...' : 'Submit & Confirm' }}
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <div v-if="showToast" class="position-fixed top-0 start-50 translate-middle-x p-3 mt-4" style="z-index: 1080;">
        <div class="toast show align-items-center text-white bg-success border-0 rounded-3 shadow-lg" role="alert">
            <div class="d-flex p-1 px-2">
                <div class="toast-body fw-semibold fs-6">
                    <i class="bi bi-check-circle-fill me-2"></i> Session completed successfully!
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" @click="showToast = false" aria-label="Close"></button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionsStore } from '@/stores/completedSessions.js' 
import * as bootstrap from 'bootstrap'

const router = useRouter()
const sessionsStore = useSessionsStore()

const selectedSession = ref(null)
const currentRating = ref(0)
const hoverRating = ref(0)
const showToast = ref(false)
const isSubmitting = ref(false)
const currentFilter = ref('pending')
const searchQuery = ref('')


onMounted(() => {
    sessionsStore.fetchSessions()
})

const prepareConfirmation = (session) => {
    selectedSession.value = session
    currentRating.value = 0 
    hoverRating.value = 0
}

const executeConfirmation = async () => {
    if (!selectedSession.value || currentRating.value === 0) return
    
    isSubmitting.value = true

    try {
        await sessionsStore.completeSession(selectedSession.value.id, currentRating.value)
        
        selectedSession.value = null
        currentRating.value = 0

        showToast.value = true
        bootstrap.Modal.getOrCreateInstance(document.getElementById('confirmationModal')).hide()
        
        setTimeout(() => {
            showToast.value = false
        }, 3000)

    } catch (error) {
        console.error("Failed to confirm session:", error)
        alert("Failed to save rating. Please try again.")
    } finally {
        isSubmitting.value = false 
    }
}

const filters = [
    { label: 'All', value: 'all' },
    { label: 'Pending', value: 'pending' },
    { label: 'Upcoming', value: 'upcoming' }, 
    { label: 'Ongoing', value: 'ongoing' },
    { label: 'Completed', value: 'completed' }
]

const filteredSessions = computed(() => {
    let filteredList = sessionsStore.sessions

    if (currentFilter.value !== 'all'){
        filteredList = filteredList.filter(s => {
            const backendStatus = s.status?.toLowerCase() || ''
            if (currentFilter.value === 'upcoming') return backendStatus === 'confirmed'
            return backendStatus === currentFilter.value
        })
    }

    if (searchQuery.value.trim() !== ''){
        const query = searchQuery.value.toLowerCase()
        filteredList = filteredList.filter(s => {
            const tutorName = (s.tutor || '').toLowerCase()
            const subject = (s.subject || '').toLowerCase()

            return tutorName.includes(query) || subject.includes(query)
        })
    }

    return filteredList
})

const getStatusClass = (status) => {
    if (!status) return 'bg-secondary text-white'

    switch (status.toLowerCase()) {
        case 'pending': return 'bg-warning text-dark'
        case 'confirmed': 
        case 'upcoming': return 'bg-primary text-white'
        case 'ongoing': return 'bg-info text-white'
        case 'completed': return 'bg-success text-white'
        default: return 'bg-secondary text-white'
    }
}

const goToDetails = (id) => router.push(`/TuteeSessionDetails/${id}`)
</script>

<style scoped>
.clickable-row {
    cursor: pointer;
}

.clickable-row:hover {
    background-color: rgba(0, 0, 0, 0.04);
}

thead th {
    position: sticky;
    top: 0;
    background-color: white;
    z-index: 2;
    box-shadow: inset 0 -2px 0 var(--sb-card-border, #dee2e6);
}
</style>