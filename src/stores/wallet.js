import { ref } from 'vue'
import { defineStore } from 'pinia'
import api from '@/services/api/api'

export const useWalletStore = defineStore('wallet', () => {
  const balance = ref(0)
  const pendingAmount = ref(0)
  const transactions = ref([])
  const withdrawals = ref([])
  const loading = ref(false)

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

  return { balance, pendingAmount, transactions, withdrawals, loading,
           fetchWallet, fetchTransactions, fetchWithdrawals, requestWithdrawal }
})
