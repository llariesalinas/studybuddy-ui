import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import api from '@/services/api/api'

export const useWalletStore = defineStore('wallet', () => {
  const balance = ref(0)
  const pendingAmount = ref(0)
  const transactions = ref([])
  const withdrawals = ref([])
  const loading = ref(false)

  const grossEarned = computed(() => {
    const credits = transactions.value
      .filter(t => t.transaction_type === 'session_credit')
      .reduce((sum, t) => sum + Number(t.amount), 0)
    const deductions = transactions.value
      .filter(t => t.transaction_type === 'commission_deduction')
      .reduce((sum, t) => sum + Math.abs(Number(t.amount)), 0)
    return credits + deductions
  })

  const totalDeductions = computed(() =>
    transactions.value
      .filter(t => t.transaction_type === 'commission_deduction')
      .reduce((sum, t) => sum + Math.abs(Number(t.amount)), 0)
  )

  const netEarned = computed(() =>
    transactions.value
      .filter(t => t.transaction_type === 'session_credit')
      .reduce((sum, t) => sum + Number(t.amount), 0)
  )

  async function fetchWallet() {
    loading.value = true
    try {
      const { data } = await api.get('wallet/')
      balance.value = data.balance
      pendingAmount.value = data.pending_amount
    } finally {
      loading.value = false
    }
  }

  async function fetchTransactions() {
    const { data } = await api.get('wallet/transactions/')
    transactions.value = data
  }

  async function fetchWithdrawals() {
    const { data } = await api.get('wallet/withdrawals/')
    withdrawals.value = data
  }

  async function requestWithdrawal(payload) {
    try {
      await api.post('wallet/withdraw/', payload)
      await fetchWallet()
      await fetchWithdrawals()
      return { success: true }
    } catch (e) {
      return { success: false, error: e.response?.data?.error || 'Withdrawal failed. Please try again.' }
    }
  }

  async function devAddFunds(amount) {
    await api.post('dev/wallet/add/', { amount })
  }

  async function devRemoveFunds(amount) {
    await api.post('dev/wallet/remove/', { amount })
  }

  return { balance, pendingAmount, transactions, withdrawals, loading,
           grossEarned, totalDeductions, netEarned,
           fetchWallet, fetchTransactions, fetchWithdrawals, requestWithdrawal, devAddFunds,
           devRemoveFunds }
})
