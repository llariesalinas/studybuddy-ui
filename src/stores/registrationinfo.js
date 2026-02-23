import { ref } from "vue";
import { defineStore } from "pinia";

export const useRegistrationInfoStore= defineStore('newUserInfo', () => {
    const newUserFullName = ref('')
    //const newUserFname = ref('')
    //const newUserMname = ref('')
    //const newUserLname = ref('')
    const newUserEmail = ref('')
    const newUserPassword = ref('')
    const newUserType = ref('')
    return {newUserFullName, newUserEmail, newUserPassword, newUserType}
})
