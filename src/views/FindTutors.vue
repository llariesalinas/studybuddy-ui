<template>
    <div class="p-4">
        <div class="mb-4">
            <h2 class="fw-bold text-dark">Find Tutors</h2>
            <p class="text-muted">Browse peer tutors matched to your learning needs.</p>
        </div>

        <form @submit.prevent="searchTutor">
            <div class="row mb-5 g-1 justify-content-center">
            <div class="col-md-2">
                <label class="form-label fw-semibold small">Subject</label>
                <select v-model="initialbookStore.selectedSubject" class="form-select">
                <option disabled value="">Select Subject</option>
                <option
                    v-for="subject in subjects"
                    :key="subject.subject_code"
                    :value="subject.subject_code"
                >
                    {{ subject.subject_name  }}
                </option>
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label fw-semibold small">Topic</label>
                <select v-model="initialbookStore.selectedTopic" class="form-select border-sb shadow-none py-2">
                    <option value="" disabled>Select Topic</option>
                    <option 
                    v-for="topic in filteredTopics"
                    :key="topic"
                    :value="topic">{{topic}}</option>
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label fw-semibold small">Mode</label>
                <select v-model="initialbookStore.selectedMode" class="form-select border-sb shadow-none py-2">
                    <option 
                    v-for="mode in modes"
                    :key="mode"
                    :value="mode">{{ mode }}</option>
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label fw-semibold small">Date</label>
                <input type="date" v-model="initialbookStore.selectedDate" class="form-control border-sb shadow-none" required />
            </div>
            <div class="col" style="flex: 0 0 12.5%; max-width: 12.5%;">
                <label class="form-label fw-semibold small">From</label>
                <input type="time" v-model="initialbookStore.selectedStartTime" class="form-control border-sb shadow-none" required />
            </div>
            <div class="col" style="flex: 0 0 12.5%; max-width: 12.5%;">
                <label class="form-label fw-semibold small">To</label>
                <input type="time" v-model="initialbookStore.selectedEndTime" class="form-control border-sb shadow-none" required />
            </div>
            <div class="col-md-1">
                <label class="form-label fw-semibold small invisible">Search</label>
                <button type="submit" class="btn bg-sb-primary text-white px-3 rounded-3 fw-semibold shadow-sm"
                :disabled="isSubmitting">
                    Search
                </button>
            </div> 
        </div>
        </form>
        

        <div v-if="isLoading" class="text-center py-5">
            <div class="spinner-border text-sb-primary" role="status"></div>
            <p class="text-muted mt-2">Running matching algorithm...</p>
        </div>

        <div v-else class="row g-4">
            <div class="col-md-6" v-for="tutor in matchedTutors" :key="tutor.profile_id">
                <div class="card border-sb shadow-sm rounded-4 h-100">
                    <div class="card-body p-4">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <div class="d-flex align-items-center gap-3">
                                <div class="bg-success bg-opacity-10 text-sb-primary fw-bold rounded-circle d-flex align-items-center justify-content-center"
                                    style="width: 48px; height: 48px;">
                                    {{ tutor.initials }}
                                </div>
                                <div>
                                    <h6 class="fw-bold mb-0 text-dark">{{ tutor.name }}</h6>
                                    <p class="text-muted small mb-0">{{ tutor.year_course }}</p>
                                </div>
                            </div>
                            <div class="text-end">
                                <span class="fw-bold text-warning d-flex align-items-center">
                                    <i class="bi bi-star-fill me-1"></i> {{ tutor.rating }}
                                </span>
                            </div>
                        </div>

                        <p class="small text-dark mb-3">{{ tutor.bio }}</p>

                        <div class="d-flex gap-2 mb-4 flex-wrap">
                            <span v-for="subject in tutor.subjects" :key="subject"
                                class="badge bg-light text-dark border border-sb">
                                {{ subject }}
                            </span>
                        </div>

                        <div class="d-flex justify-content-between align-items-center mt-auto">
                            <div class="small">
                                <span class="fw-bold text-dark">₱{{ tutor.hourly_rate }}</span><span
                                    class="text-muted">/hr</span>
                                <span class="text-muted ms-2">· {{ tutor.total_sessions }} sessions</span>
                            </div>
                            <button 
                                @click="toTutorDetails(tutor)"
                                class="btn bg-sb-primary text-white px-4 rounded-3 fw-semibold shadow-sm"
                                >
                                Book Session
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import api from '@/services/api/api'
import { ref, onMounted, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useInitialBookingPrefsStore } from '@/stores/initialbookingprefs'
import { useBookedSessionsStore } from '@/stores/bookedSessionDetails'
import { useRouter } from 'vue-router'


const bookedSessionsStore = useBookedSessionsStore()
const initialbookStore = useInitialBookingPrefsStore()
const authStore = useAuthStore()
const isLoading = ref(true)
const isSubmitting = ref(false)
const router = useRouter()

const matchedTutors = ref([])

const route = useRoute()

const modes = [
    'Online',
    'Face-to-face'
]


watch(
    () => initialbookStore.selectedSubject,
    () => {
        initialbookStore.selectedTopic = ''
    }
)

const searchTutor = async () => {
  isSubmitting.value = true
  isLoading.value = true

  try {
    const response = await api.get(
      `search-tutors/?subject=${initialbookStore.selectedSubject}`
    )

    matchedTutors.value = response.data.map(tutor => ({
      profile_id: tutor.profile_id,   // ✅ FIXED
      initials: tutor.fname[0] + tutor.lname[0],
      name: `${tutor.fname} ${tutor.lname}`,
      year_course: 'Tutor',
      rating: tutor.rating_average ?? 5.0,
      bio: 'Peer tutor available.',
      subjects: [],
      hourly_rate: tutor.hourly_rate ?? 150,
      total_sessions: tutor.total_sessions ?? 0
    }))

  } catch (error) {
    console.error('Search failed:', error)
  } finally {
    isSubmitting.value = false
    isLoading.value = false
  }
}

const toTutorDetails = (tutor) => {
    bookedSessionsStore.bookedSessionTutorID = tutor.profile_id
    bookedSessionsStore.bookedSessionTutorName = tutor.name
    bookedSessionsStore.bookedSessionSub = initialbookStore.selectedSubject
    bookedSessionsStore.bookedSessionTop = initialbookStore.selectedTopic
    bookedSessionsStore.bookedSessionMode = initialbookStore.selectedMode

    router.push(`/tutor/${tutor.profile_id}`)
}

const subjects = ref([])

onMounted(async () => {
  const res = await api.get('subjects/')
  subjects.value = res.data

  // 🔥 Sync query param into store
  if (route.query.subject) {
    initialbookStore.selectedSubject = route.query.subject
  }

  if (initialbookStore.selectedSubject) {
    await searchTutor()
  } else {
    isLoading.value = false
  }
})
</script>

<style scoped>
.border-sb {
    border-color: var(--sb-card-border) !important;
}

.text-sb-primary {
    color: var(--sb-primary) !important;
}

.bg-sb-primary {
    background-color: var(--sb-primary) !important;
}
</style>
