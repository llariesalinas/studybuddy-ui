import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useRegistrationInfoStore = defineStore('newUserInfo', () => {
  const newUserFname = ref('')
  const newUserMname = ref('')
  const newUserLname = ref('')
  const newUserEmail = ref('')
  const newUserPassword = ref('')
  const newUserType = ref('')
  const selectedInstitutionId = ref('')

  const reset = () => {
    newUserFname.value = ''
    newUserMname.value = ''
    newUserLname.value = ''
    newUserEmail.value = ''
    newUserPassword.value = ''
    newUserType.value = ''
    selectedInstitutionId.value = ''
  }

  return {
    newUserFname,
    newUserMname,
    newUserLname,
    newUserEmail,
    newUserPassword,
    newUserType,
    selectedInstitutionId,
    reset,
  }
})
