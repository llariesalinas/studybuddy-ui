import api from "@/services/api/api";
import { defineStore } from "pinia";
import { ref } from "vue";

export const useAdminStore = defineStore(
  'admin',
  () => {

    const stats = ref(null)
    const users = ref([])
    const withdrawals = ref([])
    const institutions = ref([])
    const analytics = ref(null)
    const tutorApplications = ref([])
    const tuteeApplications = ref([])
    const operationalQueue = ref({ count: 0, items: [] })

    const loading = ref({
      stats: false,
      users: false,
      withdrawals: false,
      institutions: false,
      analytics: false,
      tutorApplications: false,
      tuteeApplications: false,
      operationalQueue: false
    })

    const error = ref({
      stats: null,
      users: null,
      withdrawals: null,
      institutions: null,
      analytics: null,
      tutorApplications: null,
      tuteeApplications: null,
      operationalQueue: null
    })

    let statsPromise = null
    const fetchStats = async (force = false) => {
      // 1. If we have data and aren't forcing, return immediately
      if (stats.value && !force) return

      // 2. If a request is already in flight, wait for it
      if (statsPromise) {
        await statsPromise
        // After waiting, if we weren't forcing, we can stop here
        if (!force) return
      }

      // 3. Start a new request
      loading.value.stats = true
      error.value.stats = null

      statsPromise = (async () => {
        try {
          const response = await api.get('/admin/stats/')
          stats.value = response.data
        } catch (err) {
          console.error('Failed to load statistics:', err)
          error.value.stats = 'Failed to load statistics.'
        } finally {
          loading.value.stats = false
          statsPromise = null
        }
      })()

      return statsPromise
    }

    let operationalQueuePromise = null
    const fetchOperationalQueue = async (force = false) => {
      if (operationalQueue.value.items.length && !force) return

      if (operationalQueuePromise) {
        await operationalQueuePromise
        if (!force) return
      }

      loading.value.operationalQueue = true
      error.value.operationalQueue = null

      operationalQueuePromise = (async () => {
        try {
          const response = await api.get('/admin/operational-queue/')
          operationalQueue.value = response.data
        } catch (err) {
          console.error('Failed to load operational queue:', err)
          error.value.operationalQueue = 'Failed to load operational queue.'
        } finally {
          loading.value.operationalQueue = false
          operationalQueuePromise = null
        }
      })()

      return operationalQueuePromise
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
          const response = await api.get('/admin/users/', { params })
          users.value = response.data
        } catch (err) {
          console.error('Failed to load users:', err)
          error.value.users = 'Failed to load users.'
        } finally {
          loading.value.users = false
          usersPromise = null
        }
      })()

      return usersPromise
    }

    const updateUserStatus = async (userId, isSuspended) => {
      try {
        await api.patch(`/admin/users/${userId}/`, {
          is_suspended: isSuspended
        })

        // Optimistic update
        const user = users.value.find(u => u.id === userId)
        if (user) {
          user.is_suspended = isSuspended
        }

        // Parallel refresh in background
        Promise.all([
          fetchUsers({}, true),
          fetchStats(true)
        ])

      } catch (err) {
        console.error('Failed to update user status:', err)
        throw err
      }
    }

    const deleteUser = async (userId) => {
      try {

        await api.delete(`/admin/users/${userId}/`)

        users.value = users.value.filter(
          user => user.id !== userId
        )
        await fetchStats(true)

      } catch (err) {
        console.error('Failed to delete user:', err)
        throw err
      }
    }

    let withdrawalsPromise = null
    const fetchWithdrawals = async (status = null, force = false) => {
      if (withdrawals.value.length && !status && !force) return

      if (withdrawalsPromise) {
        await withdrawalsPromise
        if (!status && !force) return
      }

      loading.value.withdrawals = true
      error.value.withdrawals = null

      withdrawalsPromise = (async () => {
        try {
          const params = status ? { status } : {}
          const response = await api.get('/admin/withdrawals/', { params })
          withdrawals.value = response.data
        } catch (err) {
          console.error('Failed to load withdrawals:', err)
          error.value.withdrawals = 'Failed to load withdrawals.'
        } finally {
          loading.value.withdrawals = false
          withdrawalsPromise = null
        }
      })()

      return withdrawalsPromise
    }

    const updateWithdrawalStatus = async (id, payload) => {
      try {
        await api.patch(`/admin/withdrawals/${id}/`, payload)
        await fetchWithdrawals(null, true)
        await fetchStats(true)
      } catch (err) {
        console.error('Failed to update withdrawal:', err)
        throw err
      }
    }

    let institutionsPromise = null
    const fetchInstitutions = async (force = false) => {
      if (institutions.value.length && !force) return

      if (institutionsPromise) {
        await institutionsPromise
        if (!force) return
      }

      loading.value.institutions = true
      error.value.institutions = null

      institutionsPromise = (async () => {
        try {
          const response = await api.get('/admin/institutions/')
          institutions.value = response.data
        } catch (err) {
          console.error('Failed to load institutions:', err)
          error.value.institutions = 'Failed to load institutions.'
        } finally {
          loading.value.institutions = false
          institutionsPromise = null
        }
      })()

      return institutionsPromise
    }

    const addInstitution = async (payload) => {
      try {
        await api.post('/admin/institutions/', payload)
        await fetchInstitutions(true)
        await fetchStats(true)
      } catch (err) {
        console.error('Failed to add institution:', err)
        throw err
      }
    }

    const toggleInstitutionActive = async (id, isActive) => {
      try {
        await api.patch(`/admin/institutions/${id}/`, {
          is_active: isActive
        })

        // Optimistic update
        const inst = institutions.value.find(i => i.id === id)
        if (inst) {
          inst.is_active = isActive
        }

        // Parallel refresh in background
        Promise.all([
          fetchInstitutions(true),
          fetchStats(true)
        ])
      } catch (err) {
        console.error('Failed to toggle institution active status:', err)
        throw err
      }
    }

    let analyticsPromise = null
    const fetchAnalytics = async (force = false) => {
      if (analytics.value && !force) return

      if (analyticsPromise) {
        await analyticsPromise
        if (!force) return
      }

      loading.value.analytics = true
      error.value.analytics = null

      analyticsPromise = (async () => {
        try {
          const response = await api.get('/admin/analytics/')
          analytics.value = response.data
        } catch (err) {
          console.error('Failed to load analytics:', err)
          error.value.analytics = 'Failed to load analytics.'
        } finally {
          loading.value.analytics = false
          analyticsPromise = null
        }
      })()

      return analyticsPromise
    }

    let tutorApplicationsPromise = null
    const fetchTutorApplications = async (status = null, force = false, options = {}) => {
      const params = {
        ...(status ? { status } : {}),
        ...(options.reviewType ? { review_type: options.reviewType } : {})
      }
      if (tutorApplications.value.length && !status && !force) return

      if (tutorApplicationsPromise) {
        await tutorApplicationsPromise
        if (!force) return
      }

      loading.value.tutorApplications = true
      error.value.tutorApplications = null

      tutorApplicationsPromise = (async () => {
        try {
          const response = await api.get('/admin/tutor-applications/', { params })
          tutorApplications.value = response.data
        } catch (err) {
          console.error('Failed to load tutor applications:', err)
          error.value.tutorApplications = 'Failed to load tutor applications.'
        } finally {
          loading.value.tutorApplications = false
          tutorApplicationsPromise = null
        }
      })()

      return tutorApplicationsPromise
    }

    const updateTutorApplicationStatus = async (
      id,
      applicationStatus,
      rejectionReason = '',
      options = {}
    ) => {
      try {
        const payload = {
          application_status: applicationStatus,
          rejection_reason: rejectionReason
        }

        if (options.reviewType === 'renewal') {
          payload.review_type = 'renewal'
          payload.renewal_status = applicationStatus
          payload.renewal_rejection_reason = rejectionReason
        }

        const endpoint = options.reviewType === 'renewal'
          ? `/admin/tutor-document-renewals/${id}/`
          : `/admin/tutor-applications/${id}/`

        await api.patch(endpoint, payload)
        await fetchTutorApplications(null, true)
        await fetchStats(true)
      } catch (err) {
        console.error('Failed to update tutor application:', err)
        throw err
      }
    }

    let tuteeApplicationsPromise = null
    const fetchTuteeApplications = async (status = null, force = false, options = {}) => {
      const params = {
        ...(status ? { status } : {}),
        ...(options.reviewType ? { review_type: options.reviewType } : {})
      }
      if (tuteeApplications.value.length && !status && !force) return

      if (tuteeApplicationsPromise) {
        await tuteeApplicationsPromise
        if (!force) return
      }

      loading.value.tuteeApplications = true
      error.value.tuteeApplications = null

      tuteeApplicationsPromise = (async () => {
        try {
          const response = await api.get('/admin/tutee-applications/', { params })
          tuteeApplications.value = response.data
        } catch (err) {
          console.error('Failed to load tutee applications:', err)
          error.value.tuteeApplications = 'Failed to load tutee applications.'
        } finally {
          loading.value.tuteeApplications = false
          tuteeApplicationsPromise = null
        }
      })()

      return tuteeApplicationsPromise
    }

    const updateTuteeApplicationStatus = async (
      id,
      applicationStatus,
      rejectionReason = '',
      options = {}
    ) => {
      try {
        const payload = {
          application_status: applicationStatus,
          rejection_reason: rejectionReason
        }

        if (options.reviewType === 'renewal') {
          payload.review_type = 'renewal'
          payload.renewal_status = applicationStatus
          payload.renewal_rejection_reason = rejectionReason
        }

        const endpoint = options.reviewType === 'renewal'
          ? `/admin/tutee-document-renewals/${id}/`
          : `/admin/tutee-applications/${id}/`

        await api.patch(endpoint, payload)
        await fetchTuteeApplications(null, true)
        await fetchStats(true)
      } catch (err) {
        console.error('Failed to update tutee application:', err)
        throw err
      }
    }

    return {
      stats,
      users,
      withdrawals,
      institutions,
      analytics,
      tutorApplications,
      tuteeApplications,
      operationalQueue,
      loading,
      error,

      fetchStats,
      fetchOperationalQueue,
      fetchUsers,
      updateUserStatus,
      deleteUser,

      fetchWithdrawals,
      updateWithdrawalStatus,

      fetchInstitutions,
      addInstitution,
      toggleInstitutionActive,

      fetchAnalytics,

      fetchTutorApplications,
      updateTutorApplicationStatus,

      fetchTuteeApplications,
      updateTuteeApplicationStatus
    }

  },

  {
    persist: {
      key: 'admin-store',
      storage: sessionStorage,

      paths: [
        'stats',
        'users',
        'withdrawals',
        'institutions',
        'tutorApplications',
        'tuteeApplications',
        'operationalQueue'
      ]
    }
  }
)
