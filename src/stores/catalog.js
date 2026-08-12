import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api/api'
import { cachedGet, clearApiCache } from '@/services/api/cache'
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

  // Subjects are also served (as `subjects`) from a session-cached `subjects/` fetch used by
  // tutee-facing pickers. That cache has no other invalidation trigger, so every mutation below
  // that can change what a tutee should see (add, edit, remove, or an external approve/reject)
  // must burst it or those pickers keep serving a stale list until the cache's TTL expires.
  function invalidateSubjectsCache() {
    clearApiCache('catalog')
  }

  async function addCatalogSubject(payload) {
    const { data } = await api.post('/admin/course-catalog/', payload)
    courseCatalog.value = [...courseCatalog.value, data]
    invalidateSubjectsCache()
    return data
  }

  async function updateCatalogSubject(subjectCode, payload) {
    const { data } = await api.patch(`/admin/course-catalog/${subjectCode}/`, payload)
    courseCatalog.value = courseCatalog.value.map((subject) =>
      subject.subject_code === subjectCode ? data : subject,
    )
    invalidateSubjectsCache()
    return data
  }

  async function removeCatalogSubject(subjectCode) {
    await api.delete(`/admin/course-catalog/${subjectCode}/`)
    courseCatalog.value = courseCatalog.value.filter(
      (subject) => subject.subject_code !== subjectCode,
    )
    invalidateSubjectsCache()
  }

  // Syncs a subject that was already persisted elsewhere (e.g. the tutor-application review
  // panel's own save endpoint) into local catalog state, so category/keyword pickers derived from
  // `courseCatalog` update immediately instead of waiting on the next fetchCourseCatalog().
  function upsertLocalCatalogSubject(subject) {
    if (!subject?.subject_code) return
    const index = courseCatalog.value.findIndex((item) => item.subject_code === subject.subject_code)
    if (index === -1) {
      courseCatalog.value = [...courseCatalog.value, subject]
    } else {
      courseCatalog.value = courseCatalog.value.map((item, i) =>
        i === index ? { ...item, ...subject } : item,
      )
    }
    invalidateSubjectsCache()
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
    upsertLocalCatalogSubject,
    invalidateSubjectsCache,
    fetchPaymentMethods,
    fetchReceivingInstitutions,
  }
})
