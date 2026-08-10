import api from '@/services/api/api'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { buildCsv, downloadCsv, exportFilename } from '@/utils/csv'
import {
  REPORT_COMBINED_FILE_LABEL,
  USERS_FILE_LABEL,
  USER_COLUMN_GROUPS,
} from '@/constants/superadminExports'

export const useSuperAdminStore = defineStore('superadmin', () => {
  const stats = ref(null)
  const users = ref([])
  const institutions = ref([])
  const institutionPerformance = ref([])
  const analytics = ref(null)
  const pendingActions = ref({ count: 0, items: [] })
  const institutionRequests = ref([])

  const loading = ref({
    stats: false,
    users: false,
    institutions: false,
    institutionPerformance: false,
    analytics: false,
    pendingActions: false,
    institutionRequests: false,
    export: false,
    userExport: false,
  })

  const error = ref({
    stats: null,
    users: null,
    institutions: null,
    institutionPerformance: null,
    analytics: null,
    pendingActions: null,
    institutionRequests: null,
    export: null,
    userExport: null,
  })

  const replaceUser = (updatedUser) => {
    const index = users.value.findIndex((user) => user.id === updatedUser.id)
    if (index !== -1) {
      users.value[index] = { ...users.value[index], ...updatedUser }
    }
  }

  let statsPromise = null
  const fetchStats = async (force = false) => {
    if (stats.value && !force) return
    if (statsPromise) {
      await statsPromise
      if (!force) return
    }

    loading.value.stats = true
    error.value.stats = null

    statsPromise = (async () => {
      try {
        const res = await api.get('/admin/stats/')
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

  let usersPromise = null
  const fetchUsers = async (params = {}, force = false) => {
    const isSearch = Object.keys(params).length > 0
    if (users.value.length && !force && !isSearch) return
    if (usersPromise) {
      await usersPromise
      if (!force && !isSearch) return
    }

    loading.value.users = true
    error.value.users = null

    usersPromise = (async () => {
      try {
        const res = await api.get('/admin/users/', { params })
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
    const res = await api.patch(`/admin/users/${userId}/`, { is_suspended: isSuspended })
    replaceUser(res.data)
    await Promise.all([fetchUsers({}, true), fetchStats(true), fetchPendingActions(true)])
    return res.data
  }

  const updateUserRole = async (userId, role) => {
    const res = await api.patch(`/admin/users/${userId}/`, { role })
    replaceUser(res.data)
    await Promise.all([fetchUsers({}, true), fetchStats(true)])
    return res.data
  }

  const updateUserInstitution = async (userId, institutionId) => {
    const res = await api.patch(`/admin/users/${userId}/`, { institution: institutionId || null })
    replaceUser(res.data)
    await Promise.all([fetchUsers({}, true), fetchInstitutionPerformance(true)])
    return res.data
  }

  const toggleDomainExemption = async (userId, value) => {
    const res = await api.patch(`/admin/users/${userId}/`, { is_domain_exempt: value })
    replaceUser(res.data)
    await fetchPendingActions(true)
    return res.data
  }

  const sendVerificationDevAction = async (userId, action) => {
    const res = await api.post(`/admin/users/${userId}/verification-dev-tools/`, { action })
    return res.data
  }

  let instPromise = null
  const fetchInstitutions = async (force = false) => {
    if (institutions.value.length && !force) return
    if (instPromise) {
      await instPromise
      if (!force) return
    }

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
    const inst = institutions.value.find((item) => item.id === id)
    if (inst) inst.is_active = isActive
    await Promise.all([
      fetchInstitutions(true),
      fetchStats(true),
      fetchPendingActions(true),
      fetchInstitutionPerformance(true),
    ])
  }

  let perfPromise = null
  const fetchInstitutionPerformance = async (force = false) => {
    if (institutionPerformance.value.length && !force) return
    if (perfPromise) {
      await perfPromise
      if (!force) return
    }

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

  let pendingPromise = null
  const fetchPendingActions = async (force = false) => {
    if (pendingActions.value.items.length && !force) return
    if (pendingPromise) {
      await pendingPromise
      if (!force) return
    }

    loading.value.pendingActions = true
    error.value.pendingActions = null

    pendingPromise = (async () => {
      try {
        const res = await api.get('/admin/pending-actions/')
        pendingActions.value = res.data
      } catch {
        error.value.pendingActions = 'Failed to load pending actions.'
      } finally {
        loading.value.pendingActions = false
        pendingPromise = null
      }
    })()

    return pendingPromise
  }

  let institutionRequestsPromise = null
  const fetchInstitutionRequests = async (force = false) => {
    if (institutionRequests.value.length && !force) return
    if (institutionRequestsPromise) {
      await institutionRequestsPromise
      if (!force) return
    }

    loading.value.institutionRequests = true
    error.value.institutionRequests = null

    institutionRequestsPromise = (async () => {
      try {
        const res = await api.get('/admin/institution-requests/')
        institutionRequests.value = res.data
      } catch {
        error.value.institutionRequests = 'Failed to load institution requests.'
      } finally {
        loading.value.institutionRequests = false
        institutionRequestsPromise = null
      }
    })()

    return institutionRequestsPromise
  }

  const approveInstitutionRequest = async (id) => {
    const res = await api.patch(`/admin/institution-requests/${id}/`, { action: 'approve' })
    await Promise.all([
      fetchInstitutionRequests(true),
      fetchPendingActions(true),
      fetchInstitutions(true),
      fetchInstitutionPerformance(true),
      fetchStats(true),
    ])
    return res.data
  }

  const rejectInstitutionRequest = async (id) => {
    const res = await api.patch(`/admin/institution-requests/${id}/`, { action: 'reject' })
    await Promise.all([fetchInstitutionRequests(true), fetchPendingActions(true)])
    return res.data
  }

  const fetchAnalytics = async (institutionId = null, period = '30d') => {
    loading.value.analytics = true
    error.value.analytics = null

    try {
      const params = { period }
      if (institutionId) params.institution_id = institutionId
      const res = await api.get('/admin/analytics/', { params })
      analytics.value = res.data
    } catch {
      error.value.analytics = 'Failed to load analytics.'
    } finally {
      loading.value.analytics = false
    }
  }

  // `sections` narrows which sheets the server writes. Omitting it keeps the endpoint's
  // all-sections default, so an existing caller that does not pass it is unaffected. The response
  // is an xlsx workbook; downloadCsv passes the blob through with the server's content type.
  const exportAnalyticsWorkbook = async ({
    institutionId = null,
    period = '30d',
    sections = [],
    filename = '',
  } = {}) => {
    loading.value.export = true
    error.value.export = null

    try {
      const params = { period }
      if (institutionId) params.institution_id = institutionId
      if (sections.length) params.sections = sections.join(',')

      const res = await api.get('/admin/analytics/export/', {
        params,
        responseType: 'blob',
      })
      downloadCsv(filename || exportFilename(REPORT_COMBINED_FILE_LABEL, 'xlsx'), res.data)
    } catch {
      error.value.export = 'Failed to export analytics.'
      throw new Error(error.value.export)
    } finally {
      loading.value.export = false
    }
  }

  // Built client-side: /admin/users/ already returns the whole directory, so the rows the admin
  // sees are the rows we write. `groupIds` selects column groups, in declaration order.
  const exportUsersCsv = (rows, groupIds = [], filename = '') => {
    const groups = USER_COLUMN_GROUPS.filter((group) => groupIds.includes(group.id))
    if (!groups.length) return

    const columns = groups.flatMap((group) => group.columns)
    const csv = buildCsv([
      columns.map((column) => column.header),
      ...rows.map((row) => columns.map((column) => column.value(row))),
    ])

    downloadCsv(filename || exportFilename(USERS_FILE_LABEL), csv)
  }

  const fetchUserBookings = async (
    userId,
    { page = 1, dateFrom = null, dateTo = null } = {},
  ) => {
    const params = { page }
    if (dateFrom) params.date_from = dateFrom
    if (dateTo) params.date_to = dateTo
    const res = await api.get(`/admin/users/${userId}/bookings/`, { params })
    return res.data
  }

  const exportUserCsv = async (endpoint, filename, params = {}) => {
    loading.value.userExport = true
    error.value.userExport = null

    try {
      const res = await api.get(endpoint, { params, responseType: 'blob' })
      downloadCsv(filename, res.data)
    } catch {
      error.value.userExport = 'Failed to export user data.'
      throw new Error(error.value.userExport)
    } finally {
      loading.value.userExport = false
    }
  }

  const exportUserBookingsCsv = async (
    userId,
    { dateFrom = null, dateTo = null } = {},
  ) => {
    const params = {}
    if (dateFrom) params.date_from = dateFrom
    if (dateTo) params.date_to = dateTo
    return exportUserCsv(
      `/admin/users/${userId}/bookings/export/`,
      `bookings-${userId}.csv`,
      params,
    )
  }

  const fetchUserAvailability = async (userId) => {
    const res = await api.get(`/admin/users/${userId}/availability/`)
    return res.data
  }

  const exportUserAvailabilityCsv = async (userId) =>
    exportUserCsv(
      `/admin/users/${userId}/availability/export/`,
      `availability-${userId}.csv`,
    )

  const fetchUserStats = async (userId) => {
    const res = await api.get(`/admin/users/${userId}/stats/`)
    return res.data
  }

  const exportUserStatsCsv = async (userId) =>
    exportUserCsv(`/admin/users/${userId}/stats/export/`, `stats-${userId}.csv`)

  return {
    stats,
    users,
    institutions,
    institutionPerformance,
    analytics,
    pendingActions,
    institutionRequests,
    loading,
    error,

    fetchStats,
    fetchUsers,
    updateUserStatus,
    updateUserRole,
    updateUserInstitution,
    toggleDomainExemption,
    sendVerificationDevAction,
    fetchInstitutions,
    addInstitution,
    toggleInstitutionActive,
    fetchInstitutionPerformance,
    fetchPendingActions,
    fetchInstitutionRequests,
    approveInstitutionRequest,
    rejectInstitutionRequest,
    fetchAnalytics,
    exportAnalyticsWorkbook,
    exportUsersCsv,
    fetchUserBookings,
    exportUserBookingsCsv,
    fetchUserAvailability,
    exportUserAvailabilityCsv,
    fetchUserStats,
    exportUserStatsCsv,
  }
})
