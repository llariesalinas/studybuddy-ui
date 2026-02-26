import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/',
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')

  // DO NOT attach token for login/register
  if (
    token &&
    !config.url.includes('login') &&
    !config.url.includes('register')
  ) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

export default api