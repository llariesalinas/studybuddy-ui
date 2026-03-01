import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePaymentStore = defineStore('payment', () => {

  // Common
  const selectedMethod = ref(null)
  const amountPaid = ref(null)

  // GCash
  const gCashName = ref('')
  const gCashNumber = ref('')
  const gCashReference = ref('')

  // Card/Bank
  const bankName = ref('')
  const bankAccount = ref('')
  const bankReference = ref('')


  return {
    selectedMethod,
    amountPaid,
    gCashName,
    gCashNumber,
    gCashReference,
    bankName,
    bankAccount,
    bankReference
  }
})