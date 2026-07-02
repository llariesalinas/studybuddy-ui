import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import api from '@/services/api/api'
import { useCatalogStore } from '@/stores/catalog'

export const useWalletStore = defineStore('wallet', () => {
  const catalogStore = useCatalogStore()
  const balance = ref(0)
  const pendingAmount = ref(0)
  const cashinMinimum = ref(50)
  const cashoutMinimum = ref(50)
  const cashoutMaximum = ref(50000)
  const cashoutProviderFee = ref(10)
  const transactions = ref([])
  const withdrawals = ref([])
  const recentCashOuts = ref([])
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
      cashinMinimum.value = data.cashin_minimum ?? 50
      cashoutMinimum.value = data.cashout_minimum ?? 50
      cashoutMaximum.value = data.cashout_maximum ?? 50000
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

  async function fetchRecentCashOuts() {
    const { data } = await api.get('wallet/cash-outs/recent/')
    recentCashOuts.value = data
  }

  async function fetchReceivingInstitutions() {
    const data = await catalogStore.fetchReceivingInstitutions()
    receivingInstitutions.value = data
    return data
  }

  async function requestWithdrawal(payload) {
    const {
      amount,
      destination_type,
      receiving_institution_id,
      receiving_institution_name,
      receiving_institution_code,
      account_number,
      account_name,
      bank_name,
      note,
      confirm_new_destination,
    } = payload

    await api.post('wallet/cash-outs/', {
      amount,
      destination_type,
      receiving_institution_id,
      receiving_institution_name,
      receiving_institution_code,
      account_number,
      account_name,
      bank_name,
      note,
      confirm_new_destination,
    })
    await fetchWallet()
    await fetchTransactions()
    await fetchWithdrawals()
  }

  async function initiateCashIn(amount) {
    const { data } = await api.post('wallet/cash-in/', { amount })
    return data // { checkout_url, id }
  }

  async function verifyCashIn(id) {
    const { data } = await api.post(`wallet/cash-in/${id}/verify/`)
    await fetchWallet()
    await fetchTransactions()
    return data
  }

  async function devAddFunds(amount) {
    await api.post('dev/wallet/add/', { amount })
  }

  async function devRemoveFunds(amount) {
    await api.post('dev/wallet/remove/', { amount })
  }

  return { balance, pendingAmount, cashinMinimum, cashoutMinimum, cashoutMaximum, cashoutProviderFee, transactions, withdrawals,
           recentCashOuts, receivingInstitutions, loading,
           grossEarned, totalDeductions, netEarned,
           fetchWallet, fetchTransactions, fetchWithdrawals, fetchRecentCashOuts,
           fetchReceivingInstitutions,
           requestWithdrawal, initiateCashIn, verifyCashIn, devAddFunds,
           devRemoveFunds }
})
