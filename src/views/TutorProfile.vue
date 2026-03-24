<template>
<div class="profile-content">

  <div class="mb-4">
    <h2 class="fw-bold text-dark">My Profile</h2>
    <p class="text-muted">Manage your tutoring information.</p>
  </div>

  <div class="card border-sb shadow-sm rounded-4">
  <div class="card-body p-4 p-md-5">

  <!-- Avatar -->
  <div class="d-flex align-items-center mb-4 pb-4 border-bottom">
    <div
      class="rounded-circle bg-success bg-opacity-10 d-flex justify-content-center align-items-center fw-bold fs-3 me-4"
      style="width:80px;height:80px"
    >
      {{ initials }}
    </div>

    <div>
      <h5 class="fw-bold mb-1">{{ profile.fullName }}</h5>
      <p class="text-muted small mb-2">Tutor</p>
    </div>
  </div>

<form @submit.prevent="saveProfile">

<div class="row g-4">

<!-- NAME -->
<div class="col-md-6">
<label class="form-label fw-semibold small">Full Name</label>
<input v-model="profile.fullName" class="form-control">
</div>

<!-- EMAIL -->
<div class="col-md-6">
<label class="form-label fw-semibold small">Email</label>
<input :value="profile.email" disabled class="form-control bg-light">
</div>

<!-- COURSE -->
<div class="col-md-6">
<label class="form-label fw-semibold small">Course</label>

<select v-model="profile.course" class="form-select">

<option value="">Select Course</option>

<option
  v-for="c in courses"
  :key="c.course_code"
  :value="c.course_code"
>
  {{ c.course_code }} - {{ c.course_name }}
</option>

</select>
</div>

<!-- YEAR LEVEL -->
<div class="col-md-6">
<label class="form-label fw-semibold small">Year Level</label>

<select v-model.number="profile.year_level" class="form-select">

<option value="">Select Level</option>

<option
  v-for="y in yearLevels"
  :key="y.value"
  :value="y.value"
>
  {{ y.label }}
</option>

</select>
</div>

<!-- HOURLY RATE -->
<div class="col-md-6">
<label class="form-label fw-semibold small">Hourly Rate</label>
<input type="number" v-model="profile.hourly_rate" class="form-control">
</div>

<!-- TEACHING LEVEL -->
<div class="col-md-6">
<label class="form-label fw-semibold small">Teaching Level</label>
<input v-model="profile.teaching_level" class="form-control">
</div>

<!-- SESSION MODE -->
<div class="col-md-6">

<label class="form-label fw-semibold small">Session Mode</label>

<div class="form-check">
<input type="checkbox" v-model="profile.can_online" class="form-check-input">
<label class="form-check-label">Online</label>
</div>

<div class="form-check">
<input type="checkbox" v-model="profile.can_f2f" class="form-check-input">
<label class="form-check-label">Face-to-Face</label>
</div>

</div>

<!-- SUBJECTS -->
<div class="col-12">

<label class="form-label fw-semibold small">Subjects</label>

<div class="d-flex flex-wrap gap-2 mb-3">

<span
v-for="s in profile.subjects"
:key="s.subject_code"
class="badge bg-sb-primary px-3 py-2"
>

{{ s.subject_name }}

<button
type="button"
class="btn-close btn-close-white ms-2"
style="font-size:10px"
@click="removeSubject(s.subject_code)"
></button>

</span>

</div>

<div class="d-flex gap-2">

<select v-model="newSubject" class="form-select">

<option value="">Select subject</option>

<option
v-for="s in allSubjects"
:key="s.subject_code"
:value="s.subject_code"
>
{{ s.subject_name }}
</option>

</select>

<button
type="button"
class="btn btn-outline-dark"
@click="addSubject"
>
Add
</button>

</div>

</div>

<!-- BIO -->
<div class="col-12">

<label class="form-label fw-semibold small">Bio</label>

<textarea
v-model="profile.bio"
rows="4"
class="form-control"
></textarea>

</div>

</div>

<div class="text-end mt-4">
<button class="btn bg-sb-primary text-white px-4">
Save Changes
</button>
</div>

</form>

</div>
</div>
</div>
</template>

<script setup>

import { ref, computed, onMounted } from 'vue'
import api from '@/services/api/api'

const profile = ref({
  fullName: '',
  email: '',
  course: '',
  year_level: null,
  subjects: [],
  bio: '',
  hourly_rate: '',
  teaching_level: '',
  can_online: true,
  can_f2f: false
})

const courses = ref([])
const allSubjects = ref([])
const newSubject = ref('')

/* YEAR LEVELS */
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

/* INITIALS */
const initials = computed(() => {

  if (!profile.value.fullName) return ''

  return profile.value.fullName
    .split(' ')
    .map(n => n[0])
    .join('')

})

/* LOAD PROFILE */
const loadProfile = async () => {

  try {

    const res = await api.get('/tutor/profile/')
    const data = res.data

    profile.value.fullName = `${data.fname} ${data.lname}`
    profile.value.email = data.email
    profile.value.course = data.course
    profile.value.year_level = data.year_level
    profile.value.bio = data.bio

    profile.value.hourly_rate = data.hourly_rate
    profile.value.teaching_level = data.teaching_level
    profile.value.can_online = data.can_online
    profile.value.can_f2f = data.can_f2f

    const subjectRes = await api.get('/tutor/subjects/')
    profile.value.subjects = subjectRes.data

  } catch (err) {

    console.error("Failed to load tutor profile:", err)

  }

}

/* LOAD SUBJECTS */
const loadSubjects = async () => {

  const res = await api.get('/subjects/')
  allSubjects.value = res.data

}

/* LOAD COURSES */
const loadCourses = async () => {

  const res = await api.get('/courses/')
  courses.value = res.data

}

/* ADD SUBJECT */
const addSubject = async () => {

  if (!newSubject.value) return

  await api.post('/tutor/subjects/add/', {
    subject_code: newSubject.value
  })

  newSubject.value = ''
  await loadProfile()

}

/* REMOVE SUBJECT */
const removeSubject = async (code) => {

  await api.delete(`/tutor/subjects/remove/${code}/`)
  await loadProfile()

}

/* SAVE PROFILE */
const saveProfile = async () => {

  const names = profile.value.fullName.split(' ')

  const tuteePayload = {
    fname: names[0],
    lname: names.slice(1).join(' '),
    course: profile.value.course,
    year_level: profile.value.year_level,
    bio: profile.value.bio
  }

  const tutorPayload = {
    hourly_rate: profile.value.hourly_rate,
    teaching_level: profile.value.teaching_level,
    can_online: profile.value.can_online,
    can_f2f: profile.value.can_f2f
  }

  try {

    // Update profile (UserProfile)
    await api.put('/tutee/profile/update/', tuteePayload)

    // Update tutor info (Tutor model)
    await api.put('/tutor/update/', tutorPayload)

    alert("Profile Updated")

  } catch (err) {

    console.error("Profile update failed:", err)

  }

}

/* MOUNT */
onMounted(() => {

  loadProfile()
  loadSubjects()
  loadCourses()

})

</script>