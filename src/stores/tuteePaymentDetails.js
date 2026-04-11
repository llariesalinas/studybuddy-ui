import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePaymentStore = defineStore('payment', () => {
  const selectedMethod = ref(null)
  const amountPaid = ref(null)
  const receiptImage = ref(null)

  const reset = () => {
    selectedMethod.value = null
    amountPaid.value = null
    receiptImage.value = null
  }

  return {
    selectedMethod,
    amountPaid,
    receiptImage,
    reset
  }
})
