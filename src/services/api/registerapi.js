import axios from 'axios'

const API_URL = 'http://127.0.0.1:8000/api'

export const registerUser = async (store) => {
  return await axios.post(`${API_URL}/register/`, {
    email: store.newUserEmail,
    password: store.newUserPassword,
    fname: store.newUserFname,
    mname: store.newUserMname,
    lname: store.newUserLname,
    role: store.newUserType
  })
}