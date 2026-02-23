import { ref } from "vue";
import { defineStore } from "pinia";

export const useRegistrationInfoStore= defineStore('newUserInfo', () => {
    const newUserFullName = ref('')
    const newUserEmail = ref('')
    const newUserPassword = ref('')
    const newUserType = ref('')

    return {newUserFullName, newUserEmail, newUserPassword, newUserType}
})
