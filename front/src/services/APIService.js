import axios from 'axios'
import store from '../store'
import router from '../router'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001/api/v1'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

/* =========================
   REQUEST INTERCEPTOR
========================= */
api.interceptors.request.use(
  (config) => {
    try {
      const token = localStorage.getItem('access')

      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }

      return config
    } catch (error) {
      console.error('Erro no interceptor request:', error)
      return Promise.reject(error)
    }
  }
)

/* =========================
   RESPONSE INTERCEPTOR
========================= */
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    try {
      const originalRequest = error.config

      if (
        error.response &&
        error.response.status === 401 &&
        !originalRequest._retry
      ) {
        originalRequest._retry = true

        const refreshToken = localStorage.getItem('refresh')

        if (!refreshToken) {
          await handleLogout()
          return Promise.reject(error)
        }

        const response = await axios.post(
          `${API_URL}/auth/token/refresh/`,
          { refresh: refreshToken }
        )

        const { access } = response.data

        localStorage.setItem('access', access)

        api.defaults.headers.common['Authorization'] = `Bearer ${access}`
        originalRequest.headers['Authorization'] = `Bearer ${access}`

        return api(originalRequest)
      }

      return Promise.reject(error)

    } catch (refreshError) {
      console.error('Erro ao renovar token:', refreshError)
      await handleLogout()
      return Promise.reject(refreshError)
    }
  }
)

/* =========================
   LOGOUT CENTRALIZADO
========================= */
async function handleLogout() {
  store.commit('LOGOUT')
  await router.push({ name: 'signin' })
}

export default api