<template>
  <div class="tutee-profile-shell py-5">
    <div class="container py-lg-4">
      <div class="glass-modal p-0 overflow-hidden border-0 shadow-2xl">
        
        <form @submit.prevent="saveProfile" class="p-4 p-md-5">
          
          <!-- PROFILE HEADER -->
          <div class="profile-header d-flex align-items-center mb-5 pb-4 border-bottom border-light border-opacity-10">
            <div class="avatar-container me-4 position-relative">
              <img v-if="profile.profile_picture" :src="profile.profile_picture" class="rounded-circle avatar-img" @click="triggerFileInput">
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
              <p class="text-white text-opacity-75 mb-0">Tutee / {{ educationLevel.toUpperCase() }}</p>
            </div>
          </div>

          <div class="profile-body">
            <div class="row g-4">
              
              <!-- LEFT COLUMN (7/12): Personal Info + Bio -->
              <div class="col-lg-7">
                <div class="bento-card p-4 h-100">
                  <h5 class="section-title mb-4">Personal Information</h5>
                  
                  <div class="row g-3">
                    <div class="col-md-4">
                      <label class="form-label text-muted small fw-bold">First Name</label>
                      <input type="text" v-model="profile.fname" class="form-control sb-input">
                    </div>
                    <div class="col-md-4">
                      <label class="form-label text-muted small fw-bold">Middle Name</label>
                      <input type="text" v-model="profile.mname" class="form-control sb-input">
                    </div>
                    <div class="col-md-4">
                      <label class="form-label text-muted small fw-bold">Last Name</label>
                      <input type="text" v-model="profile.lname" class="form-control sb-input">
                    </div>
                    
                    <div class="col-12 mt-3">
                      <label class="form-label text-muted small fw-bold">University Email</label>
                      <input type="email" v-model="profile.email" class="form-control sb-input bg-light" disabled title="Email cannot be changed">
                      <div class="form-text small opacity-50">Email cannot be changed after registration.</div>
                    </div>

                    <div class="col-12 mt-4">
                      <div class="d-flex justify-content-between">
                        <label class="form-label text-muted small fw-bold">Bio (About Me)</label>
                        <span class="text-muted small">{{ bioCharCount }}/500</span>
                      </div>
                      <textarea 
                        v-model="profile.bio" 
                        class="form-control sb-input" 
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
                <div class="bento-card p-4 h-100">
                  <h5 class="section-title mb-4">Academic Context</h5>
                  
                  <div class="row g-3">
                    <div class="col-12">
                      <label class="form-label text-muted small fw-bold">Education Level</label>
                      <select v-model="educationLevel" class="form-select sb-input">
                        <option value="elementary">Elementary</option>
                        <option value="jhs">Junior High School</option>
                        <option value="shs">Senior High School</option>
                        <option value="college">College / University</option>
                      </select>
                    </div>

                    <div class="col-12 mt-3">
                      <label class="form-label text-muted small fw-bold">Year Level</label>
                      <select v-model="profile.year_level" class="form-select sb-input">
                        <option v-for="opt in yearOptions" :key="opt.value" :value="opt.value">
                          {{ opt.label }}
                        </option>
                      </select>
                    </div>

                    <div class="col-12 mt-3" v-if="educationLevel === 'college' || educationLevel === 'shs'">
                      <label class="form-label text-muted small fw-bold">
                        {{ educationLevel === 'college' ? 'Degree Program / Course' : 'Academic Strand' }}
                      </label>
                      <select v-model="profile.course" class="form-select sb-input">
                        <option value="">Select {{ educationLevel === 'college' ? 'Course' : 'Strand' }}</option>
                        <option v-for="c in courses" :key="c.course_code" :value="c.course_code">
                          {{ c.course_name }}
                        </option>
                      </select>
                    </div>

                    <div class="col-12 mt-4">
                      <label class="form-label text-muted small fw-bold">Preferred Subjects</label>
                      <select v-model="profile.subjects" class="form-select sb-input custom-multiselect" multiple>
                        <option v-for="s in subjects" :key="s.subject_code" :value="s.subject_code">
                          {{ s.subject_name }}
                        </option>
                      </select>
                      <div class="form-text mt-2 small opacity-50">Hold Ctrl (Windows) or Cmd (Mac) to select multiple subjects.</div>
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </div>

          <!-- PROFILE FOOTER -->
          <div class="profile-footer d-flex justify-content-end mt-5 pt-4 border-top border-light border-opacity-10">
            <button type="submit" class="btn btn-save-profile px-5 py-3 fw-bold rounded-pill shadow-lg">
              Save Profile Changes
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
  profile_picture: '',
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

const triggerFileInput = () => {
  fileInput.value.click()
}

const handleAvatarUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  const formData = new FormData()
  formData.append('profile_picture', file)

  try {
    const res = await api.post('/tutee/profile/avatar/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    profile.value.profile_picture = res.data.profile_picture
    toastStore.push("Avatar updated successfully")
  } catch (err) {
    console.error("Avatar upload failed", err)
    toastStore.push("Failed to upload avatar", 'error')
  }
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
