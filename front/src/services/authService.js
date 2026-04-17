import api from '@/services/APIService'

/**
 * Perfil do usuário autenticado (`GET` / `PATCH` /api/v1/auth/user).
 */
export const authService = {
  async getProfile () {
    const { data } = await api.get('/auth/user')
    return data.user
  },

  async updateProfile (payload) {
    const { data } = await api.patch('/auth/user', payload)
    return data.user
  }
}
