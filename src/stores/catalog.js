import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api/api'
import { cachedGet } from '@/services/api/cache'
import {
  CATALOG_CACHE_TTL_MS,
  PARTNER_INSTITUTIONS_CACHE_TTL_MS,
  PAYMENT_METHODS_CACHE_TTL_MS,
  RECEIVING_INSTITUTIONS_CACHE_TTL_MS,
} from '@/config'

export const useCatalogStore = defineStore('catalog', () => {
  const subjects = ref([])
  const courses = ref([])
  const institutions = ref([])
  const courseCatalog = ref([])
  const paymentMethods = ref([])
  const receivingInstitutions = ref([])

  async function fetchSubjects(options = {}) {
    const { data } = await cachedGet('subjects/', {
      ttlMs: CATALOG_CACHE_TTL_MS,
      scope: 'catalog',
      ...options,
    })
    subjects.value = Array.isArray(data) ? data : []
    return subjects.value
  }

  async function fetchCourses(options = {}) {
    const { data } = await cachedGet('courses/', {
      ttlMs: CATALOG_CACHE_TTL_MS,
      scope: 'catalog',
      ...options,
    })
    courses.value = Array.isArray(data) ? data : []
    return courses.value
  }

  async function fetchPartnerInstitutions(options = {}) {
    const { data } = await cachedGet('partner-institutions/', {
      ttlMs: PARTNER_INSTITUTIONS_CACHE_TTL_MS,
      scope: 'catalog',
      ...options,
    })
    institutions.value = Array.isArray(data) ? data : []
    return institutions.value
  }

  async function fetchCourseCatalog({ course = null, institutionId = null } = {}) {
    const params = {}
    if (course) params.course = course
    if (institutionId) params.institution_id = institutionId

    const { data } = await api.get('/admin/course-catalog/', { params })
    courseCatalog.value = Array.isArray(data) ? data : []
    return courseCatalog.value
  }

  async function addCatalogEntry({ course, subject, institutionId = null }) {
    const payload = { course, subject }
    if (institutionId) payload.institution_id = institutionId

    const { data } = await api.post('/admin/course-catalog/', payload)
    courseCatalog.value = [...courseCatalog.value, data]
    return data
  }

  async function removeCatalogEntry(entryId) {
    await api.delete(`/admin/course-catalog/${entryId}/`)
    courseCatalog.value = courseCatalog.value.filter((entry) => entry.id !== entryId)
  }

  async function addCustomSubject({ subjectCode, subjectName, department, institutionId = null }) {
    const payload = {
      subject_code: subjectCode,
      subject_name: subjectName,
      department,
    }
    if (institutionId) payload.institution_id = institutionId

    const { data } = await api.post('/admin/subjects/custom/', payload)
    subjects.value = [...subjects.value, data]
    return data
  }

  async function fetchPaymentMethods(options = {}) {
    const { data } = await cachedGet('payment-methods/', {
      ttlMs: PAYMENT_METHODS_CACHE_TTL_MS,
      scope: 'catalog',
      ...options,
    })
    paymentMethods.value = Array.isArray(data) ? data : []
    return paymentMethods.value
  }

  async function fetchReceivingInstitutions(options = {}) {
    const { data } = await cachedGet('wallet/receiving-institutions/', {
      ttlMs: RECEIVING_INSTITUTIONS_CACHE_TTL_MS,
      scope: 'catalog',
      cacheKey: 'wallet/receiving-institutions',
      ...options,
    })
    receivingInstitutions.value = Array.isArray(data) ? data : []
    return receivingInstitutions.value
  }

  return {
    subjects,
    courses,
    institutions,
    courseCatalog,
    paymentMethods,
    receivingInstitutions,
    fetchSubjects,
    fetchCourses,
    fetchPartnerInstitutions,
    fetchCourseCatalog,
    addCatalogEntry,
    removeCatalogEntry,
    addCustomSubject,
    fetchPaymentMethods,
    fetchReceivingInstitutions,
  }
})
