import { defineStore } from 'pinia'
import { reactive, ref } from 'vue'
import { INITIAL_BUDGET_MAX, INITIAL_BUDGET_MIN } from '@/stores/initialbookingprefs'

const createDefaultFilters = () => ({
  query: '',
  subject: '',
  mode: '',
  location: '',
  date: null,
  startTime: null,
  endTime: null,
  minRate: INITIAL_BUDGET_MIN,
  maxRate: INITIAL_BUDGET_MAX,
})

export const useFindTutorsStore = defineStore('findTutors', () => {
  const results = ref([])
  const filters = reactive(createDefaultFilters())
  const hasFetched = ref(false)

  const setResults = (data) => {
    results.value = Array.isArray(data) ? data : []
    hasFetched.value = true
  }

  const setFilters = (fields) => {
    if (!fields || typeof fields !== 'object') {
      return
    }

    Object.entries(fields).forEach(([key, value]) => {
      if (Object.prototype.hasOwnProperty.call(filters, key)) {
        filters[key] = value
      }
    })
  }

  const reset = () => {
    results.value = []
    hasFetched.value = false
    Object.assign(filters, createDefaultFilters())
  }

  return {
    results,
    filters,
    hasFetched,
    setResults,
    setFilters,
    reset,
  }
}, {
  persist: {
    storage: sessionStorage,
    key: 'sb-find-tutors',
    pick: ['filters', 'results', 'hasFetched'],
  }
})