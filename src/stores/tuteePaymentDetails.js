import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePaymentStore = defineStore('payment', () => {

  const selectedMethod = ref(null)
  const amountPaid = ref(null)

  const gCashName = ref('')
  const gCashNumber = ref('')
  const gCashReference = ref('')

  const bankName = ref('')
  const bankAccount = ref('')
  const bankReference = ref('')

  const reset = () => {
    selectedMethod.value = null
    amountPaid.value = null

    gCashName.value = ''
    gCashNumber.value = ''
    gCashReference.value = ''

    bankName.value = ''
    bankAccount.value = ''
    bankReference.value = ''
  }

  return {
    selectedMethod,
    amountPaid,
    gCashName,
    gCashNumber,
    gCashReference,
    bankName,
    bankAccount,
    bankReference,
    reset
  }
})