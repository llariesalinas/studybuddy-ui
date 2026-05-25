<template>
  <div class="tutee-profile-shell py-5">
    <div class="container py-lg-4">
      <div class="glass-modal">
        
        <form @submit.prevent="saveProfile">
          
          <!-- PROFILE HEADER -->
          <div class="profile-header d-flex align-items-center justify-content-between flex-wrap gap-3">
            <div class="d-flex align-items-center gap-4">
              <div class="avatar-wrapper">
                <img v-if="profile.profile_picture_url" :src="profile.profile_picture_url" class="rounded-circle avatar-img" @click="triggerFileInput">
                <div v-else class="rounded-circle initials-avatar d-flex align-items-center justify-content-center fw-bold fs-3" @click="triggerFileInput">
                  {{ initials }}
                </div>
                <input type="file" ref="fileInput" class="d-none" @change="handleAvatarUpload" accept="image/*">
                <div class="avatar-edit-badge" @click="triggerFileInput">
                  <i class="bi bi-camera-fill"></i>
                </div>
              </div>
              <div class="header-info">
                <h2 class="mb-1 fw-bold text-white">{{ profile.fname }} {{ profile.lname }}</h2>
                <p class="text-white text-opacity-75 mb-0">Student / Tutee</p>
              </div>
            </div>
            <div class="d-flex gap-2">
              <button type="button" class="sb-btn btn-discard px-4 py-2 fw-semibold" @click="discardChanges">Discard</button>
              <button type="submit" class="sb-btn btn-save px-4 py-2 fw-semibold">Save Profile</button>
            </div>
          </div>

          <div class="profile-body p-4 p-md-5">
            <div class="row g-4">
              
              <!-- LEFT COLUMN (7/12): Personal Info + Bio -->
              <div class="col-lg-7">
                <div class="selection-card p-4 h-100">
                  <h5 class="section-title mb-4">Personal Information</h5>
                  
                  <div class="row g-3">
                    <div class="col-md-4">
                      <label class="form-label text-muted small fw-bold">First Name</label>
                      <input type="text" v-model="profile.fname" class="form-control input-glass">
                    </div>
                    <div class="col-md-4">
                      <label class="form-label text-muted small fw-bold">Middle Name</label>
                      <input type="text" v-model="profile.mname" class="form-control input-glass">
                    </div>
                    <div class="col-md-4">
                      <label class="form-label text-muted small fw-bold">Last Name</label>
                      <input type="text" v-model="profile.lname" class="form-control input-glass">
                    </div>
                    
                    <div class="col-12 mt-3">
                      <label class="form-label text-muted small fw-bold">University Email</label>
                      <input type="email" v-model="profile.email" class="form-control input-glass bg-light" disabled title="Email cannot be changed">
                      <div class="form-text small opacity-50">Email cannot be changed after registration.</div>
                    </div>

                    <div class="col-12 mt-4">
                      <div class="d-flex justify-content-between">
                        <label class="form-label text-muted small fw-bold">Bio (About Me)</label>
                        <span :class="['small', bioCharCount > 450 ? 'text-danger fw-bold' : 'text-muted']">{{ bioCharCount }}/500</span>
                      </div>
                      <textarea 
                        v-model="profile.bio" 
                        :class="['form-control input-glass', { 'border-danger glow-danger': bioCharCount > 450 }]"
                        rows="6" 
                        maxlength="500" 
                        placeholder="Tell tutors about your learning style, academic goals, or what you usually need help with..."
                      ></textarea>
                    </div>
                  </div>
                </div>
              </div>

              <!-- RIGHT COLUMN (5/12): Academic Level + Year Level + Course/Strand + Subjects -->
              <div class="col-lg-5">
                <div class="selection-card p-4 h-100">
                  <h5 class="section-title mb-4">Academic Context</h5>
                  
                  <div class="row g-3">
                    <div class="col-12">
                      <label class="form-label text-muted small fw-bold">Education Level</label>
                      <select v-model="educationLevel" class="form-select input-glass">
                        <option value="elementary">Elementary</option>
                        <option value="jhs">Junior High School</option>
                        <option value="shs">Senior High School</option>
                        <option value="college">College / University</option>
                      </select>
                    </div>

                    <div class="col-12 mt-3">
                      <label class="form-label text-muted small fw-bold">Year Level</label>
                      <select v-model="profile.year_level" class="form-select input-glass">
                        <option v-for="opt in yearOptions" :key="opt.value" :value="opt.value">
                          {{ opt.label }}
                        </option>
                      </select>
                    </div>

                    <div class="col-12 mt-3" v-if="educationLevel === 'college' || educationLevel === 'shs'">
                      <label class="form-label text-muted small fw-bold">
                        {{ educationLevel === 'college' ? 'Degree Program / Course' : 'Academic Strand' }}
                      </label>
                      <select v-model="profile.course" class="form-select input-glass">
                        <option value="">Select {{ educationLevel === 'college' ? 'Course' : 'Strand' }}</option>
                        <option v-for="c in courses" :key="c.course_code" :value="c.course_code">
                          {{ c.course_name }}
                        </option>
                      </select>
                    </div>

                    <div class="col-12 mt-4">
                      <label class="form-label text-muted small fw-bold">Preferred Subjects</label>
                      <div class="subjects-pills d-flex flex-wrap gap-2 mt-1">
                        <label v-for="s in subjects" :key="s.subject_code" class="subject-pill-label">
                          <input type="checkbox" class="sr-only" :value="s.subject_code" v-model="profile.subjects">
                          <span :class="['subject-pill', { active: profile.subjects.includes(s.subject_code) }]">
                            {{ s.subject_name }}
                          </span>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </div>

          <!-- PROFILE FOOTER -->
          <div class="profile-footer d-flex align-items-center justify-content-between mt-5 pt-4 border-top border-light border-opacity-10 px-4 px-md-5 pb-5 flex-wrap gap-3">
            <p v-if="lastUpdated" class="mb-0 small text-muted fst-italic">Last updated: {{ lastUpdated }}</p>
            <p v-else class="mb-0"></p>
            <button type="submit" class="sb-btn btn-save hover-lift px-5 py-3 fw-bold">
              Save Changes
            </button>
          </div>

        </form>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import api from '@/services/api/api'
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()

