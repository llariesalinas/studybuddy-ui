<template>
  <div class="profile-content">
    <div class="mb-4">
      <h2 class="fw-bold text-dark">My Profile</h2>
      <p class="text-muted">Manage your personal information and tutoring preferences.</p>
    </div>

    <div class="card border-sb shadow-sm rounded-4" style="max-width: 800px;">
      <div class="card-body p-4 p-md-5">
        
        <!-- PROFILE HEADER -->
        <div class="d-flex align-items-center mb-4 pb-4 border-bottom border-sb">
          <div
            class="rounded-circle bg-success bg-opacity-10 text-sb-primary d-flex justify-content-center align-items-center fw-bold fs-3 me-4"
            style="width: 80px; height: 80px;"
          >
            {{ initials }}
          </div>

          <div>
            <h5 class="fw-bold mb-1">
              {{ profile.fname }} {{ profile.lname }}
            </h5>
            <p class="text-muted small mb-2">Student / Tutee</p>
            <button class="btn btn-outline-dark btn-sm rounded-3 fw-semibold px-3">
              Update Photo
            </button>
          </div>
        </div>

        <form @submit.prevent="saveProfile">

          <div class="row g-4 mb-4">

            <!-- FIRST NAME -->
            <div class="col-md-4">
              <label class="form-label fw-semibold small text-dark">First Name</label>
              <input
                type="text"
                v-model="profile.fname"
                class="form-control border-sb shadow-none"
              >
            </div>

            <!-- MIDDLE NAME -->
            <div class="col-md-4">
              <label class="form-label fw-semibold small text-dark">Middle Name</label>
              <input
                type="text"
                v-model="profile.mname"
                class="form-control border-sb shadow-none"
              >
            </div>

            <!-- LAST NAME -->
            <div class="col-md-4">
              <label class="form-label fw-semibold small text-dark">Last Name</label>
              <input
                type="text"
                v-model="profile.lname"
                class="form-control border-sb shadow-none"
              >
            </div>

            <!-- EMAIL -->
            <div class="col-md-6">
              <label class="form-label fw-semibold small text-dark">University Email</label>
              <input
                type="email"
                v-model="profile.email"
                class="form-control border-sb shadow-none bg-light text-muted"
                disabled
              >
              <div class="form-text small">
                Email cannot be changed after registration.
              </div>
            </div>

            <!-- COURSE -->
            <div class="col-md-6">
              <label class="form-label fw-semibold">Course</label>

              <select v-model="profile.course" class="form-select">

                <option value="">Select Course</option>

                <option
                  v-for="course in courses"
                  :key="course.course_code"
                  :value="course.course_code"
                >
                  {{ course.course_name }}
                </option>

              </select>
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold">Preferred Subjects</label>

              <select
                v-model="profile.subjects"
                class="form-select"
                multiple
              >

                <option
                  v-for="subject in subjects"
                  :key="subject.subject_code"
                  :value="subject.subject_code"
                >
                  {{ subject.subject_name }}
                </option>

              </select>

            </div>

            <!-- YEAR LEVEL -->
            <div class="col-md-6">
              <label class="form-label fw-semibold">Year Level</label>

              <select v-model="profile.year_level" class="form-select">

                <option value="">Select Year Level</option>

                <option
                  v-for="level in yearLevels"
                  :key="level.value"
                  :value="level.value"
                >
                  {{ level.label }}
                </option>

              </select>
            </div>

            <!-- BIO -->
            <div class="col-12">
              <label class="form-label fw-semibold small text-dark">
                Bio (About Me)
              </label>

              <textarea
                v-model="profile.bio"
                class="form-control border-sb shadow-none"
                rows="4"
                placeholder="Tell tutors a bit about your learning style or what you usually need help with..."
              ></textarea>
            </div>

          </div>

          <div class="text-end mt-2">
            <button
              type="submit"
              class="btn bg-sb-primary text-white px-5 py-2 rounded-3 fw-semibold shadow-sm"
            >
              Save Changes
            </button>
          </div>

        </form>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api/api'

const profile = ref({
  fname: '',
  lname: '',
  email: '',
  course: '',
  year_level: '',
  bio: ''
})

const courses = ref([])

/*
-----------------------------
LOAD PROFILE DATA
-----------------------------
*/
const loadProfile = async () => {
  try {
    const res = await api.get('/tutee/profile/')
    profile.value = res.data
  } catch (err) {
    console.error("Failed to load profile", err)
  }
}

const yearLevels = [

  { label: "Grade 1", value: 1 },
  { label: "Grade 2", value: 2 },
  { label: "Grade 3", value: 3 },
  { label: "Grade 4", value: 4 },
  { label: "Grade 5", value: 5 },
  { label: "Grade 6", value: 6 },
  { label: "Grade 7", value: 7 },
  { label: "Grade 8", value: 8 },
  { label: "Grade 9", value: 9 },
  { label: "Grade 10", value: 10 },
  { label: "Grade 11", value: 11 },
  { label: "Grade 12", value: 12 },

  { label: "1st Year College", value: 13 },
  { label: "2nd Year College", value: 14 },
  { label: "3rd Year College", value: 15 },
  { label: "4th Year College", value: 16 }

]


const subjects = ref([])

const loadSubjects = async () => {

  const res = await api.get('subjects/')

  subjects.value = res.data

}
/*
-----------------------------
LOAD COURSES FOR DROPDOWN
-----------------------------
*/
const loadCourses = async () => {
  try {

    const res = await api.get('courses/')

    console.log("Courses loaded:", res.data)

    courses.value = res.data

  } catch (err) {
    console.error("Failed to load courses", err)
  }
}

import { computed } from 'vue'

const initials = computed(() => {

  const first = profile.value?.fname?.charAt(0) || ''
  const last = profile.value?.lname?.charAt(0) || ''

  return (first + last).toUpperCase()

})
/*
-----------------------------
SAVE PROFILE
-----------------------------
*/
const saveProfile = async () => {
  try {

    await api.put('/tutee/profile/update/', profile.value)

    alert("Profile updated successfully")

  } catch (err) {
    console.error(err)
    alert("Failed to update profile")
  }
}

onMounted(() => {
  loadProfile()
  loadCourses()
  loadSubjects()
})
</script>