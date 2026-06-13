import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import api from '@/services/api/api'
import { useCatalogStore } from '@/stores/catalog'

export const useWalletStore = defineStore('wallet', () => {
  const catalogStore = useCatalogStore()
  const balance = ref(0)
  const pendingAmount = ref(0)
  const cashoutMinimum = ref(500)
  const cashoutProviderFee = ref(10)
  const transactions = ref([])
  const withdrawals = ref([])
  const payoutAccounts = ref([])
  const receivingInstitutions = ref([])
  const loading = ref(false)

  const totals = computed(() => {
    let gross = 0
    let deductions = 0
    let net = 0

    transactions.value.forEach(t => {
      const amount = Number(t.amount) || 0
      if (t.transaction_type === 'session_credit') {
        gross += amount
        net += amount
      } else if (t.transaction_type === 'commission_deduction') {
        const absAmount = Math.abs(amount)
        gross += absAmount
        deductions += absAmount
      }
    })

    return { gross, deductions, net }
  })

  const grossEarned = computed(() => totals.value.gross)
  const totalDeductions = computed(() => totals.value.deductions)
  const netEarned = computed(() => totals.value.net)

  async function fetchWallet() {
    loading.value = true
    try {
      const { data } = await api.get('wallet/')
      balance.value = data.balance
      pendingAmount.value = data.pending_amount
      cashoutMinimum.value = data.cashout_minimum ?? 500
      cashoutProviderFee.value = data.cashout_provider_fee ?? 10
    } finally {
      loading.value = false
    }
  }

  async function fetchTransactions() {
    const { data } = await api.get('wallet/transactions/')
    transactions.value = data
  }

  async function fetchWithdrawals() {
    const { data } = await api.get('wallet/cash-outs/')
    withdrawals.value = data
  }

  async function fetchPayoutAccounts() {
    const { data } = await api.get('wallet/payout-destinations/')
    payoutAccounts.value = data
  }

  async function fetchReceivingInstitutions(provider = 'instapay') {
    const data = await catalogStore.fetchReceivingInstitutions(provider)
    receivingInstitutions.value = data
    return data
  }

  async function savePayoutAccount(payload) {
    const request = payload.id
      ? api.patch(`wallet/payout-destinations/${payload.id}/`, payload)
      : api.post('wallet/payout-destinations/', payload)

    await request
    await fetchPayoutAccounts()
  }

  async function deactivatePayoutAccount(id) {
    await api.patch(`wallet/payout-destinations/${id}/`, { is_active: false })
    await fetchPayoutAccounts()
  }

  async function requestWithdrawal(payload) {
    try {
      await api.post('wallet/cash-outs/', payload)
      await fetchWallet()
      await fetchTransactions()
      await fetchWithdrawals()
      return { success: true }
    } catch (e) {
      return { success: false, error: e.response?.data?.error || 'Cash-out failed. Please try again.' }
    }
  }

  async function devAddFunds(amount) {
    await api.post('dev/wallet/add/', { amount })
  }

  async function devRemoveFunds(amount) {
    await api.post('dev/wallet/remove/', { amount })
  }

  return { balance, pendingAmount, cashoutMinimum, cashoutProviderFee, transactions, withdrawals,
           payoutAccounts, receivingInstitutions, loading,
           grossEarned, totalDeductions, netEarned,
           fetchWallet, fetchTransactions, fetchWithdrawals, fetchPayoutAccounts,
           fetchReceivingInstitutions, savePayoutAccount, deactivatePayoutAccount,
           requestWithdrawal, devAddFunds,
           devRemoveFunds }
})