const profile = ref({
  fname: '',
  mname: '',
  lname: '',
  email: '',
  course: '',
  year_level: '',
  bio: '',
  profile_picture_url: '',
  subjects: []
})

const courses = ref([])
const subjects = ref([])
const educationLevel = ref('college')
const fileInput = ref(null)

const bioCharCount = computed(() => profile.value.bio?.length || 0)

function deriveEducationLevel(yearLevel) {
  if (!yearLevel) return 'college'
  const val = parseInt(yearLevel)
  if (val >= 1 && val <= 6) return 'elementary'
  if (val >= 7 && val <= 10) return 'jhs'
  if (val >= 11 && val <= 12) return 'shs'
  return 'college'
}

const yearOptions = computed(() => {
  if (educationLevel.value === 'elementary') {
    return [1, 2, 3, 4, 5, 6].map(v => ({ label: `Grade ${v}`, value: v }))
  }
  if (educationLevel.value === 'jhs') {
    return [7, 8, 9, 10].map(v => ({ label: `Grade ${v}`, value: v }))
  }
  if (educationLevel.value === 'shs') {
    return [11, 12].map(v => ({ label: `Grade ${v}`, value: v }))
  }
  return [13, 14, 15, 16].map(v => ({
    label: `${v - 12}${v - 12 == 1 ? 'st' : v - 12 == 2 ? 'nd' : v - 12 == 3 ? 'rd' : 'th'} Year`,
    value: v
  }))
})

// Sync year_level when educationLevel changes if it doesn't match
watch(educationLevel, (newVal) => {
  const currentLevel = deriveEducationLevel(profile.value.year_level)
  if (currentLevel !== newVal) {
    // Set to first option of the new level
    profile.value.year_level = yearOptions.value[0].value
  }
})

const loadProfile = async () => {
  try {
    const res = await api.get('/tutee/profile/')
    profile.value = res.data
    educationLevel.value = deriveEducationLevel(res.data.year_level)
  } catch (err) {
    console.error("Failed to load profile", err)
    toastStore.push("Failed to load profile", 'error')
  }
}

const loadSubjects = async () => {
  try {
    const res = await api.get('subjects/')
    subjects.value = res.data
  } catch (err) {
    console.error("Failed to load subjects", err)
  }
}

const loadCourses = async () => {
  try {
    const res = await api.get('courses/')
    courses.value = res.data
  } catch (err) {
    console.error("Failed to load courses", err)
  }
}

const initials = computed(() => {
  const first = profile.value?.fname?.charAt(0) || ''
  const last = profile.value?.lname?.charAt(0) || ''
  return (first + last).toUpperCase()
})

