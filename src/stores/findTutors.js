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

// Which filter actually produced the results. Without it the UI cannot tell an exact date match
// from a fallback, and the header ends up claiming availability nobody checked.
export const MATCH_STAGE_EXACT = 'exact'
export const MATCH_STAGE_DATE_ONLY = 'date_only'
export const MATCH_STAGE_SUBJECT_ONLY = 'subject_only'

export const useFindTutorsStore = defineStore('findTutors', () => {
  const results = ref([])
  const filters = reactive(createDefaultFilters())
  const hasFetched = ref(false)
  const matchStage = ref(MATCH_STAGE_EXACT)

  const setResults = (data, stage = MATCH_STAGE_EXACT) => {
    results.value = Array.isArray(data) ? data : []
    matchStage.value = stage
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
    matchStage.value = MATCH_STAGE_EXACT
    hasFetched.value = false
    Object.assign(filters, createDefaultFilters())
  }

  return {
    results,
    filters,
    hasFetched,
    matchStage,
    setResults,
    setFilters,
    reset,
  }
}, {
  persist: {
    storage: sessionStorage,
    key: 'sb-find-tutors',
    pick: ['filters', 'results', 'hasFetched', 'matchStage'],
  }
})