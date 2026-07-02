import { defineStore } from 'pinia'
import { ref } from 'vue'
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
    paymentMethods,
    receivingInstitutions,
    fetchSubjects,
    fetchCourses,
    fetchPartnerInstitutions,
    fetchPaymentMethods,
    fetchReceivingInstitutions,
  }
})
