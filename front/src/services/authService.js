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
  },

  /**
   * Conclui login com OTP de 2FA (`POST` /api/v1/auth/2fa/verify).
   * Aceita `code` (6 dígitos) ou `link_token` (link do e-mail).
   * @returns {{ user, access, refresh }}
   */
  async verifyTwoFactor ({ challenge_id, code, link_token }) {
    const body = { challenge_id }
    if (link_token) {
      body.link_token = link_token
    } else {
      body.code = code
    }
    const { data } = await api.post('/auth/2fa/verify', body)
    return data
  },

  async requestPasswordReset ({ login }) {
    const { data } = await api.post('/auth/password-reset/request', { login })
    return data
  },

  async confirmPasswordReset ({ challenge_id, token, new_password, new_password_confirm }) {
    const { data } = await api.post('/auth/password-reset/confirm', {
      challenge_id,
      token,
      new_password,
      new_password_confirm
    })
    return data
  }
}
