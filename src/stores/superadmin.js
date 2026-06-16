import api from '@/services/api/api'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSuperAdminStore = defineStore('superadmin', () => {
  const stats = ref(null)
  const users = ref([])
  const institutions = ref([])
  const institutionPerformance = ref([])
  const analytics = ref(null)

  const loading = ref({
    stats: false,
    users: false,
    institutions: false,
    institutionPerformance: false,
    analytics: false,
  })

  const error = ref({
    stats: null,
    users: null,
    institutions: null,
    institutionPerformance: null,
    analytics: null,
  })

  // ── Stats ──────────────────────────────────────────────────────────────────
  let statsPromise = null
  const fetchStats = async (force = false) => {
    if (stats.value && !force) return
    if (statsPromise) { await statsPromise; if (!force) return }

    loading.value.stats = true
    error.value.stats = null

    statsPromise = (async () => {
      try {
        const res = await api.get('/admin/stats')
        stats.value = res.data
      } catch {
        error.value.stats = 'Failed to load statistics.'
      } finally {
        loading.value.stats = false
        statsPromise = null
      }
    })()

    return statsPromise
  }

  // ── Users ──────────────────────────────────────────────────────────────────
  let usersPromise = null
  const fetchUsers = async (params = {}, force = false) => {
    const isSearch = Object.keys(params).length > 0
    if (users.value.length && !force && !isSearch) return
    if (usersPromise) { await usersPromise; if (!force && !isSearch) return }

    loading.value.users = true
    error.value.users = null

    usersPromise = (async () => {
      try {
        const res = await api.get('/admin/users', { params })
        users.value = res.data
      } catch {
        error.value.users = 'Failed to load users.'
      } finally {
        loading.value.users = false
        usersPromise = null
      }
    })()

    return usersPromise
  }

  const updateUserStatus = async (userId, isSuspended) => {
    await api.patch(`/admin/users/${userId}/`, { is_suspended: isSuspended })
    const u = users.value.find(u => u.id === userId)
    if (u) u.is_suspended = isSuspended
    Promise.all([fetchUsers({}, true), fetchStats(true)])
  }

  // ── Institutions ───────────────────────────────────────────────────────────
  let instPromise = null
  const fetchInstitutions = async (force = false) => {
    if (institutions.value.length && !force) return
    if (instPromise) { await instPromise; if (!force) return }

    loading.value.institutions = true
    error.value.institutions = null

    instPromise = (async () => {
      try {
        const res = await api.get('/admin/institutions/')
        institutions.value = res.data
      } catch {
        error.value.institutions = 'Failed to load institutions.'
      } finally {
        loading.value.institutions = false
        instPromise = null
      }
    })()

    return instPromise
  }

  const addInstitution = async (payload) => {
    await api.post('/admin/institutions/', payload)
    await fetchInstitutions(true)
  }

  const toggleInstitutionActive = async (id, isActive) => {
    await api.patch(`/admin/institutions/${id}/`, { is_active: isActive })
    const inst = institutions.value.find(i => i.id === id)
    if (inst) inst.is_active = isActive
    Promise.all([fetchInstitutions(true), fetchStats(true)])
  }

  // ── Institution Performance ────────────────────────────────────────────────
  let perfPromise = null
  const fetchInstitutionPerformance = async (force = false) => {
    if (institutionPerformance.value.length && !force) return
    if (perfPromise) { await perfPromise; if (!force) return }

    loading.value.institutionPerformance = true
    error.value.institutionPerformance = null

    perfPromise = (async () => {
      try {
        const res = await api.get('/admin/institutions/performance/')
        institutionPerformance.value = res.data
      } catch {
        error.value.institutionPerformance = 'Failed to load performance data.'
      } finally {
        loading.value.institutionPerformance = false
        perfPromise = null
      }
    })()

    return perfPromise
  }

  // ── Analytics ──────────────────────────────────────────────────────────────
  const fetchAnalytics = async (institutionId = null) => {
    loading.value.analytics = true
    error.value.analytics = null

    try {
      const params = institutionId ? { institution_id: institutionId } : {}
      const res = await api.get('/admin/analytics', { params })
      analytics.value = res.data
    } catch {
      error.value.analytics = 'Failed to load analytics.'
    } finally {
      loading.value.analytics = false
    }
  }

  return {
    stats,
    users,
    institutions,
    institutionPerformance,
    analytics,
    loading,
    error,

    fetchStats,
    fetchUsers,
    updateUserStatus,
    fetchInstitutions,
    addInstitution,
    toggleInstitutionActive,
    fetchInstitutionPerformance,
    fetchAnalytics,
  }
})
