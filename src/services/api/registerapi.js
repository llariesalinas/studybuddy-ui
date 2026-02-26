import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/',
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api

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