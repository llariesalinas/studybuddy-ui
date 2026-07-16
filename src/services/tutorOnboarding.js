import api from '@/services/api/api'

export const fetchTutorSubjects = async () => {
  const { data } = await api.get('/tutor/subjects/')
  return Array.isArray(data) ? data : []
}

export const fetchApprovedSubjects = async (search = '') => {
  const { data } = await api.get('/subjects/', { params: { search } })
  return Array.isArray(data) ? data : []
}

export const fetchSubjectCatalog = async () => {
  const { data } = await api.get('/subjects/', { params: { catalog_scope: 'all' } })
  return Array.isArray(data) ? data : []
}

export const addTutorSubject = async (subjectCode) => {
  const { data } = await api.post('/tutor/subjects/add/', { subject_code: subjectCode })
  return data
}

export const removeTutorSubject = async (subjectCode) => {
  const { data } = await api.delete(`/tutor/subjects/remove/${subjectCode}/`)
  return data
}

export const proposeTutorSubject = async (payload) => {
  const { data } = await api.post('/tutor/subjects/propose/', payload)
  return data
}

export const submitTutorVerification = async (payload, options = {}) => {
  const endpoint = options.resubmit ? '/tutor-application/resubmit/' : '/tutor-application/submit/'
  const { data } = await api.post(endpoint, payload, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export const skipTutorVerification = async () => {
  const { data } = await api.post('/tutor/onboarding/skip-verification/')
  return data
}
