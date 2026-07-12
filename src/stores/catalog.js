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

  async function fetchCourseCatalog() {
    const { data } = await api.get('/admin/course-catalog/')
    courseCatalog.value = Array.isArray(data) ? data : []
    return courseCatalog.value
  }

  async function addCatalogSubject(payload) {
    const { data } = await api.post('/admin/course-catalog/', payload)
    courseCatalog.value = [...courseCatalog.value, data]
    return data
  }

  async function updateCatalogSubject(subjectCode, payload) {
    const { data } = await api.patch(`/admin/course-catalog/${subjectCode}/`, payload)
    courseCatalog.value = courseCatalog.value.map((subject) =>
      subject.subject_code === subjectCode ? data : subject,
    )
    return data
  }

  async function removeCatalogSubject(subjectCode) {
    await api.delete(`/admin/course-catalog/${subjectCode}/`)
    courseCatalog.value = courseCatalog.value.filter(
      (subject) => subject.subject_code !== subjectCode,
    )
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
    addCatalogSubject,
    updateCatalogSubject,
    removeCatalogSubject,
    fetchPaymentMethods,
    fetchReceivingInstitutions,
  }
})