const lastUpdated = computed(() => {
  if (!profile.value.updated_at) return null
  return new Date(profile.value.updated_at).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric'
  })
})

const triggerFileInput = () => {
  fileInput.value.click()
}

const handleAvatarUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  if (!file.type.startsWith('image/')) {
    toastStore.push('Please select an image file', 'error')
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    toastStore.push('Image must be under 5 MB', 'error')
    return
  }

  const formData = new FormData()
  formData.append('avatar', file)

  try {
    const res = await api.post('/tutee/profile/avatar/', formData)
    profile.value.profile_picture_url = res.data.profile_picture_url
    toastStore.push('Photo updated successfully')
  } catch (err) {
    console.error('Avatar upload failed', err)
    toastStore.push('Failed to upload photo', 'error')
  }
}

const discardChanges = () => {
  loadProfile()
}

const saveProfile = async () => {
  try {
    await api.put('/tutee/profile/update/', profile.value)
    toastStore.push("Profile updated successfully")
  } catch (err) {
    console.error(err)
    toastStore.push("Failed to update profile", 'error')
  }
}

onMounted(() => {
  loadProfile()
  loadCourses()
  loadSubjects()
})
</script>

<style scoped>
.tutee-profile-shell {
  min-height: 100vh;
  padding: 2rem;
  background:
    radial-gradient(circle at 0% 0%, rgba(16, 185, 129, 0.32), transparent 38%),
    radial-gradient(circle at 96% 6%, rgba(139, 92, 246, 0.2), transparent 36%),
    radial-gradient(circle at 88% 74%, rgba(14, 165, 233, 0.18), transparent 42%),
    linear-gradient(135deg, #f8fafc 0%, #f5fbf4 100%);
}

.glass-modal {
  max-width: 900px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 24px;
  box-shadow: 0 24px 80px rgba(15, 23, 42, 0.18);
  overflow: hidden;
}

.profile-header {
  background: linear-gradient(135deg, var(--sb-primary-deep) 0%, var(--sb-primary) 100%);
  padding: 3rem 2rem;
  color: white;
}

.avatar-wrapper {
  position: relative;
  width: 120px;
  height: 120px;
}

.avatar-img, .initials-avatar {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border: 4px solid rgba(255, 255, 255, 0.4);
  cursor: pointer;
  transition: transform 0.3s ease;
}

.avatar-img:hover, .initials-avatar:hover {
  transform: scale(1.05);
}

.initials-avatar {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}

.avatar-edit-badge {
  position: absolute;
  bottom: 5px;
  right: 5px;
  background: var(--sb-primary);
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: 2px solid white;
}

.selection-card {
  background: white;
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.selection-card:hover {
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  transform: translateY(-2px);
}

.section-title {
  font-weight: 700;
  color: #1e293b;
  position: relative;
  padding-left: 1rem;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 1.5rem;
  background: var(--sb-primary);
  border-radius: 2px;
}

.input-glass {
  background: rgba(248, 250, 252, 0.8);
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  padding: 0.75rem 1rem;
  transition: all 0.2s ease;
}

.input-glass:focus {
  background: white;
  border-color: var(--sb-primary);
  box-shadow: 0 0 0 4px rgba(0, 137, 90, 0.1);
  outline: none;
}

.border-danger {
  border-color: #dc3545 !important;
}

.glow-danger:focus {
  box-shadow: 0 0 0 4px rgba(220, 53, 69, 0.15) !important;
}

.sb-btn {
  border: none;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.btn-save {
  background: var(--sb-primary);
  color: white;
}

.btn-save:hover {
  background: var(--sb-primary-hover);
  color: white;
}

.btn-discard {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.4);
}

.btn-discard:hover {
  background: rgba(255, 255, 255, 0.35);
  color: white;
}

.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 137, 90, 0.25);
}

.subject-pill-label {
  margin: 0;
  cursor: pointer;
}

.subject-pill {
  display: inline-block;
  padding: 0.4rem 0.9rem;
  border-radius: 9999px;
  border: 1px solid rgba(15, 23, 42, 0.12);
  background: rgba(255, 255, 255, 0.5);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.subject-pill:hover {
  border-color: var(--sb-primary);
  color: var(--sb-primary);
}

.subject-pill.active {
  background: var(--sb-primary);
  color: white;
  border-color: var(--sb-primary);
}
</style>
